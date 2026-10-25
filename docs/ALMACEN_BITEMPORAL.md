# Almacén local bitemporal mínimo (instrumentación)

`src/politics_fantasy/warehouse.py` es una pieza **de ingeniería**, no un estudio de fiabilidad de fuentes del Congreso.

- Entrada: JSONL de eventos ya normalizados, cada uno con `source_id`, `event_id`, `source_revision`, `event_kind`, `occurred_at`, `first_public_at`, `source_url`, `raw_sha256`, `person_ids`. Todos los timestamps con zona horaria y hash SHA-256 estricto. Los archivos oficiales RAW no deben introducirse como si fueran este formato.
- Se exige SHA-256 esperado del archivo antes del primer registro.
- Inserción atómica de todas las filas: no hay ingesta parcial tolerada.
- Identidad `source_id:event_id:source_revision` es inmutable y nunca se pisa.
- `recorded_at` representa cuándo se adquirió el JSONL local, no cuándo una institución publicó originalmente un evento.
- Consulta retrospectiva exige `first_public_at <= as_of` **Y** `recorded_at <= as_of`; esto impide utilizar en una predicción de 2025 datos recogidos por primera vez en 2026. Es **conservador** y puede infrautilizar datos reales que sí eran públicos previamente; no es una solución por sí sola para certificar disponibilidad histórica.
- Un archivo dado no puede reasignarse a un `source_id` distinto al reimportarlo.
- Escala: streaming durante la escritura, índice compuesto de consulta; carga no paralela y `events_as_of` devuelve una lista en memoria (no streaming) y no soporta decenas de millones de registros. Futuro: extracción por lotes SQL, paginación/cursor, medición de rendimiento, clúster, retención de raw.

**Prohibido concluir** que la falta de filas implica ausencia de actividad política, que la columna de persona es una identificación certificada, que toda publicación ocurrió por primera vez en el timestamp declarado o que un JSONL generado para tests demuestra comportamiento de datos reales.
