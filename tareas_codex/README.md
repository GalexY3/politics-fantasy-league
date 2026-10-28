> **ESTADO VIGENTE · 28/10/2026:** T008 **COMPLETADA_VERIFICADA exclusivamente en checkout `b0344d1`** (651 PASS, 28 subtests PASS) y Atlas **35** comprobado por separado en `9d0ef84`. [Informe histórico](T008_RESULTADO.md) · [conciliación](T008_RECONCILIACION_MAIN_20261028.md). **T009 PENDIENTE:** HEAD actual de `main`, 62 deltas y suite completa, [contrato](T009_MAIN_LINUX_ATLAS60.md). Cambios C07: extras `test`/`research` requieren `tzdata` también en Linux, sin haberse instalado limpiamente como parte de T009. MAIN20B: **7 válidos y 13 disponibles**. Estado canónico [CURRENT](../ab_atlas/CURRENT.md).

> **Conciliación confirmada (28/10/2026):** T008 **COMPLETADA_VERIFICADA en `b0344d1`** (Alpine QEMU Linux: 651 Python PASS + 28 subtests PASS sin fallos ni omisiones). [Informe histórico](T008_RESULTADO.md) · [salida original](T008_POSIX_FINAL_STDOUT.txt) · [reconciliación contra main](T008_RECONCILIACION_MAIN_20261028.md). Atlas **35 lotes** comprobado en `9d0ef84`. La suite integral y Atlas **60 lotes** del `main` posterior siguen sin comprobar: tarea **[T009](T009_MAIN_LINUX_ATLAS60.md) PENDIENTE**. No sobrescribir archivos fuente posteriores ni importar ramas históricas en bloque. La campaña MAIN20B conserva 15 autorizaciones.

> **REFERENCIA ACTUAL MAIN20B · 28/10/2026:** usar `main`, `T008` sigue `PENDIENTE`; [Atlas **60 lotes**](../ab_atlas/CURRENT.md), full Python POSIX y checker nativo `NOT_RUN`. MAIN20B tiene **5 válidos y 15 autorizados disponibles**; BRANCH20 anterior está cerrado por separado. El contrato vigente está en [T008](T008_SUITE_COMPLETA_POSIX.md). Incorporar pruebas de fechas Atlas C01, mayoría estricta C04 y bootstrap por registros C05; mantener sin activar scoring real ni CI costosa.

# Cola de Codex · Politics Fantasy League

**Estado vigente, 28/10/2026: Codex no disponible temporalmente.** Ninguna tarea está ejecutándose en segundo plano. Usar exclusivamente `main` como referencia al retomar. La campaña [AB-H BRANCH20](../research/ABH_BRANCH20_20261028/FINAL_REPORT.md) está **CERRADA: 19 ciclos válidos + C01 inválido, cero pendientes**. El [estado Atlas](../ab_atlas/CURRENT.md) alcanza **55 lotes documentales** y el **replay canónico de 55 está PENDIENTE**, al igual que la suite global Python Linux/POSIX.

La tarea prioritaria P0 es **[T008 · suite Python íntegra POSIX + Atlas55](T008_SUITE_COMPLETA_POSIX.md)**. Sus criterios, comandos, baselines y precauciones están centralizados en esa ficha. El índice de estados consumible por herramientas es [BACKLOG.json](BACKLOG.json), que se comprobará al iniciar la ejecución, sin asumir HEAD antiguo.

| Expediente | Estado histórico actual | Qué falta |
|---|---|---|
| [T001](T001_RESULTADO.md) | COMPLETADA_VERIFICADA | Revalidación solo al ampliar Atlas |
| [T002](T002_RESULTADO.md) | COMPLETADA_CON_FALLOS | Python Windows 57 FAIL, 558 PASS, 28 SKIP: comparar con POSIX completo |
| [T003](T003_RESULTADO.md) | COMPLETADA_VERIFICADA | Paridad V3/V4 en snapshot anterior |
| [T004](T004_RESULTADO.md) | COMPLETADA_CON_FALLOS | Distinguir plataforma y defectos POSIX en suite global |
| [T005](T005_ORIGINALES_CONDICIONALES.md) | BLOQUEADA | Nuevos originales institucionales legítimos, derechos y autorización específica |
| [T006](T006_RESULTADO.md) | COMPLETADA_VERIFICADA | Contratos HTTP/CVE de snapshot anterior |
| [T007](T007_RESULTADO.md) | COMPLETADA_VERIFICADA | Checker 31 lotes histórico, no 55 |
| [T008](T008_SUITE_COMPLETA_POSIX.md) | PENDIENTE | Checkout `main`, full Python Linux, checker Python Atlas55, regresiones recientes y logs |

T008 debe incluir las regresiones añadidas durante BRANCH20: comparador secundario de votaciones C03, reglas de scoring ficticio C04, pluralidad/mayoría C07, portada C08, exposición futura C09, módulos recuperados C10/C12/C15 y duplicados JSON C17, interoperabilidad C18. **No** contar las 35 pruebas focalizadas C18 ni las 89 históricas CONT80 como suite global.

**Incidencia C19 abierta:** el preflight de lotes Atlas no exige una fecha `at` válida y con zona; no declarar solucionada por obtener un código de salida positivo en otra versión. [Evidencia](../research/ABH_BRANCH20_20261028/C19_RESULT.json).

Antes de operar: leer [AGENTS.md](../../../AGENTS.md), [CURRENT](../ab_atlas/CURRENT.md), [cierre BRANCH20](../research/ABH_BRANCH20_20261028/FINAL_REPORT.md) y [T008](T008_SUITE_COMPLETA_POSIX.md). Comprobar `git status`, rama y HEAD. La ejecución de una ficha no es por sí sola un ciclo AB A–J. Sin CI costosa, puntuación real, originales privados nominales, publicación multiusuario ni fusiones masivas. Se necesita autorización nueva del usuario para más ciclos AB.
