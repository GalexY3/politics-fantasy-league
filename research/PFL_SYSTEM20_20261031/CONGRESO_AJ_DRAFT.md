# PFL — estudio español sobre persistencia institucional y retroalimentación

**Estado:** BORRADOR METODOLÓGICO / NO PRERREGISTRADO / NO EJECUTADO (31-10-2026).

**Ámbito de este archivo:** nota de diseño autónoma y provisional, alojada exclusivamente en PFL-scratch-method. No se ha construido ni consultado un conjunto de resultados, no se ha entrado en expedientes particulares, no se ha ejecutado una campaña AB-H ni se han modificado los repositorios de PFL. La concesión general de hasta 20 ciclos no se considera consumida por este diseño. Cualquier futura apertura de ciclo exige identificador no solapado, ledger, contrato A–J y código/hash congelados ANTES de observar outcomes. Ninguna hipótesis ni métrica de este documento es un resultado sociológico.

**Registro preventivo de exposición:** durante la localización de páginas oficiales de documentación, el buscador web presentó incidentalmente extractos de expedientes concretos con estados de tramitación. No se abrieron esas fichas, no se descargaron datos ni se utilizaron esos extractos para formular o decidir hipótesis, población, estimandos o parámetros. Sin embargo, **no se puede afirmar cegamiento absoluto frente a todos los outcomes publicados en buscadores**. En cualquier fase confirmatoria posterior, deberán declararse y excluirse de una muestra verdaderamente retenida los registros previamente expuestos que puedan identificarse, o documentar explícitamente el riesgo residual de contaminación; no se ha realizado aquí dicha adjudicación.

## Tesis de diseño y distinción entre los dos universos

**Objeto científico general:** reconstruir cómo persisten, terminan y eventualmente reaparecen procesos institucionales iniciados en el Congreso de los Diputados; estudiar si el historial observable y cronológicamente anterior de una materia/actor aporta información para predecir el siguiente tránsito institucional. La hipótesis de retroalimentación es **predictiva o asociativa**, no una atribución causal de que un resultado legislativo altere después los incentivos de los actores.

**Denominador o población en riesgo:** las iniciativas de una **clase procesal previamente fijada** que han alcanzado el acto de entrada observable que definamos en los expedientes del Congreso (registro, presentación o calificación: escoger exactamente uno, justificarlo y conservar su fecha). Deben incluirse las iniciativas que prosperan, las que fracasan, las pendientes y las censuradas; una muestra formada solo por disposiciones aprobadas sería selección por resultado.

**Resultado publicado en BOE:** la existencia y fecha de publicación de una disposición concreta en el diario oficial puede constituir un **evento de salida** para una parte de las iniciativas. La API de sumarios de BOE documenta publicaciones por fecha y ofrece enlaces a documentos, pero **NO define la población de iniciativas que pudieron haber dado lugar a una ley**. Tampoco toda disposición del BOE procede de un expediente legislativo concreto del Congreso, ni toda actividad parlamentaria termina en el BOE. La legislación consolidada es otra colección, selectiva y revisable; sus versiones actuales no reconstruyen automáticamente qué sabía un investigador en cada fecha histórica.

**Fuente del proceso:** el buscador del Congreso distingue legislatura, tipo de iniciativa, expediente, fechas y resultado de tramitación. Sus fichas enlazan fases y publicaciones. La existencia de este buscador **no verifica todavía** que tengamos enumeración completa, descarga masiva estable, claves canónicas, historial de revisiones, primer momento de publicación o permiso de uso para nuestro corpus. El estado del proyecto sigue siendo POBLACIÓN ELEGIBLE CONGRESO **SIN ACREDITAR**. Hasta superar el gate correspondiente, el resultado admisible de esta línea es una auditoría de factibilidad, no un modelo de persistencia.

**BOCG distinto de BOE:** el Boletín Oficial de las Cortes Generales es una fuente de eventos/publicaciones parlamentarias y de control gubernamental. La publicación de una iniciativa en BOCG no es la promulgación de una ley en BOE ni equivale por sí sola a su éxito.

## Tres rutas materialmente distintas, con falsadores

