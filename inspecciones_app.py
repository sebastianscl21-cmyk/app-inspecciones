import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os
import tempfile

# ---------------------------
# Config / constantes
# ---------------------------
st.set_page_config(page_title="Inspecciones Técnicas • Corona", page_icon="🛠️", layout="centered")
CORONA_RGB = (47, 86, 166)  # color principal (azul Corona)
LOGO_FILENAME = "logo_corona.png"
FONT_FILENAME = "DejaVuSans.ttf"  # debe existir en el mismo folder

# ---------------------------
# Session init
# ---------------------------
if "findings" not in st.session_state:
    st.session_state.findings = []

# ---------------------------
# PDF helper (fpdf2 + Unicode)
# ---------------------------
class UnicodePDF(FPDF):
    def header(self):
        # Intentar insertar logo (si existe)
        try:
            if os.path.exists(LOGO_FILENAME):
                # tamaño adecuado en mm
                self.image(LOGO_FILENAME, x=10, y=8, w=30)
        except Exception:
            pass

        # Título centrado
        self.set_font("DejaVu", "B", 12)
        self.set_text_color(*CORONA_RGB)
        self.cell(0, 10, "🔍 Informe de Inspección Técnica", ln=True, align="C")
        self.ln(2)
        # línea azul
        self.set_draw_color(*CORONA_RGB)
        self.set_line_width(0.8)
        self.line(10, 23, 200, 23)
        self.ln(6)

