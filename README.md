# Herramientas de Traducción de Textos de Juego (V4 - Definitiva)

Este proyecto contiene dos scripts de Python (`extractor.py` e `injector.py`) diseñados para facilitar la traducción de textos de archivos de un juego. Esta es la versión final y más robusta, diseñada para manejar los casos más complejos.

## Lógica de Funcionamiento (V4)

Esta versión de los scripts funciona con las siguientes reglas:

1.  **Lectura de la Tercera Línea**: El extractor ignora las dos primeras líneas de cada archivo `.txt` y trabaja exclusivamente con la tercera línea.
2.  **Reglas de Marcadores**: El texto se divide según dos tipos de marcadores:
    -   **Marcadores Clásicos**: Como `<T>`, `</T>`, `{p1}`, etc.
    -   **Marcador de Barra Invertida**: Una barra invertida (`\`) seguida de los dos caracteres siguientes (ej: `\ab`) se trata como un delimitador no traducible.
3.  **Inyección con Lógica JSON Definitiva**: El script de inyección (`injector.py`) ahora utiliza un método de dos pasos para garantizar la máxima compatibilidad:
    -   Primero, **aísla** el bloque de datos JSON buscando el primer `{` y el último `}` en la línea, eliminando cualquier dato basura al principio o al final.
    -   Segundo, **desescapa** este bloque de forma robusta usando la librería `codecs` antes de parsearlo como JSON.
    -   Este proceso asegura que el script funcione incluso con archivos que tengan un formato o codificación inesperados.

## Estructura de Carpetas

```
/tu_proyecto/
|
|-- ingles/
|   |-- archivo1.txt
|   |-- (etc...)
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
2.  ¡Listo! Encontrarás los archivos completamente traducidos en la carpeta `espanol/`.
