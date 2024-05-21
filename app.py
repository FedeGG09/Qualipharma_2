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
def load_manual(tokens_referencia, texto_manual, indice_manual):
    almacenar_reglas_vectorizadas(tokens_referencia, texto_manual)
    st.success("Manual cargado y vectorizado con éxito.")

# Función para verificar cumplimiento de archivo
def verify_file_compliance(tokens_referencia, texto_comparar):
    diferencias = encontrar_diferencias(texto_comparar, " ".join(tokens_referencia))
    if diferencias:
        st.warning("El documento no cumple con las normativas establecidas en el manual de referencia.")
        st.header("Diferencias Encontradas")
        for diferencia in diferencias:
            st.markdown(f"### {diferencia['seccion']}")
            st.markdown(f"**Contenido de referencia:** {diferencia['contenido_referencia']}")
            st.markdown(f"**Contenido del documento:** {diferencia['contenido_documento']}")
            st.markdown(f"**Recomendación:** {diferencia['recomendacion']}")
    else:
        st.success("El documento cumple con las normativas establecidas en el manual de referencia.")

# Función para comparar documento con manual vectorizado
def compare_with_manual(diferencias_vectorizadas, tokens_referencia):
    resultado_comparacion = comparar_con_manual(diferencias_vectorizadas, tokens_referencia)
    if resultado_comparacion:
        st.warning("Las diferencias encontradas no cumplen con el manual vectorizado.")
        st.header("Diferencias con el Manual")
        for resultado in resultado_comparacion:
            st.markdown(f"### {resultado['seccion']}")
            st.markdown(f"**Contenido de referencia:** {resultado['contenido_referencia']}")
            st.markdown(f"**Contenido del documento:** {resultado['contenido_documento']}")
            st.markdown(f"**Recomendación:** {resultado['recomendacion']}")
            st.markdown(f"**Similitud:** {resultado['similitud']:.2f}")
    else:
        st.success("Las diferencias cumplen con el manual vectorizado.")

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
    texto_referencia = extraer_texto(reference_file_type, uploaded_reference_file)
    tokens_referencia = tokenizar_lineamientos([texto_referencia])
    load_manual(tokens_referencia, texto_referencia)

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
