# T008 · Ejecución integral POSIX y replay canónico Atlas 55 (PENDIENTE)

**Estado vigente: PENDIENTE / APLAZADA, 28/10/2026.** El usuario no tiene Codex disponible por ahora. **No se ha ejecutado** la suite Python integral actual de `main` ni el checker canónico Atlas de 55 lotes. La campaña BRANCH20 ya está **cerrada 19 válidos + C01 inválido, cero ciclos disponibles**. [Informe final](../research/ABH_BRANCH20_20261028/FINAL_REPORT.md) · [CURRENT](../ab_atlas/CURRENT.md) · [backlog](BACKLOG.json).

## Objetivo y baseline

El ejecutor comprobará en un **checkout privado íntegro Linux/POSIX** la compatibilidad global de todos los cambios de `main` y el estado canónico del Atlas. Las pruebas anteriores son **históricas y de otro alcance**: T002 documentó en Windows 57 FAIL, 558 PASS, 28 SKIP; CONT80 ocho suites Linux seleccionadas 89 PASS y 14 subtests; BRANCH20 obtuvo regresiones focalizadas de C03–C18 (incluida integración selectiva C18 35 PASS). Ninguno certifica la suite integral actual.

**Atlas al cierre:** 55 lotes (0036–0055 de BRANCH20 incluidos), recuentos documentales: 63 nodos, 81 aristas, 221 runs, 48 incidencias, 396 operaciones. **SHA canónico no disponible**, check original NO ejecutado. T007 solo verificó 31 lotes históricos.

## Primera corrida, sin tocar código ni tests

Desde la raíz del monorepo, capturar HEAD, rama, entorno, permisos y estado antes de ejecutar; si no hay checkout completo o HEAD verificable, devolver `BLOQUEADA` y no inventar resultados.

```sh
git status --short
git branch --show-current
git rev-parse HEAD
uname -a
python --version
python -m pytest --version
PYTHONDONTWRITEBYTECODE=1 python ab_atlas/atlas_delta.py check \
  --base proyectos/politics-fantasy-league/ab_atlas/seed.json \
  --updates proyectos/politics-fantasy-league/ab_atlas/updates
```

Desde `proyectos/politics-fantasy-league/`:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -rs
```

Capturar stdout, stderr, exit status, duración, versión de Python y pytest, estado del filesystem y hash SHA256 de los logs privados. **No corregir los tests después de ver fallos para hacerlos verdes**; la primera corrida roja forma parte de la evidencia. Distinguir incompatibilidades de Windows/POSIX de bugs genuinos y de dependencias ausentes. Cualquier reparación sustantiva exige plan, control negativo y prerregistro de un nuevo ciclo **solo si existe autorización posterior expresa**.

## Regresiones nuevas que deben estar incluidas

Python: `test_majority_sign_audit.py`, `test_majority_sign_failclosed.py`, `test_scoring_rule_contract.py`, `test_group_majority_semantics.py`, `test_forecast_future_exposure.py`, `test_abh_branch20_typed_refs.py`, `test_congress_vote_dates.py`, `test_congress_members.py`, `test_congress_members_duplicate_json.py`, `test_archival_contract_interop.py`. Además, todas las suites anteriores de ingesta, seguridad, auditoría, HTTP y modelo.

Node: `node --test tests/test_overview_readiness_copy.mjs` y regresiones del observatorio UI; no declarar test de navegador ejecutado si solo se pasó Node estático.

**Incidencia abierta C19:** `PFL-BRANCH20-C19-ATLAS-UNVALIDATED-AT`: la función `batch_check` admite un `at` sintético no fechado. Antes de imponer formato ISO con zona, auditar retrospectivamente 55 lotes; **no reescribir** deltas históricos inmutables ni inferir que un `check` exitoso ya comprueba cronología de publicación.

## Resultado y aceptación

Registrar en `tareas_codex/T008_RESULTADO.md` el HEAD, rama `main`, entorno, comandos, salidas y hashes, conteos PASS/FAIL/SKIP, clasificación de todos los fallos, resultado de Atlas y digest canónico verificable, con conclusiones y límites. Estado final:

- `COMPLETADA_VERIFICADA` solo si la suite global y el checker canónico salen correctamente y con evidencia, sin promover certeza sobre permisos jurídicos o valor científico.
- `COMPLETADA_CON_FALLOS` si hay errores reproducibles, adjuntando salida roja y discriminantes posteriores.
- `BLOQUEADA` si faltan checkout, Python o sistema POSIX adecuado.

Sin originales nominales privados en GitHub, sin credenciales personales, sin puntuación de políticos reales, sin despliegue, sin CI costosa ni merges automáticos. Ejecutar T008 **no consume ni crea ciclos AB**.