| Ruta y mecanismo | Población elegible y origen | Endpoint/resultado posible | Falsador que obliga a detener o redefinir | Dictamen antes de datos |
| --- | --- | --- | --- | --- |
| **R1. Supervivencia multietapa de iniciativas legislativas** (primaria condicional) | Expedientes de proyectos y/o proposiciones de ley en Congreso, por legislatura y tipo; preferiblemente una sola familia procedimental al principio. Inicio por un acto fechado y común. | Tiempo hasta siguiente hito, finalización, rechazo, caducidad, retiro o publicación de ley identificada en BOE. El BOE confirma únicamente el evento emparejado, nunca rellena el riesgo. | El Congreso no permite enumerar expedientes de entrada con denominador auditado; fechas o estados no se pueden versionar; enlaces expediente↔ley no se verifican; mezcla de tipos produce eventos no comparables. | **Primera candidata**, pero BLOQUEADA hasta acreditar marco y campos. |
| **R2. Reintroducción y continuidad entre legislaturas** (persistencia temática, no del mismo expediente) | Expedientes del Congreso de dos o más legislaturas completas y una ontología estable de materias; exige observar tanto propuestas no reintroducidas como las reintroducidas. | Tiempo hasta nueva iniciativa temática/identificada después de cierre o disolución; secuencia de intentos previos con cambios de promotor/contexto. | Solo se encuentran ejemplos famosos reintroducidos; no hay corpus de todas las propuestas iniciales; el matching temático requiere leer el resultado futuro, es inestable o confunde temas genéricos; censura histórica incontrolable. | Ruta distinta y más arriesgada. **No activar como segundo outcome de R1** sin marco temporal propio y validación ciega del enlace. |
| **R3. Control parlamentario y respuestas institucionales** (feedback de respuesta, sin usar BOE como éxito) | Todas las preguntas escritas de una o varias legislaturas del Congreso, por clase de expediente y fecha de entrada; BOCG y ficha de iniciativa como trazas. | Tiempo hasta contestación documental y secuencias de preguntas posteriores sobre asunto común. Respuesta, expiración y ausencia de observación son estados distintos. | No hay universo de preguntas iniciales y pendientes; no se distingue pregunta/contestación; imposibilidad de congelar condiciones de publicación; reapariciones no enlazables sin inferencia arbitraria. | Ruta alternativa de mecanismo distinto. **No medir su respuesta mediante BOE**. |

La selección de R1 no queda adoptada por esta tabla. Exige una revisión previa de datos, fuentes y literatura por rutas; si R1 carece de denominador, dejarla PARKED con condición de reapertura y comparar R2/R3 sin asumir su viabilidad. No permitir que BOE determine retrospectivamente qué expediente buscar. En R1, distinguir **proyectos del Gobierno** de **proposiciones de ley**: sus reglas de toma en consideración difieren; pueden requerir cohortes, transiciones y modelos separados. La tramitación incorpora Senado y otras fases que deben registrarse sin atribuir todo el tiempo al Congreso.

## A–J: contrato de estudio principal R1 (todavía no congelado)

### A. Pregunta, unidades y estimandos

**Pregunta estructural:** entre iniciativas legislativas admisibles de una familia procedimental y periodo definidos por adelantado, ¿cómo se distribuyen los tiempos de permanencia, los avances, los desenlaces competitivos y la terminación administrativa? ¿Aporta el historial institucional **disponible antes del corte** información predictiva adicional sobre la probabilidad del siguiente hito?

**Unidad primaria:** expediente legislativo × intervalo de riesgo, identificado por legislatura, código de expediente y tipo de iniciativa, manteniendo originales y eventuales derivaciones. Para predicción temporal utilizar unidades expediente-semana o expediente-mes (elección final condicionada a precisión real de fechas, sin ver outcomes). **No** equiparar expediente, texto, asunto, ley y evento: pueden existir relaciones muchos-a-muchos.

**Estimando descriptivo primario propuesto:** incidencia acumulada por causa a horizonte predeclarado h de la primera transición desde un estado parlamentario inicial; muerte/cierre/retirada/caducidad son riesgos competitivos según ontología validada. Si no se acredita la taxonomía, limitarse a descripción de transiciones observadas, sin estimación de riesgo.

