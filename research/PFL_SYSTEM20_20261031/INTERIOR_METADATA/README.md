# Lector XLSX de originales históricos del Ministerio del Interior

**Copia de procedencia en la rama PFL-SYSTEM20:** este directorio conserva el código, tests, política y recibos SHA del trabajo original en la carpeta scratch indicada más abajo. El lector y los tests se copiaron sin cambiar sus bytes para preservar el digest congelado antes de la FASE 2. Para reejecutar **desde el repositorio** sobre originales situados fuera de Git y en un **directorio de salida nuevo**, utilizar desde la raíz:

```powershell
python scripts/replay_interior_metadata.py --originals-dir ..\PFL-raw-primary\interior_20261031 --output-dir ..\PFL-interior-replay-nuevo
```

El wrapper comprueba SHA-256 de código, política, manifiesto y originales; conserva únicamente metadatos agregados y coteja sus resultados con `receipts/phase2.json`, excluyendo la hora de ejecución. La reproducción observada el 31-10-2026 dio `EXPLORATORY_METADATA_REPLAY_EQUAL` y generó una copia fuera de Git en `../PFL-interior-metadata-replay-20261031-r1`. Ni la reproducción ni el conteo de filas constituyen un ciclo científico AB-R. Los recibos iniciales inmutables se conservan en `receipts/`.

**Procedencia de la ejecución original:** `/cos-prueba/PFL-scratch-interior-20261031` (carpeta local autorizada, fuera de Git). El lector utiliza exclusivamente la biblioteca estándar de Python 3 y consultó, sin modificarlos, dos originales en `/cos-prueba/PFL-raw-primary/interior_20261031` y el manifiesto del proyecto. Aquella ejecución no realizó nuevas conexiones de red, descargas, operaciones Git, aceptación de condiciones ni publicación de filas.

## Ejecuciones realizadas y orden de operaciones

1. Verificación independiente de longitud y SHA-256 de los dos XLSX contra el manifiesto.
2. Pruebas de seguridad y lectura ZIP/XML con fixtures completamente inventados.
3. **FASE 1:** inspección estructural de los originales, dimensiones, posición del encabezado, nombres de columnas y tamaños comprimidos/descomprimidos. El archivo contiene títulos preliminares y los encabezados reales están en la fila 4. Se conservaron los tres primeros intentos de identificación en `phase1.json`, `phase1_corrected.json` y `phase1_verified.json`, y la versión de lectura final en `phase1_final.json`; estos ensayos de esquema no son ciclos AB-H.
4. 14 pruebas superadas en `python -m unittest -v test_xlsx_reader.py`, incluidas agresiones sintéticas de ZIP-bomb, rutas maliciosas, DTD, sharedStrings, tipos de celda, fórmulas y parseo exploratorio.
5. **Congelación:** `python xlsx_reader.py freeze` ejecutó nuevamente las 14 pruebas y archivó `runs/2026-10-31/tests_receipt.json`, `frozen_code.json` (hash del lector y su suite) y el hash de la FASE 1 definitiva.
6. **FASE 2:** `python xlsx_reader.py phase2`, una sola vez, con la política `metadata_policy.json` y verificación del código congelado y SHA de los originales. Solo se inspeccionan celdas de metadatos administrativos autorizadas para agregar años, ausencia de datos y repeticiones de claves parciales. Se genera `runs/2026-10-31/phase2.json`, sin filas exportadas ni valores electorales.

La FASE 1 se reproduce (en un espacio nuevo, para no sobrescribir recibos) con `python xlsx_reader.py phase1`. La congelación se realiza con `python xlsx_reader.py freeze` después de tests. `phase2` exige que `frozen_code.json` concuerde con las versiones del lector y los tests, con la FASE 1 y con el manifiesto; no repita el comando en esta carpeta porque `phase2.json` existe y la apertura exclusiva bloquea sobrescrituras.

## Seguridad implementada

El contenedor XLSX se trata como ZIP estructurado. Antes de abrir XML se verifican número de miembros, nombres, extensiones requeridas, ausencia de rutas relativas ascendentes, duplicación de entradas, atributos de enlace simbólico, cifrado, métodos de compresión y límites de tamaño y relación de expansión. El lector aplica una cota adicional al número de bytes efectivamente descomprimidos, comprueba el prólogo contra DTD y entidades, y analiza XML por streaming con `xml.etree.ElementTree.iterparse`. Reconstruye nombres de hojas mediante relaciones OOXML. Soporta `sharedStrings` con rich text, `inlineStr`, números, cadenas, booleanos, errores, fechas textuales y fórmulas (que nunca ejecuta y no toma como evidencia). Limita filas y celdas por fila; no extrae hojas completas a disco.

La FASE 1 **no lee valores de voto ni escaños**: solo coordenadas de las primeras 25 filas para identificar la fila de encabezados y el contenido textual de esa fila. La FASE 2 aplica un listado permitido y rechaza las cabeceras que indiquen resultados, votos, escaños, candidaturas, personas o partidos. En `Elecciones-Congreso-cargos-electos.xlsx` usa A–E (fecha, código/tipo de elección y provincia). En `Elecciones-Congreso.xlsx` usa solo A–C (fecha, código/tipo). Las restantes columnas, incluidas `Cargos Electos`, `Candidatura`, `Siglas Candidatura`, las 52 columnas provinciales de valores y `Total Escaños Nacional`, quedan excluidas.

## Limitaciones interpretativas

Los conteos de registros son **filas de cada fichero**, no poblaciones de iniciativas parlamentarias, éxito legislativo, aceptación de cargos o escaños. Una coincidencia entre fecha/elección/provincia es natural cuando hay varias candidaturas: no es una duplicación de filas. No existe clave primaria no-outcome suficiente para estimar duplicación de registros en el segundo XLSX. Los datos ausentes se evalúan exclusivamente sobre columnas seleccionadas; no se puede generalizar al resto de campos. El XLSX puede incluir revisiones posteriores; las fechas HTTP `Last-Modified` no acreditan `first_public_at` de elecciones antiguas. La observación es una instantánea local de octubre de 2026 y no constituye un panel temporal de versiones históricas.

El catálogo de datos.gov.es señala **CC BY 4.0**, con deberes de atribución, enlace a la licencia e indicación de modificaciones al reutilizar. El manifiesto original advierte que esto no acredita por sí mismo derechos de redistribución de todos los campos o datos de personas, ni autoriza puntuaciones de políticos reales. Los informes de scratch contienen agregados y metadatos, sin originales redistribuidos. Se realizaron pruebas de QA y exploración, **0 ciclos AB-H**, 0 inferencias causales y 0 outcomes.

Los resultados exactos, recibos y hashes se documentan en [REPORT.md](REPORT.md) y [EXECUTION_LEDGER.json](EXECUTION_LEDGER.json).
