# Proyecto de Detección Inteligente de Señales de Tránsito

Este proyecto tiene como objetivo desarrollar una aplicación para identificar señales de tránsito a partir de imágenes. La interfaz permite cargar una fotografía de una señal y obtener una predicción del tipo de señal detectada.

Actualmente, la aplicación cuenta con una versión de demostración basada en una interfaz web con Gradio y una lógica de clasificación provisional. En una etapa posterior, esta parte podrá reemplazarse por un modelo entrenado de visión artificial.

## Objetivo

- Detectar señales de tránsito reglamentarias desde imágenes.
- Crear una interfaz sencilla para pruebas y demos.
- Preparar la base para integrar un modelo de clasificación más robusto.

## Funcionalidades

- Carga de imagen desde el equipo.
- Interfaz gráfica con Gradio.
- Predicción de la categoría de señal.
- Visualización del resultado con nivel de confianza.

## Estructura del proyecto

```text
proyecto_senales/
├── app.py                 # Aplicación principal con la interfaz Gradio
├── dataset/               # Conjunto de datos para entrenamiento y pruebas
├── modelo/                # Archivos relacionados con el modelo entrenado
├── notebooks/             # Notebooks para análisis y experimentación
├── requirements.txt       # Dependencias del proyecto
├── .venv/                 # Entorno virtual del proyecto
└── README.md              # Documentación del proyecto
```

## Tecnologías utilizadas

- Python
- Gradio
- PyTorch
- TorchVision
- Pillow
- NumPy

## Requisitos previos

Antes de ejecutar el proyecto, asegúrate de tener instalado:

- Python 3.10 o superior
- pip
- Entorno virtual (opcional, pero recomendado)

## Instalación

1. Clona o descarga este repositorio.
2. Abre una terminal en la carpeta del proyecto.
3. Crea y activa un entorno virtual:

```bash
python -m venv .venv
```

En Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

4. Instala las dependencias:

```bash
pip install -r requirements.txt
```

## Ejecución

Para iniciar la aplicación:

```bash
python app.py
```

Esto abrirá la interfaz gráfica en el navegador. Desde ahí podrás cargar una imagen y obtener la predicción de la señal.

## Descargar imágenes para el dataset

Instala las dependencias del proyecto y ejecuta desde la raíz:

```bash
pip install -r requirements.txt
python descargar_dataset.py
```

El script busca imágenes con `bing-image-downloader` usando términos en español.
Por defecto intenta descargar 60 imágenes por clase: 48 para `train` y 12 para
`val`. Puedes cambiar el total con `--limit`, por ejemplo:

```bash
python descargar_dataset.py --limit 100
```

Las imágenes descargadas se guardan localmente y Git las ignora. Bing puede
devolver resultados que no correspondan a la señal; revisa las imágenes de cada
clase antes de entrenar el modelo. Para completar solo `PARE` y
usar sus búsquedas alternativas, ejecuta:

```bash
python descargar_dataset.py --classes PARE
```

El script prueba búsquedas alternativas para `PARE` y evita guardar dos veces
el mismo archivo. `PROHIBIDO_PITAR` se excluyó de la descarga automática porque
hay pocos resultados locales confiables. La cantidad disponible depende de Bing.

## Uso de la aplicación

1. Ejecuta la aplicación con `python app.py`.
2. En la interfaz, haz clic en "Cargar foto de la señal".
3. Selecciona una imagen de una señal de tránsito.
4. La aplicación devuelve la clase de la señal y un valor de confianza aproximado.

## Estado actual

La versión actual es una demo funcional para evidenciar la interfaz y la lógica de clasificación. Los nombres de señales que aparecen en la app corresponden a clases reglamentarias de ejemplo y servirán como base para la integración del modelo real.

## Próximos pasos recomendados

- Preparar y organizar el dataset.
- Entrenar un modelo CNN o un modelo de visión por computador.
- Guardar el modelo entrenado en `modelo/`.
- Reemplazar la predicción aleatoria por la salida real del modelo.
- Mejorar la validación y métricas de rendimiento.

## Notas

Este proyecto se encuentra en una etapa inicial de desarrollo. La estructura y la lógica ya están preparadas para evolucionar hacia una solución completa de clasificación automática de señales de tránsito.
