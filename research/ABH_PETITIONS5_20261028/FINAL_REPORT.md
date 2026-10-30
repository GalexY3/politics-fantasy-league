# Politics Fantasy League · PETITIONS5 (28/10/2026) · Informe A–J

**CERRADO: 5/5 ciclos AB-H A–J realmente ejecutados.** Cinco AB-R válidos **de alcance acotado**, cero inválidos, cero planificación y cero pendientes. Rama `research/pfl-abh5-petitions-20261028`, creada desde UK650 / PR #28, base SHA `d4f80ba138ce9bf03f686b51e59849470814710c`. No ChatRelay, no CI costosa, ninguna fusión a `main`, sin scoring de personas o posiciones políticas.

## 1. Nuevo fenómeno/contrato de verdad

**Hipótesis nueva:** la digitalización de la participación política por peticiones genera **dos trayectorias institucionales distintas**: respuesta del Gobierno al superar 10.000 firmas y *consideración* para debate parlamentario al superar 100.000. El observable es la **fecha administrativa documentada** de cada hito (no la actitud individual de cada firmante, la adecuación política de la petición, ni que el Gobierno acepte su contenido). Los umbrales están especificados en [el procedimiento oficial de peticiones](https://petition.parliament.uk/help) y en [la guía parlamentaria](https://guidetoprocedure.parliament.uk/concepts/L0WQsZf6/e-petitions): *considerar* no garantiza celebrar debate.

**Muestra determinista pero NO representativa:** primera docena de peticiones **cerradas, ordenadas por mayor número de firmas**, del [índice oficial de peticiones cerradas](https://petition.parliament.uk/petitions?state=closed), vínculos 17–28 en su versión indexada de aproximadamente agosto de 2026. Identificadores congelados por posición antes de abrir las fichas individuales: `700143, 730194, 727309, 737105, 722903, 705383, 702844, 730605, 705384, 718406, 746363, 700824`. La identidad y la cronología de la primera petición ya estaban expuestas antes del prerregistro: declarar exposición previa. Todas las doce tenían >100.000 firmas por el diseño de selección: **no se puede comparar por debajo/encima de umbrales, calcular probabilidades generales de respuesta/debate ni identificar discontinuidades causales**. Una persona puede firmar múltiples peticiones; las firmas de peticiones distintas **NO son ciudadanos únicos**.

**Fuentes primarias realmente consultadas:** doce URL `https://petition.parliament.uk/petitions/{id}.json` se abrieron como JSON renderizado por el lector web. Se extrajeron solo campos de fechas, firmas y estados y se guardaron en [PETITIONS12_EVENT_PANEL.json](PETITIONS12_EVENT_PANEL.json). **No se obtuvieron bytes binarios originales ni se autenticó un SHA-256 de los JSON oficiales** (`container.download` falló y el contenedor Python no resolvió el dominio). No tratar el fichero de transcripción como JSON original descargado. El lector web mostró cachés de hace aproximadamente dos a cinco meses; **no es un snapshot realtime del 28/10/2026 ni se acredita la fecha de primera publicación `first_public_at`**. [EVENT_METRICS.json](EVENT_METRICS.json) reúne los estadísticos calculados de verdad en JS V8 sobre los doce registros.

## 2. Cinco ciclos A–J, hipótesis rivales y negativos

| Ciclo | Observación discriminante y resultado | Límite principal |
|---|---|---|
| [**C01**](C01_RESULT.json) · [prereg](C01_PREREG.json) | 12 JSON publicados por el **emisor institucional original** y transcritos en un panel de 12 peticiones; todos tienen fechas de apertura, hito 10k, respuesta, hito 100k y debate programado; **12/12 coherencia en orden de hitos**. Las 12 fichas poseen actualizaciones posteriores al cierre. | La publicación como HTML/JSON visto no equivale a captura original autenticada en bytes. La selección por firma final está severamente sesgada y no representa el universo de peticiones. |
| [**C02**](C02_RESULT.json) · [prereg](C02_PREREG.json) | Fecha UTC de hito **10.000** → `government_response_at`: **mediana 16,457 días**, media 27,473, rango **12,814–128,013**, **1/12** espera >30d y 1/12 >60d. Excluyendo primera petición previamente vista, mediana **16,688d**. La H1 prerregistrada (mediana >30d) **no se sostiene**. | El comparador de 30 días es descriptivo, **no un plazo legal**. Un caso muy retrasado desplaza la media; la respuesta pública y marca técnica no siempre coinciden (C04). |
| [**C03**](C03_RESULT.json) · [prereg](C03_PREREG.json) | Fecha UTC hito **100.000** → fecha de debate programada: **12/12** con programación y `debate_outcome_at`, mediana **86,5775d**, media **130,11275d**, rango **43,112–319,084d**; **6/12** >90d. No se encontró el supuesto C03 H1 de petición top12 sin fecha de debate. | Programación/metadatos no sustituyen la comprobación independiente de debate celebrado. Para 7/12 no se ha abierto transcript; los cinco restantes se contrastan en C05. La norma de 100k **solo asegura consideración**, no debate seguro para otras peticiones. |
| [**C04**](C04_RESULT.json) · [prereg](C04_PREREG.json) | Apertura→10k y 10k→respuesta: Spearman **+0,1958**, Pearson **−0,1669**, Spearman excluyendo primera observación **+0,1455**. **No** se observa asociación monotónica negativa anunciada. Cuatro peticiones difieren entre el día de `government_response_at` y `government_response.responded_on`; en id **730605** técnica **30/07/2025** vs publicada **05/12/2025**, desfase ≈128d. Con fecha pública, mediana de tiempo al responder **18,774d**, **2/12** >30d (frente a 16,457d y 1/12 usando sello técnico). | **No decidir automáticamente cuál fecha es “correcta”**: podría tratarse de actualización/revisión o de una semántica distinta, no verificada. Los otros tres desajustes son de un día; todas 12 `updated_at` posteriores al cierre. Ningún campo puede sustituir por sí solo `first_public_at`. [Auditoría](TEMPORAL_SENSITIVITY.json). |
| [**C05**](C05_RESULT.json) · [prereg](C05_PREREG.json) | Se seleccionaron mecánicamente las **cinco primeras** peticiones con debate completado entre las doce y se abrió su transcripción **original Hansard** en otra sección institucional, por su enlace oficial. **5/5** transcripciones verificadas como páginas reales con fecha correspondiente a la ficha: **06/01/2025, 08/12/2025, 12/01/2026, 13/07/2026, 15/12/2025**. [Enlaces y manifest](C05_HANSARD_CROSSCHECK.json). | Hansard y peticiones son servicios diferentes **bajo el mismo Parlamento**: corroboración documental, no réplica de emisor independiente en sentido científico. Debate celebrado **no equivale a petición aceptada**, ley aprobada ni impacto político atribuido a firmas. |

## 3. Dictamen adversarial AB 3.2.1, R1–R5

**R1 — Estimando:** peticiones completas y fechas oficiales observadas, no individuos, “apoyo político” general ni decisiones legislativas de fondo. Distinguir `response_threshold_reached_at`, `government_response_at`, `government_response.responded_on`, `debate_threshold_reached_at`, `scheduled_debate_date`, `debate_outcome_at`, `updated_at` y captura UTC; etiquetas temporalmente no intercambiables.

**R2 — Comparadores competentes:** baseline institucional correcto **10k→respuesta; 100k→consideración**, no “100k garantiza debate”. Tiempos de respuesta comparados con umbral descriptivo preespecificado 30 días (sin inventar obligación), y sensibilidad a fuente técnica vs fecha pública. C05 transcripción Hansard frente a solo dato “outcome” de la ficha original.

**R3 — Selección, exposición y confirmación:** primeras doce **seleccionadas a posteriori por total final de firmas**, y primera petición ya vista durante factibilidad. Comparaciones exploratorias con n12, sin pruebas de significación confirmatorias, sin atribución causal ni tasa generalizable; C05 primera muestra documental de cinco seleccionada por posición, no por acierto documental. Datos del lector web con caché; nada de “hoy” o first-public sin fuente.

**R4 — Falsadores y negativa:** hipótesis de mediana de respuesta >30d **rechazada**; supuesto de una de las doce sin debate programado **rechazado**; correlación esperada negativa entre velocidad de firmas y respuesta **no observada**; desajuste temporal para un registro 128d y un caso de respuesta demorada ≈128d (no confundir ambos). El origen y semántica de la anomalía **no están determinados**.

**R5 — Detención / dependencia:** no rellenar cuota con otros estudios del mismo top12. Para un estimando de efecto del umbral se necesita una cohorte no seleccionada por firmas finales, peticiones bajo y sobre 10k/100k, censura/truncamiento y trazabilidad de versiones, con captura original. [**T022 pendiente de Codex/PC**](../../tareas_codex/T022_PETICIONES_JSON_COHORTE_20261028.md) precisa datos, hashes, controles y comparación de supervivencia sin confundir firmas con personas. Esta tarea **no se ha ejecutado** y **no cuenta** ciclo.

El dataset transcrito y el cálculo cuantitativo **sí** fueron operados con JavaScript V8 de forma real, y se registraron fuentes de cada observación; [`replay_petitions.py`](replay_petitions.py) es un script reproductor independiente **preparado, NO ejecutado aún en un checkout limpio**; tampoco se ejecutó suite integral Python/Node/Atlas sobre este HEAD. Nunca reclamar resultados de esas tareas no ejecutadas.

## 4. Indicadores de proyecto (antes → después)

| Indicador | Inicio | Cierre |
|---|---:|---:|
| AB-H concedidos / ejecutados | 5 / 0 | **5 / 5** |
| AB-R / AB-P | — | **5 / 0** |
| Inválidos / planificación / pendientes | — | **0 / 0 / 0** |
| CT2 identidad ordinal | 29/100 | **29/100** |
| V4 contractual | 36,90 % | **36,90 %** |
| VSDS | 1/3 | **1/3** |
| Logros acreditados | 2/90 | **2/90** |
| Gates de lanzamiento | 0/6 | **0/6** |
| Nuevos N1/N2/N3 | 0/0/0 | **0/0/0** |

[Ledger A–J y commits](CAMPAIGN_STATUS.json) · [Trayectoria CT2](CT2_TRAJECTORY.json) · [Gráfico CT2 completo y ampliado](CT2_FULL_AND_ZOOM.svg).

**Sin nuevo mérito científico de identidad 2/3**: esta campaña da observaciones y controles de medición de participación digital estatal, pero no estima impacto causal de umbrales, no demuestra ninguna mejora científico-predictiva de PFL, no tiene un muestreo representativo ni obtiene archivos crudos autenticados. No subir CT2 por contar ciclos.

## 5. Pendientes y siguiente solicitud

Pendientes de ejecutor **T011 y T016–T021**, preservadas sin declarar ejecución; nueva **T022**: original JSON y selección representativa/independiente; ninguna se ejecutó en este bloque. No inventar SHA256 de fuente, fechas o medidas.

**SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, solo tras autorización expresa, para una muestra abierta de peticiones con ambos lados de los umbrales y temporización observacional válida, o una nueva fuente primaria independiente con estimando preevento, siempre condicionado a R5. No avanzar de fondo sin nueva autorización.

