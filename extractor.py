# -----------------------------------------------------------------------------
# SCRIPT DE EXTRACCIÓN DE TEXTO PARA TRADUCCIÓN
# -----------------------------------------------------------------------------
#
# Autor: Jules
#
# PROPÓSITO:
# Este script extrae los textos en inglés de los archivos de juego (.txt)
# para prepararlos para la traducción.
#
# FUNCIONAMIENTO:
# 1. Busca todos los archivos .txt dentro de la carpeta 'ingles'.
# 2. Lee cada archivo y extrae los textos del campo "English".
# 3. Divide los textos en fragmentos más pequeños según un conjunto de
#    reglas y marcadores (ej: <T>, {p1}, etc.).
# 4. Genera dos archivos de salida en la carpeta 'textos':
#    - traducciones.csv: Un archivo CSV con los fragmentos de texto que
#      necesitan ser traducidos.
#    - manifest.json: Un archivo técnico que guarda la estructura original
#      de cada texto. Es CRUCIAL para que el script de inyección pueda
#      reconstruir las frases correctamente.
#
# INSTRUCCIONES DE USO:
# 1. Coloca todos tus archivos .txt originales en la carpeta 'ingles'.
#    Si la carpeta no existe, créala en el mismo directorio que este script.
# 2. Ejecuta este script desde la terminal:
#    python extractor.py
# 3. Revisa la carpeta 'textos' para encontrar los archivos generados.
# 4. Abre 'traducciones.csv' y traduce el texto de la segunda columna ("Texto").
#
# -----------------------------------------------------------------------------

import os
import re
import csv
import json

# --- CONFIGURACIÓN ---
INPUT_DIR = "ingles"
OUTPUT_DIR = "textos"
CSV_FILENAME = os.path.join(OUTPUT_DIR, "traducciones.csv")
MANIFEST_FILENAME = os.path.join(OUTPUT_DIR, "manifest.json")

# --- MARCADORES Y EXPRESIONES REGULARES ---

MARKERS = [
    "<T>", "</T>", "<A>", "</A>", "{i}", "{/i}", "<R>", "</R>", "<B>", "</B>",
    "<color=#ff003c>", "</color>", "<P>", "</P>", "<R2>", "</R2>", "<i>", "</i>",
    "<W>", "</W>", "<G>", "</G>", "<Y>", "</Y>", '"'
]

MARKERS_PATTERN_CONTENT = '|'.join(re.escape(m) for m in MARKERS)
PLACEHOLDER_PATTERN_CONTENT = r'\{[a-zA-Z0-9_]+\}'

SPLIT_PATTERN = re.compile(f'({MARKERS_PATTERN_CONTENT}|{PLACEHOLDER_PATTERN_CONTENT})')
DELIMITER_CHECK_PATTERN = re.compile(f"^(?:{SPLIT_PATTERN.pattern})$")
SCRIPT_CONTENT_PATTERN = re.compile(r'm_Script\s*=\s*"(.*)"', re.DOTALL)
ENTRY_PATTERN = re.compile(
    r'\{\s*"ID"\s*:\s*"(?P<id>.*?)"\s*,\s*.*?"English"\s*:\s*"(?P<english>.*?)"\s*,\s*"Japanese"',
    re.DOTALL
)
STANDALONE_PLACEHOLDER_PATTERN = re.compile(r'^\s*\{[a-zA-Z0-9_]+\}\s*$')

def process_text(original_id, text, file_path):
    if STANDALONE_PLACEHOLDER_PATTERN.match(text):
        return [], None
    tokens = SPLIT_PATTERN.split(text)
    tokens = [token for token in tokens if token]
    csv_rows = []
    manifest_structure = []
    fragment_counter = 1
    for token in tokens:
        if DELIMITER_CHECK_PATTERN.match(token):
            manifest_structure.append(token)
        else:
            if token.strip():
                fragment_id = f"{original_id}_{fragment_counter}"
                csv_rows.append({"ID": fragment_id, "Texto": token})
                manifest_structure.append({"ref": fragment_id})
                fragment_counter += 1
    if not csv_rows:
        return [], None
    manifest_entry = {
        "original_id": original_id,
        "file_path": file_path,
        "structure": manifest_structure
    }
    return csv_rows, manifest_entry

def extract_from_files():
    if not os.path.exists(INPUT_DIR):
        print(f"Error: El directorio de entrada '{INPUT_DIR}' no existe.")
        return
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    all_csv_rows = []
    all_manifest_entries = []
    print(f"Buscando archivos en '{INPUT_DIR}'...")
    for root, _, files in os.walk(INPUT_DIR):
        for filename in files:
            if not filename.endswith(".txt"):
                continue
            file_path = os.path.join(root, filename)
            print(f"Procesando archivo: {file_path}")
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                full_content = f.read()
            script_match = SCRIPT_CONTENT_PATTERN.search(full_content)
            if not script_match:
                print(f"  [AVISO] No se encontró 'm_Script' en {file_path}. Saltando archivo.")
                continue
            script_data_escaped = script_match.group(1)
            last_brace_pos = script_data_escaped.rfind(']}"')
            if last_brace_pos != -1:
                script_data_escaped = script_data_escaped[:last_brace_pos+2]
            if script_data_escaped.startswith("﻿"):
                script_data_escaped = script_data_escaped[1:]
            script_data_unescaped = script_data_escaped.replace('\\"', '"')
            for match in ENTRY_PATTERN.finditer(script_data_unescaped):
                original_id = match.group('id')
                english_text = match.group('english')
                csv_rows, manifest_entry = process_text(original_id, english_text, file_path)
                if csv_rows:
                    all_csv_rows.extend(csv_rows)
                if manifest_entry:
                    all_manifest_entries.append(manifest_entry)
    if all_csv_rows:
        print(f"Escribiendo {len(all_csv_rows)} fragmentos en {CSV_FILENAME}...")
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["ID", "Texto"])
            writer.writeheader()
            writer.writerows(all_csv_rows)
    else:
        print("No se encontraron textos traducibles.")
    if all_manifest_entries:
        print(f"Escribiendo manifiesto con {len(all_manifest_entries)} entradas en {MANIFEST_FILENAME}...")
        with open(MANIFEST_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(all_manifest_entries, f, indent=2, ensure_ascii=False)
    print("\n¡Proceso de extracción completado!")
    if os.path.exists("debug.py"):
        os.remove("debug.py")

if __name__ == "__main__":
    extract_from_files()
