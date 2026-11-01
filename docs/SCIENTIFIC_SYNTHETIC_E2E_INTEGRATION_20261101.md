# PFL · Integración científico-computacional E2E estrictamente sintética

**Fecha: 1/11/2026. Checkout independiente:** `PFL-SCIENTIFIC-E2E-20261101`.
Base exacta PR #21 `7e1b8480d49879dcb52e9396bd8c32adc5a4ad6f`
(PP04C ya auditada; sus **109/109 tests son históricos** y no se repiten
sin cambios en el módulo). Se trajeron solo los módulos y tests científicos
de PR #16 `f20f2a30a88946aa5b75feb0c0e52f4f39d513ae`, PR #18
`1a7e1b1b9e0661d78229fe4266f257a148ebe4c6` y PR #19
`f284c2de9128dc5a70710359de8d53f90f693a1d`, sin fusionar sus `HANDOFF`,
índices o autorizaciones parcialmente incompatibles. **0 originales, casos,
PII, distribuciones, HTTP externos, cookies, nuevas autorizaciones o datos
empíricos. R5 STOP, 0/6 gates y 0 AB científicos consumidos.**

## AB 3.2.1: A–J de un bloque de INGENIERÍA, NO ciclo AB-R/AB-P

**A / pregunta concreta.** ¿Puede una única ruta local enlazar PP04,
`source_id` exacto, SHA por byte, derechos por distribución/propósito, reloj
bitemporal, recepción/pendientes/inadmisión/censura, rivales de selección,
warehouse Node y HTTP sin convertir pruebas sintéticas o recuentos editoriales
en un denominador certificado?

**B / baselines fuertes y rivales.** PR #21 tenía los dos parsers PP04, pero
no había consumidor conjunto. PR #16 mantenía derechos `reuse_admitted=false`;
PR #18 comparaba regímenes sintéticos; PR #19 mantenía claims de derechos
del warehouse sin atestación. El servidor PR #7 ofrecía rutas de diagnóstico
independientes, no PP04→Node→HTTP. Rivales de implementación: (B0) solo
módulos desacoplados y no falla nada porque no existe consumidor;
(B1) nuevo consumidor junta por igualdad de recuentos o string `rights`;
(B2) nuevo consumidor mantiene identidad, relojes y negativas, pero divulga
identificadores de fuente antes del corte; (B3) orquestación fail-closed con
dos horizontes y falsadores comparables. No se presume B3 antes de QA.

**C / fixture y oráculos congelados.** Dos textos inventados con cabecera
`SYNTHETIC DOCUMENT FIXTURE`: PAN 2 pares Objetivo/Ministerio; IAEN 2
planificadas (I Aprobadas=1, II Pendientes=1), 2 NO INCLUIDAS entre
`4.1.2` y `4.22.1`, sin crosswalk. Activos tipados
`SYNTHETIC:PAN24` y `SYNTHETIC:IAEN24`, cada cual con SHA256 de sus
**propios bytes**, mismo namespace exacto en gate de derechos, ledger temporal
y Node (sin sustituir `:` por `_`). Los dos cortes inventados de conocimiento
son **2026-10-15T12:00:00Z** (`early`) y **2026-11-01T12:00:00Z** (`late`).
La captura ficticia de PP04 ocurre el 31/10: `early` no revela ni sus
conteos, ni IDs o SHA. La simulación de instituciones/actores/decisiones
usa temporalidad de validez y de conocimiento distintas.

**D / consumidores ya ejecutables.**

