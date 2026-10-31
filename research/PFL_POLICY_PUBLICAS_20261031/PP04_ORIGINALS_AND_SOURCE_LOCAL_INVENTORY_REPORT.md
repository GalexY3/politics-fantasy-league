# PFL · PP-04, adquisición oficial y cohorte fuente-local del PAN 2024

**Fecha:** 31/10/2026. **Estado:** adquisición original autorizada y extracción **parcial de población planificada**, NONCYCLE. **R5 = STOP.** No se ha estimado cumplimiento, duración, causalidad, impacto, efectos de acoplamiento ni capacidad predictiva. Investigación española real, pero aún no contraste AB confirmatorio.

## Continuidad, titularidad y derecho de uso

PR #9 (`0ca37662242e8a24c505f61f29e29855c833b5b6`) fue verificada contra remoto, con árbol limpio antes de crear el checkout independiente `PFL-PAN-IAEN-PP04-20261031`, rama `research/pfl-pan-iaen-pp04-originals-metadata-20261031`. Se mantienen intactos `PFL-trabajo`, PR #8 y #9, `main`, el Atlas99 y `PROJECT_STATE.json`.

El usuario **autorizó explícitamente** la consulta y descarga **local y académica** de los dos PDF del Portal de Transparencia **PAN 2024 e IAEN 2024**, sujeto a sus condiciones generales, y sin distribuir los originales. Tras revisar el [aviso de reutilización del Portal](https://transparencia.gob.es/utilidades/aviso-legal/reutilizacion), se respetan procedencia, integridad de significado, metadatos, fecha de actualización cuando conste y ausencia de patrocinio institucional. No se otorgó permiso de publicación en Git, puntuación política, descarga de otros activos ni aceptación de nuevos clickthroughs.

**Cita de fuente:** «Origen de los datos: Portal de la Transparencia de la Administración General del Estado». El índice oficial del [PAN 2024](https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2024) declara actualización **16/04/2025**; esa fecha es una marca **del índice**, no un testigo `first_public_at` de cada entrada ni del IAEN. Un [anuncio editorial del portal](https://transparencia.gob.es/masinformacion/novedades-de-transparencia/2025novedades/informeanualevaluacionnormativa2024) fechó el informe el 29/04/2025: no inferir que la portada del PDF o sus cabeceras HTTP determinan su primera publicación exacta.

## Activos obtenidos y retenidos PRIVADOS

| Activo | URL oficial exacta | Bytes | SHA-256 | Páginas | Estado |
| --- | --- | ---: | --- | ---: | --- |
| PAN2024 | [Original PDF](https://transparencia.gob.es/content/dam/transparencia_home/publicidadactiva/normativa/pan2024/PAN_2024.pdf) | 2.892.556 | `49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5` | 117 | HTTP 200, `%PDF-`, SHA verificado |
| IAEN2024 | [Original PDF](https://transparencia.gob.es/content/dam/transparencia_home/publicidadactiva/normativa/pan2024/IAEN2024PT.pdf) | 1.296.179 | `7c77a73480f3f039d8ba069e12301b7a4c7ad0eeec85934ec84721526cb88aa2` | 126 | HTTP 200, `%PDF-`, SHA verificado |

Almacén **fuera de Git**: `../PFL-raw-primary/pan_iaen_2024_20261031/` respecto al checkout PP04. Contiene los dos PDF, sus recibos privados y la extracción fuente-local. No se agregaron PDF, cuerpos originales, filas ni títulos a ningún archivo versionado. Un recibo de adquisición local registra HTTP, SHA, origen, condiciones y límite de uso. PDF renderizados al menos en portada; verificación de páginas, índices y esquemas con `pypdf` y Poppler.

## Hallazgo estructural real del PAN: 199 ≠ 198

La **introducción** del propio PAN (PDF página 9, impresión 12) habla de **199 normas proyectadas**. El apartado **«Principales Datos»** (PDF página 14, impresión 18) especifica **198**: 6 leyes orgánicas, 43 leyes y 149 reales decretos. En el cuerpo de propuestas, desde PDF página 37 a la 117, un primer parser `pypdf` identifica exactamente **198 anclas `Objetivo:` y 198 anclas `Ministerio:`**, con emparejamiento ordenado 1:1, clasificadas 6/43/149 por el título normativo inmediatamente anterior. El segundo extractor, `pdftotext` (sin `-layout`) encuentra igualmente **198** de cada etiqueta. En modalidad `-layout`, 198 apariciones se mantienen, pero algunos rótulos ya no están al comienzo de línea; por eso se documenta el riesgo de formato.

**Decisión:** se genera un registro privado provisional de **198 iniciativas planificadas de esa edición**, pero **no** se eleva a padrón independiente certificado ni se asume que la discrepancia «199» es un error de imprenta sin prueba externa. La edición podría tener otra definición editorial, revisión o errata pendiente; no se atribuye causalmente una norma adicional al silencio. Las 198 entradas aún requieren auditoría visual y oficial de sus rótulos, particiones de página, ministerio y versiones. El parser obtiene título inicial y ministerio como **extractos no verificados**: `pypdf` pierde algunos caracteres acentuados. No son IDs oficiales ni sirven de clave PAN↔IAEN.

`scripts/pan2024_local_cohort.py` exige SHA exacto del original, **117 páginas**, lectura únicamente de la sección PAN, controles de 198/6/43/149, ubicación explícita privada fuera de Git, y detención ante alteraciones; escribe de forma exclusiva un JSONL privado y un informe privado, sin sobrescribir ni imprimir nombres o resultados. El recibo SHA de código/tests es previo a la extracción. El JSONL retenido tiene **198 IDs puramente locales** y, para cada uno, tipo, número de página, una línea inicial provisional y un ministerio provisional; los campos `IAEN_link`, `actual_approval_outcome` y `first_public_at` permanecen `null`. Su SHA-256 privado es `66907d212a7d11fbb098f441a9fbb50c1aeb83c8cc0e50832b93c47cb60e17ad`.

## IAEN: delimitación de lectura y riesgo de selección

En el IAEN 2024 se inspeccionaron únicamente **portada, índice y arranque introductorio** (páginas PDF 1–4), y los destinos de sus marcadores estructurales. El informe tiene seguimiento general (sección 3), iniciativas normativas aprobadas (3.2), **normas aprobadas no incluidas en el PAN** (3.4), seguimiento por **22 ministerios** (sección 4), reales decretos-leyes (5) y anexo PRTR. El plan organiza sus entradas por **26 familias temáticas**, que no equivalen a esos ministerios. La simple coincidencia de tema o título no proporciona identidad, aprobación, causalidad o una relación por expediente. **No se examinaron ni extrajeron resultados individuales IAEN** en esta tarea.

Exposición previa: búsquedas anteriores habían mostrado resúmenes agregados de 2024 y 2025. Esos ejercicios no son holdouts confirmatorios ciegos, incluso sin consultar aquí las fichas individuales. La observación del PAN2024 como predictor real es exploratoria y longitudinalmente limitada; la futura evaluación debe definir primero un universo completo, rivales, resultado, fechas, derechos y A–J, con SHA remoto anterior a consulta de outcomes.

## Alcance científico y pendientes

**Lo que sí está demostrado:** dos PDF oficiales concretos adquiridos con el consentimiento actual; hashes y páginas; evidencia directa de la discrepancia 199/198; 198 pares `Objetivo`/`Ministerio` con distribución que coincide con la tabla principal del PAN; un inventario **privado** reproducible y sin desenlaces; diferencia estructural entre clasificación temática del PAN y seguimiento ministerial del IAEN.

**Lo que NO está demostrado:** `first_public_at` de entradas, dos vintages históricos verificables, padrón independiente all-received/admitted-first, un criterio validado de censura o negativos, enlaces oficiales item→norma→evaluación, congruencia sustantiva línea a línea verificada visualmente, permiso de publicación de filas, validez de resultados o mecanismo causal. **R5 STOP** y 0 nuevos AB. No se han movido CT2, Atlas ni puertas de producto.

**Siguiente PP-04:** comprobar manualmente los 198 títulos/páginas con controles estratificados, resolver 199/198 mediante testigo oficial sin seleccionar outcomes y buscar identificadores explícitos o crosswalk oficial PAN→IAEN para el mismo ejercicio. Si la edición carece de clave documental común o versiones históricas, dejar las relaciones como UNKNOWN. No unir automáticamente por semejanza ni utilizar el IAEN para clasificar éxitos antes de preregistro.
