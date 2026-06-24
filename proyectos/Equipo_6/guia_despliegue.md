# Guía de Despliegue en Streamlit Cloud

Para que el profesor pueda ver y probar nuestro dashboard de forma gratuita desde cualquier
navegador, usamos **Streamlit Community Cloud**. Sigue estos pasos.

> **Importante:** nuestra app **no está en la raíz** del repositorio, sino dentro de la
> subcarpeta `proyectos/Equipo_6/` (así lo exige la estructura del curso). Por eso las rutas
> de este despliegue apuntan a esa subcarpeta, no a la raíz.

## 1. Verificar los archivos en GitHub

Antes de nada, asegúrate de que en la rama que se va a publicar existan, **dentro de
`proyectos/Equipo_6/`**, estos archivos:

- `app.py` — la aplicación.
- `requirements.txt` — las dependencias (streamlit, pandas, plotly, numpy).
- `data/retail_store_inventory.csv` — el dataset.

La app encuentra el CSV con una ruta relativa al propio `app.py`, así que funciona aunque esté
en una subcarpeta. Si `requirements.txt` no estuviera, el despliegue fallaría.

## 2. Iniciar sesión en Streamlit Cloud

Ve a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión conectando tu cuenta de
GitHub. Esto le da permiso a Streamlit para leer el repositorio.

## 3. Configurar el despliegue

Haz clic en **"Create app"** (o "New app") y completa el formulario con **las rutas correctas**:

- **Repository:** `me1kimu/sic_2026_c-p_cohort_1` (o el repositorio donde quede la versión final)
- **Branch:** la rama donde esté la versión final (por ejemplo `main` una vez consolidado todo)
- **Main file path:** `proyectos/Equipo_6/app.py`  ← **no escribir solo `app.py`**

(Opcional) Personaliza la URL pública, por ejemplo `grupo-seis-retail`.

## 4. Desplegar

Haz clic en **"Deploy"**. Verás una terminal instalando lo del `requirements.txt` (tarda 1-3
minutos). Al terminar, la app carga automáticamente y podrás copiar la URL pública para ponerla
en el README y enviársela al profesor.

## Si el despliegue falla

- **"File does not exist":** revisa que el *Main file path* sea exactamente
  `proyectos/Equipo_6/app.py`.
- **Error instalando dependencias:** revisa que `requirements.txt` esté dentro de
  `proyectos/Equipo_6/`.
- **"FileNotFoundError" del CSV:** confirma que la carpeta `data/` viajó junto al `app.py`
  dentro de `proyectos/Equipo_6/`.
