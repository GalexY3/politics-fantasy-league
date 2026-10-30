# Politics Fantasy League — puerta de evidencia independiente y derechos de datos (29/10/2026)

**Estado de esta continuación: verificación de fuentes originales y preregistro CONDICIONAL; NO es un ciclo científico A–J ejecutado. STOP_R5 preserva las 2 plazas AB-H históricas.** Rama sucesora de [PR #42](https://github.com/GalexY3/Metodologia-AB/pull/42), HEAD original `3d3a1eda1dc51f74bc9cdef50afacc4d27f6e8a5`; no merges a main.

## 0. Método aplicado, permisos y límites

Se leyeron directamente en GitHub `AGENTS.md`, AB 3.2.1 y anexos O1–O7, incluyendo source-of-truth GitHub (O1), freeze/portabilidad (O2), DRIFT, CT2, gates y la separación AB-R/AB-P/AB-H del O7. Las dos verificaciones técnicas P0 de T028 **ya estaban completas** en PR42 y no se repitieron: [Python Atlas original](https://github.com/GalexY3/Metodologia-AB/actions/runs/40805714464) 80 lotes/63 nodos/81 relaciones, SHA-256 canónico `e41270a7897817f626611208f4ec483318950af59d8d27f78c925d83a93eb54f`; [Chrome Playwright real HTTP](https://github.com/GalexY3/Metodologia-AB/actions/runs/40806035386) 21/21 de piloto ficticio. Esto no altera 0/6 gates generales de producto.

**Instrumento de esta continuación:** una serie de siete consultas HTTPS **de una sola tarea y duración máxima 2–3 min cada una**, ejecutadas en un checkout privado GitHub autorizado con Python estándar. Se limitaron a obtener licencias, manuales, metadatos DDI y **un fichero de preguntas sin registros personales**. Los SHA-256 provienen de **bytes originales efectivamente leídos**, no de nombres, hashes Git o valores inferidos. Las pruebas fallidas del parser ISO y los accesos externos denegados se conservaron; no se descargaron pronósticos individuales, identificadores reales ni respuestas personales.

## 1. GJP original: permiso de reutilización documental confirmado

El archivo original **Good Judgment Project Data**, Harvard Dataverse [DOI 10.7910/DVN/BPCDH5](https://doi.org/10.7910/DVN/BPCDH5), identificador 2917327, versión 1.0, respondió por la API oficial con licencia específica **CC0 1.0**, `termsOfUse=null` y **25 archivos sin marca de restricción**. [Prerregistro](PREREG_SOURCE_GATE.json), [ejecución](https://github.com/GalexY3/Metodologia-AB/actions/runs/40807901958), [inventario y licencia JSON](GJP_DATASET_METADATA_RESULT.json). **CC0 es una autorización de derechos de autor, no una exención automática de evaluación de privacidad/ética para microdatos seudonimizados**; no se han inspeccionado filas personales.

Cuatro ficheros **originales** obtenidos exclusivamente para documentación o características de las preguntas:

| Fichero | Bytes reales | SHA-256 completo |
|---|---:|---|
| `all_individual_differences.README.md` (id 2917333) | 71.883 | `e9f137862188efa9d6d40cf904849cf99fe21a91e3fd440ee6ad8f04a73959ff` |
| `readme.txt` de mercados (id 2917338) | 5.804 | `7f66c343e910ca1a2b7262f708a3e73f275e8f3e283072428001a25292214737` |
| `readme.txt` de variables (id 2917350) | 4.382 | `adfc00ea8255a14542a6a2128e67b9902d182d7ec53b701d1343c9a6eb61c2b1` |
| `ifps.csv` de preguntas (id 2917330) | 1.072.153 | `1f64e5483741e656ddc667b310799e9aec8a8c5dbb7e12f9af5c5a60fd146286` |

Fuente reproducible: [trabajo GitHub 40808128321](https://github.com/GalexY3/Metodologia-AB/actions/runs/40808128321) y [hashes](GJP_DOCUMENTATION_HASHES_RESULT.json). El `ifps.csv` está formado por **617 registros, 14 columnas, 617 identificadores IFP distintos**. No se ha descargado `survey_fcasts.yr1.tab` (29,45 MB), `survey_fcasts.yr4.tab` (165,7 MB), ni `all_individual_differences.tab` (41,9 MB), por tratarse de filas de participantes.

## 2. Variables observables y distinción entre condiciones y exposición real

El manual de variables especifica `ctt` = condición asignada: `1a/1b/1c` participantes individuales, `2a/2b/2c` participantes que **podían ver información agregada de la multitud** (a/b/c denotan modalidades de entrenamiento) en el año 1. Documenta `fcast_type=0` primera respuesta, `1` actualización, `2` afirmación, `4` retirada. **Mellers y colaboradores 2014** describen la asignación aleatoria del año 1 a un diseño de entrenamiento × interacción social. No se ha inspeccionado el padrón original de asignados ni su implementación.

[DDI oficial](https://github.com/GalexY3/Metodologia-AB/actions/runs/40808323354): `survey_fcasts.yr1.tab` id2917351 declara **308.232 observaciones y 16 columnas**: `ifp_id,ctt,cond,training,team,user_id,forecast_id,fcast_type,answer_option,value,fcast_date,expertise,q_status,viewtime,year,timestamp`. DDI original SHA256 `519bf2701bf994c63ec267cd45e2c4ee89b0d8984f258403ac2c9ee58f67e063`. En año 2 el DDI declara 435.624 observaciones, y año 4 1.685.784 (sin datos leídos). DDI para dos `pm_transactions` respondió HTTP 400: disponibilidad desconocida, no ausencia verificada.

Una lectura adicional **prerregistrada** de la etiqueta DDI `viewtime` confirma **solo** nombre de campo, tipo numérico y huella UNF: **no define una impresión de pantalla previa a responder**, ni aporta registro de quienes no contestaron. [Control semántico](https://github.com/GalexY3/Metodologia-AB/actions/runs/40808668080), [recibo](GJP_VIEWTIME_SEMANTIC_RESULT.json). Por tanto **no está identificado `E_{itq}`** como oportunidad mostrada a una persona antes de responder. **Acceso potencial a información de la multitud tampoco es exposición a leaderboard de posiciones.**

## 3. Calidad del calendario IFP: negativa de parser preservada y reparación

[Prerregistro original](PREREG_IFP_QUALITY.json), [primer ensayo](https://github.com/GalexY3/Metodologia-AB/actions/runs/40808853715) y sus números no se modificaron retroactivamente: el parser asumió fechas ISO y obtuvo **0 fechas parseables**. Tras [prerregistro de la reparación](IFP_DATE_PARSE_REPAIR_PREREG.json), [exploración de formatos](https://github.com/GalexY3/Metodologia-AB/actions/runs/40809018691) confirmó `%m/%d/%y` para fechas de apertura, fecha límite y cierre efectivo, y `%m/%d/%y %H:%M` para suspensión; `NA`/`NULL` significan ausencia.

El [control de cronología reparado](https://github.com/GalexY3/Metodologia-AB/actions/runs/40809208653), tras [prerregistro específico](IFP_CHRONOLOGY_REPAIR_PREREG.json), obtuvo: 617 fechas de apertura y 617 plazos previstos válidos, 582 fechas de suspensión, 498 fechas de cierre efectivo (498 IFP `closed`, 119 `voided`); mediana ventana nominal **102 días**. Detectó **1 apertura posterior al plazo previsto**, **1 apertura posterior a suspensión**, **0 aperturas posteriores al cierre efectivo** y **273 suspensiones posteriores a cierre efectivo**. Estas últimas **no son automáticamente 273 errores**: la semántica entre suspensión nominal, fechas efectivas y cierre retroactivo necesita verificarse. La inferencia de elegibilidad debe incorporar esas incertidumbres y un criterio de exclusión/sensibilidad previamente fijado. [Recibo numérico](GJP_IFP_QUALITY_RESULT.json).

## 4. Auditoría adversarial de replicaciones Hudja y Lemus–Marshall

[Consulta únicamente de páginas oficiales](https://github.com/GalexY3/Metodologia-AB/actions/runs/40808491685), [registro](EXTERNAL_REPLICATION_GATE.json):
- **Hudja, Roberson y Rosokha (2025):** página del investigador HTTP 200, 74 enlaces examinados. Menciona software experimental en GitHub; no fue posible identificar allí un **paquete de microdatos con licencia específica**, asignación, exposición y resultados. El trabajo publicado analiza concursos de muestreo secuencial y muestra que un leaderboard puede **reducir** esfuerzo/calidad según horizonte y costes.
- **Lemus y Marshall (2021):** página académica del autor HTTP 200 y manuscrito `https://g-marshall.github.io/kaggle1.pdf`, pero ningún archivo verificable de datos de participantes con licencia. La página editorial del *Journal of Political Economy* declara «Data Archive» pero respondió **HTTP 403** al acceso programático legítimo. La investigación combina modelo dinámico con datos observacionales y ensayos estudiantiles y encuentra mejora media de resultados bajo sus condiciones. No hay derechos ni bytes autorizados de replicación verificados. No se eludieron 403 ni accesos.
- Publicación general / fuente de datos: Merkle et al. 2015/2017 y Bo et al. 2017 abordan dificultad, tiempo de previsión, elección selectiva de preguntas e IRT; ForecastBench publica ajuste por dificultad. La [FAQ oficial de GJ Open](https://www.gjopen.com/faq) ya aplica Brier relativo frente a la multitud ponderado por días de participación activa, sin penalización directa por preguntas no respondidas: **la mera ponderación por participación tampoco es novedosa**. No atribuir esas reglas actuales a la plataforma histórica GJP 2011–2015.

## 5. Hipótesis nueva *condicional*, registrada antes de cualquier microdato (NO ejecutada)

[Prerregistro condicional GJP 3×4](GJP_YEAR1_CONDITIONAL_PREREG.json): probar en la población de **todas las personas realmente asignadas aleatoriamente**, incluidas las que no respondieron, el **efecto ITT del acceso a información agregada de la multitud** (grupo `ctt` 2a–2c frente a 1a–1c), estratificado por entrenamiento, sobre la **probabilidad de realizar una primera previsión dentro del intervalo elegible de cada IFP**. Separar de la precisión condicional al pronosticar, que sufre selección postratamiento. Control fuerte: resultados de Mellers 2014, IRT y MNAR, feedback dinámico de Hudja/Lemus, dificultad ForecastBench y reglas de scoring preexistentes. Incluir contrastes negativos, inferencia por asignación a participante y correlación por pregunta, cambios temporales y atrición; congelar antes de cálculo.

**Bloqueos que impiden abrir un ciclo AB-R válido:** padrón íntegro de personas asignadas incluyendo no respondientes y fecha de registro **no verificado**; elegibilidad individual en cada IFP no verificada; `viewtime` no ofrece bitácora independiente de visualización; acceso y tratamiento de microdatos humanos necesitan protección jurídica/ética incluso con CC0; el efecto de crowd information y otros resultados pueden haber sido estudiados ya, por lo que falta discriminación científica original. La condición `ctt` **no equivale a ranking/leaderboard**. Se ha preregistrado una pregunta, **no realizado un experimento ni estimado un efecto**.

## 6. A–J y R5 del trabajo actual

A pregunta: fuentes independientes capaces de identificar oportunidades individuales pre-respuesta y aleatorización de feedback. B rivales: artefacto de selección/IRT/dificultad, efecto genuino crowd info y efecto genuino leaderboard distinto. C predicciones discriminantes y fallos preregistrados por cada paso; D reglas/permiso por fuente congeladas antes de recuperar; E ejecución real de **controles documentales y de calidad**, no A–J causal; F contra-controles: no confundir diseño asignado con vista efectiva ni cuestionario abierto con oportunidad personal; G no hay replicación independiente de resultado PFL; H priors actualizados con derechos/variables, fallos cronológicos y antecedentes; I **0/3 novedades sustantivas**; J **STOP_R5 del experimento humano**, sin consumir dos plazas previas.

| Indicador | Antes | Después |
|---|---:|---:|
| CT2 prospectiva ordinal | 22/100 | **22/100** |
| N1/N2/N3 nuevos | 0/0/0 | **0/0/0** |
| Plazas AB-H históricas pendientes | 2 | **2** |
| Puertas generales de lanzamiento | 0/6 | **0/6** |
| Ficheros documentales originales con SHA256 validado | 0 de GJP | **4** |
| Instrumentación de tratamiento leaderboard con exposición individual | sin validar | **sin validar** |
| T028 core Atlas + navegador | superado PR42 | **no repetido** |

La línea científica ha mejorado en **factibilidad documental**, pero no en evidencia causal original; no subir CT2 por más fuentes o métricas técnicas. Debe mantenerse R5 hasta poder verificar padrón/tiempos/exposición y aprobación para análisis humano. No puntuar políticos reales ni importar datasets humanos al repo. **No se ha usado ChatRelay, no se ha fusionado main ni ejecutado suites CI costosas**. La investigación futura no debería repetir T028 ni los siete controles de metadatos ya realizados; centrarse en la disponibilidad de un registro legal de elegibilidad/visualización o un diseño alternativo con fuente independiente y novedad explícita.
