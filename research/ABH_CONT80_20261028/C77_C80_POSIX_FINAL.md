# CONT80 · C77–C80 y cierre final de 20 ciclos AB-H

**28/10/2026.** Autorización explícita de 20 ciclos. **20/20 A–J realmente documentados: C61–C80.** No quedan plazas autorizadas; cualquier nueva campaña requiere autorización nueva. [Ledger](CAMPAIGN_STATUS.json). Los dos ciclos documentales paralelos CR01/CR02 (Atlas 0032/0033) **no** se incluyen en los 20.

## Evidencia de esta fase: POSIX exacto, no entorno Windows

Tras las cuatro suites C73–C76 (31 pruebas), se preregistraron sucesivamente C77–C80 y se ejecutaron en Linux, Python **3.13.5**, con código y tests de GitHub cuyos hashes Git se verificaron byte por byte, datos exclusivamente ficticios, cero consultas a servidores oficiales:

| Ciclo | Tipo | Suite original, resultado nativo |
|---|---|---|
| **C77** | AB-P | `tests/test_secure_store.py` — **22/22 PASS** (0,20 s). Permisos, symlinks, diez hilos de mismo SHA, dieciséis escritores JSONL, directorio `fsync` y rollback de escritura fallida. |
| **C78** | AB-P | `tests/test_private_store_process_boundaries.py` — **4/4 PASS** (5,97 s). Cuatro procesos/48 registros sin colisión; `SIGKILL` durante ledger y antes/después de enlace del objeto, auditor detecta condición insegura. |
| **C79** | AB-P | `tests/test_private_audit.py` — **24/24 PASS** (1,48 s). SHA falso, duplicados, JSONL truncado, constantes no finitas, comentarios de auditoría huérfanos, locks compartidos y muerte de proceso. |
| **C80** | AB-P | `tests/test_private_audit_cli.py` — **8/8 PASS** (7,21 s). Exit 0 solo para objeto/revisión completos; exit 2 para error, objeto huérfano, root ausente o captura no revisada, sin imprimir URL/identificador/SHA privados. |

**Ejecución conjunta, no ciclos adicionales:** las ocho suites originales versionadas de C73–C80, **89 PASS, 14 subtests PASS, 0 FAIL, 0 SKIP, exit 0 en 15,20 s**. Siete módulos Python fuente y ocho archivos de tests mostraron hashes Git idénticos a su rama; no se modificó producción ni tests. [Manifiesto de todos los SHA, incluyendo salidas](C77_C80_EVIDENCE_MANIFEST.json). El ZIP con logs está adjunto a esta conversación: `PFL_CONT80_C77_C80_POSIX_evidence.zip`, SHA-256 `cde6e8355134b770f0c97a36ea99bdca37af9367540cc9dda4851066bd9c0181`.

**No confundir alcance:** T002/T004 reportaron 57 fallos en Python global Windows, mayoritariamente por soporte POSIX, pero estos 89 ensayos **no** son la suite completa, no certifican que todos esos fallos desaparezcan en Linux. Un test de `SIGKILL` o barreras `fsync` no prueba tolerancia a un corte eléctrico o concurrencia maliciosa fuera del operador. No hay cotejo de originales institucionales, licencia efectiva, identidad estable, primera publicación ni base jurídica para perfilar a representantes.

## Atlas y metodología

El nuevo delta append-only [0035](../../ab_atlas/updates/0035-pfl-abh-cont80-c77-c80-posix-20261028.json), padre `0034`, contiene **4 `run.add` y ningún uplift**. Estado documental tras 0035: **35 lotes, 63 nodos, 81 relaciones, 201 runs, 44 incidencias y 370 operaciones**. La comprobación canónica `python ab_atlas/atlas_delta.py check` para **35 lotes no se ha ejecutado** (T007 certificaba 31 anteriores); SHA actual desconocido. Se han mantenido los resultados negativos y las limitaciones en los A–J particulares [C77](C77_RESULT.json), [C78](C78_RESULT.json), [C79](C79_RESULT.json), [C80](C80_RESULT.json).

La evaluación de progreso continúa **V4 contractual 36,90 %**, **CT2 identidad 29/100 ordinal**, VSDS **1/3**, N1/N2/N3 científicos nuevos **0/0/0**, gates de lanzamiento **0/6**. CT2 no cambia porque los tests de infraestructura no aportan prueba de identidad.

**Gráfico CT2, escala 0–100:** `0 ├─────────────● 29 ────────────────────────────────────┤ 100`  
**Detalle CT2 25–35:** `25 ├───● 29 ──────┤ 35`  
*Valores: 29 al inicio de CONT80, 29 al cierre; no se supone una evolución intermedia ni una ganancia.*

## Trabajo pendiente (sin ciclos nuevos)

[T008 — suite completa Linux/POSIX](../../tareas_codex/T008_SUITE_COMPLETA_POSIX.md) queda **PENDIENTE** con checkout íntegro, pytest global, clasificación de fallos y revalidación canónica de **35 lotes**, no 31. [T005 — originales institucionales](../../tareas_codex/T005_ORIGINALES_CONDICIONALES.md) sigue **BLOQUEADA**. No se usaron GitHub Actions costosas, no se fusionó `main`, no se incorporaron datos originales nominativos ni se activó puntuación real.

**Cierre del presupuesto: 20 ciclos efectivos, 0 restantes.** Para continuar con otro bloque AB-H haría falta una nueva concesión explícita, preferiblemente centrada en un fallo POSIX global reproducible o un original institucional que permita discriminar un bloqueo real; no se rellenarán plazas por rutina.
