# ABH25B · cierre científico-técnico de 25 ejecuciones limitadas

**Concesión nueva**: PFL-ABH25B-20261030, 25/25 ciclos de alcance limitado registrados en [AUTHORIZATION.json](AUTHORIZATION.json). Independiente de ABH25, READ5-CONTINUE15, ABH10, INTEGRATION10 y plazas históricas R5. PR #4 es **draft** y está apilada sobre PR #3 (ambas NO integradas en `main`); no publicar ni desplegar.

**Clasificación**: 12 contrastes AB-R sobre medición, procedencia o fuentes públicas; 13 mejoras AB-P de funcionalidad ficticia, incluidas diez métricas distintas con controles; **ninguna nueva observación acredita causalidad ni validación de una teoría sociológica original**. CT2 científico interno 20/100 ordinal; N1/N2/N3 = 0; 0/6 puertas de lanzamiento; P1 sigue READY_REVIEW hasta aceptación humana.

## Resultados AB-R y su alcance

- **C01**: Reino Unido, cuatro páginas congeladas, 100 peticiones cerradas; solo 25 pares de fecha de umbral/respuesta observables, 16 intervalos superiores a 21 días en ese subconjunto. No estimar incumplimiento nacional ni confundir fechas API con primera publicación autenticada. [Recibo](C01_RUN_RECEIPT.json).
- **C05-C08**: Escocia, fuente pública original y regímenes de censura diferenciados. C05 páginas cerradas: 15 registros sin campos directos de respuesta. C06 15 cerradas con mediana de apertura→cierre 319,37 días, no distribución poblacional ni hazard. C08 15 bajo consideración con edad observada mediana 127,57 días y **censura derecha**. [C05](C05_RUN_RECEIPT.json), [C06](C06_RUN_RECEIPT.json), [C08](C08_RUN_RECEIPT.json).
- **C09**: primer tramo original de estado mixto del Senedd, 50 peticiones (33 abiertas, 16 rechazadas, 1 cerrada). Fuente y SHA en [recibo](C09_RUN_RECEIPT.json).
- **C10**: 50 peticiones británicas rechazadas de dos páginas originales, con rechazo/moderación distinto de respuesta del Gobierno. **Recibo anterior ya congelado y ejecutado**, hallado al reconciliar el ledger; no sobrescrito. [Recibo](C10_RUN_RECEIPT.json).
- **C11**: 50 peticiones británicas de páginas cerradas con distinto nivel de firmas; 25 superaron 100.000, pero solo 21 de ellas tenían fecha de resultado de debate registrada; elegibilidad no equivale a debate efectivo ni petición aprobada. **Recibo anterior ya congelado y ejecutado**, no recontado. [Recibo](C11_RUN_RECEIPT.json).
- **C10W**: 50 peticiones galesas abiertas; 44 con al menos 250 firmas y 6 con al menos 10.000. El estado abierto no descarta remisión a comisión, ni acredita respuesta institucional. [Recibo](C10W_RUN_RECEIPT.json).
- **C11W**: 29 peticiones galesas en estado `completed`; ese estado no demuestra que se aceptara la solicitud ciudadana. [Recibo](C11W_RUN_RECEIPT.json).
- **C12**: 25 peticiones británicas abiertas en página fija, ninguna alcanzó 10.000 firmas ni presentaba fecha de respuesta; ausencia de respuesta en esos registros no es rechazo institucional. [Recibo](C12_RUN_RECEIPT.json).
- **C15**: consulta galesa de peticiones remitidas a comisión, 31 registros cuyo `state` actual es `closed`. La selección por remisión y el estado del ciclo de vida no son equivalentes. [Recibo](C15_RUN_RECEIPT.json).
- **C14B**: reemplazo de C14 bloqueado, usando un mecanismo diferente. Una única petición británica seleccionada por el mínimo ID de una página fija: 650 entradas de circunscripción, 108.206 firmas territorializadas frente a 110.519 totales, diferencia 2.313 de causa no verificada, HHI bruto 0,002112701780432538, equivalente matemático de 473,33 circunscripciones uniformes; sin normalización por población. **No son firmas de los diputados ni apoyo de estos**, y existe investigación previa sobre geografía de peticiones. [Recibo](C14B_RUN_RECEIPT.json).

