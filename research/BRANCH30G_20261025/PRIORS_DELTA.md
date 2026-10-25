# PF-BR30G · ampliación acumulativa de priors tras 30 A–J (25/10/2026)

Este archivo conserva PF-MG-01–03 del informe intermedio y suma los del análisis secundario. Los priors siguientes se consideran descripciones intrafuente, principios instrumentales o hipótesis NO VALIDADAS. **No** son posteriors numéricos, demostraciones causales ni validación independiente de la metodología AB.

### PF-MG-01 — Dependencia del catálogo actual (previo, conservado)
**Proposición**: el importador de Congreso Abierto conserva totales mientras excluye del diccionario nominal nombres sin correspondencia exacta en `diputados_base.tsv`.
Procedencia: importador Git blob `2a9d63c7...` y TSV `fed1b07bbc...`; comprobación documental C01.
A favor: código fuente del importador. En contra/alternativas: no se ha auditado cada fila oficial; fechas, variaciones de nombres, ausencia de originales. **Falsador**: parsing oficial con roster completo produce el mismo patrón. Tipo: VERIFICADO EN CÓDIGO / mecanismo de importación, ámbito específico.

### PF-MG-02 — No enlace es distinto de No vota (previo, conservado)
Proposición instrumental: no reetiquetar ausencias de fila nominal como la categoría de voto explícito X.
Procedencia C02 y separación matemática de totales, fixtures; límites: sin cotejo nominal original de campo. **Falsador**: fuente original demuestra que esa ausencia tiene semántica explícita de X, caso por caso. Tipo: PRINCIPIO DE MEDICIÓN.

### PF-MG-03 — Distinción de universos entre fuentes (previo, conservado)
Metadatos externos declaran 412 personas históricas frente a 350 códigos actuales en el TSV; 2.176 vs 2.175 votaciones, 147 vs 144 sesiones. **NO** deducir que 62 personas causen las 34.654 posiciones sin enlace. Falsador: emparejamiento caso a caso muestra universos incompatibles. Tipo: METADATO EXTERNO, no reconciliado.

### PF-MG-04 — Casi constante cobertura intrasesión
**Proposición**: para 138/140 sesiones con 2 o más votaciones, la cobertura registrada por el importador no varía entre votaciones de la sesión. Procedencia C04, 2.175 filas del blob secundario. Evidencia: dispersión cero en 138/140; dos anomalías con voto sin nominal. Contraevidencia: nuevas revisiones, originales históricos y distinto método de enlazado. Falsador: extracción primaria nominal completa muestra variaciones amplias dentro de sesión. Tipo: DESCRIPTIVO_SECUNDARIO. Implicación: ajustar dependencia por sesión.

### PF-MG-05 — Cambios de signo restringidos a márgenes estrechos en este snapshot
**Proposición**: 125 inversiones estrictas de signo del subconjunto nominal frente al total se encuentran en margen oficial de 20 o menos (62 hasta 5, 63 de 6 a 20). Procedencia C13 + auditor independiente aritmético (MISMA fuente). Contra: es esperable por magnitud de huecos; no aplica a otros archivos. Falsador: revisión de corpus muestra una inversión con margen >20. Tipo: DESCRIPTIVO_SECUNDARIO, sin novedad general demostrada.

### PF-MG-06 — Certificado conservador de signo
**Proposición**: si `|S_observado-N_observado| > M` donde M es el total no observado, ninguna asignación de los M puede invertir el signo observado. Resultado **matemático condicionado**, válido bajo votos categóricos de una sola opción y recuentos correctos. Aplicación C14: 1.655/2.173 casos certificados y 0 discordancias. Contra: la cota puede ser laxa; 518 sin certificado no son 518 errores. Falsador: un caso con conteos correctos y discrepancia dentro de un certificado refutaría la implementación/datos o las condiciones lógicas. Tipo: MATEMÁTICO_CONDICIONADO + DESCRIPTIVO_SECUNDARIO; no proclamar originalidad.

### PF-MG-07 — Estructura ecológica no equivale a disciplina individual
Procedencia C16–C21. Evidencia: unanimidad grupo-votación ≥2 expresados, 88,7453% sin ponderación y 94,0463% ponderando; coincidencia modal de 77.495 pares-grupo/voto 53,388%. En contra/limitaciones: dependencia por sesión, composiciones de grupo, agenda, observador secundario. Falsador: validación nominal/adscripción por fecha o modelos que atribuyan esas variaciones a artefactos. Tipo: DESCRIPTIVO_SECUNDARIO; causalidad NO.

### PF-MG-08 — Tipo de votación como posible predictor exploratorio
**Proposición**: un predictor Laplace secuencial condicionado a tipo obtuvo Brier 0,206260 frente a 0,249226 de un estimador global (C27), en 2.156 votos sin empate de un archivo retrospectivo. **NO_VALIDADO** como predictor real. Riesgos: información disponible en fecha desconocida, clasificación retrospectiva, confusión por agenda, baselines débiles y optimización adaptativa. Falsador: evaluación oficial as-of con baseline institucional competente borra la ventaja. Tipo: RETROSPECTIVO_SECUNDARIO; ninguna CT2 subida.

### PF-MG-09 — Los resultados de un formato no certifican su semántica
Procedencia C24, C29, C30. El campo de asentimiento es false en 2.175 filas; `groupAggregateMismatchedVotes=2` del bruto significa **dos desglose grupales ausentes**, NO dos discrepancias entre grupos existentes; 0/2.173 disconformidades cuando hay grupos. La integridad estructural no prueba identidad histórica ni as-of. Falsador: contrato de fuente original contradice interpretación. Tipo: METODOLÓGICO/PROCEDENCIA.

### PF-MG-10 — Predictibilidad de cobertura puede ser artefacto del sistema de observación
Procedencia C28: MAE retrospectivo de cobertura de sesión siguiente 0,004145 para último valor vs 0,033849 para media histórica acumulada. La secuencia de cobertura no mide comportamiento humano sino reconstrucción del importador con catálogo actual. Falsador: originales de campo generados históricamente y comparadores as-of reproducen utilidad para decisión independiente del importador. Tipo: HIPÓTESIS_INSTRUMENTAL_NO_VALIDADA.

## Inventario/decisiones
C11 rho≈−0,0049, C12 rho≈0,0121: conservar hallazgos nulos/no concluyentes. C24 no contiene casos `asentimiento=true`: marcar no identificable. Ningún ID anterior se borra. El ledger está en `LEDGER.json`; auditoría de precisión C29 en `AUDIT_ADVERSARIAL.md`.

**VSDS** 1/3 sin cambio · **CT2 predictiva** 24/100 sin cambio · **N1 nuevos** 0 · **N2** 0 · **N3** 0. No inventar probabilidades bayesianas numéricas.
