# PFL SYSTEM20 · R14 · Auditoría SAIP, derechos, vintages y selección institucional

**Fecha:** 31/10/2026. **Rama:** `research/pfl-system20-process-corpus-gates-20261031`. **Base R13 conciliada:** `c98e45c5e15bfe50ba153d95e30350ee30945406` local=remoto=PR #7 antes de introducir el delta; árbol con tres archivos R14 no versionados **encontrados, preservados, revisados y ampliados con copia previa privada**. El cierre debe acreditar el nuevo HEAD por separado. **R5 STOP. 20/20 SYSTEM20 disponibles; cero ciclos AB-R y AB-P ejecutados.**

## Objeto científico y contrafactuales

La prioridad no es identificar un conjunto extenso de documentos, sino una **población de solicitudes en riesgo identificable longitudinalmente**, con derecho de reutilización del activo concreto, fecha de entrada, unit IDs, estados y testigos de disponibilidad, comparador independiente y separación de expedientes en trámite y finales. Las hipótesis M1 de reproducción/autorreferencia, M2 de acoplamiento y feedback y M3 de producción editorial de observables siguen siendo hipótesis distintas a contrastar frente a B0 (calendario, capacidad, competencias, reformas, selección por canal, cambios de plataforma, política de publicación). Ni la ontología funcional luhmanniana ni las formulaciones de Easton o Deutsch equivalen al marco documental o al régimen legal de la administración observada.

La delimitación regional e institucional es parte del estimando: **SAIP Generalitat inicial ≠ reclamación GAIP ≠ solicitud ambiental castellano-manchega ≠ asiento general municipal ≠ decisión final publicada**. Ni cifras ni enlaces de estas unidades se suman para inventar una población de «procesos políticos españoles». El usuario no ha elegido corpus, pregunta definitiva, estimando, técnica ni tutor de TFM.

## Agente A: Generalitat SAIP `yjpn-vcw8` (solo documental)

Scratch independiente: `/cos-prueba/PFL-scratch-links2-20261031/ronda14`.

- Matriz `OFFICIAL_SOURCE_MATRIX.json` SHA256 **`34a3b70f8fe75df54b3c5c4c8c7337c03af418d12c7afaacf111b0efddfd641a`**.
- Informe SHA **`e11dfd9c31ef8d67c6c8af394713cc16c22b218e25a5c6d9c3b7407fa3023c0b`**.
- Recibo SHA **`38b3bbc1c4921312e9a64654b1d0de18ef6726a8ac303126477ee412dbdb0d32`**; delivery SHA **`f0206354749c5e4f3fc767b7e4c86d6636a71c8199296b795d49931fdd1c3e6b`**.
- 7 fuentes indexadas, 5 categorías de activos examinadas jurídicamente como metadatos y 30 negativos. Indexación pública `/about_data`: unas 23,4K filas **redondeadas**, 35 columnas anunciadas, 15 nombres visibles, 20 no inspeccionados/inferidos; `Codi expedient` y fechas de entrada/estado son pistas de grano pero no auditoría de clave, estados ni universo.
- Dos restore points **editoriales** 10/10 y 24/10/2026 a 13:00 UTC; cero archivos de esas versiones adquiridos, cero SHA de originales históricos y cero `first_public_at` por caso.
- Ficha nacional variante anterior: 4 formatos RDF-XML incluido, mensual; variante reciente: 3 formatos CSV/JSON/XML, semanal. Relojes de creación de catálogo/Socrata incompatibles como prueba directa de primeras publicaciones. Condiciones generales Generalitat #12 obligan por mero acceso/obtención; licencia específica de cada activo/vintage no certificada. No se han aceptado.
- QA sintética del agente **19/19 PASS**, `py_compile` PASS; reejecutada en el proceso de integración **19/19 PASS**, y los seis artefactos que el delivery enumera coinciden en SHA y tamaño **6/6**. El séptimo es el manifiesto de entrega, fuera de su autohash.

## Agente B: nuevas familias autonómicas

Scratch independiente: `/cos-prueba/PFL-scratch-congreso2-20261031/ronda14`.

- Matriz `EVIDENCE_MATRIX.json` SHA256 **`c1518477ded932d21dfef64f6f805afb8bbc3abb345b5d951221918e717be225`**.
- Recibo `RECEIPT.json` SHA256 **`83923e40109789d62f09c58e9622525d3a92430d945a49a8acad84adf23d6396`**.
- Tres familias documentadas: CLM acceso general (estadísticas/revisiones de ficha no originales históricos; licencia CC-SA declarada sin versión y condiciones por uso); Aragón acceso general (registro normativo y totales informativos no fichero inicial; Aragón Open Data vincula por acceso, sin extrapolar alcance a PDF); CLM ambiental (estadísticas 2016–2023, otro régimen jurídico y no casos individuales).
- **16/16 QA sintética PASS**, reejecutada desde scratch. Hashes de los 7 archivos enumerados en recibo comprobados **7/7 PASS**. Su freeze SHA `7065219353deae1634de8c7e806aac801f25391d015e96fe1329bb51d7a9d731` precede las pruebas según el recibo; la secuencia no autoriza inspección de casos reales.
- Ciudad Real se preserva en el documento R14 preexistente: registro general municipal con identificadores declarados, pero clasificación por familia política, enlace asiento↔expediente, condición concreta por activo y denominador externo NO verificados.

