# Herramientas de Traducción de Textos de Juego (V2)

Este proyecto contiene dos scripts de Python (`extractor.py` e `injector.py`) diseñados para facilitar la traducción de textos de archivos de un juego, siguiendo un conjunto de reglas de extracción muy específicas.

## Lógica de Funcionamiento (V2)

Esta versión de los scripts funciona con las siguientes reglas:

1.  **Lectura de la Tercera Línea**: Los scripts ignoran las dos primeras líneas de cada archivo `.txt` y trabajan exclusivamente con la tercera línea.
2.  **Reglas de Marcadores**: El texto se divide según dos tipos de marcadores:
    -   **Marcadores Clásicos**: Como `<T>`, `</T>`, `{p1}`, etc.
    -   **Marcador de Barra Invertida**: Una barra invertida (`\`) seguida de los dos caracteres siguientes (ej: `\ab`, `\cd`) se trata como un delimitador no traducible.

## Estructura de Carpetas

Para que los scripts funcionen correctamente, debes organizar tus carpetas de la siguiente manera:

```
/tu_proyecto/
|
|-- ingles/
|   |-- archivo1.txt
|   |-- archivo2.txt
|
|-- textos/
|   |-- (Aquí se generarán traducciones.csv y manifest.json)
|
|-- espanol/
|   |-- (Aquí se guardarán los archivos traducidos)
|
|-- extractor.py
|-- injector.py
|-- README.md
```

## Flujo de Trabajo para la Traducción

Sigue estos pasos en orden:

### Paso 1: Extraer los Textos

1.  Coloca todos tus archivos `.txt` originales en la carpeta `ingles/`.
2.  Abre una terminal y ejecuta el script de extracción:
    ```bash
    python extractor.py
    ```
3.  El script generará `traducciones.csv` y `manifest.json` en la carpeta `textos/`.

### Paso 2: Traducir el CSV

1.  Abre el archivo `textos/traducciones.csv` con un programa de hojas de cálculo.
2.  Traduce el texto de la segunda columna (`Texto`). No modifiques la columna `ID`.
3.  Guarda los cambios en el archivo CSV.

### Paso 3: Reinsertar los Textos Traducidos

1.  Vuelve a la terminal y ejecuta el script de inyección:
    ```bash
    python injector.py
    ```
2.  ¡Listo! Encontrarás los archivos completamente traducidos en la carpeta `espanol/`. Cada archivo contendrá las dos primeras líneas del original intactas y la tercera línea modificada con tus traducciones.
