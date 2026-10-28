# T009 · Main actual · suite Linux completa y checker Atlas 75

**Estado vigente, 28/10/2026: PENDIENTE, NO EJECUTADA.** El nombre del archivo conserva «Atlas60» por compatibilidad de enlaces, pero el **alcance canónico es el número real de lotes del HEAD al ejecutar**, actualmente **75**. Campaña AB-H [MAIN20B cerrada 20 válidos, 0 inválidos](../research/ABH_MAIN20B_20261028/FINAL_REPORT.md). Ejecutar T009 **no constituye un ciclo AB** ni concede autorización para modificar código después de fallos.

## Baselines que sí se verificaron

- **T008 HISTÓRICA:** Python Linux Alpine bajo QEMU, commit `b0344d1a1549e66274a347333239b81fc7575100`: **651 PASS, 28 subtests PASS, 0 FAIL y 0 SKIP**, según [informe original](T008_RESULTADO.md) y [stdout SHA-idéntico](T008_POSIX_FINAL_STDOUT.txt). Dos fallos de entorno iniciales preservados, loopback y base IANA/tzdata solucionados. **No** aplica al código posterior.
- **Atlas 35 HISTÓRICO:** checker canónico sobre commit `9d0ef8433f92749b3f3364f31139b07320f1ec16`, SHA reportado `bff6978684b0d6d4cdfcd8211656750430b956f6ebb92c0faeff042e13758d81`, [informe](T008_AVANCE_ATLAS35.md).
- **MAIN actual:** 75 lotes documentales, 63 nodos, 81 aristas, 241 runs, 48 incidencias, 416 operaciones derivados; **checker nativo 75, SHA canónico y pytest íntegro del HEAD actual: NOT_RUN**. Una auditoría GitHub de C19 revisó 73 lotes para cadena de padres/esquemas/cuentas, **no** todas las invariantes ni los lotes finales 0074–0075 con el checker. [Cierre MAIN20B](../research/ABH_MAIN20B_20261028/FINAL_REPORT.md).

## Criterios concretos de ejecución

1. Crear **checkout íntegro y limpio** de `main` en Linux/POSIX (QEMU Alpine es aceptable), después comparar `git rev-parse HEAD` con el HEAD remoto de `main` al inicio. Anotar `git status --short`, Python, pytest, Node, OS, `tzdata` y red. Sin originales nominales privados. No atribuir T008 a este checkout.
2. En un entorno nuevo instalar el proyecto con extra de test y comprobar explícitamente que `tzdata>=2024.1` resuelve `Europe/Madrid` si el sistema no tiene base de zonas: `PYTHONTZPATH='' python -c "from zoneinfo import ZoneInfo; ZoneInfo('Europe/Madrid')"`. Mantener loopback disponible; desactivar red externa cuando sea posible sin impedir las pruebas locales. Registrar las dependencias.
3. Desde el monorepo:
   ```sh
   git status --short
   git rev-parse HEAD
   PYTHONDONTWRITEBYTECODE=1 python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
   ```
   Registrar lotes, nodos/aristas, incidencias/operaciones, **exit**, stdout, stderr y **SHA256 del estado canónico**. Si no puede calcularse SHA, declarar `UNKNOWN`, no inventarlo.
4. Desde `proyectos/politics-fantasy-league/`:
   ```sh
   PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=src python -m pytest -q -rs
   node --test tests/test_overview_readiness_copy.mjs
   ```
   Incluir todas las suites Python/Node previas y nuevos tests MAIN20B:
   - `ab_atlas/tests/test_delta_timestamps.py` (desde raíz);
   - `tests/test_strict_group_dissent.py`, `test_cluster_bootstrap_estimands.py`;
   - `test_event_metadata_immutability.py`, `test_event_person_ids_snapshot.py`;
   - `test_field_physical_lines.py`, `test_group_report_strict_majority.py`;
   - `test_partial_seed_guard.py`, `test_round_scoring_interval_scope.py`;
   - `test_http_duplicate_json_keys.py`, `test_manual_pilot_corruption_isolation.py`;
   - todas las previas C03/C04 de BRANCH20, parsers históricos y tests de autenticidad/ingesta.
5. **Primera ejecución inalterada:** guardar stdout/stderr, exit, PASS/FAIL/SKIP y subtests en ficheros de evidencia, hashes SHA256, versiones y tiempo. No modificar tests o producción entre corridas para conseguir verde sin registrar primero la incidencia. Clasificar fallos ambientales (tzdata/loopback, path/OS) frente a defectos genuinos; toda reparación que pretenda contar como AB exige **nueva autorización expresa** (MAIN20B agotada).
6. Escribir `tareas_codex/T009_RESULTADO.md` con commit exacto, máquina/checkout, hashes, resultados y límites; clasificar `COMPLETADA_VERIFICADA`, `COMPLETADA_CON_FALLOS` o `BLOQUEADA`. La salida positiva no certifica origen de datos parlamentarios, identidad legal, primera publicación, permisos de scoring o preparación pública.

**Restricciones:** sin despliegue multiusuario, sin puntuación de personas reales, sin cambios secretos a main, sin CI costosa, sin exponer originales privados, sin fusiones masivas de ramas. T009 es la **prioridad P0 de QA** antes de otra tanda de ciclos AB.
