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

## Continuación de revisión E2E · vínculo de censura + recibo SHA (NONCYCLE)

**Incidencia nueva y alcanzable:** el consumidor `report()` emitía por una
rama `temporal.synthetic_followup_end_witnesses=1`, y por otra
`procedure.unknown_followup=1` en el corte tardío. Ambos datos estaban
individualmente bien definidos, pero no se reconciliaban por *identidad de
episodio*; la coincidencia de los escalares `1` no podía demostrar censura
observada siquiera dentro del fixture. Una reducción de cada módulo a
agregados descarta el vínculo que debe contrastarse.

**PREPATCH 1**, test `test_join_stage_episode_and_temporal_followup_by_exact_id_at_asof`:
Python código SHA `027b586387a892ff2f7c86a34080fe5799f423cec40d0fb7db9d0c230d3ce335`,
test SHA `4b3672ff0b7789bae15cec287c06a2398b7aac631c73585a53ec37805f1c2114`;
**1 FAIL** con `KeyError: followup_reconciliation`. Distinguir: el fallo
demuestra capacidad ausente, no un falso negativo previo del contrato
de estados de entrada. Se implementó dentro del MISMO consumidor, sin nuevo
módulo ni nuevo estimador, una vista derivada que mantiene internamente
el `TemporalLedger.snapshot`, su lista de `FileReceipt` y los
`EntryEpisode` antes de agregarlos.

**Identidad explícita del fixture, no heurística:**
`(source_id=SYNTHETIC_PROCESS, family=PROCESS, local_id=ENTRY4,
source_record_id=FOLLOWUP_END_FOR_ENTRY4)` se enlaza mediante
`SYNTHETIC_FOLLOWUP_CROSSWALK` server-owned exactamente a
`episode_id=SYNTHETIC:ENTRY4`. Ambos SHA **no son iguales**: el testigo
de fin de observación usa el contenido inventado `SYNTHETIC_PROCESS_v2`,
la entrada tenía un `entry_sha_claim` distinto para
`SYNTHETIC_STAGE_DOCUMENT`. El puente no los confunde; valida el SHA
temporal contra **su propio** `FileReceipt` y su captura, y rechaza
identidades de episodios ausentes, pendientes o terminados por una decisión.
`audit_lab` permanece intacto: su `unknown_followup` tardío sigue siendo
1; la vista nueva documenta un testigo de censura ficticia y resta ese
uno solo del subconjunto de pendientes de seguimiento sin testigo.

**PREPATCH 2** detectó que el nuevo campo `source_receipt_checked=True`
era demasiado amplio: también se mostraba en el corte temprano sin ningún
testigo de censura visible, y podía parecer que se autenticaba el SHA de
las etapas administrativas. Código SHA
`18392b331838233dffd8fbc606f6bbbfc36e38817e7227144f2da2df22c6d5ab`,
test SHA `1af069ef761337f1d7818f95c84cbc44351c1b633745d402fe480b6ebce00fed`:
**1 FAIL** semántico. Se sustituye por
`temporal_witness_fixture_receipt_checked` (false temprano, true tardío)
y `stage_documents_authenticated=false` en ambos; ni un SHA local ni un
testigo inventado certifican el original administrativo.

**PREPATCH 3**, falsador `test_fake_censor_witness_cannot_join_pending_case_or_wrong_digest`:
SHA previo Python `28c5244f05b7af00ef2ea135aa68f7c67c7969c820a894e6785442dc279a9cd9`,
test SHA `ae13cf836b012d22c1fd43277509b0cad77f95fc31108da1aca036fa2fcd063a`;
la primera ejecución falló por **ausencia del tercer valor de retorno**
(`ValueError: not enough values to unpack`), no porque un SHA falso
atravesara ya el algoritmo. Tras incorporar el mapa inmutable de recibos,
se valida efectivamente con dos mutaciones sintéticas: un testigo
reapuntado a la entrada 5 PENDIENTE y un SHA de testigo que no casa con su
propio recibo. Ambos son rechazados por errores distintos,
`CENSOR_WITNESS_EPISODE_LINK_INVALID` y
`CENSOR_SOURCE_RECEIPT_BINDING_MISMATCH`. No hay joins a casos reales ni
fuentes empíricas, la respuesta JSON presenta solo sumas sintéticas.

