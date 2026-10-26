# Ledger acumulativo de priors sustantivos del proyecto PF

Estado: hipótesis / compromisos de diseño; **ninguna probabilidad a posteriori numérica estimada**. No heredar confianza sustantiva de LARP. Los priors metodológicos A01–A21 residen exclusivamente en Metodologia-AB.

| ID | Enunciado y procedencia | Estado / incertidumbre | Evidencia a favor | Evidencia adversa y falsador |
|---|---|---|---|---|
| PF-P01 | Disponibilidad de registros legislativos estructurados suficientes para empezar por Congreso. Catálogos oficiales. | EMPÍRICO_DOCUMENTAL; alto riesgo de cobertura incompleta | Catálogos Congreso, Senado y BOE inspeccionados | Auditoría de descargas, licencias e identidades podría bloquear ámbito |
| PF-P02 | Separar medición, predicción y puntuación evita confundir convención con hecho. AB R1, teoría de medición. | NORMATIVO | Distinción lógica de constructos | Investigación de usuario podría requerir otras representaciones, sin fusionar la epistemología |
| PF-P03 | La oportunidad institucional y cargo explican gran parte de la variación bruta de actividad. | NO_VALIDADO | Hipótesis institucionalista plausible | Si tras ajustar calendarios/cargos apenas hay heterogeneidad, revisar; también puede cambiar por cámara |
| PF-P04 | Los modelos relacionales predicen mejor que baselines jerárquicos temporales. | NO_VALIDADO; hipótesis principal TFM | Dependencias plausibles por grupo/comisión | Prueba walk-forward de paridad informativa sin mejora invalida ventaja |
| PF-P05 | Los precios fantasy pueden reflejar pronósticos de puntos futuros, pero las pujas incorporan popularidad/sesgos. | NO_VALIDADO | Racionalidad limitada y mercado endógeno (hipótesis) | Si cambios de precio son indistinguibles de puntos esperados, reinterpretar |
| PF-P06 | Un score que prima eventos muy visibles favorecerá gobierno, liderazgos y grupos grandes. | NO_VALIDADO | Diferencias estructurales de agenda plausibles | Control de exposición y simulación de puntuación podrían neutralizar sesgo |
| PF-P07 | Gamificación altera elecciones de los usuarios y, si se conoce públicamente, quizá la atención a figuras políticas. | NO_VALIDADO | Teoría de métricas e incentivos; no evidencia de implementación | Experimento aleatorizado o serie comparada podría hallar efectos nulos |
| PF-P08 | Las redes de coalición y agenda tienen dependencia temporal no reducible a co-votación estática. | NO_VALIDADO | Relaciones políticas dinámicas observables | Modelo Markov simple igual o superior en held-out |
| PF-P09 | Recolectar alto volumen debe priorizar calidad de timestamp e identidad sobre bytes almacenados. | NORMATIVO/OPERATIVO | AB O2 y riesgos de leakage | Coste de calidad puede no compensar en algunas tareas; medir |
| PF-P10 | Un modelo de agentes calibrado reproduce escenarios fuera de muestra mejor que reglas analíticas sencillas. | NO_VALIDADO | Mecanismo plausible bajo heterogeneidad | Baseline sencillo vence ABM con datos no vistos; STOP |
| PF-P11 | El registro de votos nominales permite obtener red de afinidad descriptiva, pero no preferencias individuales causales. | MATEMÁTICO/NORMATIVO | Co-voto observable no identifica mecanismos | Ausencia de co-votos suficientes impide red robusta |
| PF-P12 | La interfaz fantasy puede aumentar comprensión de instituciones sin polarizar a usuarios. | NO_VALIDADO; hipótesis de investigación futura | Diseño pedagógico plausible | Experimento con pre/post y grupo control observa efectos nulos o adversos |

Al actualizar: conservar ID, evidencia, falsador, riesgos de selección y vínculo a commit/prueba. PF-P04 es una hipótesis de trabajo, no un hallazgo.


## Apéndice acumulativo · BR30I, 26/10/2026

