# R18 · Continuidad científica tras STOP, día civil jurídico e identificación de riesgos competitivos

**Estado:** hallazgos documentales y pruebas adversariales sintéticas; **no** contraste sobre políticos, expedientes personales ni resultados institucionales. **Fecha de trabajo:** 31-10-2026. **Base:** commit publicado R17 `ce58299e059153e3e47f62189acd0ef11b1e2a57`. La metodología adoptada continúa siendo AB 3.2.1 O1–O7, fijada por `METHOD_REFERENCE.json`; las propuestas RFC anteriores no son nuevas reglas adoptadas. **R5: STOP.**

## 1. Qué significa continuar tras un STOP

La decisión de detener una línea de adquisición o experimentación no implica que haya que inmovilizar la investigación. En particular, una ruta de datos con derechos, denominador, identidad o vintages insuficientes puede quedar `BLOCKED_R5` y pasar a la siguiente hipótesis o fuente *sin que ello autorice a tratar esa ruta como un ciclo AB válido*. El STOP local se audita con una razón, el tipo de evidencia ausente, un falsador y una condición de reapertura. Quedan abiertos desarrollo de producto no empírico, depuración científica, modelos de identificabilidad con ejemplos sintéticos y revisión documental limitada a activos reutilizables y metadatos de acceso permitido.

Se implementa una **cola de veinte oportunidades de investigación diversas**, no veinte resultados ya obtenidos, en [`R18_CONTINUATION_QUEUE.json`](../research/PFL_SYSTEM20_20261031/R18_CONTINUATION_QUEUE.json), validada por [`research_continuation.py`](../src/politics_fantasy/research_continuation.py). Cada propuesta tiene ID estable, pregunta, pista nueva o requisito de evidencia, rival/falsador, motivo de STOP cuando corresponde y condición explícita de reapertura. Un programa de 20 entradas no altera `AUTHORIZATION.json`: las **20 plazas AB-H siguen disponibles y se ejecutarán solo con los prerregistros A–J, SHA remoto antes de los outcomes y las puertas R5 exigidas**. El módulo confronta el saldo con la fuente canónica y rechaza alteraciones o claves duplicadas.

## 2. Congreso de los Diputados: ILP nacional, tipo 120, como ruta nueva

La familia **120 de iniciativa legislativa popular nacional** es distinta de los proyectos de ley 121, proposiciones 122, registros de peticiones del Senado 870/871 y de las ILP de asambleas autonómicas examinadas previamente.

Fuentes oficiales **documentales/HTML o metadatos indexados**, sin capturar casos ni desenlaces:

