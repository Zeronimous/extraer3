# -----------------------------------------------------------------------------
# SCRIPT DE INYECCIÓN DE TEXTO TRADUCIDO
# -----------------------------------------------------------------------------
#
# Autor: Jules
#
# PROPÓSITO:
# Este script reinserta los textos traducidos (del archivo .csv) en
# copias de los archivos de juego originales.
#
# FUNCIONAMIENTO:
# 1. Lee el archivo 'manifest.json' para entender la estructura de cada
#    frase original.
# 2. Lee el archivo 'traducciones.csv' para obtener los textos ya traducidos.
# 3. Para cada archivo original listado en el manifiesto:
#    a. Reconstruye las frases completas uniendo los fragmentos traducidos
#       y los marcadores/delimitadores originales.
#    b. Lee el archivo .txt original correspondiente de la carpeta 'ingles'.
#    c. Crea una copia del contenido y reemplaza el texto del campo "English"
#       con la nueva frase traducida y reconstruida.
# 4. Guarda un nuevo archivo .txt con el contenido modificado en la
#    carpeta 'espanol', manteniendo el nombre y la estructura de carpetas
#    del original.
#
# INSTRUCCIONES DE USO:
# 1. Asegúrate de haber traducido los textos en el archivo
#    'textos/traducciones.csv'. Guarda los cambios.
# 2. NO modifiques el archivo 'textos/manifest.json'.
# 3. Ejecuta este script desde la terminal:
#    python injector.py
# 4. Revisa la carpeta 'espanol'. Contendrá los archivos del juego ya
#    traducidos.
#
# -----------------------------------------------------------------------------

import os
import json
import csv
import re
from collections import defaultdict

# --- CONFIGURACIÓN ---
TEXTS_DIR = "textos"
SOURCE_DIR = "ingles" # Directorio de los archivos originales
OUTPUT_DIR = "espanol" # Cambiado a 'espanol' para evitar problemas con caracteres no ASCII
CSV_FILENAME = os.path.join(TEXTS_DIR, "traducciones.csv")
MANIFEST_FILENAME = os.path.join(TEXTS_DIR, "manifest.json")

# Patrón para encontrar el contenido de m_Script
SCRIPT_CONTENT_PATTERN = re.compile(r'(m_Script\s*=\s*")(.*)(")', re.DOTALL)

def reconstruct_string(structure, translations):
    """
    Reconstruye una cadena de texto completa a partir de su estructura del manifiesto
    y el diccionario de traducciones.
    """
    result = []
    for item in structure:
        if isinstance(item, str):
            result.append(item)
        elif isinstance(item, dict) and 'ref' in item:
            ref_id = item['ref']
            translated_text = translations.get(ref_id, f"!!!TRADUCCION_FALTANTE_{ref_id}!!!")
            result.append(translated_text)
    return "".join(result)

def inject_translations():
    """
    Función principal para leer el manifiesto y el CSV, y generar los archivos traducidos.
    """
    if not os.path.exists(MANIFEST_FILENAME) or not os.path.exists(CSV_FILENAME):
        print(f"Error: No se encontraron los archivos '{MANIFEST_FILENAME}' o '{CSV_FILENAME}'.")
        print("Asegúrate de ejecutar el script de extracción primero.")
        return

    print("Cargando traducciones y manifiesto...")
    with open(MANIFEST_FILENAME, 'r', encoding='utf-8') as f:
        manifest = json.load(f)

    translations = {}
    with open(CSV_FILENAME, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            translations[row['ID']] = row['Texto']

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

        with open(file_path, 'r', encoding='utf-8-sig') as f:
            original_content = f.read()

        modified_script_data_unescaped = ""

        script_match = SCRIPT_CONTENT_PATTERN.search(original_content)
        if script_match:
            script_data_escaped = script_match.group(2)
            modified_script_data_unescaped = script_data_escaped.replace('\\"', '"')
        else:
             print(f"  [AVISO] No se encontró 'm_Script' en {file_path}. Saltando archivo.")
             continue

        for mod in mods:
            original_id = mod['original_id']
            new_english_text = reconstruct_string(mod['structure'], translations)

            replace_pattern = re.compile(
                r'("ID"\s*:\s*"' + re.escape(original_id) + r'".*?"English"\s*:\s*")'
                r'(.*?)'
                r'("(?:\s*,\s*"Japanese"))',
                re.DOTALL
            )

            modified_script_data_unescaped = replace_pattern.sub(
                lambda m: m.group(1) + new_english_text + m.group(3),
                modified_script_data_unescaped,
                count=1
            )

        final_script_data_escaped = modified_script_data_unescaped.replace('"', '\\"')

        modified_content = SCRIPT_CONTENT_PATTERN.sub(
            r'\1' + final_script_data_escaped + r'\3',
            original_content
        )

        relative_path = os.path.relpath(file_path, SOURCE_DIR)
        output_path = os.path.join(OUTPUT_DIR, relative_path)

        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        print(f"  -> Guardado en: {output_path}")

    print(f"\n¡Proceso de inyección completado! Archivos guardados en la carpeta '{OUTPUT_DIR}'.")

if __name__ == "__main__":
    inject_translations()
