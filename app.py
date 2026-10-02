import gradio as gr
from PIL import Image
import random

# Lista de las 10 señales reglamentarias objetivo
CLASES = [
    "PARE (R-01)",
    "Ceda el paso (R-02)",
    "Prohibido avanzar / No pase (R-03)",
    "Prohibido girar a la izquierda (R-05)",
    "Prohibido girar a la derecha (R-07)",
    "Prohibido adelantar (R-14)",
    "Prohibido parquear (R-19)",
    "Velocidad máxima (R-30)",
    "Prohibido pitar (R-28)",
    "Peatones prohibidos (R-27)"
]

def clasificar_senal(imagen_entrada):
    """
    Función temporal de prueba. 
    Aquí conectaremos el modelo entrenado más adelante.
    """
    if imagen_entrada is None:
        return "Por favor, sube una imagen válida."
    
    # Simulación de predicción para probar la UI
    prediccion_demo = random.choice(CLASES)
    confianza_demo = round(random.uniform(85.0, 99.9), 2)
    
    return {prediccion_demo: confianza_demo / 100}

# Definición de la interfaz en Gradio
demo = gr.Interface(
    fn=clasificar_senal,
    inputs=gr.Image(type="pil", label="Cargar foto de la señal"),
    outputs=gr.Label(num_top_classes=1, label="Resultado de la clasificación"),
    title="Detección Inteligente de Señales de Tránsito",
    description="Sube una fotografía de una señal de tránsito reglamentaria para identificar su tipo.",
)

if __name__ == "__main__":
    demo.launch()