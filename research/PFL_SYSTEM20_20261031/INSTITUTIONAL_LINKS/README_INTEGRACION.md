# PFL links2 — contrato temporal documental y relaciones institucionales

**31-10-2026. Solo ingeniería; sin estudio AB, sin outcomes, sin publicación.** El trabajo original se realizó en un directorio local scratch aislado de PFL. Posteriormente se portó a una rama de revisión sin conservar los datos personales ni la ruta de perfil del equipo. Biblioteca estándar de Python; la ejecución original no realizó HTTP. El SHA del manifiesto DELIVERY_SHA256 identifica los originales scratch; el presente README contiene una aclaración de portabilidad.

## Diseño y diferencia frente al código existente

official_temporal_links.py construye un catálogo local de hechos documentales fuente-primero, con referencias explícitas de autoridad, familia y clave local. La identidad lógica de un hecho es (NODE|LINK, source_id, local_event_id); la revisión añade revision. Una identidad y revisión exactas se deduplican, un duplicado contradictorio genera error. IDs, títulos, fechas y nombres similares entre fuentes NO equivalen a identidad certificada.

| Componente PFL ya existente, leído solo | Función que NO se duplica | Aporte concreto de links2 |
| --- | --- | --- |
| src/politics_fantasy/warehouse.py | Almacén SQLite normalizado de EVENT, SHA, recorded_at, first_public_at y selección por corte | Proyección pura de enlaces tipados y expediente; no migración de BD |
| src/politics_fantasy/official_source_status.py | Dos XLSX Interior capturados, pero fuente y filas NO admitidas y first_public_at desconocido | Gate que no transforma metadatos en eventos |
| src/politics_fantasy/source_eligibility.py | Cuarentena de identidad/rights/claims; booleans del cliente no certifican fuentes | Mantener prohibición de scoring personal, necesitar registro servidor |
| src/politics_fantasy/boe_2023_publication_bound.py | Cota conservadora bajo política únicamente para dos documentos 2023 | BOUNDED diferente de CONFIRMED, nunca extrapolar el bound |
| research/PFL_SYSTEM20_20261031/BOE_PREP | Parser de enlaces BOE y smoke sintético; LIVE_FETCH_AUTHORIZED=False | No se descargó BOE ni se repitió esa labor |
| events.py, evidence_warehouse.mjs, typed_refs.py, ingest.py y anterior PFL-scratch-temporal-20261031/temporal_evidence.py | Tipos de evento, grafo JS, fuente local, captura segura, revisiones temporales | Joins explícitos Congreso/trámite/BOE, tres niveles de disponibilidad y reporte de missingness |

Los nodos son INSTITUTION, PROCESS, PROCEDURAL_COMMUNICATION, PROCEDURAL_DECISION y DOCUMENT. Una instancia PROCESS requiere CongressProcess(legislature, initiative_family, expediente), sin equiparar proyectos y proposiciones. PROCEDURAL_COMMUNICATION y PROCEDURAL_DECISION son operaciones observadas; INSTITUTION es la organización/documentary issuer; DOCUMENT es un artefacto documental, no el proceso. Esta es una **propuesta de codificación teórica inspirada en la distinción luhmanniana de comunicación y decisión organizacional**, no una validación de Luhmann, ni prueba de agencia individual o causa política. INSTITUTION_OPERATES e INSTITUTION_DECIDES son vínculos documentales, no psicología, responsabilidades nominales ni causalidad.

Los tipos de arista admitidos son INSTITUTION_OPERATES, INSTITUTION_DECIDES, PROCEDURE_STEP, DECISION_STEP, DOCUMENTS_STEP, DECISION_DOCUMENTED y PROCESS_PUBLISHED_IN_BOE. La última exige dos claves exactas (expediente Congreso y documento con forma BOE-A-AAAA-N), familia y legislatura coherentes, así como prueba de cruce directo en la fuente. **En las fixtures la afirmación DIRECT_OFFICIAL_CROSS_REFERENCE está inventada y es solo una condición lógica; no constituye cotejo oficial real.** No se unen por título, similitud, acrónimo, fecha o mera coaparición. El código veta relaciones de identidad personal, afiliación partidista inferida y cualquier arista de tipo no expresamente admitido.

