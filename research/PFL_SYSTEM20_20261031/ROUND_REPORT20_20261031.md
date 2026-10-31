# PFL SYSTEM20 · R20: conocimiento de aristas procesales antes del corte jurídico

**Fecha:** 31 de octubre de 2026. **Base R19 publicada:** `8c8ee7d0086d1cff826f9e33387e72b7614dcca4`. **Clase:** reparación técnica con falsador sintético; **no** ciclo AB, **no** resultado empírico sobre España. Atlas99, originales privados y autorizaciones históricas permanecen fuera del alcance de esta edición. Método AB 3.2.1/O1–O7 según `METHOD_REFERENCE.json`, sin cambio unilateral.

## Problema nuevo F03 y oráculo previo a la reparación

R19 corrigió la selección de una *revisión de vértice* antes de cortar eventos por fecha jurídica. R20 inspeccionó otra estructura distinta: **aristas con identificadores tipados** que enlazan registro, expediente, actuación, decisión y publicación, potencialmente N:M. El contrato `synthetic_registration_graph.audit_graph` filtraba las declaraciones de arista por `document_on <= cut_on` **antes** de resolver si había dos documentos incompatibles, ambos conocidos en `as_of`, bajo el mismo `edge_id`.

El oráculo usa únicamente objetos `SYNTHETIC:`. Una declaración `EDGE_1` documentada en 2020 y capturada en enero de 2026 vincula un registro a un expediente. Otra declaración con **el mismo ID**, fecha documental en 2021, capturada en febrero de 2026 y con SHA reclamado distinto discrepa del documento anterior. En enero de 2026, cuando la declaración posterior todavía no era conocida, el inventario histórico admite provisionalmente la arista antigua. En marzo de 2026, sin autenticación ni regla explícita de revisión para aristas, **es inseguro seguir presentando la arista como libre de conflicto**: la declaración posterior se conoce aunque su fecha documental supere el `cut_on=2020-12-31`. La solución conservadora es cuarentena, no incorporar la segunda arista como válida ni inventar una sucesión autorizada.

La prueba se escribió **antes** de ejecutar y reparar, y se congelaron SHA del código y el oráculo:

- Recibo `../PFL-scratch-links2-20261031/ronda20/PREPATCH_SHA256.json` SHA256 `265f91aca74b214ab576239fd2c11a1e3f439071142bcf2a884d57f251925f64`.
- Fuente `synthetic_registration_graph.py` prepatch SHA256 `48d4d69730dd82ee62270a53e51bdfc2fc1b017d153b2b32d8cba4137e879d71`.
- Oráculo `tests/test_r20_edge_conflict_knowledge_cut.py` SHA256 `2bf79507c87ca63d12f09bf58db40e6bb71c37c40e1dcd7ede9c843529de4267`.
- Resultado `PREPATCH_TEST.log` SHA256 `e077b94a3be4d9aa29406551bcc6d901a7ab87f04c8951b43d22561f8425df8e`: **1 fallo material esperado, 2 controles correctos**, 0,42 s. El sistema devolvía `SYNTHETIC_DOCUMENTARY_GRAPH_ONLY` en vez de `VISIBLE_CONFLICTING_EDGE_CLAIM_QUARANTINED` cuando ambas declaraciones eran conocidas. El control anterior a captura conservaba el enlace conocido; una declaración posterior de **otro** ID no añadía aristas indebidamente al corte antiguo.

## Corrección y alcance

Se separó de manera explícita el orden de operaciones de las aristas: **revisar conocimiento y captura local en `as_of` → detectar conflicto por identificador de arista → filtrar por la fecha del documento `cut_on` → comprobar extremos y ensamblar relaciones N:M**. La detección de conflicto depende de si dos declaraciones incompatibles eran conocidas, no de si ambas fechas de documento caben en el periodo jurídico. El cambio conserva la protección de aristas todavía no conocidas y del límite de fechas de documentos, pero prefiere **cuarentena** a un enlace histórico falsamente nítido.

Este régimen es deliberadamente distinto del de `StageVersion`: esa clase declara explícitamente una `revision` y permite seleccionar la versión conocida más reciente del mismo vértice. `TypedStageEdge` no dispone de una sucesión oficial autenticada; dos declaraciones distintas bajo un mismo `edge_id` no pueden interpretarse como actualización lícita sin prueba externa. Ni un SHA alegado ni un identificador sintético acreditan origen institucional.