```
GET /api/scientific-integration-lab?cut=early|late&scenario=...
               | host loopback, GET acotado, Cache-Control:no-store
               v
scientific_integration_lab.report (Python, sólo fixtures del servidor)
   +---- audit_pp04_dual_parsers (PR21)          - source-local, 0 joins
   +---- assess_distribution_rights (PR16)      - por activo/SHA/uso, BLOCKED
   +---- FileReceipt + TemporalLedger           - as_of y revisiones
   +---- procedural_stage_accounting.audit_lab  - inadmisión/pending/unknown
   +---- compare_total_claims                   - granos incompatibles
   +---- PR18 audit_regime_capture + compare_capture_hypotheses
   +---- synthetic_institutional_demo.report    - vínculos no autenticados
   +---- Node IPC (stdin JSON sólo sintético, 4 KiB, 5s)
            +-- evidence_warehouse.mjs PR19: source/entity/role/event,
                asOf(cutoff), rolesAt(cutoff), auditBundle/evidenceGate,
                digest SHA por bytes de CADA asset, allowlist de hashes
               v
        JSON agregado, R5 STOP, sin filas / originales / publicación
```

Hay una segunda entrada CLI offline de solo lectura que usa **el mismo
orquestador**: `python scripts/run_scientific_integration_lab.py --cut early`.
El servidor no acepta URLs, rutas, textos, identidades de personas o fechas
arbitrarias del cliente; solo `cut=early|late` y
`scenario=baseline|rights_spoof|privacy_probe`. Node exige el SHA recomputado
de un manifest ficticio y de los dos textos *registrados en el código*,
rechazando contenido arbitrario con una etiqueta `SYNTHETIC` prestada.

**E / freeze y causalidad del test.** El primer test del nuevo consumidor,
`tests/test_synthetic_scientific_integration_lab.py`, fue escrito ANTES
del módulo de producción: SHA inicial
`9d5baf7b5d2009c648f93abc3f2055d58ee881fb041b95ccc529b657d0cb6ad4`;
su colección falló por `ModuleNotFoundError`. Esto certifica que la
capacidad no existía, **no** que hubiese un bug de derechos previo. Una
primera implementación pasó 9/9. A continuación se elaboraron oráculos
adversariales prepatch, con fallos reproducidos antes de reparar.

**F / falsadores adversariales efectivamente fallados.**

| Riesgo NUEVO alcanzable en el consumidor | Resultado PREPATCH | Reparación observable |
| --- | --- | --- |
| `early` ocultaba PP04 pero exponía IDs y SHA de los dos assets que solo serían capturados a finales de octubre | **1 FAIL**; código Python `cc5c666216b5ef43420237caa9fcb0f8a6288e9f16c06de6d52cf750aae68d64`, Node `bcf56ab4c4c772bb3300adf92a65735e158a1e1dc0b4ea25eeaa85a83790e554`, test SHA `3470fdbf13afcb6175e42628eaebb19a1071e1d3f18cbec38722b2941a40e7fe` | Gating por `TemporalLedger` **también** de metadatos públicos JSON, suprimir detalles de Node tras comparar SHA en servidor; `early` no divulga identificador, SHA o conteo futuro. |
| Node permitía texto arbitrario introducido tras un prefijo `SYNTHETIC DOCUMENT FIXTURE`, con SHA autoconsistente, aunque no era uno de los dos fixtures registrados | **1 FAIL** en el mismo prepatch, Node devolvía éxito | Allowlist inmutable de hashes de **ambos** contenidos sintéticos + SHA recomputado; un digest autoafirmado no incorpora un original. |
| La primera capa temporal transformaba `SYNTHETIC:PAN24` en `SYNTHETIC_PAN24` aunque derechos/Node conservaban el namespace original | **1 FAIL**, código SHA `e5b295d4453d6b1868ce2f59318ca90bb4bc454ddea50fea9bfa40774304388d`, test `128487f223df55e1416f60ff394124eda6fd0c9a022d58e4f9553ae0cbb245ca` | `source_id` exacto en `FileReceipt`/`TemporalRecord`; `pp04_source_ids_seen` ordenado como recibos de assets sin inferir crosswalk de iniciativas. |
| Se añadió al ledger un testigo explícito **inventado** de fin de seguimiento de una entrada; el consumidor confundió todos los registros del origen con una sola revisión | Primera regresión: **8 FAIL / 5 PASS**, por selector `source_id` demasiado amplio; el test del nuevo witness solo había fallado antes por campo ausente, no por error empírico | Seleccionar revisión por `kind + source_id + source_record_id`; el testigo de seguimiento es un `EVENT` aparte, no otra versión `ENTITY`. |

