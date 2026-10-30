# PFL · briefing derivado

Rama: `main`; HEAD: `70de73612b140b827bf28d88df6800bf8e1e0b28`.
Estado rev. 7; publicación declarada: STANDALONE_QA_PASS_CUTOVER_PENDING.
Código revisado incluido en refs/heads/main: True (referencia local; hacer fetch).

Atlas: 93 lotes; SHA `7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d`; gates 0/6.
Autorización ABH10: 5/10 ejecutados; 5 disponibles, preservados bajo R5. Históricos separados: 2.

## product
- P0-INTEGRATION [DONE]: Una base técnica y de evidencia reunida y revisable. Siguiente: Integración incorporada; el siguiente hito de producto es P1-ACCOUNTS con datos ficticios
- P1-ACCOUNTS [QUEUED]: Usuarios y permisos aislados en el prototipo ficticio. Siguiente: Definir y ejecutar una implementación local mínima con pruebas de aislamiento, sin personas políticas reales
- P2-PLAYABLE-FLOW [QUEUED]: Flujo ficticio completo usable y persistente. Siguiente: Tras P1, verificar un recorrido de usuario completo y corregir fricciones observadas
- P-CONTINUITY [DONE]: Continuidad verificable entre conversaciones sin copiar un resumen que caduque. Siguiente: Cada nueva sesión lee START_HERE y cada cierre guarda estado y handoff
- P-ORGANIZATION [DONE]: Mapa por tareas, catálogo buscable e índice de investigaciones mantenidos con Git. Siguiente: Regenerar catálogo al cambiar rutas versionadas; conservar la trazabilidad de los archivos históricos
- P-MIGRATION [READY_REVIEW]: Proyecto independiente de AB con historia y herramientas reproducibles. Siguiente: Publicar y comprobar destino; retirar copia activa de AB con redirecciones

## research
- R0-FEASIBLE-QUESTION [IN_PROGRESS]: Una pregunta sociológica delimitada con evidencia accesible y falsador. Siguiente: Una sesión acotada para seleccionar entre feedback humano, respuesta institucional u otro mecanismo formal claramente etiquetado; no repetir C37 sin artefacto nuevo
- R1-DISCRIMINATING-RESULT [QUEUED]: Resultado que cambie una hipótesis social o institucional frente a un rival. Siguiente: Ejecutar el contrato de la pregunta elegida con el presupuesto autorizado aplicable; preservar exposición previa
- R-AEA-C37 [PARKED]: Acceso al registro original e historial del ensayo AEARCTR-0000981. Siguiente: No repetir búsquedas equivalentes
- R-T005 [PARKED]: Originales y condiciones de uso suficientes para una pieza concreta de T005. Siguiente: Reabrir solo la pieza para la que haya evidencia nueva

## Última validación declarada
Linux limpio: 822 Python +32 subtests, 511 Node y 38 Atlas +104 subtests PASS, cero fallos/skips. Instalación .[test], catálogo, continuidad, logros y replay PASS. Atlas93 sin cambios.

Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.

Consistencia: PASS
Huella código/tests: `5f4ae080600c8280b1fab1f548d63e8635081c904a0601089795d04ed94abd61`.
No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.
