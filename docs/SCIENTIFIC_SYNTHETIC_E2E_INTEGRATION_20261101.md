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
con las mismas publicaciones por canal admitían **clases de variación distintas**
en las entradas latentes (cambio nulo frente a cambio positivo), **no signos
matemáticamente opuestos**. La nueva capacidad comprueba **independientemente en el proceso Node**
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
Los pares 20→20 y 20→40 describen **trayectorias latentes incompatibles**
—estancamiento frente a crecimiento—, **no caída frente a subida**. Son construcciones inventadas bajo supuestos
deterministas**, no estimaciones de solicitudes reales, totales de registros,
efectos de reforma, tasas de éxito o denominadores certificados. Un testigo
discriminante exigiría un inventario independiente de todas las entradas de
la misma institución, régimen, ventana y canal, junto con el mecanismo de
publicación/captura, derechos por distribución y fechas históricas
atestadas. Ninguno está presente aquí.

**Circuito real reutilizado:** `_capture_rivals()` sigue invocando los dos
`audit_regime_capture` y `compare_capture_hypotheses` de PR18. Construye un
recibo **solamente sintético de desafío IPC**, que incluye por hipótesis las
cuatro publicaciones, conteos latentes condicionales, clases de variación, IDs de fixture,
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
prueba que las cuatro publicaciones son iguales y las trayectorias latentes
incompatibles: `ZERO_CHANGE_UNDER_ASSUMPTIONS` para `CAPTURE_EXPANSION`
y `POSITIVE_CHANGE_UNDER_ASSUMPTIONS` para `STABLE_CAPTURE`. El oráculo publica
`different_synthetic_trajectories=true`, **no** un indicador de signos opuestos.
Ocho variantes adversariales modifican por separado: distribución
por canal con el mismo total, identidad de fuente sustituyéndola por PAN24,
captura futura, ventana de exposición, conteo latente incoherente, bandera
de derechos, declaración de primera publicación y signo hipotético. Node
debe rechazar todas; otra prueba rechaza el desafío tardío en el corte temprano.
El test de ruta HTTP local comprueba `200` para los dos horizontes,
`null` temprano, diagnóstico sintético tardío, `no-store`, y `503` al
inyectar una deriva de canal que mantiene la misma suma total. En ese mismo
test se altera a continuación **únicamente** la clase de cambio de una
respuesta generada por Node real, simulando deriva del IPC: Python exige el
contrato exacto y HTTP devuelve 503, nunca un diagnóstico falso. Ningún test
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

## PR22 · equivalencia bitemporal de actor, rol y evento entre Python y Node (NONCYCLE)

**Nueva capacidad autorizada, no reparación de un defecto PREPATCH.** El
consumidor fijo `GET /api/scientific-integration-lab?cut=early|late`
contrasta ahora dos vistas independientes de las **mismas ediciones de un
expediente completamente ficticio**. Se reutilizaron
`TemporalLedger`/`FileReceipt` de Python, `evidence_warehouse.mjs` de Node,
el bridge ya presente y el endpoint HTTP; no existe módulo, ruta ni PR nueva.
No se ha usado material PAN/IAEN, originales, personas ni casos políticos.

**Custodia de dos ediciones:** `SYN:CHRONICLE_V1` y `SYN:CHRONICLE_V2`
pertenecen al emisor ficticio `SYN:CHRONICLE`. Las dos cadenas UTF-8 se
construyen en el fixture Python, con **78 y 86 bytes respectivamente**.
Sus SHA256 recomputados y comprobados también por el bridge Node frente a un
manifiesto sintético inmutable son:

| Edición | SHA256 de bytes ficticios | Captura local declarada | Primera publicación ficticia |
| --- | --- | --- | --- |
| V1 | `d652283f6dd552283d6187d03b255d1cde281ae7375697953e886ffe3cbaa245` | 20/09/2026 12:00Z | 19/09/2026 12:00Z |
| V2 | `40458358e15b6e354541cf88d238e95894bac8b2bd93bff33c91530c7c3d0836` | 31/10/2026 12:00Z | 30/10/2026 12:00Z |

Estos SHA acreditan integridad de **los bytes del fixture almacenados en este
proyecto**, no autenticidad de un editor, vigencia jurídica, derechos,
`first_public_at` real, ni pruebas de que los metadatos fueron emitidos por
una fuente administrativa. Python registra los recibos mediante
`FileReceipt(source_id,sha256,bytes,captured_at)` y Node verifica **los mismos
bytes, SHA e identificadores** antes de crear `W.source`, `W.entity`,
`W.role` y `W.event`.

**Identidad tipada declarada:** las dos versiones de evento usan
`(issuer='SYN:CHRONICLE', family='INITIATIVE', local_id='FILE_1')`,
con `revision=v1|v2`, `amendment_of` de V2 a V1 y fuentes/recibos
independientes. El contrato `TemporalLedger` valida conocimiento,
vigencia, SHA y referencias fuente-local de cada edición; el adaptador
resuelve la cadena `amendment_of` **solo porque la relación está escrita
explícitamente en el fixture**, no mediante nombre, fecha o SHA parecidos.
Node consume la misma cadena en `W.event` y la valida de nuevo.
La entidad del actor ficticio tiene **un solo ID fuente-local estable**;
los dos roles poseen intervalos disjuntos `01/09–01/10` y `01/10+`.
No se infieren equivalencias entre fuentes distintas del ejercicio.

**Matriz de observabilidad (`as_of` × `valid_at`)**, calculada por ambos
runtimes y comparada por igualdad estricta antes del HTTP:

| Corte de conocimiento | Tiempo de validez | Afirmaciones de rol visibles y vigentes | Revisiones documentales del evento conocidas | Evento lógico del fixture |
| --- | --- | ---: | ---: | ---: |
| 15/10/2026 (`early`) | 15/09/2026 | 1 (V1) | 1 (V1) | 1 |
| 15/10/2026 (`early`) | 10/10/2026 | 0 observadas | 1 (V1) | 1 |
| 01/11/2026 (`late`) | 15/09/2026 | 1 (V1) | 2 (V1 y V2) | 1 |
| 01/11/2026 (`late`) | 10/10/2026 | 1 (V2) | 2 (V1 y V2) | 1 |

**Cero afirmaciones visibles no significa ausencia de cargo.** Para el corte
temprano y vigencia 10/10, el oráculo emite
`role_observation_state=NOT_OBSERVED`, no «cargo inexistente»; la edición
correspondiente todavía no había sido capturada. El corte tardío conoce
la revisión V2 de un solo evento: **dos documentos no se convierten en dos
decisiones**. `valid_at` se consulta por dos fechas fijas sin habilitar
parámetros HTTP arbitrarios. El pipeline entrega solamente agregados
de observabilidad, versión `v1|v2` y advertencias de no certificación;
**no expone source_id, SHA ni bytes de este fixture por HTTP**, en especial
la edición futura en el corte temprano.

