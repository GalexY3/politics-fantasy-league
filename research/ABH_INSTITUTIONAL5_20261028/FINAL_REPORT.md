# Politics Fantasy League — AB-H INSTITUTIONAL5 — Cierre de 28/10/2026

**Estado:** 5/5 ciclos A–J de alcance explícitamente acotado **válidos** (C01–C05), 0 inválidos, 0 de planificación, 0 pendientes. **Cinco AB-R**; no hay AB-P ni implementación productiva. Rama `research/pfl-abh5-institutional-20261028` desde `research/pfl-abh5-source-validation-20261028` SHA inicial `3db7e73c425d234e88270ebadae03c252a0a320c`. ChatRelay **NO** utilizado. Ni `main` ni las PR #18–20 se han fusionado. Ejecutor Codex **T011 no ejecutado**.

## A. Indicadores

| Indicador | Antes | Después | Nota |
|---|---:|---:|---|
| AB-H autorizados/válidos/inválidos/planificación | 5/0/0/0 | **5/5/0/0** | Todas las preregistraciones preceden a la investigación correspondiente |
| CT2 identidad | 29/100 | **29/100** | Escala ordinal, no probabilidad |
| Valor VSDS | 1/3 | **1/3** | Sin experimento discriminante |
| Madurez contractual V4 | 36,90 % | **36,90 %** | Los hallazgos no son adjudicación de los 36 hitos |
| Logros simbólicos | 2/90 | **2/90** | Ninguno adicional adjudicado |
| Gates release | 0/6 | **0/6** | No se ejecutó despliegue |
| N1/N2/N3 nuevos | 0/0/0 | **0/0/0** | No confundir con cartera histórica sin reauditar |

[Serie CT2](CT2_TRAJECTORY.json) · [Gráfico 0–100 y ampliación](CT2_FULL_AND_ZOOM.svg). La línea CT2 permanece en 29 porque se ha mejorado la procedencia y el diseño sociológico, **no** validado una ventaja de identidad o de predicción sobre comparadores fuertes.

## B. Cinco ciclos de investigación

| Ciclo y preregistro | Pregunta / fuente nueva | Resultado adversarial sustentado |
|---|---|---|
| [C01](C01_RESULT.json) · [prereg](C01_PREREG.json) | INE ODS 5.5.1 · diferencia entre alcaldesas y concejalas 2025 | INE indexado: alcaldesas **25,01 %**, concejalas **42,76 %**, brecha de **17,75 pp**. El `open` accesible devolvió copia antigua 2024 (24,77 y 42,80). Distinguir fuentes/versiones, no afirmar descarga 2025 original. |
| [C02](C02_RESULT.json) · [prereg](C02_PREREG.json) | BOE-A-2023-15066, candidaturas 2023, vs JEC BOE-A-2023-18907, resultados | En Guadalajara se inspeccionaron **10 listas** con tres puestos principales cada una, separados de suplentes, y **3 escaños** en resultado, asignados PP 1, PSOE 1, VOX 1. Son *puestos de lista*, no 30 identificaciones de personas únicas ni probabilidades de elección. Sin género inferido. |
| [C03](C03_RESULT.json) · [prereg](C03_PREREG.json) | BOE LO 2/2024, LO 3/2007 y JEC 3/2025: alcance y periodo de exposición | Desde **22/08/2024**, nueva regla para procesos electorales **convocados después**. Listas de municipios `<=3000` exentas de art. 44bis; `>3000..5000` requieren 40/60 sin alternancia; `>5000` con listas alternas conforme al ámbito legal. 2007 ya establecía 40/60. No inferir efecto causal sobre alcaldías observadas 2025. |
| [C04](C04_RESULT.json) · [prereg](C04_PREREG.json) | Congreso sesión 203 indexada 02/10/2026 + BOE-A-2026-20526/20527 | Dos votaciones distintas, expedientes **130/000055** (sí 172, no 178, abst.0) y **130/000056** (sí 166, no 184, abst.0), con 350 votos contados por consulta indexada. **Dos derogaciones verificadas independientemente en BOE**, pero BOE **no** corrobora el desglose numérico ni los votos nominales. `open` de Congreso entrega caché sesión 193, no 203. |
| [C05](C05_RESULT.json) · [prereg](C05_PREREG.json) | Contraste adversarial 2024 a 2025 de los cinco indicadores ODS INE; prueba de mejora siempre creciente | Cuatro categorías bajan y una sube de 2024 cacheado a 2025 indexado: Congreso **−0,86**, Senado **−0,48**, consejerías **−1,67**, alcaldías **+0,24**, concejalías **−0,04 pp**. Las cinco 2025 superan sus bases 2015. Ministerio de Economía indica ejecutivas de partidos 49,5 % (2024) frente a 47,4 % (2025), indicador distinto: no mezclar denominadores. |

Datos de alcance limitado y sin nombres personales guardados: [INE 2025/2024](C01_INE_ODS_551_AGGREGATES.json), [BOE Guadalajara](C02_BOE_GUADALAJARA_SOURCE_AUDIT.json), [tratamiento jurídico](C03_LEGAL_TREATMENT_EXPOSURE.json), [Congreso/BOE 2026](C04_CONGRESO_BOE_2026_DUAL_EVIDENCE.json), [control adversarial 2024–2025](C05_INE_TREND_NEGATIVE_CONTROL.json).

