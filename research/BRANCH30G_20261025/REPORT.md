# Politics Fantasy League — BRANCH30G, cierre de los 30 ciclos A–J

**Fecha:** 25/10/2026 · **Estado:** `COMPLETE_30_A_J` con alcance DOCUMENTAL + SOFTWARE_SINTÉTICO + OBSERVACIONAL_RETROSPECTIVO. No se declara ninguna validación confirmatoria independiente.

| Indicador | Valor |
|---|---:|
| Ciclos nuevos autorizados | 30 |
| A–J completados | **30** |
| C01, mecanismo documental del importador | 1 |
| C02, ingeniería y tests sobre fixtures inventadas | 1 |
| C03–C30, auditorías descriptivas ejecutadas sobre archivo secundario | **28** |
| Ensayos nominales contra originales oficiales independientes | **0** |
| Hallazgos 2/3 o 3/3 confirmados | **0** |
| N1 nuevos acreditados | **0** |
| VSDS proyecto antes → después | **1/3 → 1/3** |
| CT2 rama predictiva antes → después (ordinal, NO probabilidad) | **24/100 → 24/100** |
| Plazas BR30G restantes | **0** |

Este bloque es distinto de las campañas BR30E/BR30F y preserva explícitamente sus saldos históricos (12 B50, 45 libres y 19 AB20). **Treinta fichas A–J no equivalen a treinta fuentes, muestras independientes ni tests de significación confirmatorios**. Los 28 análisis secundarios posteriores son exploraciones de un solo snapshot, con hipótesis influidas por investigación anterior. Todos incluyen G=ausencia explícita de replicación externa. La fase documental y la de ingeniería no contienen demostración sociológica de campo.

## Fuente y congelación

Fuente: [Congreso Abierto](https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl), blob Git SHA1 `71918bb689c7a62cfbbdafe0b9248eac6b5c4be1`, 2.175 filas, 2023-09-19 a 2026-09-30. Es fuente secundaria producida por importador; los 350 nombres/códigos en `diputados_base.tsv` (blob `fed1b07bbc8c592bc367be45ae21ece9a8c63e02`) están vinculados por nombre exacto (importador blob `2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e`). Quién Vota declara 412 diputados históricos y 350 activos, **sin emparejamiento independiente de casos**. Las cifras del archivo no demuestran por sí solas identidad o causalidad de los no enlazados.

Prerregistro específico de los 28 contratos (antes de la ejecución de este nuevo lote): commit `2d1ad13d3523022f73577af7399afcffa44bca73`, `PREREG_C03_C30.json`. Instrumento comprometido antes de ejecutar el lote: commit `e6a72d603c6544a9e7ea24185bbb4fec155dde7b`, `scripts/br30g_audit.mjs`. Resultados brutos: `RESULTS_C03_C30.json`, commit `d776ba991d4eece671e52e860ef199b0a42c006f`. **Prerregistro posterior a exposición del mismo corpus en BR30E/F**: no dar apariencia de una preregistración confirmatoria anterior al conocimiento de las hipótesis. La auditoría adversarial queda adjunta en `AUDIT_ADVERSARIAL.md`.

## 1. Cobertura, temporalidad y medición (C03–C09)

C03, cobertura mensual: 33 meses observados, 29 con >=10 votaciones. Entre estos, mínimo 86,95% (diciembre 2023) y máximo 99,43% (junio y julio 2026), con rango 12,48 puntos. Esto no identifica cambios institucionales: el índice depende de cómo el importador enlaza nombres con el catálogo y de la composición de meses.

C04, dependencia por sesión: en 140 sesiones con al menos dos votaciones, solo 2 tuvieron coberturas nominales variables entre sus votaciones (1,43% de las sesiones). Las dos contienen los casos de nula identificación. La casi invariancia a nivel sesión es compatible con un mecanismo de catálogo nominal y genera pseudorreplicación si cada votación se trata como independiente.

C05, ponderación por posiciones frente a media simple por votación: las cifras por año coinciden al redondeo de seis decimales; la casi igualdad resulta de un número de posiciones muy próximo a 350 en casi todas las votaciones. Resultado esencialmente nulo respecto al estimando de ponderación; no implica igualdad de todos los sesgos.

C06, concentración: 218 votaciones (10% redondeado hacia arriba) representan 25,34% del total de 34.654 huecos; Gini entre votaciones de los huecos ≈0,433. Los dos casos sin nominal cuentan 700 posiciones: evaluar separadamente ese extremo.

