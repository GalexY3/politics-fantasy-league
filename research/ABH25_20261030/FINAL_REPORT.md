# ABH25 · cierre de 25 contrastes con pivot y límites · 30/10/2026

**Autoridad:** [ledger](AUTHORIZATION.json) `PFL-ABH25-20261030-POSTACCESS`; nueva concesión separada de READ5-CONTINUE15 (15), ABH10 (4), INTEGRATION10 (10) y STOP_R5 histórico (2). Se abrieron 25 pruebas A–J con resultado, **25/25 ejecutadas de alcance limitado, saldo 0**. El piloto documental **C03 NO se cuenta**: sus intentos fueron de planificación bloqueada; por eso la numeración de ejecutadas es C01, C02 y C04–C26. Conservar numeración y negativos.

## AB-R: 13 contrastes de investigación, fuentes o formalización

- **C01**: auditoría original de *Suite à donner*, código congelado antes de inspección; no acreditó primera fecha pública de cada decisión en el script. No generalizar al resto del sistema. [Recibo](C01_RUN_RECEIPT.json).
- **C04 y C07**: dos primeras páginas distintas, no aleatorias, del JSON oficial de peticiones británicas: 25 cerradas por página, con hashes originales `4a60864bcae9d87c35034836640c6ca470f9aaf47c0fb06b53e164d3a661bdee` y `6d2cae6f74f171369b757715f87483aa2808d1f310df9c937657f18bdcd7c63f`. C04 mezcló campos de umbral y respuesta en un recuento ingenuo; NO se interpreta como respuesta efectivamente publicada. En C07 se midieron **por separado**: 25 fechas de umbral, 25 fechas/objetos de respuesta y 23 fechas de resultado de debate, **solo para los 25 registros seleccionados de la segunda página**. No son tasas de toda la población ni evidencia causal. [C04](C04_RUN_RECEIPT.json), [C07](C07_RUN_RECEIPT.json).
- **C08, C09, C10, C11, C12, C15, C17, C23, C24 y C26**: diez contrastes formales/sintéticos distintos sobre identificación parcial, inversión de Simpson, unidades de bootstrap, exclusión temporal, exposición conjunta, calidad JSONL, aptitud de datos externos, `as-of` documental, mayoría absoluta frente a moda y bins sin soporte. Son verificaciones matemáticas/técnicas contra los módulos existentes; **no nueva evidencia social ni nuevas teorías originales**. [Contrato A–J](C08_C26_PREREG_AJ.json), [recibo común](C08_C26_RUN_RECEIPT.json).

## AB-P: 12 contrastes técnicos de producto

- **C02**: HTTP real de dos cuentas ficticias, clubes, transferencias, alineación, jornada y reinicio, 2/2 PASS en [Actions #41018524103](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41018524103).
- **C05**: seis asentamientos concurrentes con un único cambio; **C06**: revisiones con fechas de publicidad y sin filtración futura. [Actions #41077730564](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41077730564), 2/2 PASS.
- **C13, C14, C16, C18, C19, C20, C21, C22 y C25**: nueve controles sintéticos sobre tipología de alegaciones, elegibilidad de origen, mercado artificial, inmutabilidad de reglas, expiración de sesiones, registro simultáneo, JSON malformado, OOXML/ZIP y ocho jornadas consecutivas. Pasaron en [Actions #41078862636](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41078862636). La ejecución emitió `ResourceWarning` de SQLite durante C21, **no ocultado**. No acredita despliegue seguro, aceptación humana ni exactitud del contenido político.

## Vía bloqueada sin consumir ciclo: C03

La [captura metadata-only oficial](C03_STAGE0_CSV_RECEIPT.json) obtuvo un CSV de 29 filas, MD5 correcto, pero sin ID de reunión/referencia acta. El [ZIP estructurado](C03_STAGE1_BLOCKED.json) tenía un MD5 distinto del publicado, antes de inspeccionarlo. Bajo **STOP_R5 se aparca esa fuente** hasta versión del editor autenticada, sin impedir el pivot hacia Reino Unido y las pruebas formales.

## Reproducibilidad, decisiones y alcance

- **Preprereg y fuente/código:** congelados en commits individuales de C01/C02/C04–C07 y en el contrato colectivo C08–C26 antes de nuevos outcomes; enlaces/commits en cada recibo.
- **Ejecución:** C08–C26, **19/19 PASS en Linux**; no son diecinueve cohortes, hallazgos o réplicas empíricas. Fuente oficial UK accesible con diferencias respecto del estimando francés C38.
- **Trazabilidad:** priors PF-BR81–PF-BR84, grafo O7 y lote append-only Atlas97. [Actions #41079465386](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41079465386) reprodujo **97 lotes, SHA-256 `609e93fa0abd03b4b0137bbe7549a745fd0a4f8c7317932cb6fc9057ba573ebc`**.
- **Sin promoción:** CT2 científico 20/100 ordinal, nuevos N1/N2/N3=0/0/0, grado de descubrimiento original 0/3, gates 0/6. No equiparar cuota completada con teoría contrastada externamente.
- **Producto:** P1 sigue **READY_REVIEW** hasta aceptación visual humana; P2 no se declara lanzado. Pruebas aisladas no sustituyen suite completa ni auditoría de producción.
- **Estado de publicación:** cambios en PR #3 **draft**, separados de `main`; ninguna fusión ni despliegue.

**AB-DECIDE:** El requisito de agotar la concesión se ha satisfecho mediante pivotes reales y pruebas diferenciadas, no repitiendo C03. El bloqueo de resultados sociológicos originales suficientes persiste y no se ha resuelto con simulaciones. La siguiente tarea ya no es gastar más ciclos: revisión humana de P1 y búsqueda de un corpus institucional versionado que permita observar decisiones completas.
