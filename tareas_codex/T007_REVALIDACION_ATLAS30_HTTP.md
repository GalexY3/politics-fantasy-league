> **Estado actual: COMPLETADA_VERIFICADA para su alcance (28/10/2026).** El texto de prerregistro y sus instrucciones siguientes son históricos. [Resultado efectivo T007](T007_RESULTADO.md): replay Python de 31 lotes y 55 pruebas HTTP/fuentes aprobadas sobre `af090f598fdae0cc62ff12f556840140a1cc0235`. Las suites POSIX y originales externos permanecen pendientes; no se han reejecutado desde este chat.

# T007 · Revalidar el HEAD posterior a C71 (Atlas 31 y HTTP)

**Estado PENDIENTE.** Distinta de T001/T006: aquellas **sí** tienen informes de ejecución en Windows sobre el HEAD base `6e359a89e74f06927e51ca4dc8a9ea1714e37acd`. No reutilizar sus resultados como si hubieran validado el commit actual.

## Brecha verificable

- [T001](T001_RESULTADO.md): `python ab_atlas/atlas_delta.py check` **PASS para 29 lotes**, SHA canónico reportado `c06641eb51915d0a0a5b21a111cd91b8fb55db33b7c12c0dabcde14c8635275c`. **No** comprueba el nuevos deltas `0030` y `0031`.
- [T006](T006_RESULTADO.md): fuente previa a C71, 43 casos focalizados Python PASS tras corregir tres fixtures. HTTP loopback real `/api/source-stages` probado allí. C71 añadió `source_url` para dos CVE en `source_event_registry.py`; esos bytes/campos nuevos **no estaban en el baseline**.
- [T002](T002_RESULTADO.md): suite Python en Windows **exit 1, 57 fallos / 558 PASS / 28 SKIP**; Node **125 PASS exit 0**. La mayoría de fallos están vinculados a POSIX y Windows, no deben ocultarse ni darse por corregidos.

## Encargo concreto

Desde checkout íntegro **actual** de `research/pfl-codex-contributions-20261027`, registrar `git rev-parse HEAD`, `git status --short`, plataforma y versiones. Ejecutar el checker Python del Atlas **31 deltas** (misma sintaxis que T001) y registrar stdout/stderr/código/SHA canónico **nuevo**. Comparar contadores derivados: 63 nodos, 81 edges, **191 runs**, 44 complaints y **360 operaciones**. No alterar lotes anteriores.

Luego ejecutar `PYTHONPATH=src python -m pytest -q tests/test_source_event_registry.py tests/test_source_stage_matrix.py tests/test_scoped_ccyl_refs.py tests/test_source_stage_http.py tests/test_source_stage_wire_contract.py tests/test_source_stage_document_urls.py tests/test_source_gate_boundaries.py` y comprobar `GET /api/source-stages` realmente por loopback: 3 registros, dos enlaces `source_url` con CVE correcto, ambos con `first_public_at=null`, sin habilitación de puntuaciones reales. No consumir una red externa ni añadir datos personales.

Si el entorno es Windows, **no** presentar tests que exigen POSIX como superados ni reescribir la abstracción segura solo para hacerlos pasar. Con entorno POSIX real, reintentar precisamente el subconjunto privado problemático de T002/T004 y distinguir éxitos y errores. Guardar logs/exit/hashes y test rojo previo a cualquier reparación. Sin main merge ni CI costosa.

## Aceptación

`T007_RESULTADO.md` solo tras ejecución documentada; archivo de log verificable y reproducción en HEAD explícito. Esta ficha no equivale a una ejecución ni a un ciclo AB.

**Actualización C72:** nuevo lote `0031` documenta únicamente auditoría de informes de ejecutor. Se exige replay Python de los **31 lotes actuales** y nuevos SHA/counts, no reutilizar el SHA del baseline 29 lotes. 
