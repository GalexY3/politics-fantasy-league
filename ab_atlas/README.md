> **NUEVO · Atlas de logros · 28/10/2026:** [★ Logros (90)](ACHIEVEMENTS_Atlas_Politics_Fantasy.html) está integrado como quinta vista en [AB Atlas](AB_Atlas_Politics_Fantasy.html), con **10 grandes hitos por cada una de las nueve ramas V4**, medallas por rareza y registro versionado [JSON](ACHIEVEMENTS_REGISTRY.json). Se pueden crear, editar, retirar/restaurar y desbloquear con evidencia verificable mediante importación/exportación JSON. Cambios del navegador = borrador local; GitHub es canónico tras commit. **0/90 otorgados inicialmente**; marcador simbólico **independiente del 36,90 % V4, CT2, VSDS y gates 0/6**. [Política de mantenimiento](ACHIEVEMENTS_README.md) · [validador Python](validate_achievements.py). Sidecar NO altera los lotes Atlas ni repara T010; hay que validar la interfaz en navegador real.

# AB Atlas en Politics Fantasy

**Listo para uso como piloto de seguimiento.** Modo híbrido AB-H (modo proyectos AB-P + investigación AB-R). Este directorio contiene un estado inicial editorial del 26/10/2026; no se actualiza automáticamente con otras carpetas del repositorio ni con el chat.

## Archivos

- `seed.json`: estado JSON inicial, versionado, con dependencias, seis gates de lanzamiento y nodos de investigación/producto.
- `CURRENT.md`: briefing compacto para ChatGPT, reemplazado al final de cada bloque de trabajo.
- `updates/`: nuevos deltas inmutables, uno por bloque. No reescribir lotes anteriores.
- `AB_Atlas_Politics_Fantasy.html`: visor HTML autónomo con la interfaz profesional aprobada, una fotografía inicial (NO sincronización automática).

La implementación portable y documentación están en [`/ab_atlas/`](../tools/ab_atlas/README.md).

## Protocolo económico para ChatGPT

1. Leer `CURRENT.md`, lista de `updates/` y solo el subgrafo de trabajo relevante.
2. Ejecutar los ciclos AB autorizados **adaptativamente uno por uno** y registrar evidencia y bloqueos reales.
3. Tras X ciclos, preparar un pequeño `NNNN-batch.json` con `schema=ab.atlas.delta.v1`, `batch_id` estable, `parent_batch` último, `at`, `actor`, `reason` y solo `ops` nuevos.
4. Crear fichero nuevo desde ChatGPT con GitHub; no pegar todo `seed.json` en el prompt ni reescribir todo el mapa; verificar reproducibilidad/referencias con `python tools/ab_atlas/atlas_delta.py check --base ab_atlas/seed.json --updates ab_atlas/updates`.
5. Actualizar `CURRENT.md` con 5–12 próximos nodos y el último lote. Crear PR o commit verificado. Regenerar HTML solo si se desea un snapshot nuevo.

Para ver el mapa actualizado localmente desde la raíz del repo:

```bash
python tools/ab_atlas/atlas_delta.py build --base ab_atlas/seed.json --updates ab_atlas/updates --out PFL_Atlas_Actual.html
```

Para inspeccionar solo lo relevante:

```bash
python tools/ab_atlas/atlas_delta.py brief --base ab_atlas/seed.json --updates ab_atlas/updates --limit 8
```

**No confundir** estado del nodo, validación científica, aceptación de funcionalidad, porcentaje de madurez del alcance y readiness. No declarar lanzamiento listo si falta uno de los gates críticos. No llamar prueba empírica real a fixtures.
