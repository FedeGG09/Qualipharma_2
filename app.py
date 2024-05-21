import streamlit as st
from document_analysis import (
    extraer_texto_pdf,
    extraer_texto_docx,
    leer_archivo_texto,
    encontrar_diferencias,
    vectorizar_y_tokenizar_diferencias,
    tokenizar_lineamientos,
    almacenar_reglas_vectorizadas,
    cargar_y_vectorizar_manual,
    comparar_con_manual
)

# Define la estructura del manual
indice_manual = [
    "2.1. Minor variations of Type IA",
    "2.1.1. Submission of Type IA notifications",
    "2.1.2. Type IA variations review for mutual recognition procedure",
    "2.1.3. Type IA variations review for purely national procedure",
    "2.1.4. Type IA variations review for centralised procedure",
    "2.2. Minor variations of Type IB",
    "2.2.1. Submission of Type IB notifications",
    "2.2.2. Type IB variations review for mutual recognition procedure",
    "2.2.3. Type IB variations review for purely national procedure",
    "2.2.4. Type IB variations review for centralised procedure",
    "2.3. Major variations of Type II",
    "2.3.1. Submission of Type II applications",
    "2.3.2. Type II variations assessment for mutual recognition procedure",
    "2.3.3. Outcome of Type II variations assessment for mutual recognition procedure",
    "2.3.4. Type II variations assessment for purely national procedure",
    "2.3.5. Outcome of Type II variations assessment for purely national procedure",
    "2.3.6. Type II variations assessment for centralised procedure",
    "2.3.7. Outcome of Type II variations assessment in centralised procedure",
    "2.4. Extensions",
    "2.4.1. Submission of Extensions applications",
    "2.4.2. Extension assessment for national procedure",
    "2.4.3. Extension assessment for centralised procedure"
]

# Interfaz de usuario
st.set_page_config(page_title="Qualipharma - Analytics Town", page_icon="🧪")
st.title("Qualipharma - Analytics Town")

# Sidebar para cargar archivos
st.sidebar.image("https://raw.githubusercontent.com/FedeGG09/Qualipharma_2/main/data/input/cropped-qualipharma_isologo_print-e1590563965410-300x300.png", use_column_width=True)  # Añadir logo
st.sidebar.header("Cargar Manual de Referencia")
uploaded_reference_file = st.sidebar.file_uploader("Subir archivo de referencia", type=["pdf", "txt", "docx"])
if uploaded_reference_file:
    reference_file_type = uploaded_reference_file.name.split(".")[-1]
    st.sidebar.success(f"Archivo de referencia {uploaded_reference_file.name} cargado con éxito.")

st.sidebar.header("Cargar Documento a Comparar")
uploaded_compare_file = st.sidebar.file_uploader("Subir archivo a comparar", type=["pdf", "txt", "docx"])
if uploaded_compare_file:
    compare_file_type = uploaded_compare_file.name.split(".")[-1]
    st.sidebar.success(f"Archivo a comparar {uploaded_compare_file.name} cargado con éxito.")

# Procesamiento de documentos
if st.sidebar.button("Procesar Documentos") and uploaded_reference_file and uploaded_compare_file:
    procesar_documentos(uploaded_reference_file, uploaded_compare_file, reference_file_type, compare_file_type)

# Cargar y vectorizar el manual
if st.sidebar.button("Cargar y Vectorizar Manual") and uploaded_reference_file:
    ruta_manual_vectorizado = cargar_y_vectorizar_manual(uploaded_reference_file, reference_file_type, indice_manual)

# Verificar cumplimiento de archivo
if st.sidebar.button("Verificar Cumplimiento de Archivo") and uploaded_reference_file and uploaded_compare_file:
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    texto_comparar = extraer_texto(compare_file_type, uploaded_compare_file)
    verify_file_compliance(tokens_referencia, texto_comparar)

# Comparar diferencias con manual vectorizado
if st.sidebar.button("Comparar Diferencias con Manual") and uploaded_reference_file and uploaded_compare_file:
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    texto_comparar = extraer_texto(compare_file_type, uploaded_compare_file)
    diferencias = encontrar_diferencias(texto_comparar, texto_referencia)
    if diferencias:
        diferencias_vectorizadas = vectorizar_y_tokenizar_diferencias(
            diferencias, tokens_referencia, uploaded_compare_file.name, uploaded_reference_file.name
        )
        compare_with_manual(diferencias_vectorizadas, tokens_referencia)
