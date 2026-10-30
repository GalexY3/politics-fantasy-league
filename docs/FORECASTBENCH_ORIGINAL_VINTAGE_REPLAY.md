# PFL — replay bitemporal de versiones públicas originales (C07)

**Solo preguntas y resoluciones públicas de ForecastBench.** No permite puntuar personas políticas reales, recuperar predicciones individuales, replicar un ensayo humano ni afirmar mejora causal. Fuente: Forecasting Research Institute / Karger et al., *ForecastBench*, ICLR 2025. Repositorio público: https://github.com/forecastingresearch/forecastbench-datasets (datos distribuidos con CC BY-SA 4.0; comprobar condiciones específicas antes de redistribuir datos de terceros).

El CLI offline `scripts/replay_forecastbench_vintages.mjs` resuelve un límite de C06: **no basta rechazar una versión futura**; un replay histórico correcto necesita reconstruir exactamente la versión original del fichero de resoluciones que estaba publicada en aquel corte. Las versiones no observadas no cuentan como cero resultados ni permiten rellenarse con el fichero posterior.

## Cortes exactos admitidos

| Instante de evaluación UTC | Commit público original seleccionado | Cohortes con fichero original de preguntas y resoluciones |
|---|---|---|
| `2026-10-08T00:00:00Z` | `4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110` (07/10 07:19:29Z) | 27/09 |
| `2026-10-24T00:00:00Z` | `f3d8a4f83754f6c26990c67c69185f91f214c30c` (23/10 06:53:25Z) | 27/09, 11/10 |
| `2026-10-29T16:00:00Z` | `027ba0b3017a60e0e64602d724284ac6b2d91134` (29/10 07:30:17Z) | 27/09, 11/10 |

**No se admiten otras fechas**, incluso si aparecen cronológicamente entre dos de estos puntos: el repositorio original tiene publicaciones intermedias no incluidas en este manifiesto. Para extender el rango, incorporar el historial completo de versiones y preregistrar sus blobs antes de ejecutar. La limitación surge de la auditoría adversarial [C07](../research/ABH30_NEW_20261029/C07_ADVERSARIAL_INTERMEDIATE_VERSION_NEGATIVE_AND_REPAIR_PREREG.json), no de una simple preferencia de implementación.

## Estructura de archivos locales

Crear una carpeta privada fuera de Git con un subdirectorio de **40 caracteres de commit** por versión. Conservar los bytes originales y no reserializar JSON. Ejemplo:

```text
snapshots/
  4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110/
    question_sets/2026-09-27-llm.json
    resolution_sets/2026-09-27_resolution_set.json
  f3d8a4f83754f6c26990c67c69185f91f214c30c/
    question_sets/2026-09-27-llm.json
    question_sets/2026-10-11-llm.json
    resolution_sets/2026-09-27_resolution_set.json
    resolution_sets/2026-10-11_resolution_set.json
  027ba0b3017a60e0e64602d724284ac6b2d91134/
    question_sets/2026-09-27-llm.json
    question_sets/2026-10-11-llm.json
    resolution_sets/2026-09-27_resolution_set.json
    resolution_sets/2026-10-11_resolution_set.json
```

Los blobs esperados están congelados en [`forecastbench_vintage_replay.mjs`](../src/politics_fantasy/forecastbench_vintage_replay.mjs). El comando calcula su SHA Git **antes** de parsear los archivos. No acepta manifests alternativos ni descarga contenido de Internet.

Desde `proyectos/politics-fantasy-league`:

```bash
node scripts/replay_forecastbench_vintages.mjs --snapshots-dir ./snapshots --from 2026-10-24T00:00:00Z --to 2026-10-29T16:00:00Z
```

Para comparar 8/10 con 29/10, sustituir solo `--from` por `2026-10-08T00:00:00Z`.

