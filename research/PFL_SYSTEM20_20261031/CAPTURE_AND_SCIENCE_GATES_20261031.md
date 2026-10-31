# PFL SYSTEM20 — evidencias obtenidas y límites del primer corte

**Fecha:** 31-10-2026. **Modo:** ingesta y QA de infraestructura, sin ciclo AB-R/AB-P contabilizado ni outcomes científicos preinscritos.

## Originales españoles efectivamente capturados

Dos GET oficiales desde descargas.interior.gob.es a distribuciones del catálogo de resultados electorales del Ministerio del Interior [datos.gob.es](https://datos.gob.es/es/catalogo/e00003801-resultados-electorales), que asigna **CC BY 4.0** a estas distribuciones. Sin intervención en sesiones de terceros ni aceptación mediante formularios. Bytes fuera de Git; datos de personas no publicados.

**Exploración posterior de los dos originales:** [informe y recibos](INTERIOR_METADATA/REPORT.md). La cabecera de ambos archivos no estaba en la fila 1 sino en la fila 4, con 8 y 57 columnas respectivamente. Antes de inspeccionar valores de filas, se congelaron lector, tests y política de selección no-outcome. Se procesaron únicamente metadatos administrativos: **5.600 filas del fichero de cargos y 6.203 del de resultados**, entre **1977 y 2023**, con **15 años electorales distintos**. Todas las filas tenían año identificable y no hubo missing en las columnas seleccionadas A–E y A–C, sin que ello diga nada de las demás columnas. En cargos, 832 claves fecha/elección/provincia distintas y 4.768 colisiones (varios registros por territorio; **no** se consideran duplicados de filas). En resultados, la deduplicación no pudo estimarse con esos metadatos restringidos. Los valores de votos, escaños, partidos y personas no se extrajeron. `scripts/replay_interior_metadata.py` reprodujo independientemente los mismos agregados desde los XLSX originales, con salida fuera de Git y sin red. **No** equivale a un estudio de instituciones parlamentarias.

| Distribución | Bytes | SHA-256 verificado | Cabecera Last-Modified observada |
| --- | ---: | --- | --- |
| Elecciones-Congreso-cargos-electos.xlsx | 326847 | cafc4e0f3fc53f01d1370dd47ac841c6cad43a5394e8a8d1afe2495897fbdad4 | Fri, 26 Jun 2026 05:50:13 GMT |
| Elecciones-Congreso.xlsx | 1151199 | dba3394f1812f338067231bce68acf56af1e13ddf8cfb709a814bcc46357ebc2 | Fri, 26 Jun 2026 05:50:08 GMT |

Recibo máquina [manifest](../../data/source_manifests/interior_congreso_20261031.json). Ambos devolvieron HTTP 200, URL final coincidente con fuente y estructura OOXML comprobada mediante `python scripts/verify_interior_originals.py --originals-dir <directorio_local_autorizado>`. Los seis tests sintéticos de este verificador pasaron. El primer SHA coincide con una captura previa documentada y no constituye una nueva observación independiente de comportamiento político. No hay certificación de filas, códigos, identidades ni primera fecha histórica de publicación por evento.

## Fuentes congresuales y BOE

- Congreso: descubrimiento documentado de fichas con expedientes y fechas de presentación, calificación y BOCG. **No** existe aún en PFL una enumeración completa con paginación, denominador, licencia particular y primeras fechas disponibles; el endpoint de exportación fue bloqueado desde el entorno empleado. Sin bypass. El adaptador `CONGRESO_PREP` opera solo con paginación sintética y rechaza campos de outcomes; 20 adversariales PASS.
- BOE: adaptador `BOE_PREP` de índices por documento, 11 adversariales PASS, GET real deshabilitado. Sus disposiciones **no** equivalen a todas las iniciativas legislativas. Ni la consolidación posterior ni la edición diaria fijan por sí mismas la disponibilidad retrospectiva de un expediente.
- Ministerio del Interior: ofrece observación histórica electoral propia, sin ser corpus de reproducción de todos los procesos decisionales. Su captura abre una vía de ingesta independiente sin forzar una falsa pregunta de TFM.

## Estructura temporal

`src/politics_fantasy/temporal_evidence.py` aporta una proyección in-memory de entidades, eventos, roles y relaciones source-local; valida revisiones y controla valid_from/valid_to, first_public_at y recorded_at. Las fuentes reales permanecen bloqueadas hasta registro autoritativo de procedencia, derechos y disponibilidad. Tests exclusivamente sintéticos, **no** certificación de causalidad o identidad.

## Decisión metodológica de esta etapa

**Objetivo programa:** reproducción/autorregulación política con acoplamientos y feedback como hipótesis. **Primer gate científico no superado:** población longitudinal de iniciativas completa, momentos de disponibilidad, rivales preespecificados y contrato A–J congelado en remoto antes de observar outcomes. La captura electoral es exploratoria de infraestructura; los análisis de persistencia y causalidad NO han empezado.

**Regla:** capturas y software no consumen automáticamente SYSTEM20. Hasta que existan nuevos recibos de contrastes con protocolo y SHA previos al outcome, ledger SYSTEM20 debe reflejar 0 válidos, 0 inválidos y 20 disponibles.

## Pruebas locales de este incremento (31-10-2026, Windows)

- `PYTHONPATH=src python -m pytest -q` sobre los módulos nuevos de temporalidad, metadatos oficiales, replay original, almacén, seguridad de fuentes, elegibilidad, endpoints y as-of: **88 PASS** al excluir la prueba POSIX especificada a continuación.
- `node --test tests/test_ui_source_links.mjs tests/test_evidence_warehouse.mjs tests/test_abh25b_insights_ui.mjs`: **34 PASS**, incluido control de URL segura y salvaguardas de evidencia sintética.
- `python -m unittest -q test_congreso_adapter.py` (en CONGRESO_PREP): **20 PASS**. `python -m unittest -q test_boe_capture.py` (en BOE_PREP): **11 PASS**, ambos con datos sintéticos y red desactivada.
- `node --check src/politics_fantasy/web/app.js`: PASS. La nueva ruta local de metadatos se ejercita además mediante HTTP loopback en `test_official_source_status.py`.
- **Fallo preexistente de compatibilidad Windows conservado:** al ejecutar el grupo más amplio incluyendo `tests/test_ingest.py`, la primera prueba `test_snapshot_exact_checksum_and_manifest` dispara `ValueError: SECURE_STORE_UNSUPPORTED_PLATFORM` en `src/politics_fantasy/secure_store.py` (dependencia de primitive POSIX); 53 pruebas anteriores pasaron. **No** se alteró la política de almacenamiento para suprimir la protección. La suite Linux completa sigue pendiente sobre el nuevo commit.

Estos resultados son QA de infraestructura, **no** contrastes AB-R del funcionamiento político ni autorización de ingesta nominal real.
