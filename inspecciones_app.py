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

# Subida de imagen
uploaded_file = st.file_uploader("📸 Imagen del hallazgo", type=["jpg", "jpeg", "png"])

# Descripción
description = st.text_area("✍️ Descripción del hallazgo")

if st.button("✅ Guardar hallazgo"):
    if uploaded_file and description.strip():
        image = Image.open(uploaded_file)

        st.session_state.findings.append({
            "image": image,
            "description": description,
            "timestamp": datetime.now()
        })
        st.success("Hallazgo guardado")
        st.rerun()
    else:
        st.warning("⚠️ Debes subir una imagen y escribir una descripción.")

st.divider()

# 🔹 Mostrar hallazgos
if st.session_state.findings:
    st.subheader("📌 Hallazgos registrados")

    for i, f in enumerate(st.session_state.findings, start=1):
        st.write(f"### Hallazgo {i}")
        st.image(f["image"], use_container_width=True)
        st.write(f"**Descripción:** {f['description']}")
        st.caption(f"{f['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}")

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
    pdf.cell(0, 10, f"Fecha de generación: {datetime.now().strftime('%Y-%m-%d %H:%M')}", ln=True)

    # Agregar hallazgos
    for idx, f in enumerate(st.session_state.findings, start=1):
        pdf.add_page()
        pdf.set_font("Arial", "B", 14)
        pdf.cell(0, 10, f"Hallazgo {idx}", ln=True)

        # Guardar temporal la imagen
        img_path = f"temp_image_{idx}.jpg"
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

# Botón para descargar PDF
if st.session_state.findings and machine_id.strip():
    if st.button("📥 Generar y Descargar PDF"):
        file = generate_pdf()
        with open(file, "rb") as f:
            st.download_button(
                label="⬇️ Descargar Informe PDF",
                data=f,
                file_name="Reporte_Inspeccion.pdf",
                mime="application/pdf"
            )
else:
    st.info("Completa los datos y registra hallazgos para generar el PDF")
