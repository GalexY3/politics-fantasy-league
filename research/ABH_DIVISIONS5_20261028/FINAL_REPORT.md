# Politics Fantasy League · AB-H DIVISIONS5 (28/10/2026)

**CERRADA — cinco ciclos AB A–J válidos acotados, cero inválidos, cero planificación, cero pendientes.** Cuatro AB-R (uno de acceso original negativo y tres auditorías documentales) y uno AB-P (código/regresiones). Rama `research/pfl-abh5-divisions-20261028` nacida desde `research/pfl-abh5-holdout-20261028` HEAD `34ab47d82ac16c4df0debd84ff0f1e4f971fd73e`, apilada tras PR #24. ChatRelay NO usado. No merge a main, CI costosa ni scoring de personas o partidos.

## A. Indicadores y nivel de novedad

| Métrica | Antes | Cierre |
|---|---:|---:|
| Ciclos nuevos y ejecutados | 5 autorizados / 0 | **5/5; 4 AB-R, 1 AB-P** |
| CT2 identidad, ordinal 1–100 | 29/100 | **29/100** |
| VSDS | 1/3 | **1/3** |
| Madurez contractual V4 | 36,90 % | **36,90 %** |
| Logros formalmente desbloqueados | 2/90 | **2/90** |
| Release gates | 0/6 | **0/6** |
| N1/N2/N3 NUEVOS | 0/0/0 | **0/0/0** |

[Ledger por ciclo](CAMPAIGN_STATUS.json) · [Trayectoria CT2](CT2_TRAJECTORY.json) · [Gráfico 0–100 y ampliado](CT2_FULL_AND_ZOOM.svg).

**Exposición y tipo de resultado:** C01 partió de un emisor UK nuevo ya descubierto; la API original se intentó después del prerregistro. Para C02–C04 **los totales indexados ya eran visibles antes de prerregistrar**. Estos ciclos son auditorías exploratorias de identidad/grano y procedimientos, NO experimentos ciegos ni descubrimientos científicos novedosos. C05 es instrumentación técnica sobre casos conocidos. La ampliación a otra jurisdicción **no** valida automáticamente la hipótesis científica de identidad ni una capacidad de predicción.

## B. Ejecuciones A–J y falsadores

