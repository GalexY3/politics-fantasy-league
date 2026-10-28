# Politics Fantasy League — PETITIONCOHORT5 · 28/10/2026

**CIERRE: 5/5 ciclos AB-H A–J válidos acotados realmente ejecutados; 0 inválidos, 0 planificación, un contraste adicional NO CONTADO, 0 autorizaciones pendientes.** Rama `research/pfl-abh5-petition-cohort-20261028` desde PETITIONS5 / PR #29, base exacta `07820cf20c115881d02e79141b153e3d3eea13f1`. Se han ejecutado C01, C02, C03, C05 y C06; **C04 NO se cuenta**, porque la comparación estadística sobre peticiones con 100.000 firmas había fijado mínimo n=3 y solo hay **n=2**. No ChatRelay, ni merge main, ni CI costosa, ni scoring de personas, partidos o peticionarios.

## 1. Población, prerregistros y jerarquía de evidencia

**Hipótesis sociológica:** una muestra de peticiones **seleccionadas por identificador administrativo**, y no por apoyos finales, revela un universo diferente del top12 muy firmado del bloque anterior y permite detectar cómo los **umbrales institucionales y reglas de exposición** condicionan lo que podemos medir, sin derivar causalidad ni estimar conducta individual.

**Prerregistro inicial (C01):** los **40 IDs consecutivos 700120..700159** fueron congelados antes de abrir sus resultados. La API primaria `https://petition.parliament.uk/petitions/{id}.json` fue inaccesible para casi todas las IDs desde aquí. Descubrimiento documental no seleccionado por firmas: [`Jonty/uk_petitions_data`](https://github.com/Jonty/uk_petitions_data), archivo público de copias JSON del servicio UK Petitions, con blobs Git verificables. De los 40 IDs iniciales, hay **9 archivos**, con 31 sin archivo; **700143** ya había sido consultado en PETITIONS5 y consta como pre-expuesto. No se alcanzó el mínimo inicial de 20 casos, y C01 registra **H1 negativa**: [C01 resultado](C01_RESULT.json), [prereg](C01_PREREG.json), [primer panel](ARCHIVE_COHORT40_PANEL.json).

**Una única ampliación R5**: se registró en Git **ANTES de consultar los nuevos resultados** [`C02_C05_AMENDMENT_BEFORE_EXPANSION.json`](C02_C05_AMENDMENT_BEFORE_EXPANSION.json), fijando **140 IDs consecutivos adicionales 700160..700299**, sin selección por popularidad. Se leyeron **57 archivos** de las 140 IDs, conservados en [parte 1](ARCHIVE_140_PART1.json), [parte 2](ARCHIVE_140_PART2.json), [parte 3](ARCHIVE_140_PART3.json), [parte 4](ARCHIVE_140_PART4.json). **180 IDs preseleccionadas en total, 66 copias disponibles y 114 IDs sin copia archivada**. Ausencia de archivo NO prueba que no existiera petición, que tuviera cero firmas ni que fuese rechazada. Esta expansión es **adaptativa exploratoria**, NO confirmación ciega de la cohorte original.

**Jerarquía de procedencia**: el archivo GitHub es un **tercero**, NO el servidor original. Los SHA de blobs verifican las copias del archivo y la estructura JSON, **NO autentican descarga ni estado de la API oficial**, `first_public_at`, TLS, firma digital ni snapshot inmutable. Un segundo servicio oficial **Hansard** solo corroboró un debate del nuevo caso 700138 en C06. [SOURCES_AND_PRIORS.json](SOURCES_AND_PRIORS.json) actualiza todas las fuentes, priors y límites.

**Datos agregados sin identidades de peticionarios**: [COHORT180_METRICS.json](COHORT180_METRICS.json) conserva 66 registros de atributos administrativos, recuentos, hitos y blobs por ID; no nombres, textos de petición ni firmas individuales. En el conjunto archivado hay **46 cerradas** y **20 rechazadas**, todas las copiadas como públicas; ninguna abierta. No es universo de todas las peticiones emitidas, y no es muestra aleatoria de ciudadanos.

## 2. Resultados A–J de los cinco ciclos contados

| Ciclo | Contrato, dato y contraste, con límites |
|---|---|
| [C01](C01_RESULT.json), [pre](C01_PREREG.json) | **Control negativo de acceso y cobertura:** n=9 de 40 IDs congeladas (31 sin copia), no se cumple umbral predefinido n≥20 para comparaciones en la banda inicial; se preserva la falencia en lugar de fabricar ceros. Cambio hacia archivo de terceros como fuente distinta del original y una sola ampliación congelada de rango para los siguientes ciclos. **Fuente original: cero bytes autenticados**. |
| [C02](C02_RESULT.json), [pre](C02_PREREG.json), [enmienda](C02_C05_AMENDMENT_BEFORE_EXPANSION.json) | **Cobertura institucional por umbral, n=66 copias:** bajo 10.000 firmas **53**, con respuesta documentada **0**; al menos 10.000 **13**, con respuesta **13**. De esos 13, **2** superan 100.000. No se han inventado datos para otras 114 IDs. Para los 13 que superaron 10k, mediana entre fecha de umbral y `government_response_at`: **15,560 días**, rango **12,306–38,799 días**, solo **1/13** >30 días. Es la consecuencia administrativa observada de una regla conocida, no un efecto causal de firmar. |
| [C03](C03_RESULT.json), [pre](C03_PREREG.json) | **Contraste temporal de exposición, n=46 cerradas con fechas:** mediana apertura→cierre **181,335 días**, mínimo **181,164**, máximo **182,545**: duración casi fija de seis meses. Spearman duración frente a log1p(firmas) **+0,1045**. El supuesto de que variaciones de exposición explican desigualdad de apoyos **no queda sustentado** por un intervalo prácticamente constante; 20 rechazadas no tienen la misma duración de publicación y se excluyen del cálculo de exposición. |
| [C05](C05_RESULT.json), [pre](C05_PREREG.json) | **Comparadores fuertes, LOOCV por ID, clasificación retrospectiva de presencia de respuesta:** baseline prevalencia de entrenamiento Brier **0,16308**; regla legal `firmas finales ≥10k` Brier **0**; regresión logística ridge de log(1+firmas) Brier **0,05512**. n=66 (13 con respuesta y 53 sin respuesta). La regla conocida no es nuevo conocimiento ni pronóstico: las firmas son **FINALMENTE observadas** y pueden ser posteriores al evento a predecir. Dos discrepancias entre fecha pública y fecha técnica de respuesta (700189, 700262) exigen control de versión. [Métricas](C05_BASELINE_RESULTS.json). |
| [C06](C06_RESULT.json), [pre](C06_PREREG.json) | **Corroboración documental cruzada:** nueva petición del panel **700138** tiene en archivo fecha de debate **10/02/2025**. El [debate Hansard original](https://hansard.parliament.uk/Commons/2025-02-10/debates/94821BE4-8215-4D8D-93E1-77F786B3ABD4/InheritanceTaxReliefFarms) se abrió y explícitamente identifica la **e-petition 700138** y fecha. La URL primaria `petition.parliament.uk/petitions/700138.json` dio error de lectura, por lo que **no se autentica su JSON original**. Además, la petición **700143** (ya conocida del bloque anterior) tiene **3.084.712 firmas en archivo** frente a **3.084.713 en una captura anterior de la API oficial**; diferencia **1** sin historia de correcciones atestada, no inferir causa. Un solo documento Hansard no prueba un mecanismo causal ni que una petición lograse su objetivo. |

**No contabilizado:** [C04_NOT_COUNTED.json](C04_NOT_COUNTED.json), prerregistro [C04](C04_PREREG.json): la hipótesis sobre proporción de debates completados entre expedientes con ≥100.000 firmas requería **al menos tres casos** y solo hay **dos (700138 y 700143, uno pre-expuesto)**. No se ejecuta prueba inferencial ni se inventan intervalos. Tampoco es un segundo ciclo válido por leer sus metadatos en C02. El presupuesto de cinco plazas se cierra con C06 genuinamente prerregistrado antes de consultar la nueva transcripción Hansard. Cuenta **5 válidos, 0 inválidos, 0 planificación, 1 intento/no identificable sin contar**.

## 3. Auditoría adversarial R1–R5 y límites

**R1 (estimando)**: expediente/registro de petición, no firmante único, no postura ideológica, éxito político o calidad de gobierno. Resultado de interés = presencia de respuesta documentada, fechas y tiempos institucionales. Una persona puede firmar múltiples peticiones: firmas sumadas no equivalen a población firmante única.

**R2 (controles)**: baseline administrativo publicado de umbral 10k frente a prevalencia y logística penalizada con mismo recuento final; comparador simple supera o iguala al modelo más complejo. Se distingue 100k elegibilidad de consideración para debate de un resultado completado, y sin cobertura suficiente no se estima su tasa.

**R3 (selección)**: IDs consecutivas dan un criterio más defendible que **elegir las más populares**, pero solo **66/180** tienen copia en el archivo, que tiene sus propias reglas de publicación, rechazo, revisión y archivado. Extensión adaptativa tras 9/40 documentada y congelada ANTES de los nuevos archivos; primera petición 700143 pre-expuesta; todos los análisis de datos finales son retrospectivos. No usar p-valores como prueba confirmatoria de un contraste causal.

**R4 (ablaciones/falsadores)**: primera hipótesis de suficiente cobertura 20/40 rechazada; duración de observación casi fija elimina variación útil; no support estadístico para inferir regla universal de 100k (n2); complejidad logística no aporta frente a regla administrativa, pero esta es retrospectiva tautológica. Diferencia de un apoyo entre versiones para id 700143 y fecha discordante en dos archivos archivados: **no corregir silenciosamente**.

**R5 (evidencia cuello de botella)**: solo **una expansión** administrativa 140 IDs antes de consultar resultados, luego STOP. Siguiente avance discriminante exige **descarga primaria original en PC/Work**, clarificar las 114 IDs sin copia, estados rechazados y snapshot **antes** del outcome, y prueba de un cohort prospectivo auténtico. No simular más resultados sobre estos mismos 66 registros.

## 4. CT2 y progreso, sin inflación

| Indicador | Antes | Después |
|---|---:|---:|
| Ciclos autorizados/realizados | 5/0 | **5/5** |
| AB-R / AB-P | — | **5/0** |
| Inválidos / planificación / no contabilizados | — | **0 / 0 / 1** |
| CT2 científico identidad | 29/100 | **29/100** |
| V4 contractual | 36,90% | **36,90%** |
| VSDS | 1/3 | **1/3** |
| Logros acreditados | 2/90 | **2/90** |
| Gates de lanzamiento | 0/6 | **0/6** |
| Nuevos N1/N2/N3 | 0/0/0 | **0/0/0** |

[Ledger y commits A–J](CAMPAIGN_STATUS.json) · [Trayectoria CT2 por ciclo](CT2_TRAJECTORY.json) · [CT2 0–100 + zoom 27–31](CT2_FULL_AND_ZOOM.svg). C04 **NO** tiene punto en la trayectoria, porque no fue ejecutado.

**No hay nuevo hallazgo científico 2/3**: una regla administrativa conocida y una medición descriptiva de archivos no reproducen una nueva hipótesis científica específica de identidad PFL, ni prueban capacidad prospectiva o causal. No subir CT2 por número de ciclos.

## 5. Pendientes técnicos y propuesta

[**T023 · autenticar 180 originales, conciliación e inferencia temporal correcta**](../../tareas_codex/T023_PETITIONS_IDCOHORT_ORIGINALES_20261028.md) está **PREPARADA Y NO EJECUTADA**: descargar JSON auténticos, SHA-256 oficiales, distinguir 114 IDs sin copia, validar dos discrepancias de fecha, una firma de diferencia y ejecutar suite Python/Node/Atlas en checkout limpio. Permanecen **T011, T016, T017, T018, T019, T020, T021 y T022**, todas pendientes y **no ejecutadas** por este bloque. No se ejecutó suite integral ni se obtuvo un snapshot original autenticado. No ChatRelay ni merge main.

**SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, sujeto a autorización nueva y preferentemente a la obtención de una cohorte de originales autenticados con variables observables antes del outcome; alternativamente elegir otra fuente institucional verdaderamente independiente. **No se inicia otra campaña automáticamente.**