**G / QA focal e interoperabilidad.** El consumidor nuevo tiene tests de
dos cortes, `INCLUIDAS/NO INCLUIDAS`, negativos y pendientes, censor witness,
dos modelos rivales con idénticos observados, denominadores incompatibles,
spoof de derechos, privacidad recursiva Node, SHA mutado, HTTP loopback
GET/autorización Host/query/cache y error Node→HTTP 503. Tests originales de
los tres módulos importados se ejecutan SOLO para validar su composición
en este nuevo checkout, no como nueva conquista científica. El reporte
de pruebas, compilación, SHA postpatch y HEAD se registra al final de la
ronda; resultados históricos PP04 (109) no se imputan como ejecutados aquí.

**G2 / revisión adversarial independiente posterior.** Otros dos auditores de
solo lectura detectaron tres defectos adicionales del NUEVO consumidor.
Primero, `scenario=rights_spoof` con `cut=early` tomaba
`visible.source_count !== 2` como señal de que el origen RAW falsificado era
visible. Pero ese corte solo admite una fuente ficticia temprana; el
consumidor acusaba una infracción inexistente y terminaba en HTTP 503.
Se congeló test focal SHA PREPATCH Node
`8beb938cae9a3f7883e562b2ef7d7a318f848812f1c90b624c10defaf7879aee`,
test `b070c4c2fc7c4c756ab8259c6c9ebe5d6b6983d59518629163ac9549455a04e2`:
**1 FAIL esperado**. La corrección compara el conteo de fuentes visibles
en el mismo corte con/sin el ID EXACTO de la fuente sospechosa, sin valor
global supuesto de 2. Segundo, un revisor detectó que `early` exponía el
booleano `assets_bound_to_fixed_fixture=true` aunque los bytes y SHA
estaban bien ocultos: el campo afirmaba la existencia *corroborada* de dos
assets futuros. Se amplió el test de privacidad temporal ANTES de corregir:
**1 FAIL esperado**. El booleano solo puede aparecer en `late`.

Tercero, la salida JSON del proceso Node se aceptaba con esquema abierto:
tras confirmar unos pocos indicadores, Python propagaba cualquier otra
clave, incluidos hipotéticos `real_denominator=5`, `first_public_at_real`
o `source_identity_crosswalk_certified=true` procedentes de un proceso
alterado o de deriva entre versiones. Se congeló un **falsador de IPC
realmente rojo** con `subprocess.run` simulado que devuelve una respuesta
Node autoconsistente pero científicamente falsa. SHA Python PREPATCH
`0ef89680724f854eac04b2a9da2ae3872db27811875517bc5a1db91bd15ffbeb`,
test SHA `c1c8517d972dbfab53ef0648ee5244e7a3bef5a3103041f76da7020e65236319`;
**1 FAIL** porque la promoción ficticia alcanzaba el JSON HTTP. Ahora la
frontera IPC exige un conjunto cerrado de claves, null/false para todos los
campos de autorización real y cardinalidades exactas por el corte fijo;
el fallo es una divergencia 503, NO una respuesta que simule corpus real.
Esta es una vulnerabilidad de integración/versionado de componentes, no
evidencia de entrada maliciosa desde Internet ni una fuente de datos real.

**QA final tras esas correcciones, con nuevos tests focales y contratos
importados:** **41 pruebas Python** en
`test_synthetic_scientific_integration_lab.py`,
`test_r5_asset_rights_gate.py` y `test_r24_regime_exposure_oracle.py`, más
**41 Node** en `test_r25_untrusted_rights_claims.mjs`,
`test_evidence_warehouse.mjs` y `test_evidence_privacy_recursive.mjs`.
`compileall`, `node --check`, índices/Atlas/registro de logros, revisión
Git y HEAD remoto quedan documentados por los recibos de cierre. No se ha
repetido el bloque histórico PP04 109/109, porque la parser API permanece
intacta; sí se invoca desde el E2E cada vez que se prueba `cut=late`.