**Estimando predictivo secundario condicionado:** diferencia de pérdida fuera de muestra temporal entre un baseline fuerte de duración/transición y el mismo conjunto de información ampliado con historial previo de iniciativas comparables y calendario institucional. Métricas candidatas: log-loss o Brier temporal de probabilidades de transición, calibración, y discriminación con control de censura; no fijar horizonte h sin conocer resolución y seguimiento **metadatos de cobertura**, sin inspeccionar tasas de éxito.

**Retroalimentación operacional, provisional:** historia fechada previa de la misma materia/institución/promotor (número de iniciativas presentadas, etapas alcanzadas antes del corte, intervalos observados y acumulación documentada). La mejora de predicción mediante historia es compatible con persistencia del contexto, selección, habilidad organizativa, agenda o dependencia real: no identifica un mecanismo causal.

### B. Teoría, hipótesis y explicaciones rivales

**H1 (predictiva, falsable):** indicadores de historia institucional medidos as-of mejoran la predicción temporal del siguiente estado sobre un baseline robusto que ya incluye clase de iniciativa, legislatura, tiempo en riesgo, calendario, promotor institucional y composición/posición parlamentaria observable entonces.

**H0:** la ampliación no reduce pérdida de predicción fuera de muestra de forma material/estable; un resultado nulo constituye conclusión válida dentro del alcance.

**H2 (artefacto):** la aparente mejora procede de utilizar etiquetas de estado actualizadas posteriormente, títulos modificados, información de BOE publicada después, duplicados entre expedientes o codificación temática basada en el futuro. **Falsador:** retirar las variables vulnerables o reconstruir el snapshot as-of hace desaparecer la ventaja.

**H3 (rival institucional):** el calendario de legislatura, los ciclos electorales, la composición de la mayoría, el origen gubernamental, la agenda parlamentaria o cambios reglamentarios absorben la señal atribuida a la historia.

**H4 (rival de complejidad):** mejora por más grados de libertad y frecuencia temática, no por retroalimentación: placebo de historias permutadas con estratos de legislatura/tipo y modelo de capacidad equivalente.

**H5 (dependencia de cobertura):** los procesos que mejor figuran en fuentes tienen más transiciones visibles y favorecen un falso patrón de persistencia. Estratificar por disponibilidad de fuentes/versiones y comparar tasas de missingness; no confundir campo vacío con fase no celebrada.

Estos mecanismos pertenecen a marcos de institucionalismo histórico, dinámica de agenda y policy feedback. La revisión bibliográfica sistemática de antecedentes y el carácter novedoso de una aplicación concreta aún están pendientes.

### C. Fuentes, derechos y riesgo antes de outcomes

**Fuente A — Congreso de los Diputados:** buscador de iniciativas y fichas oficiales; enumeración por legislatura y tipo de expediente, con fechas de presentación/calificación, autores, fases, órganos, documentos y, solo en fase posterior a congelación, resultados. Es obligatorio identificar un método verificable de recorrer **todas** las entradas del universo elegido, paginación, filtros de tipo, exclusiones, deduplicación y cambios de interfaz. La UI y la documentación institucional prueban categorías de consulta, no un API oficial descargable de censos.

**Fuente B — BOCG/diarios y enlaces del expediente:** fuente de publicación y comprobación de hitos, preservando fecha de acto y fecha de publicidad como atributos diferentes.

**Fuente C — BOE:** sumario oficial fechado y documento en XML/PDF firmado según proceda, utilizado SOLO para confirmar la publicación de norma previamente vinculada de forma defendible a un expediente. La API de legislación consolidada no sustituye las versiones originales ni es por sí sola un registro de iniciativas presentadas.

**Fuente D — contexto opcional:** calendarios parlamentarios, composición de gobierno/grupos, elecciones y cambios de reglas, siempre con corte temporal, emisor y derechos verificados por separado; si faltan, baseline restringido con la información sí disponible y limitaciones expresas.

