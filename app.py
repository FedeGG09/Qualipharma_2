import streamlit as st
from document_analysis import (
    extraer_texto_pdf,
    extraer_texto_docx,
    leer_archivo_texto,
    encontrar_diferencias,
    vectorizar_y_tokenizar_diferencias,
    tokenizar_lineamientos,
    almacenar_reglas_vectorizadas,
    cargar_y_vectorizar_manual
)

# Función para procesar documentos
def procesar_documentos(uploaded_reference_file, uploaded_compare_file, reference_file_type, compare_file_type):
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    texto_comparar = extraer_texto(compare_file_type, uploaded_compare_file)

    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    diferencias = encontrar_diferencias(texto_comparar, texto_referencia)

    if diferencias:
        diferencias_vectorizadas = vectorizar_y_tokenizar_diferencias(
            diferencias, tokens_referencia, uploaded_compare_file.name, uploaded_reference_file.name
        )
        st.success("Las diferencias entre los documentos han sido encontradas y vectorizadas.")
        st.header("Diferencias Encontradas")
        diferencias_tabla = [
            [diferencia.get('seccion', 'N/A'), 
             diferencia.get('contenido_referencia', 'N/A'), 
             diferencia.get('contenido_documento', 'N/A'), 
             diferencia.get('tipo', 'N/A'),
             diferencia.get('recomendacion', 'N/A')]
            for diferencia in diferencias_vectorizadas
        ]
        st.table(diferencias_tabla)
    else:
        st.info("No se encontraron diferencias entre los documentos.")

# Función para extraer texto según el tipo de archivo
def extraer_texto(file_type, file):
    if file_type == "pdf":
        return extraer_texto_pdf(file)
    elif file_type == "docx":
        return extraer_texto_docx(file)
    elif file_type == "txt":
        return leer_archivo_texto(file)
    return ""

# Función para cargar y vectorizar el manual
def load_manual(tokens_referencia):
    almacenar_reglas_vectorizadas(tokens_referencia)
    st.success("Manual cargado y vectorizado con éxito.")

# Función para verificar cumplimiento de archivo
def verify_file_compliance(tokens_referencia, texto_comparar):
    diferencias = encontrar_diferencias(texto_comparar, " ".join(tokens_referencia))
    if diferencias:
        st.warning("El documento no cumple con las normativas establecidas en el manual de referencia.")
        st.header("Diferencias Encontradas")
        diferencias_tabla = [
            [diferencia.get('seccion', 'N/A'), 
             diferencia.get('contenido_referencia', 'N/A'), 
             diferencia.get('contenido_documento', 'N/A'), 
             diferencia.get('tipo', 'N/A'),
             diferencia.get('recomendacion', 'N/A')]
            for diferencia in diferencias
        ]
        st.table(diferencias_tabla)
    else:
        st.success("El documento cumple con las normativas establecidas en el manual de referencia.")

# Interfaz Streamlit
st.title("Qualipharma - Analytics Town")

# Cargar archivo de referencia
st.sidebar.header("Cargar Manual de Referencia")
uploaded_reference_file = st.sidebar.file_uploader("Subir archivo de referencia", type=["pdf", "txt", "docx"])
if uploaded_reference_file:
    reference_file_type = uploaded_reference_file.name.split(".")[-1]
    st.sidebar.success(f"Archivo de referencia {uploaded_reference_file.name} cargado con éxito.")

# Cargar archivo a comparar
st.sidebar.header("Cargar Documento a Comparar")
uploaded_compare_file = st.sidebar.file_uploader("Subir archivo a comparar", type=["pdf", "txt", "docx"])
if uploaded_compare_file:
    compare_file_type = uploaded_compare_file.name.split(".")[-1]
    st.sidebar.success(f"Archivo a comparar {uploaded_compare_file.name} cargado con éxito.")

# Botón para procesar los documentos
if st.sidebar.button("Procesar Documentos") and uploaded_reference_file and uploaded_compare_file:
    procesar_documentos(uploaded_reference_file, uploaded_compare_file, reference_file_type, compare_file_type)

# Botón para cargar y vectorizar el manual
if st.sidebar.button("Cargar y Vectorizar Manual") and uploaded_reference_file:
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    load_manual(tokens_referencia)

# Botón para verificar el cumplimiento del archivo
if st.sidebar.button("Verificar Cumplimiento de Archivo") and uploaded_reference_file and uploaded_compare_file:
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    texto_comparar = extraer_texto(compare_file_type, uploaded_compare_file)
    verify_file_compliance(tokens_referencia, texto_comparar)
