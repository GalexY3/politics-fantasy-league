> **Actualización de consolidación de ramas (28/10/2026).** La fuente de referencia para la ejecución futura será `main` cuando se complete la integración autorizada. La rama de campaña `research/pfl-abh-branch20-20261028` se conserva como origen auditable. Atlas ahora **37 lotes**, incluidos 0036 (C01 inválido) y 0037 (C02 documental inconcluso), no los 35 de la fase CONT80; el checker Python de **37** está **NOT_RUN**. Ver [handoff actual](../research/ABH_BRANCH20_20261028/T008_EXECUTOR_HANDOFF.md) y [índice Codex](README.md). **Codex no está disponible actualmente para el usuario.** No hay prueba global Linux ejecutada ni evidencia de aprobación. No iniciar GitHub Actions costosas ni merges adicionales. El presente permiso para consolidar `main` fue concedido específicamente por el usuario; no autoriza fusiones futuras sin evaluación.

> **Actualización tras CONT80 C77–C80 (28/10/2026):** Se han ejecutado nativamente **ocho** suites originales con siete módulos SHA-idénticos a Git: **89 PASS +14 subtests PASS, sin fallos ni omisiones**. Los resultados y SHA de logs están en [informe final](../research/ABH_CONT80_20261028/C77_C80_POSIX_FINAL.md) y [manifiesto](../research/ABH_CONT80_20261028/C77_C80_EVIDENCE_MANIFEST.json). Esto **NO equivale a ejecutar la suite Python completa** ni cierra T008. Además el Atlas ha llegado a **35 lotes**; T007 solo certificó 31, por lo que la nueva validación canónica queda pendiente. El presupuesto AB-H CONT80 se ha agotado **20/20**; cualquier ciclo nuevo requiere autorización del usuario.

# T008 · Suite Python completa en Linux/POSIX: cerrar fallos de T002/T004

**Estado: PENDIENTE.** Requiere checkout íntegro de la rama `main` consolidada **en sistema POSIX real** (Linux recomendado) y ejecución por Codex u operador autorizado. No equivale a una ejecución ni a un ciclo AB.

## Por qué

[T002](T002_RESULTADO.md) documenta Windows Python 3.12.14: **57 fallos, 558 éxitos y 28 skips**, con 24 subtests; [T004](T004_RESULTADO.md) aisló fallos de `SECURE_STORE_UNSUPPORTED_PLATFORM`, `O_NOFOLLOW`, creación de symlinks y señales. No solucionar ese límite relajando el almacén.

**Evidencia positiva independiente C73–C76 (28/10/2026):** en Linux CPython 3.13.5, con SHA Git **idéntico** para siete módulos y cuatro tests originales del repo, `test_ingest.py`, `test_ingest_redirect_security.py`, `test_quarantine_ingest.py` y `test_ingest_full_local_e2e.py` dieron **31 PASS, 14 subtests PASS, exit 0, 2,30 s** en ejecución integrada. [C76_RESULT](../research/ABH_CONT80_20261028/C76_RESULT.json). [Evidencia local de esta conversación](../research/ABH_CONT80_20261028/C73_C76_EVIDENCE_MANIFEST.json) contiene SHA de logs; los logs exactos están en el ZIP adjunto a la conversación. **No son** suite completa ni revalidación de Windows.

## Contrato ejecutable

1. Registrar plataforma (`uname -a`), UID, filesystem, Python/pytest y dependencias, `git status --short`, `git rev-parse HEAD`, `git branch --show-current`. Confirmar HEAD antes de comparar T007/Atlas, que puede haber recibido lotes nuevos.
2. En `proyectos/politics-fantasy-league/`, `PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -rs`. Guardar primera corrida **sin modificar tests**, stdout/stderr y exit. Ejecutar `node --test` solo si hace falta verificar que las suites JS no se han roto; no afirmar que un Node PASS corrige Python.
3. Separar los fallos por clase, con conteos basados en stack traces reales: diferencias POSIX/Windows, sincronización y bloqueos, permisos/symlinks, import/dependencias, integridad de JSONL/SHA, redirecciones/HTTP, tests/flaky, otro defecto real. No extrapolar los 31 positivos para afirmar que desaparecen los 57 anteriores.
4. Repetir focalmente en Linux, si la suite lo permite, `test_secure_store.py`, `test_private_store_process_boundaries.py`, `test_private_audit.py`, `test_private_audit_cli.py`, `test_ingest.py`, `test_quarantine_ingest.py`, `test_ingest_full_local_e2e.py`, `test_ingest_redirect_security.py`. Para `SIGKILL`, diferencia entre error interrumpido y pérdida real de energía; no declarar tolerancia a power-loss no probada.
5. Si hay un fallo reproducible: abrir/prerregistrar contraste A–J autorizado antes de modificar código; guardar primero la regresión roja, parche mínimo, prueba verde y suite completa. No alterar tests solo para que pasen.
6. **No usar originales nominativos** ni contactos de red con Senado/Congreso; usar fixtures sintéticos en temporales. No Actions costosas, no despliegue, no merges no autorizados ni más ramas innecesarias, no habilitar scoring real.

## Criterios de aceptación

Informe `T008_RESULTADO.md` con HEAD, Linux y FS, comando/exit/log, recuento total **PASS/FAIL/SKIP** y fallos clasificados. `COMPLETADA_VERIFICADA` solamente con suite completa PASS y límites declarados; si persisten fallos, `COMPLETADA_CON_FALLOS` con reproducibilidad y próxima tarea concreta. Los seis gates continúan en 0/6 hasta evidencia independiente.
