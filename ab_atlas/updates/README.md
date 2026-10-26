# Registro de lotes

Crear archivos JSON con nombre ordenable lexicográficamente, p. ej. `0001-PFL-XXXX.json`, `0002-PFL-YYYY.json`.

Cada lote usa `schema: "ab.atlas.delta.v1"`, `batch_id`, `parent_batch`, `at`, `actor`, `reason` y `ops`.

Este README no es un lote y queda excluido por el motor de replay (solo lee `*.json`). Hasta que haya ciclos nuevos ejecutados no debe añadirse ningún patch de hallazgos inventados.
