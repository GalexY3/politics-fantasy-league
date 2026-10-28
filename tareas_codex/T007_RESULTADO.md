# T007 · Revalidación del Atlas y HTTP, 28/10/2026

**Resultado: COMPLETADA_VERIFICADA para el alcance de T007.** Checkout base `af090f598fdae0cc62ff12f556840140a1cc0235`, rama `research/pfl-codex-contributions-20261027`, Windows, Python 3.12.14. Al iniciar había únicamente los directorios generados sin versionar `ab_atlas/__pycache__/` y `src/politics_fantasy_lab.egg-info/`. La prueba HTTP añadida después se ejecutó sobre ese código base y consta en `tests/test_source_stage_http.py`. Esto no es un nuevo ciclo AB ni certifica producción.

## Atlas

Desde `C:\Github\Politics-Fantasy-Codex`, `PYTHONDONTWRITEBYTECODE=1`:

```text
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
OK 31 lotes 63 nodos SHA256 ff1160dc63a9cfdbd58e9cc534604975375438e47c7fa15a9988386e0bbaeaca
```

Exit 0, stderr vacío. `replay` a `%TEMP%\pfl-t007-replay.json`, exit 0: **63 nodos, 81 relaciones, 191 runs, 44 incidencias y 360 operaciones**, coincidentes con el conteo documental. `data_registry`, `identity` y `events` siguen bloqueados; `authentication`, `e2e` y `deployment`, pendientes. El checker acredita invariantes estructurales, no autenticidad de fuentes ni validez de las conclusiones.

## Fuentes y HTTP

Desde `C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league`, `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`:

```text
python -m pytest -q tests/test_source_event_registry.py tests/test_source_stage_matrix.py tests/test_scoped_ccyl_refs.py tests/test_source_stage_http.py tests/test_source_stage_wire_contract.py tests/test_source_stage_document_urls.py tests/test_source_gate_boundaries.py
55 passed in 0.76s
```

Exit 0, stderr vacío. Entre estas pruebas, una nueva prueba abre `ThreadingHTTPServer` en `127.0.0.1` y consulta el handler real `/api/source-stages`: HTTP 200, tres registros, dos CVE BOCCL XII distintos con URL HTTPS `www.ccyl.es` que contienen su CVE correspondiente, `first_public_at=null`, scoring real y release deshabilitados. Solo se comprueba lo servido localmente, sin abrir las URL institucionales ni probar autenticidad o primer momento de publicación. Los alias ambiguos siguen rechazándose en los controles correspondientes.

Logs originales locales, UTF-8, bajo `%TEMP%\pfl-t007-20261028\`: `atlas_stdout.txt` SHA-256 `2ab4f21905694d5418d247a22a19457d14bf5b380864ff334666f29a02d753bb`; `pytest_stdout.txt` SHA-256 `65377264edd62a975ba919ecc3aa88979fa42f859c3d0147fbd278896758355a`; ambos stderr vacíos, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

## Pendientes ajenos al alcance verificado

Los fallos de T002/T004 por dependencia POSIX, señales y creación de enlaces siguen pendientes en un entorno POSIX real; no se alteró la implementación segura para Windows. T005 sigue bloqueada para originales y permisos no acreditados. Los resultados de T001/T006 sobre 29 lotes permanecen como historial y no se presentan como mediciones de este HEAD.
