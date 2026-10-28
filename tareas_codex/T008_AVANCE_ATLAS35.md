# T008 · Avance: replay canónico del Atlas de 35 lotes

**Alcance:** comprobación estructural local solicitada en T008; **la suite Python completa en Linux sigue pendiente**. No se inicia un ciclo AB y no se modifica `main`.

Checkout `9d0ef8433f92749b3f3364f31139b07320f1ec16`, rama `research/pfl-codex-contributions-20261027`, Windows, Python 3.12.14. Había solo los directorios generados sin versionar `ab_atlas/__pycache__/` y `proyectos/politics-fantasy-league/src/politics_fantasy_lab.egg-info/`. Se usó `PYTHONDONTWRITEBYTECODE=1` y cwd `C:\Github\Politics-Fantasy-Codex`.

```text
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
OK 35 lotes 63 nodos SHA256 bff6978684b0d6d4cdfcd8211656750430b956f6ebb92c0faeff042e13758d81
```

Exit 0 y stderr vacío. `replay` al directorio temporal, exit 0, confirmó **63 nodos, 81 relaciones, 201 ejecuciones, 44 incidencias y 370 operaciones**. Los seis gates continúan sin superar: tres bloqueados y tres pendientes. Estos controles no verifican la verdad, autenticidad o fecha de publicación de las fuentes.

Logs UTF-8 locales bajo `%TEMP%\pfl-atlas35-20261028\`: `check_stdout.txt` SHA-256 `791fc10a8a8881f13336c7cc7295db67810a0cc6a6fa668f7c71eca290a6d0f8`, `replay_stdout.txt` SHA-256 `7f8a97500636a9482279f448490ec4c62d24fe81254f4bd40601166e784de549`; ambos stderr vacíos, SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

La evidencia anterior de **89 pruebas y 14 subtests en Linux** sigue siendo una selección ejecutada por ChatGPT, no la suite completa y no ejecutada de nuevo por Codex aquí. Windows no dispone de WSL, Docker o Podman: el requisito de T008 de un checkout completo en POSIX real permanece pendiente. No se han relajado los controles del almacén ni se ha recurrido a CI costosa.
