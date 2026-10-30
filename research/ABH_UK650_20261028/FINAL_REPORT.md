# Politics Fantasy League · UK650 · AB-H 2026-10-28

**CERRADA: cinco ciclos AB-H A–J ejecutados, 5/5 válidos ACOTADOS de investigación AB-R, 0 inválidos, 0 de planificación, 0 restantes.** Desde `research/pfl-abh5-eu-participation-20261028` (PR #27, base SHA `925ac442a94a6b9497a798b3b6b46afd45739869`) hacia `research/pfl-abh5-ukconstituency-20261028`. No ChatRelay, fusiones a `main`, CI costosa ni evaluación de personas/partidos. Las cinco preguntas quedaron **prerregistradas antes de adquirir y analizar el CSV**. Los documentos de resultados A–J y métricas están en este directorio.

## 1. Fuente, procedencia y límites que condicionan la fuerza de las conclusiones

**Nueva población independiente de las campañas anteriores:** 650 circunscripciones parlamentarias del Reino Unido en las generales del 4 de julio de 2024, con **4.515 candidaturas**. En vez de volver al panel EU27 o a doce votaciones de EE. UU., el nuevo estimando estudia la asociación entre **participación electoral, margen de victoria y fragmentación de candidatos**, y la estabilidad geográfica de esa asociación.

El **publicador institucional original** es la [Biblioteca de la Cámara de los Comunes, General election 2024 results](https://commonslibrary.parliament.uk/research-briefings/cbp-10009/), que ofrece CSV oficiales de [resultados por circunscripción](https://researchbriefings.files.parliament.uk/documents/CBP-10009/HoC-GE2024-results-by-constituency.csv), [resultados por candidato](https://researchbriefings.files.parliament.uk/documents/CBP-10009/HoC-GE2024-results-by-candidate.csv) y un fichero de cambios del conjunto de datos revisado el 5 de enero de 2026. **No logramos descargar directamente ninguno de los archivos del servidor parlamentario**: el lector web rechazó el tipo `text/csv`, `container.download` falló y la petición HTTPS local tuvo error DNS. **0 bytes oficiales originales autenticados y 0 SHA-256 oficiales verificados.** No atribuir al archivo reutilizado una firma del Parlamento ni `first_public_at`.

**Vía real de acceso:** copias públicas de terceros en GitHub, repositorio `emagar/caso-pc-oto2024`, [CSV por distrito](https://github.com/emagar/caso-pc-oto2024/blob/master/data/uk/HoC-GE2024-results-by-constituency.csv) (Git blob `835aae9eb124e215b7f159b2db90fcc9b66416d8`) y [CSV por candidato](https://github.com/emagar/caso-pc-oto2024/blob/master/data/uk/HoC-GE2024-results-by-candidate.csv) (Git blob `dd4c81aee7ace632c1ffc75bd5518363a458f94c`). Ambos archivos de **la misma copia** presentan 650 ONS ID únicos y 4.515 filas de candidatos; **650/650 sumas de candidatos = votos válidos** y **650/650 márgenes por primero/segundo = campo de mayoría**, con cero errores numéricos en los campos analizados. Se creó el [CSV derivado de 650 observaciones](UK650_DERIVED_AGGREGATES.csv) con solo agregados, sin guardar nombres de candidatos; [auditoría de integridad](C01_DATA_QUALITY.json).

**Versiones no intercambiables:** otra copia pública en `ralphascott/UKGE24_wpc_census_summaries` (Git blob `0fccff58e1df830fc9cc4ac8a36aee8ce04d5caf`) también contiene 650 distritos, pero cambia el censo de **11** circunscripciones (diferencia neta de −38.717 electores frente al primer espejo), los votos válidos de **una** (+10), y rechazados de **cuatro** (−190). [Conciliación por distrito](C01_VERSION_SENSITIVITY.json). El primer espejo suma 48.247.224 electores, 28.808.652 válidos y 116.253 rechazados; el segundo 48.208.507 electores, 28.808.662 válidos y 116.063 rechazados. Otra publicación de resumen posterior muestra datos aún distintos; no atribuimos causas ni fechas de corrección sin el changelog parlamentario original. **No se ha mezclado ninguna cifra del segundo espejo con las candidaturas del primero.** La correlación principal sí se recalculó por separado en el segundo espejo, [C02_ALTERNATE_MIRROR_SENSITIVITY.json](C02_ALTERNATE_MIRROR_SENSITIVITY.json).

### Variables/denominadores

- **Participación** = (votos válidos + rechazados) / censo electoral ×100. Es una proporción territorial, no una tasa individual ligada a condiciones socioeconómicas.
- **Margen de victoria** = (votos primero − segundo)/ votos válidos ×100. No es una variable exógena ni disponible antes del recuento final.
- **Número efectivo de candidaturas (ENP)** = 1 / Σ(candidatura votos / votos válidos)². Cada candidatura cuenta, incluida candidatura independiente. No utilizar solo número de partidos nacionales; candidaturas minoritarias y las singulares quedan incluidas.
- **Grupo geográfico** = 12 regiones / 4 naciones (England 543, Scotland 57, Wales 32, Northern Ireland 18). El margen, el ENP y los mismos resultados electorales están **simultáneamente determinados por el escrutinio**, y no identifican causalidad ni predicciones legítimas anteriores a la elección.

## 2. Cinco ciclos y resultados discriminantes

| Ciclo | Evidencia, regla de análisis y contraste |
|---|---|
| [**C01**](C01_RESULT.json) · [prereg](C01_PREREG.json) | Hallazgo de acceso **negativo al original**: cero bytes descargados del servidor Commons. **Pivot R5** a dos copias GitHub del mismo archivo parlamentario, con 650 distritos, 4.515 candidatos, 650/650 votos conciliados y 650/650 mayorías. Comparador independiente de otra **copia** detecta **11/1/4** variables de censo/válidos/rechazados diferentes. Es control de calidad por versión, NO certificación del original ni un nuevo emisor institucional. |
| [**C02**](C02_RESULT.json) · [prereg](C02_PREREG.json) | Con n=650, margen de victoria frente a participación: **Pearson −0,28657**, **Spearman −0,27616**. Cuartiles ordenados de menor a mayor margen: participación media **62,1733 / 61,1650 / 59,0885 / 57,3975 %**, diferencia extremo **4,7758 pp**. Regresión lineal simple de participación: **−1,70 pp por +10 pp de margen**; **R²=0,0821**. Cuadrática R²=0,08214, casi idéntica. Repetido en la segunda copia distinta: Pearson **−0,28953**, Spearman **−0,27897**; el signo y magnitud se mantienen, aunque la fuente original sigue sin autenticar. [Cálculos](C02_METRICS.json). Asociaciones no causales. |
| [**C03**](C03_RESULT.json) · [prereg](C03_PREREG.json) | ENP real con 4.515 filas de candidaturas: media ENP **3,47485**; con turnout Pearson **+0,0460**, Spearman **+0,0706**, casi nulo. Margen y ENP correlacionan **−0,5827**. En OLS que condiciona por margen, ENP tiene pendiente **−2,463 pp** de turnout por unidad ENP (SE robusto HC3≈0,631); incluyendo región **−2,623 pp** (SE HC3≈0,555), **signo contrario** a la asociación bivariada. **No** afirmar que fragmentar candidaturas reduce participación: puede tratarse de un efecto supresor matemático de variables derivadas de los mismos votos. [Cálculos](C03_METRICS.json). |
| [**C04**](C04_RESULT.json) · [prereg](C04_PREREG.json) | La pendiente de margen sobre turnout pasa de **−0,16999 pp de turnout por punto de margen** (simple, R²=0,0821) a **−0,11404** con efectos de **12 regiones** (R²=0,2566): atenuación de **32,91 %**. Spearman por nación **England −0,299**, **Wales −0,496**, **Scotland +0,191**, **Northern Ireland +0,234** (NI n=18); variación de signo importante, sin causalidad ni conclusión global universal. Son regiones y partidos/competencias diferentes, no muestras aleatorias de un único tratamiento. [Cálculos](C04_METRICS.json). |
| [**C05**](C05_RESULT.json) · [prereg](C05_PREREG.json) | Contraste de generalización *geográfica interna* con grupos completos excluidos del entrenamiento. **Dejar una nación fuera** (4 grupos), MAE en pp: media entrenamiento **5,8722**, margen **5,7855**, margen+ENP **5,8067** (ENP empeora +0,0213 pp frente a margen). **Dejar una región fuera** (12 grupos): MAE **5,7485**, margen **5,4461**, margen+ENP **5,4407** (mejora trivial **0,0054 pp**). Pre-regla de mejora relevante ≥0,5 pp NO se supera. Resultados calculados por grupo entero, no split aleatorio; ninguna de estas cifras es verdadera predicción electoral, pues margen y ENP **son datos posteriores a la votación**. [Cálculos](C05_METRICS.json). |

El patrón del contraste principal (margen y participación) es **estadísticamente descriptivo, no efecto causal demostrado de competitividad**. Pueden intervenir renta, nivel educativo, edad, composición social, movilización, calidad del censo, ubicación, campaña o instituciones; el ajuste por regiones no controla todos estos factores. R1 unidad de circunscripción; R2 comparadores competentes de media, margen, margen+ENP y efectos geográficos; R3 muestras seleccionadas antes de datos, pero históricas, sin modelo temporal ciego; R4 negativos/cambios de signo y ablaciones; R5 detención de intentos de descarga fallidos con rescate de fuentes terciarias y etiquetas de calidad.

## 3. Ejecución, código y limitaciones importantes

- C02–C05 **sí se calcularon realmente en JavaScript V8**, recorriendo las 650 observaciones derivadas de la copia fuente cargada por el conector GitHub. Los resultados exactos se guardaron en [UK650_METRICS.json](UK650_METRICS.json) y JSON por ciclo. Se utilizó cálculo de rangos medio (Spearman), OLS y matriz HC3, diferencias por cuartiles, regiones y validación de grupos enteros.
- [replay_uk650.py](replay_uk650.py) **preparado para reproducción** en Python `pandas/numpy/scipy/statsmodels/sklearn`, con validación de consistencia, regresiones y CV agrupada; **NO se ha ejecutado en checkout limpio**, y su existencia no demuestra todavía una réplica numérica independiente del cálculo JS.
- No se ejecutó toda la suite Python/Node/Atlas de PFL. No originales institucionales autenticados, no `first_public_at`, no auditoría externa independiente de fuente. La Biblioteca ha revisado los datos varias veces, al menos una publicación lista cambios hasta enero 2026, pero no atribuir ninguna cifra concreta a esos cambios sin el original.
- Datos agregados de política electoral únicamente: no se ha perfilado ni puntuado a candidatos concretos, partidos o electores, no se ha calculado preferencia individual ni recomendación persuasiva.

## 4. CT2, límites científicos y progreso contractual

| Métrica | Antes | Cierre |
|---|---:|---:|
| AB-H concedidos / ejecutados | 5 / 0 | **5 / 5** |
| AB-R / AB-P / inválidos / planificación | — | **5 / 0 / 0 / 0** |
| CT2 científico identidad (ordinal) | 29/100 | **29/100** |
| VSDS | 1/3 | **1/3** |
| V4 contractual | 36,90 % | **36,90 %** |
| Logros acreditados | 2/90 | **2/90** |
| Gates | 0/6 | **0/6** |
| Nuevos N1 / N2 / N3 | 0 / 0 / 0 | **0 / 0 / 0** |

[Ledger y commits](CAMPAIGN_STATUS.json) · [CT2 por ciclo](CT2_TRAJECTORY.json) · [CT2 completo y ampliado](CT2_FULL_AND_ZOOM.svg). **2/3 NO acreditado**: un conjunto de resultados electorales históricos de terceros con una asociación ecológica ya plausible no prueba un mecanismo original de Politics Fantasy League, ni predicción externa, ni ventaja superior a controles de una nueva línea científica. No subir el índice por contar cinco ciclos.

## 5. Ejecutores y bloqueos reales

**[T021 · capturar originales parlamentarios y reproducir UK650](../../tareas_codex/T021_UK650_ORIGINALES_Y_RÉPLICA_20261028.md) — PREPARADA, NO EJECUTADA.** Solicita descarga autenticada de ambos CSV oficiales y del historial XLSX de correcciones, SHA-256 de bytes, concordancia de 650 ONS ID, revisión de los conflictos 11/1/4, ejecución nativa del script y suite Python/Node/Atlas integral. No modificar campañas históricas retrospectivamente ni reclamar que se ejecutó Codex.

Continúan pendientes **T011, T016, T017, T018, T019 y T020**; ninguna consume un ciclo ni se ha ejecutado de manera implícita.

## 6. Criterio de parada R5 y solicitud futura

**STOP** en el mismo panel británico de 2024 hasta conseguir el original autenticado o un año/país nuevo seleccionado antes de consultar resultados. No hay motivo para repetir cinco transformaciones adicionales del mismo fichero ni para presentar MAE de variables post-electorales como forecast.

**SOLICITO 5 CICLOS AB-H ADICIONALES**, sujetos a nueva autorización explícita, solo para estimandos diferentes, fuentes originales verificadas o diseño prospectivo serio con variables disponibles *antes* del evento. No reclamar autorización nueva por esta frase ni realizar trabajo a futuro en segundo plano.

