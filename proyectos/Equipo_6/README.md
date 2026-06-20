# MVP: Sistema Inteligente de Predicción de Ventas y Gestión de Inventario para Retail

Este proyecto consiste en un Producto Mínimo Viable (MVP) desarrollado en una semana para el sector retail. Su objetivo principal es optimizar la gestión de inventario y prevenir quiebres de stock mediante predicciones de demanda algorítmicas, presentadas a través de un dashboard interactivo e intuitivo construido en Streamlit.

El modelo y las lógicas de negocio utilizan el conjunto de datos `Retail Store Inventory Forecasting Dataset`.

## Estructura del Proyecto

El repositorio está estructurado de la siguiente manera:

* `notebooks/01_eda.ipynb`: Análisis Exploratorio de Datos (EDA) para comprender las distribuciones, valores atípicos y patrones en el inventario y las ventas históricas.
* `notebooks/02_modelo.ipynb`: Entrenamiento, validación y evaluación de los algoritmos de predicción de la demanda.
* `inventory_risk.py`: Módulo de procesamiento que calcula la métrica de riesgo de quiebre de stock y genera alertas accionables.
* `app.py`: Archivo principal de la aplicación Streamlit que renderiza el panel de control interactivo.

## Capturas del Dashboard

* `[Placeholder: Insertar captura de pantalla de la vista general (KPIs principales y métricas globales) aquí]`
* `[Placeholder: Insertar captura de pantalla del ranking de productos con riesgo "Alto" aquí]`
* `[Placeholder: Insertar captura de pantalla del gráfico interactivo de predicción de demanda aquí]`

## Instalación y Ejecución en Local

Sigue estos pasos para ejecutar el proyecto en tu máquina local. Se requiere Python 3.8 o superior.

1. **Clonar el repositorio:**
   ```bash
   git clone <URL_DEL_REPOSITORIO>
   cd <NOMBRE_DEL_DIRECTORIO>
   ```

2. **Instalar dependencias:**
   Se recomienda crear un entorno virtual previamente. Luego, instala las librerías necesarias:
   ```bash
   pip install -r requirements.txt
   ```

3. **Ejecutar la aplicación:**
   Levanta el servidor local de Streamlit ejecutando:
   ```bash
   streamlit run app.py
   ```
