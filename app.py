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

# Interfaz Streamlit
st.set_page_config(page_title="Qualipharma - Analytics Town", page_icon="🧪")
st.title("Qualipharma - Analytics Town")

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

if st.sidebar.button("Procesar Documentos") and uploaded_reference_file and uploaded_compare_file:
    procesar_documentos(uploaded_reference_file, uploaded_compare_file, reference_file_type, compare_file_type)

if st.sidebar.button("Cargar y Vectorizar Manual") and uploaded_reference_file:
    # Llamar a la función para cargar y vectorizar el manual
    texto_manual = extraer_texto(reference_file_type, uploaded_reference_file)
    indice_manual = [...]  # Define el índice manual aquí
    ruta_manual_vectorizado = cargar_y_vectorizar_manual(uploaded_reference_file, reference_file_type, texto_manual, indice_manual)

if st.sidebar.button("Verificar Cumplimiento de Archivo") and uploaded_reference_file and uploaded_compare_file:
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    texto_comparar = extraer_texto(compare_file_type, uploaded_compare_file)
    verify_file_compliance(tokens_referencia, texto_comparar)

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
