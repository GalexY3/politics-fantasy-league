# T021 · Autenticar los originales de UK General Election 2024 y replicar UK650

**PENDIENTE. NO EJECUTADA. No es un ciclo AB.** Partir de `research/pfl-abh5-ukconstituency-20261028` de `GalexY3/Metodologia-AB`; leer `AGENTS.md`, AB 3.2.1, `ab_atlas/CURRENT.md`, `research/ABH_UK650_20261028/CAMPAIGN_STATUS.json` y `FINAL_REPORT.md`. Crear rama propia `exec/pfl-t021-uk650-originals-20261028`; PR borrador contra UK650. **No ChatRelay, main merge, CI costosa ni puntuaciones/etiquetas de individuos reales.**

## Datos originales y cronología exacta

Biblioteca de la Cámara de los Comunes: `https://commonslibrary.parliament.uk/research-briefings/cbp-10009/`, con:
1. CSV oficial `https://researchbriefings.files.parliament.uk/documents/CBP-10009/HoC-GE2024-results-by-constituency.csv` (650 distritos).
2. CSV oficial `https://researchbriefings.files.parliament.uk/documents/CBP-10009/HoC-GE2024-results-by-candidate.csv` (4.515 candidaturas en las copias estudiadas).
3. Hoja XLSX oficial `Record of dataset changes (updated 5 Jan 2026)` desde enlace de la página de briefing, para atribución de modificaciones y comparación de versiones.

**En ChatGPT, la descarga de los originales devolvió unsupported CSV, fallo de descarga y DNS en el contenedor; originales oficiales = 0 bytes y 0 hashes SHA-256 autenticados.** Lo que sí se procesó realmente fueron **copias de terceros** del nombre de archivo de Commons Library, obtenidas por conector GitHub del repositorio público `emagar/caso-pc-oto2024` (`data/uk/`) y comparadas con `ralphascott/UKGE24_wpc_census_summaries`. No elevar un blob GitHub de un tercero a hash de origen oficial.

Hashes de archivo **Git blob de la copia** analizada: distrito `835aae9eb124e215b7f159b2db90fcc9b66416d8`; candidatos `dd4c81aee7ace632c1ffc75bd5518363a458f94c`. Tercera copia de contraste, sin candidato emparejado `0fccff58e1df830fc9cc4ac8a36aee8ce04d5caf`. Al alinear 650 ONS ID entre dos versiones, se hallaron **11 distritos con censo diferente** (diferencia sumada -38.717 de la segunda frente a la primera), 1 con votos válidos diferentes (+10) y 4 con rechazados diferentes (-190). Las dos primeras copias de `emagar` sí conciliaron **650/650** votos válidos contra suma de 4.515 candidaturas y **650/650** márgenes de primero contra segundo. **No combinar** versiones cruzadas.

Para cada original: URL efectiva, verificación TLS, redirecciones, HTTP status, fecha/hora UTC de captura, MIME, tamaño de fichero, SHA-256 de bytes **originales**, formato/delimitador/encoding, identificador de versión y fecha de revisión documentada. Revisar archivo de cambios sin inventar razones para los 11 censos. Guardar originales fuera del Git (gitignored) y solo manifiestos/hashes, estadísticas anonimizadas y logs en el repo. Las copias GitHub no son certificación legal.

## Reproducción y estudios externos

Primero verificar físicamente la transcripción en `research/ABH_UK650_20261028/UK650_DERIVED_AGGREGATES.csv`; para reproducir usar `python replay_uk650.py` desde directorio de investigación, dependencias `pandas numpy scipy statsmodels scikit-learn`. El script Python **se preparó en GitHub y NO fue ejecutado sobre el CSV de un checkout local** durante la campaña: los cálculos originales se ejecutaron **de verdad** mediante JavaScript V8 sobre las 650 filas leídas por GitHub y están en `C02_METRICS.json` a `C05_METRICS.json`. Verificar la reproducción nativa y registrar diferencias si apareciesen.

Expectativas para el espejo analizado: Pearson margen-turnout ≈**−0,28657**; Spearman ≈**−0,27616**; diferencia cuartiles de turnout **4,77583 pp**; 12 regiones; atenuación de pendiente OLS margen con regiones **32,91 %**; ENP vs turnout Spearman **0,07057**, ENP parcial por región y margen **−2,623** pp por unidad, bajo endogeneidad; cuatro naciones heldout MAE mean/margin/margin+ENP **5,8722 / 5,7855 / 5,8067 pp**, 12 regiones heldout **5,7485 / 5,4461 / 5,4407 pp**. No hablar de generalización causal ni previsión, pues margen y ENP se conocen **después** de la votación.

Efectuar validación sobre descarga oficial con **versionado separado**. Comparar cifras con resumen posterior y verificar por qué los totales del espejo difieren de los publicados más tarde: archivo `C01_VERSION_SENSITIVITY.json`. Repetir correlación con versión oficial verificada; registrar diferencia numérica en PR de executor, **sin modificar campañas AB históricas ni adjudicar ciclos científicos nuevos**, para un nuevo ensayo prerregistrado posterior si fuese necesario.

Ejecutar suite completa Python/Node/Atlas en checkout limpio del executor; conservar primera prueba fallida, salidas, versiones, exit codes y hashes. No modificar tests para forzar acierto.

## Condiciones de aceptación

`tareas_codex/T021_RESULTADO.md` y `tareas_codex/T021_EVIDENCIA/MANIFEST.json`, con originales auténticos y su SHA, changelog, columnas, conciliaciones entre versiones, replicación script, QA. `SUCCESS` únicamente con dos originales oficiales capturados y autenticados, changelog contrastado, script y suite completa PASS. `PARTIAL/BLOCKED` según fallos reales, sin contar planificación o descargas fallidas como ciclo AB. Crear PR borrador contra `research/pfl-abh5-ukconstituency-20261028`, no fusionar main. No usar ChatRelay.
