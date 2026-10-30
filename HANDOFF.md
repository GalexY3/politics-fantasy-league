# PFL · briefing derivado

Rama: `main`; HEAD: `b94dc649bd983fcc66e2030ee5bf0bc6e930716a`.
Estado rev. 6; publicación declarada: STANDALONE_MIGRATION_QA_IN_PROGRESS.
Código revisado incluido en refs/heads/main: True (referencia local; hacer fetch).

Atlas: 93 lotes; SHA `7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d`; gates 0/6.
Autorización ABH10: 5/10 ejecutados; 5 disponibles, preservados bajo R5. Históricos separados: 2.

## product
- P0-INTEGRATION [DONE]: Una base técnica y de evidencia reunida y revisable. Siguiente: Integración incorporada; el siguiente hito de producto es P1-ACCOUNTS con datos ficticios
- P1-ACCOUNTS [QUEUED]: Usuarios y permisos aislados en el prototipo ficticio. Siguiente: Definir y ejecutar una implementación local mínima con pruebas de aislamiento, sin personas políticas reales
- P2-PLAYABLE-FLOW [QUEUED]: Flujo ficticio completo usable y persistente. Siguiente: Tras P1, verificar un recorrido de usuario completo y corregir fricciones observadas
- P-CONTINUITY [DONE]: Continuidad verificable entre conversaciones sin copiar un resumen que caduque. Siguiente: Cada nueva sesión lee START_HERE y cada cierre guarda estado y handoff
- P-ORGANIZATION [DONE]: Mapa por tareas, catálogo buscable e índice de investigaciones mantenidos con Git. Siguiente: Regenerar catálogo al cambiar rutas versionadas; conservar la trazabilidad de los archivos históricos
- P-MIGRATION [IN_PROGRESS]: Proyecto independiente de AB con historia y herramientas reproducibles. Siguiente: Completar QA y publicar destino antes del corte de AB

## research
- R0-FEASIBLE-QUESTION [IN_PROGRESS]: Una pregunta sociológica delimitada con evidencia accesible y falsador. Siguiente: Una sesión acotada para seleccionar entre feedback humano, respuesta institucional u otro mecanismo formal claramente etiquetado; no repetir C37 sin artefacto nuevo
- R1-DISCRIMINATING-RESULT [QUEUED]: Resultado que cambie una hipótesis social o institucional frente a un rival. Siguiente: Ejecutar el contrato de la pregunta elegida con el presupuesto autorizado aplicable; preservar exposición previa
- R-AEA-C37 [PARKED]: Acceso al registro original e historial del ensayo AEARCTR-0000981. Siguiente: No repetir búsquedas equivalentes
- R-T005 [PARKED]: Originales y condiciones de uso suficientes para una pieza concreta de T005. Siguiente: Reabrir solo la pieza para la que haya evidencia nueva

## Última validación declarada
Baseline AB: 820 Python/511 Node/38 Atlas PASS. Standalone paths, commit resolution and declared dependencies changed; complete standalone QA is pending.

Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.

Consistencia: PASS
Huella código/tests: `5f4ae080600c8280b1fab1f548d63e8635081c904a0601089795d04ed94abd61`.
No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.
