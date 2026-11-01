# PFL · S9 registro científico sintético persistente, bitemporal y cerrado

**Estado:** capacidad informática nueva, NONCYCLE, **R5 STOP**. PR #22 DRAFT.
**Fecha de ejecución:** 1 de noviembre de 2026.
**Alcance:** SQLite local con fixtures exclusivamente inventados, no fuentes
oficiales, no expedientes, no personas reales, no corpus, no derechos reales,
no nueva identificación causal ni denominador independiente.

## Finalidad y arquitectura

S8 disponía de vistas sintetizadas por ejecución sobre fixtures Python y un
oráculo independiente Node para S3, B0/B3 y S7. S9 añade algo diferente:
**conservar bytes de documentación ficticia, metadatos y relaciones tipadas
entre reinicios de dos procesos**, y producir una consulta temporal reproducible
desde ese estado SQLite. No sustituye el oráculo científico ni reimplementa
sus DGP; el campo `models.s3_s7_endpoint` remite explícitamente a
`/api/scientific-integration-lab`, cuya paridad Python→Node permanece
independiente y conserva sus propias restricciones de admisión. El registro
no es un almacén de decisiones reales ni un sistema de descubrimiento web.

Implementación: `src/politics_fantasy/scientific_registry.py` (único módulo
nuevo que justifica la capa transaccional) y ruta GET en
`src/politics_fantasy/server.py`. El fichero persistente SQLite se ubica junto
a la base del juego local y usa otro nombre:
`scientific_registry_synthetic.sqlite3`. No comparte cuentas, tokens ni
eventos de jugadores. Su creación es idempotente y siempre carga las mismas
siete distribuciones sintéticas cerradas. Un registro de admisión de fuentes
externas no existe; `POST /api/scientific-registry` no está permitido.

## Estructura SQLite v1→v2 (fase S9 publicada inicialmente)

La fase inicial S9 se publicó con `PRAGMA user_version=2`, `registry_meta` con identificador
de fixture y SHA del manifiesto, `schema_history` con versiones 1 y 2, tabla
`distribution` de documentos con BLOB UTF-8, tabla `typed_fact` de registros
por emisor y clave tipada y tabla `typed_edge` de enlaces declarados dentro
de un emisor. La versión 1 contiene el manifiesto y distribuciones; la 2
añade los hechos, relaciones y triggers de inmutabilidad. La migración
preserva bytes de los siete documentos de una versión 1 previa **solo si
todos sus campos y recibos coinciden** con el fixture conocido y su
manifiesto. Una versión desconocida o una base parcial no se repara ni se
resetea a escondidas.

`BEGIN IMMEDIATE` garantiza serialización y commit o rollback. Las
instrucciones DDL se ejecutan una a una dentro de esa transacción, sin
usar `sqlite3.executescript`, cuya confirmación implícita rompería esa
atomicidad. Los `UPDATE` y `DELETE` de `distribution`, `typed_fact` y
`typed_edge` están prohibidos por seis triggers. Se coteja además el
**SHA-256 de toda la definición SQLite (`sqlite_master`)** contra el
esquema canónico construido en memoria: tablas, `CHECK`, índices y cuerpo
efectivo de cada trigger, no solo su nombre o `user_version`. Se auditan
también los BLOB, hashes y revisiones **en todas las lecturas**, porque un
operador con acceso directo a SQLite podría manipular los triggers.
Inserciones de fuentes o hechos no incluidos en el manifiesto también
producen un error, nunca una admisión automática. En el servidor Python,
un bloqueo de inicialización evita carreras entre peticiones simultáneas
del mismo proceso; SQLite gestiona la transacción entre procesos.