**Alcance temporal:** NO FIJADO; no elegir legislaturas, años, tipos ni tamaño muestral por resultados vistos. Definirlos al auditar acceso a los **metadatos de población**; registrar si las legislaturas elegidas están cerradas o si existe censura administrativa. Dejar fuera de la primera inferencia causal cualquier comparación con disposiciones no parlamentarias.

### D. Diccionario, preregistro y congelación

**Campos mínimos de entidad/proceso (sus nombres son contrato, no campos acreditados del portal):**

| Campo de trabajo | Significado y control |
| --- | --- |
| source_id, source_uri, issuer, rights_uri | Emisor, recurso y condición de uso comprobable por versión. |
| content_sha256, captured_at, parse_version | Byte hash, momento de captura y versión de parser. |
| legislature, initiative_type, expediente_id | Clave compuesta del universo; desambiguar renumeraciones e interacciones entre Cámaras. |
| entry_event, entry_occurred_at, entry_first_public_at | Acto de entrada y fechas del hecho y primer conocimiento público verificable. Si falta este último, marcar UNKNOWN; no inferirlo de captura actual. |
| event_type, occurred_at, first_public_at, effective_from/to | Transición y sus cuatro tiempos; permitir NULL y rangos inciertos. |
| process_status_asof, status_recorded_at, correction_at | Estado visible en una fotografía, publicación de estado y corrección. Estado actual no equivale a estado histórico. |
| originator_id, body_id, topic_class_asof | Promotor, órgano y materia codificados solo desde información previa al corte. |
| linked_boe_id, link_basis, link_confidence | Documento BOE y evidencia del enlace, con nivel UNKNOWN si no se prueba; match por título como candidato, nunca llave única automática. |
| terminal_cause, censor_reason, risk_entry/risk_exit | Desenlaces competitivos, censura derecha, izquierda/truncamiento y ventanas válidas. |
| data_quality_flags | Ambigüedad de identidad, OCR, campos faltantes, backfill, cambios de fuente, conflicto temporal. |

**Invariante as-of:** para una predicción al tiempo t, cada hecho usado debe satisfacer first_public_at ≤ t o acreditar otra disponibilidad pública en t; no basta occurred_at ≤ t. Si una fuente solo entrega su última fotografía, tratar los estados históricos como **no verificables** hasta recuperar snapshots archivados o demostrar inmutabilidad y publicación anterior. Fecha de captura es límite superior de disponibilidad observada, no primera publicación. Todo texto semántico de reintroducción se codifica desde la versión disponible en t.

**Congelación requerida:** guardar contrato de pregunta/unidad/mecanismo, instrumento y pruebas, lista de URL/iteradores, filtros de tiempo/tipo, criterios de exclusión, adversariales, baseline, esquema, semillas y plan de multiplicidad; anotar Git commit y hashes SHA256 de código y contratos ANTES de desbloquear datos de estado/resultados. Este borrador **no es** esa congelación.

### E. Ejecución prospectiva, pendiente

**Stage 0 (solo metadatos de elegibilidad; autorizado aquí como diseño, NO ejecutado):** construir iterador de expedientes para tipos/legislaturas declarados, limitando la extracción a ID, tipo, fecha inicial y metadatos de cobertura necesarios. No descargar documentos de desenlace, no mostrar tablas de resultado, no inspeccionar BOE de casos concretos. Si el portal expone outcomes junto a metadatos, la extracción debe ocultarlos al analista mediante whitelist de campos, logs mínimos y una validación separada del parser. Auditoría de paginación y denominador con totales del Congreso para el **mismo** alcance, sin afirmar censalidad por contar resultados de una sola página.

**Stage 1 (solo cuando G1 pase):** resolver integridad, procedencia, fechas y versionado, y congelar el análisis. Comparar catálogo en más de una extracción/fecha si es necesario para advertir cambios; el tiempo de captura no certifica la trayectoria histórica.

**Stage 2 (solo con contrato preregistrado):** importar estados y eventos, reconstruir cohortes/riesgos, vincular BOE con evidencia, calcular modelos descriptivos/baseline y ejecutar evaluación cronológica retenida.

**Stage 3:** reproducir desde originales, publicar exclusivamente artefactos con derechos comprobados, auditar manualmente una muestra preespecificada de enlaces sin revelar identificadores personales no necesarios; informe de fallos y condiciones de revisión. Ninguna fase se considera realizada en esta nota.

