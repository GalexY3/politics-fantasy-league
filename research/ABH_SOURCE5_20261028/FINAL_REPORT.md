# Politics Fantasy League · AB-H SOURCE5 (28/10/2026)

**CIERRE: 5/5 ciclos A–J válidos de alcance acotado, 0 inválidos, 0 de planificación, 0 restantes.** Rama `research/pfl-abh5-source-validation-20261028`, iniciada desde `research/pfl-abh5-postt010-20261028` (HEAD inicial `56660f0cf648aabb4d8fb4d22e0f93bc7036967a`). Es el **segundo bloque de cinco ciclos**, distinto de la campaña anterior ya cerrada. ChatRelay NO utilizado. **C01** abrió prereg e intentó reconsultar el JSON del Congreso, encontró el bloqueo 403 ya documentado y se dejó como **intento no contado** por R5; no es el primero de los cinco ciclos válidos. Los ciclos contados son **C02–C06**.

## A. Indicadores y contabilidad de los ciclos

| Indicador | Inicio | Cierre | Comentario |
|---|---:|---:|---|
| AB-H autorizados | 5 | 5 ejecutados | C02–C06; C01 intento descartado |
| AB-R / AB-P | — | 2 / 3 | C02, C06 / C03–C05 |
| Inválidos / planificación / disponibles | 0/0/5 | 0/0/0 | C01 no completo A–J, no consumido |
| CT2 identidad | 29/100 | **29/100** | Escala ordinal, no probabilidad |
| VSDS | 1/3 | **1/3** | Sin mejora experimental |
| Avance contractual V4 | 36,90 % | **36,90 %** | No recalculado ni simulado |
| Logros activos desbloqueados | 2/90 | **2/90** | QA-01/QA-02 solo candidatos |
| Gates de release | 0/6 | **0/6** | Ningún permiso nuevo |
| Hallazgos N1/N2/N3 **nuevos** | 0/0/0 | **0/0/0** | No audita el N1 histórico del portfolio |

[Trayectoria CT2 estructurada](CT2_TRAJECTORY.json) · [Gráfico completo 1–100 y ampliado](CT2_FULL_AND_ZOOM.svg). La línea se mantiene plana en 29 porque los controles de software, un nuevo catálogo y el reanálisis de datos ya expuestos **no** demuestran una contribución sociológica novedosa. No existe repunte de CT2 ni inferencia causal.

## B. Ejecución y evidencia ciclo por ciclo

| Ciclo | Tipo / deriva | Realización verificable | Resultado y falsación |
|---|---|---|---|
| [C02](C02_RESULT.json) | AB-R D0,8 | Vía oficial del Ministerio del Interior para distribuciones de paridad de candidatos/as y cargos electos | **0 originales XLSX**: URL y descripción de catálogo **no equivalen** a corpus, checksum, filas o fecha de primera publicación. Nueva vía de trabajo, no hallazgo N1. |
| [C03](C03_RESULT.json) | AB-P D0,3 | [Guard de bytes OOXML](../../src/politics_fantasy/source_capture_guard.py), [8 controles](../../tests/test_source_capture_guard.py) | **8 PASS**. Rechaza archivos vacíos, HTML 403, ZIP defectuoso/atravesado, SHA erróneo y URL insegura. Estructura válida **no demuestra** origen institucional. |
| [C04](C04_RESULT.json) | AB-P D0,3 | [Guard temporal as-of](../../src/politics_fantasy/publication_asof_research.mjs), [6 controles](../../tests/test_publication_asof_research.mjs) | **6 PASS**. Mantiene `UNKNOWN_FIRST_PUBLIC_AT` sin declaración acreditada, evita sustituirlo por fecha de hecho/captura; resultado con atestación sigue siendo provisional. |
| [C05](C05_RESULT.json) | AB-P D0,5 | [Comparador de composiciones](../../src/politics_fantasy/parity_comparator_research.mjs), [7 controles](../../tests/test_parity_comparator_research.mjs) | **7 PASS**. Exige misma elección/distrito y cobertura de categorías; produce brecha porcentual descriptiva con los dos denominadores. Todos los datos de test son sintéticos, no resultados del Interior. |
| [C06](C06_RESULT.json) | AB-R D0,4 | [Sensibilidad por votación](../../src/politics_fantasy/vote_aggregate_sensitivity.py), [6 controles](../../tests/test_vote_aggregate_sensitivity.py) | **6 PASS**. Reanaliza cuatro agregados transcritos en ACH20; una fila por expediente oculta diferencias de `49,712644` y `52,011494` pp entre votos. No es un nuevo corpus ni nuevo N1. |

Los ocho archivos de código/test de C03–C06 se compararon **exactamente por SHA Git blob** con los archivos de la rama. El entorno local aislado corrió Python 3.13 y Node 22.16.0; [registro detallado de resultados](TARGETED_NATIVE_TESTS.json): **14 Python + 13 Node = 27 controles PASS**, sin fallos finales. Se preserva el primer 12/13 de C04+C05: la prueba esperaba el subtipo de rechazo `UNMATCHED_STRATUM` donde el código rehusó la unión como `CATEGORY_MISMATCH`; se corrigió la aserción, no el comportamiento. Los estados de módulo ausente antes de escribir código son RED de instalación, **no RED conductual**. Esto no equivale a una ejecución del repositorio completo, de Linux limpio ni de Atlas sobre el nuevo HEAD.