Una distribución conserva `source_id` **interno**, `issuer` ficticio,
revisión inmutable, `amendment_of`, `source_bytes` exactos como BLOB,
`source_sha256` calculado sobre bytes, captura inventada,
`first_public_known_at` de ficción, `first_public_at_real=NULL`, finalidad
solicitada, derechos y autenticación real bloqueados, calidad declarada,
cobertura temporal no acreditada y procedencia únicamente sintética.
Cada revisión tiene su recibo: **no se reescribe la V1 cuando aparece V2**.
Las claves `issuer×kind×source_local_key` separan ACTOR, ORGANIZATION,
ROLE, EVENT, COMMUNICATION, DECISION y PROCESS. Una `amendment_of` válida
debe mantener esas tres dimensiones, avanzar número de versión y ser
conocida con posterioridad al hecho que revisa. Una arista debe referir
extremos tipados existentes del mismo emisor; no se construyen identidades
reales por coincidencia de nombres.

Se almacenan **siete** BLOB ficticios: las seis distribuciones S8
correspondientes a dos ediciones de la crónica, dos de la cadena institucional
y los dos ejemplos del parser PP04; una séptima fuente de etapas, también
anclada al fixture procedural sintético previo, se mantiene
**exclusivamente interna**, sin descriptor público. Hay **20 hechos tipados
y seis enlaces explícitos**. El catálogo HTTP publica únicamente seis
descriptores pseudónimos `S9:PUBLIC_01…06`, con SHA-256 de los **bytes del
descriptor público**, distintos del SHA interno que se comprueba sin
mostrar. En el corte temprano se ven dos y en el tardío seis. El orden,
las revisiones y las fechas no se deducen de una URL externa.

## Consulta bitemporal y clasificación de evidencia

Ruta GET única y enumerada:

```text
/api/scientific-registry?cut=early|late&valid_at=2026-09-11|2026-09-15|2026-10-10&family=all|PP04|CHAIN|CHRONICLE&published_until=as_of|2026-09-19T12:00:00Z|2026-10-30T12:00:00Z
```

Todos los parámetros son opcionales. Por defecto,
`cut=late&valid_at=2026-09-15&family=all&published_until=as_of`.
`cut` traduce a `as_of=2026-10-15T12:00:00Z` o
`2026-11-01T12:00:00Z` conforme al laboratorio S8. Una evidencia entra
en el snapshot únicamente cuando **su captura y primera publicación
ficticia conocida no superan el corte, su registro no es posterior a
`as_of`, su vigencia incluye `valid_at` y su publicación no supera el
filtro elegido**. Una fecha de publicación futura en un corte temprano
se rechaza como parámetro incorrecto, HTTP 400. No hay `source_id`, SQL,
URL ni fecha arbitraria que el consumidor pueda inyectar en esta ruta.

La respuesta `pfl.synthetic_scientific_registry.v1` tiene
`registry.distributions` (catálogo público de revisiones y calidad),
`snapshot.graph.chain` y `.chronicle` (nodos y aristas separadas,
con revisiones documentales colapsadas en un **único objeto lógico**),
`snapshot.episodes` (pendencia, aprobación, inadmisión explícitamente
*estipulada en el fixture*, seguimiento desconocido y ausencia de
testimonio independiente de censura), `snapshot.pp04` y `models`.

Las dos cronologías **no se unen por identidad nominal**. La primera
secuencia distingue actor, organización, comunicación, proceso y decisión;
la segunda conserva dos ediciones de un mismo evento y cambia el rol
documentado entre días de vigencia. La revisión documental de una
comunicación o evento no se suma como otra comunicación o evento.

La fase PP04 reproduce dos enunciados bajo «INCLUIDAS» —uno aprobado y
otro pendiente— y dos bajo «NO INCLUIDAS». Las «NO INCLUIDAS» son
normas fuera del plan, **no rechazos, inadmisiones ni unidades de la
cohorte planificada**. La inadmisión de un episodio procedural inventado
es otra categoría diferenciada, documentada solo como **estipulación
del laboratorio sintético**, no evidencia administrativa real. Un estado
pendiente o desconocido no se interpreta como negativo; no se supone
un derecho-censor real independiente ni un registro exhaustivo inicial.

## Recibo auditable sin exposición de fuentes internas