### F. Controles adversariales, selección y ausencia

Controles antes de outcomes: paginación duplicada u omitida; expedientes que cambian identificador; iniciativas originadas en el Senado; procedimiento del Gobierno frente a proposiciones; disolución parlamentaria y caducidad; desaparición de documentos; backfills y correcciones ex post; inconsistencias entre registro y primera publicación; caso BOE sin expediente y expediente sin BOE; publicación posterior al corte predictivo; paso por Senado y retraso externo a Congreso; competencia de múltiples terminales; calendario y periodos sin actividad.

Prohibir dos errores: **survivorship bias** por construir la cohorte desde BOE y **immortal time bias** por requerir información que se observa solo después de que un expediente sobrevive. Para la predicción de reintroducción, evitar leakage al agrupar por tema desde textos de legislaturas futuras; para evaluaciones reiteradas, agrupar procesos vinculados en particiones temporales que impidan duplicación entre entrenamiento y test.

La ausencia de un trámite en la extracción debe etiquetarse UNOBSERVED, no FAILED; la ausencia de vínculo a BOE debe distinguir UNKNOWN_LINK, NO_BOE_YET y NO_MATCH_CONFIRMED únicamente si existe verificación suficiente. No inferir inacción, incumplimiento, opacidad, estrategia o corrupción a partir de un NULL.

### G. Comparadores, inferencia y resultado discriminante

**Baseline descriptivo:** tabla de flujos por estado y riesgos competitivos; incidencia acumulada con censura apropiada, intervalos y denominadores documentados. Kaplan–Meier no es estimador de incidencia por causa cuando las salidas alternativas son competitivas.

**Baseline predictivo mínimo:** hazard en tiempo discreto con edad del expediente, tipo, legislatura/cohorte, calendario y estatus/órgano disponible al corte. **Baseline fuerte:** expansión jerárquica o regularizada con interacciones por familia procedimental y variables de contexto institucional justificadas, validación cronológica, calibración y control de censura; construir un competidor flexible de igual capacidad si el tamaño y soporte lo admiten. No declarar mejora frente a un modelo ingenuo cuando exista uno más competente.

**Modelo de interés:** mismo baseline, mismo horizonte, misma población, mismos datos disponibles y procedimiento de hiperparámetros, más una familia preregistrada de indicadores históricos as-of. Ablaciones: (i) retirar historia, (ii) permutar historia dentro de legislatura/tipo sin destruir calendarios, (iii) retirar materia/promotor, (iv) bloquear títulos/revisiones posteriores, (v) cambiar definición de censura o periodo de entrada.

**Partición:** forward chaining, último periodo retenido sin mirar etiquetas, separación entre expedientes conexos y evaluación de cambios de legislatura; no hacer mezcla aleatoria expediente-semana. Métricas y umbral de mejora material se congelarán antes de ver outcomes, con incertidumbre por clúster y comprobación de calibración. Si la fuente no permite establecer la disponibilidad temporal, no efectuar evaluación retrospectiva de predicción as-of; se permite informe descriptivo con limitación explícita.

**Lectura de hipótesis:** persistencia temporal, reintroducción, respuesta institucional y publicación normativa son mecanismos/estimandos diferentes; no se suman en un «índice de desempeño político». Asociación entre historia y desenlace no demuestra path dependence causal, eficiencia, promesas cumplidas o efecto de políticas sobre paro, salarios u otros outcomes económicos.

### H. Antecedentes, priors y evidencia

Antes del primer ciclo realizar revisión dirigida de estudios de supervivencia legislativa, reapertura de iniciativas, agendas parlamentarias, agenda-setting y policy feedback en España y comparables; registrar comparadores previos, unidad, periodos, disponibilidad y licencias. La distinción conceptual entre persistencia de un expediente y persistencia de un asunto se conserva como prior explícito. No afirmar prioridad ni novedad general sin revisión sistemática.

