# Descargamos los módulos necesarios
import subprocess
import os
from os import listdir
from os.path import isfile, join

#subprocess.run(["pip", "install", "-U", "setuptools", "wheel"])
subprocess.run(["pip", "install", "-U", "spacy"])
subprocess.run(["pip", "install", "pdfminer.six"])
subprocess.run(["pip", "install", "pdfminer"])

import spacy
import pdfminer
from spacy import displacy
from pdfminer.high_level import extract_text

# FALTA EDITAR
subprocess.run(["pip", "install", "https://github.com/DaniLim/Modelo-Legal_Monetario/releases/download/es_legal_monetario-0.0.2/es_legal_monetario-0.0.2.tar.gz"])

# Nombre del equipo
nombre_equipo = "rugby mates"

# Directorio de la carpeta donde se encuentran los documentos BOE
# RELLENAR POR USUARIO
carpeta_de_BOEs = "./PDFs"

# Listado de los ficheros
listado_de_BOEs = [f for f in listdir(
    carpeta_de_BOEs) if isfile(join(carpeta_de_BOEs, f))]

#Creamos carpeta donde almacenar ficheros de salida
os.mkdir(f"{carpeta_de_BOEs}/Entidades_extraidas_rugby_mates")

# Iteramos sobre todos los ficheros
for fichero in listado_de_BOEs:
    text = extract_text(f"{carpeta_de_BOEs}/{fichero}")

    # Limpiamos letras sueltas y margenes
    text = text.splitlines()

    for frase in reversed(text):
        if len(frase) < 2:
            text.remove(frase)

    # Se junta el texto para evitar saltos de linea
    text = " ".join(text)

    # Limpieza de las palabras que estan dividas por ser final de linea
    text = text.replace("- ", "")
    text = text.replace("-", "")

    # Repaso de lo que por temas de lectura del pdf se queda junto
    text = text.split()
    texto_limpio = []
    for palabra in text:
        # Por problemas con el € se hace por separado
        if len(palabra) > 2 and "€/" not in palabra:
            if palabra[0]+palabra[1] == "€.":
                palabra = "€. " + palabra[2:]
            elif palabra[0] == "€":
                palabra = "€ "+palabra[1:]
            elif "€" in palabra[:len(palabra)-2]:
                pos = palabra.find("€")
                palabra = palabra[:pos-1]+" € "+palabra[pos+1:]

        # Separacion de las frases que han sido leidas incorrectamente
        if len(palabra) > 2:
            if "." in palabra:
                pos = palabra.find(".")
                if pos == 0 or pos == len(palabra)-1:  # Puntos finales
                    pass
                # Numeros
                elif str.isdigit(palabra[pos - 1]) and str.isdigit(palabra[pos + 1]):
                    pass
                else:
                    palabra = palabra.replace(".", ". ")
            elif ":" in palabra:
                pos = palabra.find(":")
                if pos == 0 or pos == len(palabra)-1:  # Puntos finales
                    pass
                # Numeros
                elif str.isdigit(palabra[pos - 1]) and str.isdigit(palabra[pos + 1]):
                    pass
                else:
                    palabra = palabra.replace(":", ": ")
        texto_limpio.append(palabra)

    # Texto limpio
    texto_limpio = " ".join(texto_limpio)

    # Carga del modelo previamente instalado
    nlp = spacy.load("es_legal_monetario")
    doc = nlp(texto_limpio)

    #Entidades en formato TXT
    with open(f"{carpeta_de_BOEs}/Entidades_extraidas_rugby_mates/SOLUCION_{nombre_equipo}_{fichero[:len(fichero)-4]}.txt", "w", encoding="utf-8") as f:
        for entity in doc.ents:
            f.write(f"{entity.text} | {entity.label_}\n")

    #Entidades en formato HTML
    colores = {"MONEDAS": "#F1FF9F"}
    options = {"ents": ["LEGAL", "MONEDAS"], "colors": colores}

    html = displacy.render(doc, style="ent", options=options)
    with open(f"{carpeta_de_BOEs}/Entidades_extraidas_rugby_mates/data_vis_{nombre_equipo}_{fichero[:len(fichero)-4]}.html", "w", encoding="utf-8") as f:
        f.write(html)
