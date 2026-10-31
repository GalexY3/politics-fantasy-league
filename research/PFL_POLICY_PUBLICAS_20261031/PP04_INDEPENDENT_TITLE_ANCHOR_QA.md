# PP-04 · Revisión independiente de identidad textual de las 198 fichas

**31/10/2026. NONCYCLE / R5 STOP.** Revisión de calidad del parser fuente-local de `PAN_2024.pdf`; **no** es verificación exhaustiva de fichas, identificación oficial, contraste IAEN ni análisis de eficacia normativa. Conserva los dos PDF, los JSONL y los recibos en el almacén privado fuera de Git. No reproduce títulos ni datos individuales en esta rama.

## Falsador descubierto en la PR #10

La versión inicial de `scripts/pan2024_local_cohort.py` tomaba `candidate_titles[-1]`: el último comienzo de línea que coincidiese con `LEY`, `LEY ORGÁNICA` o `REAL DECRETO` antes de `Objetivo:`. Esto falla cuando un título largo de una sola iniciativa contiene otra ley referenciada en una segunda línea. **En la ficha fuente-local 81 (PAN PDF página 69, impresión 85)**, la segunda referencia a una ley se presentaba erróneamente como comienzo del título del ítem. La imagen de esa página confirmó que la cabecera normativa empieza en la línea anterior. El rango legal y el conteo 198 no cambiaban, por lo que la QA de totales no detectaba el error.

Prueba adversarial nueva `test_nested_reference_to_another_law_inside_the_title_is_not_title_start` escrita antes de editar el parser, con fixture 100 % ficticio. En commit base **`9c3b8faac74f839f7e6c800677223d7d3d7a202e`** y SHA previo de fuente `2c532451c3d9e39309f9f9abf939bc0d6b65030bcbf8e9e98039c7f0586c4735` y test `03e06ab3bd27994b80771b8d8b5375950287061a02d7bfcfde06ae7ca8c43ae9`, el test falló por obtener una cabecera de título interior. El recibo previo es `../PFL-scratch-pan-iaen-20261031/PREPATCH_PR10_TITLE_ANCHOR_SHA256.txt`, fuera de Git.

La reparación acotada cambia el ancla seleccionada a **la primera** línea normativa del bloque posterior al `Ministerio` de la ficha anterior, conservando los controles `Objetivo`→`Ministerio`, tamaño, edición y SHA de fuente. La prueba sintética pasa tras la reparación. El script modificado tiene SHA `a1b6d56868e47b7c44caa70640b69c1b2e73fca6e16b4458ac62596fd05aa0ba`; SHA del test permanece `03e06ab3bd27994b80771b8d8b5375950287061a02d7bfcfde06ae7ca8c43ae9`. Recibo posterior `../PFL-scratch-pan-iaen-20261031/POSTPATCH_PR10_TITLE_ANCHOR_SHA256.txt`.

## Contraste independiente sobre el original autorizado

Dos rutas de extracción de texto del mismo **PAN original SHA `49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5`** fueron comparadas en un scratch fuera de Git: `pypdf` del programa y Poppler `pdftotext -layout` con análisis distinto de bloques. Ambas reconocen 198 secuencias de propuesta y el mismo rango en cada ordinal (6 orgánicas, 43 leyes, 149 reales decretos), pero esto **no** es un denominador registral independiente: ambos proceden del mismo original. Antes del cambio, 197/198 primeras cuatro palabras normalizadas del título coincidían; después, **198/198**. La única ficha cuyo primer renglón se modificó fue la auxiliar 81, comprobada visualmente en su página. Se preservó el archivo de salida anterior como histórico y se generó nueva derivada privada:

- SHA-256 del JSONL anterior, **histórico**: `66907d212a7d11fbb098f441a9fbb50c1aeb83c8cc0e50832b93c47cb60e17ad`.
- SHA-256 del JSONL corregido, **recomendado para QA posterior**: `c5bb5feba316c77c827bf60e912074ebc2ab56fd2be0489122116c30a78d86bf`.

El esquema conservó **198 IDs auxiliares locales** y `IAEN_link = null`, `actual_approval_outcome = null`, `first_public_at = null` en todos los casos. No se abrieron filas de resultados individuales del IAEN para esta prueba. La concordancia de cuatro palabras normalizadas no certifica la ortografía completa, la segmentación de líneas ni la identidad de cada título; la revisión humana de las 198 fichas sigue pendiente. La inconsistencia original **introducción 199 / tabla y cuerpo 198** sigue abierta, sin inventar una ficha 199.

## QA y límites

El primer intento de ejecutar la batería combinada sin `PYTHONPATH=src` falló durante la importación; es un error de entorno, **no un falsador científico**. Con `PYTHONPATH=src`: **98/98 pruebas Python focales PASS** (10 del parser, 88 de PAN/IAEN, trazas, C20, R21 y R22). El parser sobre original con SHA fijado devuelve 198/6/43/149, sin desenlaces ni crosswalk. La revisión de licencias, las versiones históricas y `first_public_at` no cambian; sin originales en Git, sin AB-R, sin cambios CT2/Atlas, sin merge ni publicación de personas.

**Siguiente tarea:** verificación visual sistemática por páginas y estratos del inventario, búsqueda documental de errata o edición explicativa para 199/198, y luego solo vínculos oficiales explícitos PAN→IAEN. No usar títulos parecidos como claves, ni promover la QA técnica a cumplimiento de políticas públicas.
