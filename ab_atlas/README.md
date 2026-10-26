# AB Atlas en Politics Fantasy

**Listo para uso como piloto de seguimiento.** Modo híbrido AB-H (modo proyectos AB-P + investigación AB-R). Este directorio contiene un estado inicial editorial del 26/10/2026; no se actualiza automáticamente con otras carpetas del repositorio ni con el chat.

## Archivos

- `seed.json`: estado JSON inicial, versionado, con dependencias, seis gates de lanzamiento y nodos de investigación/producto.
- `CURRENT.md`: briefing compacto para ChatGPT, reemplazado al final de cada bloque de trabajo.
- `updates/`: nuevos deltas inmutables, uno por bloque. No reescribir lotes anteriores.
- `AB_Atlas_Politics_Fantasy.html`: visor HTML autónomo con la interfaz profesional aprobada, una fotografía inicial (NO sincronización automática).

La implementación portable y documentación están en [`/ab_atlas/`](../../../ab_atlas/README.md).

## Protocolo económico para ChatGPT

1. Leer `CURRENT.md`, lista de `updates/` y solo el subgrafo de trabajo relevante.
2. Ejecutar los ciclos AB autorizados **adaptativamente uno por uno** y registrar evidencia y bloqueos reales.
3. Tras X ciclos, preparar un pequeño `NNNN-batch.json` con `schema=ab.atlas.delta.v1`, `batch_id` estable, `parent_batch` último, `at`, `actor`, `reason` y solo `ops` nuevos.
4. Crear fichero nuevo desde ChatGPT con GitHub; no pegar todo `seed.json` en el prompt ni reescribir todo el mapa; verificar reproducibilidad/referencias con `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates`.
5. Actualizar `CURRENT.md` con 5–12 próximos nodos y el último lote. Crear PR o commit verificado. Regenerar HTML solo si se desea un snapshot nuevo.

Para ver el mapa actualizado localmente desde la raíz del repo:

```bash
python ab_atlas/atlas_delta.py build --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates --out PFL_Atlas_Actual.html
```

Para inspeccionar solo lo relevante:

```bash
python ab_atlas/atlas_delta.py brief --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates --limit 8
```

**No confundir** estado del nodo, validación científica, aceptación de funcionalidad, porcentaje de madurez del alcance y readiness. No declarar lanzamiento listo si falta uno de los gates críticos. No llamar prueba empírica real a fixtures.
