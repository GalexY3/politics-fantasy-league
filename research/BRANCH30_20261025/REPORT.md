# Informe de campaña BRANCH30 · Politics Fantasy League, v0.4

**Fecha:** 25-10-2026 · **Estado:** cierre 30 incrementos de ingeniería verificables; cero experimentos políticos confirmatorios. Se aplicó *branching* condicionado: A (integridad nominal) → B (medición) → C (estructura/composición) → D (evaluación) → E (producto navegable). Diseño de cada lote congelado en GitHub **antes** de ejecución mediante commits por lote; el código fuente se publicó después de realizar pruebas, por lo que NO se cumple el requisito científico completo O2 de *code freeze prior to run*. Este documento es readout retrospectivo, no validación científica.

## Decisión del investigador: VSDS

Solo en este proyecto, el equivalente visible a los grados 0/3–3/3 se llama **VSDS: Valor Sociológico y Data Science**, y califica utilidad, instrumentación y transferibilidad; la escala de descubrimientos de AB 3.2.1 sigue en campos separados. Definición canónica: `docs/VSDS_PROYECTO.md`. Valor global actual: **1/3** (cinco subsistemas instrumentales verificados en laboratorio sintético). Requisitos VSDS-2/3 (datos humanos/institucionales certificados y comparación) y VSDS-3/3 (uso/confirmación independiente y transportabilidad) no satisfechos.

## Balance

| Rama | Números | Ciclos de producción aceptados | Resultados/limitaciones |
|---|---|---:|---|
| A. Historial nominal | 01–06 | 6 | Elección cerrada, conflictos, doble corte de disponibilidad, revisión, grupo histórico |
| B. Medición sociológica | 07–12 | 6 | Elegibles explícitos, desconocidos, mayorías per-vote, abstención, Mixto/ties |
| C. Estructura | 13–18 | 6 | Margen, diversidad, estandarización, Simpson, covoto con baseline marginal |
| D. Predicción | 19–24 | 6 | Poisson NLL, MAE, skill, calibración, embargo, bootstrap clusters |
| E. Producto | 25–30 | 6 | Fixture sin identidades reales, reporte separado, VSDS, endpoint `/api/lab`, integración UI |
| **Total** | **01–30** | **30** | **No independencia científica: son incrementos de ingeniería bajo una suite común** |

Total automatizado: **87 pruebas** (57 preexistentes + 30 nuevos contratos). El documento `QA_20261025.txt` registra la salida. JS sintaxis validada con `node --check`. La suite nueva no es una prueba de seguridad, ni cotejo del JSON oficial, ni test exhaustivo visual cross-browser.

**Iteración fallida conservada:** en BR30-13, la primera versión del *test* exigía un margen de mayoría de 1/2 para 2 YES frente a 1 NO y 1 NO_VOTE. El margen real con denominador de votos expresos es (2-1)/3 = 1/3. Se corrigió el resultado esperado, no el código ni el denominador. El fallo no crea un ciclo extra ni prueba una teoría.

## Hipótesis sociológicas relevantes y límites

- Medir participación necesita **censo de oportunidades individual fechado**; una fila ausente no es evidencia de ausencia. No se calculará tasa puntual si falta cobertura.
- Discrepancia con la mayoría de grupo puede calcularse condicionando por grupo en fecha, pero no permite atribuir autonomía, conflicto, incoherencia o ideología.
- Altos niveles de covoto pueden explicarse en gran medida por los márgenes de las decisiones. La baseline marginal aquí es simple y requiere rivales más fuertes (partido, agenda, periodo) antes de informes sociológicos.
- El test de inversión de Simpson demuestra una posibilidad matemática, no que ocurra en España. Contrastes estratificados por temas sin prereg causan selección.
- Penalizar a figuras por bajo volumen de actividad sin reconocer oportunidades distintas convertiría visibilidad administrativa en aparente valor personal. El fantasy continúa completamente ficticio.

## Corpus y prioridad externa

La web institucional del Congreso expone resultados agregados y recursos nominales descargables: https://www.congreso.es/es/opendata/votaciones. La metodología de Congreso Abierto (https://congresoabierto.org/metodologia/) ilustra complicaciones de afiliación en fecha, falta de nominales en votaciones secretas o por llamamiento y diferenciación de no-voto; **no se importaron sus microdatos en esta campaña**. Este conjunto de 30 ciclos NO contiene ningún dato parlamentario nominal validado. No se estimó ningún político real. Son antecedentes públicos, no certificados de este software.

## Valor/CT2 y juicios AB

- VSDS=**1/3**, útil como prueba de infraestructura para sociología/data science. Niveles originales de descubrimiento científico: N1=0, N2=0, N3=0; CT2 de predicción individual parlamentaria=**24/100**, sin cambios por 30 tests sintéticos. Escala CT2 ordinal/no probabilidad.
- Confirmación empírica externa: ninguna. Semántica de fuentes: NO CERTIFICADA. Inferencia causal: ninguna. Originalidad: no reivindicada.
- Comparadores: negativos deterministas (ausencia=no-voto, mayoría agregada, no ajuste, skill sin baseline, IID bootstrap). No hubo comparadores empíricos ejecutados sobre corpus real.
- Validación informática: local, repetición posterior con extracción limpia del release ZIP. Falta revisión visual en navegador y seguridad multiusuario.

## Decisión y branching

**CONTINUE PRODUCT + REPAIR EXTERNAL DATA.** Los siguientes ciclos con mejor valor esperado son conectores nominales con hashes, revisión de schema/intervalo de publicación, censos de oportunidades y afiliación longitudinal; evaluar baselines en ventana congelada; instrumentar seguridad de cuentas antes de publicar el fantasy. Un despliegue abierto no está autorizado técnicamente (servidor local sin auth).

**Saldos:** PF-B50: 42 pendientes antes de esta tanda, 30 consumidos como incrementos de producción, quedan **12**. PF-F45: **45** bucles libres autorizados no consumidos; PF-AB20: **19** pendientes de ejecución empírica. La nueva autorización de 30 **no se suma como saldo extra**: se aplicó al PF-B50 ya concedido, sin confundir planificación y prueba.

## Publicación y migración

Provisional en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`. Mover a `GalexY3/polictics_fantasy_league`, conservando hash/commits y dejar puntero; no modificar métodos AB ni hacer de repositorio metodológico depósito definitivo.

## Solicitud de continuidad al investigador

La siguiente campaña debería permitir **BRANCHING de producción + investigación**, focalizada en conectar fuentes institucionales reales y validación sociológica antes de optimizar la gamificación. No se cuenta como autorización hasta respuesta del investigador; la solicitud tampoco invalida los saldos autorizados aún no consumidos.

SOLICITO BRANCHING 30 CICLOS
