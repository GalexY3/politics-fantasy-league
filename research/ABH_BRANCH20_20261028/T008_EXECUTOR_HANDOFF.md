> **Nota de consolidación (28/10/2026).** Para ejecutar esta ficha tras el fast-forward autorizado, usar **`main` como rama de referencia y HEAD real**, no `research/pfl-abh-branch20-20261028` que figura más abajo como origen histórico. Mantener 37 lotes, no 35. Consultar [índice Codex](../../tareas_codex/README.md). El usuario tiene Codex temporalmente no disponible y esta ejecución está **en espera**, sin CI ni job activo. El contrato de ejecución y los límites restantes se mantienen.

# T008 · Entrega a ejecutor POSIX sobre BRANCH20

**Estado PENDIENTE — 28/10/2026.** La ejecución de T008 NO está acreditada. Esta ficha es una tarea concreta para Codex/u otro ejecutor con checkout íntegro, **no** un ciclo AB por sí misma.

## Rama y estado que debe usar

- Repo privado: `GalexY3/Metodologia-AB`.
- Rama actual de campaña: `research/pfl-abh-branch20-20261028`.
- HEAD de inicio de esta campaña: `72a2ae2deeb9eaa719b598943c1e8d18360ed6ea`; **no fijarlo como HEAD actual**, hay nuevos commits.
- Atlas de referencia en esta rama: **37 lotes** (0036 recoge intento C01 inválido; 0037 documenta C02 negativo), contadores derivados **63 nodos, 81 aristas, 203 runs, 45 complaints, 373 operaciones**. La validación Python de 37 sigue `NOT_RUN`. T007 verificó 31; no aplicar su SHA a 37.
- Historial técnico previo: 8 suites originales seleccionadas Linux 89 PASS + 14 subtests; Windows full pytest 57 FAIL / 558 PASS / 28 SKIP, Node 125 PASS. **No** equiparar 89 seleccionados con full pytest.

## Contrato de ejecución

Desde checkout completo en Linux/POSIX, antes de ejecutar pruebas:

```sh
git status --short
git branch --show-current
git rev-parse HEAD
uname -a
python --version
python -m pytest --version
```

Si la rama o checkout no son correctos, DETENER y documentar `BLOCKED`. Guardar versión de dependencias, FS si está disponible, y stdout/stderr completos en **ubicación privada no versionada**. No se requiere red externa ni credenciales institucionales para las pruebas.

Desde la raíz del repositorio, ejecutar el checker canónico con todas las actualizaciones ya integradas:

```sh
PYTHONDONTWRITEBYTECODE=1 python ab_atlas/atlas_delta.py check \
  --base proyectos/politics-fantasy-league/ab_atlas/seed.json \
  --updates proyectos/politics-fantasy-league/ab_atlas/updates
```

Desde `proyectos/politics-fantasy-league/` ejecutar **sin modificar código ni tests previamente**:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -rs
```

Registrar exit code real, PASS / FAIL / SKIP / subtests, duración, hashes SHA256 de logs y HEAD. Si hay fallos, conservar primera corrida íntegra, clasificar por stack trace y entorno (POSIX, permisos, enlaces, señales, lock/concurrencia, imports, test defectuoso o fallo funcional). No interpretar `SIGKILL` como corte eléctrico. No convertir la tarea Codex en ciclo AB ni realizar reparaciones sin un nuevo prerregistro C03 (u otra rama) y el correspondiente contraste discriminante autorizado.

## Criterios de aceptación

Crear `research/ABH_BRANCH20_20261028/T008_EXECUTOR_RESULT.md` con referencias a logs, HEAD, entorno, número de lotes, SHA canónico y resultados completos, más fichero JSON estructurado si resulta útil. Declarar `COMPLETADA_VERIFICADA` solo si ambas ejecuciones terminan satisfactoriamente y el alcance completo queda documentado. Si falla, `COMPLETADA_CON_FALLOS` con trazas y próxima tarea concreta; si no hay checkout ejecutable, `BLOCKED` con causa precisa.

Mantener fixtures sintéticas, sin publicar originales de votaciones nominativas ni credenciales, sin puntuaciones reales, sin cambios a `main` ni CI costosa. No elevar V4 36,90 %, CT2 29/100, VSDS 1/3 ni los seis gates sin evidencia que corresponda específicamente a esas medidas.