def generate_pdf(inspection_type: str, machine_id: str) -> str:
    # Verificar fuente
    if not os.path.exists(FONT_FILENAME):
        raise FileNotFoundError(f"La fuente '{FONT_FILENAME}' no fue encontrada. Colócala en la carpeta del script.")

    pdf = UnicodePDF()
    # Registrar fuente Unicode
    pdf.add_page()  # añadir página temprana para registrar fuente visualmente estable; fpdf2 permite add_font luego también
    pdf.add_font("DejaVu", "", FONT_FILENAME, uni=True)
    pdf.add_font("DejaVu", "B", FONT_FILENAME, uni=True)

    # Regenerar documento (mejor limpiar la primera página en blanco)
    pdf = UnicodePDF()
    pdf.add_font("DejaVu", "", FONT_FILENAME, uni=True)
    pdf.add_font("DejaVu", "B", FONT_FILENAME, uni=True)
    pdf.set_auto_page_break(auto=True, margin=12)

    # ---- Portada ----
    pdf.add_page()
    pdf.set_font("DejaVu", "B", 22)
    pdf.set_text_color(*CORONA_RGB)
    pdf.ln(10)
    pdf.cell(0, 10, "📋 Informe de Inspección", ln=True, align="C")
    pdf.ln(8)

    # Info en recuadro
    pdf.set_font("DejaVu", "", 11)
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(220, 220, 220)
    left = 20
    width = 170
    # caja con datos
    txt = (
        f"🛠️  Tipo de inspección: {inspection_type}\n"
        f"🏷️  Máquina: {machine_id}\n"
        f"📅  Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
        f"📄  Total hallazgos: {len(st.session_state.findings)}"
    )
    # Dibujar un multi-cell con fondo rellenado (simular caja)
    x_before = pdf.get_x()
    y_before = pdf.get_y()
    pdf.set_xy(left, y_before)
    pdf.multi_cell(width, 7, txt, border=1, fill=True)
    pdf.ln(6)

    # ---- Hallazgos: texto primero, foto debajo ----
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.add_page()
        # Título del hallazgo
        pdf.set_font("DejaVu", "B", 14)
        pdf.set_text_color(*CORONA_RGB)
        pdf.cell(0, 8, f"✔ Hallazgo {idx}", ln=True)
        pdf.ln(2)

        # Descripción
        pdf.set_font("DejaVu", "", 11)
        pdf.set_text_color(10, 10, 10)
        # Añadimos un pequeño recuadro con la descripción
        desc_txt = f["description"]
        pdf.set_fill_color(255, 255, 255)
        pdf.set_draw_color(220, 220, 220)
        pdf.multi_cell(0, 6, "Descripción:\n" + desc_txt, border=1)

        pdf.ln(4)

        # Imagen (debajo del texto)
        try:
            # Guardar temporal en formato JPEG con conversión RGB
            with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as tmp:
                temp_img_path = tmp.name
            img = f["image"]
            # Asegurar RGB
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(temp_img_path, format="JPEG", quality=85)

            # Insertar imagen centrada con margen
            pdf.image(temp_img_path, x=15, w=180)  # ancho máximo 180mm en A4 con márgenes
            os.remove(temp_img_path)
        except Exception as e:
            pdf.set_font("DejaVu", "", 10)
            pdf.set_text_color(150, 0, 0)
            pdf.multi_cell(0, 6, f"(No se pudo incrustar la imagen: {e})")

        pdf.ln(6)
        # Metadata del hallazgo
        pdf.set_font("DejaVu", "I", 9)
        pdf.set_text_color(110, 110, 110)
        pdf.cell(0, 5, f"Registrado: {f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Exportar a archivo temporal y retornarlo
    out_path = "Reporte_Inspeccion_Corona.pdf"
    pdf.output(out_path)
    return out_path

# ---------------------------
# UI Streamlit
# ---------------------------
st.title("🔎 Registro de Inspección • Corona")

col1, col2 = st.columns([3, 1])
with col1:
    inspection_type = st.selectbox("Tipo de inspección", ["Mecánica", "Eléctrica"])
    machine_id = st.text_input("Identificación de la máquina", help="Nombre o código de la máquina")

with col2:
    # Mostrar logo en la UI si está disponible
    if os.path.exists(LOGO_FILENAME):
        st.image(LOGO_FILENAME, use_column_width=True)
    else:
        st.info("Coloca 'logo_corona.png' en la carpeta para que aparezca en el PDF.")

st.markdown("---")
st.subheader("Agregar nuevo hallazgo")

# Opción: cámara o archivo
method = st.radio("Agregar foto desde:", ["📸 Cámara", "📁 Archivo"], horizontal=True)
img_input = None
if method == "📸 Cámara":
    img_input = st.camera_input("Tomar foto")
else:
    img_input = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png"])

description = st.text_area("Descripción del hallazgo", height=150)

if st.button("✅ Guardar hallazgo"):
    if img_input is None or not description.strip():
        st.warning("Por favor toma/sube una imagen y escribe la descripción.")
    else:
        # Abrir imagen como PIL
        try:
            pil_img = Image.open(img_input)
        except Exception as e:
            st.error(f"No se pudo leer la imagen: {e}")
            pil_img = None

        if pil_img:
            st.session_state.findings.append({
                "image": pil_img,
                "description": description.strip(),
                "timestamp": datetime.now()
            })
            st.success("Hallazgo agregado ✅")
            st.rerun()

st.markdown("---")

# Mostrar hallazgos actuales
st.subheader("📂 Hallazgos registrados")
if st.session_state.findings:
    for i, f in enumerate(st.session_state.findings, start=1):
        st.markdown(f"**Hallazgo {i}**")
        st.image(f["image"], use_container_width=True)
        st.write(f["description"])
        st.caption(f"{f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        if st.button(f"🗑️ Eliminar {i}"):
            st.session_state.findings.pop(i - 1)
            st.rerun()
else:
    st.info("Aún no hay hallazgos. Agrega el primero arriba.")

st.markdown("---")

# Botón generar PDF (solo si hay hallazgos y máquina)
if st.session_state.findings and machine_id.strip():
    if st.button("📥 Generar y descargar PDF"):
        try:
            pdf_file = generate_pdf(inspection_type, machine_id)
            with open(pdf_file, "rb") as fh:
                pdf_bytes = fh.read()
            st.download_button("⬇️ Descargar Informe (PDF)", data=pdf_bytes,
                               file_name=f"Inspeccion_{machine_id}.pdf",
                               mime="application/pdf")
        except FileNotFoundError as fe:
            st.error(str(fe))
        except Exception as e:
            st.error(f"Ocurrió un error generando el PDF: {e}")
else:
    st.info("Completa la identificación de la máquina y agrega hallazgos para generar el PDF.")
