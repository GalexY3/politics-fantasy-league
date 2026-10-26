# Atlas de candidaturas proclamadas del Congreso (elecciones del 23/07/2023)

**Unidad observacional:** candidatura electoral proclamada por una Junta Electoral Provincial en una circunscripción, numeración y elección dadas. No es necesariamente partido legal inscrito, grupo parlamentario, cargo político ni militancia de ningún individuo.

## Fuente auténtica

[BOE-A-2023-15066](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066), fecha oficial 27/06/2023; PDF 4.298.580 bytes, SHA-256 `d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`, descargado por HTTPS institucional en [GitHub Actions](https://github.com/GalexY3/Metodologia-AB/actions/runs/40322243535). Extracción `pdftotext -layout` del PDF completo, separación por encabezado Junta Electoral Provincial y dentro de ella Congreso/Senado. No se trasladan nombres de candidatos individuales ni posibles identificadores personales a este conjunto.

El [parser fuente](../scripts/audit_boe_nominations_all.py) exige grupos en mayúsculas con sigla al final e identificador de lista ordinal; si aparecen saltos de numeración, se detiene la certificación de esa sección. La primera prueba real detectó un fallo de extracción de siglas cortas —en especial «VOX»— y se reparó. La segunda prueba reconoció **52 cabeceras provinciales**, con **25 secciones en las que pudo extraer 263 rótulos de candidaturas con secuencia continua** y **27 secciones excluidas por numeración incompleta**. De las 25 extraídas, **16 carecen de aviso conocido** y **9 contienen expresiones que requieren revisión por «no proclamada»**. No equivale a una extracción completa ni correcta de los 52 ámbitos. Las incidencias están preservadas en [manifest del atlas](../data/observatory/boe_2023_multiterritory_reviewed.json).

## Estados de calidad

- **EXTRACTED_NO_KNOWN_NOTICE:** 16 secciones; la secuencia 1..n cumple reglas del parser. Todavía podría haber errores semánticos y no constituye certificado jurídico de totalidad.
- **EXTRACTED_REVIEW_NOTICE:** 9 secciones; secuencia continua, pero el cuerpo menciona candidaturas no proclamadas, por lo que su estatus demanda revisión con contexto.
- **NON_SEQUENTIAL_QUARANTINE:** 27 secciones; el parser perdió o no pudo adjudicar uno o varios ordinales. Sus rótulos incompletos no se ofrecen como universo electoral íntegro.

No existe un denominador contrastado de **todos los partidos políticos activos en España** ni de **todas las personas políticamente influyentes**; se preserva `coverage_rate:null` para esas poblaciones. Las 52 cabeceras detectadas son solo un denominador documental de este PDF histórico. La técnica no demuestra que 263 candidaturas distintas equivalgan a 263 partidos: la misma sigla se repite entre provincias y coaliciones.

## Seguridad y privacidad

- No se usan nombres de particulares, supuesta afiliación, ideología, medios, relaciones personales o scoring de mérito.
- Claves de candidatura: `(BOE 2023, junta provincial, Congreso, ordinal)`; identidad jurídica de partido = **no confirmada**.
- API local `GET /api/official-nominations` devuelve únicamente acrónimos, secciones, fuente SHA y alertas. Rechaza fuentes con hash inesperado, filas sin ID válido, coincidencias ordinales duplicadas, atribución personal o inscripción legal inventada.
- El frontend lista las secciones en controles expandibles con avisos, sin convertir visibilidad documental en influencia.
- Este atlas es investigación histórica y prototipo de ingeniería, no una clasificación partidista.

## Alcance del siguiente paso

La prioridad para convertirlo en una población válida es revisar las 27 secciones incompletas contra el PDF original y distinguir expresamente las nueve con mensajes de no proclamación, con doble comprobación independiente. Después hacen falta fuentes jurídicas del Registro de Partidos y fuentes temporalmente válidas para cargos públicos. No adjudicar `src.registry` o `id.real` por disponer solo de siglas.

**Estado científico:** ningún resultado causal, N1/N2/N3 nuevos=0. La validación es documental y acotada a una sola elección de 2023.
