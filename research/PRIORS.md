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
