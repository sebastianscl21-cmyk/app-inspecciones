import streamlit as st
from PIL import Image
from datetime import datetime
from fpdf import FPDF
import os

# Configuración de la página
st.set_page_config(page_title="Inspecciones Técnicas", page_icon="🛠️", layout="centered")

# Inicializar hallazgos en sesión
if "findings" not in st.session_state:
    st.session_state.findings = []

# Título
st.title("📋 Registro de Inspección Técnica")

# Selección del tipo de inspección
inspection_type = st.selectbox("Tipo de inspección", ["Mecánica", "Eléctrica"])

# Nombre o código de la máquina
machine_id = st.text_input("Identificación de la máquina")

st.divider()

st.subheader("Registrar nuevo hallazgo")

# Selección de origen de imagen
option = st.radio("¿Cómo deseas agregar la foto?", ["📸 Cámara", "📁 Cargar archivo"])

if option == "📸 Cámara":
    image_file = st.camera_input("Tomar foto")
else:
    image_file = st.file_uploader("Seleccionar imagen", type=["jpg", "jpeg", "png"])

# Descripción del hallazgo
description = st.text_area("✍️ Descripción del hallazgo")

if st.button("✅ Guardar hallazgo"):
    if image_file and description.strip():
        image = Image.open(image_file)

        st.session_state.findings.append({
            "image": image,
            "description": description,
            "timestamp": datetime.now()
        })
        st.success("Hallazgo guardado ✅")
        st.rerun()
    else:
        st.warning("⚠️ Debes tomar o subir una imagen y escribir una descripción.")

st.divider()

# 🔹 Mostrar hallazgos
if st.session_state.findings:
    st.subheader("📌 Hallazgos registrados")

    for i, f in enumerate(st.session_state.findings, start=1):
        st.markdown(f"### Hallazgo {i}")
        st.image(f["image"], use_container_width=True)
        st.write(f"**Descripción:** {f['description']}")
        st.caption(f"🕒 {f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

        if st.button(f"🗑️ Eliminar hallazgo {i}"):
            st.session_state.findings.pop(i-1)
            st.rerun()

else:
    st.info("Aún no hay hallazgos registrados.")

st.divider()

# 📄 Función para generar PDF
def generate_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=10)

    # Portada
    pdf.add_page()
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, "INFORME DE INSPECCIÓN", ln=True, align="C")

    pdf.ln(10)
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, f"Tipo de inspección: {inspection_type}", ln=True)
    pdf.cell(0, 10, f"Máquina: {machine_id}", ln=True)
    pdf.cell(0, 10, f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    # Agregar hallazgos al PDF
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Hallazgo {idx}", ln=True)

        # Guardar temporales
        img_path = f"temp_img_{idx}.jpg"
        f["image"].save(img_path)

        pdf.ln(5)
        pdf.image(img_path, w=160)
        os.remove(img_path)

        pdf.ln(5)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 8, f["description"])

    pdf_path = "Reporte_Inspeccion.pdf"
    pdf.output(pdf_path)
    return pdf_path

# Botón para generar PDF
if st.session_state.findings and machine_id.strip():
    if st.button("📥 Generar y Descargar PDF"):
        file = generate_pdf()
        with open(file, "rb") as f:
            st.download_button(
                "⬇️ Descargar PDF",
                data=f,
                file_name="Reporte_Inspeccion.pdf",
                mime="application/pdf"
            )
else:
    st.info("Completa los datos y registra hallazgos para generar el PDF.")
