# Politics Fantasy League · AB-H INCENTIVE_MECHANISMS5 · Informe final · 29 octubre 2026

**CERRADO 5/5**: tres AB-R de experimentación **exclusivamente sintética** (C01, C02, C04) y dos AB-P de ingeniería de seguridad semántica local (C03, C05). 0 inválidos finales, 0 ciclos de planificación, 0 restantes. Hubo **una primera ejecución defectuosa de C03 (14/18)** por fallo del ejecutor de test, reparada y reejecutada **dentro del mismo ciclo** (18/18), conservando su errata. Ningún estudio con participantes humanos ni datos de políticos reales. No ChatRelay, CI costosa, merge a main ni reactivación de scoring personal.

Rama `research/pfl-abh5-incentive-mechanisms-20261029` desde HEAD `a19b50b0f0576fd2a4ab0b69e24657102e75c7da` / PR #33. Este bloque tiene PR draft sucesora. [Ledger A–J](CAMPAIGN_STATUS.json) · [SOURCES y PRIORS](SOURCES_AND_PRIORS.json) · [CT2](CT2_TRAJECTORY.json) · [gráfico 0–100 y zoom](CT2_FULL_AND_ZOOM.svg).

## 1. Pregunta y prioridad académica

**Estimando mecanístico en un juego ficticio:** ¿cómo interactúan el número de oportunidades, la normalización de puntos, el incentivo a seleccionar eventos fáciles, y la pérdida de cobertura cuando se evalúan logros sintéticos en una liga? Esta pregunta puede discriminar artefactos del diseño PFL, pero su plausibilidad sociológica depende de comportamiento real, no disponible. Los agentes simulados solo obedecen reglas definidas por el propio investigador; una diferencia numérica impuesta por estas reglas NO demuestra comportamiento humano, calidad parlamentaria, valor de un partido o causalidad social.

