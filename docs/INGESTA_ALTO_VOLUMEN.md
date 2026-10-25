# Arquitectura de extracción y análisis longitudinal a alto volumen

La apuesta principal no es recopilar sin límite. Es construir un **conjunto de datos longitudinales institucionales recuperable, interrogable, versionado e independientemente auditable**. «Gran volumen» describe una exigencia de capacidad del sistema, no una licencia para aumentar solicitudes a páginas oficiales.

## Fuente → Extractor → Raw Lake

Cada conector declara `source_id`, `base_url`, patrones efectivos de URLs obtenidos de catálogos reales, términos legales, semántica temporal, paginación validada y rate limit acordado. Prohibido fabricar endpoints. ETL piloto: `src/politics_fantasy/ingest.py` extrae un documento oficial comprobado, verifica HTTPS/host final, guarda bytes por hash SHA-256 y metadatos HTTP, y ralentiza peticiones. Requiere revisión humana de derechos antes de activarse. **No es todavía un recolector a escala de producción**.

Para el backfill autorizado: inventario de URLs desde índices oficiales, cursor reiniciable y checkpoint por fuente, colas con prioridad, budgets de solicitudes (por origen), exponential backoff/Retry-After/ETag, circuit breaker ante errores y fetches idempotentes. Guardar el HTML/JSON/XML fuente sin transformar, con fecha de fetch y ETag, en almacenamiento que preserve todas las revisiones. Una instantánea no sobreescribe una anterior.

## Datos escalables e instrumentación

- `bronze`: parser estricto por versión + tests con fixtures reales licenciados. Rechazos al *quarantine* con causa y hash, no a descartes silenciosos.
- `silver`: UUID interno, IDs oficiales, mandatos vigentes, roles, trámites, agenda, votación individual, tipos canónicos. Joins por IDs e intervalos, no por coincidencia textual de nombre.
- `gold`: agregados persona×semana×institución×clase de acto; columnas de *exposure* con procedencia; training features congeladas al día anterior del primer evento puntuable.
- Metadatos con linaje: `source_id`, `raw_sha`, `parser_version`, `schema_version`, `first_seen`, `released_at_claimed`, `known_at`, `adjudicator`, `confidence` y estado de revisión.
- Observabilidad: longitud histórica, coverage ratio frente a censo de recursos, latencia de publicación, distribución de campos faltantes, duplicados, drift de schema, discrepancia entre fuente y hecho normalizado, fallos de endpoint y tiempo de recuperación.

## Carga y consulta

Comenzar con almacenamiento local raw + PostgreSQL indexado y particiones temporales de hechos. Cuando el tamaño / latencia lo justifique, extraer `silver/gold` en Parquet columnar por año/institución, ejecutar análisis con DuckDB/Polars/PyArrow. El grafo político puede derivarse por ventanas temporales en tablas relacionales/Parquet; no asumir necesidad de una base de grafos antes de medir coste-beneficio. Las consultas analíticas serán *as-of*, no consultas al estado más reciente.

Procesado textual: extracción/conversión con reglas auditables antes de embeddings o LLM; clasificación de función de la intervención en muestra con doble codificación humana y acuerdo; proveedores LLM (si se usan) se tratan como etiquetadores falibles, con versión exacta, costes, sesgos y auditorías de discrepancia. La etiqueta semántica no puede convertirse automáticamente en «éxito político».

## Calidad y escalabilidad

El test de stress deberá generar una carga **sintética inequívocamente marcada** (p.ej. 100 mil eventos) y comparar tiempo/consumo y detección de duplicados con una base de conteo verificada. La serie sintética NO demuestra que el parser de Congreso funcione. Se requiere una muestra real anonimizada y admisible para validación de ingesta y un catálogo oficial para evaluar cobertura. `src/politics_fantasy/quality.py` proporciona auditoría en streaming de JSONL normalizado y declara su propia limitación de memoria O(nº IDs); corpus superiores requieren SQL/external sort y no una lista infinita en Python.

## Datos políticos no equivalen a desempeño

Una votación individual es una comunicación institucional trazable. Su tasa refleja el calendario y presencia, no causalmente «influencia». Las coaliciones observadas mediante redes de co-voto no demuestran afinidades personales ni negociación informal. El modelo predictivo debe comparar el valor añadido de relaciones y agenda frente al baseline simple y registrar incertidumbre y cambios de régimen.

## Aceptación mínima de un conector real

Se exige: URI oficial y reutilización lícita, muestra real de schema preservada, test de parser contra fixture, IDs estables y revisiones, al menos dos descargas en fechas distintas para conocer cambios, observabilidad de errores, auditoría manual de campos y prueba de que ningún dato futuro entra en `as_of`. **Ninguno de esos gates de corpus real consta superado el 24-10-2026.**