## Temporalidad as-of y ausencias

TimeEvidence mantiene tres clases **distintas**. CONFIRMED requiere supuesto instante exacto first_public_at de esa revisión, verificado por fuente independiente en una futura integración; el harness acepta únicamente testigos sintéticos. BOUNDED admite available_by como cota conservadora sujeta a política específica, pero NO representa first_public_at exacto. UNKNOWN carece de ambos: el evento se excluye y no se imputa al día del boletín, firma o captura. Las dos fechas de prueba son autodeclaraciones ficticias, no testimonios oficiales.

Los nodos usan occurred_at y recorded_at; los enlaces poseen su recorded_at. Para consultar as_of=t se exige que tanto la disponibilidad acreditada/cotada como la captura no sean futuras. Primero se resuelven revisiones; solo después se filtran eventos ocurridos y extremos referenciales. Una revisión de tiempo de publicación desconocido, ya capturada a t, embarga la identidad entera frente a usar sin advertencia su versión anterior. Un empate de revisiones públicas no se resuelve por orden alfabético. Una arista necesita ambos nodos visibles y es como máximo tan cierta temporalmente como su extremo menos fuerte.

Snapshot separa confirmed_nodes, bounded_nodes, confirmed_links y bounded_links, además de bloqueos y unknown. Coverage contabiliza **solo los procesos registrados en ese pequeño grafo**, las etapas documentadas y los expedientes sin enlace BOE observable: ese último estado es NOT_OBSERVED, jamás un cero de éxito o fracaso institucional. Los campos de denominador censal Congreso, tasa de cobertura y tasa de éxito se dejan null.

**Regla antipérdida de temporalidad:** para un pronóstico hecho en t, as_of=t y valid_at=t. Consultar as_of futuro con valid_at pasado es una reconstrucción retrospectiva, no un histórico de información disponible entonces, y puede contaminar predicciones.

## Ejecución y ejemplos

Ejecutar desde PFL-scratch-links2-20261031:

    python -m unittest -v test_official_temporal_links
    python -m py_compile official_temporal_links.py test_official_temporal_links.py smoke_links2.py
    python smoke_links2.py
    Get-FileHash -Algorithm SHA256 .\official_temporal_links.py,.\test_official_temporal_links.py,.\smoke_links2.py,.\EXECUTION_RECEIPT.json

Las pruebas de unittest crean temporales dentro del scratch. Incluyen controles adversariales de join expediente incompatible, relación entidad-trámite sin extremos, identidad de emisor, duplicados, revisiones con fechas empatadas, captura tardía, revisión antigua recuperada posteriormente, primera publicación desconocida, cota vs instante exacto, admisión de fuentes reales, validez/corte, datos JSON duplicados y no finitos, y cotejo de los dos derivados del mismo original.

smoke_links2.py utiliza dos fixtures ficticios fechados en **2099**, con una supuesta legislatura XX, expediente imaginario, órgano, comunicación, decisión y BOE con ID deliberadamente inventado. Al corte anterior: **4 nodos confirmados, 4 aristas confirmadas, 0 bounded**. Al posterior: **4 nodos y 4 aristas confirmadas, más 1 documento BOE bounded y 1 enlace bounded**. Otro proceso con tiempo UNKNOWN no se admite. Este resultado valida el contrato del código, no un hecho de política española.

## Verificación de fuentes españolas YA versionadas, sin extraer personas

La ejecución comprueba únicamente archivos locales que existían previamente en PFL-trabajo y sus bytes JSON locales. No consulta fichas individuales, no descarga PDF ni XLSX, no añade filas y no re-publica fuentes:

