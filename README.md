"""
Aplicación de Streamlit para realizar inspecciones de sistemas hidráulicos.

Esta aplicación muestra imágenes de referencia de flexibles hidráulicos, válvulas y
cilindros y permite al inspector evaluar el estado de cada elemento. Por cada
imagen se selecciona un estado (Bueno, Regular, Malo), se escriben
observaciones y opcionalmente se captura una foto con la cámara del dispositivo.
Al enviar el formulario, las respuestas se guardan en un archivo Excel y las
fotos capturadas se almacenan en una carpeta de evidencias.

Para ejecutar la aplicación:
1. Instala las dependencias de ``requirements.txt``.
2. Ejecuta ``streamlit run inspeccion_app.py`` dentro de la carpeta del proyecto.
3. Abre el enlace que Streamlit muestra en el navegador.

Ten en cuenta que Streamlit Community Cloud no garantiza persistencia
permanente de archivos generados por la app; para uso productivo se recomienda
conectar una base de datos o una hoja de cálculo en la nube.
"""

import datetime
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import streamlit as st


def load_reference_images() -> List[Dict[str, Any]]:
    """Carga la lista de imágenes de referencia localizando la carpeta ``images``.

    La función intenta encontrar la carpeta ``images`` de varias maneras para
    hacer la aplicación más robusta en entornos de despliegue donde el nombre
    de la carpeta raíz puede variar (por ejemplo, sufijos agregados por
    plataformas de alojamiento). Se comprueban tres posibles ubicaciones:

    1. La subcarpeta ``images`` situada junto al archivo fuente (``__file__``).
    2. La subcarpeta ``images`` situada en la carpeta padre del archivo fuente.
    3. La subcarpeta ``images`` situada en el directorio de trabajo actual.

    Si ninguna de estas carpetas existe, se utilizará la primera opción por
    defecto. En cualquier caso, las rutas de los archivos se devolverán aunque
    no existan y el código principal avisará con un mensaje de advertencia.
    """
    base_dir = Path(__file__).resolve().parent
    # Candidatos para la carpeta de imágenes
    candidate_dirs = [
        base_dir / "images",
        base_dir.parent / "images",
        Path.cwd() / "images",
    ]
    image_dir: Path = candidate_dirs[0]
    for candidate in candidate_dirs:
        if candidate.is_dir():
            image_dir = candidate
            break

    # Lista de títulos y nombres de archivo esperados
    image_filenames = [
        (
            "Conjunto de flexibles y componentes (Vista 1)",
            "5835788d-17c6-4868-b511-9f1d8c6ca27c.png",
        ),
        (
            "Conjunto de flexibles y componentes (Vista 2)",
            "76164296-abbd-4216-b789-a85bebff607f.png",
        ),
        (
            "Conjunto de flexibles y componentes (Vista 3)",
            "7b28b868-8f14-4cc6-a84b-2fef321e2a55.png",
        ),
        (
            "Conjunto de flexibles y componentes (Vista 4)",
            "10d3488f-5cf0-42c4-8bb7-004b29b53513.png",
        ),
        (
            "Detalle de flexibles y válvulas (Vista 5)",
            "39ded217-dd8e-4355-9395-a9f3ffd9ef3c.png",
        ),
        (
            "Detalle de componentes (Vista 6)",
            "aa8a9f13-1bb5-4b81-a2ac-db56dfa06993.png",
        ),
        (
            "Detalle de sistema hidráulico (Vista 7)",
            "a3adf982-8286-4f0b-b58f-57ce85ae84cf.png",
        ),
    ]
    images_info: List[Dict[str, Any]] = []
    for title, filename in image_filenames:
        images_info.append(
            {
                "title": title,
                "path": image_dir / filename,
            }
        )
    return images_info


def initialize_excel(excel_path: Path, columns: List[str]) -> pd.DataFrame:
    """Crea el archivo Excel si no existe y devuelve su DataFrame.

    Si el archivo existe, lo abre y devuelve el DataFrame. Si no, crea un
    DataFrame vacío con las columnas proporcionadas y lo guarda para futuras
    escrituras.
    """
    if excel_path.exists():
        return pd.read_excel(excel_path)
    df = pd.DataFrame(columns=columns)
    df.to_excel(excel_path, index=False)
    return df