El recibo `../PFL-scratch-links2-20261031/ronda20/POSTPATCH_SHA256.json` fue creado **antes de la regresión ampliada**, con SHA256 `4b25c0796c5279b5c1945ccd1e2787f7d95c25117b3237277ab26a776419d021`; código reparado SHA256 `55e12770207469483670167772da9347599bfbf42f96360177b153960d2be6a4` y oráculo intacto SHA256 `2bf79507c87ca63d12f09bf58db40e6bb71c37c40e1dcd7ede9c843529de4267`. Primera QA focal postpatch **32/32 PASS** en pruebas de aristas R20, grafo R16 y regresión temporal R19.

**Clasificación:** riesgo futuro en la instrumentación sintética de grafos documentales; **no** se ha demostrado explotación de un endpoint real, consulta de aristas de expedientes auténticos ni contaminación observada de un denominador oficial. No se han leído originales, PII, desenlaces individuales ni sus hashes privados para esta prueba. Una cuarentena documental no significa una decisión jurídica negativa ni una censura.

## Interpretación sistémica e identificación

La integridad de relaciones institucionales es relevante para distinguir persistencia funcional, continuidad jurídico-institucional y continuidad documental. Un expediente que aparezca conectado con otro por un ID reutilizado no prueba que la organización política haya reproducido una decisión ni que exista retroalimentación entre instituciones. En un análisis luhmanniano, la reproducción exige secuencias de comunicaciones/decisiones atribuibles; en uno inspirando en Easton, la identificación de entradas y outputs requiere poblaciones y trayectorias definidas; en Deutsch, una respuesta reguladora exige antecedentes temporalmente anteriores y mecanismo verificable. Un enlace contaminado puede generar una falsa continuidad en cualquiera de esas formalizaciones.

**Falsador de la cautela:** una fuente oficial autenticada que documente expresamente la genealogía y vigencia de varias versiones de una misma arista, con `valid_from`, `valid_to`, publicación/captura y crosswalk tipado. Bajo ese contrato se podría diseñar una política de revisión conocida, en lugar de cuarentena genérica. Es una condición de investigación futura, no un hecho encontrado en R20.

La **condición R5 STOP** permanece intacta: no existe población longitudinal empírica admisible con derechos de distribución, denominador independiente, negativos/pendientes/censura, vintages históricos y `first_public_at` autenticado. R20 no crea material para un test A–J. La cola anterior C15 (alias/jurisdicción) sigue `QUEUED`; esta corrección **no satisface** por sí sola su contrato de colisiones entre autoridades y no se marca como completada. Aun tras un STOP local se puede continuar otra ruta con evidencia nueva, pero no gastar plazas AB por QA.

## Estado y continuidad

El ledger añade **dos trabajos no cíclicos**, pruebas/reparación F03 e informe/integración R20, ambos `cycles_charged:0`. Presupuesto SYSTEM20: 20 autorizadas, **0 válidas, 0 inválidas, 0 planificación, 20 disponibles**. La cola de 20 líneas mantiene 1 `BLOCKED_R5`, 9 `PARKED`, 4 `COMPLETED_NONCYCLE`, 6 `QUEUED`. La siguiente oportunidad real es un problema nuevo de identidad interinstitucional o de derechos que pueda falsarse sin consultar originales protegidos; no repetir R5–R19.

**QA focal ampliada ejecutada en Windows:** **137/137 PASS** en diez suites Python de los contratos de índice, temporalidad R18/R19/R20, grafos sintéticos, registro y readiness HTTP; `python -m compileall -q src/politics_fantasy` PASS. Atlas99 comprobado desde `seed + updates`: **99 lotes, 63 nodos**, SHA256 `bc4c7b094df4cb95f073a3d41f18c5c362bea80ca6b3ce275ed07593571c46e9`, sin deriva. Las comprobaciones de índice/proyecto, staging, secretos y publicación Git se documentan en el cierre; estos ensayos no acreditan autenticidad de datos. No se ha ejecutado Linux ni CI remota. No se fusiona PR #7 a main ni hay despliegue público.