El registro nuevo de SOURCES/PRIORS/O7 solo sería admisible tras ejecución autorizada y comprobada dentro de la rama aprobada; esta nota no añade ni modifica ninguna fuente/claim del proyecto canónico. Un bloqueo del denominador es un hallazgo metodológico de factibilidad documentable, **no** resultado empírico sobre persistencia.

### I. Grado de evidencia y puertas científicas/de producto

Estado de partida de diseño: **grado científico no promovido; CT2 y gates de PFL no cambian**. No se declara evidencia independiente, validez causal, predicción validada, producto aceptado, ni imputación de efectos a actores. Separar:

- G0: marco/definición/protocolo y condición de congelación sin outcomes.
- G1: población Congreso completa para el alcance elegido, derechos verificables, cobertura/fechas/IDs auditados.
- G2: procesos/eventos bitemporales, desenlaces y censoring reproducibles, links BOE con evidencia; metadata as-of verificada.
- G3: baseline fuerte, validación temporal retenida y rivales/controles discriminantes.
- G4: reproducibilidad íntegra por tercero y resultados negativos/positivos con incertidumbre.
- G5: adopción humana de aplicaciones y gates propios de datos/puntuación/publicación, fuera de esta investigación.

Un fallo de G1 impide G2–G4; una ejecución de software no equivale a un avance de CT2 científico. Los gates de fantasy no se levantan por completar el protocolo.

### J. Regla de decisión, presupuesto y parada R5

**No abrir ciclo 1** hasta resolver G1 y fijar pregunta, corte, clase de expediente, fuente y código/controles con hashes preregistrados. Si falla la enumeración, registrar qué mecanismo falló, cuáles fueron los dos intentos equivalentes y el artefacto concreto que permitiría reabrirlo; R5 exige PARKED tras dos negativas equivalentes sin novedad. No reemplazar por búsquedas ad hoc de leyes ya aprobadas ni gastar una plaza en variar filtros sin cambiar mecanismo.

Una vez abierta una plaza específica, considerarla válida solo con ejecución real, recibo verificable, registro de fallos, resultados diferenciadores y cierre A–J; registrar invalidaciones y planificación por separado. Cualquier ciclo de producto AB-P debe tener contrato y métrica funcional propios, separado del AB-R institucional. El límite de 20 **no** requiere agotarlo. No usar hipótesis de esta nota para atribuir nuevos ciclos a concesiones históricas.

## Prerrequisitos verificables antes de registrar un ciclo

1. **Gobernanza:** confirmar HEAD, rama de investigación, ledger de la autorización nueva independiente, permiso para publicar originales/derivados y no duplicación de campañas previas; preservar otras concesiones.
2. **Taxonomía institucional:** determinar legislación exacta y fases por tipo (Gobierno/proposición/Senado), fecha de riesgo de entrada y eventos competitivos con fuentes primarias.
3. **Marco de elegibilidad:** documentar iteración exhaustiva de expediente por legislatura y tipo, resolución de paginación y filtros, totales de referencia del mismo universo, exclusiones, cobertura y esquema de deduplicación. No usar BOE para obtener el denominador.
4. **Identidad:** clave estable de expediente, versión, organismo, periodo y origen; protocolo auditable de enlace expediente↔BOCG↔BOE. Los enlaces dudosos quedan desconocidos.
5. **Tiempo as-of:** demostrar al menos para el subconjunto usado qué metadatos eran públicos y cuándo; registrar fecha de hecho, publicación, captura y revisión, con casos de backfill y corrección.
6. **Licencias:** verificar condiciones de reutilización aplicables a cada fuente y su versión; existencia de una API o sitio no equivale a derecho para cualquier redistribución.
7. **Selección científica:** revisar tres rutas, antecedentes y falsadores; escoger población, intervalo, resolución temporal y estimando antes de outcomes; justificar por qué la comparación es competente.
8. **Instrumentación:** congelar parser con whitelist de Stage 0, tests de paginación, duplicado, link dudoso, fecha invertida, versión tardía, censoring, pérdidas y cross-legislatura; hash Git/SHA256 previo a análisis de resultados.
9. **Evaluación:** predefinir baseline, holdout temporal, métricas, sensibilidad y tratamiento de multiplicidad; separar análisis exploratorio de prueba confirmatoria.
10. **Reproducción/cierre:** guardar manifest de fuentes, código, hashes, fecha de captura, comandos, salida y límites. Si cualquiera de los puntos críticos falla, documentar BLOCKED/PARKED y saldo intacto.