| Vista derivada; exclusivamente ficticia | Corte `early` | Corte `late` |
| --- | ---: | ---: |
| Fin de observación enlazado por ID, revisión y recibo | 0 | 1 |
| Seguimiento desconocido **sin** tal testigo | 4 | 0 |
| Pendiente probado, **no** censura | 1 | 2 |
| Inadmitido, **no** censura | 0 | 1 |
| Derechos autentificados para registrar casos reales | No | No |

El hecho de que `unknown_without_censor_witness=0` tardío en el ejemplo
no implica ausencia de ignorancia sobre la población real. La
clasificación es de **un fixture con cinco entradas deliberadamente
construidas**, no una tasa de riesgo ni población española. En ambos cortes
`right_censoring_independently_attested=false`, `R5=STOP_R5`, 0/6 gates.

**Nueva pista R29, sin acceso a distribuciones:**
[Asturias SAIP — estadísticas mensuales](../research/PFL_SYSTEM20_20261031/ROUND_REPORT29_ASTURIAS_SAIP_PREACCESS_20261101.md),
ficha oficial de datos.gob.es con cinco formatos, no cinco vintages ni
registro inicial independiente. `NEW_CATALOG_METADATA_ONLY_STOP_LOCAL_R5`.
Comparada con R11/R13/R14/R26/R27/R28; no GET de editor ni originales.

## Revisión posterior PR22: retroactividad por etapa aún no conocida

Una auditoría adversarial independiente sobre HEAD
`52d8025338b04a68fb98b5c7e1be13560e679263` de la PR #22 localizó
un fallo **nuevo y alcanzable en el helper** `_reconcile_followup`. El
contrato base `procedural_stage_accounting.audit_lab` filtra `StageAct` y
`PendingWitness` por `safe(observed_at) <= as_of`, pero el nuevo helper
rechazaba una evidencia de censura visible con el simple predicado
`episode.acts or episode.pending`, incluso cuando esos otros documentos
solo se conocerían en fechas posteriores al corte. También impedía censura
ficticia tras una etapa no terminal ya conocida (p. ej. `ADMITTED`).

**PREPATCH congelado:** test parametrizado
`test_future_or_nonterminal_step_cannot_invalidate_visible_censor_witness`
con tres modificaciones de `SYNTHETIC:ENTRY4`, todas legales según
`EntryEpisode`: un PendingWitness capturado **04/11/2026**, un StageAct
`APPROVED` capturado **05/11/2026**, y una etapa `ADMITTED` no terminal
capturada en septiembre. El corte de diagnóstico es el mismo
`2026-11-01T12:00:00Z`; el `TemporalLedger.snapshot` y `audit_lab`
originales no cambian su diagnóstico (`unknown_followup=1`, censura
derivada tardía=1). Sin embargo, **3 FAIL esperados** en el helper integrado
con `CENSOR_WITNESS_EPISODE_LINK_INVALID`. Huellas PREPATCH:
`scientific_integration_lab.py`
`7cdd6c92447f20029242fb72c4c079d5a8f9ac8926bab0a80b7f118367d311a9`;
test inicial con dos casos
`fe32aa33c0e854ec4e29f6ec12ee0a51cfebf30d47f01486449c6dff8ebb7414`.
La tercera variante `VISIBLE_ADMITTED` también se ejecutó roja antes de
modificar código.

**Corrección integrable sin nuevos módulos:** el helper importa `safe`,
`TERMINAL`, `utc`, `day` y `legal_civil_date` del contrato ya utilizado.
Solo una etapa **terminal** conocida en el corte, o un PendingWitness
documentado y observado antes de él, contradicen la vista de censura;
una transición no terminal permitida no es por sí misma decisión final.
La identificación de episodio sigue exacta, el SHA del FileReceipt sigue
siendo del **activo correspondiente** y el resultado continúa declarando
`real_censoring_attested=false`.

**Controles positivos añadidos:** dos pruebas confirman que si la entrada
ficticia realmente tiene, en el mismo corte, un pendiente o una decisión
`REJECTED` observados, la vista de censura los rechaza. Los tests históricos
PP04 y Node no son reejecutados sin cambios relevantes en esos módulos.
**R5 STOP, 0/6 gates, 0 AB, 0 originales/PII**.