- [Índice de iniciativas del Congreso, XV legislatura, filtro tipo 120](https://www.congreso.es/es/busqueda-de-iniciativas?_iniciativas_legislatura=15&_iniciativas_mode=verListadoIndice&_iniciativas_tipo=120&p_p_cacheability=cacheLevelPage&p_p_id=iniciativas&p_p_lifecycle=2&p_p_mode=view&p_p_resource_id=filtrarListado&p_p_state=normal): metadatos indexados anuncian editorialmente `iniciativas_encontradas=48` y campos `fecha_presentado`, `fecha_calificado`, `id_iniciativa`, `resultado_tram`. **Ni se descargó la lista original ni se aceptó el 48 como población real, ni se consultaron desenlaces.** Se expusieron incidentalmente encabezados de resultados en fragmentos del buscador y se registró posible contaminación de un futuro holdout; no se analizaron valores de casos.
- [Ley Orgánica 3/1984](https://www.boe.es/buscar/act.php?id=BOE-A-1984-7249): art. 4, presentación y trámite parlamentario; art. 5, calificación y decisión de admisión/inadmisión, con subsanación; art. 7, intervención de JEC **solo después** de la admisión; art. 14, tratamiento al disolverse la Cámara sin caducidad automática de la iniciativa, con necesidad de aclarar los identificadores y los cambios entre legislaturas. Estos extremos son reglas jurídicas, no registros observados de todos los casos.
- [Aviso legal general Congreso](https://www.congreso.es/eu/cem/aviso-legal): información genérica de reutilización que **no sustituye** la verificación jurídica de derechos y condiciones de cada activo/distribución.

**Fallo de identificación principal:** una lista de iniciativas publicadas por el Congreso no acredita que todas las presentaciones ante la Secretaría General estén incluidas; un recuento de la Junta Electoral Central tampoco puede servir de denominador externo *preadmisión*, porque esa autoridad recibe una selección posterior a la decisión de Mesa. Además, la regla de continuidad translegislaturas obliga a distinguir identidad del episodio, iniciativa subyacente, nuevo número de procedimiento y estado al corte. Incluso 48 filas y el mismo recuento en dos páginas del mismo backend no demuestran población exhaustiva.

**STOP local ILP 120:** no abrir outcomes ni contabilizar AB. **Reapertura:** testigo externo de todas las presentaciones, incluidas inadmisiones/subsanaciones/no calificadas/pendientes, identificadores oficiales `asiento→Mesa→JEC` y continuidad de legislatura, permisos por distribución y originales históricos con fecha de disponibilidad acreditada. Si solo se certificara un universo admitido-first, el estimando debe restringirse explícitamente a las admitidas, sin inferir presentación pre-Mesa.

Un segundo candidato de peticiones ciudadanas del Congreso produjo únicamente evidencias ya documentadas para Senado 870/871: se **aparcó**, sin afirmar que no exista un registro que aún no se haya encontrado. Esto satisface la instrucción de registrar un STOP y continuar por un mecanismo diferente.

## 3. F01, fallo material reproducido en la interfaz: `as_of` con zona horaria

El servidor admite `as_of=2026-11-01T01:05:00+01:00`, conservando el instante histórico en la respuesta. Antes de R18, `web/app.js` exigía una cadena que terminara literalmente en `Z`. Al construir un enlace secundario a `/api/registration-readiness`, omitía `as_of` si llevaba un desplazamiento válido como `+01:00`; el destino pasaba a modo `CURRENT`. Se reprodujo con la expresión real del código congelado y una prueba de expectativa **que fallaba antes del parche**. No se ha demostrado una divulgación de datos originales reales: la vista habitual carga CURRENT, y la API todavía exige controles de alcance y oculta las fuentes futuras.

La corrección conserva marcas temporales ISO con `Z` u offset y, si se proporciona un corte malformado, **no produce un enlace CURRENT alternativo**: muestra texto sin enlace. Se mantiene una vía CURRENT solo si el cliente solicita CURRENT explícitamente (`as_of` ausente/null). Las pruebas Node del renderizador real cubren ambos escenarios y otros campos HTML no confiables.

**Falsador de la corrección:** un futuro refactor vuelve a generar `/api/registration-readiness?source_id=...` sin la consulta `as_of` desde una respuesta histórica o permite que una cadena malformada sea interpretada silenciosamente como CURRENT. El certificado de QA es técnico y sintético, no certificación de un archivo histórico.

## 4. F02, error de calendario: fecha civil de competencia ≠ fecha UTC

R13–R17 habían separado `cut_on` (día legal de evento) y `as_of` (instante de conocimiento), pero varios instrumentos sintéticos comparaban `day(cut_on)` y `day(documented_on)` directamente con `utc(as_of).date()`. Ejemplo construido: `2026-11-01T00:15:00+01:00` es 1 de noviembre en la España peninsular y todavía 31 de octubre UTC. El sistema rechazaba erróneamente un acto/documento registrado a esa hora bajo el calendario peninsular. Se reprodujeron cuatro falsos negativos: `CohortCut`, `StageAct`, `PendingWitness` y `EntryEpisode`.

La corrección añade un `legal_calendar_zone` IANA **explícito** al objetivo poblacional cuando se hacen afirmaciones sobre días jurídicos; se permiten `Europe/Madrid`, `Atlantic/Canary` y `UTC` en los ejemplos sintéticos, sin inferirla de un nombre de institución. Etapas y testimonios de pendiente deben concordar con el ámbito de la cohorte. La finalización de `cut_on` exige la **siguiente medianoche de la zona jurídica**, no medianoche UTC ni una duración fija de 24 horas. La zona IANA resuelve los cambios de horario estacional y distingue una misma marca UTC entre Península y Canarias. Sin zona no hay aseveración de fecha civil en estos instrumentos, aunque sí pueden mantenerse cálculos meramente documentales sin interpretación jurídica.

**Limitación crítica:** ninguna fuente política real ha sido adjudicada a una zona por un tercero ni posee permisos/cobertura/vintages gracias a este parche. Son contratos sintéticos con significado civil correcto; quedan por auditar instrumentos no incluidos en el alcance de la reparación, como determinadas proyecciones de grafo sintético y bounds antiguos. Se evita una conversión mecánica a `.date()` del offset aportado por el cliente, que no siempre coincide con la jurisdicción del expediente.

## 5. C13: identificación parcial de riesgos competitivos, aun con N completo

R17 mostró que dos historias ficticias con documentación visible idéntica podían tener distinta tasa interna de recurrencia. R18 refuerza constructivamente el argumento en un punto distinto: **incluso con la misma población completa de registros conocida y con los mismos documentos de resultados seleccionados, los riesgos competitivos por causa pueden diferir**.

En [`synthetic_competing_risks_equivalence.py`](../src/politics_fantasy/synthetic_competing_risks_equivalence.py), dos mundos artificiales mantienen idéntico `episode_id`, fecha de alta y misma proyección de resultados localmente capturados. Solo cambia un desenlace oculto: en uno es una aprobación y en otro un rechazo. Los vectores completos de causas difieren sin que el observador distinga los documentos disponibles. La comparación exige corte de día jurídico finalizado y jamás exporta conteos oraculares ocultos ni identificadores.

Sean dos historias completas ficticias \(H_1,H_2\) y la proyección documental disponible \(O_t\). El instrumento exhibe un caso en que:

\[
N(H_1)=N(H_2),\qquad O_t(H_1)=O_t(H_2),\qquad F_k(H_1)\neq F_k(H_2)
\]

donde \(F_k\) es la incidencia acumulada de al menos una causa. Por tanto, **obtener un denominador independiente es necesario para ciertos estimandos, pero no basta para identificar incidencias por causa cuando los desenlaces siguen sujetos a publicación selectiva**. No se puede asignar a los casos no visibles la categoría rechazo, fracaso, pendiente o censurado sin pruebas positivas. Este razonamiento tampoco prueba que ese patrón ocurra en España; sirve como falsador de modelos que confunden fuente de publicación con proceso completo.

## 6. Gobernanza y saldos tras la investigación

La cola R18 incluye 20 preguntas distinguibles y auditables. En el cierre de esta ronda se completan como **trabajo no cíclico** F01 (interfaz), F02 (calendario) y C13 (contraejemplo por causa). Otras líneas quedan bloqueadas/aparcadas con condiciones de reapertura; las demás continúan como agenda de investigación, no resultados consumados. Un STOP de adquisición no habilita resultados reales ni altera las seis puertas de liberación históricas.

La próxima ruta sustantiva debe proporcionar nueva evidencia independiente sobre población/identidad/cobertura/rights o abordar instrumentos que todavía introduzcan una ambigüedad material verificable. Si se repite el mismo obstáculo sin activo/criterio nuevo, la línea queda aparcada, no se consume una plaza. **SYSTEM20: 0 AB ejecutados, 20 plazas disponibles; R5 STOP.** Atlas99 y todos los originales privados siguen sin cambios. No se decide en esta ronda el TFM, el tutor, la hipótesis dominante, el estimando principal ni un despliegue real.
