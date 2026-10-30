# T024 · Australian Electoral Commission 2025: originales y réplica completa

**PENDIENTE / NO EJECUTADA / NO CONSUME CICLOS AB.** Base: `research/pfl-abh5-aec-choice-20261028` en `GalexY3/Metodologia-AB`; leer `AGENTS.md`, AB 3.2.1 O3–O6, `proyectos/politics-fantasy-league/ab_atlas/CURRENT.md`, `research/ABH_AECCHOICE5_20261028/FINAL_REPORT.md` y `CAMPAIGN_STATUS.json`. Rama ejecutora nueva `exec/pfl-t024-aec-originals-20261028`, PR borrador hacia AECCHOICE5, nunca main; sin ChatRelay, CI costosa, datos nominativos ni puntuaciones políticas.

## Originales obligatorios, con ruta exacta y cronología

Fuente institucional primaria AEC `https://results.aec.gov.au/31496/Website/HouseDownloadsMenu-31496-Csv.htm`, elecciones federales del 3 mayo 2025, fecha del `generated` en las copias 16 junio 2025.

Cuatro CSV de divisiones con nombre exacto (localizar vínculo CSV real en catálogo, no inventar host):
- `HouseNominationsByDivisionDownload-31496.csv` (nominaciones; variable fijada antes de elecciones; mirror Git blob `aef89aafac5cea807c38159abcc841b9ad82046a`).
- `GeneralEnrolmentByDivisionDownload-31496.csv` (campo `CloseOfRollsEnrolment` antes de elecciones; mirror `4b7962ef4fc1eebde9961ba5d662da6699dcb3d7`).
- `HouseInformalByDivisionDownload-31496.csv` (votos informales totales por división; mirror `bacba88b544695c25e1178546355f19c04d2b915`).
- `HouseTurnoutByDivisionDownload-31496.csv` (participación; mirror `9849657147267214f28d091a83c03cede6bc2c67`).

En esta campaña se **vieron los enlaces primarios**, pero **no se descargaron originales**: el navegador web dio cache miss al abrir CSV y el contenedor Python devolvió DNS failure. Los **cuatro CSV de GitHub son copias de tercero**, las cabeceras internas dicen `Generated:2025-06-16`, pero el hash Git **NO** prueba autenticidad del archivo original, certificación TLS, ni el primer momento público de disponibilidad de cada predictor. Repetir capturas con PC/Work autorizado: URL efectiva, TLS/redirect, código HTTP, tamaño, tipo, SHA256 de bytes crudos, `ETag/Last-Modified` si existen, fecha UTC de descarga, enlace de licencia y cadena documental de publicación. Comparar SHA en las copias GitHub mediante el cálculo de git blob hash y byte_sha256 aparte; **no confundirlos**.

## Replicación de números + controles reales

Reproducir en **checkout limpio** el CSV derivado `research/ABH_AECCHOICE5_20261028/AEC2025_DIVISION_PANEL.csv` y el `C01_SOURCE_AUDIT.json`, con joins `DivisionID` de 150/150, 8 estados y 4 clases demográficas, sin discrepancia en tasas calculadas (<0,012 pp redondeo). Suma nacional: **919.512 votos informales / 16.409.748 papeletas = 5,60345 %** (AEC publica 5,60%). La fuente AEC independiente de recuento aparece en `https://www.aec.gov.au/About_AEC/research/files/analysis-informal-voting-2025-election.pdf` (abril 2026), que estudia **25 divisiones seleccionadas por alto voto informal** y no es representativa. No usar su taxonomía para representar nacionalmente.

Calcular **Pearson +0,5763872 y Spearman +0,6906767**, quitando dos casos ya expuestos Calwell/Riverina rho +0,6798433. OLS regular con HC3 y efectos por estado + AEC demographic + log(close-of-rolls), coeficiente nominaciones **+0,838263 pp por candidatura**, HC3SE **0,111535**, R2 sin elección 0,468528 y con 0,632917. Diferencia de informales entre papeletas con 7+ vs <=6 candidaturas: **+2,56625 pp**, excluyendo dos ejemplos +2,47964. Validación dejando **un estado completo fuera** (8 folds) y sin estado FE para estados nunca vistos: MAE media 2,48457; AEC clase+log(enrolment) 2,39580; +nominaciones 1,98009 pp, ventaja +0,41571. **Todos son análisis retrospectivos**: las cabeceras se generaron pos-electoralmente, aunque número de nominaciones y close rolls sean conceptualmente disponibles antes de votar. Reproducir en Python/Node con librería de estadísticas competente, tolerancias, código de salida y hashes, y registrar cualquier discrepancia.

## Test científico / preevent criteria

La asociación es conocida y previa: McGinn & Maruyama (2025) `https://doi.org/10.1111/1475-4932.12877` ya encuentran un efecto causal en 2004–2016 usando variación inducida por cambio de circunscripciones; nuestra regresión transversal 2025 **NO replica esa identificación causal ni es nueva teoría**. La norma AEC explica que las papeletas con más candidatos requieren preferencias completas, pero votos informales incluyen deliberados y errores. Se recomienda preparar un **nuevo ensayo científicamente discriminante con sello temporal anterior a la elección siguiente**, por ejemplo históricos AEC genuinos de 2019/2022 como training, 2025 un bloque temporal previamente no explorado para otras variables o 2028/2029 prospectivo si está disponible; fijar features medidos realmente antes del evento, baselines y cortes, sin convertir comparación retrospectiva ajustada en forecasting probado. Todo experimento científico futuro requiere autorización AB nueva.

## Entregables/aceptación

`tareas_codex/T024_RESULTADO.md`, `T024_EVIDENCIA/MANIFEST.json` (estado original files y SHA, primeras URLs, log reproducción, command versions, first failing test and full Python/Node/Atlas QA). RESULTADO **SUCCESS** solamente si 4 originales auténticos, 150/150 reconciliación, ensayo reproducido con datos originales y suites completas PASS; **PARTIAL/BLOCKED** si falta algo, con evidencias concretas. No declarar T024 ejecutado antes del resultado del executor, no fusionar main ni premiar nuevas N1/2/3 o CT2 automáticamente.
