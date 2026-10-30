# T025 · Release path, achievement v6, guard fail-closed y QA limpia

**Estado: TAREA PENDIENTE PARA CODEX/PC. NO EJECUTADA EN ESTA CAMPAÑA.** Rama de referencia `research/pfl-abh5-release-criticalpath-20261028`, derivada de AECCHOICE5 PR #31. Verificar HEAD al comenzar y leer `AGENTS.md`, AB 3.2.1 y O3–O7, `ab_atlas/CURRENT.md`, `research/ABH_RELEASEPATH5_20261028/FINAL_REPORT.md`, `product/progress_scope_v4_20261027.json`, `ab_atlas/ACHIEVEMENTS_REGISTRY.json`, `product/release_gates_v1_20261028.json`, `docs/THREAT_MODEL_STRIDE_PUBLIC_RELEASE_20261028.md`.

## 1. Primer paso P0: reproducir tests críticos, no afirmar release ni nuevo score personal

Crear rama de ejecución `exec/pfl-t025-releasepath-qa-20261028` en checkout limpio y PR **borrador contra RELEASEPATH5**, jamás main. Sin ChatRelay ni CI costosa. Ejecutar nativamente con salida stdout/stderr, exit code, versiones, SHA del HEAD y estado `git status --porcelain`:
1. `python proyectos/politics-fantasy-league/ab_atlas/validate_achievements.py` (registro v6, **5/90**, 6 eventos de auditoría append-only).
2. `node --test proyectos/politics-fantasy-league/tests/test_release_guard.cjs` (9 casos con fuente **real** de V4 y logros, no fixtures inventados). Este script **no se ha ejecutado nativamente** en la campaña. Las 9 pruebas sobre blob exacto de `release_guard.cjs` sí se ejecutaron en JavaScript V8 (8/9 primera, 9/9 tras corregir regex, `C04_GUARD_TESTS.json`).
3. `node proyectos/politics-fantasy-league/src/politics_fantasy/release_guard.cjs proyectos/politics-fantasy-league/product/release_gates_v1_20261028.json proyectos/politics-fantasy-league/product/progress_scope_v4_20261027.json proyectos/politics-fantasy-league/ab_atlas/ACHIEVEMENTS_REGISTRY.json`: **exit esperado = 3 (release BLOCKED 0/6)**, no ERROR de sistema. Verificar JSON estructura sin permitir `ready=true` accidental.
4. Prueba completa **Python, Node y navegador loopback** en checkout limpio según README + O6: conservar primer fallo, no editar tests para aparentar PASS. El historial T008 nativo histórico no es certificado de HEAD actual.

## 2. Límite de confianza del guard que no puede ignorarse

El `release_guard.cjs` usa función inyectada `verifyEvidence(spec, attestation)`. **Por defecto devuelve false** y el CLI está deliberadamente bloqueado: **ningún badge, 100% ficticio V4 o cadenas de atestación dentro del manifest desbloquean 0/6 gates**. El test con `()=>true` es exclusivamente una **simulación de dependencia externa NO IMPLEMENTADA**. No sustituirla por `()=>true` en producción; eso crearía una puerta trasera de release. Antes de permitir `ready=true` se requiere verificación independiente de fuente/bytes/identidad/revisores/autenticidad de cada gate y un cierre humano/jurídico aparte. Probar adversarialmente Host, Origin, CSRF, IDOR, carreras de transferencias, fuente no autenticada, as-of futuro, inferencias de puntuaciones personales y fuga de secretos, según el STRIDE.

## 3. Ruta a 100% y gates reales, no métricas cosméticas

[Resumen de prioridad calculado](../research/ABH_RELEASEPATH5_20261028/C05_PRIORITY_MATRIX.json): V4 **36,90 %**, faltan **63,10 pp** respecto del alcance actual, **8 hitos nivel0**, **9 nivel1**, **6/6 gates abiertos**. Tres logros documentales auditados en registro v6 `PFL-SCIENCE-01`, `PFL-EVENTS-01`, `PFL-SECURITY-02`, con todos los anteriores 2/90, ahora 5/90. **El 36,90 y los gates no cambian**, ya que desbloquear medallas no acredita implementación.

Las seis puertas del manifest requieren (a) **fuentes RPP originales y derechos específicos**, (b) **identidad jurídica real con controles de homónimos**, (c) **eventos verificables persona-fecha/primera publicación**, (d) **authn/authz multiusuario**, (e) **E2E real y réplica independiente**, (f) **hosting seguro y piloto aprobado**. El modo local ficticio es el único autorizado en alcance acotado; **ni observatorio agregado ni fantasy nominal público están autorizados por el guard**.

## 4. Entregables y criterios de aceptación

Crear `tareas_codex/T025_RESULTADO.md`, `tareas_codex/T025_EVIDENCIA/MANIFEST.json`, logs de auditoría de código y QA con SHA de pruebas y fecha UTC. Adjuntar **resultados nativos**, no inferidos de ejecución JS en chat, y diagnosticar blockers sin maquillarlos; revisar si la registry v6 o HTML de logros requiere regeneración/actualización del snapshot embebido (si HTTP consume JSON puede funcionar y file:// requerir importación manual). Confirmar no scripts modifican V4 por medallas. Marcar PASS del guard de demo sin tocar el estado de release pública 0/6. Entregar backlog de P0 ejecutables con criterios de aceptación y separaciones técnicas/jurídicas.

**No fusionar a main, no publicar puntuaciones nominales, no lanzar CI costosa.** Mantener T011 y T016–T024 pendientes, no declararlos ejecutados. `SUCCESS` técnico solo si tests nativos y suite real pasan con logs, no significa lanzamiento listo ni gate abierto; `PARTIAL` con bloqueos de entorno concretos.
