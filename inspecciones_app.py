import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os
import tempfile
import uuid

# ---------------------------
# Config y opciones
# ---------------------------
st.set_page_config(page_title="Inspecciones Técnicas", page_icon="🛠️", layout="centered")

# 📌 Eliminar opción deprecada que causaba error en versiones nuevas
# st.set_option('deprecation.showfileUploaderEncoding', False)

# Nombre del PDF de salida
PDF_OUTPUT_NAME = "Reporte_Inspeccion.pdf"

# ---------------------------
# Inicializar session_state
# ---------------------------
if "findings" not in st.session_state:
    st.session_state.findings = []
if "cam_key_counter" not in st.session_state:
    st.session_state.cam_key_counter = 0
if "uploader_key_counter" not in st.session_state:
    st.session_state.uploader_key_counter = 0

# ---------------------------
# Clase PDF (sin emojis y diseño limpio)
# ---------------------------
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.set_text_color(40, 40, 40)
        self.cell(0, 10, "Informe de Inspección Técnica", ln=True, align="C")
        self.ln(2)
        self.set_draw_color(0, 102, 204)
        self.set_line_width(0.7)
        self.line(10, 22, 200, 22)

def add_box(pdf, text):
    pdf.set_fill_color(245, 245, 245)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.3)
    pdf.set_font("Arial", "", 11)
    pdf.multi_cell(0, 8, text, border=1, fill=True)

def generate_pdf(inspection_type, machine_id):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 18)
    pdf.set_text_color(0, 102, 204)
    pdf.ln(20)
    pdf.cell(0, 10, "Informe de Inspección", ln=True, align="C")
    pdf.ln(10)

    # Caja datos generales
    pdf.set_text_color(0)
    add_box(pdf,
        f"Tipo de inspección: {inspection_type}\n"
        f"Máquina: {machine_id}\n"
        f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Páginas de hallazgos
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.add_page()
        pdf.set_font("Arial", "B", 13)
        pdf.set_text_color(0, 102, 204)
        pdf.cell(0, 10, f"Hallazgo {idx}", ln=True)

        # Procesar imagen temporalmente
        try:
            img_temp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            temp_path = img_temp.name
            img_temp.close()

            img = f["image"]
            if img.mode != "RGB":
                img = img.convert("RGB")
            img.save(temp_path, format="JPEG", quality=85)

            pdf.image(temp_path, x=15, w=170)
            os.remove(temp_path)
        except Exception as e:
            pdf.set_font("Arial", "I", 10)
            pdf.set_text_color(150, 0, 0)
            pdf.multi_cell(0, 6, f"(No se pudo incrustar la imagen: {e})")
            pdf.set_text_color(0)

        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"Descripción:\n{f['description']}", border=1)

        pdf.ln(3)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100)
        pdf.cell(0, 6, f"Registrado el: {f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    # Guardar PDF
    out_path = PDF_OUTPUT_NAME
    pdf.output(out_path)
    return out_path

# ---------------------------
# UI Streamlit
# ---------------------------
st.title("🔎 Registro de Inspección")

inspection_type = st.selectbox("Tipo de inspección", ["Mecánica", "Eléctrica"])
machine_id = st.text_input("Identificación de la máquina")

st.divider()
st.subheader("Agregar hallazgo")

# 👇 Keys dinámicas: evitan error de repetición en móviles
cam_key = f"cam_{st.session_state.cam_key_counter}"
uploader_key = f"up_{st.session_state.uploader_key_counter}"

opt = st.radio("Seleccionar método de imagen:", ["📸 Cámara", "📁 Cargar Archivo"], horizontal=True)

if opt == "📸 Cámara":
    img_input = st.camera_input("Tomar foto", key=cam_key)
else:
    img_input = st.file_uploader("Subir imagen", type=["jpg", "jpeg", "png"], key=uploader_key)

desc = st.text_area("Descripción del hallazgo", height=150)

if st.button("Guardar hallazgo"):
    if img_input and desc.strip():
        try:
            pil_img = Image.open(img_input)
            st.session_state.findings.append({
                "image": pil_img,
                "description": desc.strip(),
                "timestamp": datetime.now()
            })
            st.session_state.cam_key_counter += 1
            st.session_state.uploader_key_counter += 1
            st.success("✅ Hallazgo guardado.")
        except Exception as e:
            st.error(f"No se pudo procesar la imagen: {e}")
    else:
        st.warning("📌 Debes subir/tomar imagen y escribir descripción.")

st.divider()

# Lista de hallazgos
if st.session_state.findings:
    st.subheader("Hallazgos registrados")
    for i, f in enumerate(st.session_state.findings, start=1):
        st.markdown(f"**Hallazgo {i}**")
        st.image(f["image"], use_container_width=True)
        st.write(f["description"])
        st.caption(f"{f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")
        
        if st.button(f"Eliminar {i}", key=f"del_{i}_{uuid.uuid4().hex}"):
            st.session_state.findings.pop(i - 1)
            st.session_state.cam_key_counter += 1
            st.session_state.uploader_key_counter += 1
            st.success("🗑️ Eliminado")

else:
    st.info("📌 No hay hallazgos aún.")

st.divider()

if st.session_state.findings and machine_id.strip():
    if st.button("Generar y descargar PDF"):
        try:
            pdf_path = generate_pdf(inspection_type, machine_id)
            with open(pdf_path, "rb") as fh:
                st.download_button("⬇️ Descargar Informe (PDF)",
                                   data=fh,
                                   file_name=pdf_path,
                                   mime="application/pdf")
        except Exception as e:
            st.error(f"Error generando PDF: {e}")
else:
    st.info("🔐 Ingresa máquina y registra al menos un hallazgo.")
