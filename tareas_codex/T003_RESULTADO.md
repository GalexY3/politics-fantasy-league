# T003 · Paridad nativa V3/V4

**Resultado: COMPLETADA_VERIFICADA, comprobación local delimitada.** Baseline: `6e359a89e74f06927e51ca4dc8a9ea1714e37acd` en la rama `research/pfl-codex-contributions-20261027`; Python 3.12.14 y Node 24.16.0 en Windows. La ejecución T002 registró inicialmente un fallo Node relacionado y se conservó ese negativo abajo. Los cambios de T003 se prepararon después del baseline, sobre ese árbol.

## Entradas y fuentes

Hashes SHA-256 de bytes de los archivos locales utilizados (las rutas son relativas a `proyectos/politics-fantasy-league`):

| Archivo | Bytes | SHA-256 |
| --- | ---: | --- |
| `product/progress_scope_v3_20261026.json` | 16830 | `4ffc447ccba7b030a0bfad0a0ae70e3a4cbff2d87604531dcef9e1d424db737e` |
| `product/progress_scope_v4_20261027.json` | 17818 | `15199b5fa2b24aacd5776902437b2b5aac19038281f95d5d89a4c1bd533c244f` |
| `src/politics_fantasy/progress_api.py` | 6472 | `3900e82b08dba370a2d4fe99068f85c5c4d2ee17ac2985bbb60e89b1b6cee594` |
| `src/politics_fantasy/progress_model.mjs`, tras corrección | 6926 | `1546965fc3de48f84ee670523e0236ed1659ba9e2c5a65279623a1b01114d563` |
| `tests/test_progress_cross_runtime.py` | — | `9f77b4547a05d69b80529b2435d633bec9077d33171d72e09dfee4a18ce4ada6` |
| `tests/test_progress_cross_runtime.mjs` | 2847 | `f50a3b4e1d86b31173d4c2c14fd375e5c59c03954ee03dcf383f8436b0f61350` |

## Ejecución y resultado

Desde `C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league`, con `PYTHONPATH=src` y `PYTHONDONTWRITEBYTECODE=1`:

```text
C:\Users\Nitropc\AppData\Local\Temp\pfl-cdx08-20261027\Scripts\python.exe -m pytest -q tests/test_progress_cross_runtime.py tests/test_progress_api.py tests/test_progress_contract_failclosed.py
21 passed in 0.25s; exit 0

node --test tests/test_progress_cross_runtime.mjs tests/test_progress_model.mjs tests/test_progress_revision_v4.mjs tests/test_progress_contract_failclosed.mjs
36 passed; 0 failed; 0 skipped; exit 0
```

El test Python carga los dos JSON completos, invoca el evaluador real Node en un proceso hijo y compara los campos equivalentes, incluidos todos los tracks, hitos, pesos, unidades, contribuciones, bloqueos y estado global, con tolerancia absoluta `1e-9` para números. Node ejecuta además su evaluador y `compare` nativos. Resultado: V3 **36,35 %**, V4 **36,90 %**, **+0,55 pp** de trabajo, efecto de alcance 0; nueve líneas y 36 hitos en ambas; solo `id.real` y `ev.person` cambian de nivel 0 a 1; seis bloqueos y `real_people_scoring_ready=false` en ambas. Las negativas ejecutadas en ambos runtimes comprueban rechazo de `NaN` y bloqueo si falta un hito crítico.

No todos los atributos descriptivos son idénticos: Python incluye `ok`, JavaScript incluye `method` y los textos `scope_change_notice` difieren. El test contrasta los campos semánticamente equivalentes especificados, no afirma igualdad byte a byte de las respuestas ni ignora diferencias de pesos o datos.

## Negativo conservado y reparación

En el baseline T002, la prueba Node preexistente `wrong scope identity cannot be compared` falló: `compare` rechazaba la familia ajena mediante `BAD_SCOPE_VERSION` antes de llegar a la comprobación de linaje esperada por el test, `SCOPE_LINEAGE_MISMATCH`. Ambas respuestas rechazaban el alcance; no se observó una aceptación indebida. Se adelantó exclusivamente la detección de dos IDs de alcance distintos; si los IDs coinciden, ambos ámbitos siguen pasando por validación completa. La nueva regresión también verifica que dos ámbitos de la misma familia no admitida se rechazan con `BAD_SCOPE_VERSION`.

La ficha T003 y la prueba que falló ya estaban versionadas antes de ejecutar el baseline; no se congeló un prerregistro específico adicional para esta corrección después de descubrir el fallo. Se registra como reparación post hoc, no como ciclo AB independiente.

La paridad del indicador contractual no demuestra validez externa, precisión política ni preparación de lanzamiento. Los resultados de la suite completa posterior deben consultarse en T002, sin deducirlos de esta ejecución focalizada.
