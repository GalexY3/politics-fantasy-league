# Politics Fantasy League — AB-H USHOUSE5 — cierre del 28/10/2026

**5/5 ciclos completos A–J ejecutados y registrados, 4 AB-R + 1 AB-P, 0 inválidos, 0 planificación, 0 pendientes.** Rama `research/pfl-abh5-us-house-20261028` desde DIVISIONS5 HEAD `88c665d1f8c8587c3b7f263b2d1294eda20f1d59`. **No ChatRelay, no merge main, no CI costosa, no resultados inventados ni valoración de personas/partidos.** Todos los ciclos fueron prerregistrados antes de su operación concreta; se distinguen explícitamente los resultados ya expuestos antes de cada preregistro.

## 1. Indicadores de la línea científica

| Medida | Inicio | Cierre | Por qué |
|---|---:|---:|---|
| Ciclos AB-H, ejecutados | 0/5 | **5/5** | Cinco pares A–J, 4 AB-R + 1 AB-P |
| CT2 ordinal (línea identidad PFL) | 29/100 | **29/100** | No nueva evidencia discriminante de identidad/valor científico prospectivo |
| VSDS | 1/3 | **1/3** | No estudio predictivo cegado |
| Madurez contractual V4 | 36,90 % | **36,90 %** | No revisar/autoasignar hitos |
| Logros acreditados | 2/90 | **2/90** | No nuevos awards |
| Gates release | 0/6 | **0/6** | Sin lanzamiento ni suite integral |
| N1/N2/N3 nuevos | 0/0/0 | **0/0/0** | Asociación descriptiva y control conocido de composición, sin novedad científica |

[Estado y commits](CAMPAIGN_STATUS.json) · [Trayectoria CT2 por ciclo](CT2_TRAJECTORY.json) · [Gráfico CT2 completo y zoom](CT2_FULL_AND_ZOOM.svg). El índice no es probabilidad calibrada ni porcentaje de avance de producto.

## 2. Nueva clase de evidencia: votaciones por grupos del Congreso de EE. UU.

Fuente primaria de publicación: **Office of the Clerk of the U.S. House of Representatives**, 119.º Congreso, sesiones primera (2025) y segunda (2026). Se eligieron **roll calls consecutivos 178–183 de cada año ANTES de abrir la mayoría de sus resultados**. Las fichas oficiales HTML publican tipo de votación, moción, Yea/Nay/Present/Not Voting y totales por partido. El XML original se intentó mediante enlace público y `container.download`, pero el acceso falló: **0 bytes originales XML, 0 hashes de original, first_public_at UNKNOWN**. Los datos guardados son transcripciones agregadas verificadas contra la ficha institucional y aritmética, no dataset original con autenticación binaria. **El roll 180 de 2025 y el roll 180 de 2026 estaban expuestos ANTES de C01/C02**, por consulta de factibilidad; se registran sensibilidades excluyéndolos.

### C01 — 2025, seis decisiones consecutivas (AB-R)

[Preregistro](C01_PREREG.json) · [resultado A–J](C01_RESULT.json) · [seis recuentos oficiales transcritos](C01_2025_OFFICIAL_AGGREGATES.json).

2025, 24–26 junio, rolls 178–183: solo **1/6** tiene mayorías de votos Yea coincidentes en republicanos y demócratas (179, suspensión de reglas para condenar la violencia política, **424 Yea / 0 Nay**). En cinco decisiones las mayorías votan en sentido opuesto, incluyendo 181 **208–216**, 182 **218–206** y 180 **219–206**. El **margen estrecho de recuento total** no es un indicador de consenso entre partidos; puede ocultar polarización. 2025 180 ya expuesto: si se excluye queda 1/5 mayoría coincidente. Fuente: `https://clerk.house.gov/Votes/2025{178..183}`. No medir 'lealtad' de representantes individuales ni asistencia física a partir de Not Voting.

### C02 — 2026, segunda sesión, muestra fijada antes del resultado (AB-R)

[Preregistro](C02_PREREG.json) · [resultado](C02_RESULT.json) · [seis recuentos](C02_2026_OFFICIAL_AGGREGATES.json).

2026, 20 mayo, rolls 178–183: **5/6** comparten la mayoría Yea en ambos grandes partidos; una sola división, 183 sobre moción de recommit, vuelve a oposición **207–208**. Los rolls 178–182 son **cinco mociones de suspensión de reglas** para pasar medidas (405–4, 393–16, 405–5, 401–6, 415–0). En cada una el voto independiente está contabilizado y el total de grupos iguala los resultados generales. Excluyendo el roll 180 preexpuesto: **4/5** mayorías coincidentes frente a 1/5 en 2025. **No** comparar igual número ordinal de roll entre años como el mismo asunto legislativo ni atribuir efecto al año.

### C03 — Comparadores competentes, claramente RETROSPECTIVOS (AB-R)

[Preregistro](C03_PREREG.json) · [resultado](C03_RESULT.json) · [datos de comparación](C03_RETROSPECTIVE_PROCEDURE_BASELINE.json).

Predicción descriptiva de y = «coinciden las mayorías agregadas de ambos grandes partidos» en seis votos ya conocidos de 2026. Dos reglas:
- Control A: clase modal 2025 = **no coinciden**, predicción constante → **1/6 aciertos** en 2026.
- Regla B (procedimental): en 2025 la única suspensión de reglas coincidió, los cinco votos restantes no. Reglas fijas: **suspensión → coinciden; otros → no** → **6/6 aciertos** en 2026.
- Control «siempre coinciden» → **5/6** en 2026. Sensibilidad quitando 180: regla procedimental 5/5, control constante 1/5.