**Falsadores de capacidad, sin inventar rojo PREPATCH:** once pruebas nuevas
ejecutan el mismo protocolo Python y Node, el anti-lookahead, la sustitución
de revisión por `amendment_of`, los dos relojes, ocho alteraciones
adversariales (SHA, issuer, source_id, captura futura, publicación desconocida,
typed key ausente, amendment faltante y falsa certificación de crosswalk)
y la ruta HTTP real en loopback. En la prueba de divergencia, un proceso Node
auténtico devuelve un agregado deliberadamente adulterado en stdout;
Python detecta la discrepancia frente a su `TemporalLedger` y responde HTTP
**503** con `Cache-Control: no-store`, en vez de publicar el agregado
incorrecto. Los cuerpos HTTP se examinan también para comprobar que no
contienen los SHA, IDs o textos del fixture de cronología.

**Validación focal nueva:**
`PYTHONPATH=src python -m pytest -q tests/test_synthetic_scientific_integration_lab.py -k bitemporal_actor_event`
→ **11 PASS, 41 deseleccionadas**. Dos negativas previas del bridge de SHA,
seleccionadas individualmente como comprobación de compatibilidad tras
ampliar la frontera IPC, también PASS; no se han repetido las suites
históricas de Node ni las 109 PP04.

**Interpretación:** misma edición, bytes y referencias tipadas en dos motores,
pero ninguna autenticación real del emisor, derechos, versión oficial,
`first_public_at` histórico o censo independiente. Los indicadores
`first_public_at_real=null`, `rights_independently_verified=false`,
`source_crosswalk_certified=false`, `independent_denominator=null` y
`real_actor_identity_verified=false` son invariantes del nuevo oráculo.
**R5 STOP, 0/6 gates, 0 AB empíricos, sin scoring, originales, PII,
main, CI ni despliegue.**

## PR22 · identificación parcial S3: dos observaciones binarias y selección hipotética

**Alcance diferencial, NONCYCLE.** En el checkout de PR22 se añadió al
consumidor Python/Node/HTTP **existente** un tercer experimento sintético,
sin nuevo módulo ni ruta ni fuente de datos. El archivo suplementario
`/mnt/data/PFL_S3_repro/pfl_identificacion_parcial.py` no estaba disponible
en el entorno local de esta ejecución; las fórmulas y valores del oráculo
se reconstruyeron de forma conservadora a partir de los racionales exactos
aportados en la autorización. Por tanto no se afirma haber ejecutado el
código original del suplemento.

La observación ficticia solo tiene dos categorías binarias: antes
`positive=6, negative=4`; después `positive=7, negative=3`. Ningún
`negative` de este fixture representa una **inadmisión, desestimación, rechazo,
norma no aprobada ni otro outcome administrativo**. Tampoco equivale a
censura: el fixture registra **cero testigos de censura documentada** en
ambos periodos, sin restar negativas ni deducir cierres.

Definimos `q=P(Y=1 | observado)` y una razón de probabilidad de observación
hipotética `r=P(observado | Y=1)/P(observado | Y=0)`. Para `r>0` la proporción
subyacente compatible es

\[
 p=\frac{q}{q+r(1-q)}.
\]

El cálculo exacto con `fractions.Fraction` en Python y una implementación
**independiente** de racionales con `BigInt` y máximo común divisor en Node
produce, bajo el supuesto condicional `r∈[1/2,2]` en cada periodo:

| Valor ficticio | Racional exacto |
| --- | --- |
| Fracción positiva observada antes y después | `3/5`; `7/10` |
| Región de prevalencia antes | `[3/7, 3/4]` |
| Región de prevalencia después | `[7/13, 14/17]` |
| Cambio compatible después menos antes | `[-11/52, 47/119]` |

El extremo inferior del cambio se calcula `7/13 - 3/4`; el superior,
`14/17 - 3/7`, manteniendo ambos supuestos por periodo y sin postular un
acoplamiento no observado entre razones de selección. Al retirar **toda**
restricción de razón de observación, no quedan cotas informativas de
prevalencia más estrechas que `[0,1]`, ni del cambio más estrechas que su
clausura trivial `[-1,1]`. Son **regiones identificadas condicionales a
supuestos ficticios**, no intervalos de confianza, estimaciones de la
población española, efectos causales, evidencia de selección real ni tasas
de negativas institucionales.

**Frontera de IPC:** `_partial_identification_fixture()` crea únicamente
el esquema `pfl.synthetic_partial_identification_wire.v1` sin filas, personas,
textos, originales ni capturas auténticas. `_partial_identification()`
valida el esquema cerrado, los conteos exactos, el orden/cotas de `r`, los
contadores de censura cero y las banderas de autoridad inactivas; devuelve
fracciones canónicas `n/d`. El puente Node recibe el mismo wire, comprueba
independientemente sus invariantes y recalcula el oráculo completo
`pfl.synthetic_partial_identification_oracle.v1`. Python compara **todos**
los campos de retorno de Node, nunca solamente los extremos numéricos.
En `cut=early` **ambos** tienen `partial_identification_oracle=null`; en
`cut=late` la ruta ya existente `GET /api/scientific-integration-lab`
expone solo un agregado sin identidades ni datos originales. Deriva Node
en cualquier fracción, categoría o autoridad → excepción Python →
**HTTP 503**, nunca respuesta aparentemente certificada.

**Falsación focal nueva:** permutación del orden de los periodos y los campos;
intercambio o suplantación de `r` mínimo/máximo; cambio de cualquiera de
los recuentos de observación; transformación espuria de cero testigos de
censura en una categoría negativa; falsas declaraciones de denominador
independiente, derechos, primera publicación, causalidad o negativa
administrativa; transmisión de un oráculo futuro al corte temprano; y
mutación de `-11/52` a `-10/52` **después de ejecutar Node real** para
comprobar el rechazo por el servidor local. Los tests no contaminan los
fixtures PP04 ni el programa de equivalencia observacional anterior.

Los bloqueos permanecen en `independent_registry_total=null`,
`first_public_at_real=null`, `rights_independently_verified=false`,
`causal_effect_identified=false`, `empirical_estimand_admitted=false`,
`R5=STOP_R5`, **0/6 gates y 0 ciclos AB**. Ningún original público/privado,
persona, censo real o supuesto de causalidad entra en la ruta.

**QA focal de esta entrega:** `PYTHONPATH=src python -m pytest -q
tests/test_synthetic_scientific_integration_lab.py -k
's3 or controlled_observational_equivalence or bitemporal_actor_event'`
→ **35 PASS / 30 deseleccionados**. Incluye 13 pruebas seleccionadas por
`s3`, validación de paridad de racionales exactos, spoof de derechos,
denominador y tiempo, invariancia de orden, protección del corte temprano y
la respuesta HTTP 503 de un Node real deliberadamente divergente. `node
--check`, `python -m py_compile` y `git diff --check`: PASS. No se
reejecutaron las 41 pruebas históricas Node ni las 109 pruebas PP04.

**Recibos SHA-256 (bytes tras QA, antes del commit):** Python
`26aed3e87e69f7da7524d34a056de17480b27744a4b390170c0da4db48877aab`,
Node
`fed4254a121484e6426ff69e434cfbc1b54ae92a87d19901767502dde7446799`,
tests
`9a71e0b900e09326a21cf6f3f3eddc4e7ccc279483f3682cabff66b9fbef94d3`.
Estos hashes corroboran el código local probado, **no** autenticidad de
originales ni suficiencia científica.

