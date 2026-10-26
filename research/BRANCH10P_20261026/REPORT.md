# BR10P · primera decena autorizada: extracción fuente BOE a varias provincias

**Cierre 10/10 A–J**, véanse [PREREG](PREREG.json), [RESULTS](RESULTS.json) y [LEDGER](LEDGER.json). Este bloque no se ha convertido en un estudio prospectivo de influencia política.

El original [BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066), publicado en 2023 y recibido por HTTPS oficial, conserva SHA-256 `d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`. Se extrajeron **52 cabeceras provinciales**, de las cuales **25 dieron secuencias continuas** y un total de **263 candidaturas electorales** de un total de **50 siglas distintas**; 27 territorios tenían saltos de numeración (R5 de completitud). De las 25 secciones con secuencia continua, **16 carecen de advertencia conocida y nueve contienen referencias a no proclamación** que exigen revisión jurídica del texto original.

Primer intento de extractor original rechazó todas las secciones; se conservó ese fallo. Se reparó la condición de títulos cortos (VOX). La [manifestación de resultados](../../data/observatory/boe_2023_multiterritory_reviewed.json) conserva fuente, identificadores por provincia/documento/número, incidencias y cero identidades personales o partidos inscritos supuestos.

Existe un nuevo [API read-only](../../src/politics_fantasy/nomination_atlas.py) en `GET /api/official-nominations`, incorporado al [Atlas del prototipo](../../src/politics_fantasy/web/app.js). No habilita puntuaciones reales ni un registro nacional de partidos. Las [pruebas Python adversariales](../../tests/test_audit_boe_nominations_all.py) comprueban ausencia de nombres personales y disyunción del Senado; [test_nomination_atlas.py](../../tests/test_nomination_atlas.py) verifica integridad y fuente.

**Límite crucial:** los 263 registros son listas en determinadas circunscripciones de una elección de 2023, no 263 organizaciones distintas ni evidencia de actividad o influencia en 2026. Se ha realizado un cruce conservador únicamente para ocho siglas de Albacete; no se fusionan acrónimos de otras provincias con personalidades jurídicas sin autoridad.

**Decisión:** `CLOSE_BR10P / AUDIT5Q_REPAIR`; se gastan los primeros diez ciclos. El bloque de cinco auditorías revisará integridad, privacidad y presentación; el último bloque autorizado de veinte ciclos se enfocará donde el contraste revele lagunas verificables.

[Fuente y limitaciones](../../docs/BOE_NOMINATION_ATLAS_2023.md) · [Priors](PRIORS_DELTA.md).
