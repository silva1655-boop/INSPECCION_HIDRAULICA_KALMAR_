import datetime
from pathlib import Path
from typing import List, Dict, Any

import pandas as pd
import streamlit as st


# =========================
# CONFIGURACIÓN GENERAL
# =========================
st.set_page_config(
    page_title="Inspección hidráulica",
    layout="centered",
)


# =========================
# UTILIDADES
# =========================
def find_images_dir() -> Path:
    """Busca la carpeta images en varias ubicaciones posibles."""
    base_dir = Path(__file__).resolve().parent
    candidates = [
        base_dir / "images",
        base_dir.parent / "images",
        Path.cwd() / "images",
        Path("images"),
    ]

    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate

    # Devuelve la primera opción aunque no exista, para mostrar la ruta esperada
    return candidates[0]


def load_reference_images() -> List[Dict[str, Any]]:
    """Retorna la lista de imágenes de referencia."""
    image_dir = find_images_dir()

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

    return [
        {
            "title": title,
            "path": image_dir / filename,
        }
        for title, filename in image_filenames
    ]


def initialize_excel(excel_path: Path, columns: List[str]) -> pd.DataFrame:
    """Crea el Excel si no existe y devuelve el DataFrame actual."""
    if excel_path.exists():
        try:
            return pd.read_excel(excel_path)
        except Exception:
            return pd.DataFrame(columns=columns)

    df = pd.DataFrame(columns=columns)
    df.to_excel(excel_path, index=False)
    return df


def append_to_excel(df: pd.DataFrame, row: Dict[str, Any], excel_path: Path) -> None:
    """Agrega una fila al Excel usando concat."""
    new_df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    new_df.to_excel(excel_path, index=False)


def save_uploaded_image(uploaded_bytes: bytes, output_dir: Path, prefix: str) -> str:
    """Guarda la imagen capturada y devuelve el nombre del archivo."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S%f")
    filename = f"{prefix}_{timestamp}.png"
    output_dir.mkdir(parents=True, exist_ok=True)
    out_path = output_dir / filename

    with open(out_path, "wb") as f:
        f.write(uploaded_bytes)

    return filename


# =========================
# APP PRINCIPAL
# =========================
def main() -> None:
    st.title("Formulario de inspección de sistemas hidráulicos")
    st.write(
        "Complete los datos generales y revise cada imagen de referencia. "
        "Seleccione el estado, agregue observaciones y tome una fotografía "
        "si detecta daño, fuga o anomalía."
    )

    images_info = load_reference_images()
    images_dir = find_images_dir()

    with st.expander("Verificación rápida de archivos", expanded=False):
        st.write(f"Carpeta de imágenes detectada: `{images_dir}`")
        for info in images_info:
            st.write(f"- {info['path'].name}: {'✅' if info['path'].exists() else '❌'}")

    # Columnas del registro
    base_columns = ["fecha", "inspector", "equipo"]
    for idx in range(1, len(images_info) + 1):
        prefix = f"comp{idx}"
        base_columns.extend(
            [
                f"{prefix}_estado",
                f"{prefix}_observaciones",
                f"{prefix}_foto",
            ]
        )

    excel_path = Path("registro_inspecciones.xlsx")
    evidence_dir = Path("evidence")
    df_existing = initialize_excel(excel_path, base_columns)

    with st.form("inspection_form"):
        col1, col2 = st.columns(2)
        with col1:
            fecha = st.date_input("Fecha de inspección", value=datetime.date.today())
            inspector = st.text_input("Nombre del inspector")
        with col2:
            equipo = st.text_input("Equipo / Número de serie")

        responses: Dict[int, Dict[str, Any]] = {}

        for idx, info in enumerate(images_info, start=1):
            st.markdown("---")
            st.subheader(info["title"])

            img_path = Path(info["path"])
            if img_path.exists():
                st.image(str(img_path), use_container_width=True)
            else:
                st.warning(f"No se encontró la imagen de referencia: {img_path.name}")
                st.caption(f"Ruta buscada: {img_path}")

            estado = st.radio(
                f"Estado del elemento {idx}",
                ["Bueno", "Regular", "Malo"],
                horizontal=True,
                key=f"estado_{idx}",
            )

            observaciones = st.text_area(
                f"Observaciones / Fugas detectadas para el elemento {idx}",
                key=f"observaciones_{idx}",
                placeholder="Ej.: fuga en terminal, flexible cuarteado, roce, humedad, daño en funda, etc.",
            )

            foto_file = st.camera_input(
                f"Capturar foto de daños (opcional) para el elemento {idx}",
                key=f"foto_{idx}",
            )

            responses[idx] = {
                "estado": estado,
                "observaciones": observaciones,
                "foto_data": foto_file,
            }

        submitted = st.form_submit_button("Guardar inspección")

    if submitted:
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
        st.success("Inspección guardada correctamente.")
        st.info(f"Registro actualizado: {excel_path.resolve()}")


if __name__ == "__main__":
    main()