## Instrumentación: hallazgo de fallo y corrección

El fichero R14 no versionado `r14_documentary_frame_gate.py` era coherente en otros aspectos (15/15 QA iniciales), pero al tomar `ArchiveHint.described_at` como filtro de conocimiento dejaba ver retrospectivamente una restauración del 10/10 en un `as_of=11/10`, aunque el investigador solo obtuvo evidencia el 31/10. Asimismo la independencia aparente de un comparador se exponía aun si el comparador no había sido documentado en aquel corte. **El fallo fue reproducido antes de parchear** y se guardó copia de los dos archivos iniciales en scratch privado del prime, con SHA original anotado en el informe de conversación.

La reparación exige `locally_known_on` para activo, comparador y cada entrada de versión, y aplica precisión DATE conservadora: el material auditado el 31/10 no puede verse antes del **01/11/2026 00:00:00Z**. La fecha editorial permanece separada: no acredita disponibilidad histórica. Cuatro tests adversariales adicionales; **19/19 QA R14 gate PASS** y sintaxis Python PASS. Este contrato es **solo sintético** y no transforma índices en originales, derechos o estimadores.

El nuevo manifiesto redactado por whitelist `data/source_manifests/r14_scoped_documentary_redacted_20261031.json`, SHA256 **`1a25b34117459fe5914293ca91701863ad02eefb1304be65528e9533e4df0c2a`**, contiene únicamente URLs de fichas, cuatro nuevas **rutas documentales** y enriquecimiento sin duplicación de SAIP R13. No contiene filas individuales ni documentos, identifiers de personas ni outcomes. Los SHA de matrices privadas están presentes **solo como referencias de linaje**, no se copia su contenido a Git.

`procedural_discovery_r14.py` fija el SHA, estructura, derechos bloqueados, hosts oficiales, tipos/ámbito y el corte; falla cerrado frente a alteraciones. `procedural_population_readiness.py`, `denominator_evidence_status.py` y el panel local presentan cuatro grupos nuevos, sin adición entre fuentes; 37→**41 grupos de evidencia** solo desde el corte 01/11, **dos** con capturas fuente-local antiguas, no 41 cohortes. La consulta por `source_id` mantiene indistinguible una fuente todavía futura de otra inexistente. El panel escapa contenido dinámico. Los cuatro grupos no incluyen de nuevo SAIP.

## Admisión, negativos, derechos y falsadores

No hay prueba suficiente de fuente original con todos los iniciales, derechos por activo y fecha, ausencia de condiciones por mero acceso, listas de nulos, paginación completa, estados pendientes/inadmisibles/retiros/subsanaciones, mapa oficial de transiciones, denominador independiente del mismo universo ni `first_public_at` real. Los contadores editoriales no miden causalidad, y las revisiones de ficha no son versiones de ficheros auténticos.

**Reapertura de R5, exclusivamente condicional:** autorización jurídica específica y sin aceptación de términos por el usuario; prueba de distribución completa de entradas con protecciones de datos; identificadores invariables y relaciones oficiales doble-ID; auditoría externa de denominador/canales/estados; testigos positivos de pendientes y censura; dos originales de un mismo activo con SHA y testigo histórico realmente comparables; prepublicación remota de A–J, hipótesis rivales, parsers, código y SHA antes de consultar outcomes. Un negativo con respecto a cualquiera de estas condiciones mantiene STOP.

**Restricciones realmente preservadas:** cero GET a originales de datos y PDF individuales, cero casos/outcomes/PII consultados, cero términos/cookies aceptados, cero contactos, cero puntuaciones políticas reales, cero cambios de `main`, cero CI costosa, cero nuevos resultados o ciclos AB. Los originales Canarias y SIAP y sus derivados permanecen fuera de Git sin nuevas lecturas o reprocesado.

## QA y publicación

Regresión focal integrada del delta y límites HTTP/UI: **75/75 Python y 26/26 Node PASS** (incluye test R14 de fuente futura/inexistente por `/api/denominator-evidence`), sintaxis Python y JS PASS. La QA acredita contratos de software y restricciones de observabilidad, **no** corroboración empírica o contraste de hipótesis. QA Linux R14: **no ejecutada**.

Al cierre se verificarán JSON, código Python, índice, Atlas, estado, diff/staging sin archivos originales, HEAD local/remoto y PR #7. **El presupuesto SYSTEM20 continúa en 20 de 20 plazas disponibles** y las concesiones históricas no cambian.
