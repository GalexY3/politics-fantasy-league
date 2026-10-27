# Politics Fantasy · nuevo BRANCHING20C · cierre R5 (27/10/2026)

**Autorización:** nueva concesión explícita «Concedido», independiente del permiso conservador agotado anterior. **Balance:** 4 registros C01–C04 consumidos (C04 parada R5), **16 autorizados sin consumir**. Método AB 3.2.1/O7, AB-H: AB-R y AB-P no comparten criterios de confirmación científica.

## C01 — fase jurídica del mandato y acatamiento (AB-R)
Prerregistro: [C01_PREREG.json](C01_PREREG.json). Resultado: [C01_RESULT.json](C01_RESULT.json).

La [sesión nº 82 del Senado, 15/09/2026](https://www.senado.es/web/actividadparlamentaria/sesionesplenarias/pleno/rwdsesionespleno/detalle/index.html?id=83&legis=15&ns=82) registra el **acatamiento constitucional** de Clara María Martín García, Javier Ignacio Maroto Aranzábal y Francisco Javier Iglesias García, expedientes **500/000322–324**. Es una cuarta clase de actuación distinta de la aceptación de candidaturas, la designación autonómica y la fecha de inicio del mandato que ya se auditaron en RC05/RC06.

[BOE-A-2025-23055](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2025-23055), vigente desde **15/11/2025** según análisis BOE, artículo 12: la condición se perfecciona tras **credencial + declaraciones + juramento/promesa**, conjuntamente. El acatamiento del 15 de septiembre no acredita automáticamente ni la fecha de presentación de credencial ni la fecha de declaraciones de las tres personas. Se **desconoce** para cada persona el instante de perfección de la condición y la fecha original de difusión pública de cada campo. Por tanto no afirmar capacidad plena desde 10/09 ni desde 11/09 ni simplemente desde el acto de acatamiento.

**Alcance epistemológico:** casos seleccionados tras conocer las fuentes; contraste exploratorio, no estimación de error, causalidad o generalización a todos los senadores.

## C02 — ataque de falsa procedencia sobre función pura (AB-P)
[C02_PREREG.json](C02_PREREG.json) · [C02_RESULT.json](C02_RESULT.json).

Se ejecutó el módulo anterior `provenance_claim_gate.py` con prueba negativa: sin registro de evidencias, devuelve `eligible=False`; con un mapping pasado por el propio llamador que falsificaba `first_public_at`, devuelve `eligible=True` pero **`release_grade=False`**. Los 10 tests de RC07 se reejecutaron con PASS en staging. **No se ha demostrado ningún exploit HTTP**: el servidor actual no expone esa función en una ruta pública. Hallazgo técnico confirmatorio de una dependencia de confianza que el informe anterior ya advertía, no nueva vulnerabilidad remota ni hallazgo científico.

## C03 — índice interno inmutable y ensayos (AB-P)
[C03_PREREG.json](C03_PREREG.json) · [C03_RESULT.json](C03_RESULT.json) · [módulo](../../src/politics_fantasy/source_event_registry.py) · [tests](../../tests/test_source_event_registry.py).

El módulo versionado contiene tres referencias documentales fijas: `ESE/000002-01` (aceptación de nominaciones), `ESE/000002-02` (designación plenaria) y `SENADO-XV-P82-20260915` (acatamiento). Todos tienen `first_public_at=None`, por lo que se rechazan como evidencia disponible `as_of` de eventos reales. La condición plena sigue sin certificar.

**Diez pruebas Python locales, 10/10 PASS:** tipos incorrectos, ausencia de primera publicación, rechazo de condición plena por mero acatamiento, referencia desconocida, rechazo de parámetro falsificado `trusted_registry`, imposibilidad de modificar el registro interno editando una copia del catálogo, y corte temporal sin zona horaria. Se ensayó una copia local exacta del módulo publicado; no se ha ejecutado la suite sobre un checkout completo, ni E2E. El registro fijo no está respaldado por firma institucional; es un **índice documental**, no una certificadora de fuentes.

## C04 — intento de integración HTTP y STOP_R5 (AB-P)
[C04_PREREG.json](C04_PREREG.json) · [C04_RESULT.json](C04_RESULT.json).

Se especificó una ruta de solo lectura `/api/source-stages` detrás del `Host` local y controles contra inyección de fuente. La escritura del cambio en `server.py` fue bloqueada por las protecciones de la herramienta de edición conectada; posterior lectura confirmó que **la ruta no estaba presente**. No existen nuevas pruebas HTTP realizadas ni un endpoint desplegado, y no se atribuye aceptación de usuario, avance de producto o seguridad real a este intento. Registrado como STOP_R5.

## Metodología, trazabilidad y límites de crecimiento
- [CAMPAIGN_INIT.json](CAMPAIGN_INIT.json) y [CAMPAIGN_FINAL.json](CAMPAIGN_FINAL.json) separan el bloque nuevo del histórico cerrado. C01–C03 cerrados, C04 STOP; **4/20 contabilizados, 16 aún disponibles**. No se pide otra autorización.
- [PRIORS_DELTA.json](PRIORS_DELTA.json) incorpora y contextualiza los nuevos priors: fases jurídicas, dependencia del registro de confianza, ausencia de `first_public_at` y falta de integración HTTP.
- [Catálogo de fuentes](../../docs/CATALOGO_FUENTES.md) actualizado con Senado/BOE, granos, fuentes y limitaciones.
- [Atlas delta 0007](../../ab_atlas/updates/0007-pfl-b20c-20261027-r5.json) append-only, `parent_batch=0006-PFL-RC06-RC07-CLOSE-20261027`. Replay estructural independiente sobre 7 JSON verdaderos del repositorio: **PASS, 33 nodos, 51 enlaces, 25 runs, 17 complaints, 97 operaciones**. **No se ejecutó el validador Python oficial `atlas_delta.py check`** ni se generó hash íntegro del nuevo estado.
- Coste GitHub Actions solicitado: **0**, commits `[skip ci]`; ninguna modificación de `main`.

**Indicadores invariantes:** PFL-V1 rev3 36,35 % convencional; CT2 identidad 29/100 ordinal; VSDS 1/3; N1/N2/N3 científicos nuevos 0/0/0; 0/6 gates críticos acreditados. No se habilitan puntuaciones políticas de personas reales.

**Razón R5 para interrumpir sin agotar los veinte:** el contraste legal y la seguridad de función pura están delimitados, pero no existe prueba nueva de primera publicación histórica por observación, ni bytes originales descargados aquí, ni una integración/checkout real comprobable en este entorno. Repetir los mismos documentos o acumular tests sintéticos sería pseudo-replicación. Para reanudar de forma discriminante: fuentes originales/fechas confiables, adjudicación por fuente independiente de un homónimo completo y/o validación de integración del índice por API local + `atlas_delta.py check` oficial con checkout revisado. Mantener las 16 plazas intactas hasta entonces.
