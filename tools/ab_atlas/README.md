# AB Atlas v0.2 · Grafo universal, AB-P y AB-META

Prototipo offline para investigación, proyectos y combinación de ambos, creado como piloto operativo de AB 3.2.1-O7. **No es un servicio online ni sincroniza GitHub automáticamente.** No hay benchmarking externo de superioridad.

## Uso inmediato

Abra `AB_Atlas_Politics_Fantasy.html` en un navegador moderno. El diseño está destinado a uso real de trabajo: barra de búsqueda, filtros por modo/estado, grafo navegable, plan por fases, dependencias, condiciones críticas de entrega, recibos de ejecución, complaints, aceptación verificable, inspección de nodos e historial. Use **Exportar JSON** para conservar una copia fuera del navegador; la conservación local puede no estar disponible en entornos privados.

Para crear un proyecto nuevo sin programar, pulse **Nuevo** e indique objetivo, audiencia y modo `AB-P`, `AB-H`, `AB-R` o `AB-META`. La creación automática produce solo estructura de propuesta; **no inventa validaciones ni completitud**.

## CLI de cualquier proyecto

Requiere Python 3.10+ (stdlib). El generador es una pieza independiente de GitHub:

```bash
python abmap.py init --name "Mi proyecto" --mode project --outcome "Entregar simulador funcional" --audience "Equipo de investigación" --file mapa.json
python abmap.py add --file mapa.json --title "Interfaz funcional" --kind deliverable --phase build
python abmap.py scan --file mapa.json --root . --limit 100
python abmap.py inspect --file mapa.json --node root --depth 1
python abmap.py summary --file mapa.json
python abmap.py build --file mapa.json --output Mi_Proyecto_Atlas.html
```

La orden `scan` registra archivos como artefactos **sin revisar**. No reconoce resultados científicos ni funcionalidad real mediante lectura superficial de ficheros.

Para control de producto:

```bash
python abmap.py gate --file mapa.json --id privacidad --label "Revisión de privacidad"
python abmap.py gate --file mapa.json --id privacidad --status passed --evidence "informe/security-review.md"
python abmap.py accept --file mapa.json --node ID --criteria "Pasa E2E" --evidence "tests/e2e.log" --verified-by "QA"
python abmap.py status --file mapa.json --node ID --status validated --reason "Criterios comprobados"
python abmap.py scope --file mapa.json --reason "Añadir exportación móvil" --outcome "Nuevo resultado definido"
```

Para complaints y AB-META:

```bash
python abmap.py run --file mapa.json --run-id R01 --activity "Prueba E2E" --status failed
python abmap.py complaint --file mapa.json --run-id R01 --severity major --category UX --description "Flujo bloqueado"
python abmap.py method-change --file mapa.json --decision propose --description "Reducir documentación repetida" --rationale "Sobrecoste observado"
```

**Precaución:** indicar una ruta de evidencia y un verificador no autentica la fuente, y el visor no puede certificar científicamente un resultado. La CLI valida consistencia, no verdad. Los cambios de AB no se adoptan por sí solos.

## Estructura

- `abmap.py` — CLI autónoma con lectura, validación, cambios atómicos y generador de HTML.
- `viewer/template.html` — visor HTML/CSS/JS autónomo sin dependencias externas.
- `examples/politics_fantasy_example.json` — snapshot editorial del repositorio Politics Fantasy, 26/10/2026 (no actualizado en vivo).
- `examples/ab_meta_20_cycles.json` — campañas C01–C20 y autocrítica de AB Atlas.
- `docs/AB_P_MODO_PROYECTOS_V02.md` — contrato y ciclo AB-P específico.
- `research/AB_O7_C01_C20_LEDGER.json` — las 20 fichas A–J y resultados de pruebas.
- `research/INFORME_20_CICLOS.md` — conclusiones, limitaciones y decisión sobre ampliación.
- `tests/test_cycles.py` — 20 comprobaciones de ingeniería C01–C20.
- `tests/test_abmap.py` — tres pruebas heredadas adaptadas al scaffold explícito.
- `tests/test_browser_interactions.py` — cinco pruebas de interacción Chromium/Playwright (dependencia opcional).

## Pruebas

```bash
python -m unittest discover -s tests -p test_cycles.py -v
python -m unittest discover -s tests -p test_abmap.py -v
# Si está instalado playwright y Chromium:
python -m unittest discover -s tests -p test_browser_interactions.py -v
```

Todos los ciclos 01–20 son **pruebas exploratorias dependientes de ingeniería**, no veinte experimentos científicos independientes, ni estudios con usuarios reales. El campo `result` de cada ciclo indica exactamente qué fue observado. Un test PASS no prueba que el método mejore la investigación.

## v0.3 · Actualización incremental de bajo coste para ChatGPT

**Filosofía:** una única fuente de verdad reconstruible, sin hacer que el agente reescriba o relea en cada turno un JSON de miles de nodos. Un mapa canónico inicial (`examples/politics_fantasy_example.json`) más pequeños ficheros append-only en un directorio `atlas_updates/`. Cada fichero representa **un lote de trabajo tras X ciclos**; el usuario no necesita fijar X en la herramienta.

Flujo local:

```bash
# 1. Preparar un lote después de, por ejemplo, cinco ciclos
python atlas_delta.py template --base examples/politics_fantasy_example.json --updates atlas_updates --batch-id 0001-PFL-20261026 --out atlas_updates/0001-PFL-20261026.json
# 2. Editar SOLO las operaciones `ops` de ese lote (nuevos nodos, evidencias, gates, complaints)
# 3. Validar las operaciones sin modificar el baseline
python atlas_delta.py check --base examples/politics_fantasy_example.json --updates atlas_updates
# 4. Generar contexto compacto para el siguiente agente
python atlas_delta.py brief --base examples/politics_fantasy_example.json --updates atlas_updates --out CURRENT_BRIEF.json
# 5. Regenerar HTML únicamente cuando se necesite inspeccionar el mapa actualizado
python atlas_delta.py build --base examples/politics_fantasy_example.json --updates atlas_updates --out Atlas_Actual.html
```

**Importante:** reserve el directorio `atlas_updates/` para lotes JSON. `CURRENT_BRIEF.json` debe estar fuera de él (p. ej. `CURRENT_BRIEF.json`), porque `replay` interpreta cada JSON de ese directorio como un lote y lo validará como tal.

Reglas: identificadores estables, `parent_batch` igual al último lote aplicado, razones explícitas, no convertir una complaint en error demostrado sin revisión, conservar historial y rechazar toda mutación inválida. Rehacer la vista no es requisito de cada ciclo. El campo `state_sha256` verifica el contenido reconstruido; no confirma autenticidad de evidencia.

**Para editar directamente desde ChatGPT conectado a GitHub:** el agente puede incorporar un fichero delta corto por cada lote en `proyectos/politics-fantasy-league/ab_atlas/updates/`, actualizar un resumen `CURRENT.md` de pocas líneas, y hacer commit/PR. No necesita trasladar todo el grafo al prompt. Los patches solo son reproducibles cuando se dispone del baseline y de todos los deltas en orden; el HTML exportado por el navegador no se sincroniza por sí solo con GitHub. Si hay edición simultánea de otros agentes hay que detectar y resolver conflictos de cabecera antes de mezclar.
