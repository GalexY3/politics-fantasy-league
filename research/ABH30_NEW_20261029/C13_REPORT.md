# PFL · ABH30-C13 — Límites de identificación bajo pérdidas de resultados en piloto ficticio

**29/10/2026 · AB-H técnico-matemático, DRIFT D2.** Nuevo módulo [`fictional_missingness_bounds.mjs`](../../src/politics_fantasy/fictional_missingness_bounds.mjs). Es una intervención de producto **AB-P**, no ensayo humano AB-R ni descubrimiento original de resultados empíricos. Se deriva de la amenaza de selección de 945→891 trabajadores descrita en el estudio externo del ciclo C12 y del código PFL preexistente `pilot_analysis_dryrun.mjs`, que advertía `COMPLETE_CASE_NOT_ITT` sin cuantificar el conjunto de efectos compatibles con pérdidas.

## Hallazgo técnico y resultado adversarial

Bajo el único supuesto de que cada resultado final de la futura prueba ficticia se normaliza en **[0,1]**, para brazo `a`, `N_a` asignados, `n_a` observados y `S_a` suma de resultados observados:

\[
\mu_a\in\left[\frac{S_a}{N_a},\frac{S_a+N_a-n_a}{N_a}\right].
\]

Se implementan los extremos de combinaciones lineales por sus signos para tres contrastes de diseño 2×2 de los **cuatro brazos ficticios ya existentes** (`control`, `transparency`, `leaderboard`, `both`): efecto principal de transparencia, efecto principal de clasificación y su interacción. Los extremos son **sharp bajo los supuestos declarados de valores omitidos libres en [0,1]**, sin MAR, imputación ni normalidad; **no constituyen un intervalo de confianza**. No se deduce que los participantes reales hayan sido asignados correctamente o recibido los estímulos.

Ejemplo adversarial **íntegramente ficticio**, reproducido en el Node real después del freeze: cada brazo tiene diez «asignaciones» sintéticas. Control, transparencia y ambos tienen diez resultados y suma 6 (media 0,6). En `leaderboard`, hay cuatro observados, suma 3,8 y **seis ausentes**. Su media de *complete cases* sería 0,95, frente a control 0,60. El contraste factorial «leaderboard», calculado ingenuamente con las medias observadas, resulta **+0,175**; el intervalo identificado con todas las omisiones permitidas es **[−0,11; +0,19]**. El signo **no está identificado**. Para interacción, intervalo **[−0,38; +0,22]**. Una puntuación elevada entre quienes completan **no autoriza** declarar ventaja ITT del juego.

## Freeze, ejecución y límites

Código original propio congelado antes de outcomes: blob Git `93f18028fba28e9a4ee2b71183ca5a9a6825fde6` y SHA-256 `fec140b8f467be3c8514661ba697b669cb0a43342864e8ddf13122004df5c584`. Batería de **18 tests** blob `eedf1b826914ffae4634216107fa090be0d3910c`, SHA-256 `6cd78e9fe28215570688197e19135370db874f9f17009a1a9cd7873adcf2d3ad`. Ambos se subieron antes del [contrato A–J](C13_PREREG_AJ_SHA.json), commit **`5c2b06558f7f497a4d21954467f48d95310247d7`**. Después de él se comprobó paridad SHA de archivos locales, y **Node.js v22.16.0 `node --test tests/test_fictional_missingness_bounds.mjs`: 18/18 PASS, 0 FAIL, exit code 0**. Archivo TAP local con SHA-256 `79c6901be66bc47e324ccb032ae0d6f93965cd1ea57d6f714c37b35d8ccada96`. [Recibo C13](C13_RUN_RECEIPT.json). No hay ejecuciones fallidas ni reparaciones posteriores.

## A–J

**A — Estimando:** media normalizada [0,1] por brazo y tres contrastes lineales en un marco de asignados/observados. Los valores sintéticos no identifican un efecto causal humano sin aleatorización, distribución estable y tratamiento de interferencias.

**B — Rivales:** H1, la media de completos puede mostrar signo definido pero los límites bajo omisiones pueden incluir 0. H0, la media de completos identifica el signo sin supuestos. Rival fuerte: los límites de peor caso pueden ser anchos o inútiles; eso indica falta de información, no mal funcionamiento. Un estimador MAR sería más estrecho solo bajo supuestos adicionales no contrastados.

**C — Diseño:** 18 casos antes de ejecución: observación completa colapsa intervalo, efecto e interacción conocidos con datos ficticios completos, falta adversarial invierte la interpretación, brazo totalmente ausente, más ausencia no estrecha el intervalo con suma fija, rechazo de falsos ceros y datos malformados.

**D — Código:** módulo de solo agregados, no admite filas individuales, IDs, nombres, identificadores de políticos o eventos públicos. No extrae datos del experimento externo ni calcula historia humana.

**E — Ejecución:** test nativo 18/18, código y SHA emparejados con GitHub y recibo. En el ejemplo sintético los cálculos numéricos coinciden con límites analíticos.

**F — Auditoría:** la función declara `actual_randomization_authenticated=false`, `actual_exposure_authenticated=false`, `causal_effect_claim=false`, `release_ready=false`. Fallan grupos ausentes, sumas fuera de rango, valores no finitos, objetos mal formados y cargas con filas individuales. No incorpora interferencia entre rooms ni cobertura real.

**G — Control:** el código PFL existente `pilot_analysis_dryrun.mjs` indica ausencia de identificación pero no produce cotas numéricas. Este nuevo cálculo mejora una propiedad verificable del flujo de interpretación. Contra controles completos de media y escenario extremo, reproduce igualdad cuando no faltan datos y amplitud cuando se omiten.

**H — Priors:** PF-BR52 registra formalmente la aplicación matemática de límites de peor caso a cuatro brazos ficticios, distinguida de los priors humanos PF-BR50/51. No reivindicar la conocida fórmula Manski como descubrimiento nuestro.

**I — Dictamen:** un **AB-P válido de alcance matemático y QA**, no ensayo de conducta. CT2 científica prospectiva **20/100 ordinal** sin aumento; N1/N2/N3 nuevos **0/0/0**, release gates **0/6** y científico **0/3**. Falta integración de producción y muestra humana.

**J — Decisión:** contabilizar **solo C13**: 13/30 ciclos nuevos válidos acotados, **17 nuevos sin consumir**, **dos históricos STOP_R5**. Continuar por una vía más discriminante de audiencias: cuartil privado vs leaderboard público vs información no comparativa, manteniendo reward y estímulos, pero no replicar más semillas ficticias con la misma función para consumir cupo. Sin main merge, ChatRelay, CI costosa, licencia nueva, contacto de autores ni scoring real.