**R30 preacceso, fuera del pipeline:**
[Catálogo Junta de Castilla y León: sugerencias y quejas](../research/PFL_SYSTEM20_20261031/ROUND_REPORT30_CYL_SUGERENCIAS_PREACCESS_20261101.md)
contiene metadatos sobre Tipo, Estado, fecha, origen, unidad, provincia y
referencia. Es identidad documental nueva frente a R5–R29, pero no
padrón independiente de recepción ni derecho adjudicado por activo. No
se visitó ninguna distribución ni editor sujeto a condiciones.

## Falsador PREPATCH: dos agregados correctos unidos en horizontes distintos

La revisión adversarial posterior al HEAD PR22
`11ecfd92facf8c30a33dafa77a8aca92db0d7ebe` identificó un **fallo
material nuevo de composición** en `_reconcile_followup`: el `Snapshot`
temporal porta su propio `as_of`, pero el dict de
`procedural_stage_accounting.audit_lab` no lo incluye. Dos resultados
individualmente válidos podían unirse sin comprobar si correspondían al
mismo corte. En una llamada sintética verdadera, el snapshot tardío
`2026-11-01T12:00:00Z` con `unknown_followup=4` del corte temprano produjo
un diagnóstico *híbrido* de **1 testigo de censura enlazado, 3
desconocidos restantes, 1 pendiente y 0 inadmitidos**, mientras que la
composición coherente tardía mostraba 1, 0, 2 y 1. No se demostró
explotación por un cliente remoto: el endpoint público del laboratorio
selecciona ambos relojes conjuntamente, aunque el helper es alcanzable por
otros consumidores internos.

Oráculos añadidos ANTES del parche:
`test_reconcile_rejects_genuinely_valid_procedural_output_from_wrong_cut`
y `test_reconcile_cannot_accept_procedural_counts_not_derived_from_episodes`
fallaron **2/2 PREPATCH**, porque el helper aceptaba respectivamente un
agregado de corte anterior y un contador adulterado. SHA PREPATCH Python
`5ac507e08ce04bba43edb087f0a883ee270d85a9989e0075f609304f50a873d3`,
test `f60ff1478cabb782832dbed520e8ee8414be5d3d69cb03ac5537a2ebc0872143`.
No se usaron originales ni datos de casos españoles.

Corrección: sin tocar `audit_lab` ni crear módulos, la frontera E2E vuelve
a ejecutarlo con **los mismos episodios y exactamente `snapshot.as_of`**;
compara el contrato de salida COMPLETO y rechaza el cruce con
`FOLLOWUP_CUT_MISMATCH`. Un tercer test focal modifica solo el reloj
interno del consumidor y comprueba **HTTP 503 y `Cache-Control: no-store`**
en lugar de 200 con una interpretación histórica mezclada. Los controles
positivos `early`, `late`, PP04, derechos de distribución y Node permanecen
inmutables; la nueva inspección es de ingeniería sintética, **no apertura
de derechos ni acreditación de censura real**.

## R31: resultado documental negativo, sin nueva cohorte

