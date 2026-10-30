# PFL · briefing derivado

Rama: `codex/pfl-pr2-review`; HEAD: `9d5603ea1cb023f1c7edd6f1036cc2b8a731cd8e`.
Estado rev. 9; publicación declarada: PR2_REVIEW_ON_CURRENT_MAIN.
Código revisado incluido en refs/remotes/origin/main: True (referencia local; hacer fetch).

Atlas: 94 lotes; SHA `ac64213f1901a0e07832083a0c6afbe8ddf02097a2d2a83556a94fc77a10ae8a`; gates 0/6.
Autorización ABH10: 6/10 ejecutados; 4 disponibles, preservados bajo R5. Históricos separados: 2.

## Último trabajo de origen migrado (AB PR81)
P1 GitHub Actions #40995507812: 35 Python tests PASS y node --check, dos cuentas y clubes separados. R1 C38 GitHub Actions #40996183394: 8/8 tests Python y 4170 registros originales, diferencia documentacion −29,08 p.p. Atlas94 original Python #40996696957: 94 lotes, SHA ac64213f..., nodes63 edges81.
Pruebas históricas de AB; no sustituyen QA sobre el nuevo commit.

## Estado del corte de repositorios
DRAFT_PENDING_INDEPENDENT_LINUX_QA; origen: PR #81 (d725a8dff37429a035b6e1ffb27c3568e51322ce); rama de revisión: migration/pfl-final-cutover-20261030. Consultar status del traslado y recibo de incorporación antes de continuar.

Concesión nueva INDEPENDIENTE PFL-GRANT-20261030-INTEGRATION10: 0/10 ejecutados; 10 disponibles. No reasignar saldo ABH10.

## product
- P0-INTEGRATION [DONE]: Una base técnica y de evidencia reunida y revisable. Siguiente: Integración incorporada; el siguiente hito de producto es P1-ACCOUNTS con datos ficticios
- P1-ACCOUNTS [READY_REVIEW]: Cuentas y sesiones locales con clubes ficticios aislados por cuenta; sin despliegue público. Siguiente: Revisión visual humana de dos perfiles en navegador y confirmación de aceptación; después P2 flujo jornada
- P2-PLAYABLE-FLOW [QUEUED]: Flujo ficticio completo usable y persistente. Siguiente: Tras aceptación humana P1, comprobar acceso→club→alineación→jornada ficticia→resultado en navegador con persistencia/reinicio.
- P-CONTINUITY [DONE]: Continuidad verificable entre conversaciones sin copiar un resumen que caduque. Siguiente: Cada nueva sesión lee START_HERE y cada cierre guarda estado y handoff
- P-ORGANIZATION [DONE]: Mapa por tareas, catálogo buscable e índice de investigaciones mantenidos con Git. Siguiente: Regenerar catálogo al cambiar rutas versionadas; conservar la trazabilidad de los archivos históricos
- P-MIGRATION [DONE]: Proyecto independiente de AB con historia y herramientas reproducibles. Siguiente: Continuar P1-ACCOUNTS en este repositorio; adoptar cambios de AB solo explícitamente

## research
- R0-FEASIBLE-QUESTION [READY_REVIEW]: Pregunta institucional delimitada frente a rutas de rank humano e incentivos, con datos públicos originales accesibles y licencia abierta. Siguiente: Revisar el resultado C38 importado y sus fuentes; al validar el commit independiente decidir aceptación científica y el siguiente contraste.
- R1-DISCRIMINATING-RESULT [READY_REVIEW]: Negativo observacional C38 preregistrado: diferencia high−low −29,08 pp en documentación CSV, 3 de 4 años comparables con signo contrario. Siguiente: Revisión del investigador; si interesa validar interpretación sustantiva, obtener actas oficiales fechadas de comisiones y auditar decisión no consignada, no más umbrales arbitrarios
- R-AEA-C37 [PARKED]: Acceso al registro original e historial del ensayo AEARCTR-0000981. Siguiente: No repetir búsquedas equivalentes
- R-T005 [PARKED]: Originales y condiciones de uso suficientes para una pieza concreta de T005. Siguiente: Reabrir solo la pieza para la que haya evidencia nueva

## Última validación declarada
Linux limpio: 822 Python +32 subtests, 511 Node y 38 Atlas +104 subtests PASS, cero fallos/skips. Instalación .[test], catálogo, continuidad, logros y replay PASS. Atlas93 sin cambios.

Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.

Consistencia: PASS
Huella código/tests: `6389f0bc8dff3da59c951766d1d10a2cd385e69f468f18cb4a2d6809f4fcbd8f`.
No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.
