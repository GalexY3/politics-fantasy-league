# Politics Fantasy League · AB-H C41–C50 (CONT50) · informe de cierre

**27 de octubre de 2026.** El usuario concedió **10 nuevos ciclos AB-H** de branching. **Ejecutados y documentados C41–C50: 10/10 A–J**, bloque autorizado agotado. Los diez son **AB-P de ingeniería, instrumentación y QA**, no resultados científicos AB-R sobre representantes españoles. [Registro de campaña](CAMPAIGN_STATUS.json), [prerregistro C41](CAMPAIGN_C41_PREREG.json), [Atlas lote 0027](../../ab_atlas/updates/0027-pfl-abh-cont50-c41-c50-20261027.json). Se han escrito los prerregistros C42–C50 antes de sus contrastes, manteniendo fuentes, rivales, falsadores y límites. No hay tests ficticios ni trabajo atribuido a Codex.

**Rama:** `research/pfl-codex-contributions-20261027`, con lectura de blobs SHA de GitHub privado y ejecución local Linux Python 3.13.5 y Node v22.16.0. Sin merge a `main`, Actions costosas, importación de nominativos originales ni scoring de figuras reales.

## Resultado por ciclo

| Ciclo | Evidencia real y límite decisivo |
|---|---|
| **C41 AB-P** | Se integró `forecast.py` con los cambios que faltaban en CONT40. SHA antes `5aaa18dfe...`; tras parche `ef4508fadf...`. **10 FAIL/2 PASS en la fuente original → 12/12 PASS tras aplicar el parche**; dos tests versionados exactos. La primera aplicación local con `patch -p1` falló por la ruta, se corrigió con `-p3`. [C41](C41_RESULT.json). |
| **C42 AB-P** | Test de parámetros finitos y `min_joint` del grafo `network.py`, antes pendiente: Git blob `277b3de...` de la regresión ya en la rama, **7/7 PASS** nativos. [C42](C42_RESULT.json). |
| **C43 AB-P** | Se publicaron seis pruebas contrafactuales `as_of` para `historical_rate` y revisión pública: conocimiento futuro no reescribe el pasado; empates de publicación se rechazan. **6/6 PASS**, originales ficticios. [C43](C43_RESULT.json). |
| **C44 AB-P** | Contraste directo de **archivos V3 y V4 íntegros** de GitHub: 36 hitos y 9 líneas, 36,35 % y 36,90 %, +0,55 pp, los **seis gates bloqueados**. Únicamente `id.real` y `ev.person` pasan 0→1. **9/9 invariantes PASS** por cálculo JS externo. **Desviación del prerregistro:** el replay previsto de esos archivos V3/V4 a través de *ambos runtimes nativos* **no se ejecutó**; se registró la sustitución de instrumento en lugar de inventar una certificación. [C44](C44_RESULT.json). |
| **C45 AB-P** | Se ejecutaron juntos `test_quality.py` original y el negativo C36 sobre `quality.py` SHA idéntico: **3/3 PASS**. La cobertura sigue siendo `NOT_INFERABLE_WITHOUT_SOURCE_CENSUS`. [C45](C45_RESULT.json). |
| **C46 AB-P** | `test_network.py` original, siete pruebas finitas y dos nuevas de no fuga futura/selección contradictoria: **10/10 PASS**; la nueva prueba está versionada, idéntica por hash. No expresa colaboración/ideología. [C46](C46_RESULT.json). |
| **C47 AB-P** | Política `source_eligibility.py` y `test_source_eligibility.py` originales de GitHub, SHA idénticos: **12/12 PASS**. Falsas URLs oficiales y recibos declarados por usuario no liberan scoring. No prueba autenticidad/autoridad real de un editor. [C47](C47_RESULT.json). |
| **C48 AB-P** | `evaluation.py` + `test_evaluation.py` originales, SHA idénticos: **6/6 PASS**, Poisson NLL completo, MAE, skill, calibración con soporte insuficiente, purga temporal y bootstrap por sesiones. No es prueba de predicción real. [C48](C48_RESULT.json). |
| **C49 AB-P** | **48/48 casos PASS**, 45 combinaciones de conteos y tasas más tres controles de skill: `poisson_nll(y,λ) - poisson_log_loss(y,λ) = lgamma(y+1)` sobre λ positivo. Test nuevo guardado en la rama con SHA exacto `adc28fd...`. **48 casos parametrizados no equivalen a 48 hallazgos independientes**. [C49](C49_RESULT.json). |
| **C50 AB-P** | **Ejecución integrada seleccionada:** **173/173 pytest Python PASS en 11,91 s**, **9/9 Node.test PASS en 65,53 ms**. Los **12 módulos fuente y 18 archivos de tests utilizados coinciden con SHA del árbol privado de GitHub**; incluye los controles POSIX sobre interrupciones de CONT30. Se guarda stdout y manifiesto de hashes. **No** es suite integral del proyecto ni validador Python Atlas. [C50](C50_RESULT.json). |