## C. Procedencia, controles, validez

**Fuentes oficiales enlazadas**:
- INE ODS indicador 5.5.1: https://www.ine.es/dyngs/ODS/indicador.htm?id=4990 — **aviso**: el buscador indexado recientemente devuelve 2025 y el resultado de apertura almacenado 1,1 años antes devuelve 2024; ambos archivados como versiones diferentes, sin supuesta captura del API original.
- Instituto de las Mujeres / Ministerio de Economía, explicación de edición 2025: https://portal.mineco.gob.es/es-es/comunicacion/Paginas/MujeresYHombres_INE_poder_tomadecisiones_igualdad.aspx — distinto indicador para ejecutivas de partidos.
- Candidaturas JEP 2023: https://www.boe.es/buscar/doc.php?id=BOE-A-2023-15066; JEC resultados: https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907 — originales oficiales **HTML consultados**, no PDF original descargado/hash, sin correspondencia individual validada.
- 2024 regla paridad: https://www.boe.es/buscar/doc.php?id=BOE-A-2024-15936 y 2007 precedente: https://www.boe.es/buscar/act.php?id=BOE-A-2007-6115; 2025 interpretación JEC: https://boe.es/buscar/act.php?id=BOE-A-2025-22665. Los textos describen obligaciones normativas; **no prueban cumplimiento ni un efecto**.
- Congreso últimas votaciones: https://www.congreso.es/es/opendata/votaciones; BOE https://boe.es/diario_boe/txt.php?id=BOE-A-2026-20526 y https://boe.es/diario_boe/txt.php?id=BOE-A-2026-20527. Publicación BOE el 02/10/2026, sin hora exacta de publicación del JSON original de voto.

**R1: unidad y estimando**: distinguir candidaturas, puestos principales, titulares electos, concejalías, alcaldías, leyes y votaciones. **R2: rivales competentes**: unidades separadas de carrera política, porcentajes institucionales con denominadores heterogéneos, fuente BOE como verificador de decisión jurídica pero no de tally; regla previa 2007 como baseline regulatorio. **R3: multiplicidad/selección**: las cinco pruebas son exploratorias, con datos descubiertos antes de prereg en algunos ciclos; no contrastes inferenciales ni selección ciega. **R4: controles adversariales**: censo de fuentes incompleto, saltos de fecha/versión, extrapolación de candidaturas a electos, causalidad 2024 sin exposición real, confusión de votación con expediente. **R5**: no repetir reintentos de descargas sin vía nueva; los cinco ciclos sí han ejecutado análisis documental y cálculos existentes, pero **no** se atribuyen nuevos hallazgos 1/3/2/3/3/3 por aritmética o redescubrimiento.

## D. Lista pendiente para Codex/PC, no imputada a ciclos ejecutados

1. **T011** https://github.com/GalexY3/Metodologia-AB/blob/research/pfl-abh5-source-validation-20261028/proyectos/politics-fantasy-league/tareas_codex/T011_FUENTE_PARIDAD_QA_SOURCE5_20261028.md: HTTPS original XLSX Interior, TLS/hashes, inspección exacta de géneros y estratos; full Python/Node/Atlas limpio sobre SHA de PR nuevo, sin publicar filas nominales. **No ejecutada**.
2. **T012 (propuesta, no ejecutada)**: recuperar por SDMX/descarga versionada el INE ODS 5.5.1 para 2024/25/2015, registrar fecha de observación, versión, denominador y hash del original. Verificar que diferencias de cifras no son mezcla de caches o redefinición.
3. **T013 (propuesta, no ejecutada)**: recuperar originales nominales Congreso 02/10/2026 en modo seguro de uso interno, validar secuencia de votos, expediente, categoría de ausencia, fechas `first_public_at` con evidencia no inferida; construir prueba independiente BOE de **resultado jurídico**, no de cifras si BOE no las incluye.
4. **Protocolo futuro**: pruebas de exposición a LO 2/2024 en municipios `<=3000`, `3001–5000` y `>5000` con población legalmente pertinente, elección posterior, reglas autonómicas y controles ante discontinuidad; **no** ejecutar causalidad con el agregado 2025.

## E. Dictamen de novedad y siguiente autorización

**2/3 NO ACREDITADO**. Existe evidencia pública más concreta y una triangulación jurídica de dos decisiones parlamentarias, pero no dataset nominal original, no vínculo longitudinal de personas, no intervención ni línea base predictiva fuerte, no replicación de técnica independiente ni evaluación prospectiva. El valor real del bloque es reducir errores de unidad, procedencia, tiempo y causalidad, no elevar porcentajes ficticios. No se ha hecho ningún test computacional integrado en este bloque (solo cálculo aritmético con JavaScript); no presentar PASS de fuente o reproducibilidad.

**SOLICITO BRANCHING AB-H DE 5 CICLOS ADICIONALES**, solo previa autorización nueva, para nuevas fuentes realmente discriminantes y contrastes competentes, conservando negativos y bloqueos que necesiten Codex. Esta solicitud no es autorización automática.