C07–C08, heterogeneidad por categoría: la tasa de falta de enlace de votos «Sí» fue 14,82% en 2023 y 1,05% en 2026; la de «No», 13,96% y 0,66% respectivamente. La diferencia Sí−No de tasas cambia de signo entre años (2024: −1,26 puntos, 2025: +0,44 puntos). **No es un mecanismo causal de afinidad partidista**; el catálogo y la composición anual son explicaciones rivales.

C09, 2 de 2.175 votaciones sin lista nominal: `s89-v005` y `s202-v021`, con 350 posiciones cada una. No son «ausencias de diputados».

## 2. Comparación de estratos y mayorías (C10–C15)

C10: 9 tipos de votación con >=25 registros; la cobertura difiere según tipo, pero tipos y fechas están asociados. C11: rho de Spearman entre número de grupos y cobertura ≈−0,0049. C12: rho entre margen absoluto normalizado de Sí−No y cobertura ≈0,0121. **No se detecta una asociación monótona sustantiva en estos resúmenes**, con las limitaciones de una fuente y dependencia temporal.

C13: entre votaciones con margen oficial absoluto Sí−No de 0 a 5 hay 62 inversiones estrictas y 19 discrepancias con empate sobre 222 casos; de 6 a 20, 63 inversiones estrictas y 5 con empate sobre 452; con margen >20, ninguna inversión estricta entre 1.501 votos (dos sin nominal). **Los 125 cambios de dirección y los 24 que involucran empate** del C22 adversarial anterior se explican por el balance parcial de identificación. No altera resultados oficiales.

C14: si el margen en nominales identificados es `D = |S_index−N_index|` y el número de posiciones sin enlazar es `M`, la condición suficiente `D > M` hace que el signo observado no pueda cambiar bajo ninguna asignación admisible de los M. Se certificaron **1.655 de 2.173** votaciones indexadas (**76,16%**) y **cero discordancias** entre las certificadas en este archivo. Las otras 518 quedan indeterminadas por *esta cota conservadora*, pero **no significa** que 518 mayorías sean incorrectas. De ellas, 125 tienen inversión estricta frente al total disponible. Es una garantía **matemática condicionada a las definiciones**, no una nueva teoría ni validación externa.

C15: 125 inversiones estrictas distribuidas entre 37 sesiones; las cinco sesiones con más casos concentran 35,20% de ellas. La dependencia intrasesión desautoriza un análisis iid ingenuo.

## 3. Grupos y estructura institucional (C16–C22)

C16: 19.494 filas grupo-votación con >=2 votos expresados; 88,75% son unánimes según S/N/Abst, frente al 94,05% si se pondera por número de votos expresados. La diferencia ilustra dependencia del tamaño, no disciplina causal. C17: entropía media normalizada (S/N/Abst) ≈0,0528. C18: entre grupos-voto con >=10 expresados la tasa de unanimidad va de 94,53% (2023) a 96,34% (2026), sin inferir que cambie la cohesión individual por año.

C19: entre 77.495 pares de grupos con mayorías claras en una misma votación, 53,39% coinciden en la opción modal. Es una relación **ecológica**, repetida por asunto; no red causal de influencia. C20: entre 36 pares con >=20 votos en 2024 y 2025, se registran variaciones descriptivas, por ejemplo GJxCAT–GR del 74,26% al 61,65%. No controlar agenda impide adjudicar cambios de posición ideológica o coalición.

C21: al retirar *aritméticamente* el desglose de un grupo para recalcular el signo Sí−No, se registran **2.982 cambios de signo grupo-votación** distribuidos en 1.033 votaciones distintas. No constituye prueba de pivotalidad causal, poder negociador ni de influencia individual. C22: por tipo de votación, la fracción con mayoría Sí presenta grandes diferencias descriptivas; por ejemplo, 15,38% en debates de totalidad frente a 87,63% en convalidación/derogación de reales decretos-leyes. Nuevamente, es selección de agenda, no una causa identificada.

## 4. Visibilidad, semántica y predicción (C23–C28)

C23: 396 votaciones tienen campo `di` no vacío; su cobertura es 95,60% frente a 95,41% en las 1.779 restantes. `di` es una variable derivada de los nominales actuales, no medida independiente de desobediencia o disciplina: **no** debe introducirse como predictor causal.

C24: ningún registro del corpus analizado presenta `asentimiento=true`. Resultado del contraste: `NOT_IDENTIFIABLE`, no «el asentimiento no tiene efecto».

