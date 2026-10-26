# BR20K — priors y validez del indicador de avance (26 octubre 2026)

La métrica de progreso del proyecto NO sustituye los priors científicos AB, CT2 ni VSDS. Los priors anteriores PF-P, PF-MG, PF-H, PF-I y PF-J siguen intactos en el ledger acumulativo. Añadir estos priors de gobernanza no constituye innovación científica confirmada.

## PF-K01 — Madurez del proyecto solo tiene significado condicionada a un alcance congelado

**Proposición:** un porcentaje sin denominador y definición de producto es arbitrario. Es válido publicar un índice reproducible cuando tareas, pesos, niveles y snapshot están versionados y auditados. **Procedencia:** 9 vías y 36 hitos en [scope V1](../../product/progress_scope_v1.json), fórmula en [progress_model.mjs](../../src/politics_fantasy/progress_model.mjs), 20 checks V8. **A favor:** 33,725% reproducible de 36 niveles codificados. **En contra:** tamaños de tareas, pesos y madurez son juicios de diseño, no estimaciones de horas ni de éxito científico. **Falsador:** cambiando arbitrariamente los pesos se muestra una falsa continuidad o se pierde trazabilidad de subobjetivos. **Estado:** prioridad de gobernanza, no descubrimiento sociológico.

## PF-K02 — Progreso ponderado y disposición para lanzamiento deben calcularse aparte

**Proposición:** seis gates bloqueantes de datos originales/identidad/eventos individuales/auth/QA E2E/despliegue pueden impedir producto público aunque la demo sea funcional. **A favor:** [snapshot](../../product/progress_snapshot_v1_20261026.json) y `evaluate(scope).release_blockers`. **En contra:** los seis gates son anclas de la V1 y podrían variar con arquitectura nueva o cambios legales. **Falsador:** despliegue validado que cumpla finalidad de V1 y permita operar sin uno de los gates, con justificación de equivalencia. **Estado:** control operacional versionado.

## PF-K03 — La puntuación puede bajar legítimamente cuando crece el scope

**Proposición:** sin ningún cambio de trabajo, un quinto requisito de cobertura municipal nacional en la sublínea de fuentes reduce el índice de 33,725% a 32,330% (−1,395 pp). **A favor:** [comparación con detalle](../../product/progress_scope_change_example.json), pruebas V8 del mismo cálculo. **Contra:** distribución de efecto dependiente de pesos y composición de la vía, secuencia work-first no única. **Falsador:** fórmula que declara mismo baseline y pesos, pero no reproduce la diferencia. **Estado:** resultado matemático **hipotético**, NO revisión V2 adoptada.

## PF-K04 — Evidencia de fuente, integridad de archivo y validación original no son equivalentes

**Proposición:** tener catálogos abiertos y una URL de JSON oficial no significa disponer de filas validadas y reconstruidas para actividad de personas. **A favor:** [descubrimiento del esquema de diputados](ORIGINAL_SOURCE_DISCOVERY.md): JSON activo de julio 2026 legible por web, sin preservación local de bytes, no roster bitemporal; consulta del RPP solo interfaz. **En contra:** el JSON oficial es una vía realista de adquisición posterior; la dificultad puede ser contingente al entorno. **Falsador:** capturar bytes originales SHA256 y un enlace jurídico/histórico verificable. **Estado:** limitación epistemológica de fuentes, J STOP_R5.

## PF-K05 — Cuantificar trabajo no autoriza aumentar VSDS o CT2

**Proposición:** un control de proyecto valorado 33,725% no es una evaluación del valor sociológico, la novedad científica, la potencia predictiva ni la probabilidad de fin. **A favor:** [VSDS](../../docs/VSDS_PROYECTO.md), [TFM](../../docs/PLAN_TFM.md), límites de cohorte. **Contra:** podría surgir evidencia sustantiva de campo en futuras campañas y justificar cambios de otro indicador, no por el simple progreso del código. **Falsador:** comparación prospectiva fuerte con dataset original que cambie justificadamente VSDS. **Estado:** separación conceptual.

## PF-K06 — Prueba disponible no equivale a prueba ejecutada

**Proposición:** pruebas Node y Python/HTTP publicadas pero no ejecutadas no deben contarse como validación nativa de nueva API. **A favor:** 20/20 contratos de funciones puras pasaron en V8; [test_progress_api.py](../../tests/test_progress_api.py), [test_progress_http.py](../../tests/test_progress_http.py) y workflow CI están escritos sin un job PASS observado. **Contra:** una ejecución limpia puede confirmar la funcionalidad, pero también revelar errores. **Falsador:** logs reproducibles del checkout actual con green tests y resultados HTTP. **Estado:** prior de medición y QA.

## Resumen de contabilidad

**Cierre BR20K: 20/20 A–J**, 4 decisiones STOP_R5, 20 pruebas de progreso JS ejecutadas en V8, sin corpus original nuevo ni validación nativa de Python/HTTP. **VSDS 1/3**, **CT2 multiactor 20/100**, **CT2 predictiva parlamentaria 24/100**, **N1/N2/N3 nuevos 0**. El índice de completitud V1 = **33,725%**, con metodología y ámbito fijados.
