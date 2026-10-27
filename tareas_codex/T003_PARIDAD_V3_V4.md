# T003 · Paridad nativa de progreso V3/V4 entre Python y JavaScript

**Prioridad P1 · Estado PENDIENTE · No ejecutada por Codex.** [Volver al índice](README.md).

## Antecedente y falsador

**C44** confirmó aritméticamente, desde los dos JSON originales del repo, que V3 = **36,35 %** y V4 = **36,90 %** sobre nueve líneas, 36 hitos; en V4 solo suben `id.real` y `ev.person` (de nivel 0 a 1). Los seis gates siguen bloqueados. Pero **NO se ejecutó ambos evaluadores nativos contra esos documentos completos**. Antes, C33–C34 unificaron casos sintéticos de contrato (Python 15 PASS + Node 9 PASS). Esta tarea evita presentar esa combinación como una validación integral de los snapshots.

## Instrumentos ya versionados

- `product/progress_scope_v3_20261026.json`
- `product/progress_scope_v4_20261027.json`
- `src/politics_fantasy/progress_api.py` → `evaluate_scope(...)`.
- `src/politics_fantasy/progress_model.mjs` → `evaluate(...)`.
- `tests/test_progress_api.py`, `tests/test_progress_revision_v4.mjs` y `tests/test_progress_contract_failclosed.py/.mjs`.

## Plan ejecutable

En checkout íntegro y HEAD documentado, leer ambas APIs para identificar las **claves reales** de los resultados (no adivinarlas). Crear o ejecutar un test de paridad que lea los mismos dos JSON de disco y compare sus campos semánticamente equivalentes, tras normalizar únicamente formatos de representación (por ejemplo, redondeo) **sin cambiar datos, pesos ni hitos**.

Comprobar explícitamente: V3 **36,35 %**; V4 **36,90 %**; efecto trabajo **+0,55 puntos porcentuales**; 9 tracks, 36 hitos en cada versión; cambio de nivel solo en los dos IDs documentados; **seis bloqueos de lanzamiento** en ambas salidas. Registrar bytes/hash de ambos JSON y fuente exacta de cada evaluador. Usar **ambos runtimes reales** (no recálculo manual JS como sustituto) y ejecutar al menos una negativa de gate crítico faltante y una de `NaN`.

## Aceptación y límites

- Test de paridad reproducible y versionado; logs nativos **Python y Node** con exit code 0.
- Si las APIs difieren, dejar **resultado rojo** con un contraejemplo mínimo antes de cambiar código. No modificar V4 para hacer pasar el test.
- Si se actualiza un evaluador, incluir nueva regresión sin romper T002.
- Paridad y porcentaje contractual **no son validación externa del producto, inferencia política ni justificación de release**.

**Entregable:** `T003_RESULTADO.md`, script/test nuevo y reproducción. No marcar completado solo por la auditoría C44.