## PR22 · corrección diferencial: tipos JSON del oráculo S3 al cruzar IPC/HTTP

**Un fallo nuevo y alcanzable, no modificación de la matemática S3.** La
frontera Python del consumidor comparaba con igualdad ordinaria de diccionarios
el oráculo S3 producido por Node y el oráculo propio. En Python
`False == 0` y `0 == False`, aunque en JSON son tipos diferentes. Por ello,
una respuesta auténtica del proceso Node cuya salida se alteraba **después**
de su ejecución podía convertir un contador de censura ficticia `0` en el
booleano `false`, o la declaración de derechos `false` en el número `0`, y
seguir atravesando el comparador; la ruta HTTP devolvía **200** con un
oráculo formalmente inválido. No se demostró una promoción de permisos a
`true` ni un ataque remoto sin controlar previamente el IPC.

**Falsador PREPATCH real:** se añadió el test parametrizado
`test_s3_node_ipc_boolean_integer_type_confusion_must_fail_closed_prepatch`
en el archivo existente `tests/test_synthetic_scientific_integration_lab.py`.
Primero ejecuta el proceso Node genuino con los fixtures exclusivamente
sintéticos; modifica **solo uno** de los dos tipos en su salida JSON;
finalmente consulta por HTTP local la ruta original con `cut=late`.
El oráculo exige `503`, `Cache-Control: no-store` y error
`SYNTHETIC_BRIDGE_UNAVAILABLE`. Se congelaron los SHA anteriores al parche:
Python `26aed3e87e69f7da7524d34a056de17480b27744a4b390170c0da4db48877aab`
y test añadido
`c2000dca548008614e78f90094a56d098805720cf8f055a83d82f65b787d0c86`.
La ejecución **PREPATCH 2/2 FAIL** observó en ambos casos **HTTP 200**, no
503; 65 pruebas existentes se deseleccionaron.

**Corrección mínima:** en el `expected_keys`/contrato existente de
`_node_warehouse` se conserva el esquema y se sustituye únicamente la
comparación del suboráculo S3 por comparación de **JSON canónico**
(`json.dumps` con `sort_keys=True` y separadores estables). A diferencia
de la igualdad de diccionarios Python, los tokens JSON `false` y `0`
permanecen distintos, al igual que `true` y `1`; el orden de propiedades
no influye. Se mantiene la doble comprobación completa antes y después
del IPC, sin cambiar fracciones, referencias, cortes temporales o Node.

**POSTPATCH:** exclusivamente esos dos nuevos oráculos **2/2 PASS**
(65 deseleccionados), con proceso Node genuino mutado y rechazo HTTP 503;
smoke positivo adicional sobre Node/Python auténticos `early=null`,
`late.change_bounds=[-11/52,47/119]`, tipo entero real en cero testigos,
`rights_independently_verified=false`; `node --check`, `py_compile`
y `git diff --check` PASS. No se reejecutaron 35 pruebas S3 anteriores,
11 bitemporales, 109 PP04 ni 41 Node históricos. **R5 STOP, 0/6 gates,
0 AB científicos, cero datos reales/PII y sin CI, main ni despliegue.**

**Recibos POSTPATCH SHA-256:** Python
`3374ca2cc1fc088546e69f68e2cd9499923453f9fdde48fb6e3a53188b214182`,
prueba focal
`c2000dca548008614e78f90094a56d098805720cf8f055a83d82f65b787d0c86`.
Node no se modificó y conserva
`fed4254a121484e6426ff69e434cfbc1b54ae92a87d19901767502dde7446799`.

## PR22 · cadena transversal tipada: actor, organización, comunicación, decisión y proceso

**Capacidad NUEVA de ingeniería, `NONCYCLE`, no reparación de un defecto
empírico ni de la anterior cadena bitemporal.** La función
`_bitemporal_actor_event` ya validaba actor, institución, rol y revisión
documental de un evento. `procedural_stage_accounting` modelaba episodios
de manera separada. Hasta esta ampliación ninguna composición E2E exigía
un **único origen con recibos SHA por edición**, referencias tipadas y los
mismos relojes de conocimiento y validez para las **cinco familias**.

La capacidad se incorporó exclusivamente en `scientific_integration_lab.py`,
`scientific_integration_warehouse.mjs` y la ruta HTTP existente; no se creó
un módulo, esquema de ingestión real, nueva ruta, nueva PR ni ciclo AB.
`_typed_institutional_chain_fixture` define exactamente **dos cuerpos
documentales inventados** de un mismo emisor `SYN:CHAIN`. Cada uno tiene su
SHA-256 real de los bytes del fixture, `source_id`, `captured_at` y
`first_public_at` **ficticio** propio. Python registra los recibos exactos
en `TemporalLedger` y Node recalcula **independientemente** ambos digests
antes de construir entidades y eventos con el almacén existente.

Las claves tipadas incluyen las familias `ACTOR`, `ORGANIZATION`,
`COMMUNICATION`, `DECISION` y `PROCESS`; una referencia a organización o
persona nunca sustituye otra categoría mediante similitud de nombres.
La comunicación C1 tiene dos **revisiones documentales** (la segunda con
`amendment_of` explícito), pero **una sola comunicación lógica**. La
decisión D1, fechada ficticiamente el 14/09/2026 y conocida únicamente en
la edición capturada el 31/10/2026, es un evento **diferente**: ni el
acto de emitir C1 ni su revisión cuentan como aprobación administrativa.
El proceso P1 está modelado como **un `EntryEpisode`**, con testigo de
pendencia conocido en el corte temprano y acto final `APPROVED` conocido
en el tardío. No se convierte el episodio en un `W.event` adicional, ni
se crean dos procesos por las dos versiones de fuente.

| Vista sintética | `early` 15/10/2026 | `late` 01/11/2026 |
| --- | ---: | ---: |
| Recibos de edición visibles según captura/publicación ficticia | 1 | 2 |
| Revisiones conocidas de comunicación C1 | 1 | 2 |
| Comunicaciones lógicas | 1 | 1 |
| Decisiones visibles con `valid_at=11/09/2026` | 0 | 0 |
| Decisiones visibles con `valid_at=15/09/2026` | 0 | 1 |
| Estado P1 para `valid_at=15/09/2026` | `PENDING_AS_OF_EVIDENCE` | `APPROVED_AS_OF_EVIDENCE` |
| Negativas y censuras observadas en la cadena | 0 y 0 | 0 y 0 |

El corte `early` puede desconocer una decisión que jurídicamente se
representa como ocurrida en septiembre, porque su publicación/captura
**ficticia** es posterior. A su vez, consultar `valid_at=11/09` aun con
`as_of=late` **no** convierte una decisión del 14/09 en decisión del 11/09.
Esto es una comprobación de ingeniería de conocimiento frente a validez,
no una verificación histórica de una actuación española.