Los priors PF-P01–PF-P12 anteriores siguen íntegros. Los hallazgos de campañas PF-MG, PF-H y PF-CONT se conservan en los respectivos archivos fuente: [BR30G/PRIORS_DELTA.md](BRANCH30G_20261025/PRIORS_DELTA.md), [BR20H/PRIORS_DELTA.md](BRANCH20H_20261025/PRIORS_DELTA.md) y [CONTINUACION_20261026/REPORT.md](CONTINUACION_20261026/REPORT.md). Ninguna clasificación pasada cambia por este apéndice.

La procedencia, evidencias contrarias, incertidumbres y falsadores completos de PF-I01–PF-I10 están en **[BR30I/PRIORS_DELTA.md](BRANCH30I_20261026/PRIORS_DELTA.md)**, que forma parte **del ledger acumulativo** junto a esta síntesis, no una sustitución.

| Nuevo ID | Síntesis del prior | Grado epistémico | Principal limitación/falsador |
|---|---|---|---|
| PF-I01 | 52×6=312 recuentos electorales oficiales JEC 2023 transcritos coinciden con el dataset secundario. | COMPARACIÓN DOCUMENTAL DE UNA ELECCIÓN | Verificar bytes de PDF y correcciones posteriores |
| PF-I02 | 59 opciones del CSV suman los votos a candidaturas en cada provincia. | CONSERVACIÓN AGREGADA | Las denominaciones/identidades de listas no quedan certificadas |
| PF-I03 | Cinco totales nacionales no representados coinciden con el Cuadro III JEC. | CONTRASTE DOCUMENTAL RETROSPECTIVO | Solo 5 seleccionados post hoc, no 54 restantes |
| PF-I04 | 48 de 59 opciones registran votos y cero escaños; 606.450 votos (≈2,4766%). | DESCRIPTIVO DEL ARCHIVO 2023 | No significa 48 partidos legales, ni influencia |
| PF-I05 | Páginas JEC/JEP muestran 12+4 referencias de coalición para las generales 2023. | DOCUMENTAL TERRITORIAL | No equivale a censo exhaustivo jurídico/territorial |
| PF-I06 | 10 siglas de coalición enlazan exactamente y de forma única con opción del CSV; 4 sin match exacto y 2 solo Senado. | ENLACE DE TEXTO CONSERVADOR | Match no prueba identidad legal o partidos integrantes |
| PF-I07 | 52 provincias muestran entre 8–14 opciones con votos en fuente. | DESCRIPTIVO ELECTORAL | No mide pluralismo ideológico ni trayectoria de organizaciones |
| PF-I08 | Datos finales de 2026 no prueban su disponibilidad as-of en 2023 para modelización histórica. | PRIOR DE CONTROL TEMPORAL | Conseguir snapshots independientes first_public_at |
| PF-I09 | Grafo 75 nodos/10 aristas y atlas con procedencia documental programados. | VALIDEZ DE INGENIERÍA CONDICIONADA | GitHub Actions, HTTP Python y navegador E2E aún no certificados |
| PF-I10 | Treinta ciclos AB con datos dependientes y QA no son treinta experimentos científicos independientes. | PRIOR METODOLÓGICO | Nuevas fuentes/muestras independientes podrían cambiar conclusiones |

**Evidencia acumulativa nueva:** [LEDGER A–J BR30I](BRANCH30I_20261026/LEDGER.json), [JEC/atlas contraste](BRANCH30I_20261026/RESULTS_JEC_2023_FULL.json), [prueba de 30 endpoints](BRANCH30I_20261026/RESULTS_C01_C30_POST_MERGE.json).

**Estado global de la investigación:** nuevas contribuciones N1/N2/N3=0; VSDS 1/3; CT2 multiactor 20/100 y CT2 predictiva 24/100, inalteradas; son ordinales de ramas distintas, **no probabilidades**. Mantener la discrepancia entre calidad de datos agregados corroborada y ausencia de validación histórica de personas.


## BR30J · ampliación de fuentes y trazabilidad (26/10/2026)

El bloque de 30 A–J BR30J no logró todavía capturar un padrón nacional de partidos y personas con documentos originales. Añade **ocho priors PF-J01–PF-J08** que se preservan en el ledger acumulativo, con evidencia a favor, adversa, incertidumbre, procedencia y falsador en [BRANCH30J/PRIORS_DELTA.md](BRANCH30J_20261026/PRIORS_DELTA.md). Ningún prior anterior se reemplaza.