El JSON de salida es únicamente agregado: recuentos por cohorte, resultados conocidos en la primera y segunda versión, anteriores conservados, nuevos, desaparecidos y resultados binarios revisados. Los IDs de preguntas se usan solamente en memoria para uniones por `(source,id)`; no salen por pantalla ni se incorporan al repositorio. Brier condicional a desenlace conocido **no es medida de precisión de PFL ni de toda la población de eventos**.

## Evidencia realmente ejecutada y límites

El motor quedó congelado en GitHub y se ejecutó sobre siete archivos públicos originales recuperados por el conector GitHub; los siete SHA Git de **bytes originales completos** coinciden. Los recuentos de la versión del 08/10 son 30 preguntas de mercado admisibles (cohorte 27/09). En 24/10 son 46 (27/09) y 2 (11/10); en 29/10 son 52 y 8. En las tres comparaciones de cohortes idénticas se hallaron **0 pérdidas y 0 cambios de desenlace binario entre los previamente conocidos**. No se ha comprobado cada una de las versiones intermedias.

Se ejecutaron tras el freeze final **25 pruebas Node nativas del motor y 8 pruebas nativas del CLI** sobre fuentes sintéticas temporales deliberadamente no oficiales, con comprobación exacta de hashes del código local frente a GitHub. **El CLI completo no se ha ejecutado con los siete archivos originales en disco local**: esa ruta de éxito sigue pendiente de contrastar en un entorno que tenga los bytes originales. El replay original positivo se realizó en el entorno de acceso a GitHub sobre el **código exacto congelado**, no con el ejecutable Node offline.

Este flujo no prueba autenticidad independiente del editor científico, `first_public_at` para cada fila, disponibilidad previa en mercados externos, derechos para tratar microdatos humanos, asignaciones de tratamientos ni impacto sobre PFL. No hace un despliegue o aumenta las seis puertas de lanzamiento. Los dos intentos reparados (syntax y fechas intermedias) y sus hashes están conservados en el informe [C07](../research/ABH30_NEW_20261029/C07_RUN_RECEIPT.json).

## C08 — Historial completo de publicaciones de ambas rutas (29/10/2026)

El motor importable [`forecastbench_full_history.mjs`](../src/politics_fantasy/forecastbench_full_history.mjs) reconstruye todos los **16 cambios originales** de la ruta de resolución `2026-09-27` y los **3 cambios** de `2026-10-11` consultados en el historial Git de la fuente, hasta `2026-10-29T16:00:00Z`. `versionAt(cohort,asOfInstant)` devuelve la última **versión de archivo Git** conocida en ese instante (o ausencia de fichero), no la primera publicación de una noticia en su mercado. No extrapola a futuro. Los dos ficheros de preguntas originales tienen hashes previamente publicados.

Se verificaron los SHA de los **21 blobs originales** (19 versiones de resoluciones y dos preguntas) y se procesaron datos fuente reales con el validador congelado, encontrando Sep27 30→52 y Oct11 2→8 oportunidades binarias de mercado admisibles y **cero inversiones o pérdidas de las previamente admitidas** en el historial examinado. También se observan **descensos de las filas brutas** de los archivos: no confundir actualización de la fuente con mera anexión de filas. [Informe C08](../research/ABH30_NEW_20261029/C08_REPORT.md) y [recibo con las 19 versiones](../research/ABH30_NEW_20261029/C08_RUN_RECEIPT.json).

**Distinción operativa:** este módulo es todavía un motor puro, **NO modifica el CLI histórico C07 para aceptar todos los cortes**. El CLI documentado arriba sigue limitado a tres checkpoints y mantiene todos sus rechazos. **No se afirma una ejecución nativa del motor C08 sobre los originales en disco**: los 27 tests del nuevo código pasaron en V8 sobre copias del Git blob exacto; los originales se procesaron con conector GitHub y V8 en lotes solapados. La integración positiva nativa y la autenticación de cada archivo en el nuevo CLI siguen pendientes. C08 es un ciclo AB-H limitado, **no** una puerta de lanzamiento superada, intervención humana ni evidencia causal.
