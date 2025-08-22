# Herramientas de Traducción de Textos de Juego

Este proyecto contiene dos scripts de Python (`extractor.py` e `injector.py`) diseñados para facilitar la traducción de textos de archivos de un juego.

## Estructura de Carpetas

Para que los scripts funcionen correctamente, debes organizar tus carpetas de la siguiente manera:

```
/tu_proyecto/
|
|-- ingles/
|   |-- archivo1.txt
|   |-- archivo2.txt
|   |-- (y cualquier otra subcarpeta con archivos .txt)
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

-   **`ingles/`**: Debes crear esta carpeta y colocar aquí todos los archivos `.txt` originales que quieres traducir. Los scripts buscarán en todas las subcarpetas dentro de `ingles`.
-   **`textos/`**: Esta carpeta será creada automáticamente por `extractor.py`.
-   **`espanol/`**: Esta carpeta será creada automáticamente por `injector.py`.

## Flujo de Trabajo para la Traducción

Sigue estos pasos en orden:

### Paso 1: Extraer los Textos

1.  Asegúrate de que todos tus archivos de texto originales estén en la carpeta `ingles/`.
2.  Abre una terminal o línea de comandos en la carpeta del proyecto.
3.  Ejecuta el script de extracción:
    ```bash
    python extractor.py
    ```
4.  El script procesará todos los archivos y creará dos nuevos archivos dentro de la carpeta `textos/`:
    -   `traducciones.csv`: Contiene los fragmentos de texto a traducir.
    -   `manifest.json`: Un archivo técnico que el segundo script necesita. **NO LO MODIFIQUES**.

### Paso 2: Traducir el CSV

1.  Abre el archivo `textos/traducciones.csv` con un programa de hojas de cálculo (como Microsoft Excel, Google Sheets, LibreOffice Calc, etc.).
2.  Traduce el texto de la segunda columna (`Texto`).
3.  **Importante**: No modifiques la primera columna (`ID`) ni cambies el orden de las filas.
4.  Guarda los cambios en el archivo CSV.

### Paso 3: Reinsertar los Textos Traducidos

1.  Una vez que hayas terminado de traducir y guardado el archivo CSV.
2.  Vuelve a la terminal y ejecuta el script de inyección:
    ```bash
    python injector.py
    ```
3.  El script leerá tus traducciones y las reinsertará en copias de los archivos originales.
4.  ¡Listo! Encontrarás los archivos completamente traducidos en la carpeta `espanol/`, manteniendo la misma estructura de nombres y subcarpetas que tenías en `ingles/`.
