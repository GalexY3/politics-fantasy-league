# Politics Fantasy League · PILOT_NATIVE5 · Informe final AB-H · 29/10/2026

## Estado y titular científico
**CINCO ciclos A–J válidos y acotados ejecutados, 5/5**, tres AB-P (C01, C03, C04) y dos AB-R de auditoría adversarial/documental (C02 y C05). 0 inválidos, 0 planificación y 0 pendientes de esta autorización. Rama `research/pfl-abh5-pilot-native-integration-20261029`, iniciada exactamente desde [PR #35](https://github.com/GalexY3/Metodologia-AB/pull/35) HEAD `f60aebb9fae4bfa09bb642c68cdd072ab99583f6`. Sin ChatRelay, merge a main, CI costosa ni puntuación de personas políticas reales.

**Este bloque es ingeniería y auditoría, NO ensayo con participantes:** no hay sujetos reclutados, consentimientos reales, datos personales, desenlaces humanos ni efecto causal PFL identificado. CT2 de la línea prospectiva **25/100** ordinal y sin cambios; otras líneas, identidad PFL 29 y mecanismos sintéticos 20, son distintas. VSDS 1/3, V4 contractual 36,90%, 2/90 logros, gates lanzamiento 0/6, N1/N2/N3 nuevos 0/0/0. Ningún resultado 1/3–3/3 científico nuevo.

[Estado/ciclos](CAMPAIGN_STATUS.json) · [sources/priors](SOURCES_AND_PRIORS.json) · [CT2 gráfico total y zoom](CT2_FULL_AND_ZOOM.svg) · [gates éticos](ETHICS_RIGHTS_GATE.md).

## C01 AB-P: ejecución nativa de los cinco módulos anteriores

[Prereg](C01_PREREG.json) commit `2a1ef0e7abbb3c38fc4713b7802507489b627507` antes de ejecutar, [resultado A–J](C01_RESULT.json).

Se descargaron a través del conector GitHub los **cinco códigos exactos** de PR35. Se reconstruyeron en un contenedor aislado con Node `v22.16.0` y se verificó su SHA Git blob con `git hash-object`: asignación `f85cfbd1...`, ítems `a23a8a9...`, clave `63c6ff6...`, intake `3e4f0f1...`, análisis `e7a63b8...`. Todos coinciden con los blobs del repositorio; cinco `node --check` PASS.

**84/84 pruebas previas reproducidas en Node nativo**, ahora con nuevas afirmaciones ejecutadas contra esas funciones: C02 parent 17/17, C03 parent 20/20, C04 parent 22/22, C05 parent 25/25. El script de reproducción aislada fue ejecutado localmente (`/mnt/data/pfl_native_qa/replay84.mjs`, git blob `de4084d749518b7b426da1ee753d234870334287` antes de parches) pero **no se ha almacenado como tal en la rama privada**: el conector GitHub no comparte directamente el sistema de archivos aislado. No afirmar que se ha ejecutado la suite *full checkout* o que la prueba local forma parte de CI. T027 registra la deuda.

Rival competente: el entorno V8 previo podía ocultar incompatibilidades de Node. Aquí no se observaron fallos para las 84 mismas propiedades. No valida fiabilidad de instrumentos psicológicos ni efectos en usuarios.

## C02 AB-R: hallazgo adversarial de forma de los datos y reparación

[Prereg](C02_PREREG.json) y [resultado](C02_RESULT.json).

Se sometieron a los **tres validadores** `pilot_dryrun_intake.mjs`, `fictional_transfer_key.mjs` y `pilot_analysis_dryrun.mjs` a entradas con `Symbol` y atributos heredados, fuera de las anteriores pruebas basadas en `Object.keys`. Se verificó en Node que **cinco casos de metadatos extra antes eran admitidos** (nombres, afiliación ficticia/«preferencia» como campos ocultos, tanto en envoltorios como en respuestas y filas). El sexto caso confirmó que el objeto `approval` simulado podía falsificarse.

Se actualizaron las tres funciones para requerir objeto plano (o prototipo `null`), **`Reflect.ownKeys` exactamente igual a la lista permitida** y propiedades propias de valor, sin getters. Nuevos Git blobs: `f0959f...`, `34e7af...`, `97dd199...`. Tras el parche, **cinco de cinco bypasses de metadatos rechazados y 84/84 pruebas originales nativas conservadas**. El sexto caso no se «repara»: el objeto de aprobación sigue siendo un mock **no apto para usos humanos**. No existe endpoint de intake en el servidor.

Esto es reparación de validación sintética, no prueba de protección frente a todos los objetos hostiles, `Proxy` arbitrarios o ataques de infraestructura.

## C03 AB-P: interfaz local sin clave de respuestas

[Prereg](C03_PREREG.json) y [resultado](C03_RESULT.json); código en [`pilot_local/`](../../pilot_local/README.md).

Se implementó un navegador de cuatro condiciones ilustrativas: tutorial neutro/denominadores × actividad agregada/leaderboard de **avatares ficticios**. La selección de condición es manual para inspección local, **no asignación experimental**. Las preguntas X1–X4 provienen del mismo módulo original, sin incluir la clave de corrección, `scoring`, `intake` ni analizador en las rutas servidas. Selecciones conservadas solo temporalmente en DOM, sin envío ni persistencia.

**17/17 comprobaciones de fuentes nativas** PASS: cuatro valores de condición, campos con labels/fieldset, ausencia de `innerHTML`, ausencia de almacenamiento/telemetría, clave no importada, fuente CSS focus/viewport, y controles de cliente. Los cuatro recursos nuevos (`index.html`, `app.mjs`, `style.css`, `server.mjs`) se copiaron al contenedor local y cotejaron por Git blob. **Chromium headless se intentó**, pero terminó por timeout sin volcar DOM: browser E2E y accesibilidad real **NO VERIFICADOS**. Los tutoriales no están equiparados aún en tiempo/dificultad y el piloto no es científicamente desplegable.

## C04 AB-P: servidor mínimo y auditoría HTTP

[Prereg](C04_PREREG.json) y [resultado](C04_RESULT.json); test persistido [`pilot_local/smoke_http.mjs`](../../pilot_local/smoke_http.mjs).

El servidor Node escucha **solo `127.0.0.1:8787`**. `GET`/`HEAD` únicamente para cinco rutas declaradas; todo lo demás responde 404, y métodos de envío (POST/PUT/DELETE) 405. Sin cookies, tracking, respuestas por red, formulario con submit ni almacenamiento. Se envían `CSP` con `connect-src 'none'`, `no-store`, `nosniff`, `no-referrer`, permisos sensibles deshabilitados y `frame-ancestors none`.

**15/15 comprobaciones HTTP en Node nativo** PASS sobre proceso local, incluyendo negación de endpoint de respuestas, clave de corrección, traversal, queries, analytics y métodos que mutan. La fuente `smoke_http.mjs` sí está en GitHub con hash `a1fc27d8703fa9875b199cb7811aee3a67ee1f44`, verificado antes de ejecutarlo. Esto **no** prueba seguridad contra extensiones locales, navegador malicioso, servidores montados con otra configuración o despliegue público.

## C05 AB-R: auditoría de la campaña anterior y ética

[Prereg](C05_PREREG.json) y [resultado](C05_RESULT.json).

Se consultaron en vivo los cinco registros del padre `ABH_PROSPECTIVE_PILOT5`, el lote Atlas `0078` y los cinco pares prereg→resultado mediante `compare_commits`: todos muestran `ahead`, `behind=0` y de 5 a 10 commits entre prereg y resultado; el lote 0078 tiene cinco `run.add`. Esto verifica cronología y registro, **no evidencia humana** ni novedad. El `ab_atlas/CURRENT.md` canónico estaba **sin sincronizar desde el bloque previo** por tamaño/bloqueo del conector; no se ha ejecutado checker Atlas nativo ni se declara reparado.

Fuentes actuales independientes para futuras obligaciones: [Comité de Ética de la Investigación USAL](https://investigacion.usal.es/es/comite-bioetica), [AEPD consentimiento inequívoco](https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0211-segun-el-rgpd-como-debe-solicitarse-el-consentimiento-de-los-interesados-para-tratar-sus-datos-personales), [AEPD bases jurídicas](https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0214-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-datos), [AEPD anonimización](https://www.aepd.es/preguntas-frecuentes/0-conceptos-basicos/FAQ-0005-sobre-los-datos-anonimizados). No se ha obtenido informe/dispensa de comité, autorización de tratamiento o consentimiento. Ver [gate](ETHICS_RIGHTS_GATE.md).

## R1–R5, contraste adversarial y tareas pendientes

**R1** identidad de los constructos: reglas de game demo ≠ comportamiento humano, personaje ficticio ≠ representante real. **R2** Node nativo vs V8 y casos adversariales frente a tests originales, comparación por misma fuente. **R3** hashes y prereg commits; parent con cinco ancestrías verificadas, pero trabajo local sin checkout integral. **R4** reportar fallos de `Object.keys`, revisión mock, E2E de Chromium fallido, ausencia de paridad temporal y estado parcial del Atlas. **R5** cerrar pruebas locales del bloque y no reclamar efectos reales hasta datos prospectivos aprobados.

[**T026**](../../tareas_codex/T026_PILOT_NATIVE_ETHICS_QA_20261029.md) permanece **parcial/abierta**; [**T027**](../../tareas_codex/T027_PILOT_BROWSER_ATLAS_ETHICS_20261029.md) específica prueba nativa de checkout completo, navegador, seguridad extendida, sincronización/QA Atlas 0078–0079 y consulta ética aplicable. No cuentan como ciclos ejecutados.

## Decisión

**CLOSE_BOUNDED_5_OF_5**. Guardar fuentes, priors, CT2/Atlas y PR borrador sucesora. **SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, sujetos a autorización nueva, pero priorizar tareas con nueva evidencia independiente: completar navegador/Atlas, requisitos previos de investigación humana o pivot científico PFL no dependiente de reclutamiento; no repetir lo sintético para consumir cupo. La solicitud se ofrecerá también como botón.


## Registro GitHub verificable

**PR draft #36**: https://github.com/GalexY3/Metodologia-AB/pull/36, apilada sobre `research/pfl-abh5-prospective-pilot-20261029`; creada y confirmada sin fusionar. Atlas 0079 y estado complementario versionados; `CURRENT.md` canónico aún desincronizado (heredado de 0078). No se ejecutaron GitHub Actions ni estudios humanos.
