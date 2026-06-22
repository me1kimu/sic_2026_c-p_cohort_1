# 🚌 Enrutador Logístico Inteligente (Híbrido Neuro-Simbólico)

![Python](https://img.shields.io/badge/Python-3.8%2B-blue?logo=python)
![Gradio](https://img.shields.io/badge/UI-Gradio-orange?logo=gradio)
![HuggingFace](https://img.shields.io/badge/AI-Hugging_Face-yellow?logo=huggingface)
![Pandas](https://img.shields.io/badge/Data-Pandas-green?logo=pandas)

Un sistema de recomendación de rutas para la red de transporte público (Transantiago/RED) que combina el rigor matemático de la **Teoría de Grafos (Algoritmo de Dijkstra)** con la flexibilidad cognitiva de los **Modelos de Lenguaje Grande (LLMs)**.

## 👥 Equipo
* **Daniel Quiroz** - GitHub: [@Veldora2112](https://github.com/Veldora2112)
* **Pablo Camus Navarro** - GitHub: [@PaCaNav](https://github.com/PaCaNav)
* **Jacob** -GitHub:[]()

---

## 🎯 Pregunta de Análisis
> *¿Cómo podemos optimizar el enrutamiento logístico en una red masiva de transporte público, combinando métricas matemáticas exactas (tiempo y distancia) con la adaptación cognitiva al contexto situacional y necesidades subjetivas del usuario mediante Inteligencia Artificial?*

## 💡 Hallazgo Principal
A lo largo de este proyecto, demostramos que los algoritmos tradicionales de grafos (como Dijkstra) son insuperables en la precisión del cálculo de rutas, pero carecen de empatía situacional. Al integrar una capa de **IA Generativa (Hugging Face)** sobre la capa matemática, logramos un "Enrutador Híbrido" capaz de recomendar una ruta un poco más larga, pero más segura o cómoda, si el contexto del usuario (ej. "viajo con bultos grandes" o "viajo de noche") así lo requiere.

---

## 📊 Dataset
El proyecto se alimenta de la estructura oficial de transporte metropolitano.
* **Fuente:** Datos Abiertos GTFS de la Red Metropolitana de Movilidad / IDEOCUC.
* **Vértices (Nodos):** ~11.500 paraderos georreferenciados.
* **Aristas (Conexiones):** Extraídas dinámicamente de las secuencias de viaje (`stop_times.txt`).
* **Licencia:** Datos Abiertos / CC BY 4.0.

---
## Datos Crudos:
EL dataset 'stop_times.txt' supera el limite de 50 MB, los datos procesados estan en /data, los datos crudos de 'stops.txt' y 'stops_times.txt' estan en:
    https://drive.google.com/drive/folders/1eQJ7S-DfivQ-RlxMXLr87Km6vAaFXDnw?usp=drive_link
## 🏗️ Arquitectura del Sistema
El proyecto sigue un estándar modular de desarrollo, separando el Pipeline de Datos (ETL) del núcleo de la aplicación:

```text
📁 proyectos/
├── 📁 data/                        # Almacenamiento de archivos crudos y JSON procesado
│   ├── stops.txt                   # (Ignorado en git)
│   ├── stop_times.txt              # (Ignorado en git)
|   ├── gtfs_limpio.json
│   └── arcgis_limpio.json.        # Base de datos en caché para carga en milisegundos
├── 📁 notebooks/                   # Jupyter Notebooks de exploración y ETL
│   ├── 00_prototipo_original.ipynb # Respaldo del prototipo monolítico
│   ├── 01_eda.ipynb                # Análisis Exploratorio de Datos
│   └── 02_limpieza_gtfs.ipynb      # Script que transforma los .txt al archivo .json
├── 📁 outputs/                     # Recursos visuales generados
│   └── dashboard_preview.png       # Captura de la UI
├── .env                            # (Oculto) Token de seguridad
├── .gitignore                      # Reglas de exclusión para GitHub
├── app.py                          # 🚀 Script principal que levanta la interfaz Gradio
├── grafo_logistica.py              # Clase base del Grafo
├── motor_logico.py                 # Algoritmo de Dijkstra y validaciones
├── motor_ia.py                     # Integración con LLM (Modo Local/Cloud)
└── requirements.txt                # Dependencias del proyecto
