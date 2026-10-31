# PFL — conciliación de Atlas99 con PROJECT_STATE

**Fecha:** 2026-10-31. **Tipo:** mantenimiento documental, **0 ciclos AB-R / 0 ciclos AB-P**.

El árbol de PR #4 ya contenía un backfill de Atlas99 en el historial, pero `PROJECT_STATE.json` rev16 declaraba 98 lotes y 355 ejecuciones. Antes de alterar el snapshot se ejecutaron, de modo independiente al estado derivado:

```
python tools/ab_atlas/atlas_delta.py check --base ab_atlas/seed.json --updates ab_atlas/updates
python tools/ab_atlas/atlas_delta.py replay --base ab_atlas/seed.json --updates ab_atlas/updates --out ../PFL-replay-check-20261031/atlas_replayed.json
```

Recibo de ejecución local: `OK 99 lotes 63 nodos SHA256 bc4c7b094df4cb95f073a3d41f18c5c362bea80ca6b3ce275ed07593571c46e9`; salida `Reconstruido` en la ruta fuera del repositorio. Un conteo independiente del JSON obtenido devolvió:

| Campo | Replay observado |
| --- | ---: |
| batches | 99 |
| nodes | 63 |
| edges | 81 |
| runs | 362 |
| complaints | 51 |
| passed_gates | 0 |
| state_sha256 | `bc4c7b094df4cb95f073a3d41f18c5c362bea80ca6b3ce275ed07593571c46e9` |

SHA-256 **de los bytes del fichero JSON serializado**: `d79e1b3c3af042283c73648a703324dbeceec33ea01247d577edda744282dbed`. No debe confundirse con el digest canónico de estado de Atlas.

**Corrección realizada:** `PROJECT_STATE.json` rev17 refleja esos valores observados, sin editar `ab_atlas/seed.json`, lotes append-only, resultados, snapshots de campañas ni grados científicos. La sección `latest_validation` conserva su referencia a la validación histórica de Atlas98 y no debe interpretarse como certificación de suites completas sobre esta rama.

**Pendiente:** comprobar `python scripts/project_status.py check`, catálogo y tests pertinentes en este HEAD, y publicar el parche en rama revisable si no surgen errores. No implica aceptación humana de P1 ni publicación del producto.
