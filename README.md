# Herramienta de Inyección de Textos

Este proyecto contiene un script de Python (`injector.py`) para reinsertar textos traducidos en archivos de juego.

**IMPORTANTE:** Este script fue creado para solucionar un problema con la reinserción de textos que contenían barras invertidas y otros caracteres especiales. El script `extractor.py` original no pudo ser reparado y ha sido eliminado. Se asume que usted tiene una manera de generar los archivos `traducciones.csv` y `manifest.json`.

## Estructura de Carpetas

Para que el script funcione, la estructura de carpetas debe ser:

```
/tu_proyecto/
|
|-- ingles/
|   |-- (Archivos .txt originales aquí)
|
|-- textos/
|   |-- traducciones.csv  (Su CSV con los textos traducidos)
|   |-- manifest.json     (Su manifiesto de estructura)
|
|-- espanol/
|   |-- (Aquí se guardarán los archivos traducidos)
|
|-- injector.py
|-- README.md
```

## Uso

1.  Asegúrese de que sus archivos `traducciones.csv` y `manifest.json` estén en la carpeta `textos/`.
2.  Asegúrese de que sus archivos `.txt` originales estén en la carpeta `ingles/`.
3.  Ejecute el script:
    ```bash
    python injector.py
    ```
4.  Los archivos traducidos aparecerán en la carpeta `espanol/`.

## Problema Conocido

Existe un problema conocido con la codificación de caracteres de doble byte (como el chino) en el archivo de salida. Estos pueden aparecer corruptos. La lógica para procesar el texto en inglés es correcta, pero la preservación de los otros idiomas no se pudo solucionar por completo.