C25: 350 identificadores nominales únicos; primera aparición: 305 (2023), 27 (2024), 11 (2025), 7 (2026). Los 350 aparecen por última vez en 2026. Este patrón es coherente con que el diccionario de importación se basa en diputados actuales; **no** demuestra fecha de inicio o final de mandato.

C26: Brier de predicción retrospectiva secuencial de `Sí>No`, frecuencia acumulada con suavizado: 0,2492 frente a 0,5394 de predecir siempre Sí (baseline deliberadamente débil), en 2.156 votos sin empate. No es modelado político validado y no tiene un holdout as-of.

C27: predictor Laplace online condicionado a etiqueta de `tipo`, Brier **0,2063** frente a **0,2492** de la misma regla sin tipo, diferencia −0,0430. La etiqueta puede correlacionarse con resultados por agenda y puede no estar disponible con anticipación. El archivo fue descargado en una versión final retrospectiva; **no acredita predicción prospectiva** ni supera todavía baselines jerárquicos o políticos fuertes.

C28: predictor de cobertura de la sesión siguiente: MAE 0,004145 usando cobertura de sesión anterior vs 0,033849 usando promedio histórico de sesiones. La persistencia proviene plausiblemente de cobertura inducida por el importador y composición de sesiones, no de un pronóstico de comportamiento parlamentario.

## 5. Calidad instrumental y puerta de producto (C29–C30)

C29: campos obligatorios presentes y URLs HTTPS en las 2.175 filas; cuatro filas de grupo `?`; no IDs de votación duplicados. **Precisión adversarial:** hay dos votaciones *sin desglose por grupos* y no dos discrepancias aritméticas entre grupos existentes; **0 inconsistencias entre 2.173 votaciones con grupos**, 19.561 filas grupo-voto consistentes. Mantener el JSON bruto y esta errata verificable.

C30: 95 votaciones concilian nominal y agregado completamente; 2.173 tienen grupos completos, pero ninguna votación cuenta en esta campaña con **verificación nominal original independiente + censo de elegibilidad y adscripción a fecha + marca pública as-of**. Puerta de puntuación individual de políticos reales: **0 casos certificados**. Se autoriza análisis descriptivo de agregados del archivo con advertencias, no un fantasy político de personas puntuado como si fuera medición sociológica válida.

## 6. Contabilidad de evidencia

* 1 ciclo documental C01 (mecanismo del importador y comparación de metadatos).
* 1 ciclo de producción C02 (auditor de enlace nominal y pruebas con datos inventados).
* 28 ciclos A–J de contraste **retrospectivo/intrafuente**, sin confirmación externa. Incluyen salidas nulas/inconclusas y mediciones que son consecuencia directa del método de extracción.
* Auditoría separada (no nuevo ciclo) reproduce suma principal, descomposición de signos, condición suficiente de robustez y ausencia de discrepancias entre grupos presentes.
* No se calcula ninguna probabilidad bayesiana posterior, tamaño de efecto causal ni p-valor de 28 pruebas como si fueran independientes. CT2 permanece plana 24/100 en todos los ciclos. **N1 nuevo=0; N2=0; N3=0.**

**Reproducir:** descargar legalmente exactamente el blob original, `node scripts/run_br30g_audit.mjs /ruta/pleno.jsonl --out /ruta/RESULTS.json`; la CLI verifica SHA1 Git y rechaza otras revisiones salvo `--allow-other-blob` para estudio nuevo. Ejecutar `node --test tests/test_br30g_audit.mjs` para fixtures de QA. Esos tests no corroboran fuentes originales. La totalidad del ledger A–J está en `LEDGER.json`; primarios y negativos se mantienen versionados. `CT2_TRAJECTORY.csv` conserva 30 valores observados iguales a 24.

## AB-DECIDE y solicitud de siguiente evidencia

**CLOSE_BR30G**: 30/30 unidades A–J contabilizadas, ninguna validación oficial nominal nueva, ninguna clasificación de descubrimiento superior a la anterior. **REPAIR_SOURCE** sigue vigente para desplegar y puntuar personas reales. No se continúa explotando artificialmente el mismo fichero. La siguiente campaña debería empezar solo con originales nominales del Congreso + identidad histórica + fecha de publicación de cada atributo; a partir de esa nueva información se podrían contrastar efectos de cobertura y verdaderos modelos temporales.

**SOLICITO BRANCHING 20 CICLOS** (condicionados al acceso efectivo a datos oficiales originales y a la posibilidad de comprobar la pertenencia histórica de los sujetos; propuesta, NO autorización ni ejecución).
