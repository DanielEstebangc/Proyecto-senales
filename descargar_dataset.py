"""Descarga imágenes de señales usando Bing Image Downloader."""

import argparse
import hashlib
import random
import shutil
import sys
import tempfile
from pathlib import Path
from urllib.error import HTTPError, URLError

from bing_image_downloader.bing import Bing
from PIL import Image, UnidentifiedImageError


ROOT = Path(__file__).resolve().parent
DATASET_DIR = ROOT / "dataset"
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp", ".bmp"}

BUSQUEDAS = {
    "PARE": "señal pare señal de tránsito Colombia",
    "CEDA_EL_PASO": "señal ceda el paso Colombia",
    "NO_PASE": "señal prohibido avanzar no pase Colombia",
    "PROHIBIDO_GIRAR_IZQ": "señal prohibido girar a la izquierda Colombia",
    "PROHIBIDO_GIRAR_DER": "señal prohibido girar a la derecha Colombia",
    "PROHIBIDO_ADELANTAR": "señal prohibido adelantar Colombia",
    "PROHIBIDO_PARQUEAR": "señal prohibido parquear Colombia",
    "VELOCIDAD_MAXIMA": "señal velocidad máxima 50 Colombia",
    "PEATONES_PROHIBIDOS": "señal prohibido peatones Colombia",
}
BUSQUEDAS_ALTERNATIVAS = {
    "PARE": (
        "señal pare en calle Colombia foto",
        "señal pare carretera Colombia fotografía",
        "stop sign street photo",
        "stop sign road photo",
    ),
}
USER_AGENT = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/131.0.0.0 Safari/537.36"
)


def valid_images(directory):
    images = []
    for path in directory.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in IMAGE_EXTENSIONS:
            continue
        try:
            with Image.open(path) as image:
                image.verify()
        except (UnidentifiedImageError, OSError):
            print(f"  Se omite archivo de imagen inválido: {path.name}")
            continue
        images.append(path)
    return sorted(images)


def count_images(directory):
    if not directory.exists():
        return 0
    return sum(
        path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
        for path in directory.iterdir()
    )


def image_hash(path):
    digest = hashlib.sha256()
    with path.open("rb") as image_file:
        for chunk in iter(lambda: image_file.read(64 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def download_from_bing(search_term, limit, output_dir):
    search = Bing(
        search_term,
        limit,
        Path(output_dir),
        adult="off",
        timeout=10,
        verbose=False,
    )
    # Bing rejects the outdated browser identity bundled with the library.
    search.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept-Language": "es-CO,es;q=0.9,en;q=0.8",
        }
    )
    search.run()
    return search.download_count


def split_images(class_name, images, train_target, val_target):
    random.Random(class_name).shuffle(images)
    train_dir = DATASET_DIR / "train" / class_name
    val_dir = DATASET_DIR / "val" / class_name
    train_dir.mkdir(parents=True, exist_ok=True)
    val_dir.mkdir(parents=True, exist_ok=True)
    counts = {
        "train": count_images(train_dir),
        "val": count_images(val_dir),
    }
    targets = {"train": train_target, "val": val_target}
    known_hashes = {
        image_hash(path)
        for directory in (train_dir, val_dir)
        for path in directory.iterdir()
        if path.is_file() and path.suffix.lower() in IMAGE_EXTENSIONS
    }

    for image in images:
        image_digest = image_hash(image)
        if image_digest in known_hashes:
            continue
        available = [
            split for split in ("train", "val")
            if counts[split] < targets[split]
        ]
        if not available:
            break
        split = min(
            available,
            key=lambda name: counts[name] / targets[name] if targets[name] else 1,
        )
        destination_dir = train_dir if split == "train" else val_dir
        next_index = counts[split] + 1
        destination = destination_dir / (
            f"{class_name}_{next_index:03d}{image.suffix.lower()}"
        )
        while destination.exists():
            next_index += 1
            destination = destination_dir / (
                f"{class_name}_{next_index:03d}{image.suffix.lower()}"
            )
        shutil.copy2(image, destination)
        known_hashes.add(image_digest)
        counts[split] += 1

    return counts


def fill_class(class_name, search_terms, train_target, val_target):
    train_dir = DATASET_DIR / "train" / class_name
    val_dir = DATASET_DIR / "val" / class_name
    targets = {"train": train_target, "val": val_target}
    counts = {
        "train": count_images(train_dir),
        "val": count_images(val_dir),
    }

    for search_term in search_terms:
        missing = sum(
            max(0, targets[split] - counts[split]) for split in targets
        )
        if missing == 0:
            break

        request_limit = min(max(missing * 2, 30), 100)
        print(f"  Buscando: {search_term}", flush=True)
        with tempfile.TemporaryDirectory(
            prefix="bing_", dir=DATASET_DIR
        ) as staging_dir:
            try:
                download_from_bing(search_term, request_limit, staging_dir)
            except (HTTPError, URLError, TimeoutError, OSError) as error:
                print(f"  Falló esta búsqueda: {error}")
                continue

            downloaded = valid_images(Path(staging_dir))
            if not downloaded:
                continue
            previous_total = sum(counts.values())
            counts = split_images(
                class_name, downloaded, train_target, val_target
            )
            added = sum(counts.values()) - previous_total
            print(f"  Imágenes nuevas válidas: {added}")

    return counts


def main():
    parser = argparse.ArgumentParser(
        description="Descarga imágenes de señales con Bing y las reparte 80/20."
    )
    parser.add_argument(
        "--limit",
        type=int,
        default=60,
        help="Cantidad objetivo por clase entre train y val (por defecto: 60).",
    )
    parser.add_argument(
        "--classes",
        nargs="+",
        choices=BUSQUEDAS,
        help="Procesar solo las clases indicadas.",
    )
    args = parser.parse_args()
    if args.limit < 1:
        parser.error("--limit debe ser mayor que cero.")

    train_target = (
        args.limit if args.limit == 1
        else min(args.limit - 1, max(1, round(args.limit * 0.8)))
    )
    val_target = args.limit - train_target
    incomplete = []

    selected_classes = args.classes or list(BUSQUEDAS)
    for class_name in selected_classes:
        search_terms = (
            BUSQUEDAS[class_name],
            *BUSQUEDAS_ALTERNATIVAS.get(class_name, ()),
        )
        targets = {"train": train_target, "val": val_target}
        train_dir = DATASET_DIR / "train" / class_name
        val_dir = DATASET_DIR / "val" / class_name
        counts = {
            "train": count_images(train_dir),
            "val": count_images(val_dir),
        }
        missing = sum(
            max(0, targets[split] - counts[split]) for split in targets
        )
        print(f"\nDescargando {class_name}", flush=True)
        if missing == 0:
            print("  Ya se alcanzó la cantidad objetivo.")
            continue

        DATASET_DIR.mkdir(parents=True, exist_ok=True)
        counts = fill_class(
            class_name, search_terms, train_target, val_target
        )

        print(
            f"  Resultado: {counts['train']} train, {counts['val']} val"
        )
        if any(counts[split] < targets[split] for split in targets):
            incomplete.append(class_name)

    if incomplete:
        print(
            "\nBing no entregó suficientes imágenes válidas para: "
            + ", ".join(incomplete)
            + ". Revisa las imágenes obtenidas o vuelve a ejecutar el script."
        )
        return 1

    print("\nDescarga completada.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except KeyboardInterrupt:
        print(
            "\nDescarga interrumpida. Las imágenes ya guardadas se conservaron.",
            file=sys.stderr,
        )
        raise SystemExit(130)
