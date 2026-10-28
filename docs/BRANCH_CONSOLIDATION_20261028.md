# Consolidación de ramas y gobierno de main — 28/10/2026

**Permiso:** El usuario pidió unificar Politics Fantasy y AB en la versión más reciente de `main` y autorizó que T008 permanezca en el backlog de Codex; los 18 intentos AB-H pendientes permanecen autorizados, pero esta operación de integración y organización de Git no consume ciclos A–J.

## Auditoría de referencia (realizada mediante GitHub remoto)

- Repositorio privado: `GalexY3/Metodologia-AB`; `main` estaba en `f430a085fa1606c4fc7919a768b7b77976da5699` al iniciar esta auditoría.
- Línea de proyecto origen: `research/pfl-abh-branch20-20261028`; deriva de `research/pfl-codex-contributions-20261027`.
- GitHub informó `main...research/pfl-codex-contributions-20261027`: **760 commits ahead, 0 behind**; el branch BRANCH20 estaba **13 ahead, 0 behind** de Codex. Es una línea con fast-forward posible **si sigue confirmándose justo antes de actualizar la referencia**.
- La vista GitHub de cambios `main...Codex` truncó los ficheros a 300; **no hay auditoría integral de cada parche**. La integración preserva historia y contenido de la línea más reciente, pero NO certifica que la suite Python global pase.
- Ramas enumeradas por API de GitHub: 26, con paginación agotada. El análisis comparó cada rama contra BRANCH20: seis estaban completamente contenidas por **ancestría**, dieciocho tenían commits exclusivos/divergentes. Un commit exclusivo no implica un cambio funcional faltante: podría haber sido reimplementado de otra forma, y no se debe mezclar sin inspección por semántica.

### Completamente incluidas en BRANCH20 por ancestría

`docs/core-recovery-20261022`, `method/operational-o2-20261022`, `research/pfl-abh-45-20261027`, `research/pfl-abh-atlas-c20-20261026`, `research/pfl-codex-contributions-20261027`, `research/pfl-sources-reconcile-20261027`.

### Ramas históricas divergentes conservadas, no fusionadas automáticamente

- Método y documentación: `feature/ab-atlas-o7-incremental-20261026` (22 exclusivos), `governance/ab-o5-drift-distance-20261024` (1), `governance/o6-reporting-and-cycle-requests-20261024` (3), `integration/ab-observatory-20261023` (2), `research/ab4-reliability-20261022` (3), `research/ab45-beijing-audit-20261022` (7), `research/ab45-instrumentation-20261022` (6), `research/ab321-o3-drift-20261023` (1), `research/ab-o4-novelty-trajectory-20261024` (1), `research/branch30-invariant-audit-20261022` (5), `research/evidence-gate-20261022` (4).
- Politics Fantasy: `fix/pfl-quick-review-20261026` (2 exclusivos), `research/pfl-ab20-identity-temporal-20261026` (147), `research/pfl-ab20b-historical-identity-20261026` (171), `research/pfl-ab-adaptive32-20261026` (95), `research/pfl-abh-branch20-20261026` (14), `research/pfl-final20-source-integrity-20261026` (29), `research/pfl-sequential-32-20261026` (61).

**Prioridad futura de revisión por utilidad e independencia:** `fix/pfl-quick-review-20261026` (PR #11, 2 commits, potenciales correcciones), luego antiguas PR PFL #12–#15 y cualquier cambio propio de metodología O7. No mezclar dos ciclos incompatibles de Atlas de ramas divergentes ni sobreescribir `CURRENT.md` con informes obsoletos. Revisar diff por fichero y pruebas antes de cherry-picks selectivos. Las cinco PR históricas #11–#15 quedaron abiertas/draft al auditar; no se cerraron, aprobaron ni fusionaron mediante esta tarea.

## Decisión operativa

**`main` será la rama de referencia para la siguiente actividad AB y para Codex**, sin crear ramas nuevas por defecto. Mantener ramas históricas como archivo hasta una revisión de equivalencia y valor; no borrarlas ni forzar referencias Git. Cualquier actualización de `main` debe conservar los límites científicos y operativos: CT2 identidad 29/100 ordinal, progreso V4 36,90 % contractual, VSDS 1/3, hallazgos nuevos N1/N2/N3 0/0/0, gates 0/6. T008 se conserva pendiente en `tareas_codex/`, con checker de Atlas 37 y suite completa Linux no ejecutada. No GitHub Actions costosas, no datos nominales privados ni scoring real.

**Integración técnica propuesta y autorizada:** movimiento de ref `main` por fast-forward, `force=false`, comprobación de HEAD esperado, sin generar una PR de cientos de cambios que lance CI automática. El resultado efectivo del movimiento se verificará en GitHub por separado. Esta nota describe la auditoría y el plan; no inventa un merge realizado.

## Resultado verificado del fast-forward — 28/10/2026

**COMPLETADO:** GitHub devolvió `success: true` al mover `refs/heads/main` sin forzar, con expectativa de SHA anterior `f430a085fa1606c4fc7919a768b7b77976da5699` y destino `5d766d6466325698e14d865d12a919abed0f3c13`. Inmediatamente después, se leyó de nuevo la rama remota y se confirmó **`main` HEAD = `5d766d6466325698e14d865d12a919abed0f3c13`**; la comparación con `research/pfl-abh-branch20-20261028` devolvió `identical`, `ahead=0`, `behind=0`. La cola `tareas_codex/BACKLOG.json` se abrió desde `main`: `T008=PENDIENTE`, `atlas_lots=37`, `codex_available_to_user=false`; `ab_atlas/CURRENT.md` también leído en `main`.

**Importante:** Esta verificación fue de refs, contenidos y documentación en GitHub, NO ejecución de tests, check del Atlas ni revisión del contenido de todos los commits. Conservar los 18 branches divergentes como candidatos de revisión. No existe ninguna tarea de Codex en ejecución; la cola está estacionada. Los commits de mantenimiento posteriores a este movimiento pueden hacer que `main` avance más allá del SHA indicado.