| Ciclo | Evidencia real y resultado |
|---|---|
| [C01](C01_RESULT.json) · [prereg](C01_PREREG.json) **AB-R D1** | UK Parliament proporciona **API oficial documentada** `GET /data/divisions.{format}/search`, `GET /data/division/{divisionId}.{format}`, identificadores y campos `PublicationUpdated`. Intentos de abrir JSON de 20–27/10/2026 con web y recuperar CSV oficial de 15/07/2026 **fallaron**. **0 bytes JSON/CSV capturados**, 0 hash original y `first_public_at` desconocido. Una ficha original de Commons [división 2411](https://votes.parliament.uk/votes/commons/division/2411) sí muestra `deferred division`, votos `Proxy` y distintas razones por las que falta voto registrado. La portada abierta por una caché antigua terminaba en julio; la búsqueda indexada de octubre era más reciente. Una documentación API no demuestra acceso. |
| [C02](C02_RESULT.json) · [prereg](C02_PREREG.json) **AB-R D0,4** | 21/10/2026, lista oficial Commons **cuatro decisiones** 101–104. Las divisiones parlamentarias **101** y **103** representan mociones distintas pero publican el mismo resultado **345 Aye / 108 No**. De los cuatro vectores de totales solo hay **tres distintos**. Por tanto **(Aye,No) no sirve como identificador único** y tampoco permite demostrar que sean los mismos miembros. Listado indexado, sin fichero nominal: [fixture](C02_UK_DISTINCT_DIVISIONS_COLLISION.json). |
| [C03](C03_RESULT.json) · [prereg](C03_PREREG.json) **AB-R D0,5** | 20/10/2026, un mismo `Northern Ireland Troubles Bill` tuvo **cinco votaciones consecutivas** (enmiendas, nuevas cláusulas y tercera lectura, divisiones 96–100). Porcentaje `Aye/(Aye+No)` **26,1161 %–64,9606 %**, diferencia **38,8445 puntos**. La suma de **2.490 votos registrados en cinco divisiones no son 2.490 personas distintas**. Por tratarse de preguntas procedimentales distintas, no llamar a esto cambios de opinión o postura única sobre toda la ley. [Fixture](C03_UK_BILL_STAGES_20261020.json). |
| [C04](C04_RESULT.json) · [prereg](C04_PREREG.json) **AB-R D1** | En otra cámara, **Lores**, 26/10/2026, tres divisiones relativas al `Cyber Security and Resilience (Network and Information Systems) Bill` (IDs 3729, 3730, 3731). `Content/(Content+Not Content)` varía **36,5385 %, 56,5826 %, 55,5874 %**, amplitud **20,0441 puntos**. Cámara distinta con categorías `Content/Not Content`, `tellers` con rol especial e integrantes de cámara distintos. No son personas ni votos Aye/No comparables semánticamente con Commons; tampoco es réplica de un mecanismo causal. [Fixture](C04_UK_LORDS_SAME_BILL_AGGREGATES.json). |
| [C05](C05_RESULT.json) · [prereg](C05_PREREG.json) **AB-P D0,3** | Implementado **validador de identidad, grano y procedencia** en [division_ontology_research.mjs](division_ontology_research.mjs) + [14 tests Node](test_division_ontology_research.mjs). **14/14 PASS** ejecutados nativamente con Node en contenedor local, y **blobs GitHub idénticos a archivos ejecutados**: fuente `d209949e2c788691d6f0a4e0ccdef9f18e7fb0a7`, tests `17fd8c094768860d58180b6555262e3cea20e9b0`. Rechaza identidad por totales, duplicados, categorías de cámara equivocadas, errores contables, enteros booleanos, falsa asistencia física, `first_public_at` no atestado, fuentes HTTP, URI erróneas, fechas imposibles y trámites vacíos. Primera tentativa exploratoria V8 falló por la global `URL` no disponible; fue **error de desarrollo registrado**, no otro ciclo ejecutado. [Auditoría de ejecución](C05_NODE_TEST_AUDIT.json). Suite integral Python/Node/Atlas del repositorio **NO ejecutada** en este HEAD. |

## C. Fuentes oficiales y condiciones de reproducibilidad

1. **UK Parliament Developer Hub** https://developer.parliament.uk/ · [Commons Votes API Swagger](https://commonsvotes-api.parliament.uk/swagger/ui/index): solo documentación. No se ha obtenido ningún JSON primario de `2026-10-20..27`. En fuente abierta de julio existen etiquetas explícitas `Proxy`, `deferred` y descripción de ausencia de voto registrado.
2. **Commons Index 20/21 octubre 2026** https://votes.parliament.uk/Votes/Commons · [filtro 21 octubre](https://votes.parliament.uk/Votes/Commons?Fromdate=2026-10-21&ToDate=2026-10-21). Las búsquedas de hoy exponen resultados actuales, pero la llamada `open` a filtro de 21 octubre devolvió `Cache miss`, no original descargado; conservar esta limitación por campo.
3. **Lords 26 octubre** https://votes.parliament.uk/votes/lords/division/3729 · https://votes.parliament.uk/votes/lords/division/3730 · https://votes.parliament.uk/votes/lords/division/3731 · la portada oficial enumera totales y fechas, las fichas incluyen roles/tellers. No se guardan nombres ni votos individuales.
4. [UK National Data Library: Parliament voting records](https://www.data.gov.uk/collections/government-and-parliament/parliament-voting-records) advierte de **diferencias entre los resultados oficiales de recuento de tellers y la suma de nombres registrados**, que deben ser un estado de reconciliación, nunca una 'corrupción' asumida.

La fuente informativa de C02–C04 es **índice o HTML institucional**, no JSON de API con SHA. Un resultado de búsqueda sin bytes no demuestra apertura de fichero nominal, autoría original de cada fila ni fecha de primera publicación. No se inventan `first_public_at`, descargas ni licencias.

## D. Dictamen R1–R5

**R1, estimando y unidad**: `house + Parliament/session + official division ID + procedural stage + dated source version` identifica una división; totales de voto no lo hacen. El estimando Aye o Content por división es cuota de **votos contados**, no asistencia, representación de miembros ni preferencia individual oculta. **R2**: rival de identidad ingenuo `(fecha, Aye, No)` falla en 101/103; rival de única postura por bill falla ante 96–100. Un contrato con división oficial y trámite preservado es el baseline metodológico apropiado; no se ha comparado un predictor entrenado. **R3**: valores mayoritariamente vistos antes de prereg, observaciones elegidas de forma exploratoria, dos días/cámaras y sin muestreo externo: nada inferencial ni fusión de grados 1/3. **R4**: negativos de totales idénticos pero decisiones diferentes, múltiples trámites, chamber ontology, roles especiales, proxies, ausencias y publicación. **R5**: no repetir descargas JSON/CSV fallidas para gastar ciclos; usar HTML genuino y prueba local mientras se delega captura original a T018. C05 14 tests validan invariantes **en sus fixtures**, no el sistema completo ni un hallazgo científico.

**2/3 NO ACREDITADO**, nuevos N1/N2/N3=0, y CT2 sin cambios. Aportación práctica: especificación de origen/identidad/procedimiento que reduce falsos eventos y sesgos de medida, pero todavía falta el dataset nominado original, temporalidad y prueba externa independiente de mérito de modelo.

## E. Ejecutor pendiente, no contabilizado

[**T018 — UK Parliamentary original JSON/CSV y QA integral**](../../tareas_codex/T018_UK_DIVISIONS_ORIGINALES_20261028.md) guardada, **NO EJECUTADA**: captar del API original Commons/Lords divisionId (sin confundir con division number), hash exactos, metadata, recuentos y tellers, contrastes con los fixtures de esta campaña y suite Python/Node/Atlas de checkout limpio. Mantener JSON nominal fuera de Git, no evaluar actores ni inferir asistencia. Permanecen las tareas técnicas T011, T016 y T017 abiertas en sus ramas; ninguna consume una plaza AB.

## F. Solicitud para futura rama

**SOLICITO BRANCHING AB-H DE 5 CICLOS ADICIONALES**, condicionado a autorización independiente, para datos parlamentarios de fuentes originales accesibles o evaluación ciega de una hipótesis sociológica realmente discriminante. No proponer otra repetición de índices UK/BOE ni pruebas pequeñas sin fuente novedosa; dar prioridad a T018 y comparadores competentemente especificados. Solicitud no concede ni inicia nuevos ciclos.