La respuesta incluye `snapshot_receipt_sha256` y
`snapshot_receipt={schema,canonicalization,content_scope,bytes,sha256,
canonical_json,external_authenticity_certified:false}`. El digest
SHA-256 recae exclusivamente sobre el **JSON canónico UTF-8 de la vista
pública** definida por `{schema,cut,as_of,valid_at,family,published_until,
distributions,snapshot}` con claves ordenadas y separadores compactos.
Se puede volver a calcular desde los bytes de `canonical_json`, sin
acceder a los BLOB privados. El recibo permite comparar reinicios y
filtros y detectar alteraciones del snapshot exportado, pero **no prueba
autoría de una entidad pública, autenticidad de originales ni derechos
de reutilización**. El contrato conserva `real_source_ingestion_allowed=false`,
`independent_denominator=null`, `scientific_ab_cycles=0`,
`release_gates_passed=0` y `R5=STOP_R5`.

## Pruebas de falsación y reproducibilidad

`tests/test_s9_scientific_registry.py` ejecuta escenarios nuevos de
ingeniería, no fallos de producción PREPATCH inventados: creación y
reapertura idempotente, **dos intérpretes Python independientes** leyendo
el mismo SQLite y conservando BLOB y digest, 16 llamadas concurrentes,
migración real de v1 poblada a v2 con mismos bytes, rollback íntegro
de migración conflictiva, seis triggers de inmutabilidad, intento de
promoción de derechos/issuer/denominador/fecha real bloqueado por
`CHECK`, manipulación de bytes/SHA/emisor/orden de publicación/revisión/
crosswalk/cobertura y relaciones, recuento de PP04 no-negativo,
cortes temporalmente independientes, esquema cerrado HTTP con 400
para entradas ilegales, y 503 sin resultados falsos al corromper SQLite.
El control integrado invoca además la ruta previa `/api/scientific-integration-lab`
con el Node warehouse auténtico y contrasta los **20 estados S7** y la
cota racional S3; **el registro no certifica esos oráculos ni los recalcula**.

Límites de validación: una base de datos local y sus triggers no equivalen
a un servicio remoto resistente a atacantes con acceso al disco del usuario;
el fixture es cerrado y no acepta distribuciones externas. No se ha
hecho adquisición web, consulta de originales, prueba con personas reales,
auditoría externa de licencias, confirmación oficial de identidad,
crosswalk documental interfuentes, denominador de todas las entradas,
medición de efectos, despliegue, CI ni merge de `main`.

El recibo técnico con SHA de los archivos, suite y HEAD se conserva en
`docs/S9_DURABLE_SYNTHETIC_REGISTRY_RECEIPT.json`, una vez concluido el QA.

## Continuación S9.1 · GAP #1: historial cerrado de preadmisión (SQLite v3)

**Naturaleza:** nueva capacidad funcional, NONCYCLE. El problema observado
era que las ocho consultas `synthetic_candidate_admission` de S8 devolvían
`REJECTED_R5` sin dejar una historia duradera de su *evaluación* en S9.
No existía un defecto de producción PREPATCH que justificara declarar
tests de regresión rojos. La incorporación S9.1 no abre fuentes, derechos
ni validadores externos.

El fixture S8 existente tiene una particularidad crucial: sus ocho
escenarios (`baseline`, `sha_spoof`, `issuer_spoof`, `rights_missing`,
`first_public_missing`, `crosswalk_missing`, `denominator_missing` y
`coverage_missing`) utilizan el **mismo `distribution_id` fuente-local y
los mismos bytes de base**. Son ocho variantes de un procedimiento de
comprobación, **no** ocho fuentes originales, actores, ediciones, decisiones
ni entradas administrativas distintas. Por eso se adopta una tabla nueva
`assessment_event`, aislada de `distribution`, `typed_fact` y `typed_edge`.

La migración explícita `PRAGMA user_version=3` conserva el histórico 1, 2
y añade la entrada 3 a `schema_history`. Se lleva a cabo en la misma
transacción `BEGIN IMMEDIATE` que valida/siembra la base. Se comprobaron
upgrades desde SQLite v1 y v2 sin alterar los siete BLOB documentales,
veinte hechos tipados ni seis aristas. Las ocho evaluaciones deterministas
se almacenan como **dieciséis eventos inmutables**, dos por ID público
`S9:ASSESS_01…08`: `REGISTERED` seguido de
`ASSESSED_REJECTED_R5`, sin ningún estado `APPROVED` ni posibilidad de
promover permisos reales. Los ocho ID de evaluación son pseudónimos
opacos, no source IDs; la tabla conserva los identificadores fuente-local,
emisor alegado, hashes y bytes del recibo **únicamente dentro de SQLite**.