**Unión de contratos:** Python aplica `FileReceipt` + `TemporalRecord`,
`TemporalLedger.snapshot(as_of,valid_at)`, `EntryEpisode`, `PendingWitness`,
`StageAct`, `audit_lab` y `assess_distribution_rights` **por distribución
y propósito**. Para ambas ediciones, la finalidad `LOCAL_ACADEMIC_READ`
declarada por el fixture **no** cubre `PUBLIC_AGGREGATE_DISPLAY`: el gate
no admite reutilización ni evidencia empírica. Node utiliza
`W.source/entity/event/asOf/auditBundle`, valida el wire de claves y
enlaces tipados completos, y reconstruye la misma proyección agregada.
Python compara con JSON canónico la salida íntegra de Node; una deriva
observable causa **HTTP 503**, no resultados inventados. En HTTP se ocultan
bytes, SHA, IDs de actor/evento y episodio: solo se exponen agregados
con `Cache-Control: no-store`.

**QA nueva, sin PREPATCH ficticio para la capacidad:** tests focales de
paridad entre motores en ambos cortes, dos fechas de validez, clasificación
de eventos y revisión, vinculación exacta de SHA a cada familia y episodio,
rechazo de `source_id`/SHA/captura futura/mezcla COMMUNICATION↔DECISION,
alteración de claves de proceso, suplantación de derechos, denominador y
`first_public_at_real`; y un test HTTP con Node real adulterado únicamente
en `logical_decisions`, que debe devolver 503. Ninguna prueba accede a
originales de PAN/IAEN, personas reales o fuentes privadas.

La política de evidencia sigue conservando `first_public_at_real=null`,
`independent_denominator=null`, `official_identity_crosswalk_verified=false`,
`real_outcomes_attested=false`, `rights_by_asset_purpose_admitted=false`,
`real_decision_outcome_attested=false`, `real_censoring_attested=false`,
`R5=STOP_R5`, **0/6 gates y 0 ciclos científicos**. PP04 y su población
`NO INCLUIDAS` no reciben nuevos emparejamientos ni denominadores.

### Defecto material independiente priorizado: tipos procedimentales al unir cortes

Una auditoría externa identificó un fallo **alcanzable** en el consumidor
existente `_reconcile_followup`: `reconstructed != procedural` permitía
agregados JSON semánticamente inválidos por igualdad de Python entre
`1`/`True` y `2`/`2.0`. Dos alteraciones sintéticas, una en
`terminal_by_cause.INADMITTED`, otra en
`observed_pending_at_last_witness`, sobrevivían y se exponían en
`GET /api/scientific-integration-lab?cut=late` con **HTTP 200**, incluso
cuando la llamada ejecutaba Node genuino. No hay evidencia de explotación
externa, de acceso a expedientes reales ni de cambio de estimando.

**PREPATCH congelado:** test único parametrizado en el archivo de tests
existente, con dos oráculos del helper y dos de HTTP, **4/4 FAIL reales**
(67 tests antiguos deseleccionados). SHA producción PREPATCH
`dddb22c94fbccc854ccaa868d933dda56b578786d416528657dc241260cc8608`
y test congelado
`9d9194890b3605eebad40b8028e61d2d45ca904b60d504e1b552b9f3756d2367`.
El código productivo previo ya contenía la nueva cadena `NONCYCLE` aún
sin publicar, pero la función vulnerable seguía exactamente sin parche.

**Reparación local:** comparar el agregado procedimental reconstruido
completo y la salida recibida con **JSON canónico tipado**, de forma que
`true` no sea un entero y `2.0` no sustituya al contador natural `2`.
Solo cambia el contrato ya existente `_reconcile_followup`, no la clase
de decisiones, el mecanismo de censura ni los registros de fuentes.
**POSTPATCH:** los cuatro falsadores rojos pasaron **4/4 PASS**.

**QA final focal conjunta:** `PYTHONPATH=src python -m pytest -q
tests/test_synthetic_scientific_integration_lab.py -k
'typed_institutional_chain or followup_structurally_equal_but_json_type_invalid_must_fail_prepatch or followup_type_drift_must_fail_closed_actual_http_prepatch'`
→ **18 PASS, 67 deseleccionados**. `node --check`, `python -m
py_compile` y `git diff --check`: PASS. No se reejecutaron las 35 S3,
11 bitemporales, 109 PP04 ni 41 Node históricas. Sin CI, main o despliegue.

**Recibos SHA-256 de producción y test después de QA:** Python
`2ac2a5546e58e45d2733747a44b0d9d2f639b66f883029f519e7dbdb62bc905c`,
Node
`c5db9a77c831c9e21f6380916bc7acb209888933d8cdb2e8b1b4b1a762ee6732`,
tests
`ef0720582da8910e23b3a9897fdf2308533e2de4e776d6d78d5502b58a333be7`.
Son huellas de bytes de software de laboratorio, **no** recibos de
originales ni acreditación de acceso científico a datos reales.

## PR22 · experimento B0 calendario frente a B3 selección/publicación (NONCYCLE)

**Capacidad nueva, no defecto PREPATCH ni reutilización nominal del rival
anterior.** El experimento `CAPTURE_EXPANSION` frente a `STABLE_CAPTURE`
comparaba totales por canal y períodos. Esta nueva instrumentación utiliza
el **mismo wire sintético de las cinco familias** (`ACTOR`, `ORGANIZATION`,
`COMMUNICATION`, `DECISION`, `PROCESS`) y ambas ediciones de la cadena
tipada, con su `source_id` y SHA-256 **exacto por fuente/revisión**. Para
cada `as_of` temprano y tardío se calcula una proyección de hechos
identificados por **familia, clave tipada, emisor, SHA, revisión, fecha de
validez y semántica**. La comparación completa se realiza internamente;
HTTP muestra solo recuentos y estados agregados, nunca identificadores,
bytes ni SHA privados del fixture.

Los **dos procesos generadores de datos (DGP)** estipulan el MISMO N=4
hipotético de primeros episodios recibidos, NO un N empírico ni un censo
administrativo autenticado. Los tres episodios adicionales E2, E3 y E4
son supuestos latentes sin recibo de publicación: no aparecen como hechos
observados. La proyección pública conserva el episodio publicado P1,
su comunicación C1 con dos revisiones, la decisión D1 distinta y las
identidades source-local de actor y organización. En el corte temprano
solo se conoce la primera edición; en el tardío se conocen ambas.

| Elemento exclusivamente hipotético | B0, calendario | B3, selección/publicación |
| --- | --- | --- |
| N de primeros episodios recibidos | 4 | 4 |
| Episodios sin publicación específica | 3 | 3 |
| Fracción hipotética de procesos publicados | `1/4` | `1/4` |
| Causa postulada de salida de la segunda edición | Calendario de publicación del 30/10 | Selección editorial el 20/10 para publicación el 30/10 |
| E2 | Pendiente; no negativo | Pendiente; no negativo |
| E3 al corte tardío del 01/11 | Sin acto terminal conocido; audiencia futura ficticia el 05/11 | Rechazo ficticio del 10/10, **no publicado** |
| E4 | Testigo de censura a derecha estrictamente hipotético | El mismo testigo de censura, nunca rechazo |

