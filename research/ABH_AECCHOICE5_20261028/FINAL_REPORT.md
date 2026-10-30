# Politics Fantasy League — AECCHOICE5 · Informe final 28/10/2026

**CERRADO: 5/5 ciclos AB-H A–J ejecutados válidos acotados, cinco AB-R, 0 inválidos, 0 planificación, 0 restantes.** Una tentativa de descarga del original falló y se contabiliza aparte **sin sumar ciclo**. Rama `research/pfl-abh5-aec-choice-20261028`, desde PETITIONCOHORT5 / PR #30, base SHA `31161fee11030cd7a03217dfaa766065b8133dea`. Ninguna fusión a main, ningún ChatRelay ni CI costosa, ninguna calificación de actores o partidos.

## 1. Nueva pregunta y relevancia previa: candidaturas en la papeleta y votos informales

**Nueva población:** las **150 circunscripciones** de elecciones federales australianas del **3 mayo 2025**; no se reutilizó el panel de peticiones, UK650, EU27 ni votaciones anteriores. Pregunta sociológica: ¿un conjunto más amplio de opciones electorales se relaciona con más papeletas inválidas/informales por dificultad o coste de completar preferencias, incluso frente a explicaciones territoriales? El outcome es **% de votos informales entre papeletas emitidas**, no preferencias de electores ni una medida pura de confusión. En Australia pueden ser intencionales (blancas, rechazo explícito) o accidentales (numeración incorrecta); no es posible individualizar causas a partir de totales por distrito. [Reglas AEC de papeletas formales](https://www.aec.gov.au/Voting/How_to_Vote/Voting_HOR.htm).

**Novedad científica ya contestada por otros, crucial para la adjudicación:** Eamon McGinn y Shiko Maruyama, [*Why Waste Your Vote? Informal Voting in Compulsory Elections in Australia* (2025)](https://doi.org/10.1111/1475-4932.12877), **ya** documentan en elecciones 2004–2016 una relación causal entre más candidaturas y más votos informales, con una estrategia que utiliza cambios de circunscripciones. La [AEC revisó en abril de 2026 papeletas informales](https://www.aec.gov.au/About_AEC/research/files/analysis-informal-voting-2025-election.pdf) de **25 circunscripciones escogidas por alta tasa de voto informal** y encontró señales de errores de preferencias con papeletas largas; **esa submuestra no representa al país**. Además, la [AEC participación 2025](https://www.aec.gov.au/election/fe25/participation-rates.htm) destacó previamente **Riverina y Calwell**, ambas con 13 candidaturas y elevadas tasas informales: dos observaciones pre-expuestas antes de nuestros prerregistros. No confundir coherencia descriptiva temporal con una contribución original o una replicación del diseño causal previo.

## 2. Trazabilidad de fuente, antes/después y control de calidad

La [página oficial AEC de descargas 2025](https://results.aec.gov.au/31496/Website/HouseDownloadsMenu-31496-Csv.htm) enumera las tablas primarias de nominaciones, enrolment, votos informales y participación por circunscripción; la mayoría de sus enlaces CSV no pudo abrirse directamente desde este entorno (cache miss y DNS del contenedor). **Los cuatro CSV analizados proceden de una COPIA PÚBLICA DE TERCERO** `rNLKJA/public-services-open-source-data`, [directorio raw](https://github.com/rNLKJA/public-services-open-source-data/tree/main/original/datasets/au-federal-election-results/raw), con **cuatro hashes Git blob exactos**. Contienen cabeceras AEC con fecha de **generación 16 junio 2025**, posterior al evento electoral. Se conservaron nombres, nombres de columnas y fingerprints en [C01_SOURCE_AUDIT.json](C01_SOURCE_AUDIT.json). **Cero bytes originales descargados desde la AEC; no hay SHA256 del original, `first_public_at` ni evidencia documental de que esas COPIAS de junio existieran antes de la votación**. Sin embargo, el número final de nominaciones registradas y el censo al cierre de inscripciones son *variables determinadas antes del evento por su significado institucional*, no necesariamente snapshots publicados con timestamp autenticado. No afirmar *backtest prospectivo*.

Se unieron cuatro fuentes por `DivisionID` para **150 divisiones únicas**, todas con 8 estados/territorios y 4 categorías AEC (*Inner Metropolitan, Outer Metropolitan, Provincial, Rural*), sin ausencias, duplicados o inconsistencias en nombres, censos finales, fracciones calculadas ni voto total contra participación. [Panel agregado AEC2025_DIVISION_PANEL.csv](AEC2025_DIVISION_PANEL.csv). Suma de votos informales **919.512** sobre **16.409.748** papeletas, tasa **5,60345 %**, conciliada con el **5,60 %** que publica la AEC en su informe oficial. Es control de agregado, **no certificado criptográfico** de cada fila original.

**Antes de elección (por definición, no por sello de esta copia):** `Nominations`, `CloseOfRollsEnrolment`, `Demographic` / estado. **Después:** `InformalVotes`, `InformalPercent`, `TurnoutPercentage`, `TurnoutSwing`. Solo se utilizaron los primeros como variables explicativas de los modelos; una fuente generada después obliga a explicitar que la *disponibilidad real en la fecha de predicción* no está probada. [Resultado C01](C01_RESULT.json).

## 3. Cinco ciclos prerregistrados antes de leer las 150 respuestas

| Ciclo A–J | Comparador y resultado | Falsador y límite |
|---|---|---|
| [C01](C01_RESULT.json) / [prereg](C01_PREREG.json) | Acceso documental AEC oficial al catálogo, y cuatro copias públicas AEC con **150/150 joins, 0 discrepancias**. Nacional **919.512 / 16.409.748 = 5,60345 %**. | Descarga original **no disponible**; original SHA=UNKNOWN. Válido como auditoría acotada de copia, NO fuente primaria autenticada. |
| [C02](C02_RESULT.json) / [prereg](C02_PREREG.json) | Nominaciones y % informal: **Pearson +0,57639**, **Spearman +0,69068**, OLS simple **+1,0018 pp de voto informal por nominación** (R² **0,3322**). Media de % informal en cuartiles de nominaciones: **3,756 / 4,536 / 6,229 / 7,763 %**. Excluyendo Calwell y Riverina (pre-expuestos), Spearman **+0,67984**, n=148. | Se apoya hipótesis exploratoria positiva `rho>0,20`, pero la literatura **ya había descrito** el mecanismo, no se identifica causalidad con esta correlación ecológica. |
| [C03](C03_RESULT.json) / [prereg](C03_PREREG.json) | Competente OLS estado (7 FE), AEC demografía (3 FE), log censo de cierre: R² **0,46853**. Añadir nominaciones: R² **0,63292** (**+0,16439**). Pendiente de nominaciones **+0,83826 pp** por candidatura, HC3 SE **0,11153**; intervalo descriptivo robusto 95% **[0,61965, 1,05687]**. | Sin control completo de idioma, educación, selección de candidatos, experiencia de voto o cultura institucional; los errores de distritos comparten estado y son dependientes. Intervalo no confiere identificación causal. |
| [C04](C04_RESULT.json) / [prereg](C04_PREREG.json) | Papeletas con **≤6** candidaturas, n40, informal medio **3,697 %**; **≥7**, n110, **6,263 %**; diferencia **+2,566 pp**. Excluyendo los 2 pre-expuestos, **+2,480 pp**. Hay diferencias positivas en casi todos los estados con ambos tipos; **NT n2** diferencia −0,92 pp, no interpretable con confianza. | Seis/siete **no es discontinuidad legal**, solo corte aproximado de longitud de preferencias. Selección no aleatoria y mezcla de blancos/intencionalidad. La AEC 2026 confirmó la plausibilidad mediante un estudio de muestra sesgada. |
| [C05](C05_RESULT.json) / [prereg](C05_PREREG.json) | **Leave-one-state-out** (8 grupos enteros, n150) para porcentaje informal: MAE de media del entrenamiento **2,48457 pp**; con clase geográfica + log censo antes del voto **2,39580 pp**; añadiendo nominaciones **1,98009 pp**, ganancia **0,41571 pp** que supera el mínimo preregistrado **0,25 pp**. RMSE respectivamente **3,257 / 3,204 / 2,813 pp**. | La definición de variables antecede al evento, pero los resultados y la versión analizada de las fuentes se conocían en el momento de evaluar: **validación interna y retrospectiva**; ocho grupos estatales, NO predicción con corte temporal previo ni holdout 2028. |

[Cálculos completos, gráficos tabulares y comparadores](AEC2025_METRICS.json). Los cinco experimentos numéricos y auditorías **sí se realizaron** en JS V8 sobre los 150 registros obtenidos mediante GitHub; **no** se corrió suite Python/Node/Atlas desde checkout limpio, **no** se ejecutó Codex y **no** se verificaron los cuatro bytes originales de AEC. Los preregistros están registrados con commits anteriores a la carga de la tabla completa de informalidad. Se inspeccionaron dos ejemplos nacionales previamente, y dos filas de participación solo para ver el esquema: no hay reivindicación de ceguera total.

## 4. Evidencia, priors, R1–R5 y atribución de novedad

[Registro actualizado de fuentes y priors](SOURCES_AND_PRIORS.json).

**R1**: unidad electoral división y proxy voto informal, no error individual o “desinformación” inferida; firmas de candidatos individuales no se guardan. **R2**: contraste con baselines competentes que disponen de los mismos predictores, no un rival estúpido; buen control state FE/área/censo y *heldout* por estado completo. **R3**: cinco pruebas relacionadas en un conjunto 2025 retrospectivo, dos casos y la tasa nacional expuestos al explorar la fuente; no calcular p-valores confirmatorios ni asumir independencia entre los ocho estados. **R4**: doble exclusión de Calwell/Riverina, cutoff >6 vs ≤6, ajuste territorial y comparación de pérdidas; registrar patrones negativos parciales en NT y límites de selección. **R5**: STOP tras estas cinco operaciones porque la hipótesis y un diseño causal anterior fueron publicados (McGinn–Maruyama 2025). La prioridad es original de AEC y una evaluación temporal futura, **no repetir regresiones sobre los mismos 150 distritos**.

**Interpretación:** evidencia descriptiva sólida de coherencia con mecanismo ya conocido, y útil para PFL como advertencia sobre variables de complejidad de participación y sobre modelo simple versus complejo. Pero **NO cumple novedad científica 1/3 ni 2/3** ni prueba nueva tesis específica de producto Fantasy. No premiar la significación de una correlación ya esperada ni la mejor MAE de un mismo año.

## 5. Indicadores y CT2

| Medida | Inicio | Cierre |
|---|---:|---:|
| AB-H verdaderamente realizados | 0/5 | **5/5** |
| AB-R/AB-P/ inválidos/ planificación | — | **5/0/0/0** |
| CT2 identidad (ordinal, no probabilidad) | 29/100 | **29/100** |
| V4 contractual | 36,90% | **36,90%** |
| VSDS | 1/3 | **1/3** |
| Logros acreditados | 2/90 | **2/90** |
| Gates | 0/6 | **0/6** |
| Nuevos N1/N2/N3 | 0/0/0 | **0/0/0** |

[Ledger A–J / commits](CAMPAIGN_STATUS.json) · [CT2 trayectoria completa](CT2_TRAJECTORY.json) · [CT2 gráfico completo 0–100 y ampliado 27–31](CT2_FULL_AND_ZOOM.svg). Sin inflación numérica de trayectoria.

## 6. Tareas a Codex, no ejecutadas

[**T024 · originales AEC 2025 y réplica/QA integral**](../../tareas_codex/T024_AEC2025_ORIGINALES_QA_20261028.md), creada y **NO EJECUTADA**, con URLs, los cuatro blobs espejo Git, requisitos SHA-256 originales, controles de calendarios de los predictores, 150/150 joins, reproducción de resultados y suite completa. Persisten tareas **T011 y T016–T023** sin cambio de estado. La descarga original fallida fue una operación de búsqueda C01, no un ciclo adicional ni un desbloqueo.

**SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, sujeto a aprobación separada: preferentemente un corpus independiente con observaciones anteriores a un evento aún no analizado y una hipótesis PFL más específica, en lugar de nuevas variantes sobre la elección australiana de 2025. No ejecutar automáticamente otro bloque.

