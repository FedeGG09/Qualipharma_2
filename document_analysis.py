import os
import pandas as pd
import pdfminer.high_level
import spacy
import json
import csv
import docx
from sklearn.feature_extraction.text import TfidfVectorizer
from docx import Document
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
import logging

import nltk
nltk.download('punkt')
nltk.download('wordnet')

logging.basicConfig(filename='logs/document_analysis.log', level=logging.DEBUG)

lemmatizer = WordNetLemmatizer()

def extraer_texto_docx(docx_file):
    texto = ""
    doc = Document(docx_file)
    for paragraph in doc.paragraphs:
        texto += paragraph.text + "\n"
    return texto.strip()

def extraer_texto_pdf(pdf_file):
    return pdfminer.high_level.extract_text(pdf_file)

def leer_archivo_texto(txt_file):
    return txt_file.read().decode('utf-8')

def tokenizar_lineamientos(lineamientos):
    tokens = []
    for lineamiento in lineamientos:
        tokens.extend(word_tokenize(lineamiento))
    return list(set(tokens))

def vectorizar_texto(texto, tokens_referencia):
    vectorizer = TfidfVectorizer(vocabulary=tokens_referencia, lowercase=False)
    vector_tfidf = vectorizer.fit_transform([texto])
    return vector_tfidf.toarray()

def encontrar_diferencias(documento1, documento2):
    diferencias = []
    try:
        lineas1 = documento1.split('\n')
        lineas2 = documento2.split('\n')

        for i, (linea1, linea2) in enumerate(zip(lineas1, lineas2), start=1):
            if linea1 != linea2:
                diferencia = {
                    "seccion": f"Línea {i}",
                    "contenido_referencia": linea1,
                    "contenido_documento": linea2,
                    "tipo": "Línea",
                    "recomendacion": f"Revisar la línea {i} en el documento y ajustarla según el manual."
                }
                diferencias.append(diferencia)

        return diferencias
    except Exception as e:
        logging.error(f"Error al encontrar diferencias: {e}")
        return None

def vectorizar_y_tokenizar_diferencias(diferencias, tokens_referencia, nombre_documento_comparar, nombre_documento_referencia):
    diferencias_vectorizadas = []
    for diferencia in diferencias:
        vector_tfidf = vectorizar_texto(diferencia["contenido_documento"], tokens_referencia)
        diferencia_vectorizada = {
            "seccion": diferencia["seccion"],
            "contenido_referencia": diferencia["contenido_referencia"],
            "contenido_documento": diferencia["contenido_documento"],
            "tipo": diferencia["tipo"],
            "recomendacion": diferencia["recomendacion"],
            "vector": vector_tfidf.tolist()[0]
        }
        diferencias_vectorizadas.append(diferencia_vectorizada)
    df_diferencias = pd.DataFrame(diferencias_vectorizadas)
    ruta_directorio = "data/output"
    os.makedirs(ruta_directorio, exist_ok=True)
    nombre_archivo_csv = f"{nombre_documento_comparar}_diferencias.csv"
    ruta_archivo_csv = os.path.join(ruta_directorio, nombre_archivo_csv)
    df_diferencias.to_csv(ruta_archivo_csv, index=False, encoding='utf-8')
    return diferencias_vectorizadas

def extraer_titulo_seccion(seccion, indice_manual):
    for item in indice_manual:
        if item in seccion:
            return item
    return "Seccion Desconocida"

def cargar_y_vectorizar_manual(file, file_type, indice_manual):
    # Cargar el texto del manual desde el archivo
    texto_manual = extraer_texto(file_type, file)
    
    # Tokenizar el texto del manual para obtener los tokens de referencia
    tokens_referencia = tokenizar_lineamientos([texto_manual])

    # Almacenar las reglas vectorizadas
    reglas_vectorizadas = almacenar_reglas_vectorizadas(tokens_referencia, texto_manual, indice_manual)
    
    # Guardar el manual vectorizado en un archivo CSV
    ruta_archivo_csv = "data/output/manual_vectorizado.csv"
    with open(ruta_archivo_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Seccion", "Vector"])
        for seccion, vector in reglas_vectorizadas.items():
            writer.writerow([seccion, json.dumps(vector)])
    
    # Retornar la ruta del archivo CSV del manual vectorizado
    return ruta_archivo_csv

def load_manual(tokens_referencia, texto_manual, indice_manual):
    almacenar_reglas_vectorizadas(tokens_referencia, texto_manual, indice_manual)

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

# Aquí deberías cargar y vectorizar el manual
ruta_manual_vectorizado = cargar_y_vectorizar_manual(uploaded_reference_file, reference_file_type, indice_manual)

# Luego, carga los tokens de referencia y el texto del manual
tokens_referencia = cargar_tokens_referencia(ruta_manual_vectorizado)
texto_manual = cargar_texto_manual(ruta_manual_vectorizado)

# Finalmente, carga el manual
load_manual(tokens_referencia, texto_manual, indice_manual)