Esta comparación evita tomar la distinta cobertura o el distinto
denominador como respuesta: **hasta un supuesto registro independiente
que confirmase exactamente N=4 no discriminaría entre B0 y B3**.
El testigo diferencial necesario es **documentación independiente,
tipada y temporalmente admisible del estado administrativo de E3**, o
un **registro verificable de decisiones de selección y calendario de
publicación**. Un certificado de rechazo de E3 fechado y publicado con
conocimiento admisible al corte tardío falsaría la variante B0; un
testigo independiente que acreditase ausencia de acto terminal hasta el
corte podría falsar la variante B3. El mero `first_public_at` de las dos
ediciones compartidas **tampoco discrimina** los mecanismos: podrían
generar exactamente las mismas fechas de publicación. Ninguno de esos
testigos diferenciales existe en el laboratorio como evidencia real;
se registran como `available=false`.

| Proyección observada del **mismo fixture** | Early, `valid_at=15/09` | Late, `valid_at=15/09` |
| --- | ---: | ---: |
| Actor / organización | 1 / 1 | 1 / 1 |
| Revisiones documentales de comunicación C1 | 1 | 2 |
| Comunicaciones lógicas | 1 | 1 |
| Decisiones D1 visibles | 0 | 1 |
| Hechos documentales de proceso P1 (entrada, pendencia, aprobación) | 2 | 3 |
| Estado publicado del proceso P1 | Pendiente | Aprobado |

Al consultar `valid_at=11/09` aun con el corte `as_of=late`, no se
adelanta la decisión del 14/09. Al reproducir el corte `early` dentro
de la consulta `late`, la firma completa de las observaciones anteriores
permanece idéntica. Se contrasta la igualdad interna de **cada tupla
tipada, fuente/recibo, revisión y fecha**, no solamente la igualdad de
recuentos marginales. La revisión C1 v2 no se cuenta como una segunda
comunicación; la comunicación no es una decisión; P1 no son dos
episodios por sus documentos; los tres casos latentes no se suman a
`terminal_by_cause`, pendientes observados ni censuras reales.

**Sensibilidad S3:** el experimento reutiliza **sin recalibración** el
oráculo S3 ya calculado independientemente en Python `Fraction` y Node
`BigInt`: `r=P(publicado|Y=1)/P(publicado|Y=0) ∈ [1/2,2/1]` y
`Δ∈[-11/52,47/119]`, siendo `r` una **razón de probabilidades de
selección condicionales y NO una odds ratio**. Los binarios S3 6/4 y
7/3 NO proceden de esta cadena, no cuantifican sus casos y no autorizan
una interpretación causal. El bloque S3 está `null` en `early`, pues
su información sintética se incorpora únicamente al corte tardío.

**Contratos y defensa:** Python crea un wire `pfl.synthetic_b0_b3_full_observation_wire.v1`
con dos mecanismos congelados y un oráculo
`pfl.synthetic_b0_b3_observational_equivalence_oracle.v1`; Node valida
la misma estructura cerrada, los SHA/source_id de la cadena, sus claves
tipadas, los cuatro casos estipulados y la no disponibilidad de los
testigos, y vuelve a calcular las proyecciones exactas con el almacén
ya existente. Python compara canónicamente el resultado completo del
proceso Node para impedir deslizamientos de familia, fechas y tipos JSON.
La ruta HTTP existente devuelve **503** y `Cache-Control: no-store` si
Node se desvía incluso cuando el agregado total de eventos permanece
constante. Las fronteras de IPC se mantienen acotadas: entrada máxima
12 288 caracteres y salida máxima 9 000, exclusivamente para los
fixtures sintéticos enumerados, sin aceptar archivos, URL, identidades
o fuentes suministrados por el cliente.

**QA focal nueva:** tests seleccionados con `-k 'b0_b3'` verifican la
igualdad no vacía de las cinco familias en early y late, fechas de
validez distintas, recibos fuente y hashes, revisión vs evento,
N=4 en ambos mecanismos, estado diferencial E3 y testigos ausentes,
E2 pendiente, E4 censura no equiparada a rechazo, razones S3 exactas,
contratos cerrados frente a spoof de `source_id`/SHA, semántica, tiempo
ficticio, denominador, derechos, publicación y causa, y prueba HTTP
real de discrepancia Node que intercambia una comunicación por una
decisión **manteniendo constante la suma total**. **22 PASS,
85 deseleccionados**; `node --check`, `py_compile` y `git diff --check`
PASS. Es una capacidad nueva `NONCYCLE`: **NO hay PREPATCH rojo
ficticio**; tampoco se reejecutaron las 18 pruebas focales de la fase
anterior ni las suites históricas S3, bitemporal, PP04 o Node.

**Puertas inalteradas:** `real_all_received_denominator=null`,
`real_first_public_at=null`, testigos externos `available=false`,
`rights_for_public_aggregate_admitted=false`,
`official_crosswalk_verified=false`, `empirical_causal_effect_identified=false`,
`scientific_cycles=0`, `R5=STOP_R5`, **0 AB**, sin acceso a originales,
PII, CI, `main`, merge ni despliegue. La población de PP04
`NO INCLUIDAS` sigue excluida; E3 hipotéticamente rechazado bajo B3
**no** se promueve a negativo administrativo observado.

**Recibos SHA-256 de la capacidad B0/B3 tras QA focal:**
`scientific_integration_lab.py` =
`fbfc896fe0350da5c8a0141596d79b216ef02a719a0221bdcf42f188f006d686`,
`scientific_integration_warehouse.mjs` =
`3cfcec205e00acbf6921924c8db70364804ffd1b789d717510f75482c9e4998b`,
`test_synthetic_scientific_integration_lab.py` =
`e7b16dc188101b88853277cb5e8b5be02adebaebeb2430329f3a485b64dec8c3`.
SHA del código no equivale a autenticidad de documentos administrativos.

## PR22 · matriz de testigos diferenciales B0/B3 — capacidad nueva NONCYCLE

Esta capacidad extiende el experimento anterior B0 calendario frente a
B3 selección/publicación **sin crear una fuente empírica**. Ambos mecanismos
siguen compartiendo exactamente **cuatro episodios recibidos hipotéticos**,
dos ediciones publicadas, sus SHA-256 por fuente y revisión, claves tipadas
de actor, organización, comunicación, decisión y proceso, y la misma
proyección pública a `early` y `late`. La nueva matriz responde una
pregunta diferente: **qué clase de testigo adicional sería admisible al
corte de conocimiento y cuál de los dos mecanismos, si alguno, quedaría
refutado**. Las once filas son **escenarios alternativos**; no son once
observaciones reales simultáneas ni se combinan en un expediente.

### Contrato congelado y relojes

El esquema de entrada existente en el IPC incorpora
`pfl.synthetic_b0_b3_witness_matrix_wire.v1`, que incluye referencias
source-local y los SHA exactos de las dos ediciones de la cadena más
**once recibos documentales totalmente inventados**. Por testigo se
conserva, exclusivamente dentro de Python/Node: ID del escenario, tipo
de declaración, emisor ficticio, bytes y SHA-256, clave tipada, fecha de
validez, `first_public_at` ficticio, `captured_at`, suficiencia del enlace
y exhaustividad pretendida. El testigo de dos ediciones vincula sus
dos SHA a un único activo/distribución ficticio, sin confundir edición
con entidad o evento adicional.