## Contrato de entregables de Stage 0 (solo futuro)

Crear **solo cuando se autorice la preparación técnica** un reporte de elegibilidad sin outcomes con: definición textual del universo; rango temporal propuesto; tipos y legislaturas incluidos/excluidos; emisor, URI, licencia por archivo; fecha de consulta; SHA256 de bytes autorizados; instrumento y hash; número de IDs únicos enumerados; duplicados; faltantes de fecha; totales y paginación; tasas de registros sin primer momento de publicidad; criterios de paro; resultado PASS/BLOCKED de G1. Cada conteo debe proceder de consulta reproducida y declararse con su corte; **en este documento no existe ningún valor observado**.

Manifest futuro propuesto (campos vacíos hasta observar fuentes, jamás rellenar a mano con estimaciones):

    {
      "status": "NOT_COLLECTED",
      "congreso_population_verified": false,
      "initiative_type": null,
      "legislature_scope": null,
      "risk_entry_definition": null,
      "publisher": "Congreso de los Diputados",
      "official_source_uri": "https://www.congreso.es/es/web/guest/busqueda-de-iniciativas",
      "license_verified": null,
      "captured_at": null,
      "source_sha256": null,
      "instrument_git_commit": null,
      "n_items": null,
      "n_unique_exp": null,
      "missing_entry_time": null,
      "first_public_at_coverage": null,
      "pagination_audit": null,
      "source_total_reconciliation": null,
      "outcome_fields_read": false,
      "decision": "NO_CYCLE"
    }

**Reproducibilidad de la nota sin consultar outcomes (PowerShell, directorio scratch):**

    Get-FileHash -Algorithm SHA256 .\PFL_CONGRESO_PERSISTENCIA_FEEDBACK_AJ_BORRADOR_20261031.md
    Get-Content -Raw .\PFL_CONGRESO_PERSISTENCIA_FEEDBACK_AJ_BORRADOR_20261031.md

Estos comandos son para la **nota**, no para un análisis de datos. No se ha creado ni invocado ningún parser de Congreso/BOE; el esquema de manifest es una propuesta de aceptación, no un registro empírico. La ejecución futura requerirá instrumentos nuevos con criterios de test; no inventar rutas de script existentes.

## Referencias primarias de documentación consultadas, sin expedientes individuales ni outcomes

- Congreso, **Buscador de iniciativas**: https://www.congreso.es/es/web/guest/busqueda-de-iniciativas — filtros de legislatura, tipo, fecha, expediente y resultado; existencia del buscador, no exhaustividad ni exportabilidad acreditadas.
- Congreso, **Consultas más frecuentes**: https://www.congreso.es/es/cem/faqs — el expediente permite consultar estado y publicaciones asociadas para clases distintas de iniciativa.
- Congreso, **Funciones del Congreso**: https://www.congreso.es/es/cem/func — distinción de proyectos y proposiciones de ley, toma en consideración y fases.
- AEBOE, **FAQ de sumarios BOE**: https://www.boe.es/datosabiertos/faq/boe.php — el BOE publica normas y actos, expone sumarios y formatos documentales; no es listado de propuestas fallidas.
- AEBOE, **API de datos abiertos**: https://www.boe.es/datosabiertos/api/api.php — documentación de rutas sumario por fecha y legislación consolidada; NO se consultaron documentos de resultados.
- AEBOE, **FAQ de legislación consolidada**: https://www.boe.es/datosabiertos/faq/consolidada.php — carácter informativo/revisable de la consolidación, sin sustituir la publicación oficial histórica.

**Restricción final:** ningún enlace a un caso concreto, ninguna muestra del BOE extraída, ninguna población Congreso admitida, ninguna inferencia cuantitativa calculada. La siguiente acción justificable es **verificar el marco de expedientes del Congreso mediante metadatos de elegibilidad**, sin desbloquear la variable resultado hasta cerrar G1 y congelar A–J definitivos.
