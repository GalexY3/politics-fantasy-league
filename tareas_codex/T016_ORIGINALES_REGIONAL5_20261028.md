# T016 · Captura y QA de fuentes electorales REGIONALES 2024

**PREPARADA, NO EJECUTADA; ejecución técnica Codex no cuenta ciclo AB.** Partido de rama `research/pfl-abh5-regional-audit-20261028`; crear rama de ejecución independiente `exec/pfl-t016-regional-source-20261028` desde su HEAD verificado. Leer `AGENTS.md`, AB 3.2.1, Atlas CURRENT y `research/ABH_REGIONAL5_20261028/CAMPAIGN_STATUS.json`. No usar ChatRelay, no fusionar ni lanzar CI costosa, no publicar datos identificables.

## Fuentes primarias exactas por recuperar

1. **Galicia** Junta Electoral de Galicia, DOG 06/03/2024: `https://www.xunta.gal/dog/Publicados/2024/20240306/AnuncioG2453-050324-1_es.html`. Buscar enlace `Descargar PDF` y original autonómico CSV por provincias de `https://datos.gob.es/es/catalogo/a12002994-elecciones-al-parlamento-de-galicia-resultados-2024` (página de distribución). Conservar archivos **fuera de Git**, hash SHA256 original, tamaño, URL efectiva, cabeceras HTTP, descarga UTC, redirecciones, TLS y tipo MIME. No guardar nombres de electos en un fixture agregado.
2. **Euskadi 2024 definitivo**: catálogo oficial `https://www.euskadi.eus/gobierno-vasco/-/informacion/descargas-de-ficheros-de-resultados-de-elecciones/`, entrada P24 CSV enlazada a `https://www.euskadi.eus/contenidos/informacion/w_em_descargas/es_def/adjuntos/csv/Cas-csv.zip`; XLSX P24 a través de enlace oficial. También P20 histórico para comparación temporal. Diferenciar el **informe PROVISIONAL** abril 2024 `https://www.euskadi.eus/contenidos/informacion/w_in_24_pv_resultados/es_def/adjuntos/informe-elecciones-parlamento-vasco_2024.pdf` de la publicación **DEFINITIVA** del 09/05/2024 `https://www.euskadi.eus/gobierno-vasco/-/noticia/2024/publicados-resultados-definitivos-elecciones-al-parlamento-vasco-del-21-abril/`. Si falla la descarga del ZIP, registrar motivo y detener reintentos, sin inventar datos.
3. **Europeas 2024** JEC/BOE: `https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-13092` y el XML/PDF enlazado desde la edición. Guardar el original fuera de Git y verificar los nueve ganadores + el mayor no electo, 61 escaños estatales, 17.652.007 votantes / 17.527.438 válidos / 124.569 nulos; NO atribuir escaños a provincias.

## Defecto real observado a revisar, NO corregir fuentes silenciosamente

DOG Galicia secciones I–II: encabezado estatal 1.488.805 candidaturas / 1.501.857 válidos, mientras **cuatro provincias** y **11 candidaturas** suman 1.488.705 y 1.501.757. Los 1.515.944 votantes menos 14.187 nulos = 1.501.757. Página resumen institucional `https://conselleriadepresidencia.xunta.gal/es/relacions-institucionais-e-parlamentarias/informe-dos-resultados-electorais` publica la cifra provincial, pero contiene otros campos incongruentes (PSdeG 2024, abstenciones). Buscar **corrección de erratas oficial posterior**, contrastar CSV original a nivel mesa/municipio/circunscripción, determinar qué población electoral/CERA está incluida. Distinguir fuente original frente a reconstrucción y discrepancia conocida, sin declarar que se ha encontrado la causa editorial.

## QA de la nueva rama

- Ejecutar exactamente `python proyectos/politics-fantasy-league/research/ABH_REGIONAL5_20261028/replay_galicia.py` desde la raíz con stdlib: verificar 4 circunscripciones / 75 escaños y contrafactual estado único 75.
- Ejecutar `python -m unittest -v test_source_invariant_guard.py` desde `proyectos/politics-fantasy-league/research/ABH_REGIONAL5_20261028`; registrar los 9 resultados del **código GitHub exacto**, NO atribuirle automáticamente los 9 PASS aislados de ChatGPT, que se ejecutaron sobre copia local semántica no binariamente idéntica.
- Ejecutar suite completa Python, Node y Atlas en **checkout limpio** de la rama de ejecución, sin fuentes privadas, registrando primer fallo, último PASS si procede, stdout/stderr/exit, versión de Python/Node, commit y SHA256 de todos los logs; no manipular expectativas para forzar PASS.
- Si se usa dataset descargado, inspeccionar columnas, formato/encoding/ZIP/CRC, unidades, cobertura, campos de partidos y fechas verificables; construir solo agregados sin datos nominativos. No inventar `first_public_at`; fecha de boletín no equivale a hora primera de publicación.

## Entregables y aceptación

`tareas_codex/T016_RESULTADO.md` con manifest `tareas_codex/T016_EVIDENCIA/MANIFEST.json` (SHA originales fuera de repo, salida de tests, provenance/versiones), y propuesta de reparación separada de fuentes, no modificación retroactiva de resultados AB. Dar resultado **SUCCESS/PARTIAL/BLOCKED** según acceso auténtico y QA verificable. Abrir PR borrador dirigida a REGIONAL5, sin fusionar; no crear ni gastar ciclos AB ni medallas automáticamente.