El oráculo de salida
`pfl.synthetic_b0_b3_witness_matrix_oracle.v1` **no incluye bytes,
SHA ni identidades source-local**: ofrece para cada caso/corte
`witness_admissibility`, `compatible_mechanisms`, `falsified`,
`identified_from_observation`, `identification_scope`,
`causal_identified=false` y `real_evidence_admitted=false`. La expresión
`identified_from_observation=true` solo indica **identificación condicional
al testigo inventado dentro del laboratorio**; nunca acredita identificación
empírica, una selección realmente observada ni causalidad.

El corte **early** pregunta por conocimiento
`as_of=2026-10-15T12:00:00Z` y estado válido el **15/10**;
**late** pregunta por conocimiento `as_of=2026-11-01T12:00:00Z`
y estado válido el **31/10**. No basta que una declaración afirme
referirse a una fecha pasada: su captura y su primera publicación
**ficticia** deben ser anteriores o iguales al corte. Tampoco se admite
una declaración relativa a un día de validez posterior a la consulta.

### Resultados de la matriz congelada

Las abreviaturas **B0+B3** indican compatibilidad con ambas hipótesis;
**B0** o **B3** indican identificación exclusivamente condicional al
testigo inventado. `NO CONOCIDO` no es una negación, y `INADMISIBLE`
no es un resultado administrativo.

| Escenario independiente | Early | Late | Justificación diferencial |
| --- | --- | --- | --- |
| Ningún testigo | B0+B3 | B0+B3 | La observación publicada es igual |
| Registro independiente simulado `ALL_RECEIVED`, N=4 | B0+B3 | B0+B3 | Ambos estipulan N=4; el denominador igual no discrimina |
| Documento incompleto o sin enlace tipado | INADMISIBLE, B0+B3 | INADMISIBLE, B0+B3 | No se adjudica identidad ni episodio sin crosswalk específico |
| E3 rechazado el **10/10**, documento independiente, capturado/publicado antes de late | NO CONOCIDO, B0+B3 | **B3**, B0 refutado | Contradice la ausencia de terminal en B0 |
| E3 sigue pendiente al **31/10**, registro exhaustivo hipotético | NO CONOCIDO, B0+B3 | **B0**, B3 refutado | Contradice el rechazo de E3 el 10/10 que estipula B3 |
| E2 pendiente | B0+B3 | B0+B3 | Pendencia conocida no es rechazo ni censura |
| E4 con testigo ficticio de censura a derecha | NO CONOCIDO, B0+B3 | B0+B3 | Censura de seguimiento no demuestra resultado terminal |
| Dos ediciones del mismo activo con recibos SHA auténticos del **fixture** | NO CONOCIDO, B0+B3 | B0+B3 | Dos versiones idénticas a las publicadas no informan del mecanismo de selección |
| Log de regla de selección independientemente comprobado **en el fixture** y concordante con B3 | NO CONOCIDO, B0+B3 | **B3**, B0 refutado | Exige comprobar regla, versión, decisión temporal y aplicación al mismo activo |
| Testigo publicado y capturado **después de ambos `as_of`** | NO CONOCIDO, B0+B3 | NO CONOCIDO, B0+B3 | No hay *lookahead* admisible |
| `first_public_at` retrospectivo 19/09, pero captura local 31/10 | NO CONOCIDO, B0+B3 | B0+B3 | Una fecha pública antigua no retrotrae el conocimiento local ni discrimina por sí misma |

El testigo E3 de pendencia exhaustiva lleva fecha válida **31/10**,
publicación ficticia **31/10 a las 13:00 UTC** y captura **01/11 a las
08:00 UTC**, ambas anteriores al corte tardío del 01/11 a las 12:00;
no se inventa una publicación anterior al estado que se pretende
documentar. La primera publicación **real** continúa siendo `null`.

### Criterios de aceptación, rechazos y consecuencias epistemológicas

La capacidad solo considera hipotéticamente admisibles los documentos
con **estructura exacta**, familia y enlace tipados del caso, `source_id`
y SHA de los bytes sintéticos esperados, fechas de publicación/captura
válidas para el corte y testigo suficientemente exhaustivo cuando la
afirmación lo requiere. Un enlace incompleto se conserva como
`INADMISSIBLE_INCOMPLETE_OR_UNLINKED` sin refutar modelo alguno. Las
mutaciones de SHA, fuente, familia, enlace, exhaustividad, fecha, orden,
activo/distribución, derechos o declaraciones de denominador y crosswalk
**reales** se rechazan cerradamente antes de emitir un oráculo. Los
testigos válidos del laboratorio llevan el estado inequívoco
`ADMISSIBLE_HYPOTHETICAL_ONLY`.

Python verifica `FileReceipt` de cada testigo y ejecuta
`assess_distribution_rights` **por activo y propósito**: el supuesto
`LOCAL_ACADEMIC_READ` jamás certifica
`PUBLIC_AGGREGATE_DISPLAY` ni la reutilización de originales.
Node reconstruye por separado la matriz, los contenidos sintéticos y
sus SHA con `crypto.createHash`, y valida el esquema completo. El
consumidor Python coteja el resultado íntegro por JSON canónico tipado;
el HTTP ya existente solo devuelve agregados sin PII y responde
**503/no-store** ante divergencia real de IPC, incluso si la discrepancia
se introduce después de ejecutar el Node genuino.

La matriz conserva explícitamente la distinción **resultado negativo
administrativo observado** frente a **rechazo E3 oculto e hipotético bajo
B3**. `E2=PENDING` no equivale a negativo, `E4=RIGHT_CENSOR` no equivale
a rechazo y el universo `NO INCLUIDAS` de PP04 nunca se usa como grupo
de negativos. No se inventa un denominador de entradas, un documento
oficial ni una prueba histórica disponible para identificar la selección.

Se conserva la referencia independiente S3, **no calibrada sobre esta
cadena**: `r = P(publicado|Y=1) / P(publicado|Y=0)` en `[1/2,2/1]`,
región no causal del cambio `[-11/52,47/119]`, **no una odds ratio**.
Está bloqueada en `early` por conocimiento temporal y disponible como
oráculo de sensibilidad ficticio en `late`. En todos los casos
`real_independent_all_received=null`, `real_first_public_at=null`,
`rights_for_public_display_admitted=false`,
`real_crosswalk_verified=false`, `causal_identified=false`,
**R5 STOP, 0 AB científicos, 0/6 puertas empíricas**.

**Pruebas focales nuevas** (`-k witness_matrix`): paridad Python/Node
con el **mismo wire**, matriz caso por caso early/late, contraste de
revisión y recibos exactos, anti-lookahead, admisibilidad/invalidación,
alteraciones SHA, familia, derechos, crosswalk, fechas y exhaustividad,
S3 racional exacta y servidor HTTP con Node auténtico adulterado para
contradecir la refutación de E3. **20 PASS, 107 deseleccionados**.
`node --check`, `py_compile`, `git diff --check`: PASS. No se repiten
las 22/35/18 pruebas anteriores, PP04 ni las 41 Node históricas. Es una
capacidad **NONCYCLE**, sin fabricar un fallo PREPATCH inexistente.