| ID | Priorización/hipótesis | Alcance y evidencia | Contraevidencia / falsador |
|---|---|---|---|
| PF-J01 | Catálogo oficial ≠ datos oficiales capturados | Ocho superficies documentadas, cero filas oficiales nuevas | Primer original auténtico materializado con licencia/historial |
| PF-J02 | SHA256 de bytes ≠ firma/autenticación del emisor | CLI de ingesta escrita y control V8 de rechazo | Verificar procedencia mediante origen independiente y checksum |
| PF-J03 | Persona, partido, coalición, candidatura y plataforma tienen identidades diferentes | 7 figuras inventadas con relaciones tipadas y homonimia | Fallo en vínculo real documentado de organizaciones/personas |
| PF-J04 | Dos capturas del mismo evento no prueban dos eventos | As-of y revisión verificados solo en fixture V8 | Duplicación/retroactividad falsa en corpus real |
| PF-J05 | Participación pública sin escaño no mide influencia causal | Contratos sin `influence_score`; actor/evento no parlamentario ficticio | Experimento causal externo con control de intervenciones |
| PF-J06 | Cobertura nacional sin denominador real no identificable | `coverage_rate:null` en auditor | Censo de población objetivo válida y cobertura auditable |
| PF-J07 | Elecciones municipales 2023 son universo distinto de generales | 41 siglas de RTVE transcritas parcialmente, datos CC BY de votomunicipal anunciados sin descargar | Archivo municipal original y emparejamiento legal por municipio |
| PF-J08 | 30 checks V8 no son 30 experimentos de campo | 30/30 PASS sintéticos/documentales y cero personas reales nuevas | Pruebas prospectivas independientes con fuentes originales |

[Ledger BR30J con fichas A–J](BRANCH30J_20261026/LEDGER.json) · [Resultados 30/30 y runtime no verificado](BRANCH30J_20261026/RESULTS_FINAL.json) · [Informe de limitaciones y siguiente evidencia](BRANCH30J_20261026/REPORT.md).

**N1/N2/N3 nuevos 0. VSDS 1/3. CT2 multiactor 20/100 y predictiva parlamentaria 24/100 sin incremento**, ordinales y no probabilísticos. R5 de RPP/candidaturas oficiales sigue sin levantarse.


## BR20K — índice de progreso versionado (26/10/2026)

Se añade una familia **PF-K01–PF-K06** de priors de medición y gobernanza, **sin borrar ni reinterpretar los priors anteriores**. Evidencia favorable/adversa, falsadores, alcance y procedencia íntegros en [BR20K/PRIORS_DELTA.md](BRANCH20K_20261026/PRIORS_DELTA.md).

| ID | Síntesis | Límite principal |
|---|---|---|
| PF-K01 | Índice de madurez solo interpretable sobre un denominador de producto versionado | Pesos y niveles son criterios del investigador, no horas observadas |
| PF-K02 | Readiness de lanzamiento debe ser gate independiente del avance porcentual | Los 6 gates dependen de la arquitectura de V1 |
| PF-K03 | Más objetivos pueden reducir el porcentaje sin pérdida de progreso efectivo | Ejemplo V2 es hipotético, no una revisión adoptada |
| PF-K04 | URL oficial legible o SHA de archivo local no equivale a original autenticado | Falta importar RPP y cohorte histórica de personas |
| PF-K05 | Avance del trabajo no altera VSDS o CT2 por sí solo | Requiere evidencia sociológica/predictiva independiente |
| PF-K06 | Prueba Node/Python publicada no equivale a prueba ejecutada | No hay corrida nativa o navegador E2E verificada |

La [métrica V1 PFL-V1-20261026](../product/progress_snapshot_v1_20261026.json) adjudica **33,725% (33,7% visible), 9 sublíneas y 36 hitos**, con seis bloqueos de lanzamiento. No expresa tiempo o probabilidad de entrega. La prueba de ampliar municipios da **32,330%** en ejemplo hipotético, cero variación del trabajo ejecutado.

[Ledger BR20K A–J](BRANCH20K_20261026/LEDGER.json) · [Informe](BRANCH20K_20261026/REPORT.md).

**Misma situación epistémica:** VSDS 1/3, CT2 multiactor 20/100, CT2 parlamentaria 24/100; N1/N2/N3 nuevos = 0.


