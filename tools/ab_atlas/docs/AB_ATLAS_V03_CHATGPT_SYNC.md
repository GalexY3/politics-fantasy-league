# AB Atlas 0.3 — Contrato de sincronización de bajo coste

Estado: prototipo portable validado estructuralmente, sin sincronización online automática.

## Principios

1. **Lote después de X ciclos:** la agencia de investigación se conserva; cada ciclo A–J decide el siguiente. No se confunde `commit de cierre de lote` con evidencia científica nueva.
2. **Write delta, not full graph:** cada cambio se añade como operación compacta con IDs estables; los cambios simultáneos sobre el mismo elemento deben rechazarse/reconciliarse, no machacarse.
3. **Low-context retrieval:** abrir primero CURRENT.md o un brief de proyecto (objetivos, 5–12 próximos nodos, gates, blockers, incidencias y última revisión). Abrir evidencias enlazadas solo si la decisión lo requiere.
4. **Event sourcing y checkpoints:** baseline versionado + lotes JSON ordenados. Al alcanzar muchos deltas, almacenar snapshot/checkpoint reproducible, dejando archivo inmutable de historia; no borrar cambios negativos.
5. **Costo y juicio epistémico:** no forzar auditoría pesada para tareas triviales. Investigación AB-R y AB-META conserva falsadores, preregistros y límites; AB-P exige entregables aceptados y gates separados de índices de progreso.
6. **Método revocable:** AB-META puede proponer, comparar, aceptar bajo supervisión y revertir cambios. Una variante no es mejor por haber sido adoptada.

## Archivo compacto de cambios

Ejemplo (JSON):

```json
{
  "schema": "ab.atlas.delta.v1",
  "batch_id": "0001-PFL-20261026",
  "parent_batch": "",
  "at": "2026-10-26T20:00:00+00:00",
  "actor": "chatgpt",
  "reason": "Fin del bloque AB, evidencias registradas",
  "ops": [
    {"op":"node.add", "node":{"id":"PFL-0001","title":"Auditar identidad multifuente","kind":"task","mode":"project","status":"blocked"}},
    {"op":"run.add", "run":{"id":"PFL-R001","activity":"Intento de obtener registro real","status":"stopped"}},
    {"op":"complaint.add", "complaint":{"id":"PFL-Q001","run_id":"PFL-R001","description":"No hay fuente primaria verificable","severity":"major"}}
  ]
}
```

La categoría `complaint` registra observaciones críticas; no equivale automáticamente a un error confirmado ni permite declarar falsedad de la fuente. Las demostraciones de ejemplo se marcan como tales, no como resultados reales.

## Secuencia obligatoria en cada bloque

- Antes: leer resumen compacto y último lote; revisar bloqueos y preguntas críticas sin resolver.
- Durante: decidir el próximo ciclo según la última evidencia; anotar pruebas, negativos, costes y nuevas ramas.
- Al final: añadir un delta, validar su estructura/referencias con replay, generar brief y, cuando exista acceso, PR/merge respetando conflicto de rama. No reescribir un nodo histórico silenciosamente.
- Reportar: ciclos realmente ejecutados, disponibles por autorización, calidad de evidencia, cambios AB-P, gates de producto y complaints abiertas. Si el entorno no permite actualizar el repositorio, entregar patch local y declararlo.

## Validación de eficacia pendiente

Medir costo de tokens y tiempo real de reanudación, ramas olvidadas, colisiones, reversión y recuperación frente a un gestor profesional de proyectos. La estructura compacta **debería** reducir transferencia redundante; esto sigue sin ser una mejora cuantificada experimentalmente.
