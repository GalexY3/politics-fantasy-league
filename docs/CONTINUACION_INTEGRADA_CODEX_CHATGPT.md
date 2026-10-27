# Confirmación del checkout 4faf31a y nuevos resultados nativos · 27/10/2026

El usuario facilitó un ZIP que contiene la rama integrada al **commit exacto `4faf31a`**. Se extrajo localmente en ChatGPT, se comparó el commit con la rama de GitHub (**identical** al comenzar), y se ejecutaron sin Codex **421 tests Python + 28 subtests, 110 JS y 34 tests de AB Atlas**, todos PASS. La validación **oficial** `ab_atlas/atlas_delta.py check` ya cubre **19 lotes / 60 nodos / SHA256 `9389c8cf4b3950c6558019cb769072e23e0f5aacf1b7be8adba88c1a9d11ddf0`** (incluye el lote posterior 0019 de recibo, no una campaña AB adicional).

La prueba que antes estaba escrita pero sin ejecutar —`test_ingest_http_boundary.py`— **se ha ejecutado y ha pasado en servidor localhost real**. El conjunto dirigido HTTP/ingesta registra **20 PASS + 14 subtests**, dentro de los 421, con `403` para Host externo y `404` para rutas de captura que todavía no existen. **No** confundir ausencia de esas rutas con haber implementado la ingesta HTTP externa.

Se corrigió `tests/run_browser_smoke.py` que aún esperaba V3 36,4; ahora exige V4 36,9 y se ha comprobado su compilación. El smoke visual Chromium **NO está validado**: falta browser Playwright empaquetado y el Chromium de sistema devolvió `ERR_BLOCKED_BY_ADMINISTRATOR` sobre localhost en el entorno. Corresponde probarlo en CI/escritorio autorizado, sin intentar saltar esas restricciones. [Recibo de verificación, comandos y límites](../research/ABH_INGEST_CONTINUATION_20261027/VERIF_ZIP_4FAF31A_RESULT.md).

Se preservan los historiales distintos **AB-H45, CDX01–09 e IC01–IC03**. La nueva verificación es POST HOC, no IC04. Todos los originales privados permanecen fuera de Git, el mapeo institucional de `NO VOTAN` sigue pendiente y los indicadores **V4 36,90 %, CT2 29/100, VSDS 1/3, gates 0/6** no se promueven. La rama integrada continúa aislada de `main`. [AB Atlas CURRENT](../ab_atlas/CURRENT.md).

---

## Estado anterior a la revalidación del ZIP

# Estado posterior a IC01–IC03 — 27/10/2026

**Usar siempre la rama integrada `research/pfl-codex-contributions-20261027` y consultar [AB Atlas CURRENT](../ab_atlas/CURRENT.md).** Esta sección es la continuidad vigente; el texto inferior documenta el estado anterior a esta intervención.

La campaña de 45 ciclos ChatGPT **45/45 cerrada**, la secuencia Codex **CDX01–CDX09** y los nuevos **IC01–IC03** son **tres conjuntos distintos**. No consumir/combinar cuotas históricas ni inventar ciclos. [Informe IC](../research/ABH_INGEST_CONTINUATION_20261027/REPORT_IC01_IC03.md).

**Implementado:** `ingest.py` valida fuente y hostname oficial exactos y **cada salto de redirección antes de conectar**, límite cinco, preserva SHA/manifiesto. `quarantine_ingest.py` realiza flujo real **local y ficticio** captura→verificación SHA→validador fuente Congreso/Senado→estado de cuarentena, y nunca promueve a publicación o scoring. Tests **IC01 9/9, IC02 6/6** nativos localmente. Hubo arreglos de fixture conservados en historial y el archivo de prueba IC01 ejecutado por copia no coincidía en SHA con GitHub; repetirlo fielmente en el checkout.

**No conectado:** el servidor ofrece `GET /api/source-stages` read-only, `GET /api/health` demo, pero **no contiene un HTTP POST que capture fuentes ni un GET de cuarentena**. Se ha escrito `test_ingest_http_boundary.py` y añadido a CI opcional; **no ejecutado** sobre servidor integral. Sin original publisher→HTTP→identidad→puntos real.

