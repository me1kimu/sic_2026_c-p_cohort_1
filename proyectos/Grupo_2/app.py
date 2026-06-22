import gradio as gr
from google.colab import userdata
from grafo_logistica import GrafoLogistica
from motor_logico import MotorLogico
from motor_ia import MotorIA
from procesamiento_datos import construir_grafo_desde_gtfs, cargar_paraderos_desde_arcgis

# 1. Recuperar token y cargar datos
try:
    HF_TOKEN = userdata.get('HF_TOKEN')
except:
    HF_TOKEN = None

# Ya no usamos cargar_paraderos_desde_arcgis. Usamos los datos procesados en la celda anterior.

grafo_memoria = GrafoLogistica()

# 🚨 Inyección de Vértices y Aristas directa al núcleo del Grafo
grafo_memoria.paraderos = set(paraderos_reales.keys())
grafo_memoria.adyacencia = conexiones_reales

# Iniciamos el Motor de Red
motor_red = MotorLogico(grafo_memoria)
motor_red.cargar_datos_base(paraderos_reales, servicios_reales)

# Iniciamos la IA
cerebro_ia = MotorIA(motor_red, HF_TOKEN)

# ==========================================
# 5. INTERFAZ GRÁFICA (Gradio)
# ==========================================
# Cuidado: Como ahora tenemos miles de paraderos, el Dropdown puede ser pesado.
# Seleccionamos solo los primeros 1000 para que la interfaz web cargue rápido.
nombres_paraderos = list(paraderos_reales.keys())[:1000]

# Para las paradas intermedias (opcionales) agregamos la opción "Ninguna" al principio
opciones_intermedias = ["Ninguna"] + nombres_paraderos

# Fíjate qué limpio: Gradio llama DIRECTAMENTE a cerebro_ia.evaluar_estrategia_logistica_multiparada
# El sistema prueba automáticamente todos los órdenes posibles entre las paradas
# intermedias seleccionadas y se queda con el de menor costo.
app = gr.Interface(
    fn=cerebro_ia.evaluar_estrategia_logistica_multiparada,
    inputs=[
        gr.Dropdown(choices=nombres_paraderos, label="📍 Origen"),
        gr.Dropdown(choices=opciones_intermedias, value="Ninguna", label="➕ Parada intermedia 1 (opcional)"),
        gr.Dropdown(choices=opciones_intermedias, value="Ninguna", label="➕ Parada intermedia 2 (opcional)"),
        gr.Dropdown(choices=nombres_paraderos, label="🎯 Destino"),
        gr.Textbox(lines=2, label="🗣️ Contexto")
    ],
    outputs=gr.Markdown(label="🧠 Decisión del Agente"),
    title="🤖 Agente Logístico",
)

app.launch()