## C. Contraste descriptivo que cambia una decisión de modelado, no una conclusión social

Única muestra utilizada: [ACH20 C08, cuatro recuentos HTML ya transcritos](../ABH_ACH20_20261028/C08_CONGRESO_AGGREGATE_SAMPLE.json), fuente catalogada Congreso sesión 193 del 23/07/2026; **no** se obtuvieron los bytes originales XML/JSON nominales. El `total` es **sí + no + abstención** en cada votación, no la totalidad de diputados ni el universo de individuos expuestos. Primer `first_public_at` desconocido. [Resultado numérico íntegro](C06_AGGREGATE_SENSITIVITY.json).

| Expediente | Convalidación, sí sobre votos contados | Urgencia, sí sobre votos contados | Porcentaje si se colapsaran ambas |
|---|---:|---:|---:|
| 130/000049 | 175/348 = 50,287356 % | 344/344 = 100 % | 519/692 = **75,000000 %** |
| 130/000050 | 167/348 = 47,988506 % | 347/347 = 100 % | 514/695 = **73,956835 %** |

**Decisión de unidad:** una votación institucional no es un expediente. No utilizar el agregado por expediente como señal única de consenso ni para atribuir comportamiento a personas. La evidencia que ya existía en ACH20 C08 refutaba la relación 1:1; aquí se cuantifica la distorsión con una línea base descriptiva más adecuada, **sin prueba inferencial**. Cuatro observaciones seleccionadas no permiten estimar efectos ni extrapolar.

## D. Bloqueos, controles adversariales y tareas para Codex

- **T011 sigue pendiente**: [encargo técnico específico](../../tareas_codex/T011_FUENTE_PARIDAD_QA_SOURCE5_20261028.md). Exige obtener por HTTPS comprobado los XLSX originales de Interior, registrar redirecciones/código HTTP/tamaño/hash y esquema de denominadores, y ejecutar suite completa Python/Node/Atlas en un checkout limpio de la rama; guardar fallos, logs, SHAs y controles. Prohibidos datos nominales originales en Git, scoring de personas reales, saltar TLS o CI costosa.
- **No hay fuente gubernamental original validada** de paridad; el XLSX guard solo prueba integridad estructural de bytes **que otro ejecutor aporte**. La posible ausencia de filas no equivale a cero casos.
- **Fecha de publicación y fuga temporal**: no hay evidencia independiente de `first_public_at`; el helper C04 es un contrato sintético y su atestación no verifica por sí sola la página del editor.
- **Denominadores para sociología electoral**: el comparador C05 está desconectado del esquema XLSX real; su brecha de composición no es probabilidad individual de elección, desigualdad causal ni medida de resultados por nombre.
- **Dos medallas QA**: [auditoría de candidatos QA-01/QA-02](QA_ACHIEVEMENTS_CANDIDATES.json). T010 sí contiene logs de una suite integral en **otro SHA**; SOURCE5 añade código no validado en checkout integral. En consecuencia **no** se desbloquean estas medallas ni se eleva artificialmente 2/90 a 4/90.
- Revisiones de PR #18 y #19 siguen pendientes; SOURCE5 no fusiona ni sustituye sus resultados. El porcentaje V4 y los seis gates continúan sin adjudicación nueva.

## E. Dictamen R1–R5 y siguientes decisiones

**R1**: Estimando sociológico plausible: diferencia de representación entre candidatos/as y electos por elección/distrito y categorías verificadas, **pendiente de obtener denominadores y clasificaciones originales**. **R2**: baseline competente igual distribución y ámbito electoral, no ratios mezclados; para votos, estratificación por voto original frente al colapso por expediente. **R3**: la serie de ensayos ha sido adaptativa y exploratoria; no reclamamos intervalos inferenciales ni multiplicidad controlada. **R4**: negativos específicos de fuentes falsas, fechas indebidas, IDs duplicados y categorías no coincidentes. **R5**: STOP de reintentos de origen 403, avance por instrumentos locales mientras se mantiene la tarea de ejecución para el original. **2/3 NO ACREDITADO**: no hay ventaja de modelo frente a rival fuerte con datos auténticos, ni repetición independiente prospectiva, ni un mecanismo causal de alcance general. Tampoco se proclama un 1/3 nuevo por reanalizar filas conocidas.

### Procedencia y reproducibilidad

Preregistraciones anteriores a código/ejecución: [C03](C03_PREREG.json), [C04](C04_PREREG.json), [C05](C05_PREREG.json), [C06](C06_PREREG.json); C02 [prereg](C02_PREREG.json). La campaña conserva [autorización](AUTHORIZATION.json), [intento no contado](C01_ACCESS_PROBE.json), [ledger de estado](CAMPAIGN_STATUS.json), [resultados nativos](TARGETED_NATIVE_TESTS.json) y gráfico CT2. Ningún dato original ni propiedad intelectual privada se han publicado o fusionado. El soporte local de pruebas representa solo los módulos de investigación, **no** todo el repositorio.

**SOLICITO BRANCHING AB-H DE 5 CICLOS ADICIONALES**, condicionado a investigar evidencia institucional nueva realmente discriminante, primero mediante originales y denominadores autenticables de T011 si llegan; de lo contrario, resolver una nueva clase de bloqueo no dependiente de descargas, sin volver a repetir el 403 ni gastar ciclos en tests triviales. Esta solicitud **no** concede autorización ni permite ejecución futura automática.
