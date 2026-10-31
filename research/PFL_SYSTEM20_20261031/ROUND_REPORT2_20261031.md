# PFL SYSTEM20 · segunda ronda española: tres cohortes reales y esquema relacional

**Fecha:** 31-10-2026. **Rama de integración:** `research/pfl-system20-process-corpus-gates-20261031`, derivada sin overwrite del HEAD **ceca9a44961cf13b515750f66bd6c61cd55b3de9** de PR #6. Este informe es evidencia de **ingeniería e inspección de fuentes, no un artículo empírico AB-H sobre política española**. Estado del TFM: pregunta abierta. Fantasy: aplicación secundaria.

## Resultado material

Se identificó un catálogo oficial con licencia **Open Data Commons PDDL** por recurso del [Parlamento de Canarias](https://datos.parcan.es/). Se capturaron con GET HTTPS y SHA tres originales CSV *concretos*, sin cuentas, cookies ni aceptación interactiva. [Manifiesto de los tres originales](../../data/source_manifests/parcan_20261031.json). Cada captura tiene recibo HTTP/fecha, URL de catálogo, SHA, tamaño y prohibición de reintentos ante bloqueos. Los originales se conservan exclusivamente en `/cos-prueba/PFL-scratch-congreso2-20261031/runs/2026-10-31`; Git **no contiene sus CSV ni las filas de iniciativas**.

| Distribución oficial | SHA-256 | Bytes | Filas fuente-local con ID único y fecha |
| --- | --- | ---: | ---: |
| Canarias 2023/X, proposiciones de ley PPL | c426afb56f8b5c51f84afeeadb281a340cf46ccc268f218b2d5841961bd9b095 | 285 | 1 |
| Canarias 2024/XI, preguntas escritas PE | 9ee6895522725f29cdf977ac0dd6da0490ad27c4128dea5fc2d0d7f48bf0e19c | 203545 | 686 |
| Canarias 2026/XI, preguntas escritas PE | fe51a78cc89a9549b9e0232c27b638b6fd4fa0c1aefec2ce89ddb7455312dad2 | 169570 | 524 |

**Observación de calidad reproducible:** 1.211 filas en estos tres **estratos**, con cero claves ID+legislatura repetidas *dentro de cada distribución*, cero faltantes de ID/legislatura/fecha de creación y formato de fechas `YYYY-MM-DD`. No se identificó un denominador independiente de la Cámara ni un registro PE 2025/XI, de modo que no se acreditó una cohorte longitudinal exhaustiva. Una distribución no contiene todo un sistema político. La PE 2026 está expuesta a censura del corte 31/10/2026.

**Separación de outcomes:** el CSV original tiene cabeceras `SITUACION` y `TIPO_FINALIZACION`, pero sus valores **no se inspeccionaron ni agregaron**. El parser `csv.reader` sí decodifica estructuralmente todas las celdas, lo cual se declaró expresamente; no afirmamos cegamiento de bytes. El código de conteo se congeló antes del primer reporte de cobertura, **después de capturar los datos**: no es prerregistro A–J de un outcome ni permite atribuir validez confirmatoria retroactiva. Tests sintéticos de fuente: **10/10 PASS**. [Reporte de fuentes, negativos y derechos](PARCAN_COHORTS/EVIDENCE_REPORT.md), [ledger instrumental](PARCAN_COHORTS/EXECUTION_LEDGER.json), [recibo congelado](PARCAN_COHORTS/receipts/frozen_code.json).

## Normalización de registros reales — local y conservadora

Se implementó `scripts/build_parcan_local_processes.py`, que vuelve a verificar los tres originales frente a SHA y recibos, consume exclusivamente los tres campos institucionales ID, legislatura y fecha de creación, verifica tipo/identidad/duplicados y conserva **sin derivación** `first_public_at=null`, `terminal_state=null`, `transition_events=null`. Normalizó **1.211 registros fuente-local**, salida `process_source_metadata.jsonl` **solo en el PC**: `/cos-prueba/PFL-local-processes-20261031-r1`. SHA-256 de ese JSONL: `7ed31c97be3928e306749972f5b3d746ca0c20a961818674ff0626e9c6679463`. Cada registro conserva source SHA y tiempo de registro local 31-10-2026T05:24:04Z, no se le atribuye una observabilidad pública anterior. [Recibo del origen y normalizador](../../data/source_manifests/parcan_20261031.json). Se ejecutaron ocho pruebas específicas de fechas imposibles, identidad, esquemas, no salida de resultados y seguridad de escritura.

## Capacidad del producto: fuentes y cortes consultables

El GET **local** `/api/spanish-process-cohorts` ofrece las tres cohortes **agregadas**, sus hashes, años, clases y limitaciones mediante `src/politics_fantasy/parcan_cohort_status.py`; el panel está integrado en el observatorio web, separado del juego. La fuente del endpoint es una *instantánea agregada exacta* vinculada por SHA `72f4c0a66c80a032c108b70a6051fe79f9916e12bf202a6720a5968785328b64`, no los originales individuales ni el JSONL local.

El parámetro opcional `as_of=YYYY-MM-DDTHH:MM:SSZ` tiene **semántica del observatorio local**, no primera publicación histórica. Ante un corte anterior a 31-10-2026T05:19:18Z no se devuelve ninguna de las 1.211 filas agregadas y la cardinalidad queda `null`/desconocida, **no cero iniciativas**. Ante un corte posterior devuelve la instantánea capturada, sin inferir el estado real anterior de ningún expediente. Hay controles HTTP de host local, parámetros repetidos, fechas sin zona, rechazos de digest, valores no finitos y referencias inesperadas; no hay navegación a originales ni endpoints públicos desplegados. El panel del Interior continúa mostrando metadatos agregados 1977–2023 tras verificar SHA de su recibo.

## Capacidad del modelo relacional

`src/politics_fantasy/official_temporal_links.py` incorpora un **modelo puramente documental** de instituciones, expedientes del Congreso, comunicaciones procesales, decisiones y documentos, con enlaces tipados a posibles resultados BOE. Distingue `CONFIRMED` vs `BOUNDED` vs `UNKNOWN`, revisión, `recorded_at`, identidad source-local, duplicados y conexiones por referencia directa. Exige crossref para un posible enlace BOE–Congreso; **un texto publicado no es la población en riesgo**. En 44 pruebas adversariales sintéticas PASS se detectó y corrigió la fuga de revisiones futuras en contadores de QA. Los cuatro documentos españoles cotejados por el agente fueron agregados/derivados previamente versionados, sin revalidar sus originales o producir joins reales. El código **no** habilita importación real de personas, procesos con outcomes ni scoring.

**Crítica ontológica:** una institución o actor no se identifica automáticamente con una operación política luhmanniana; un documento puede ser observación de una operación, pero no su identidad ontológica. `docs/PROGRAMA_COMPARATIVO_SISTEMA_POLITICO_ABH_20261031.md` mantiene tres rutas rivales: autorregulación endógena, acoplamientos con el entorno y selección documental. No se ha confirmado ninguna.

## Bloqueos negativos retenidos, sin reiteración

- **Congreso nacional:** exportación de iniciativas HTTP403 en el historial; no reintentada ni eludida; población longitudinal completa sin acreditar, especialmente fracasos/caducidades/censura.
- **Senado:** catálogo oficial de iniciativas legislativas XML V–XV encontrado, pero aviso de aceptación plena por mero uso; no se descargó ningún original ni aceptaron términos.
- **Cataluña SIIP:** licencia general potencialmente vinculante por acceso; no se descargó.
- **Canarias PPLM 2024/XI:** HTTP200 pero el contenido fue rechazado (vacío, HTML o demasiado grande según validador), **sin bytes conservados ni reintento**, no significa cohorte vacía.
- **Canarias PE 2025/XI:** distribución correspondiente no identificada/verificada; no inferir ausencia de iniciativas.
- **BOE/BOCG/Interior y mediaciones económicas/empresariales:** fuentes documentales potenciales y contextuales, pero no se han validado enlaces causales ni se ha unido una empresa a un procedimiento por nombres, fechas coincidentes o ideología.
- **Disponibilidad `as-of`:** los CSV presentan estado *actual* sin vintages probados por expediente; `F_CREACION`, BOCG, HTTP Date y fecha de captura no son `first_public_at`. No hay exposición/horizonte suficientemente definidos para supervivencia, riesgos competitivos o predicción externa.

## Decisión AB-H y trazabilidad

Los tres estratos no superan todavía el G1 de una población en riesgo completa y sus transiciones. Ningún outcome fue abierto para estimación sustantiva; no existe contrato de contraste A–J y código remoto SHA congelados **antes de outcomes**, por lo que no se abrió ningún ciclo AB-R. Las pruebas de Python/Node, capturas, ledgers, metadata-only y desarrollo de producto son **trabajo real no contabilizado como experimentos científicos**. Concesión [SYSTEM20](AUTHORIZATION.json): **20 autorizados, 0 válidos, 0 inválidos, 0 cobrados por planificación y 20 disponibles**; no se ha creado una tanda adicional. No se elevó CT2, Atlas ni preparación para puntuaciones de personas.

**Integración:** esta rama está concebida como PR nueva de revisión apilada sobre PR #6 (a su vez sobre #4 y #3). `main` queda intacta: revisión de dependencias, auditoría Linux de este HEAD y autorización del producto siguen pendientes; un test de compatibilidad Git no equivale a aceptación jurídica/científica. El TFM permanece sin título/estimando central adoptados. El siguiente gate útil es obtener población exhaustiva con estados, fechas de transición y primeras versiones públicas verificables, o un piloto descriptivo con diseño explícitamente transversal y sin pretensión de causalidad.