**SHA-256 del código y los tests después de QA focal:** Python
`f53fc104863a15c9b23bf916b585affb59f5a19f173bec7a48202d07e66bb2e7`,
Node
`d15a686cc8c6d78d8d217a74d128ac524341bd397b5522e7c7bef1f4ff6b770e`,
tests
`8f35e0b4cbcb72a45c1fce01444c2c96c8d0237e181fa263e348e55304ab0f45`.
Estas huellas no autentican derechos ni fuentes originales.

## PR22 · S7: conjuntos robustos de testigos diferenciales (NONCYCLE)

**Capacidad nueva, no incidencia PREPATCH.** El oráculo S6 de once
testigos individuales permanece inalterado y sirve como fuente de
admisibilidad sintética. S7 añade veinte **conjuntos alternativos de
testigos** contra los mismos modelos B0 calendario y B3
selección/publicación, que estipulan N=4, dos ediciones SHA verificadas
y exactamente la misma proyección publicada de actor, organización,
comunicación, decisión y proceso. Los conjuntos son escenarios de
contraste: **no son veinte documentos históricos ni pruebas acumuladas**.

### Contrato, firmas y salidas

El nuevo contrato cerrado `pfl.synthetic_b0_b3_witness_sets_wire.v1`
viaja en el IPC con el campo `s7_witness_sets`. Contiene el esquema S6,
los recibos SHA exactos de las dos ediciones de la cadena, ocho testigos
adicionales inventados `s7_extra_witnesses`, y veinte entradas
`witness_sets` con `{case,witness_ids}`. Cada testigo nuevo conserva
tipo, emisor, distribución, `source_id`, bytes y digest SHA-256,
referencia tipada, fase administrativa, resultado alegado, fechas de
validez, publicación/captura, completitud, independencia, exhaustividad,
crosswalk y propósito. Su campo `signature_scheme` declara
`SYNTHETIC_HMAC_SHA256_NOT_OFFICIAL`. Python y Node recalculan
**independientemente** ese HMAC sobre los bytes inventados mediante una
clave pública de prueba incluida en el repositorio. **No es una firma
administrativa, un secreto de producción ni una autenticación real de
emisor, independencia o derechos**.

El nuevo oráculo `pfl.synthetic_b0_b3_witness_sets_oracle.v1` se
expone solo como agregados en
`warehouse.b0_b3_witness_sets.sets_by_knowledge_cut.{early,late}.sets`.
Cada conjunto proporciona `case`, `status`, `compatible_mechanisms`,
`falsified`, `identified_from_observation`, `reason`,
`witness_admissibility` por miembro y, si procede, la prueba
`contradiction` con familia, fase, igualdad de episodio y fecha,
y número de documentos retenidos. Se omiten de HTTP los bytes, SHA,
HMAC, distribuciones e identificadores source-local de los testigos.

Los **seis estados** son `INCONCLUSIVE`, `B0_ONLY`, `B3_ONLY`,
`NEITHER`, `CONFLICT` e `INADMISSIBLE`. `NEITHER` significa que un
**único testigo sintético admisible**, E3 APPROVED el 10/10, contradice
ambos DGP estipulados. Es un resultado científico-condicional del
fixture, **no** un error HTTP, ni una afirmación de que E3 haya sido
aprobado realmente. `CONFLICT` significa que **dos testigos
individualmente admisibles son contradictorios**: la máquina conserva
los dos y suspende la adjudicación; no descarta uno, no atribuye
intenciones y no afirma falsación simultánea de B0 y B3. En cambio,
`INADMISSIBLE` indica evidencia documental bien formada dentro del
esquema cerrado pero no apta para sostener una conclusión. Una
alteración del *wire* registrado, la firma, la identidad tipada,
los SHA, el esquema o el IPC es **corrupción contractual y causa 503**:
no puede confundirse con `INADMISSIBLE`.

### Matriz de veinte conjuntos

Los resultados de la columna `late` se obtienen con el mismo corte
`as_of=2026-11-01T12:00:00Z`, válido a `31/10`; `early` corresponde a
`as_of=2026-10-15T12:00:00Z`, válido a `15/10`.

| ID S7 | `late.status` | Efecto condicional |
| --- | --- | --- |
| `S7_NONE` | `INCONCLUSIVE` | Ningún testigo; B0 y B3 retenidos |
| `S7_N4_SAME` | `INCONCLUSIVE` | N=4 en ambos; no discrimina |
| `S7_TWO_VINTAGES` | `INCONCLUSIVE` | Dos ediciones del mismo activo con recibos SHA; no discrimina |
| `S7_PENDING_CENSOR` | `INCONCLUSIVE` | E2 pendiente y E4 censurado, sin crear negativas |
| `S7_B0_ONLY` | `B0_ONLY` | E3 STILL_PENDING exhaustivo 31/10 refuta B3 |
| `S7_B3_ONLY` | `B3_ONLY` | E3 REJECTED 10/10 refuta B0 |
| `S7_SELECTION_LOG_B3` | `B3_ONLY` | Regla editorial sintética verificada y contrastada |
| `S7_NEITHER_APPROVED` | `NEITHER` | E3 APPROVED 10/10, HMAC sintético correcto, refuta ambos |
| `S7_CONFLICT_SAME_TERMINAL_DAY` | `CONFLICT` | E3 APPROVED y E3 REJECTED, mismo episodio, fase TERMINAL y día 10/10 |
| `S7_CONFLICT_PENDING_VS_REJECTED` | `CONFLICT` | E3 REJECTED 10/10 contradice pendencia exhaustiva 31/10 |
| `S7_INADMISSIBLE_SHA` | `INADMISSIBLE` | SHA alegado no coincide con bytes del fixture |
| `S7_INADMISSIBLE_ISSUER` | `INADMISSIBLE` | Emisor ficticio no aceptado en el laboratorio |
| `S7_INADMISSIBLE_CROSSWALK` | `INADMISSIBLE` | Clave tipada apunta a decisión en vez de episodio E3 |
| `S7_INADMISSIBLE_INDEPENDENCE` | `INADMISSIBLE` | Sin independencia acreditada siquiera en el fixture |
| `S7_INADMISSIBLE_EXHAUSTIVITY` | `INADMISSIBLE` | Pendencia E3 sin testigo exhaustivo |
| `S7_INADMISSIBLE_TIME` | `INADMISSIBLE` | Primera publicación alegada posterior a captura |
| `S7_INADMISSIBLE_PURPOSE` | `INADMISSIBLE` | Finalidad sintética del documento no cubre el replay |
| `S7_INADMISSIBLE_INCOMPLETE` | `INADMISSIBLE` | Documento S6 temprano incompleto y sin enlace |
| `S7_WITNESS_AFTER_CUT` | `INCONCLUSIVE` | Captura posterior incluso al corte tardío: no puede usarse |
| `S7_RETROSPECTIVE_FIRST_PUBLIC` | `INCONCLUSIVE` | Publicación ficticia antigua y captura posterior no retrotraen conocimiento |

En el corte **early**, los casos E3 de octubre y los nuevos documentos
adicionales aún no capturados son `INCONCLUSIVE` con
`NOT_KNOWN_AT_CUT`: no se anticipa siquiera su invalidez documental.
El documento S6 `INCOMPLETE_UNLINKED` sí está conocido en early y
permanece `INADMISSIBLE`. El testigo tardío de noviembre sigue
inutilizable también en late. Las etiquetas de escenario son un
**catálogo contrafactual fijado por el programador**, no noticias
retroactivas sobre hechos públicos.