El `captured_at` **inventado** de su fuente es
`2026-10-31T12:00:00Z`; los relojes ficticios de registro y evaluación
son `2026-10-31T12:15:00Z` y `2026-10-31T13:00:00Z`. El conocimiento
público del **recibo de evaluación ficticio** se estipula a
`2026-10-31T13:00:00Z`. Esto **no** certifica la primera publicación real
de la supuesta distribución de origen: en particular,
`first_public_missing` conserva la carencia de esa fecha en el candidato.
Un corte de conocimiento temprano ve cero evaluaciones y el tardío ve
ocho; el filtro de publicación hasta el 30 de octubre deja cero incluso
en corte tardío. Los eventos de auditoría no utilizan el día de vigencia
del hecho (`valid_at`), evitando interpretar una revisión administrativa
ficticia como acontecimiento anterior o como testigo de una decisión real.

Los recibos privados usan bytes JSON UTF-8 canónicos, SHA-256 exacto,
identificador de evaluación, variante, número y estado de transición,
timestamp, issuer y fuente-local ficticios, y el resultado calculado por
`synthetic_candidate_admission` sin alterar sus comprobaciones. La tabla
contiene dos triggers adicionales de inmutabilidad (ocho en total),
`CHECK` para prohibir autenticación real, admisión de derechos, denominador,
`first_public_at_real` y filas de fuente importadas; el auditor comprueba
el SHA de cada recibo, los dieciséis registros completos y **el DDL
íntegro** en cada consulta. Manipular bytes/SHA/estado/emisor/tiempos o
eliminar un trigger deja el endpoint científico en HTTP 503,
sin autocorrección silenciosa del histórico.

Sin modificar su ruta ni sus filtros, `GET /api/scientific-registry` publica
ahora `registry.schema_version=3`, `registry.migration_history=[1,2,3]` y
`snapshot.admission_assessments`, con el esquema
`pfl.synthetic_admission_assessments.v1`. El objeto contiene
`assessment_count`, `registered_count`, `assessed_rejected_r5_count`,
`history_event_count`, `assessments` y los límites de admisión.
Cada evaluación incluye un ID público opaco, variante, estado final
`ASSESSED_REJECTED_R5`, `revision=assessment_v1`, captura,
`registered_at`, `assessed_at`, las dos transiciones de historia,
**las siete comprobaciones internas y todos los motivos de bloqueo**
devueltos por S8. Contiene asimismo `public_receipt_sha256` calculado
sobre esos campos públicos; no expone ni la fuente-local privada ni el
emisor alegado. El recibo general `snapshot_receipt` ya existente
incorpora automáticamente la proyección y su digest SHA-256 cambia con
el corte/filtro: **no hace falta un segundo endpoint ni un segundo DGP**.
Cuando `family` no es `all`, las evaluaciones se omiten, porque no tienen
atribución fiable a PP04/CHAIN/CHRONICLE.

El conjunto de pruebas focales S9.1 verifica los ocho resultados S8
sin reimplementarlos, las dieciséis transiciones, integridad de cada
recibo, reinicios de dos procesos Python, migración **v1/v2→v3**,
no alteración de las anteriores 7/20/6 filas, no anticipación temporal,
no fuga del source ID, 8 alteraciones SQL intencionadas, triggers,
restricciones `CHECK` y HTTP 400/503. La batería Python S9+S10
finalizó **47/47 PASS** tras agregar 14 controles nuevos. La actualización
del frontend S9.1, su validación y la publicación Git de PR22
se gestionan conjuntamente con el agente principal por su titularidad
exclusiva de `app.js` y tests JS.

**Sin admisión empírica:** R5 STOP; cero fuentes reales importadas;
cero permisos de distribución acreditados; `real_first_public_at=null`;
denominador independiente nulo; cero ciclos AB; 0/6 puertas.
