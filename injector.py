# -----------------------------------------------------------------------------
# SCRIPT DE INYECCIÓN DE TEXTO TRADUCIDO (V2)
# -----------------------------------------------------------------------------
#
# Autor: Jules
#
# PROPÓSITO:
# Este script reinserta los textos traducidos (del archivo .csv) en
# copias de los archivos de juego originales, siguiendo la nueva lógica.
#
# REGLAS DE INYECCIÓN (Según último requerimiento):
# 1. Lee las primeras dos líneas del archivo original y las mantiene intactas.
# 2. Reconstruye la tercera línea del archivo combinando los textos traducidos
#    con los marcadores originales (guardados en manifest.json).
# 3. Guarda un nuevo archivo .txt en la carpeta 'espanol' con el contenido
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
import codecs

# --- CONFIGURACIÓN ---
TEXTS_DIR = "textos"
SOURCE_DIR = "ingles"
OUTPUT_DIR = "espanol"
CSV_FILENAME = os.path.join(TEXTS_DIR, "traducciones.csv")
MANIFEST_FILENAME = os.path.join(TEXTS_DIR, "manifest.json")

# Patrones para encontrar y reemplazar el contenido
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

def inject_translations():
    """Función principal para generar los archivos traducidos."""
    if not os.path.exists(MANIFEST_FILENAME) or not os.path.exists(CSV_FILENAME):
        print(f"Error: No se encontraron '{MANIFEST_FILENAME}' o '{CSV_FILENAME}'.")
        return

    print("Cargando traducciones y manifiesto...")
    with open(MANIFEST_FILENAME, 'r', encoding='utf-8') as f:
        manifest = json.load(f)
    translations = {row['ID']: row['Texto'] for row in csv.DictReader(open(CSV_FILENAME, 'r', encoding='utf-8'))}

    modifications_by_file = defaultdict(list)
    for entry in manifest:
        modifications_by_file[entry['file_path']].append(entry)

    print(f"Se procesarán {len(modifications_by_file)} archivo(s).")
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    for file_path, mods in modifications_by_file.items():
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
            print(f"  [AVISO] No se encontró 'm_Script' en la tercera línea de {file_path}. Saltando.")
            continue

        script_data_escaped = script_match.group(2)
        script_data_unescaped = script_data_escaped.replace('\\"', '"')

        for mod in mods:
            original_id = mod['original_id']
            new_english_text = reconstruct_string(mod['structure'], translations)

            safe_new_english_text = new_english_text.replace('\\', '\\\\')

            replace_pattern = re.compile(
                r'("ID"\s*:\s*"' + re.escape(original_id) + r'".*?"English"\s*:\s*")'
                r'(.*?)'
                r'("(?:\s*,\s*"Japanese"))',
                re.DOTALL
            )

            script_data_unescaped = replace_pattern.sub(
                r'\1' + safe_new_english_text + r'\3',
                script_data_unescaped,
                count=1
            )

        final_script_data_escaped = script_data_unescaped.replace('"', '\\"')

        safe_final_script_data_escaped = final_script_data_escaped.replace('\\', '\\\\')

        modified_line3 = SCRIPT_CONTENT_PATTERN.sub(
            r'\1' + safe_final_script_data_escaped + r'\3',
            line3,
            count=1
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
    inject_translations()
