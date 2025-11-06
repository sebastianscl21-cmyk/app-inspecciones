import streamlit as st
from PIL import Image
from fpdf import FPDF
import io
import tempfile
from datetime import datetime

st.set_page_config(page_title="App de Inspecciones", layout="centered")

def init_state():
    if 'findings' not in st.session_state:
        st.session_state.findings = []
    if 'machine' not in st.session_state:
        st.session_state.machine = ''
    if 'inspection_type' not in st.session_state:
        st.session_state.inspection_type = 'Inspección mecánica'

def add_finding(image_bytes: bytes, description: str):
    st.session_state.findings.append({
        'image': image_bytes,
        'description': description
    })

def create_pdf(machine_name: str, inspection_type: str, findings: list) -> bytes:
    pdf = FPDF(unit='mm', format='A4')
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.add_page()
    pdf.set_font('Arial', 'B', 16)
    pdf.cell(0, 10, 'Informe de Inspección', ln=True, align='C')
    pdf.ln(5)
    pdf.set_font('Arial', '', 12)
    pdf.cell(0, 8, f'Máquina: {machine_name}', ln=True)
    pdf.cell(0, 8, f'Tipo de inspección: {inspection_type}', ln=True)
    pdf.cell(0, 8, f'Fecha: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}', ln=True)
    pdf.ln(8)
    pdf.set_font('Arial', '', 11)
    pdf.multi_cell(0, 6, f'Total de hallazgos: {len(findings)}')

    for idx, f in enumerate(findings, start=1):
        img_bytes = f['image']
        desc = f['description']

        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
            tmp.write(img_bytes)
            tmp.flush()
            img_path = tmp.name

        pdf.add_page()
        pdf.set_font('Arial', 'B', 12)
        pdf.cell(0, 8, f'Hallazgo {idx}', ln=True)
        pdf.ln(3)

        try:
            pil_img = Image.open(io.BytesIO(img_bytes))
            w_px, h_px = pil_img.size
            available_w = 180
            pdf.image(img_path, x=15, y=pdf.get_y(), w=available_w)
            img_h_mm = (h_px / w_px) * available_w
            pdf.ln(img_h_mm + 4)
        except:
            pdf.set_font('Arial', 'I', 10)
            pdf.multi_cell(0, 6, 'No se pudo insertar la imagen')
            pdf.ln(4)

        pdf.set_font('Arial', '', 11)
        pdf.multi_cell(0, 6, desc)

    out = pdf.output(dest='S').encode('latin-1')
    return out

init_state()
st.title('App de Inspecciones (mecánica / eléctrica)')

with st.form(key='main_form'):
    st.session_state.inspection_type = st.selectbox('Tipo de inspección', 
                                                    ['Inspección mecánica', 'Inspección eléctrica'], index=0)
    st.session_state.machine = st.text_input('Identificación de la máquina')
    st.form_submit_button('Guardar datos básicos')

st.markdown('---')
st.header('Registrar hallazgo')
col1, col2 = st.columns([1, 2])
with col1:
    image_file = st.camera_input('Tomar foto')
    file_upload = st.file_uploader('O cargar desde archivos', type=['jpg','jpeg','png'])

with col2:
    description = st.text_area('Descripción del hallazgo', height=160)
    if st.button('Agregar hallazgo'):
        chosen = image_file if image_file is not None else file_upload
        if chosen is None:
            st.warning('Debe añadir una imagen')
        elif not description.strip():
            st.warning('Debe escribir una descripción')
        else:
            add_finding(chosen.getvalue(), description.strip())
            st.success('Hallazgo agregado')

if st.session_state.findings:
    st.subheader('Hallazgos registrados')
    for i, f in enumerate(st.session_state.findings, start=1):
        cols = st.columns([1, 3])
        with cols[0]:
            st.image(f['image'], use_column_width=True)
        with cols[1]:
            st.write(f"**Descripción {i}:**\n{f['description']}")
            if st.button(f'Eliminar {i}'):
                st.session_state.findings.pop(i-1)
                st.experimental_rerun()

st.markdown('---')
st.header('Generar Informe PDF')
if st.button('Descargar PDF'):
    if not st.session_state.machine.strip():
        st.warning('Ingrese la máquina')
    elif not st.session_state.findings:
        st.warning('No hay hallazgos')
    else:
        pdf_bytes = create_pdf(st.session_state.machine, 
                               st.session_state.inspection_type, 
                               st.session_state.findings)
        st.download_button('Descargar Archivo', data=pdf_bytes,
                           file_name='informe_inspeccion.pdf',
                           mime='application/pdf')