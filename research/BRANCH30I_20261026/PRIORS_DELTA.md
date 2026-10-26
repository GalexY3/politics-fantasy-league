# PF-BR30I — nuevos priors de 30 ciclos (26 octubre 2026)

Se preservan sin borrado todos los priors PF-H, PF-CONT, PF-MG y anteriores. Este documento registra **observaciones y actualizaciones de confianza condicionadas por una elección y dos fuentes**, no conclusiones universales, probabilidades bayesianas numéricas ni causalidad política.

## PF-I01 — Concordancia externa de agregados electorales
*Proposición*: para las 52 circunscripciones de las elecciones al Congreso de julio 2023, los seis recuentos del Cuadro I oficial JEC/BOE coinciden con la columna correspondiente del CSV secundario: **312 de 312**.
*Procedencia*: [BOE-A-2023-18907](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907), cuadro I; transcripción MANUAL publicada en `JEC_2023_TABLE_I_TRANSCRIPTION.psv`; [anerodata 202307.csv](https://github.com/anerodata/data-elecciones-congreso-espana/blob/main/202307.csv), Git blob `59a7734f0deba570ea87681236ecd4c9008ebd33`.
*Favor*: correspondencia exacta 52x6 por código de provincia y sumas nacionales [37.469.458, 24.952.447, 24.688.087, 24.487.414, 200.673, 264.360]. *En contra/incertidumbre*: un único año/acto y documento original transcrito manualmente; no se ha descargado ni hasheado PDF original en el repositorio. Los datos secundarios pudieron derivar de la misma fuente documental. *Falsador*: cotejo automático de los bytes originales encuentra discrepancias o correcciones no consideradas.
*Estado*: RESULTADO DESCRIPTIVO DOCUMENTAL INDEPENDIENTE DE PUBLISHER, NO INDEPENDIENTE ESTADÍSTICAMENTE; no demuestra calidad individual de labels ni predictibilidad.

## PF-I02 — Exhaustividad aritmética de las columnas de opciones de 2023
*Proposición*: las 59 columnas de votos de etiquetas de candidaturas del CSV suman a los votos a candidaturas de la JEC en cada provincia, 52/52.
*Favor*: código `scripts/jec2023_audit.mjs` compara y arroja 0 discordancias. *En contra*: pueden subsistir nombres fusionados, columnas rotuladas incorrectamente o mezclas de partidos y coaliciones. *Falsador*: fuente primaria por candidatura presenta una etiqueta ausente o cifra mal asignada.
*Estado*: INVARIANTE DEL ARCHIVO SECUNDARIO + COTEJO DEL TOTAL EXTERNO, no censo de partidos legales.

## PF-I03 — Verificación documental individualizada de cinco opciones sin escaños
*Proposición*: los totales nacionales PACMA 169.237, CUP-PR 99.644, Frente Obrero 46.274, NC-bc 45.595 y PDeCAT-E-CiU 32.016 coinciden con el Cuadro III oficial de la JEC/BOE.
*Favor*: cinco comparaciones exactas por sigla única, 5/5. *En contra*: selección a posteriori de los primeros cinco publicados; no muestreo aleatorio, no certifica las otras 54 etiquetas. *Falsador*: desglose provincial original contradice la suma o existe una revisión oficial posterior.
*Estado*: CONFIRMACIÓN DOCUMENTAL LIMITADA, no éxito predictivo.

## PF-I04 — Inclusión de opciones sin escaños
*Proposición*: 48 de 59 etiquetas del archivo 2023 registran votos y cero escaños; suman 606.450 votos, **2,4766% de los votos a candidaturas**.
*Favor*: análisis reproducible de 52 provincias; confirma actividad electoral documentada sin representación congresual. *En contra*: una etiqueta puede ser coalición, lista o candidatura, no necesariamente un partido jurídicamente distinto. Ninguna cifra estima influencia, relevancia, competencia o probabilidad electoral. *Falsador*: comparación del cuadro oficial III completo cambia la clasificación o la suma.
*Estado*: DESCRIPTIVO ESPECÍFICO DE ELECCIÓN, no teoría de campo político validada.

## PF-I05 — Coaliciones como entidad jurídicamente diferenciada
*Proposición*: se distinguen 12 entradas en la página oficial de coaliciones ante la JEC y 4 ante juntas provinciales para 2023, incluyendo referencias senatoriales.
*Favor*: [JEC central](https://www.juntaelectoralcentral.es/cs/jec/elecciones/coalicionesJEC?fechaeleccion=2023-07-23&tipoeleccion=Elecciones+Generales) y [JEP provinciales](https://www.juntaelectoralcentral.es/cs/jec/informacion/enlaces/GENERALES_2023Abrl_CoalicionesJEP), ambos HTML oficiales consultados y transcritos. *En contra*: no es necesariamente inventario exhaustivo de todas las candidaturas jurídicas, ni demuestra nombre o membresía del RPP. *Falsador*: actas de juntas provinciales no incluidas/documentos de cambios obligan a ampliar la tabla.
*Estado*: FUENTE DOCUMENTAL DE FORMAS DE COALICIÓN, no censo jurídico nacional.

## PF-I06 — Enlace por siglas ≠ identidad legal
*Proposición*: 10 de las 16 referencias JEC/JEP tienen coincidencia única por sufijo de siglas con una etiqueta de las 59; 4 sin enlace exacto y 2 referencias marcadas únicamente para Senado.
*Favor*: `coalitionCrosswalk` deliberadamente no usa similitud difusa; 10 aristas en grafo de 75 nodos. *En contra*: `JUNTS`, por ejemplo, puede tener variantes tipográficas que el algoritmo no enlaza; NO deducir ausencia de la coalición. Tampoco inferir automáticamente partidos constituyentes. *Falsador*: ID legal cruzado con candidatura proclamada determina un enlace diferente.
*Estado*: ENLACE DOCUMENTAL CONSERVADOR CON INCERTIDUMBRE, no validación de identidad jurídica.

## PF-I07 — Variación geográfica de la oferta electoral documentada
*Proposición*: entre las 52 provincias del archivo hay entre 8 y 14 etiquetas con votos positivos por circunscripción.
*Favor*: 52 filas, 59 columnas con denominadores observados. *En contra*: la variable refleja oferta electoral y codificación del archivo, no pluralismo subjetivo ni fuerza ideológica. *Falsador*: BOE 2023 por provincia detecta opciones no recogidas o etiquetas dobles.
*Estado*: DESCRIPTIVO, sin comparación de calidad política por provincia.

## PF-I08 — No inferir disponibilidad temporal de una copia final
*Proposición instrumental*: la igualdad histórica de una copia en 2026 con la tabla oficial de 2023 no certifica fecha de primera publicación de cada atributo ni ausencia de backfill.
*Favor*: ninguna captura archivada original con first_public_at; el motor bloquea scoring de personas reales y pronóstico as-of. *En contra*: la fecha del BOE fecha algunos agregados como publicados, pero no certifica cuándo se dispuso de una versión específica de cada CSV/candidatura. *Falsador*: historial de capturas originales con timestamp verificado permite reproducir campo disponible a cada corte.
*Estado*: PRECAUCIÓN TEMPORAL, no experimento longitudinal.

## PF-I09 — Integración de producto con origen observable
*Proposición*: el atlas visual muestra siglas de coalición oficialmente documentadas y cinco opciones con total de votos individual contrastado; la API expone el estado documental sin puntuaciones personales.
*Favor*: nuevo esquema de atlas, [read-only adapter](../../src/politics_fantasy/electoral_atlas.py), [HTML/JS](../../src/politics_fantasy/web/app.js), 30 checks V8 de contratos. *En contra*: no hay verificación de E2E navegador ni de ejecución de workflow GitHub Actions en este turno. El SHA Git del dato fuente no garantiza licencia de redistribución del original ni autentica una transcripción manual.
*Estado*: PRODUCCIÓN SOFTWARE INSPECCIONADA Y PARCIALMENTE PROBADA; no producto público desplegado.

## PF-I10 — Apariencia de hallazgos por multiplicidad AB
*Proposición*: 30 decisiones A–J, múltiples invariantes aritméticos de un mismo acto electoral y un grafo formal NO son 30 resultados sociológicos independientes.
*Favor*: fuentes/documentos repetidos y tests dependientes del mismo corpus; 30/30 aceptaciones V8 y confirmación documental externa parcial. *En contra*: no todas las reglas de QA prueban comportamiento real de un usuario, y no se ha auditado la totalidad del RPP. *Falsador*: estudios futuros verdaderamente independientes con nuevos periodos/fuentes/actores y estimandos refutables.
*Estado*: GOBERNANZA, mantener escala científica AB 0/3 para nuevas teorías.

## Nota final de contabilidad
- Priors anteriores sin eliminación, novedades PF-I01–PF-I10.
- **N1/N2/N3 nuevos=0**; no se estableció contribución teórica original ni resultado predictivo prospectivo.
- VSDS proyecto permanece 1/3. CT2 multiactor 20/100, predictiva parlamentaria 24/100, ambas **escalas ordinales de ramas diferentes, sin cambio por pruebas de ingeniería**.
- La comparación oficial fortalece la procedencia de los agregados de julio de 2023 pero **no** prueba influencia, mérito, ideología o adecuación para puntuar personas.