**Atlas:** hasta lote `0017-PFL-INGEST-IC01-IC03-20261027`, replay independiente JS 17 lotes PASS (60 nodos, 78 edges, 98 runs, 40 complaints). El validador Python oficial solo está acreditado hasta lote 0016; no reutilizar su SHA anterior como si describiera 0017. **NO VOTAN** permanece mapeo operativo sin documentación oficial de significado. V4 **36,90%**, CT2 **29/100**, VSDS **1/3**, gates **0/6** invariantes. Los originales privados continúan fuera de Git.

**Próximo paso con valor:** ejecutar `pytest` en checkout íntegro, validar el endpoint HTTP negativo y la integridad del Atlas Python, valorar diseño de un **operador de ingesta autenticado** con política de egress y licencias solo tras esa aceptación. R5: no crear un endpoint vulnerable o seguir generando fixtures sin nueva observación.

---

## Nota histórica anterior a IC01–IC03

# Continuación coordinada de Politics Fantasy

Trabaja desde la rama **`research/pfl-codex-contributions-20261027`**, que integra el cierre de ChatGPT `1f2dd59` y los nueve ciclos CDX01–CDX09 de Codex. Lee primero `AGENTS.md`, `ab_atlas/CURRENT.md` y los resultados de la pieza que vayas a modificar. Conserva ambos historiales y no fusiones a `main` por tu cuenta.

La campaña AB-H45 cerró A01–A20, R01–R05 y B01–B20: **45/45**, sin ciclos pendientes de ese bloque. El usuario también autorizó a Codex una línea abierta separada. No presentes los nueve CDX como parte de los 45 ni inventes cuotas o resultados. Antes de continuar ciclos en este chat, interpreta la autorización vigente del usuario y aplica R5 y el contrato AB; si hace falta una autorización adicional, solicítala con un objetivo concreto.

El Atlas integrado conserva la secuencia de ChatGPT 0012–0015 y reencadena el lote Codex como 0016, conservando el original en Git. Se ejecutó el validador Python oficial: 16 lotes, 58 nodos y hash `3168eab0eadab0f2900e2ab0bb0c2aa6f40a4a381e83fca9cf782d84899aeb4d`. Haz `fetch` y comprueba el último lote antes de escribir otro: si hay trabajo concurrente, reconcilia padres y contenido en vez de sobrescribirlo.

Prioriza el flujo de ingesta y sus fronteras, con una comprobación reproducible y fixtures ficticios:

1. Examina `src/politics_fantasy/ingest.py`: el cliente local usa redirecciones de `urlopen` y actualmente comprueba el destino final después de abrirlo. Verifica cada salto antes de contactar un destino no permitido, incluye cadena de redirecciones y emparejamiento fuente/host, con pruebas negativas controladas. Esto es un hallazgo local de código; no se ha demostrado una ruta HTTP explotable.
2. Diseña y prueba un flujo integral de captura/ingesta, validadores originales y cuarentena, con pruebas HTTP solo donde exista esa interfaz. Distingue el catálogo HTTP de fuentes y la simulación de jornada de una ingesta real completa: ambos se prueban, pero no son ese E2E. No introduzcas originales privados ni datos nominativos en Git.
3. Mantén la semántica de `NO VOTAN` como interpretación operativa pendiente de documentación institucional. La coherencia interna de los XML y JSON no certifica identidad, semántica jurídica ni `first_public_at`.
4. Registra evidencia, negativos, límites y cualquier delta de Atlas; ejecuta la suite pertinente y mantén explícitamente V4 36,90 %, CT2 identidad 29/100, VSDS 1/3 y gates 0/6 salvo que una evaluación válida y documentada justifique cambiarlos. Sin Actions innecesarias.

La validación posterior a la integración produjo 404 tests Python y 14 subtests aprobados, 1 omitido por enlaces simbólicos en Windows; 110 tests JavaScript y el smoke de juego Chromium aprobados. Son resultados locales en ese entorno, no validación de producción ni de fuentes reales de extremo a extremo.
