# PFL SYSTEM20 — cierre verificable de la ronda de infraestructura española

**Fecha:** 31 de octubre de 2026. **Modo:** implementación/investigación documental y exploración de calidad de fuente, **sin contraste científico AB-R válido**. **Rama:** `research/pfl-system-core-source-pilot-20261031`, [PR #6](https://github.com/GalexY3/politics-fantasy-league/pull/6) draft, basada en PR #4, dependiente de PR #3. PR #5 sobre visión científica permanece abierta; su documento de visión se integró sin cambiar su contenido, y no se ha fusionado su rama. **Sin merge a main.**

## Problema de investigación y límites

PFL tiene como objeto principal estudiar la reproducción, autorregulación, persistencia y transformación del sistema político español, situando los acoplamientos con derecho, economía, empresas, medios y sociedad como segunda dimensión sustantiva. La unidad no puede ser indistintamente una persona, institución, documento, elección o comunicación. La delimitación distingue límite funcional, jurídico-institucional y empírico; la secuencia hipotética perturbación → atención → decisión → ejecución → medición → nueva decisión necesita resultados temporalmente verificables y rivales para hablar de feedback. No es un efecto probado por crear una base de datos. TFM final, primer estimando y fuente elegible definitiva continúan abiertos.

## Evidencia material nueva, con conservación de los originales

Se capturaron dos distribuciones públicas de resultados de elecciones al Congreso, emitidas por el Ministerio del Interior y catalogadas con CC BY 4.0:

- `Elecciones-Congreso-cargos-electos.xlsx`: 326.847 bytes; SHA-256 `cafc4e0f3fc53f01d1370dd47ac841c6cad43a5394e8a8d1afe2495897fbdad4`; coincide con un hash documental anterior del proyecto.
- `Elecciones-Congreso.xlsx`: 1.151.199 bytes; SHA-256 `dba3394f1812f338067231bce68acf56af1e13ddf8cfb709a814bcc46357ebc2`.

Ambos originales: HTTPS HTTP200, URL efectiva original, SHA y tamaño reproducidos, empaquetado OOXML válido. Bytes en `/cos-prueba/PFL-raw-primary/interior_20261031` **fuera del repositorio**. Git guarda solo [manifest](../../data/source_manifests/interior_congreso_20261031.json), fuentes y material derivado agregado. Fecha de captura: 31-10-2026; HTTP Last-Modified 26-06-2026 no acredita fechas históricas de primera publicidad. Derechos por campo, propósitos de reutilización y datos personales requieren revisión aparte antes de exponer registros.

El [lector original congelado, política y recibos](INTERIOR_METADATA/) no requirió bibliotecas de hojas de cálculo, utilizó ZIP/XML de biblioteca estándar y excluyó expresamente las columnas de votos, escaños, personas y candidaturas. En las dos distribuciones la cabecera estaba en fila 4; originales con 8 y 57 columnas. La exploración metadata-only observó **5.600 y 6.203 filas**, **15 años electorales distintos de 1977 a 2023**, y 0 missing en las columnas administrativas permitidas (A–E y A–C) únicamente. Para cargos, 832 claves parciales fecha/elección/provincia, con 4.768 colisiones esperables por múltiples observaciones, **no** 4.768 duplicados. Para resultados, un identificador de fila sin outcomes no está acreditado; duplicación **desconocida**, no cero. [Informe detallado](INTERIOR_METADATA/REPORT.md), [ledger instrumental](INTERIOR_METADATA/EXECUTION_LEDGER.json) y [recibo de la primera agregación](INTERIOR_METADATA/receipts/phase2.json).

**Reproducción independiente:** el [wrapper](../../scripts/replay_interior_metadata.py) recargó los originales fuera de Git, verificó código, SHA de política/manifiesto/bytes, recalculó agregados y devolvió `EXPLORATORY_METADATA_REPLAY_EQUAL` para la misma proyección salvo hora de ejecución. La SHA del primer recibo es `e2128f79c6bb06ca51953d99746a5c0267fcb5fc89f4a119356fa2c344d04207`; un segundo fichero de reporte tiene otra SHA por la hora de ejecución. No se observó outcome político ni se entrenó modelo.

## Ingeniería funcional e integración

- `scripts/verify_interior_originals.py`: replay fail-closed de SHA/longitud, estructura OOXML y protección de rutas y tamaño ZIP.
- `src/politics_fantasy/temporal_evidence.py`: proyección experimental, inicialmente solo sintética, para ENTITY/EVENT/ROLE/RELATION con referencias source-local, revisiones, validez temporal y conocimiento (first_public_at, recorded_at), deduplicación/conflictos y ausencia UNKNOWN/NOT_OBSERVED/EXPLICIT_ZERO. Sin registro de admisión real por autoridad/servidor, **no** produce hechos personales reales ni validación de causalidad.
- `research/PFL_SYSTEM20_20261031/CONGRESO_PREP/`: adaptador offline sintético de censo de expedientes, estrato legislatura/tipo, paginación exacta, denominadores, censura derecha y veto a outcomes en FASE0.
- `research/PFL_SYSTEM20_20261031/BOE_PREP/`: adaptador sintético de índices BOE, acceso GET real bloqueado por condiciones de reutilización pendientes.
- `src/politics_fantasy/official_source_status.py`, `src/politics_fantasy/server.py`, `src/politics_fantasy/web/app.js`: nuevo GET local `/api/scientific-sources` y panel de observatorio sobre metadatos de distribución y SHA truncada, sin originales, nombres, scoring ni falsos claims de cobertura. Cualquier URL o manifest inválido se rechaza.
- `docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md`, `AGENTS.md`, `START_HERE.md`, `docs/PLAN_TFM.md`: restauración del alcance real español y de la prioridad teórica; las opciones del TFM no se promocionan a elección aprobada.
- `docs/AB_O1_O7_RFC_PFL_20261031.md`: propuesta metodológica justificada sobre separación Git/raw/admisión, checkpoints derivados, coste y guardas O1/O7, sin cambiar el método AB pinneado ni reivindicar AB-META.

## QA y fallos no ocultados

Los nuevos controles locales dieron: 32 pruebas de temporalidad, 20 de Congreso, 11 de BOE, 14 de XLSX, 6 del replay de ZIP y 3 del recibo de metadatos; el panel HTTP incluye 3 pruebas en `test_official_source_status.py`. La batería de regresión Windows-safe de almacén/source/as-of/HTTP registró 88 PASS y la revisión Node 34 PASS. La continuidad del proyecto tuvo **14/14 PASS** después de la primera integración. Los números de grupos pueden solaparse; no se suman como ejecuciones AB ni como descubrimientos.

Un intento de ampliar `pytest` a `tests/test_ingest.py` falló en Windows con `SECURE_STORE_UNSUPPORTED_PLATFORM`, dependencia POSIX anterior; se conservó y **no se desactivó el gate de seguridad**. Revisión Linux full sobre el HEAD de esta PR y aceptación humana de P1 siguen pendientes.

## Programa científico y bloqueos

El acceso a la exportación de iniciativas del Congreso no se consiguió verificar (403 sin evasión); tampoco el marco completo de procesos por legislatura/tipo ni `first_public_at` por evento. No sería legítimo usar solo disposiciones BOE aprobadas para estimar supervivencia de iniciativas; el fichero de resultados electorales tiene otro grano. El [borrador A–J](CONGRESO_AJ_DRAFT.md) presenta hipótesis sobre transición y memoria institucional con rivales de calendario, composición, selección, cobertura y fuga temporal. No está congelado para outcomes, no certifica una población ni consume cupo.

Se necesitan: universo completo de oportunidades institucionales y documentos fechados, comparación de tres rutas y antecedentes competentes, prerregistro con código SHA remoto antes del primer outcome, control de censura y fuga, baseline cronológico, sensibilidad e incertidumbre. Si una fuente vuelve a fallar sin condición nueva, aplica R5 y pivota a otra fuente o mecanismo sin inventar datos.

**Presupuesto:** [SYSTEM20](AUTHORIZATION.json) 20 autorizados, **0 ciclos válidos nuevos, 0 inválidos AB, 0 de planificación cobrados, 20 restantes**. Los tests, capturas, reparaciones, instrumentación y exploración previa son `noncycle_work`. No alterar contadores antiguos de ABH25/ABH25B, CT2 ordinal ni gates de lanzamiento: 0/6.

## Decisión de integración

El avance se mantiene en PR #6 en borrador; PR #3/#4 de las que depende están sujetas a revisión y PR #5 no se fusiona automáticamente. La integración en `main` requiere verificación Linux en el commit pertinente, revisión de compatibilidad, alcance jurídico y control de regresiones, sin tener por superada la aceptación humana ni abrir puntuaciones de políticos reales. Esta limitación no invalida la utilidad de originales y código ya adquiridos.