## BR12M — evidencia original y pruebas nativas (26/10/2026)

Los priors PF-P, PF-MG/H/I/J/K precedentes siguen intactos. Se suman PF-M01–PF-M06 con procedencia, evidencia contraria, falsadores y límites, desarrollados en [BR12M/PRIORS_DELTA.md](BRANCH12M_20261026/PRIORS_DELTA.md).

| Prior | Resultado nuevo | Alcance y límite |
|---|---|---|
| PF-M01 | Run [40258776701](https://github.com/GalexY3/Metodologia-AB/actions/runs/40258776701): 91 Node + 50 Python PASS | QA nativa, no replicación empírica social |
| PF-M02 | **PDF original BOE** recuperado con HTTPS, SHA256 **f2146cf…d2f8a**, 52×6=**312 celdas** cotejadas automáticamente y sin diferencia | Solo resultados agregados de una elección 2023; no registro RPP |
| PF-M03 | Dos JSON Congress 404, Interior XLSX falla TLS; no se desactivó autenticación | R5 de rutas específicas, no prueba de inexistencia |
| PF-M04 | Revisión 2 del mismo scope: **33,725→35,450%**; **+1,725 pp trabajo**; scope 0 | Madurez subjetiva de hitos, no tiempo restante |
| PF-M05 | Corpus de resultados electoral ≠ identidades jurídicas o actividad individual | 0 personas nacionales validadas y scoring real cerrado |
| PF-M06 | Artefacto privado expira en 3 días, SHA/URL/código quedan documentados | Custodia original a largo plazo aún no certificada |

[12 A–J BR12M](BRANCH12M_20261026/LEDGER.json) · [informe y fuentes negativas](BRANCH12M_20261026/REPORT.md) · [V2 actual](../product/progress_snapshot_v2_20261026.json). Se preserva **VSDS 1/3; CT2 multiactor 20/100 y predictiva 24/100; N1/N2/N3 científicos nuevos 0**.


## BR8N — fuente original de candidaturas, identidad conservadora y navegador (26/10/2026)

Se incorporan **PF-N01–PF-N06** a la familia acumulativa, sin borrar ni reinterpretar PF-P, PF-MG/H/I/J/K/M. Para cada uno, evidencia favorable, contraevidencia, falsador y alcance completo se conservan en [BR8N/PRIORS_DELTA.md](BRANCH8N_20261026/PRIORS_DELTA.md).

| Prior | Evidencia nueva | Límite determinante |
|---|---|---|
| PF-N01 | PDF BOE-A-2023-15066, 4.298.580 bytes, SHA256 `d1c179fc…ef0eda20`, ocho candidaturas al Congreso en Albacete | No son 8 partidos jurídicos certificados |
| PF-N02 | Cruce exacto 8/8 con resultados 2023; FO, PACMA, PUM+J y Recortes Cero con votos **nacionales** y cero escaños | No mide influencia ni votos específicos de Albacete |
| PF-N03 | Match ambiguo pasa a estado no resuelto y no se infiere militancia | JEC 78/2026 documenta límites de adscripción dentro de coaliciones |
| PF-N04 | [CI 40316425686](https://github.com/GalexY3/Metodologia-AB/actions/runs/40316425686) 3/3 jobs verdes; 98 Node, 59 Python; Chromium local | No es piloto público, navegador/dispositivo exhaustivo ni auditoría de seguridad de cuentas |
| PF-N05 | Diez barras nativas `<progress>` renderizadas con CSS externo bajo CSP restrictivo | No prueba accesibilidad formal completa |
| PF-N06 | V2 35,450 → **V3 36,350%**, +0,900pp por trabajo y 0 por alcance | Seis gates de lanzamiento y niveles científicos invariantes |

[BR8N 8 A–J](BRANCH8N_20261026/LEDGER.json) · [Informe](BRANCH8N_20261026/REPORT.md) · [Progreso V3](../product/progress_snapshot_v3_20261026.json).

**N1/N2/N3 científicos nuevos 0, VSDS 1/3, CT2 multiactor 20/100, CT2 parlamentaria 24/100.** Los tests nativos y las candidaturas históricas son resultados técnicos/documentales delimitados.
