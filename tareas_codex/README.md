> **ESTADO VIGENTE TRAS BRANCH20 C04 (28/10/2026).** Codex no está disponible para el usuario. **T008 PENDIENTE**: checkout completo de `main`, suite Python integral Linux/POSIX y checker canónico de **39 lotes** (0038 y 0039 añaden C03 y C04). Las reparaciones focalizadas C03 (`majority_sign.py`, **14 PASS**) y C04 (`scoring.py`, **8 PASS**) NO certifican compatibilidad global. Preservar los primeros resultados rojos C03/C04 y sus hashes, y ejecutar sus pruebas en la suite global. Campaña activa: 3 válidos, 1 inválido, 16 autorizaciones restantes; no consumirlos automáticamente al ejecutar T008.

# Cola de tareas Codex — Politics Fantasy League

**Estado 28/10/2026: EN ESPERA.** El usuario no tiene disponible Codex en este momento. Conservar el backlog y no fingir ejecución ni programar reintentos automáticos. El trabajo de investigación AB-H puede continuar por otras vías; los 18 intentos restantes de la campaña BRANCH20 no son presupuesto de Codex y no se consumen al redactar tareas.

**Rama de referencia prevista:** `main`, tras la consolidación autorizada por el usuario el 28/10/2026. Antes de cualquier ejecución, Codex debe verificar HEAD, permisos y estado real del repositorio. No crear más ramas de trabajo por inercia. Las ramas antiguas divergentes quedan bajo auditoría; no hacer merges masivos.

## Tarea principal pendiente

**[T008 — Suite Python integral en Linux/POSIX y replay Atlas de 39 lotes](T008_SUITE_COMPLETA_POSIX.md)** — `PENDIENTE`, prioridad P0. Esta ficha forma parte del [índice estructurado](BACKLOG.json). Una [entrega ejecutable concreta](../research/ABH_BRANCH20_20261028/T008_EXECUTOR_HANDOFF.md) conserva los comandos y las condiciones de aceptación de esta etapa.

T002 registró **57 FAIL, 558 PASS, 28 SKIP** en la ejecución integral histórica Windows. En CONT80, C73–C80 documentaron **89 pruebas originales PASS + 14 subtests** de **ocho suites seleccionadas** en Linux/POSIX; no son la ejecución integral. El checker Python de T007 verificó **31 lotes**; la cadena llega a **39 lotes** después de 0036 (C01 inválido) y 0037 (C02 negativo). El **replay canónico de 37 lotes no está ejecutado**.

T008 deberá documentar HEAD real, Python/pytest, sistema de archivos, primera corrida de `PYTHONPATH=src python -m pytest -q -rs` sin alterar tests, exit code, PASS/FAIL/SKIP, logs y SHA; desde raíz repo, `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates`. Solo con ambas ejecuciones satisfactorias y pruebas registradas podrá indicarse `COMPLETADA_VERIFICADA`; de lo contrario `COMPLETADA_CON_FALLOS` o `BLOQUEADA` según proceda. Correr T008 por sí solo **no es un ciclo AB A–J**.

## Expedientes históricos

| Ficha | Estado registrado | Alcance |
|---|---|---|
| [T001](T001_RESULTADO.md) | COMPLETADA_VERIFICADA | Replay Atlas histórico 29 lotes |
| [T002](T002_RESULTADO.md) | COMPLETADA_CON_FALLOS | Suite Windows y Node; fallos persistentes |
| [T003](T003_RESULTADO.md) | COMPLETADA_VERIFICADA | Paridad V3/V4 en la revisión ensayada |
| [T004](T004_RESULTADO.md) | COMPLETADA_CON_FALLOS | Seguridad local Windows y limitaciones POSIX |
| [T005](T005_ORIGINALES_CONDICIONALES.md) | BLOQUEADA | Original auténtico, derechos, identificadores y revisión jurídica |
| [T006](T006_RESULTADO.md) | COMPLETADA_VERIFICADA | HTTP y claves BOCCL XI/XII en snapshot histórico |
| [T007](T007_RESULTADO.md) | COMPLETADA_VERIFICADA | Atlas 31 y HTTP en HEAD histórico |
| [T008](T008_SUITE_COMPLETA_POSIX.md) | PENDIENTE | Suite completa Linux y Atlas 39 en HEAD actual |

## Condiciones de ejecución

Leer [AGENTS.md](../../../AGENTS.md), `ab_atlas/CURRENT.md` y el [informe de consolidación](../docs/BRANCH_CONSOLIDATION_20261028.md) antes de trabajar. Reexaminar siempre el commit HEAD, pues esta cola no garantiza que una referencia histórica siga actual. No inventar comandos, salidas ni SHA. No modificar pruebas para forzar aprobación. Reservar evidencias en rutas de proyecto o externas privadas sin subir originales nominales ni credenciales. No activar CI costosa, no fusionar otras ramas automáticamente, no publicar scoring de personas reales y no alterar `main` sin una autorización de escritura específica coherente con el trabajo pedido. Los seis gates permanecen **0/6**.

El usuario puede reactivar T008 cuando Codex esté disponible. No existe una ejecución en curso ni una obligación de lanzarla durante el trabajo AB-H.