**Prior art adversarial:**
- Witkowski et al., [AAAI 2018](https://doi.org/10.1609/aaai.v32i1.11471) y [Management Science 2023](https://doi.org/10.1287/mnsc.2022.4410): mecanismos de competición de pronósticos, incentivos a alterar informes extremos, no novedad del principio.
- Laird y Louis, [*Empirical Bayes Ranking Methods* (1989)](https://doi.org/10.3102/10769986014001029): rankings dependientes de precisión y suavizado; no novedad de Beta shrinkage.
- Hood y Piotrowska, [*Goodhart’s Law and the Gaming of UK Public Spending Numbers*](https://doi.org/10.1080/15309576.2020.1749092); Lemus y Marshall [*Dynamic Tournament Design*](https://doi.org/10.1086/711762): antecedente del gaming de indicadores y los efectos de leaderboards.

## 2. Ciclos y pruebas ejecutadas

### C01 AB-R · heterogeneidad de exposición y error de medición

[Prereg](C01_PREREG.json) congelado en `66d99e656b1b8d5a28ad6ef1a827003ba820c77c`, [motor](C01_ENGINE.js) congelado en `cfaa58a11a62a19a0472655eb24e8da255d62dea` **antes de ejecución**, [resultado](C01_RESULT.json) `851635fb131850e64b2673e697689c562512f9b5`.

A unidad: agente ficticio×ronda; 16 agentes por ronda (8 con 3 oportunidades, 8 con 12). Probabilidad `p ~ U(0.25,0.75)`, independientes del grupo; 600 rondas por cada semilla 12001 y 13999. Contrato B: recuento bruto corregido por escala /12 vs tasa observada vs suavizado Beta(2,2). C–D: mismo sorteo Bernoulli para los tres métodos, MAE frente a `p` verdadero; prueba adicional de `p=0.5` igual para todos los agentes y «ganador» definido matemáticamente con empates fraccionarios. E: MAE promedio de dos semillas **0,24239** para `success/12`, **0,16595** `success/n`, **0,10037** `(success+2)/(n+4)`. F: el recuento escalado es referencia deliberadamente sensible a exposición; comparador competente es la tasa sin suavizar, superada **en este generador y prior particular**. Un Beta diferente o otra distribución latente puede invertirlo. G: no replicación externa; H: prior sobre denominadores y precisión; I: validez matemática local, 0/3 científico; J: rama hacia incentivos selectivos, no premio.

### C02 AB-R · selección estratégica inducida por normalización

[Prereg](C02_PREREG.json) `56957b5ab74b24edaa9519ec21328091d9a86105`, [motor](C02_ENGINE.js) `95ddc4cc3ba333cef45b473b6b38f8a72ca82483`, [resultado](C02_RESULT.json) `c2261a89b73b86844848c214fb31053303001c66`.

A: dos políticas permitidas en modelo ficticio: ejecutar 20 acciones programadas frente a realizar solo cuatro fáciles. B: recompensas por sumatorio, tasa observada, suavizado Beta(2,2), tasa con denominador fijo de 20. C: 4 p=.85, 16 p=.40; estimandos analíticos y 500 mundos emparejados por semilla (22001,23999), mismas realizaciones bajo cuatro normas. D: fuente sintética / PRNG fijo. E: ventaja esperada de la política selectiva sobre participar en todas: **−6,4** puntos brutos; **+0,36** tasa observada; **+0,18333** suavizado; **−0,32** tasa de 20 oportunidades. Simulación estocástica coincide aproximadamente con la expectativa analítica; no demuestra incentivos empíricos. F: el denominador programado puede penalizar faltas de oportunidad no controladas, y el beneficio de estrategia depende enteramente de la función de utilidad impuesta. Comparador fuerte: regla Bayesian shrink no elimina cherry-picking. G: ningún ensayo con personas. H: prior de riesgo de seleccionar eventos fáciles; I: 0/3; J: seguir con instrumento seguro.

### C03 AB-P · puntuación estrictamente ficticia y ausencia de datos

[Prereg](C03_PREREG.json) `e7fe9c50a9dcd54e3daceae16f36a39489103e28`, [código de producto](../../src/politics_fantasy/synthetic_round_score.mjs) `3c8a8f210cc1475dc9f2f4d54ed341c65ac3b220`, [resultados](C03_RESULT.json). Guard puro `scoreSyntheticRound` valida prefijos `SYN-RND-` y `SYN-EVT-`, versión `synthetic-v#`, evidencia `synthetic-fixture:...`, vector completo de acciones con intento y éxito, niega campos de personas y partidos, rechaza duplicados e inconsistencias. Si no se verifica cobertura devuelve `COVERAGE_UNKNOWN` con `scores=null`; si la agenda está realmente vacía devuelve `VERIFIED_NO_OPPORTUNITIES` con `scores=null`; no interpreta ambos como cero documentado. Caso de 0 éxitos con intentos completos sí produce cero de éxitos.

E: **18/18 verificaciones V8 PASS al reparar el ejecutor**, inspección de identidad de texto exacta frente al archivo guardado. **Errata](C03_ERRATA_AND_REPAIR.json)**: la primera prueba fue 14/18 porque el entorno V8 no ofrece `structuredClone`; se reejecutaron mismas 18 con copia JSON, sin modificar motor, y se conserva historia. F: QA de una función, no de un servidor ni sistema de identidad. G: no CI, Node nativo ni navegador. H: guard sintético. I: AB-P acotado, cero subida científica o gate. J: aceptación local del producto.

### C04 AB-R · pérdida dependiente del resultado y coste de abstención

[Prereg](C04_PREREG.json) `88947ac55dcb979f7ffac79067e9086d152485a6`, [motor](C04_ENGINE.js) `37f77293a96d784060d922215687ed17b4dec172`, [resultado](C04_RESULT.json) `04398f40e1e047ff80f36ce6eb49c63d65858cb7`.

A unidad: 10 éxitos/no éxitos Bernoulli(`p=.6`) generados en juego ficticio; estimando diferencia entre tasa observada y tasa completa. B: pérdida MCAR 10% vs MNAR éxito 40% / fracaso 5%, frente a oracle completo y rechazo del score si hay incompletitud. C: 600 mundos × dos semillas 42001 y 43999, con mecanismos de pérdida generados para las mismas muestras; sin selección posterior. E: promedio de medias por semilla: sesgo `observado-oracle` MCAR **−0,00056**, MNAR **−0,11437**; MAE **0,03846** vs **0,11859**; disponibilidad del guard solo **32,83%** y **5,83%** de mundos completos. F: la fuente de sesgo MNAR está programada, no descubierta. La política «no puntuar si faltan datos» no rellena eventos y tiene un coste grande de disponibilidad. G: no prueba sobre fuente institucional o jugadores. H: riesgo de declarar cero / selección de cobertura; I: 0/3; J: trasladar a manifest.

### C05 AB-P · integridad referencial de puntuación ficticia

[Prereg](C05_PREREG.json) `601c30f87cbca4a3c7f4eaab253ce8aeb31225cf`, [módulo](../../src/politics_fantasy/synthetic_round_manifest.mjs) `b226f9d56ee5d4a9c89b87c173dbd934edc2296d`, [resultado](C05_RESULT.json) `cc00ae5ffb75b48f4921bdd71cf52c6759c621b7`.

B: manifest sin controles vs manifiesto canónico que protege reproducción. C: 10+ afirmaciones adversariales predeclaradas; resultado **18/18 V8 PASS**, entre ellas repetición idempotente, detección de cambio de regla, fecha/línea no usada, evidencia distinta bajo mismo id, objeto mutado, campos de persona/partido, ausencia de cobertura. D: serialización JSON explícita y cadena `canonical_payload`; **no es hash criptográfico ni firma digital**. F: un atacante que reescriba manifest y almacenamiento no queda detenido; aún no hay transacciones de base de datos ni autenticación, se requiere revisión de seguridad. G: sin despliegue ni usuario. H: metadatos de fuente y conflictos con versión previa. I: AB-P acotado 0/3 científico; J: detener con R5 nuevas iteraciones únicamente sintéticas.

## 3. Dictamen y límites

Los cinco ciclos aportan **evidencia local formal**, no comportamiento observado. Se han contrastado escenarios de oportunidad, utilidad optimizada por políticas, errores de normalización y missingness condicional, además de probar dos utilidades de software. Todos sus mecanismos son consecuencias de los supuestos y reglas programados. No hay un nuevo fenómeno social independiente de la simulación, diseño humano aleatorizado, correlación de política real, validación de ranking, ni hallazgo 1/3 distinto del prior art. No usar resultados sintéticos para evaluar políticos, partidos, ideologías o personas.

El score CT2 de la **línea paterna PFL identidad** permanece **29/100**. La línea filial específica de mecanismos sintéticos tiene **CT2 20/100**, juicio ordinal **provisional de baja confianza** por la falta de datos de participantes, fuerte antecedente y retos de implementación; no constituye descenso de 29 a 20 ni probabilidad. VSDS **1/3**; V4 contractual **36,90%**, 2/90 logros, 0/6 gates, N1/N2/N3 **0/0/0**. No hay incremento de madurez contractual por dos utilidades aisladas aún sin integración y test nativo.

## 4. R1–R5 y auditoría adversarial

**R1:** los agentes son ficticios, el «éxito» Bernoulli no es calidad democrática ni productividad; el denominador agenda es una convención. **R2:** controles incluyen tasa observada, suavizado Beta y regla programada, comparadas con idénticos draws y oráculo de p; ninguna recibe datos extras. **R3:** cinco ciclos relacionados y diseño/semillas fijados antes de ejecutar; sus réplicas simuladas NO son muestras sociales independientes. **R4:** selección adversarial de casos (n corto, cherry pick, missingness MNAR), explicitación de coste de abstención, error del harness C03 con historia preservada; sin test externo. **R5:** detener nuevas simulaciones similares hasta acceder a conductas de jugadores o a una intervención propia prospectiva.

## 5. Próxima evidencia necesaria y tareas de Codex

Para descubrir un mecanismo de sociología del juego aplicable a PFL hace falta un experimento ético con personas participantes voluntarias usando **solo figuras y asuntos ficticios**, asignación aleatoria a reglas de recompensa y cuadros de clasificación, resultados de elección/participación/comprensión registrados con timestamp y consentimiento, baseline estadístico competente, tamaño muestral planificado y prereg anterior a exposición. No entrenar algoritmos sobre datos ajenos sin licencia, ni asignar puntuaciones a personas políticas reales. Alternativa: corpus independiente legalmente reutilizable con histórico de reglas y respuestas fechadas. Un plan sin participantes no debe contarse como descubrimiento.

**Pendiente de Codex / PC:** ejecutar Node en los dos nuevos módulos, suites focalizadas e integrales en checkout limpio y auditoría de seguridad de consumidores; registrar receipt y SHA exactos. T011 y T016–T024 anteriores siguen pendientes de sus verificaciones; **no se afirma su ejecución**.

**SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, con autorización nueva independiente, dirigidos a instrumentar un ensayo prospectivo ético (producto AB-P + investigación AB-R posterior si existen respuestas reales) y a evitar más variantes sintéticas sin discriminación; no comenzar sin concesión explícita.
