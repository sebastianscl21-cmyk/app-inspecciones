import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os

# Configuración de la página
st.set_page_config(page_title="Inspecciones Técnicas", page_icon="🛠️", layout="centered")

# Inicializar hallazgos
if "findings" not in st.session_state:
    st.session_state.findings = []

# Color corporativo Corona
CORONA_BLUE = (47, 86, 166)

class PDF(FPDF):
    def header(self):
        # Logo Corona (arriba izquierda)
        try:
            self.image("logo_corona.png", x=10, y=8, w=35)
        except:
            pass  # Si el logo no está, no rompe el PDF

        self.set_font("Arial", "B", 12)
        self.set_text_color(*CORONA_BLUE)
        self.cell(0, 10, "🔍 Informe de Inspección Técnica", ln=True, align="C")
        self.ln(4)

        self.set_draw_color(*CORONA_BLUE)
        self.set_line_width(0.8)
        self.line(10, 23, 200, 23)
        self.ln(6)

def add_box(pdf, text):
    pdf.set_fill_color(240, 240, 240)
    pdf.set_draw_color(200, 200, 200)
    pdf.set_line_width(0.4)
    pdf.set_font("Arial", "", 12)
    pdf.multi_cell(0, 8, text, border=1, fill=True)

def generate_pdf(inspection_type, machine_id):
    pdf = PDF()
    pdf.set_auto_page_break(auto=True, margin=12)

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 22)
    pdf.set_text_color(*CORONA_BLUE)
    pdf.ln(25)
    pdf.cell(0, 10, "📋 Informe de Inspección", ln=True, align="C")
    pdf.ln(15)

    pdf.set_font("Arial", "", 12)
    pdf.set_text_color(0)
    add_box(pdf,
        f"🛠️ Tipo: {inspection_type}\n"
        f"🏭 Máquina: {machine_id}\n"
        f"📅 Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )

    # Hallazgos
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.add_page()

        pdf.set_font("Arial", "B", 14)
        pdf.set_text_color(*CORONA_BLUE)
        pdf.cell(0, 10, f"✅ Hallazgo {idx}", ln=True)
        pdf.set_text_color(0)

        img_path = f"temp_{idx}.jpg"
        f["image"].save(img_path)
        pdf.image(img_path, x=15, w=170)
        os.remove(img_path)

        pdf.ln(5)
        pdf.set_font("Arial", "", 11)
        pdf.multi_cell(0, 7, f"📝 Descripción:\n{f['description']}", border=1)

        pdf.ln(3)
        pdf.set_font("Arial", "I", 9)
        pdf.set_text_color(100)
        pdf.cell(0, 6, f"⏱️ {f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}", ln=True)

    pdf_path = "Reporte_Inspeccion.pdf"
    pdf.output(pdf_path)
    return pdf_path


# UI Streamlit
st.title("🔎 Registro de Inspección")

inspection_type = st.selectbox("Tipo de inspección", ["Mecánica", "Eléctrica"])
machine_id = st.text_input("Identificación de la máquina")

st.divider()
st.subheader("Agregar hallazgo 🆕")

opt = st.radio("Seleccionar método", ["📸 Cámara", "📁 Archivo"])
img = st.camera_input("Tomar foto") if opt == "📸 Cámara" else st.file_uploader("Subir imagen", ["jpg", "jpeg", "png"])

desc = st.text_area("Descripción del hallazgo")

if st.button("✅ Guardar hallazgo"):
    if img and desc.strip():
        st.session_state.findings.append({
            "image": Image.open(img),
            "description": desc,
            "timestamp": datetime.now()
        })
        st.success("Hallazgo agregado ✅")
        st.rerun()
    else:
        st.warning("⚠️ Falta imagen o descripción")

st.divider()

if st.session_state.findings:
    st.subheader("📂 Hallazgos")
    for i, f in enumerate(st.session_state.findings, start=1):
        st.image(f["image"], use_container_width=True)
        st.write(f"📝 {f['description']}")
        st.caption(f"⏱️ {f['timestamp']}")
        if st.button(f"🗑️ Eliminar {i}"):
            st.session_state.findings.pop(i-1)
            st.rerun()
else:
    st.info("Sin hallazgos todavía 👷‍♂️")

st.divider()

if st.session_state.findings and machine_id.strip():
    if st.button("📥 Generar PDF"):
        file = generate_pdf(inspection_type, machine_id)
        with open(file, "rb") as f:
            st.download_button(
                "⬇️ Descargar PDF",
                data=f,
                file_name=f"Inspección_{machine_id}.pdf",
                mime="application/pdf"
            )
else:
    st.info("Agrega hallazgos e identifica la máquina")
