# Guía de Despliegue en Streamlit Cloud

Para que el profesor pueda ver y probar nuestro dashboard de forma gratuita desde cualquier navegador, utilizaremos **Streamlit Community Cloud**. Sigue estos 4 pasos:

1. **Verificar el archivo `requirements.txt`:**
   Antes de hacer nada, asegúrate de que todos los cambios (incluido `app.py` y el módulo de riesgo) estén subidos a GitHub (en la rama `main`). **Crucial:** Verifica que en la raíz exista el archivo `requirements.txt` con todas las dependencias listadas (ej. `streamlit`, `pandas`, `numpy`, `scikit-learn`). Si este archivo no está, el despliegue fallará.

2. **Iniciar sesión en Streamlit Cloud:**
   Ve a [share.streamlit.io](https://share.streamlit.io/) e inicia sesión conectando tu cuenta de GitHub. Esto le dará permisos a Streamlit para leer nuestro repositorio.

3. **Configurar el despliegue:**
   - Haz clic en el botón azul **"New app"**.
   - En el formulario, selecciona nuestro repositorio en el campo **Repository**.
   - En **Branch**, selecciona `main`.
   - En **Main file path**, escribe `app.py`.

4. **¡Desplegar!**
   - Haz clic en **"Deploy!"**. Verás una terminal donde Streamlit comienza a instalar las cosas del `requirements.txt`. Toma un par de minutos. Al finalizar, la app cargará automáticamente y podrás copiar la URL pública para enviársela al profesor.