La [FAQ oficial del agregador](https://datos.gob.es/es/preguntas-frecuentes)
documenta explícitamente que una solicitud de datos recién recibida no es
todavía pública y solo se publica en un estado posterior de asignación.
Esto confirma, para ESE procedimiento, la diferencia entre recibir y
publicar y refuerza la definición operacional de población de entrada.
No permite deducir cifras ni reglas de publicación de otros editores.
Ninguna ficha nueva encontrada entre metadatos R5–R30 ofrece el padrón
independiente, dos vintages auténticas y licencias exigidos por R5.
Informe: [R31 PREACCESO STOP](../research/PFL_SYSTEM20_20261031/ROUND_REPORT31_CATALOG_SELECTION_GATE_20261101.md).

## Nueva regresión E2E PP04: las dos poblaciones editoriales deben llegar al HTTP

**Hallazgo incremental y observable:** en el HEAD anterior de PR22
`707f5d1ecaa0eb6445d28d706319b56cbd9f8a83`, el parser real
`audit_pp04_dual_parsers` calculaba un recuento explícito
`line_parser_unplanned_entries_source_local` para las iniciativas
`NO INCLUIDAS`, en un universo distinto de `planned_count`. Pero el
consumidor `scientific_integration_lab.report` omitía esa clave al proyectar
el objeto `pp04` hacia el HTTP. El indicador
`not_included_4221_excluded=True` no sustituye el recuento de otras
secciones NO INCLUIDAS: confundía exclusión de 4.22.1 del universo de
previstas con preservación completa de la población documental alterna.

**Falsador PREPATCH congelado:**
`test_pp04_http_consumer_must_preserve_both_source_local_documentary_populations`
en `tests/test_synthetic_scientific_integration_lab.py`. Con llamadas
verdaderas a `report(cut='early'|'late')`, comprobó que `early.pp04=None`
y que `late.pp04.planned_count=2`, pero falló **1/1 ROJO** por
`KeyError: 'line_parser_unplanned_entries_source_local'`. Código Python
SHA previo **`35574fefd7b6b3f28d5c49063fb737d40a253320022ed8938ea47e23935f9844`**;
test PREPATCH **`f32ea59c7160aa15f2abb4a0e3488850769de4bb9e929f591ff27b8ef96ceee8`**.

Corrección **en el mismo consumidor**, sin tocar los parsers PR21 ni sus
109 tests históricos: proyección de la clave source-local exacta junto con
`planned_count`, `approved_count`, `pending_unsplit_count` y el
indicador de sección 4.22.1 excluida. Ambos recuentos se mantienen
**sintéticos, documentales y disjuntos por heading de IAEN**; no se suman
para construir una población inicial de expedientes ni se inferiere que
`NO INCLUIDAS` signifique solicitudes denegadas o decisiones negativas.
`item_crosswalk_verified=False`, derechos `reuse_admitted=False`,
`independent_all_received_denominator=None`, `R5=STOP_R5`.

**QA POSTPATCH:** dos tests focales nuevos **2/2 PASS**, el segundo con
servidor HTTP real en loopback, `cut=early` sin información posterior,
`cut=late` con 2 previstas y 2 NO INCLUIDAS, respuesta `Cache-Control: no-store`
sin datos reales; suite completa del consumidor actualizada **30/30 Python
PASS**, `compileall` Python y `node --check` PASS. Las pruebas históricas
**41/41 Node y 109/109 PP04 no se han repetido** porque esos módulos no
cambiaron; no se presenta QA nominal como certificación científica.

**R33 preacceso documental, NO nueva cohorte:** criba oficial de índices
`datos.gob.es` frente a R5–R32, que reencontró BDNS (familia R11),
Madrid AIP (R11) y AGE (R32), todos ya excluidos para R5. La [ficha BDNS](https://datos.gob.es/es/catalogo/e05250001-base-de-datos-nacional-de-subvenciones)
describe concesiones publicables con retención, no el censo original
externo de solicitudes con denegadas/pendientes. La [FAQ de datos.gob.es](https://datos.gob.es/es/preguntas-frecuentes/que-significan-los-estados-de-la-seccion-disponibilidad-de-datos)
documenta que, para ese portal, `Recibido` aún no es público. No se han
abierto distribuciones, originales, editores condicionados ni PII.
**`NO_DIFFERENTIAL_ALL_RECEIVED_SOURCE_STOP_LOCAL_R5`, 0/6 gates, 0 AB**.

## PR22 · experimento controlado de equivalencia observacional entre Python, Node y HTTP (NONCYCLE)

**Objeto incremental, no reparación de un bug previo.** El comparador PR18
`compare_capture_hypotheses` ya demostraba dentro de Python que dos hipótesis
con las mismas publicaciones por canal admitían signos distintos de entradas
latentes. La nueva capacidad comprueba **independientemente en el proceso Node**
que el conjunto de cuatro celdas, ventanas, relojes de captura, identidades
de fixture y escenarios hipotéticos derivados de PR18 **es exactamente el
mismo** antes de exponerlo por el consumidor Python y la ruta HTTP existente.
Un hash autoconsistente o coincidencia de sumas no equivale a este contrato.

El diseño experimental es estrictamente ficticio: **antes de la reforma**
(`01/09–30/09/2026`) aparecen ocho publicaciones `PAPER` y dos `ELECTRONIC`;
**después** (`01/10–30/10/2026`) ocho `PAPER` y doce `ELECTRONIC`.
Ambos escenarios comparten por completo estas cuatro observaciones y el
instante de captura local artificial `31/10/2026 12:00Z`. Cambia únicamente
el mecanismo hipotético de observación, no los datos visibles:

| Protocolo rival sintético | Cobertura supuesta antes | Cobertura supuesta después | Entradas ficticias implícitas antes → después | Diagnóstico condicionado |
| --- | --- | --- | --- | --- |
| `CAPTURE_EXPANSION` | 1/2 | 1 | 20 → 20 | Sin cambio en el total latente construido |
| `STABLE_CAPTURE` | 1/2 | 1/2 | 20 → 40 | Crecimiento en el total latente construido |

**La igualdad de las publicaciones no identifica qué mecanismo es correcto.**
Los pares 20→20 y 20→40 son **estados latentes inventados bajo supuestos
deterministas**, no estimaciones de solicitudes reales, totales de registros,
efectos de reforma, tasas de éxito o denominadores certificados. Un testigo
discriminante exigiría un inventario independiente de todas las entradas de
la misma institución, régimen, ventana y canal, junto con el mecanismo de
publicación/captura, derechos por distribución y fechas históricas
atestadas. Ninguno está presente aquí.

**Circuito real reutilizado:** `_capture_rivals()` sigue invocando los dos
`audit_regime_capture` y `compare_capture_hypotheses` de PR18. Construye un
recibo **solamente sintético de desafío IPC**, que incluye por hipótesis las
cuatro publicaciones, conteos latentes condicionales, signos, IDs de fixture,
ventanas, capturas, `first_public_at=null`, `independent_registry_total=null`
y derechos/crosswalk no acreditados. `scientific_integration_warehouse.mjs`
valida el esquema exacto, aplica un oráculo Node determinista *separado* de
los cálculos Python, exige todos los estratos y recalcula las dos parejas
latentes bajo las fracciones indicadas. Python vuelve a validar el objeto
Node completo y solo entonces responde en
`GET /api/scientific-integration-lab?cut=late`. En `cut=early` el resultado
del experimento es `null`; una proyección futura enviada al Node es rechazada.

Los IDs `SYNTHETIC:BEFORE_REFORM:PAPER`, etc. identifican **estratos del
experimento**, no los activos `SYNTHETIC:PAN24`, `SYNTHETIC:IAEN24`, los
actores `SYN:ACTOR` ni los episodios de registro `SYNTHETIC:ENTRY*`.
La comprobación de igualdad de IDs dentro del fixture **no crea un crosswalk
interinstitucional** ni una fuente independiente. Tampoco altera los
recibos `FileReceipt`, la reconciliación de censura, las negativas,
el sistema de roles, ni el gate de reutilización de PR16.

**Oráculos nuevos, sin fingir PREPATCH de defecto inexistente:** el test
`test_controlled_observational_equivalence_two_dgps_one_public_projection`
prueba que las cuatro publicaciones son iguales y los signos latentes
opuestos. Ocho variantes adversariales modifican por separado: distribución
por canal con el mismo total, identidad de fuente sustituyéndola por PAN24,
captura futura, ventana de exposición, conteo latente incoherente, bandera
de derechos, declaración de primera publicación y signo hipotético. Node
debe rechazar todas; otra prueba rechaza el desafío tardío en el corte temprano.
El test de ruta HTTP local comprueba `200` para los dos horizontes,
`null` temprano, diagnóstico sintético tardío, `no-store`, y `503` al
inyectar una deriva de canal que mantiene la misma suma total. Ningún test
consume archivos originales o PII.

**QA exclusiva de once pruebas nuevas:**
`PYTHONPATH=src python -m pytest -q tests/test_synthetic_scientific_integration_lab.py -k controlled_observational_equivalence`
→ **11/11 PASS**, con **30 tests históricos deseleccionados**. `node --check`
del puente, `py_compile` del módulo integrado y `git diff --check`: PASS.
El primer intento de pytest sin `PYTHONPATH` no colectó ninguna prueba
(`ModuleNotFoundError`); no se presentó como rojo prepatch científico.
No se repitieron las suites completas históricas de Node ni PP04.

**Resultado:** nueva capacidad de falsación transversal de dos mecanismos
ficticios, **NONCYCLE**, sin atestación de primera publicidad, sin fuente
de derechos, sin denominador de todas las entradas, sin estimando empírico,
sin scoring y sin promoción de los sistemas externos. **R5 STOP,
0/6 gates, 0 AB científicos; no main, CI ni despliegue.**