El conflicto terminal comprueba internamente **la misma referencia
tipada E3, el mismo `stage=TERMINAL` y el mismo día válido** con
resultados excluyentes; la salida conserva ambos recibos conceptuales
sin elegir «ganador». El segundo conflicto compara rechazo terminal
10/10 con un inventario exhaustivo que todavía afirma pendencia a 31/10.
En ambos, la compatibilidad se conserva como *no adjudicada*, no como
prueba positiva de los modelos.

### Garantías epistémicas y QA

Todos los derechos reales para publicar agregados derivados de
originales permanecen bloqueados: la función Python
`assess_distribution_rights` se ejecuta por activo y finalidad, sin
confundir una cobertura de replay ficticio con consentimiento del
editor. No existe `real_denominator`, `real_first_public_at`,
autenticidad oficial de emisor, crosswalk real, acreditación de
independencia, admisión causal ni ciclos AB. E3 rechazado u aprobado
es un resultado oculto **solamente hipotético**; E2 pendiente no es
rechazo, E4 censura a derecha no es rechazo, y PP04 `NO INCLUIDAS`
continúa separado del universo de negativas administrativas.

La sensibilidad S3 sigue siendo **independiente de estos expedientes**.
Se reproduce con racionales exactos Python `Fraction` y Node `BigInt`:
`q_before=3/5`, `q_after=7/10`, razón
`r=P(publicado|Y=1)/P(publicado|Y=0) ∈ [1/2,2/1]`
(**no una odds ratio**) y límites no causales de cambio
`[-11/52,47/119]`. Early muestra `null` en el bloque S3.

Pruebas **exclusivamente nuevas**, seleccionadas con `-k s7_`:
paridad independiente de los dos motores sobre ambos cortes, las veinte
filas y seis estados, reproducción de las contradicciones con identidad
de episodio/fase/fecha, firma ficticia válida, evidencia formalmente
inadmisible, testigos futuros, privacidad, 503 ante alteración posterior
de Node y 503 ante inyección de identidad tipada o `source_id` inválidos
en el servidor real. **24 PASS, 127 deseleccionadas**; `node --check`,
`python -m py_compile` y `git diff --check` PASS. No se ejecutaron
las suites históricas S6, S5, S3, PP04 ni las 41 pruebas Node. Como
capacidad nueva **no se inventa una prueba roja PREPATCH**.

**Recibos S7 SHA-256 tras QA focal:** Python
`fe32ae28fb300c1f3cd0c7565f10b9c840f9e4a6428bb15bd468776a39b02bb4`,
Node
`890c5e8fbad150f74d23c2831d4504a472912b69723b1d097a891cb879c197a9`,
tests
`eabdefecb6261dbcac6638b82f9f56d5d48d8570ee82bd98fdbf211c22d4d22d`.
Estos SHA atestiguan únicamente los bytes del código local sometido a
las pruebas nuevas: no derechos de fuentes, publicidad real ni una
identificación científica de mecanismos políticos.

## PR22 · S8: interfaz científica y observatorio sintético ejecutable (NONCYCLE)

La aplicación local incorpora una pestaña **Laboratorio científico** que ejecuta
`GET /api/scientific-integration-lab?cut=early|late&scenario=baseline|rights_spoof|privacy_probe`.
El navegador comprueba el esquema cerrado y los bloqueos R5, y oculta resultados
ante 503 o discrepancia. Muestra la sensibilidad de selección S3 con intervalos
racionales no causales; los modelos B0 (calendario) y B3 (selección/publicación)
observacionalmente equivalentes; y los veinte conjuntos de testigos S7,
manteniendo sus seis estados y distinción entre `NEITHER`, `CONFLICT` e
`INADMISSIBLE`. El observatorio incluye un grafo **ficticio** tipado por actor,
organización, comunicación, decisión y proceso, navegable por `as_of` y
`valid_at` independiente, más una crónica de roles/eventos documentalmente
revisados. No une ambos dominios por identidad real ni contabiliza una revisión
como otra decisión/persona. Los testigos S7 internos permanecen redactados.

`explorer.catalog.distributions` aporta un catálogo filtrable por conocimiento
y por primera publicación **inventada** del descriptor (19/09 o 30/10, nunca
posterior a `as_of`). Cada edición declara familia, revisión, emisor ficticio,
captura y publicación simuladas, SHA-256 del **descriptor público sintético**,
calidad estrictamente interna, cobertura temporal real nula, motivo de
inadmisión y derechos de uso público no acreditados. Los SHA y los ID internos
de los originales de prueba de Python/Node nunca atraviesan HTTP: se verifica
su integridad *dentro* del proceso y se ofrecen recibos diferentes para los
descriptores públicos, conservando contratos anteriores de redacción.

`GET /api/scientific-lab-export?cut=&scenario=&published_until=` devuelve el
recibo `pfl.synthetic_scientific_export_receipt.v1`: `canonical_json` construido
mediante JSON UTF-8, claves ordenadas y separadores compactos; `bytes` y
`sha256` sobre **exactamente esos bytes**. WebCrypto vuelve a verificar la
huella antes de descargar el archivo. El límite de publicación filtra solo el
catálogo sintético del JSON exportado y nunca modifica los oráculos S3/S7
independientes del corte de conocimiento; el filtro futuro es error 400.

`GET /api/scientific-lab-admission?candidate=baseline|sha_spoof|issuer_spoof|rights_missing|first_public_missing|crosswalk_missing|denominator_missing|coverage_missing`
es una **prueba seca de ocho variantes cerradas** de un único documento inventado.
Valida SHA, emisor permitido, orden de publicación/captura, enlace tipado,
registro de entradas, cobertura y finalidad, y siempre devuelve
`status=REJECTED_R5`, `source_rows_imported=0` y causas de bloqueo externo.
Incluso el candidato íntegro internamente carece de autenticación real,
denominador independiente, derechos por recurso/finalidad, fecha de primera
publicación real, crosswalk oficial y testigo independiente. **No existe
ingesta de nuevas distribuciones reales ni POST de importación**. El dry-run
sirve para diseñar y probar futuros requisitos de admisión sin abrir R5.

Los nuevos tests focales HTTP + Python y el harness Node VM ejecutan la UI
efectiva (incluidos eventos de cambio de `as_of`/`valid_at`/filtro, verificación
WebCrypto y rechazo de un SHA alterado). La VM no equivale a una prueba manual
de navegador real, accesibilidad completa ni despliegue. Los módulos del
proyecto y las fuentes reales españolas siguen separados: **R5 STOP, cero
ciclos AB científicos, cero autorización de original, cero gates superados**.

Recibo técnico de la capacidad: `docs/S8_SYNTHETIC_SCIENTIFIC_UI_RECEIPT.json`.
Su resultado es ingeniería sintética revisable en la PR #22 DRAFT, sin CI ni
fusión a `main`; el estado de tests y los SHA efectivos se registran en el
recibo después de la verificación local.
