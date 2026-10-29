# Politics Fantasy League · ABH30-C10 — Revisiones reales del archivo público original

**Fecha:** 29/10/2026. **Modalidad AB-H acotada:** AB-R de integridad documental + AB-P de instrumento. **DRIFT D1** respecto a C09. **No** es una intervención con participantes, una mejora predictiva, una confirmación científica original ni una prueba de lanzamiento. Continuación apilada sobre el PR #60, sin fusionar a `main`.

## Resultado principal

El C09 solo tenía pruebas sintéticas del comparador de filas originales. C10 utiliza el **mismo código congelado** para tres pares de versiones históricas **originales** de `forecastingresearch/forecastbench-datasets` (dos cohortes). El contrato A–J y las seis identidades Git esperadas se fijaron en el commit `1dd2ea52bcce8de76dc5b415592288295fce2dfe` **antes de recuperar los cuerpos completos** de los seis ficheros. Su contenido UTF-8 completo se recuperó por el conector GitHub, se recalculó su SHA1 Git, comprobando antes el vector `git hash-object abc`. Los seis SHA calculados coincidieron con las identidades Git de los ficheros originales. El código ejecutado V8 procede exactamente del blob Git C09 `2e1ed7f5e23bbad79c81013505882830907cb258`, SHA256 congelado `21882420a2713ee8490d819d9936d33a5123f6869d4b97e3c244098908653ee9`.

| Cohorte / transición | Filas anteriores → posteriores | Sin cambios | Altas | Bajas | Filas modificadas |
| --- | ---: | ---: | ---: | ---: | ---: |
| 27/09 · 07→08 octubre | 441→440 | 221 | 0 | 1 | 219 |
| 27/09 · 11→12 octubre | 437→427 | 215 | 0 | 10 | 212 |
| 11/10 · 23→24 octubre | 441→438 | 196 | 2 | 5 | 240 |

**Las tres identidades de conteo son correctas**: `filas_pre - bajas + altas = filas_post`, sin duplicados de claves compuestas `(source,id)` en los tres pares. Las cifras sumadas (16 bajas, dos altas, 671 modificaciones) son **eventos entre versiones**, no entidades únicas en la población ni indicios de manipulación política. Que una fila cambie no equivale a que cambie su desenlace binario admisible.

La descomposición **post hoc**, independiente del endpoint principal prerregistrado, encontró cambios en `resolution_date` (214, 212 y 239 respectivamente) y en `resolved_to` (79, 77 y 128). Los datos originales incluyen valores decimales continuos en `resolved_to`; **no se pueden interpretar esas 284 modificaciones de campo como 284 inversiones de resultados binarios**. En contraste, C08 documentó cero inversiones en el subconjunto de **preguntas binarias de mercado elegibles** para los 19 cortes anteriores. No se ha demostrado ni negado aquí estabilidad para todas las preguntas o mercados del mundo.

## Contrato metodológico A–J

**A — Problema y estimando.** A diferencia de un conjunto de resultados humanos, la unidad observable es la fila pública de `resolutions` identificada por proveedor e ID, comparada entre dos instantes de publicación Git. Estimando descriptivo: proporción y recuento de altas, bajas, cambios de valores y filas conservadas por revisión. No intervención, aleatorización, exposición ni bienestar.

**B — Hipótesis y rivales.** H1: al menos una caída de recuento oculta supresiones o sustituciones reales de claves, y algunas filas retenidas cambian de contenido. H0: el original satisface una propiedad append-only para claves o la supuesta diferencia se debe a duplicados/esquema incompatible. Rival fuerte: el cambio es mantenimiento ordinario de valores económicos/fechas y no afecta a predicción binaria; el C09 puede ser útil como QA sin constituir ciencia novedosa. La fuente no es una autoridad de first_public_at por evento de la plataforma subyacente.

**C — Diseño fijo.** Tres pares exactos seleccionados por las caídas de filas *ya publicadas en C08*: septiembre 07→08/10, septiembre 11→12/10 y octubre 23→24/10. Las identidades Git, fechas y consecuencias de falla estaban congeladas antes de inspeccionar contenidos en C10. Selección informada por resultado bruto previo: estudio **dirigido a casos de cambio**, no representativo del historial completo ni preregistro ciego de una población inédita.

**D — Instrumentación.** Código reutilizado de C09 sin modificarse: `src/politics_fantasy/forecastbench_raw_revision_guard.mjs`, SHA Git y SHA256 anteriores. Prerregistro [C10_PREREG_AJ_SHA.json](C10_PREREG_AJ_SHA.json) en commit `1dd2ea52bcce8de76dc5b415592288295fce2dfe`. SHA1 Git recalculado sobre el contenido **completo** de cada fuente, no solo metadatos proporcionados por el conector.

**E — Ejecución.** Se ha ejecutado el comparador congelado en V8 sobre seis documentos públicos auténticos en tres pares. El SHA1 Git original coincide **6/6** y las tres comparaciones A–J terminan sin excepciones. **No se ejecutaron seis archivos originales en el Node local**, ni se pasó un E2E completo desde disco por el CLI del producto; las 19 pruebas Node anteriores de C09 sí se han repetido y pasado, pero no sustituyen el positive original.

**F — Auditoría adversarial.** Validación de clave compuesta y duplicados, orden temporal, Git de fuente, identidad de recuentos y exclusión de resultados con identificadores. Fuente original con correcciones de fecha y valores continuos: erróneo clasificar todas como revisiones de Y binario. Informar por separado los endpoints post hoc.

**G — Control y transferibilidad.** Un contador de filas detectaría −1, −10 y −3, pero **no** explicaría los cambios en 671 transiciones de filas presentes. El C08 anterior atendía solo al subconjunto binario elegible. Comparar todo el JSON hace explícito el límite de ese subconjunto; no constituye replicación externa porque se usa el mismo publicador y cohortes anteriores.

**H — Prior único y negativo.** Se añade un único prior documental **PF-BR49**: el contenido original se revisa in place entre Git commits, incluso cuando el subconjunto admisible mantiene outcomes estables. Preservar PF-BR01–48 y su información adversarial. Las 671 modificaciones no constituyen 671 descubrimientos.

**I — Dictamen.** **C10 AB-H válido limitado a integridad de fuente original pública y utilidad de QA**, grado científico **0/3**, CT2 prospectiva PFL **20/100 ordinal** sin variar, nuevos N1/N2/N3 **0/0/0**, puertas críticas de lanzamiento **0/6**. Sin participantes, datos personales, permisos externos aceptados, calificación de políticos ni despliegue.

**J — Decisión.** Contar exactamente **un** ciclo C10 de los 30 nuevos autorizados, quedando **10/30 realizados, 20 restantes**. Las dos plazas AB-H históricas permanecen **STOP_R5**. Prioridad ulterior: fuente verdaderamente independiente con derechos, y/o ruta positiva de blobs originales en disco con control upstream; no continuar revisando fechas solo para gastar plazas. Sin `main` merge, CI costosa, ChatRelay ni contacto con autores.

[Recibo de ejecución detallado](C10_RUN_RECEIPT.json) · [Ledger de campaña](CAMPAIGN_STATUS.json).