**Límite decisivo:** toda la muestra de evaluación 2026 estaba visible ANTES del prerregistro específico de C03, y B se ajusta a **una sola suspensión de 2025**. 2026 tiene seis votos **de una única jornada**, cinco mociones procedimentalmente afines. **Esto NO es un experimento predictivo prospectivo ni prueba de validación fuera de muestra genuina**, y no debe presentarse como tal, aunque la división temporal sea posterior por calendario.

### C04 — Auditoría adversarial de mezcla de procedimientos (AB-R)

[Preregistro](C04_PREREG.json) · [resultado](C04_RESULT.json) · [tabla y estandarización](C04_STRATIFIED_CASE_MIX.json).

La diferencia ingenua de mayorías coincidentes aumenta de **1/6 en 2025 (16,67 %) a 5/6 en 2026 (83,33 %)**, una **brecha +66,67 puntos porcentuales**. Pero al separar tipos:
- **Suspensión de reglas:** 2025 **1/1** acuerdo; 2026 **5/5** acuerdo.
- **Todos los demás:** 2025 **0/5** acuerdo; 2026 **0/1** acuerdo.

La estandarización directa a composición común 50/50 (o a los pesos procedimentales 2025 y 2026) deja **diferencia ajustada 0 pp**, frente a +66,67 sin ajustar. Es un contraejemplo local de **sesgo de composición** en una comparación histórica no aleatoria. **No demuestra causalidad** ni el efecto nulo general del año: n=12 votos, cuatro fechas distintas (2025 tres días y 2026 un día), estratos con n=1 y selección exploratoria; etiquetas conocidas antes de la prereg C04. Por tanto no generar intervalos de confianza independientes por voto ni presentar una nueva teoría de comportamiento parlamentario.

### C05 — Instrumento reproducible de validación e información disponible antes del voto (AB-P)

[Preregistro](C05_PREREG.json) · [resultado](C05_RESULT.json) · [source](research_only_house_groups.py) · [15 tests](test_research_only_house_groups.py) · [auditoría](C05_LOCAL_TEST_AUDIT.json).

Ejecutado localmente `python -m unittest -v test_research_only_house_groups.py`: **15/15 PASS, 0 FAIL** en Python 3.13.5. Comprobados los blobs idénticos entre fuente local ejecutada y GitHub: módulo `a8ff1dae5b4449a728d7e535bc86ab1947295eec`; tests `04071e17eec565b9e03ade141266c98e327967cc`. Pruebas discriminan 2025 y 2026 con votos de Independiente, sumas partido→total, tipo Boolean, negativos, suplantación URL, años/fechas imposibles, grupo sin mayoría y **rechazo de margen o totales realizados usados como características supuestamente disponibles antes de la votación**. Son controles de *data leakage* y coherencia, NO autenticación de fuente ni previsión de parlamentarios concretos. **Suite integral Python/Node/Atlas en HEAD NO ejecutada.**

## 3. Reglas AB R1–R5, límites y falsadores

**R1**: voto publicado Yea/Nay no significa preferencia o asistencia individual; unidad de análisis = una división y los agregados por partido, no persona. El estimando es proporción de decisiones con mayorías partidarias coincidentes en estas doce decisiones, no propensión de un legislador. **R2**: control modal del año anterior, control siempre-acuerdo y clasificación por trámite, con entradas equivalentes; el control más fuerte disponible en estos datos es la **estratificación del tipo de moción**, no el margen observado después del voto (que filtraría el resultado). **R3**: preselección de números 178–183 antes de la mayoría de consultas, pero los dos roll 180 pre-expuestos; comparadores C03 y auditoría C04 postexpuestos, sin reclamo de 0.05/validación ciega; múltiples observaciones 2026 dentro de una sola sesión con dependencia. **R4**: al controlar estratos procedimentales, la aparente diferencia entre años se anula en esta cohorte; el mecanismo 'año cambia bipartidismo' carece de soporte en estos doce casos. **R5**: fuente nueva de EE. UU. y mecanismo de composición distinto a los británicos y D'Hondt; no repetir descargas XML inaccesibles, dejar original a Codex y detener exploración aritmética repetitiva sin nueva clase de evidencia.

**No se acreditan nuevos N1/N2/N3 ni 2/3.** El mecanismo de composición es conocido en estadística; la utilidad es concreta para el diseño de medidas sociológicas y fuentes, pero no demuestra originalidad científica ni una predicción prospectiva de PFL. CT2 identidad permanece 29.

## 4. Tareas técnicas pendientes

[**T019 — XML oficiales House 12 registros y QA integral**](../../tareas_codex/T019_US_HOUSE_XML_PREDICCION_20261028.md) **PREPARADA, NO EJECUTADA**. Pide 12 XML auténticos, TLS/hashes, esquema, correcciones, clasificación de Independiente, temporales, ejecución de código de HEAD y suite completa. Solo una eventual prueba futura con fecha de corte pre-registrada, resultados desconocidos, muestras nuevas y autorización independiente puede demostrar capacidad predictiva. Permanecen **T011, T016, T017 y T018**, no ejecutadas en esta campaña. Ningún bloqueo fue contabilizado como ciclo propio.

## 5. Gobernanza y solicitud

Se agotó el presupuesto 5/5 con cinco ciclos A–J documentados y reales; el usuario no debe aprobar otra vez este bloque ya concedido. No ChatRelay, no `main` ni CI costosa, no rankings políticos. Para nueva rama, solicitar solo hipótesis realmente discriminantes y corpus original verificable; no más tests sobre doce roll calls para aparentar progreso.

**SOLICITO BRANCHING AB-H DE 5 CICLOS ADICIONALES**, condicionado a **nueva autorización expresa**, preferiblemente después de resolver T019 o con otra fuente independiente accesible para evaluación verdaderamente prospectiva.
