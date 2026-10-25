# Informe AB30D — 30 ciclos A–J, no 30 descubrimientos

**Fecha:** 25 de octubre de 2026. **Autorización:** 30 ciclos con branching, contrato A–J completo. 
**Grano:** 30 contrastes computacionales/analíticos sobre poblaciones sintéticas; seis de ellos no admiten una comparación sustantiva válida. Un ciclo ejecutado no implica hallazgo.

## Integridad de la secuencia

- Prerregistro de 30 contratos almacenado en GitHub **antes** de ejecutar el banco: commit `e726e8f9e246b3ce952daa633c4ca39583c800e6` (normalización del salto de línea tras `6c5232c`).
- Código de los generadores y 30 instrumentos congelado en GitHub **antes** de ejecutar: `f46626b41111346e5022498c4343b0c1fddad43f`.
- 80 semillas de prueba exploratoria + 80 semillas disjuntas de contraste de estrés + 80 semillas para ablación por caso; mismos generadores de familia, **no** replicación empírica ni una familia de 7200 observaciones independientes sobre política española.
- El único archivo `RESULTS.json` conserva los números brutos; `RESULTS_AUDITED.json` es una auditoría posterior identificada, no una sustitución silenciosa.
- 153/153 tests Python al cierre, incluida integridad A–J, determinismo y revisión negativa de comparadores. Los fallos iniciales de QA constan en este informe.
- Fuente institucional: https://www.congreso.es/es/opendata/votaciones; esquema tercero: https://congresoabierto.org/datos/; **no se descargó ni certificó** corpus nominal español durante esta campaña por DNS inaccesible en el entorno local.

## A–J materialmente aplicado

**A–C:** 30 estimandos, hipótesis rivales, falsadores y diseños experimentales fijados antes del resultado. **D:** invariantes de códigos, semillas, endpoints y generación. **E:** ejecución 30/30, `RESULTS.json` con 3 regímenes por caso. **F:** controles nulos y auditoría metodológica que reclasifica nueve pruebas definicionales e invalida seis comparadores inadecuados. **G:** contraste con semillas disjuntas bajo generador sintético alterado; *ninguna replicación de campo*. **H:** anotaciones de apoyo/contraejemplo y nuevos priors con fuente de evidencia. **I:** límite de identificación y puntuación por separado. **J:** dictamen, decisión y necesidad concreta de evidencia. Este ledger no afirma 30 descubrimientos independientes.

## Auditoría adversarial

| Clasificación final | Número | Lectura correcta |
|---|---:|---|
| Contrastes condicionados al generador | 12 | Sensibilidad de instrumentación, sin transportabilidad |
| Identidades o comprobaciones definicionales | 9 | Verificación semántica; no hipótesis sociológicas nuevas |
| Comparaciones/controles inválidos | 6 | No interpretar ventajas numéricas como evidencia |
| Control negativo sin mejora | 1 | La propuesta no supera en ese diseño |
| Fallo de identificación (MNAR) | 1 | Ponderar por grupo no corrige falta de datos por outcome |
| Reversión en estrés | 1 | Shrinkage gana en generador cercano y pierde cuando cambia el estrato raro |

## Tres resultados que informan el diseño

1. **M03** — Bajo falta de datos dependiente del voto, ponderar por representación de grupo puede empeorar la estimación (ventaja de candidato en holdout = -0.102). Eso no identifica qué ocurre en el Congreso; demuestra que las fuentes nominales con cobertura desigual requieren un mecanismo de selección explícito.
2. **C09** — La regularización del estrato raro cambió de signo: 0.024 en diseño principal a -0.029 en holdout sintético. Es un contraejemplo contra automatizar un criterio de estabilidad bajo cambios de grupo.
3. **T13 y T17** — La predicción mejora numéricamente si se permite información futura, pero eso invalida el comparador por *leakage*. No es una ventaja científica ni desplegable.

## Detalle completo por ciclo

**Ventaja de pérdida** = error del comparador − error del candidato. Un signo positivo no indica validez ni novedad. **Entre casos las unidades son diferentes**; no se promedian. Los números siguientes son sobre datos sintéticos.

