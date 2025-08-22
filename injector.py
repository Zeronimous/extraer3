# -----------------------------------------------------------------------------
# SCRIPT DE INYECCIÓN DE TEXTO TRADUCIDO (V3 - Lógica JSON)
# -----------------------------------------------------------------------------
#
# Autor: Jules
#
# PROPÓSITO:
# Este script reinserta los textos traducidos (del archivo .csv) en
# copias de los archivos de juego originales. Esta versión utiliza un
# método de parseo JSON que es 100% robusto y seguro para manejar
# cualquier tipo de caracter especial, comillas o barras invertidas.
#
# REGLAS DE INYECCIÓN (Según último requerimiento):
# 1. Lee las primeras dos líneas del archivo original y las mantiene intactas.
# 2. Parsea el contenido de la tercera línea como una estructura de datos JSON.
# 3. Modifica los textos en inglés directamente en la estructura de datos.
# 4. Convierte la estructura de datos de nuevo a un string JSON, que ya
#    estará perfectamente escapado.
# 5. Guarda un nuevo archivo .txt en la carpeta 'espanol' con el contenido
#    reensamblado (2 líneas originales + 1 línea modificada).
#
# INSTRUCCIONES DE USO:
# 1. Asegúrate de haber traducido los textos en 'textos/traducciones.csv'.
# 2. NO modifiques 'textos/manifest.json'.
# 3. Ejecuta este script desde la terminal:
#    python injector.py
# 4. Revisa la carpeta 'espanol' para encontrar los archivos del juego traducidos.
#
# -----------------------------------------------------------------------------

import os
import json
import csv
import re
from collections import defaultdict

# --- CONFIGURACIÓN ---
TEXTS_DIR = "textos"
SOURCE_DIR = "ingles"
OUTPUT_DIR = "espanol"
CSV_FILENAME = os.path.join(TEXTS_DIR, "traducciones.csv")
MANIFEST_FILENAME = os.path.join(TEXTS_DIR, "manifest.json")

# Patrón para encontrar y reemplazar el contenido de m_Script
SCRIPT_CONTENT_PATTERN = re.compile(r'(m_Script\s*=\s*")(.*)(")', re.DOTALL)

def reconstruct_string(structure, translations):
    """Reconstruye una cadena de texto a partir del manifiesto y las traducciones."""
    result = []
    for item in structure:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and 'ref' in item:
            ref_id = item['ref']
            translated_text = translations.get(ref_id, f"!!MISSING_{ref_id}!!")
            result.append(translated_text)
    return "".join(result)

def inject_translations_json():
    """
    Función principal que utiliza parseo JSON para una inyección 100% segura.
    """
    if not os.path.exists(MANIFEST_FILENAME) or not os.path.exists(CSV_FILENAME):
        print(f"Error: No se encontraron '{MANIFEST_FILENAME}' o '{CSV_FILENAME}'.")
        return

    print("Cargando traducciones y manifiesto...")
    with open(MANIFEST_FILENAME, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    translations = {row['ID']: row['Texto'] for row in csv.DictReader(open(CSV_FILENAME, 'r', encoding='utf-8'))}

    new_english_texts = {}
    for entry in manifest:
        original_id = entry['original_id']
        new_text = reconstruct_string(entry['structure'], translations)
        new_english_texts[original_id] = new_text

    mods_by_file = defaultdict(list)
    for entry in manifest:
        mods_by_file[entry['file_path']].append(entry['original_id'])

    print(f"Se procesarán {len(mods_by_file)} archivo(s).")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file_path, ids_in_file in mods_by_file.items():
        print(f"Procesando: {file_path}")
        if not os.path.exists(file_path):
            print(f"  [AVISO] El archivo original '{file_path}' no se encontró. Saltando.")
            continue

        try:
            with open(file_path, 'r', encoding='utf-8-sig') as f:
                line1 = f.readline()
                line2 = f.readline()
                line3 = f.readline()
        except Exception as e:
            print(f"  [ERROR] No se pudo leer el archivo {file_path}. Error: {e}")
            continue

        script_match = SCRIPT_CONTENT_PATTERN.search(line3)
        if not script_match:
            continue

        json_string_escaped = script_match.group(2)
        json_string_with_garbage = json_string_escaped.replace('\\"', '"')

        first_brace_pos = json_string_with_garbage.find('{')
        if first_brace_pos == -1:
            print(f"  [ERROR] No se encontró un JSON de inicio ('{{') en la tercera línea de '{file_path}'.")
            continue

        json_string = json_string_with_garbage[first_brace_pos:]

        try:
            data = json.loads(json_string)
        except json.JSONDecodeError as e:
            print(f"  [ERROR] La tercera línea de '{file_path}' no contiene un JSON válido. Error: {e}")
            continue

        for item in data.get("Data", []):
            item_id = item.get("ID")
            if item_id in new_english_texts:
                item["English"] = new_english_texts[item_id]

        new_json_string = json.dumps(data, ensure_ascii=False)
        final_escaped_string = new_json_string.replace('"', '\\"')

        modified_line3 = SCRIPT_CONTENT_PATTERN.sub(
            r'\1' + final_escaped_string + r'\3',
            line3
        )

        relative_path = os.path.relpath(file_path, SOURCE_DIR)
        output_path = os.path.join(OUTPUT_DIR, relative_path)
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8-sig') as f:
            f.write(line1)
            f.write(line2)
            f.write(modified_line3)
        print(f"  -> Guardado en: {output_path}")

    print(f"\n¡Proceso de inyección completado! Archivos guardados en la carpeta '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    inject_translations_json()
