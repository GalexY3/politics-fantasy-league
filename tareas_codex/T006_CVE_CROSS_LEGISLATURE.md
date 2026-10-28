# T006 · Integración HTTP y búsqueda de referencias ESE ambiguas tras C66–C68

**Estado: PENDIENTE (Codex no ejecutado). Prioridad P1 — después de T002.**

En la revisión C66 se encontraron **dos documentos originales con la misma referencia corta** `ESE/000002-01`: BOCCL XI, CVE `BOCCL-11-000084`, del 09/05/2022; y BOCCL XII, CVE `BOCCL-12-000986`, del 10/09/2026. No son un mismo original. **No** deducir identidad longitudinal por código ESE.

C67 sustituyó las claves del registro local por `CCYL:BOCCL-12-000986` y `CCYL:BOCCL-12-001042`, con el identificador corto solo como campo descriptivo. Las antiguas claves `ESE/000002-01` y `ESE/000002-02` se rechazan con `AMBIGUOUS_UNQUALIFIED_ESE_REF`. `first_public_at` sigue en `None`; release/real-person scoring **siempre falso**. C67 verificó **28/28 tests Python nativos**; C69 verificó **7/7 tests del contrato JSON**, C71 **32/32 tests unitarios seleccionados** tras añadir enlaces originales a ambos documentos CVE en fuente exacta; C68 inspeccionó servidor/UI. La tentativa C69 de reconstruir `server.py` en otro contenedor falló por transporte; **no** se ejecutó el servidor HTTP real. C71 publicó dos enlaces `source_url` en el catálogo; hay que verificar su salida mediante la ruta HTTP verdadera.

## Tarea ejecutable en checkout completo

1. Registrar HEAD, `git status`, Python/Node, consultar [informe CONT80](../research/ABH_CONT80_20261028/REPORT_FINAL.md) cuando esté disponible y los recibos C66–C68.
2. Ejecutar `PYTHONPATH=src python -m pytest -q tests/test_source_event_registry.py tests/test_source_stage_matrix.py tests/test_scoped_ccyl_refs.py tests/test_source_stage_http.py` desde `proyectos/politics-fantasy-league/`. Registrar exit, stdout/stderr, número de tests.
3. Desde el inventario real del repositorio, localizar **todas** las referencias del patrón `ESE/000002-0[12]` en código ejecutable, fixtures, scripts y documentación; separar **ejemplos históricos** de **lookup en ejecución**. El índice GitHub code-search visto por ChatGPT estaba incompleto; no asumir búsqueda exhaustiva.
4. Ejecutar el servidor **solo en loopback** y comprobar `GET /api/source-stages`: son tres registros documentales, dos `CCYL:BOCCL-12-...`, ninguno con publicación original atestiguada ni puntuación real. Comprobar que los alias cortos nunca se consideran certificados.
5. Si aparece cliente roto: conservar test rojo; corregir únicamente el consumidor real, repetir suite integral T002 y documentar cambios. No cambiar los originales históricos ni inventar fecha/hora de publicación.

## Criterios de aceptación

Inventario de referencias, SHA de fuente y test, prueba HTTP real, commits, logs y límites. **No** dar por completada por los 28 tests unitarios de C67 o la revisión estática de C68. No merge `main`, Actions costosas ni publicación de nombres nominativos. Esta ficha no es un ciclo AB concedido a Codex.