* data/observatory/boe_2023_albacete_verified.json: 8 etiquetas de candidaturas de Albacete, **no** ocho partidos jurídicos ni ocho procesos parlamentarios.
* data/observatory/boe_2023_multiterritory_reviewed.json: cotejo en Albacete del orden y acrónimo de las ocho etiquetas y del hash del PDF original **declarado** por ambos derivados. Resultado **8/8 coincidencias**. Ambos derivados se basan en el **mismo documento BOE-A-2023-15066**: no es test independiente del original, pues sus bytes originales no fueron reabiertos.
* data/observatory/bocg_membership_events_2023_2025_AGGREGATE.json: dos números BOCG seleccionados con claves ordinales de eventos; sin población completa, sin identidad personal longitudinal y sin first_public_at exacto.
* data/source_manifests/interior_congreso_20261031.json: recibo de dos XLSX de Interior y licencia de catálogo CC BY 4.0; no se revisan sus filas ni se certifica primera publicación histórica o población de iniciativas Congreso.

El reporte agregado conserva la huella SHA256 de cada **JSON local existente**, no afirma haber comprobado de nuevo la firma de los documentos originales. Estado de los tres checks y del cotejo adicional: LOCAL_DOCUMENTARY_AGGREGATE_CHECKED_NOT_ADMITTED o SAME_ORIGINAL_TWO_DERIVATIVES_AGREE_LOCAL_ONLY. **0 procesos españoles insertados, 0 personas exportadas, 0 joins reales, 0 ciclos científicos.** Ver EXECUTION_RECEIPT.json y TEST_RESULTS.log.

## Límites de derechos y autenticidad

Un SHA local valida identidad de bytes leídos, no autoría oficial, licencia de la transformación, instante histórico de publicidad, interpretación legal, completitud del corpus ni identidad de personas. El catálogo CC BY 4.0 de Interior no autoriza por sí solo usos personales o puntuación. La reutilización de BOE y BOCG requiere conservar atribución, límites y restricciones por distribución y finalidad; aplicar privacidad y base jurídica cuando proceda. La descarga/preparación BOE del proyecto original está bloqueada por términos. No se han aceptado nuevas condiciones ni descargado documentos de terceros en esta campaña.

La etiqueta SYNTHETIC_LAB declarada por el llamador NO constituye un mecanismo seguro de autenticación ni prueba de que un input arbitrario es ficticio. Este módulo no es una API pública ni debe consumir datos reales. Una integración futura requiere **registro de procedencia, licencias, hashes y sellos históricos controlado por el servidor**; no basta un booleano del cliente. Sin fuente fiable, los enlaces de expediente y BOE deben permanecer UNKNOWN o no admitidos.

## Plan de integración condicionado

**G0 — código y paridad:** revisión por prime de las interfaces del almacén canónico warehouse.py y del grafo JS, sin instalar un segundo almacén físico. Cotejar identidad de evento, relojes, revisión y as-of; portar exclusivamente la proyección de enlaces tipados que añada capacidad nueva. No cambiar Git ni código original hasta autorización.

**G1 — autoridad:** conservar originales en almacenamiento privado y verificar licencias concretas por distribución/fin, hash, publicación histórica exacta o bound conservador sustentado, identidad del emisor y evidencia textual de crossref. Prohibir autoacreditación por usuario. Cuando falte cualquiera, bloquear, sin sustituir first_public_at por fecha de oficio.

**G2 — riesgo Congreso:** obtener población censal elegible de iniciativas por legislatura y tipo, con pendientes, retiradas, caducadas y fracasadas. BOE es potencial **resultado de publicación**, nunca población de oportunidades. No convertir datos electorales o de candidaturas en procesos legislativos.

**G3 — tests:** someter a controles de correcciones, deduplicación, versiones contradictorias, contaminación futura, licencias y enlaces many-to-many; ejecutar además suites canónicas de PFL (warehouse, evidence_warehouse, source_eligibility, BOE_PREP) y auditoría de referencialidad.

**G4 — investigación:** solo con fuente, población y finalidad válidas, seleccionar hipótesis y comparadores competentes, congelar el contrato A–J y SHA de código ANTES de outcomes, ledger y R5. **Ningún ciclo AB fue abierto o consumido** por esta tarea. La salida actual es una prueba técnica y una auditoría de concordancia local limitada, nunca validación causal o predictiva.