| ID | Rama / pregunta | Ventaja base | Ventaja estrés | Ablación | Estado tras auditoría |
|---|---|---:|---:|---:|---|
| M01 | MCAR y precisión | +0.0001 | +0.0000 | +0.0000 | NEGATIVE_CONTROL |
| M02 | MAR por grupo | +0.1864 | +0.1459 | +0.0030 | CONDITIONAL_SYNTHETIC |
| M03 | MNAR no identificable | -0.1003 | -0.1017 | +0.0046 | IDENTIFICATION_FAILURE |
| M04 | Abstención distinta de no-voto | +0.1069 | +0.1054 | +0.0000 | DEFINITIONAL_ONLY |
| M05 | Censo elegible y cotas | +0.5750 | +0.7375 | +0.0000 | INVALID_COMPARISON |
| M06 | Revisiones y doble recuento | +0.0354 | +0.0216 | +0.0000 | DEFINITIONAL_ONLY |
| C07 | Estandarización y Simpson | +0.1959 | +0.1367 | +0.0134 | DEFINITIONAL_ONLY |
| C08 | Sin cambio de agenda | +0.0153 | +0.0121 | +0.0146 | DEFINITIONAL_ONLY |
| C09 | Estrato raro | +0.0236 | -0.0294 | +0.0236 | STRESS_REVERSAL |
| C10 | Cambio temporal de agenda | +0.0441 | +0.0690 | -0.0007 | CONDITIONAL_SYNTHETIC |
| C11 | Cambio de grupo | +0.1005 | +0.2077 | +0.0000 | DEFINITIONAL_ONLY |
| C12 | Mayoría y empate | +0.5875 | +0.6000 | +0.0000 | DEFINITIONAL_ONLY |
| T13 | Filtración temporal | +0.6425 | +0.6439 | +0.0000 | INVALID_COMPARISON |
| T14 | Sesión como clúster | +0.0400 | +0.0711 | +0.0247 | CONDITIONAL_SYNTHETIC |
| T15 | Error estándar por sesión | +0.3750 | +0.3750 | +0.0125 | CONDITIONAL_SYNTHETIC |
| T16 | Snapshot retrospectivo | +0.0245 | +0.0262 | +0.0000 | DEFINITIONAL_ONLY |
| T17 | Variables de tema futuras | +0.1619 | +0.2672 | +0.0000 | INVALID_COMPARISON |
| T18 | Bootstrap serial | +0.3000 | +0.6125 | +0.0000 | CONDITIONAL_SYNTHETIC |
| R19 | Acuerdo esperado | +0.6873 | +0.7713 | +0.4823 | INVALID_COMPARISON |
| R20 | Confusión por grupo | +0.3960 | +0.5754 | +0.0000 | CONDITIONAL_SYNTHETIC |
| R21 | Shock compartido | +0.5995 | +0.7842 | -0.0025 | CONDITIONAL_SYNTHETIC |
| R22 | Tamaño de grupo | +27.8682 | +28.3483 | +4.2130 | INVALID_COMPARISON |
| R23 | Aristas ausentes MAR | +0.1228 | +0.1320 | -0.0000 | CONDITIONAL_SYNTHETIC |
| R24 | Doble conteo de díadas | +109.5375 | +260.5875 | +0.0000 | DEFINITIONAL_ONLY |
| F25 | Exposición desigual | +0.9500 | +0.9750 | +0.0000 | CONDITIONAL_SYNTHETIC |
| F26 | Popularidad y cobertura | +0.0968 | +0.0721 | +0.0027 | CONDITIONAL_SYNTHETIC |
| F27 | Proxy Goodhart | +1.4627 | +2.1831 | +0.0000 | CONDITIONAL_SYNTHETIC |
| F28 | Rankings con pocos eventos | +0.0052 | +0.0393 | +0.0018 | CONDITIONAL_SYNTHETIC |
| F29 | Métrica propia para eventos raros | +0.0176 | +0.0661 | +0.0146 | INVALID_BASELINE |
| F30 | Congelación de puntuaciones | +0.0307 | +0.0373 | +0.0000 | DEFINITIONAL_ONLY |

## Limitaciones y decisión AB-DECIDE

Las 30 salidas sirven como pruebas de tensión de métodos que eventualmente se aplicarían a una muestra real; **no constituyen observaciones de personas o instituciones**. Algunos resultados son construidos por definición y los comparadores de seis casos no respetan igualdad de estimando, disponibilidad temporal o capacidad estadística; la auditoría los invalida. La normalización de grupos y revisión de resultados requieren censos históricos, valores de no-voto registrados, fecha de primera publicación y contraste con JSON oficial. La selección a partir del mismo generador no establece causalidad ni confirma resultados originales.

**AB-DECIDE final:** `REPAIR_SOURCE_ACCESS` y `CONTINUE_ONLY_WITH_FIELD_DATA`. Mantener VSDS=1/3; CT2 rama predictiva=24/100; N1=N2=N3=0. Ninguna puntuación de fantasía se calcula aquí sobre políticos reales. Las notas y limitaciones de los 30 casos constan en el JSON A–J.

**Saldos previamente preservados:** 12 del bloque B50; 45 bucles libres; 19 del bloque AB20. Este bloque AB30D se ejecuta y se agota como cómputo, con seis casos inválidos registrados y 0 experimentos de campo válidos. No tratar estos 30 como avance automático hacia VSDS 2/3.

## Solicitud para el siguiente bloque

Prioridad: obtener archivos auténticos descargables y verificables; evaluar corpus por temporalidad, censo, faltantes, temas, afiliación y comparadores prequential; mantener production si aportara la fuente nueva. **SOLICITO BRANCHING 30 CICLOS**. Autorización nueva opcional, no consumo de saldos anteriores.