**H / resultado analítico del fixture, exclusivamente ilustrativo.**

| Dimensión | Corte temprano | Corte tardío | Qué NO demuestra |
| --- | --- | --- | --- |
| Documentos PP04 fuente-local | Ocultos; no SHA visible | 2 previstas (1 aprobada, 1 pendiente); 2 NO INCLUIDAS preservadas | 2/2 no es crosswalk PAN↔IAEN ni tasa de cumplimiento |
| Revisiones temporales del proceso ficticio | `v1` | `v2` | No certifica primera publicidad histórica real |
| JS roles sintéticos conocidos | 1 | 2 | No es censo de actores españoles ni información a disposición de agentes reales |
| Entradas de registro ficticio | 5 conocidas; una pendiente, 4 seguimientos sin terminal conocido | 1 aprobada, 1 inadmitida, 2 pendientes, 1 seguimiento desconocido | No aporta N independiente ni su mecanismo de observación real |
| Fin de observación sintetizado y tipado | No conocido | 1 testigo de seguimiento finalizado **inventado** y separado del terminal | No certifica censura derecha de un caso real; `unknown_followup` sigue 1 en el contrato de base |
| PR18 modelos rivales | No disponibles antes de captura | Misma proyección publicada compatible con tendencias verdaderas diferentes bajo supuestos | No identifica tendencia ni efecto causal real |
| Rights por activo y finalidad | No revelar avisos futuros | Uso `PUBLIC_AGGREGATE_DISPLAY` no cubierto por aviso sintético de `LOCAL_ACADEMIC_READ` | Ni ambos usos ni atestación del editor son derechos adquiridos |

**I / validez, separación de universos.** PP04 es una población editorial
de normas previstas, y el registro ficticio es una población separada de
entradas administrativas. `PopulationTarget` no contiene `PAN_PLAN_ITEM`
ni `PLAN_EDITION_ITEM`: es deliberadamente incorrecto forzar el conteo 2 a
`ALL_RECEIVED_REGISTRATION`, o igualar `Pendientes` a inadmisiones. El
contrato `compare_total_claims` rechaza dos unidades administrativas
incompatibles aunque su recuento inventado coincida. No existe identificador
oficial que enlace entradas, actores, decisiones, publicaciones y PP04;
los recibos de bytes solo vinculan los **dos artefactos del laboratorio**.
Un `Node audit.ok` no acredita autentificación externa, derechos, privacidad
de un corpus futuro ni denominador. El endpoint no debe exponerse a internet.

**J / decisión.** `INTEGRATED_SYNTHETIC_ENGINEERING_READY_REVIEW`,
**NONCYCLE**, candidato de PR DRAFT contra la base #21. No fusionar main
ni admitir originales. El Laboratorio es consumidor científico reproducible;
el Observatorio/Fantasy permanecen sujetos a R5 y no reciben nueva fuente ni
puntuación. Se aplaza el rediseño de interfaz.

## Nuevo preacceso R5, separado del test sintético

El hallazgo del catálogo nacional [Barcelona IRIS](../research/PFL_SYSTEM20_20261031/ROUND_REPORT28_BARCELONA_IRIS_PREACCESS_20261101.md)
es `NEW_INDEXED_CATALOG_IDENTITY_ONLY_STOP_LOCAL_R5`: título «gestionados»
no asegura población de todas las entradas, cadena CSV/XML anual no demuestra
vintages auténticas de una misma edición y licencia declarada en `datos.gob.es`
no adjudica condiciones del editor por uso/activo. Frente a Madrid R11/R26,
Córdoba R27 y otros R5, es nuevo índice, no nueva cohorte científica.
