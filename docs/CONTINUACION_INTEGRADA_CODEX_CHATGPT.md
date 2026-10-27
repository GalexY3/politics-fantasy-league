# Continuidad vigente · CONT50 C41–C50 cerrado 10/10 · Atlas 0027

Leer [CURRENT](../ab_atlas/CURRENT.md), [ledger](../research/ABH_CONT50_20261027/CAMPAIGN_STATUS.json) e [informe](../research/ABH_CONT50_20261027/REPORT_FINAL.md). Usuario autorizó exactamente 10 nuevos AB-H, se documentaron y ejecutaron **C41–C50, 10/10 A–J**, saldo 0. **No** comenzar C51 sin nueva concesión.

C41 integró y probó `forecast.py` (10 FAIL/2 PASS originales → 12 PASS); C42 publicó las siete regresiones del grafo; C43 verificó cortes históricos; C44 re-auditó JSON originales V3/V4 con nueve invariantes **sin cumplir el replay previsto por ambos runtimes**; C45–C49 ejecutaron pruebas originales de calidad, grafo, política de admisibilidad, estadística y 48 controles de identidad Poisson. C50 cerró con **173 Python + 9 Node PASS**, **12 módulos fuente y 18 archivos tests** con Git SHA idéntico. Solo subconjunto verificado; ningún pytest global ni Node global ni originales externos. Evidencia local archivada en `PFL_CONT50_native_evidence.zip` en esta conversación.

Atlas append-only **0027**, **27 lotes**; conteos **derivados** 63/81/**169**/44 y **338 operaciones**. El checker Python canónico de Atlas **NOT_RUN**, SHA estado no calculado. Indicadores V4 **36,90%**, CT2 identidad **29/100**, VSDS **1/3**, nuevos N1/N2/N3 0, gates **0/6**. No acciones CI, merges o puntuaciones personales reales.

**Codex #17 [pendiente](https://github.com/GalexY3/Metodologia-AB/issues/17)**: cuando pueda accederse, checkout HEAD exacto, comprobar **27 deltas** del Atlas con salida/exit/SHA, pytest completo y Node. Ni abrir una issue ni registrar esta nota es ejecución. El siguiente trabajo debería priorizar corpus original institucional y bloqueos reales, no repetir variantes de NaN/fixture bajo cuotas.

---

# CONT40 C31–C40 cerrado: 10/10, Atlas 0026

