# PFL · briefing derivado

Rama: `integration/pfl`; HEAD: `a4a730f3962edc0703ab0be8c3901a309366e7b6`.
Estado rev. 2; integración pendiente de revisión según GitHub.

Atlas: 93 lotes; SHA `7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d`; gates 0/6.
Autorización ABH10: 5/10 ejecutados; 5 disponibles, preservados bajo R5. Históricos separados: 2.

## product
- P0-INTEGRATION [READY_REVIEW]: Una base técnica y de evidencia reunida y revisable. Siguiente: Revisar PR80 para main; la base operativa estable integration/pfl ya está disponible para continuar
- P1-ACCOUNTS [QUEUED]: Usuarios y permisos aislados en el prototipo ficticio. Siguiente: Definir y ejecutar una implementación local mínima con pruebas de aislamiento, sin personas políticas reales
- P2-PLAYABLE-FLOW [QUEUED]: Flujo ficticio completo usable y persistente. Siguiente: Tras P1, verificar un recorrido de usuario completo y corregir fricciones observadas
- P-CONTINUITY [DONE]: Continuidad verificable entre conversaciones sin copiar un resumen que caduque. Siguiente: Cada nueva sesión lee START_HERE y cada cierre guarda estado y handoff

## research
- R0-FEASIBLE-QUESTION [IN_PROGRESS]: Una pregunta sociológica delimitada con evidencia accesible y falsador. Siguiente: Una sesión acotada para seleccionar entre feedback humano, respuesta institucional u otro mecanismo formal claramente etiquetado; no repetir C37 sin artefacto nuevo
- R1-DISCRIMINATING-RESULT [QUEUED]: Resultado que cambie una hipótesis social o institucional frente a un rival. Siguiente: Ejecutar el contrato de la pregunta elegida con el presupuesto autorizado aplicable; preservar exposición previa
- R-AEA-C37 [PARKED]: Acceso al registro original e historial del ensayo AEARCTR-0000981. Siguiente: No repetir búsquedas equivalentes
- R-T005 [PARKED]: Originales y condiciones de uso suficientes para una pieza concreta de T005. Siguiente: Reabrir solo la pieza para la que haya evidencia nueva

## Última validación declarada
Linux Alpine/QEMU, checkout limpio a4a730f3: 806 Python +32 subtests PASS; 508 Node PASS; 38 Atlas +104 subtests PASS; replay93, continuidad y logros v6 PASS; cero fallos/omisiones. Documentación posterior solo registra los resultados.

Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.

Consistencia: PASS
Huella código/tests: `745e33df79698d92aa86442abaf5838a35441c03ed4c782af1683d3aa4f33727`.
No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.