## Resumen de instrumentación

**C50 no se suma a sus test parciales como nuevas replicaciones:** reúne material ejecutado en las campañas anteriores más los nuevos test de esta campaña. El recuento final más útil para el estado del subconjunto es **173 Python + 9 Node, 0 fallos**, con archivos fuente/test SHA iguales a GitHub. El archivo reproducible de salida contiene `C41_before.txt`, `C41_after.txt`, C42/C43/C45/C46/C47/C48/C49, `C50_python.txt`, `C50_node.txt` y `C50_sha_manifest.json`. No se incluyen datos privados de personas. Enlace local de conversación: `/mnt/data/PFL_CONT50_native_evidence.zip`.

Los nuevos tests pueden inspeccionarse en `tests/test_forecast_finite.py`, `test_forecast_history_finite.py`, `test_network_finite.py`, `test_asof_counterfactual.py`, `test_network_asof_counterfactual.py` y `test_poisson_cross_module_identity.py`. Los originales `test_private_audit*.py`, `test_private_store_process_boundaries.py`, `test_secure_store.py`, `test_evaluation.py`, `test_network.py`, `test_quality.py`, `test_source_eligibility.py` y los tests de progreso se conservaron con hashes exactos.

**Contraste adversarial:** los ficheros de progreso V3/V4 se verificaron sobre fuentes originales mediante cálculo independiente en un entorno JS, pero no a través de una ejecución Python+Node completa con esos documentos. Ningún test repara un original institucional ausente, determina `first_public_at` de forma fehaciente, resuelve `NO VOTAN`, acredita RPP por partido, certifica derechos para perfilar personas o establece suficiencia de cobertura. El bloqueo real de *release* continúa.

## AB Atlas, CT2, DRIFT y estados

El lote append-only `0027-PFL-ABH-CONT50-C41-C50-20261027` contiene **10 `run.add`**, sin modificar gates, nodos, aristas, incidencias ni métricas. Sobre la contabilidad anterior: **27 lotes; 63 nodos, 81 aristas, 169 ejecuciones, 44 incidencias, 338 operaciones**, **todos conteos derivados**, todavía **sin la comprobación canónica Python ni SHA de estado**.

**Madurez V4: 36,90 %**, índice contractual, no probabilidad ni porcentaje de políticos incorporados. **CT2 identidad: 29/100 ordinal**, **VSDS: 1/3**, hallazgos nuevos **N1/N2/N3: 0/0/0**, gates de lanzamiento **0/6**. Ningún parámetro mejora por acumular ciclos. Gráfico CT2 existente, **sin falsificar evolución**: [vista completa 0–100 y ampliada 20–40](../ABH_CONT30_20261027/CT2_IDENTITY_CURRENT.svg).

Clasificación de esta campaña: **AB-P, distancia instrumental D0–D1** (tests de contratos previamente existentes, corrección de residuos y compatibilidad entre módulos), no DRIFT D3–D5 ni aumento de hallazgos científicos. **R1:** estimando QA de ficción, no identificación causal. **R2:** casos negativos antes del parche y tests de compatibilidad. **R3:** casos correlacionados; no sumarlos como experimentos científicos. **R4:** fuente exacta por blob y ejecución nativa acotada; no checkout global. **R5:** detener nuevos microtests repetitivos si no resuelven un fallo de integración o bloqueo de producto.

## Continuidad y bloqueo pendiente

Codex puede esperar. La [incidencia #17](https://github.com/GalexY3/Metodologia-AB/issues/17) debe actualizarse a **27 lotes** cuando se retome, y exige checkout exacto de la rama, `python ab_atlas/atlas_delta.py check`, hash de estado, pytest completo y Node completo; guardar comandos, logs, exit codes y fallos, sin CI costosa ni merge a main. **No atribuir ejecución alguna a Codex.** Una próxima campaña debería reducir el énfasis en controles numéricos marginales y atacar validación integral y originales institucionales individualizados que cambien la decisión de producto.

**Cierre:** 10/10 ciclos autorizados consumidos, 0 pendientes de CONT50. Para iniciar un bloque nuevo de ciclos AB-H es necesaria otra autorización explícita.
