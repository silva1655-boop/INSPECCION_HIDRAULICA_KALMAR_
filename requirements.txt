# Inspección hidráulica

Este repositorio contiene una aplicación **Streamlit** para realizar
inspecciones de sistemas hidráulicos de equipos de manutención. La app
muestra imágenes de referencia y permite documentar el estado de cada
componente, anotar observaciones y tomar fotos de anomalías.

## Contenido

- `inspeccion_app.py` – script principal de la aplicación.
- `images/` – carpeta con las siete imágenes de referencia usadas en el formulario.
- `requirements.txt` – dependencias Python para ejecutar la app en Streamlit Community Cloud o localmente.
- `README.md` – este archivo con instrucciones de uso.

## Uso local

1. Clona o descarga este repositorio.

2. (Opcional) Crea un entorno virtual y actívalo:
   ```bash
   python -m venv venv
   source venv/bin/activate  # en Windows: venv\Scripts\activate
   ```

3. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
   ```

4. Ejecuta la app con Streamlit:
   ```bash
   streamlit run inspeccion_app.py
   ```

5. Accede al enlace local que mostrará Streamlit en el navegador y completa el formulario. Al guardar, se creará/actualizará el archivo
   `registro_inspecciones.xlsx` y se guardarán las fotos en la carpeta `evidence/`.

## Despliegue en Streamlit Community Cloud

1. Crea un repositorio en GitHub con el contenido de este proyecto.
2. Inicia sesión en [Streamlit Community Cloud](https://share.streamlit.io/) y selecciona **Create app**.
3. Selecciona tu repositorio y rama, y define `inspeccion_app.py` como el archivo principal.
4. Configura la versión de Python (recomendado: 3.11 o 3.12) y haz clic en **Deploy**.
5. La app se desplegará y podrás compartir el enlace con tu equipo.

Nota: Streamlit Community Cloud no garantiza la persistencia de archivos generados; para un uso productivo se recomienda almacenar los datos en una base de datos o Google Sheets.
