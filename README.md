# Clasificación de señales de tránsito

Proyecto académico para explorar la clasificación de señales de tránsito a
partir de imágenes. Incluye una interfaz web de demostración con Gradio, un
script para descargar y organizar imágenes, y un script de entrenamiento con
transfer learning usando MobileNetV2 y PyTorch.

> **Estado:** la interfaz todavía genera predicciones aleatorias de demostración.
> No carga el modelo entrenado. El entrenamiento y la aplicación son flujos
> separados por ahora.

## Contenido del proyecto

```text
proyecto_senales/
├── app.py                  # Interfaz Gradio y clasificador de demostración
├── descargar_dataset.py    # Descarga y división de imágenes (80/20)
├── dataset/
│   ├── train/              # Imágenes para entrenamiento, organizadas por clase
│   └── val/                # Imágenes para validación, organizadas por clase
├── modelo/
│   ├── entrenar.py         # Entrenamiento de MobileNetV2
│   └── modelo_senales.pth  # Pesos generados localmente al entrenar
├── requirements.txt        # Dependencias de Python
└── README.md
```

El entorno virtual `.venv` y las imágenes descargadas son archivos locales y
no forman parte del repositorio.

## Clases del dataset

El entrenador y el descargador usan estas nueve clases:

- `CEDA_EL_PASO`
- `NO_PASE`
- `PARE`
- `PEATONES_PROHIBIDOS`
- `PROHIBIDO_ADELANTAR`
- `PROHIBIDO_GIRAR_DER`
- `PROHIBIDO_GIRAR_IZQ`
- `PROHIBIDO_PARQUEAR`
- `VELOCIDAD_MAXIMA`

La interfaz de demostración en `app.py` muestra una lista distinta de diez
etiquetas; entre ellas aparece `PROHIBIDO_PITAR`, que no está incluida en el
dataset ni en el descargador.

## Requisitos

- Python 3.10 o superior.
- `pip`.
- Conexión a Internet para descargar imágenes y, la primera vez que se entrena,
  para obtener los pesos preentrenados de MobileNetV2.
- GPU compatible con CUDA opcional. Sin ella, PyTorch puede entrenar en CPU.

## Instalación en Windows (PowerShell)

Ejecuta los comandos desde la carpeta raíz del proyecto:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Si PowerShell bloquea la activación del entorno, puedes ejecutar los scripts
con el intérprete de `.venv` directamente:

```powershell
.\.venv\Scripts\python.exe .\app.py
```

## Descargar imágenes

Desde la raíz del proyecto, ejecuta:

```powershell
python .\descargar_dataset.py
```

Por defecto, el descargador intenta obtener hasta 60 imágenes por clase y las
reparte entre `train` y `val` aproximadamente en proporción 80/20. Para cambiar
el objetivo por clase o descargar solo algunas clases:

```powershell
python .\descargar_dataset.py --limit 100
python .\descargar_dataset.py --classes PARE CEDA_EL_PASO
```

La cantidad final depende de los resultados disponibles en Bing. Revisa
manualmente las imágenes y elimina las que no correspondan a su clase antes
de entrenar. El descargador guarda las imágenes dentro de `dataset/`; Git las
ignora.

tener en cuenta que aveces descarga imagenes que no sirven, entonce recomendado limpiar manualmente y verificar las imagenes

## Entrenar el modelo

Comprueba que existan imágenes válidas dentro de las carpetas de clase de
`dataset/train` y `dataset/val`. Luego, desde la raíz del proyecto, ejecuta:

```powershell
python .\modelo\entrenar.py
```

No ejecutes `python entrenar.py` desde la raíz: el script está dentro de
`modelo`. Ejecutarlo desde la raíz también permite que encuentre `dataset/` y
guarde el resultado en `modelo/modelo_senales.pth`.

El script redimensiona las imágenes a 224 × 224, usa MobileNetV2 preentrenada,
congela sus capas base y entrena la capa clasificadora durante cinco épocas.
Al finalizar guarda el estado del modelo y los nombres de las clases en el
archivo `.pth`. El entrenamiento depende de tener imágenes en ambas divisiones
y de que las clases estén organizadas en subcarpetas.

## Ejecutar la aplicación

Desde la raíz del proyecto:

```powershell
python .\app.py
```

Gradio mostrará una dirección local en la terminal para abrir la interfaz en el
navegador. La clasificación actual es aleatoria y sirve únicamente para probar
la interfaz; todavía no utiliza `modelo/modelo_senales.pth`.

## Dependencias

Las dependencias están listadas en [requirements.txt](./requirements.txt):
PyTorch, TorchVision, Gradio, Pillow, NumPy y Bing Image Downloader.
