# T020 · Datos originales firmados del Parlamento Europeo y réplica independiente

**PENDIENTE — NO EJECUTADA; no consume ciclos AB.** Base `research/pfl-abh5-eu-participation-20261028` en `GalexY3/Metodologia-AB`. Leer AGENTS.md, protocolo 3.2.1, `ab_atlas/CURRENT.md` y `research/ABH_EU27_20261028/FINAL_REPORT.md`. Crear rama ejecutora separada y PR borrador hacia EU27, nunca main. No ChatRelay, CI costosa ni registros personales.

## Descarga y autenticación: requisito prioritario

Portal oficial Parlamento Europeo: https://results.elections.europa.eu/en/tools/download-datasheets/ . El índice publicado ofrece archivos **CSV de participación por país (2019/2024)** y **equilibrio de género por país** (periodos constitutivos 2019 y 2024), además de los ficheros **JSON**, firmas digitales adjuntas, certificados y cadena de certificación. En ChatGPT la descarga de ese portal devolvió 502, y el contenedor sin DNS no pudo resolver el dominio: **0 bytes originales y 0 firmas verificadas**. NO convertir las transcripciones propias en CSV oficiales firmados.

Usar navegador real o Work/PC autorizado para: descargar los cuatro datos originales y sus cuatro firmas correspondientes; certificado y cadena de certificación; registrar URL final, fecha/hora UTC de captura, HTTP/TLS, tamaño MIME, SHA-256 real y código exacto de verificación criptográfica (p.ej. OpenSSL, según tipo de firma). Declarar VERIFIED solo con validación de firma/chain exit=0, no por presencia de enlaces. Si autenticación bloqueada registrar PARTIAL/BLOCKED con razón, no inventar bytes/certificados. Guardar originales gitignored; subir solo manifest SHA, versiones y panel agregado sin datos personales.

## Conciliación y réplica de fuentes

Contrastar firmas/CSV contra `research/ABH_EU27_20261028/EU27_OFFICIAL_HTML_TRANSCRIPTION.csv`, 27 ISO, años 2019/2024, turnout y % mujeres. La tabla 2019 publica porcentajes de mujeres **redondeados a enteros**; 2024 a dos decimales. El total EU 2024 mujeres **38,53%** es agregado ponderado por escaños y no media no ponderada de países (**35,57%** en el panel). 2024 Alemania incluye categoría *Other* 1,04%.

Para clasificación legal del voto obligatorio en 2024, cotejar fuente EPRS 2024 con cinco estados `BE BG LU CY EL` y ficha posterior EP con cuatro `BE BG LU EL`; no suponer retroactividad normativa ni efectividad de sanciones. Verificar cronología con legislación nacional y fuentes originales 2024, sin decidir causalidad por descarte arbitrario. Buscar fuente **independiente del EP** para una réplica de representación femenina, por ejemplo IPU Parline o autoridad nacional, con fecha de constitución alineada; indicar conflictos.

## Ejecución y validación

En checkout limpio ejecutar desde `research/ABH_EU27_20261028` el script `python analyze_eu27.py`; requerimientos Python pandas, scipy, numpy y scikit-learn. Git blob transcripción `ad33f639c2e7d51584ffd9012a715d1fea3798f0`; script `c092caee24fd2e1b66c7e80205d027904c24fcc8`, ambos **ejecutados localmente y verificadas coincidencias exactas** en ChatGPT. Confirmar n=27, no nulos, Pearson ~−0,0244, Spearman ~+0,0599, cambios rho ~+0,1911, LOOCV MAE 10,09 para 2019 género vs 11,55 solo participación 2024. Si CSV firmado modifica valores, **no ajustar silently**: documentar errata, versionar otra muestra y repetir evaluación con prerregistro independiente si se pretende confirmación.

Correr también suite Python/Node/Atlas **integral** en checkout limpio si las restricciones de coste lo permiten, con stdout/stderr, códigos de salida y hashes. El script analítico NO sustituye la suite.

## Entregables

`tareas_codex/T020_RESULTADO.md` y `tareas_codex/T020_EVIDENCIA/MANIFEST.json` con hashes originales y verificación de firmas; comparación exacta con 27 filas y fecha de representación, respuesta de fuente externa de género (si accesible), QA. RESULTADO SUCCESS si originales + firmas de ambas series verificados, conciliación y QA limpia; PARTIAL/BLOCKED con bloqueos reales. PR borrador, sin fusionar. No aumentar CT2 ni conceder N1 automáticamente: toda observación de 2019/2024 ya fue utilizada en análisis exploratorio.
