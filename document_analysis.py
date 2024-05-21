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

def almacenar_reglas_vectorizadas(tokens_referencia, texto_manual):
    reglas_vectorizadas = {}
    reglas = texto_manual.split("\n")
    for regla in reglas:
        regla = regla.strip()
        if regla:
            vector_tfidf = vectorizar_texto(regla, tokens_referencia)
            reglas_vectorizadas[regla] = vector_tfidf.tolist()[0]
    ruta_archivo_csv = "data/output/reglas_vectorizadas.csv"
    with open(ruta_archivo_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Regla", "Vector"])
        for regla, vector in reglas_vectorizadas.items():
            writer.writerow([regla, json.dumps(vector)])
    return reglas_vectorizadas

def cargar_y_vectorizar_manual(file, file_type, tokens_referencia):
    texto_manual = extraer_texto(file_type, file)
    reglas_vectorizadas = almacenar_reglas_vectorizadas(tokens_referencia, texto_manual)
    ruta_archivo_csv = "data/output/manual_vectorizado.csv"
    with open(ruta_archivo_csv, 'w', encoding='utf-8', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Regla", "Vector"])
        for regla, vector in reglas_vectorizadas.items():
            writer.writerow([regla, json.dumps(vector)])
    return ruta_archivo_csv

def comparar_con_manual(diferencias_vectorizadas, tokens_referencia):
    try:
        manual_vectorizado = pd.read_csv("https://raw.githubusercontent.com/FedeGG09/Qualipharma_2/main/data/ouput/reglas_vectorizadas.csv")
    except FileNotFoundError:
        logging.error("El archivo 'reglas_vectorizadas.csv' no se encontró.")
        return None

    resultados_comparacion = []
    for diferencia in diferencias_vectorizadas:
        vector_diferencia = diferencia["vector"]
        for _, fila in manual_vectorizado.iterrows():
            regla_vector = json.loads(fila["Vector"])
            similitud = sum(a * b for a, b in zip(vector_diferencia, regla_vector))  # Cálculo de similitud
            if similitud < 0.8:  # Umbral de cumplimiento
                resultado = {
                    "seccion": diferencia.get("seccion"),
                    "contenido_referencia": diferencia.get("contenido_referencia"),
                    "contenido_documento": diferencia.get("contenido_documento"),
                    "tipo": diferencia.get("tipo"),
                    "recomendacion": diferencia.get("recomendacion"),
                    "similitud": similitud
                }
                resultados_comparacion.append(resultado)
    return resultados_comparacion if resultados_comparacion else None
