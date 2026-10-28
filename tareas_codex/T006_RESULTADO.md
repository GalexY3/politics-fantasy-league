# T006 · Resultado de comprobación local

**Alcance:** comprobación post hoc de integración, no nuevo ciclo AB. Checkout de partida `6e359a89e74f06927e51ca4dc8a9ea1714e37acd`, rama `research/pfl-codex-contributions-20261027`; Python 3.12.14, Node v24.16.0, Windows. El checkout tenía carpetas generadas sin versionar `ab_atlas/__pycache__/` y `src/politics_fantasy_lab.egg-info/`, sin afectar a esta verificación.

## Comprobaciones

- Desde `proyectos/politics-fantasy-league`, con `PYTHONPATH=src` y `PYTHONDONTWRITEBYTECODE=1`, `python -m pytest -q tests/test_source_event_registry.py tests/test_source_stage_matrix.py tests/test_scoped_ccyl_refs.py tests/test_source_stage_http.py` terminó con **32 passed**, código 0, 0,92 s. Estas pruebas usan un servidor local real en loopback para los casos HTTP.
- Una comprobación HTTP independiente inició `ThreadingHTTPServer` únicamente en `127.0.0.1` y solicitó `GET /api/source-stages`: HTTP **200**, exactamente tres registros con claves `CCYL:BOCCL-12-000986`, `CCYL:BOCCL-12-001042` y `SENADO-XV-P82-20260915`; 0 fechas de primera publicación verificadas, `first_public_at=null` en todos, `real_person_scoring=false` y `release_ready=false`. SHA-256 de la respuesta `930666c1d3e4c6daaa6e83017225f171b4698099057ca77226602e9cbd3227d3`.
- Por separado, la función de servidor `evaluate_server_claim` rechazó `ESE/000002-01` y `ESE/000002-02` con `AMBIGUOUS_UNQUALIFIED_ESE_REF`, `eligible=false` y `release_grade=false`. El endpoint es un catálogo de lectura, **no un endpoint HTTP que adjudique claims**. El campo `short_ref` sigue figurando como descriptor, no como clave ni certificación.
- Se reforzó el test HTTP existente para comprobar exactamente las tres claves y que ninguna clave sea un alias `ESE/`.

## Inventario y resultado negativo conservado

La búsqueda de texto de **todos los archivos versionados** del commit base se hizo con `git grep -n -I -e ESE/000002-01 -e ESE/000002-02 6e359a8 --` desde la raíz; terminó con código 0, **52 líneas en 26 archivos**. En código productivo solo aparece `src/politics_fantasy/source_event_registry.py`: dos `short_ref` descriptivos y el conjunto que rechaza expresamente los dos alias. No hay coincidencias en `scripts/`. En pruebas aparecen `test_rc07_provenance_claim_gate.py` (registros sintéticos históricos deliberados), `test_scoped_ccyl_refs.py` (prueba negativa de alias) y `test_source_gate_boundaries.py` (fixtures de tipos). Las demás coincidencias son documentación, fichas o registros históricos de Atlas/investigación. Se revisaron las referencias en código y tests, no se buscaron datos privados ignorados ni contenido binario.

La prueba existente `python -m pytest -q tests/test_source_gate_boundaries.py` produjo inicialmente **3 failed, 8 passed**: los casos de entrada no string esperaban `UNSUPPORTED_CLAIM`, pero usaban un alias que ahora se rechaza primero como ambiguo. Se confirmó que los tres valores no string devuelven `UNSUPPORTED_CLAIM` con la clave calificada real. Se migró esa entrada del fixture al CVE, sin modificar el código de producción; el rechazo independiente de alias se conserva en `test_scoped_ccyl_refs.py`. Tras ello, la orden focal anterior ampliada con `tests/test_source_gate_boundaries.py` terminó con **43 passed**, código 0, 0,75 s.

## SHA-256 del código y tests examinados tras el ajuste

| Ruta desde el proyecto | SHA-256 |
| --- | --- |
| `src/politics_fantasy/source_event_registry.py` | `d32718571d68801b91604c6695528cd47442e8a729959c5525a9071939b4568a` |
| `src/politics_fantasy/server.py` | `2041b19cd5bec3eedf48f0161478eace7c15ccae0771a2dddc318313df8a8938` |
| `tests/test_source_event_registry.py` | `e6009556a5e047ad76758a5d7eb38d9a994ce5363c2aee4e8eb23bfdeb0097a4` |
| `tests/test_source_stage_matrix.py` | `af9fb4efbfd5aeceecfaf94be4b1322bc0c10a3b8186947530ced9bdced55f82` |
| `tests/test_scoped_ccyl_refs.py` | `6bec7c676fcb76bbc5b3ff60222f62cb44d1515144af5be7fcffb0fbe727db32` |
| `tests/test_source_stage_http.py` | `2351c57abd1756db6514d5b700b91fb88ade7c7e61a26779a7548854d333de32` |
| `tests/test_source_gate_boundaries.py` | `ceca83c61b12d98c03a0ee250975ad419a03d8683fa88f569a42c5b6702b12df` |

Los controles focales pasan; la aceptación integral depende de la ejecución y el informe de T002 sobre el árbol final. Estas comprobaciones no prueban identidad histórica, autenticidad de publicaciones, `first_public_at`, compatibilidad de clientes externos no presentes en el repositorio ni preparación de lanzamiento. No se ha contactado ninguna fuente externa ni se ha añadido material privado.