**Solapamientos y negativos NO contados:** C02 Canadá devolvió HTML, no XML; C14 Escocia página 12 vacía; nuevo C13 repitió mecanismo de debate de C11; nuevo C16 repitió moderación/rechazo de C10. En el primer CI de C09-C16 falló un control de fixture con JSON malformado y se reparó antes de consultar datos. Los nombres C10W y C11W se adoptaron porque C10/C11 ya tenían recibos válidos; las preguntas galesas estaban prerregistradas antes de outcomes y no se reescribieron. [Adjudicación y SHA de fuentes](C09_C16_COLLISION_AND_NEGATIVES.json). Los registros no son muestras representativas, y algunas páginas/consultas se solapan: **no sumar sus n como personas o peticiones únicas**.

## Resultado AB-P: funcionalidades reales de ficción, no evidencia humana

- **C03**: desglose de puntos por figura congelado transaccionalmente al cerrar una jornada; sin reconstruir inventadamente rondas antiguas. [Recibo](C03_RUN_RECEIPT.json).
- **C04**: clasificación acumulada por puntos asentados, empates y cobertura insuficiente. [Recibo](C04_RUN_RECEIPT.json).
- **C07**: historial local de transferencias limitado por club, persistencia y UI. [Recibo](C07_RUN_RECEIPT.json).
- **C17–C26**: diez indicadores nuevos visibles en la pantalla principal y derivados exclusivamente del estado aislado de cada cuenta local: valor de cartera ficticia, fichajes asequibles, Shannon de roles, HHI de grupos inventados, valor de titulares y reserva, flujo limitado de créditos, rotación del mercado, preparación de alineación, media de jornadas efectivamente puntuadas y concentración de aportaciones congeladas. [Contrato A–J](C17_C26_PREREG_AJ.json), [recibo](C17_C26_RUN_RECEIPT.json). En [GitHub Actions #41105541770](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41105541770), **10/10 pruebas Python y 2/2 pruebas Node nuevas pasan**; cobertura de los tests limitada, sin UX humana.

## Teoría, fuente, selección y amenazas

La evidencia apoyada por las peticiones UK/Wales/Scotland permite mejorar una *ontología de respuesta institucional*: moderación, logro de umbral, remisión, examen, respuesta escrita, debate y clausura son eventos semánticamente distintos. No permite inferir el efecto causal del número de firmas en la adopción de políticas, el tratamiento de individuos, ni comparar porcentajes entre instituciones sin marcos de muestreo y definiciones homologadas.

**Fuentes**: [UK Parliament petitions](https://petition.parliament.uk/petitions), [Senedd petitions](https://petitions.senedd.wales/petitions), [Scottish Parliament petitions](https://petitions.parliament.scot/); originales públicos con SHA en cada recibo. Priors PF-BR85–PF-BR88 versionados en `research/ABH_BROWSER_ATLAS_EVIDENCE5_20261029/SOURCES_AND_PRIORS.json`, nodos y dependencias O7 actualizados. Los bytes individuales con texto/personas no se incorporan al repositorio; solo métricas agregadas y hashes.

## Integridad y cierre pendiente de QA

El ledger registra **25/25 ejecutados, 0 pendientes** y preserva los anteriores saldos. El lote Atlas98 debe reproducirse sobre la rama; el índice canónico, los tests de Python y Node, el estado derivado y esta PR deben pasar CI antes de considerar el cierre técnico íntegro. **No hay fusión a main, aprobación de publicación, aceptación humana de P1 ni aumento de CT2.**

**Siguiente programa discriminante:** muestreo estratificado por cohorte/estado con captura versionada de umbral→respuesta y comparación de marcos jurídicos, además de prueba de uso real de P1. Solo nuevos ciclos con observación o producto sustantivo, no reproducción redundante de páginas ni mero mantenimiento.
