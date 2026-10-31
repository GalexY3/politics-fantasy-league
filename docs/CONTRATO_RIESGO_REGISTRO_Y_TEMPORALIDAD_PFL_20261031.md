# PFL · Registro, expediente, operación y población de riesgo

**Estado:** contrato ontológico y metodológico en propuesta, NO protocolo AB-H congelado, NO decisión de TFM. Fecha: 31/10/2026. Se distingue normativa y documental de disponibilidad de originales y datos históricos. Las pruebas de QA son sintéticas, salvo el replay metadata-only de una página SIAP ya capturada.

## La entrada puede preceder al expediente admitido

La [Ley vasca 10/2016, de iniciativa legislativa popular, artículo 5](https://www.boe.es/buscar/doc.php?id=BOE-A-2016-6996), distingue actos jurídicos de relevancia directa para el diseño. Su art. 5.1 dispone la asignación por el **Registro General** de un número único a la iniciativa propuesta; el art. 5.2 atribuye a la **Mesa** la decisión posterior de admisión o inadmisión. El art. 5.7 dispone la publicidad de iniciativas propuestas registradas, con cautelas de protección de datos; el 5.8 la publicación de acuerdos de inadmisión en el boletín, y el 5.10 la anotación en registro de retiradas antes de la toma en consideración. La fecha del documento BOE no es la primera disponibilidad de un asiento individual. El texto consolidado del BOE advierte que es informativo y no tiene valor jurídico propio; para cita jurídica prevalece el documento oficial original.

Esta ley regula **una familia concreta de ILP ante una Cámara autonómica**, no todo expediente español. No se dispone de un libro de asientos completo descargable y autorizado para esa familia. Su valor aquí es demostrar conceptualmente que **registro, admisión, expediente, publicación y desenlace son unidades y operaciones distintas**, con oportunidades de selección sucesivas. Un buscador que solo incluye admitidas, debatidas, contestadas o aprobadas no constituye una cohorte de *todas las registradas*. La obligación legal de hacer públicas propuestas tampoco demuestra retrospectivamente que cada asiento tuviera una versión web con primera publicación verificable.

Por tanto, una cohorte de **registradas** debe partir de su propio registro y luego reconciliar los expedientes y decisiones; una cohorte de **admitidas** puede comenzar en la resolución de admisión si ese es el estimando previamente declarado, pero no generalizar a inadmisiones anteriores. Una cohorte extraída de BOCG/BOE condiciona la selección a publicaciones y no estima por sí misma oportunidades que fracasaron antes de la publicación.

## Ontología de unidades, fuentes y tiempo

Se distinguen **asiento de entrada**, **expediente**, **actuación/trámite**, **decisión**, **documento**, **organización**, **rol institucional** y **persona**, sin equivalencias automáticas. Un asiento puede no generar un expediente admitido; varias entradas podrían vincularse a un mismo expediente y una decisión/documento puede relacionarse con varias actuaciones. Los enlaces necesitan claves de origen y referencias oficiales; nunca se fabrica identidad entre instituciones por semejanza textual, tema, nombre personal o coincidencia temporal.

El namespace mínimo es institución × legislatura × familia × identificador fuente-local, y potencialmente el registro general de entrada en otra clave. Las relaciones entre registro, Mesa, expediente, Senado, BOCG y BOE requieren un **hecho documental de enlace** con su fuente, hora/fecha conocida y derechos. Un texto de boletín no se convierte en denominador del Congreso; una referencia a empresa o medio no es interacción causal probada.

| Dimensión | Hecho distinguible | Ante falta de evidencia |
| --- | --- | --- |
| Identidad | ID de registro y expediente por autoridad y familia, versión | Relación UNKNOWN, sin match nominal |
| Hecho jurídico | tipo, emisor, ocurrencia y eventual vigencia | EVENT_UNVERIFIED |
| Publicación | documento, serie, emisor, fecha editorial y hash | DOCUMENT_NOT_OBSERVED |
| Primera disponibilidad | first_public_at acreditado y, si procede, intervalo de cotas | UNKNOWN; captura no es primera publicación |
| Observación | original, URI, licencia, SHA, HTTP Date y reloj de captura | NOT_CAPTURED |
| Resultado | clase terminal, fundamento y fecha, con posibles recursos/correcciones | UNKNOWN_TERMINAL, no fracaso |
| Censura | cierre de seguimiento, cambio de legislatura/régimen y pérdida observacional | CENSOR_UNDETERMINED |
| Contexto exterior | serie electoral, economía, medios, derecho o empresa, con vintage | Bloquear variables posteriores al corte |

Para una predicción en tiempo \(t\), todo atributo debe ser acreditadamente accesible en o antes de \(t\). Su fecha de acontecimiento anterior no basta. Una actuación de 2023 incorporada retroactivamente a una base en 2026 no podía utilizarse como predictor de 2023 sin otro testigo. Una captura actual es un límite conservador de observación **en el sistema local**, no el primer instante en que se hizo público el hecho. Si una entrada estuvo ausente de una captura de un índice completo y apareció en otra, eso acota cuándo se observó por primera vez **en dicho índice**, no su registro o publicidad general.

## Instrumentos implementados en ronda 6

Se añade [contrato de índices paginados](../src/politics_fantasy/procedural_index_contract.py), que analiza capturas originales por página y rechaza cambios de scope/filtros, saltos en paginación, inconsistencias de total, mezcla de autoridad/host, duplicados contradictorios, fecha imposible, replays de bytes, captura temporal demasiado extendida y pretensiones de outcomes o disponibilidad histórica sin testigo. Aun si **todas las páginas concuerdan con el contador editorial**, el resultado mantiene **denominador científico desconocido** hasta demostrar cobertura independiente de todas las entradas. Dos series completas pueden compararse en modo prospectivo solo como diferencias de presencia en el índice, sin deducir actos o fracasos.

La [segunda auditoría SIAP offline](../scripts/verify_siap_page1_offline.py) coteja original HTML, recibos, freeze previo a la captura y metadata por SHA, y extrae con otro parser exclusivamente 20 IDs privados de la página 1 de 44 anunciadas. Emite únicamente conteos, huellas y 43 páginas no comprobadas. Es **QA independiente posterior al GET**, no un preregistro científico ni un análisis de estados de tramitación. El original permanece en scratch, no se distribuye en Git.

La consulta del [observatorio de preparación longitudinal](../src/politics_fantasy/procedural_population_readiness.py), accesible por /api/procedural-population-readiness?as_of=, cruza de forma **no aditiva** tres familias: CSV Canarias (1.754 metadatos, cuyas dos fotografías locales permanecen separadas), SIAP Catalunya (20 links de una página) y descubrimiento de índices Congreso aún sin original admitido. Sus nueve puertas de admisión permanecen NOT_ATTESTED: derechos por activo y bytes originales, identificadores, paginación/selección, denominador de registro independiente, acto de entrada, transiciones, estados terminales/pendientes, vintages y censura. Las consultas históricas anteriores a una captura no revelan recuentos posteriores.

## Programa comparativo y decisiones

**M1 · Reproducción, persistencia y autorregulación:** unidad expediente × intervalo y causas competitivas predefinidas cuando exista riesgo elegible. Baseline fuerte de edad-proceso, calendario, régimen/legislatura, procedimiento y órgano; rival con historia institucional disponible as-of, placebo de historia permutada y validación temporal externa. Evaluar log-loss, Brier y calibración con censura, no declarar causalidad por mera mejora predictiva. Falsador: mejora nula/instable fuera de tiempo o desaparición tras depurar fugas retrospectivas.

**M2 · Acoplamiento con entorno:** Easton (inputs/outputs y respuesta), Deutsch (información y realimentación) y Luhmann (comunicaciones/decisiones y reproducción) no son equivalentes. Las señales económicas, jurídicas, electorales, mediáticas o empresariales requieren fuentes, revisiones y retardos anteriores a la decisión. Baseline de tendencias/reglas/calendario, shocks negativos y controles de futuro; no interpretar correlación como feedback sin identificar mecanismo, dirección y temporización.

**M3 · Selección documental:** cotejar libro de entrada, expediente, boletines y BOE para observar quién desaparece *antes* de cada fase. Ausencia de documento no equivale a fracaso; un caso pendiente no es terminal; una cohorte solo de aprobadas produciría sesgo de supervivencia, y requerir un tránsito futuro puede crear *immortal-time bias*. Solo con universo, causas y fechas acreditadas procederían riesgos competitivos e incidencia acumulada con censura.

Las fronteras **funcional**, **jurídico-institucional** y **empírico-documental** se conservan diferenciadas. Un rastro documental puede evidenciar un acto y no demostrar por sí solo una operación funcional en teoría de sistemas. El TFM, el estimando/corpus definitivos y la selección de los tres mecanismos siguen abiertos, y la aplicación fantasy permanece ficticia.

## Gates y propuestas O1/O7 (sin aprobación)

G0: originales/derechos por activo; G1: población de *todas las entradas del tipo seleccionado* o coherente cohorte de admitidas explicitada; G2: paginación e identidad verificables; G3: actos/transiciones y motivos de censura; G4: disponibilidad bitemporal histórica; G5: contratos A–J, código y SHA congelados **remotamente antes de outcomes**; G6: contraste discriminante con rivales, controles negativos y holdout temporal. No hay fuente que pase el conjunto actual.

**O1-RFC-04:** introducir definición configurable de unidad de entrada (registro previo, presentación, admisión) y test obligatorio de selección de la familia cuando se reclamen todos los intentos; mantener legales estudios que intencionadamente comiencen en admitidas si su inferencia queda limitada a esa población.

**O7-RFC-07:** exigir evidencia de cobertura bajo fuente × familia × entrada × vintage; hacer replay automático de SHA de recibos privados y tests de drift de filtros, futuro y ausencia. La medida es propuesta para evaluación de costes y beneficios frente a O1–O7 vigentes; no se da por adoptada ni se afirma su eficacia científica sin comparar.

**Estado real:** SYSTEM20 20 autorizados, 0 ciclos científicos válidos/invalidos/de planificación, 20 disponibles. Las verificaciones del índice, mocks, tests y documentos son ingeniería y diseño, no resultados AB-R/AB-P.