def append_to_excel(df: pd.DataFrame, row: Dict[str, Any], excel_path: Path) -> None:
    """Anexa una fila al archivo Excel y guarda el resultado.

    Debido a que ``DataFrame.append`` está deprecado en pandas >= 2, se
    utiliza ``pd.concat`` para unir el DataFrame existente con la nueva fila y
    luego se escribe el Excel de vuelta.
    """
    new_df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    new_df.to_excel(excel_path, index=False)


def save_uploaded_image(uploaded_bytes: bytes, output_dir: Path, prefix: str) -> str:
    """Guarda una imagen capturada o subida en la carpeta de evidencias.

    Genera un nombre único basado en la fecha y hora actual y lo devuelve.
    """
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
    filename = f"{prefix}_{timestamp}.png"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename
    with open(out_path, "wb") as f:
        f.write(uploaded_bytes)
    return filename


def main() -> None:
    """Ejecuta la aplicación Streamlit."""
    st.set_page_config(page_title="Inspección hidráulica", layout="centered")
    st.title("Formulario de inspección de sistemas hidráulicos")
    st.write(
        "Complete los datos generales y revise cada imagen de referencia. "
        "Seleccione el estado correspondiente, anote observaciones y capture una foto si observa anomalías."
    )

    images_info = load_reference_images()

    # Definir columnas para el Excel: tres datos generales y tres por cada imagen
    base_columns = ["fecha", "inspector", "equipo"]
    for idx in range(1, len(images_info) + 1):
        prefix = f"comp{idx}"
        base_columns.extend([
            f"{prefix}_estado",
            f"{prefix}_observaciones",
            f"{prefix}_foto",
        ])

    excel_path = Path("registro_inspecciones.xlsx")
    df_existing = initialize_excel(excel_path, base_columns)

    evidence_dir = Path("evidence")

    # Definir el formulario
    with st.form("inspection_form"):
        fecha = st.date_input("Fecha de inspección", value=datetime.date.today())
        inspector = st.text_input("Nombre del inspector")
        equipo = st.text_input("Equipo/Número de serie")

        responses = {}
        for idx, info in enumerate(images_info, start=1):
            st.subheader(info["title"])
            img_path = Path(info["path"])
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.warning(f"No se encontró la imagen de referencia: {img_path.name}")
                st.caption(f"Ruta buscada: {img_path}")
            # Estado del componente
            estado = st.radio(
                f"Estado del elemento {idx}",
                ["Bueno", "Regular", "Malo"],
                index=0,
                key=f"estado_{idx}",
            )
            # Observaciones
            observ = st.text_area(
                f"Observaciones / Fugas detectadas para el elemento {idx}",
                key=f"observ_{idx}",
            )
            # Captura de foto
            foto_file = st.camera_input(
                f"Capturar foto de daños (opcional) para el elemento {idx}",
                key=f"foto_{idx}",
            )
            responses[idx] = {
                "estado": estado,
                "observaciones": observ,
                "foto_data": foto_file,
            }

        submitted = st.form_submit_button("Guardar inspección")

    if submitted:
        # Construir la fila para agregar
        new_row: Dict[str, Any] = {
            "fecha": fecha,
            "inspector": inspector,
            "equipo": equipo,
        }
        for idx in range(1, len(images_info) + 1):
            prefix = f"comp{idx}"
            estado = responses[idx]["estado"]
            observaciones = responses[idx]["observaciones"]
            foto_widget = responses[idx]["foto_data"]
            foto_filename = ""
            if foto_widget is not None:
                image_bytes = foto_widget.getvalue()
                foto_filename = save_uploaded_image(image_bytes, evidence_dir, prefix)
            new_row[f"{prefix}_estado"] = estado
            new_row[f"{prefix}_observaciones"] = observaciones
            new_row[f"{prefix}_foto"] = foto_filename
        append_to_excel(df_existing, new_row, excel_path)
        st.success("¡Inspección guardada correctamente!")


if __name__ == "__main__":
    main()