[Informe](../research/ABH_CONT40_20261027/REPORT_FINAL.md) y [ledger](../research/ABH_CONT40_20261027/CAMPAIGN_STATUS.json). Se hicieron 91 tests Python y 9 Node sobre módulos SHA-idénticos a la rama, más 12 Python sólo sobre modificación local **no incorporada** de forecast. V4 36,90%, CT2 29, VSDS 1/3 y gates 0/6; Atlas 26 lotes, 159 runs derivados sin check Python canónico. [Codex #17](https://github.com/GalexY3/Metodologia-AB/issues/17) sigue pendiente hasta que esté disponible; no se ha ejecutado. Se necesita nuevo permiso para otra campaña.

---

# Continuidad vigente · CONT30 C21–C30 completado 10/10 · Atlas 0025

**Fecha:** 27/10/2026. **Leer primero [CURRENT](../ab_atlas/CURRENT.md), [ledger CONT30](../research/ABH_CONT30_20261027/CAMPAIGN_STATUS.json) e [informe completo C21–C30](../research/ABH_CONT30_20261027/REPORT_FINAL.md)**. Usuario autorizó **10 ciclos adicionales AB-H** y exigió ciclos completos, corrección metodológica y reportes de avance; se han documentado C21–C30 **10/10**, saldo 0. Cualquier nuevo bloque requiere permiso expreso.

**Cambio importante en nivel de evidencia:** primer subconjunto **Python nativo ejecutado** sobre tres módulos extraídos del GitHub privado byte-idénticos según hash Git (`secure_store.py`, `private_audit.py`, `private_audit_cli.py`). Cuatro suites versionadas SHA-idénticas, incluida `tests/test_private_store_process_boundaries.py` añadida en C30, arrojaron **58 PASS / 0 FAIL (10.48 s)**. Pruebas de contorno realizadas adicionalmente: 640 registros JSON únicos con 8 procesos ×40 ×2 rondas y `SIGKILL` reales contra funciones del almacén en cuatro situaciones. **C24** reveló tres errores de fixture (0644, rechazo de permisos anterior al parser) y **C25** reparó sólo los tests a 0600; quedó documentado el fallo original. **C29** tuvo un hook inicial inválido y luego corrección de instrumentación; no confundir ensayos inválidos con bug productivo. Los tests demuestran funcionamiento local POSIX en esos casos, **no** recuperación automática tras apagado, transacciones globales ni seguridad frente a procesos hostiles.

**Atlas** último lote `0025`: 25 deltas append-only, 63 nodos, 81 aristas, **149 runs**, 44 complaints, 318 ops derivadas. **El ejecutable Python canónico sobre los 25 originales aún no se ha corrido**. CT2 identidad 29/100 ordinal, V4 36,90 %, VSDS 1/3, N1/N2/N3 nuevos 0/0/0, gates 0/6; sin puntuaciones reales ni datos nominales originales publicados.

**Tarea Codex abierta #17:** https://github.com/GalexY3/Metodologia-AB/issues/17 — ejecutar en checkout íntegro del HEAD de la rama `research/pfl-codex-contributions-20261027` checker Atlas de **25 lotes**, con SHA/exit/output, pytest completo y pruebas JavaScript/Node. **Abrir/actualizar el issue no implica ejecución.** No Actions costosas, no merge a main, no originales privados en Git. Al terminar una campaña futura, actualizar Atlas CURRENT y el ledger antes de solicitar más ciclos.

---

# Continuidad vigente · CONT20 C11–C20 cerrado 10/10 · Atlas 0024 · 27/10/2026

**Leer [CURRENT](../ab_atlas/CURRENT.md), [ledger CONT20](../research/ABH_CONT20_20261027/CAMPAIGN_STATUS.json) e [informe final CONT20](../research/ABH_CONT20_20261027/REPORT_FINAL.md).** Segunda campaña autorizada de diez ciclos **agotada** C11–C20, todos con registro A–J (limitaciones explícitas); otro bloque requiere permiso nuevo.

C11 auditó mediante JS **los 23 deltas originales GitHub** previos, 63 nodos/81 edges/129 runs/44 complaints, sin Python canónico. C12–C13 refuerzan estrictamente JSONL. C14 lectura anclada de RAW, C15 fsync creación root, C16 rollback en excepción capturada, C17 lector compartido flock, C18 inventario de huérfanos, C19 subprocess SIGKILL real **sólo con datos ficticios** y fail-closed si falta newline, C20 inspección privada de ledgers **antes de solicitud a origen**. Nuevos tests Python añadidos a Git, **no ejecutados en checkout integral**.

**Atlas nuevo 0024:** diez `run.add` en lote `0024-PFL-ABH-CONT20-C11-C20-20261027`; conteos **derivados** 63/81/139/44, total 24 lotes, no SHA estado Python. CT2 29/100, VSDS 1/3, V4 36,90 %, 0/6 launch gates, N1/N2/N3 nuevos 0. Ningún CI costoso, main merge o puntuación real.

**Próxima tarea concreta para Codex (solo cuando haya permisos/entorno):** checkout exacto de la rama; `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates` para 24 lotes, stdout/stderr/exit/hashes; pytest completo y Node, especialmente fallos/portabilidad de C12–C20. No elevar madurez hasta que existan salidas verificables y fuentes originales adjudicadas.

---

# Continuidad vigente · CONT10 cerrada 10/10 y Atlas 0023 · 27/10/2026

**Consultar primero [CURRENT](../ab_atlas/CURRENT.md), [ledger cerrado](../research/ABH_CONT10_20261027/CAMPAIGN_STATUS.json) e [informe A–J C01–C10](../research/ABH_CONT10_20261027/REPORT_FINAL.md).** El usuario autorizó 10 ciclos nuevos AB-H y después exigió terminar los ya concedidos. **Hechos C01–C10, saldo 0**. A partir de ahora cualquier nueva campaña AB requiere nuevo permiso; distinguir del historial AB-H45, CDX01–09 e IC01–23.

C01–C05: replay estructural JS Atlas 0001–0020, semántica institucional no-equivalente a contrato XML `NO VOTAN`, licencia acotada de Senado, actualización documental, RPP sin original y R5 previo. C06–C10: tail Atlas 0021/0022 verificable, CLI auditor inseguro para manifest sin tamaño corregido (salida 2), bloqueo cooperativo `fcntl.flock` sobre apéndice JSONL ante fragmentación, necesidad Linux de fsync(dirfd), y sincronización de nombres de directorios de objeto/manifest. **No se ha ejecutado pytest full** tras dichos cambios. Las pruebas locales referidas son microtests aislados de código/mecanismo POSIX, no pruebas completas sobre checkout del HEAD; la prereg C07 se asentó después del primer prototipo y se declaró así.

**Atlas 23 lotes, último 0023; conteo derivado 63 nodos, 81 aristas, 129 runs, 44 complaints**. Python `atlas_delta.py check` sobre los 23 originales y hash de estado **sin ejecutar**. Madurez V4 36,90 %, CT2 identidad 29/100, VSDS 1/3, N1/N2/N3 nuevos 0/0/0, 0/6 gates. No puntuación real, originales privados, Actions costosas ni merges a main.

**Tarea inmediata para Codex si sigue el trabajo:** validar bajo checkout completo y código exacto de la rama los 23 deltas de Atlas, pytest completo y tests Node, pruebas específicas de C07/C08/C10, y ensayo adversarial de fallo de proceso limitado a datos sintéticos y sistema desechable. Registrar comandos/salidas y SHA canónico. Nunca prometer durabilidad de corte eléctrico a partir de `os.fsync` sin prueba y protocolo transaccional. Para investigación institucional RPP/Senado, requerir documento original y evitar repetir catálogos.

---

# Continuidad vigente · CONT10 con pausa R5 tras C05 · 27/10/2026

**Leer [CURRENT](../ab_atlas/CURRENT.md) y [ledger CONT10](../research/ABH_CONT10_20261027/CAMPAIGN_STATUS.json) primero.** Autorizados por el usuario diez ciclos AB-H nuevos en la rama `research/pfl-codex-contributions-20261027`; **C01–C05 completados A–J, cinco autorizados no ejecutados**, pausa **STOP_R5**. No descontar de este cupo los historiales separados AB-H45, CDX01–09 e IC01–IC23; no pedir nueva autorización sobre las cinco plazas ya existentes.

C01 comprobó estructuralmente por JS **20 lotes exactos de GitHub** hasta Atlas 0020 sin errores observados: **63 nodos / 81 aristas / 119 runs / 44 complaints**, pero **no ejecutó Python canónico**. C02 identificó semántica institucional de presencia sin voto en el Senado, **no** el diccionario exacto del literal XML `NO VOTAN`. C03 confirmó CC BY 4.0 salvo excepciones y condiciones en el **subportal de datos abiertos** del Senado, con seis distribuciones de listas de iniciativas; C04 incorporó esa evidencia a la matriz canónica de derechos sin elevar gates. C05 consultó las rutas registrales oficiales RPP, **sin recuperar un original por entidad o certificado firmado**, y activó R5 para no repetir intentos equivalentes.

**Atlas:** `0021` (C01–C04) y `0022` (C05) incorporados append-only, comprobadas cabeceras/parents y cinco runs. Total derivado **22 lotes, 63 nodos, 81 relaciones, 124 runs, 44 complaints**, pendiente todavía del `atlas_delta.py check` canónico y SHA del estado exacto. No se lanzó CI, ni corrió full pytest de esta cabeza, ni se fusionó a `main`. Quedan **V4 36,90 %, CT2 29/100, VSDS 1/3, N1/N2/N3 nuevos 0/0/0, gates 0/6**. Ni la licencia de portal ni la comprobación JS autorizan scoring real.

**Siguiente intervención con nueva evidencia:** Codex/checkout íntegro debe certificar el replay Python de los 22 lotes y ejecutar pytest completo y pruebas de recuperación ante terminación de proceso; para AB-R, obtener un documento oficial RPP individual o un esquema XML del Senado directamente verificable. Las cinco plazas CONT10 permanecen disponibles, pero R5 exige no gastarlas sin nuevos instrumentos o fuentes.

---

# Continuidad vigente · campaña de ingesta IC04–IC23 cerrada · 27/10/2026

**Revisar primero** [AB Atlas CURRENT](../ab_atlas/CURRENT.md) y [el cierre IC04–IC23](../research/ABH_INGEST_CONTINUATION_20261027/REPORT_IC04_IC23_FINAL.md). Se ha consumido el permiso de **20/20 ciclos IC04–IC23**, en `research/pfl-codex-contributions-20261027`. Historiales separados y anteriores: **ChatGPT AB-H45 (45), Codex CDX (9), ChatGPT IC01–IC03 (3)**. No modificar `main` ni tratar estos conjuntos como una sola campaña.

**Implementado y probado localmente:** almacenamiento privado POSIX resistente a enlaces simbólicos, validación de longitud de HTTP, limpieza de escritura parcial, permisos privados y preflight; identidad técnica **`capture_id` por captura**, no por persona; auditoría de SHA, longitud y revisiones contra manifiesto con manejo de duplicaciones, legados, huérfanos y JSONL incompleto. La consola `python -m politics_fantasy.private_audit_cli --root <root_posix_privado>` solo imprime agregados, y exit 0 significa integridad/revisión local operativa, **no autorización para publicar ni puntuar políticos**. Tres tests E2E ficticios locales han pasado.

**Evidencia QA:** IC21 ejecutó **67 tests Python focalizados + 14 subtests, 110 JS**, todos PASS. La suite completa de Python llegó a alrededor del 58 % y agotó el límite de ejecución, sin fallo visible; por ello **no está certificada como PASS**. El workflow opcional incluye nuevos tests, pero **GitHub Actions no se ha disparado**. El importador seguro es **solo POSIX/Linux**; Windows nativo rechaza de manera explícita; la demo de juego en Windows no cambia. No hay ingesta real mediante `POST /api/ingest`, que todavía no existe.

**Atlas:** lote 0020 añadido después de 0019, con 20 runs y tres incidencias pendientes. La lectura de ambos deltas reales y controles estructurales del lote nuevo pasó. El validador Python canónico del **estado exacto GitHub con 20 lotes sigue pendiente** (la última comprobación local de 19 usó 0019 reconstruido, no sus bytes exactos). No atribuirle un SHA canónico nuevo no calculado. Los originales nominativos nunca se subieron a GitHub.

**Sin cambios de puntuaciones científicas ni producto:** V4 **36,90 %**, CT2 **29/100**, VSDS **1/3**, N1/N2/N3 nuevos **0**, gates **0/6**. `NO VOTAN` continúa pendiente de evidencia semántica institucional, `first_public_at` y licencias de originales tampoco acreditadas.

**Próximos resultados discriminantes, sujetos a nueva autorización de 5–15 ciclos:** rerun en checkout fresco de CI completo y Atlas Python sobre bytes actuales, prueba de recuperación ante terminación de proceso, revisión de derechos/publicación original y eventual diseño seguro de operador de captura autenticado. Aplicar R5, no consumir cuotas artificialmente.

---

## Historial anterior a la campaña IC04–IC23

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
