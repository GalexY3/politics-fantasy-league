# Mapa de Politics Fantasy

Mapa generado por `python scripts/project_index.py build`. El índice es navegación; **no acredita ejecución ni actualidad científica**. El estado vigente está en [PROJECT_STATE.json](PROJECT_STATE.json).

## Dónde buscar según la tarea

| Quiero… | Entrada |
| --- | --- |
| Continuar o empezar otro chat | [START_HERE](START_HERE.md), [prompt](NEW_CHAT_PROMPT.md) |
| Saber qué falta y qué sigue | [Estado e hitos](PROJECT_STATE.json), [handoff](HANDOFF.md) |
| Entender el juego local | [Servidor](src/politics_fantasy/server.py), [lógica y BD](src/politics_fantasy/product.py), [interfaz](src/politics_fantasy/web/app.js) |
| Revisar datos, identidades y cuarentena | [Ingesta](src/politics_fantasy/ingest.py), [almacén](src/politics_fantasy/secure_store.py), [cuarentena](src/politics_fantasy/quarantine_ingest.py) |
| Encontrar una pregunta o una campaña | [Índice de investigación](research/INDEX.md) |
| Encontrar tests y comandos de QA | [Tests](tests/), [runner Node](scripts/run_node_tests.mjs), [pyproject](pyproject.toml) |
| Distinguir los tres mapas | [Atlas](ab_atlas/README.md), [O7](research/ABH5B_INCENTIVE_FORMAL_20261029/O7_CAUSAL_GRAPH.json), [logros](ab_atlas/ACHIEVEMENTS_README.md) |
| Localizar un expediente Txxx | [Cola](tareas_codex/README.md), [backlog](tareas_codex/BACKLOG.json) |
| Saber qué rama contiene el trabajo | [Ramas](BRANCHES.json) |
| Revisar la incorporación a main | [Revisión del código](docs/MAIN_REVIEW_20261030.md), [integración](research/INTEGRATION_20261030/REPORT.md) |

## Buscar sin leer todo el historial

```sh
python scripts/project_index.py find T005
python scripts/project_index.py find recibos
python scripts/project_index.py find forecastbench --category experimental_code
python scripts/project_index.py check
```

El catálogo completo está en [PROJECT_INDEX.json](PROJECT_INDEX.json). Solo lista archivos versionados; no explora carpetas privadas locales.

## Responsabilidad de las carpetas

| Categoría | Archivos | Uso |
| --- | ---: | --- |
| `archive` | 6 | Documentación histórica conservada |
| `atlas` | 112 | Grafo Atlas, logros y sincronización |
| `atlas_engine` | 12 | Motor Atlas fijado y sus pruebas; procedencia en UPSTREAM.json |
| `continuity` | 8 | Estado vigente, objetivos e inicio de conversación |
| `data` | 29 | Datos/fixtures versionados y metadatos; no datos locales privados |
| `evidence` | 378 | Recibos, originales conservados y copias históricas; no código activo |
| `experimental_code` | 30 | Instrumentos experimentales; su presencia no prueba integración en el juego |
| `operations` | 103 | Herramientas, configuración y operación local |
| `reference` | 82 | Manuales, contratos y referencias |
| `research` | 1975 | Preguntas, campañas, análisis y resultados de investigación |
| `runtime` | 102 | Aplicación, reglas y almacenamiento del prototipo |
| `task_queue` | 120 | Expedientes y resultados de ejecución |
| `verification` | 232 | Pruebas y ejecutores de comprobación |

## Dónde guardar trabajo nuevo

- Funcionalidad activa en `src/politics_fantasy/`; pruebas ejecutables en `tests/`. Los módulos experimentales se identifican en el catálogo y no se consideran conectados a la app por estar en src.
- Manuales mantenidos en `docs/`; decisiones e hitos actuales en `PROJECT_STATE.json`. Evitar duplicar el estado en nuevos documentos fechados.
- Investigación nueva bajo `research/<pregunta>/`, con subcarpetas de campaña/ejecución y sus contratos; mantener separados fuente, análisis, resultado y evidencia. Los directorios históricos conservan sus rutas y IDs.
- Capturas privadas o nominales en las rutas locales excluidas de Git. Nunca convertir el catálogo en un inventario público de esas capturas.
- Evidencias inmutables conservan bytes, hashes y commit. No moverlas para que el árbol parezca más limpio ni usarlas como código activo.
- Tras añadir, renombrar o retirar archivos versionados: preparar el cambio en Git, regenerar índice y ejecutar `check`. Un índice antiguo debe fallar de forma visible.
