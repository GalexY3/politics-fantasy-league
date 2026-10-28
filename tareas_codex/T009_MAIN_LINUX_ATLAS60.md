> **Alcance vigente tras MAIN20B C07, 28/10/2026:** T009 permanece PENDIENTE para el HEAD real de `main` y **62 lotes** del Atlas, no 60. El nombre del archivo conserva la cifra del snapshot inicial para mantener enlaces; el ejecutor usará `ls updates/*.json` y el número real al ejecutar. T008 está verificada únicamente en el checkout histórico `b0344d1`. C07 añadió `tzdata>=2024.1` a los extras opcionales `test` y `research` sin restricción Windows; al ejecutar T009 verificar con **instalación limpia de `.[test]` y TZPATH del sistema desactivada** que `ZoneInfo("Europe/Madrid")` resuelve y registrar el entorno. No confundir un entorno configurado con prueba del código actual. [C06-C07](../research/ABH_MAIN20B_20261028/C06_C07_REPORT.md).

# T009 · Revalidación de main: Linux completo y Atlas 62

**Estado: PENDIENTE.** Se crea como tarea nueva, **NO** sustitución de T008. T008 **está COMPLETADA_VERIFICADA únicamente en el checkout histórico b0344d1a1549e66274a347333239b81fc7575100**: suite completa Linux Alpine bajo QEMU, **651 tests PASS +28 subtests PASS, 0 FAIL/0 SKIP** tras preparar loopback y base IANA, según [informe original SHA-idéntico](T008_RESULTADO.md) y [stdout original](T008_POSIX_FINAL_STDOUT.txt). Replay canónico de **35 lotes** ejecutado históricamente de forma independiente en commit `9d0ef8433f92749b3f3364f31139b07320f1ec16`, ver [T008_AVANCE_ATLAS35.md](T008_AVANCE_ATLAS35.md). Ambos sucesos están preservados sin falsificar una prueba del HEAD actual.

## Contexto nuevo que exige este expediente

La comparación GitHub del checkout T008 `b0344d1` con `main` observado en `894e1b7a48c83bd84cc4c38cfb7e7699bf077ac1` mostró historias divergentes (**162 commits ahead / 4 behind; 119 archivos cambiados**). Se añadieron/alteraron doce módulos Python/JS importantes y catorce archivos de test (incluido uno Node); entre ellos validación de fechas Atlas C01, C03/C04 mayoría/scoring, nuevos parsers de historial e identidad, mayoría estricta C04 MAIN20B y bootstrap de sesiones C05 MAIN20B. Este conteo es una comparación entre dos snapshots, no una prueba de fallos.

Atlas creció de **35 lotes con checker nativo PASS** a **62 lotes**, con recuentos **documentales** de 63 nodos, 81 aristas, 226 runs, 48 incidencias y 401 operaciones; **SHA del estado canónico de 60 UNKNOWN**. `atlas_delta.py` ahora tiene validador ISO-aware de `batch.at` y un registro histórico de inversión de 1534 segundos entre 0015 y 0016. El resultado histórico de 35 lotes no valida automáticamente los 25 nuevos.

## Criterios de aceptación

1. Verificar checkout íntegro **actual** en Linux/POSIX real (puede ser VM QEMU), registrar `git status --short`, `git rev-parse HEAD`, `git branch --show-current`, `uname -a`, Python/pytest/Node/tzdata/loopback. **Comparar el HEAD concreto con `main` antes de concluir**. La suite no requiere CI pública ni activación de workflows caros.
2. Conservar la **primera** ejecución sin parches, incluso si falla. Desde raíz del repositorio:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
   ```
   Desde `proyectos/politics-fantasy-league`:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -rs
   node --test tests/test_overview_readiness_copy.mjs
   ```
   Conservar stdout/stderr, códigos de salida, versiones y SHA256 verificables de logs. Distinguir ausencia de `tzdata`/loopback de regresiones reales, **sin cambiar pruebas o producción entre corridas**.
3. Incluir los tests añadidos después de T008: `ab_atlas/tests/test_delta_timestamps.py`, `test_majority_sign_failclosed.py`, `test_scoring_rule_contract.py`, `test_group_majority_semantics.py`, `test_forecast_future_exposure.py`, `test_congress_members*.py`, `test_congress_vote_dates.py`, `test_archival_contract_interop.py`, `test_strict_group_dissent.py`, `test_cluster_bootstrap_estimands.py`; evitar contar manualmente más de una vez tests que ya incorpore el full suite.
4. Ejecutar el **checker nativo Atlas 62 lotes y obtener SHA de estado**. Comprobar incidencia `PFL-BRANCH20-C19-ATLAS-UNVALIDATED-AT` sin reescribir lotes históricos y clasificar las anomalías de fecha. Si hubiera nuevos deltas al ejecutar, usar el número **real** de ese HEAD, no asumir 60.
5. Reportar en `T009_RESULTADO.md` estado `COMPLETADA_VERIFICADA`, `COMPLETADA_CON_FALLOS` o `BLOQUEADA`, con evidencia y límites. Un resultado PASS no acredita identidad jurídica, derechos de reutilización ni puntuación política real.

**No consume ciclos AB-H por realizar una tarea de QA.** Nuevas reparaciones que requieran ciclos A–J deben contar con preregistro y cargo contra la campaña MAIN20B (15 autorizaciones disponibles en la última auditoría), sin automatizar scoring de personas ni desplegar la plataforma.
