# -----------------------------------------------------------------------------
# SCRIPT DE EXTRACCIÓN DE TEXTO PARA TRADUCCIÓN (V2)
# -----------------------------------------------------------------------------
#
# Autor: Jules
#
# PROPÓSITO:
# Este script extrae los textos en inglés de los archivos de juego (.txt)
# para prepararlos para la traducción, siguiendo reglas específicas.
#
# REGLAS DE EXTRACCIÓN (Según último requerimiento):
# 1. IGNORA las primeras dos líneas de cada archivo .txt.
# 2. PROCESA únicamente la tercera línea de cada archivo.
# 3. DIVIDE el texto encontrado en el campo "English" según dos tipos de marcadores:
#    a) Marcadores Clásicos: <T>, {p1}, etc.
#    b) Nueva Regla: Una barra invertida `\` seguida de DOS caracteres cualesquiera (ej: \ab, \cd).
#
# FUNCIONAMIENTO:
# - Genera dos archivos de salida en la carpeta 'textos':
#   - traducciones.csv: Contiene los fragmentos de texto a traducir.
#   - manifest.json: Un archivo técnico que guarda la estructura para poder
#     reconstruir las frases. Es CRUCIAL para el script de inyección.
#
# INSTRUCCIONES DE USO:
# 1. Coloca tus archivos .txt originales en la carpeta 'ingles'.
# 2. Ejecuta este script desde la terminal:
#    python extractor.py
# 3. Abre 'textos/traducciones.csv' y traduce el texto de la columna "Texto".
#
# -----------------------------------------------------------------------------

import os
import re
import csv
import json
import codecs

# --- CONFIGURACIÓN ---
INPUT_DIR = "ingles"
OUTPUT_DIR = "textos"
CSV_FILENAME = os.path.join(OUTPUT_DIR, "traducciones.csv")
MANIFEST_FILENAME = os.path.join(OUTPUT_DIR, "manifest.json")

# --- LÓGICA DE MARCADORES ---
OLD_MARKERS = [
    "<T>", "</T>", "<A>", "</A>", "{i}", "{/i}", "<R>", "</R>", "<B>", "</B>",
    "<color=#ff003c>", "</color>", "<P>", "</P>", "<R2>", "</R2>", "<i>", "</i>",
    "<W>", "</W>", "<G>", "</G>", "<Y>", "</Y>", '"'
]
OLD_MARKERS_PATTERN = '|'.join(re.escape(m) for m in OLD_MARKERS)
PLACEHOLDER_PATTERN = r'\{[a-zA-Z0-9_]+\}'
BACKSLASH_MARKER_PATTERN = r'\\..'
TOKENIZER_PATTERN = re.compile(f'{OLD_MARKERS_PATTERN}|{PLACEHOLDER_PATTERN}|{BACKSLASH_MARKER_PATTERN}')

# Patrones para extraer el contenido del archivo
SCRIPT_CONTENT_PATTERN = re.compile(r'm_Script\s*=\s*"(.*)"', re.DOTALL)
ENTRY_PATTERN = re.compile(
    r'\{\s*"ID"\s*:\s*"(?P<id>.*?)"\s*,\s*.*?"English"\s*:\s*"(?P<english>.*?)"\s*,\s*"Japanese"',
    re.DOTALL
)
STANDALONE_PLACEHOLDER_PATTERN = re.compile(r'^\s*\{[a-zA-Z0-9_]+\}\s*$')

def process_text(original_id, text, file_path):
    try:
        clean_text = codecs.decode(text, 'unicode_escape')
    except Exception:
        clean_text = text

    if STANDALONE_PLACEHOLDER_PATTERN.match(clean_text):
        return [], None

    tokens = []
    last_idx = 0
    for match in TOKENIZER_PATTERN.finditer(clean_text):
        tokens.append(clean_text[last_idx:match.start()])
        tokens.append(match.group(0))
        last_idx = match.end()
    tokens.append(clean_text[last_idx:])

    csv_rows = []
    manifest_structure = []
    fragment_counter = 1
    for token in tokens:
        if token == '':
            continue
        if TOKENIZER_PATTERN.fullmatch(token):
            manifest_structure.append(token)
        else:
            fragment_id = f"{original_id}_{fragment_counter}"
            csv_rows.append({"ID": fragment_id, "Texto": token})
            manifest_structure.append({"ref": fragment_id})
            fragment_counter += 1

    if not manifest_structure:
        return [], None

    return csv_rows, {
        "original_id": original_id,
        "file_path": file_path,
        "structure": manifest_structure
    }

def extract_from_files():
    if not os.path.exists(INPUT_DIR):
        print(f"ADVERTENCIA: El directorio '{INPUT_DIR}' no existe. Se creará uno.")
        os.makedirs(INPUT_DIR)

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

            try:
                with open(file_path, 'r', encoding='utf-8-sig') as f:
                    f.readline()
                    f.readline()
                    third_line = f.readline()

                if not third_line:
                    continue

                script_match = SCRIPT_CONTENT_PATTERN.search(third_line)
                if not script_match:
                    continue

                script_data_escaped = script_match.group(1)
                script_data_unescaped = script_data_escaped.replace('\\"', '"')

                for match in ENTRY_PATTERN.finditer(script_data_unescaped):
                    original_id = match.group('id')
                    english_text = match.group('english')
                    csv_rows, manifest_entry = process_text(original_id, english_text, file_path)
                    if csv_rows:
                        all_csv_rows.extend(csv_rows)
                    if manifest_entry:
                        all_manifest_entries.append(manifest_entry)
            except Exception as e:
                print(f"  [ERROR] No se pudo procesar el archivo {file_path}. Error: {e}")

    if all_csv_rows:
        print(f"Escribiendo {len(all_csv_rows)} fragmentos en {CSV_FILENAME}...")
        with open(CSV_FILENAME, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=["ID", "Texto"])
            writer.writeheader()
            writer.writerows(all_csv_rows)
    if all_manifest_entries:
        print(f"Escribiendo manifiesto con {len(all_manifest_entries)} entradas en {MANIFEST_FILENAME}...")
        with open(MANIFEST_FILENAME, 'w', encoding='utf-8') as f:
            json.dump(all_manifest_entries, f, indent=2, ensure_ascii=False)
    print("\n¡Proceso de extracción completado!")

if __name__ == "__main__":
    extract_from_files()
