# Arquitectura científica y funcional

## Objeto y distinción ontológica

El proyecto observa *decisiones y comunicaciones institucionales públicamente registradas*, no 'calidad intrínseca de un político'. El sistema produce cuatro objetos con regímenes epistémicos distintos: (a) registros recuperados de una fuente; (b) inferencias codificadas sobre registros; (c) probabilidades de eventos futuros con incertidumbre y calibración; (d) puntos de un juego derivados de una **convención pública**. Los objetos (b)–(d) no se confunden con (a).

Lente sistémica [marco propuesto]: diferenciación funcional entre política, medios, derecho, administración y juego; comunicaciones y decisiones atribuidas institucionalmente; observación de segundo orden (los indicadores y el fantasy pueden modificar la conducta observada); dependencia de trayectoria y retroalimentación. Contrastar esta interpretación con explicaciones de institucionalismo, teoría de elección racional, redes e incentivos; no invocar 'emergencia' cuando la regla de simulación impone el resultado.

## Unidades de análisis

**Persona**: identificador estable interno (no deduplicar por nombre). **Mandato/cargo**: intervalo temporal, institución, partido y grupo —adscripciones que pueden cambiar—. **Iniciativa**: expediente estable, promotores diferenciados y fases. **Evento**: transición o acto identificado de manera única en su fuente (una votación, intervención, modificación de trámite, nombramiento). **Participación**: relación tipada y evidenciada persona↔evento (emisor, proponente, interviniente, voto registrado, firmante). **Organización**: partido, grupo parlamentario, órgano, ministerio y club fantasy como categorías distintas. **Tiempo**: tiempo efectivo del hecho y tiempo de conocimiento público (bitemporalidad); snapshot de alineación previo a jornada.

No deducir automáticamente que quien vota a favor promovió la iniciativa, ni que el promovente causalmente consiguió su aprobación. La aprobación de una ley tampoco es el indicador correcto de todas las funciones representativas o de control del Ejecutivo.

## Pipeline propuesta

`landing/raw` (archivos fuente, hashes, headers y hora) → `bronze` (parseo por versión, control de esquema, rechazos) → `silver` (IDs, vocabularios, eventos, correcciones, relaciones) → `gold` (tablas analíticas congeladas *as-of*, features con tiempo de disponibilidad) → `prediction` (distribuciones, calibración, score) → `fantasy` (cuentas, mercado, jornadas, ranking, eventos adjudicados).

Ejecución por lotes incremental e idempotente; controles de disponibilidad, cuotas, cadencia y fuente; colas de eventos con reconciliación nocturna y versionado sin sobreescritura. Para escala de miles/millones de documentos la propuesta es `httpx/requests` con reintentos conservadores + almacenamiento de blobs cifrado + PostgreSQL (OLTP) + Parquet/DuckDB o Polars (OLAP) + Prefect/Dagster (orquestación), **a evaluar, no stack implantado**. Python para ingesta/NLP/simulación; R para inferencia multinivel, modelos de recuento y análisis de robustez; SQL como soporte reproducible.

La extracción a gran volumen es un problema de reproducibilidad institucional antes que de velocidad máxima: cada estado reconstruido debe poder explicar *de dónde salió, cuándo se conoció y bajo qué definición*.

## Mecánica fantasy: propuesta, no copia

Cada usuario crea un **club o coalición fantasy ficticia**, elige figuras públicas reales dentro de restricciones de presupuesto y posiciones institucionales y participa en temporadas con cortes temporales explícitos. Se evita llamar al club 'partido registrado' porque tiene otro significado jurídico. Un fichaje de una persona **no significa adhesión ideológica**.

Presupuesto, mercado de pujas, cambios de plantilla y jornadas son mecánicas del género. Las opciones como límites de fichajes por grupo, diversidad de cargos o cupos ministeriales deben estudiarse con simulaciones de competitividad, no imponerse como 'justas' sin evidencia. No se copian las cifras ni reglas exactas de LaLiga Fantasy.

Una jornada puede ser una semana política (lunes-domingo) con *lock* anterior al primer evento puntuable conocido, y ventana excepcional para eventos sobrevenidos. **Esto es hipótesis de diseño, no decisión definitiva**.

### Capa de eventos observables (definiciones candidatas)

Tipos: intervención de control registrada, pregunta parlamentaria, iniciativa formal, enmienda, rol documentado en aprobación/rechazo de trámite, asistencia/voto cuando es verificable, nombramiento o pérdida de cargo, actividad institucional calendarizada. Los eventos de medios y redes sociales forman una **rama separada**: su volumen y sesgos de cobertura los hacen problemáticos como primera fuente de puntos.

### Capa de puntuación separada del predictor

`score_{i,w}=Σ_e weight_{kind(e),role(i,e),version} * evidence_quality_e * eligibility(i,e)`. La fórmula inicial es un **contrato normativo** testeable y modificable por temporada; el control de complejidad evita premiar infinitas intervenciones triviales o convertir toda controversia en 'pérdida de puntos'. Mantener `missing != zero`, controlar doble atribución y documentar límites de rol.

Diseño de pruebas: (i) puntuación bruta, (ii) normalizada por exposición (oportunidades institucionales), (iii) contrafactual por papel de gobierno/oposición, (iv) combinación con índice de colaboración de calidad, cuyo fundamento precisa validación manual. El fantasy puede usar una opción reglamentaria fija aunque la investigación rechace que mida valor social objetivo.

## Problema del valor de mercado

Propuesta testable: calcular estimación predictiva de puntos futuros `P(Y_{i,w+1}|X_{<=w})`, incertidumbre y riesgo de no disponibilidad; precio inicial determinado por mercado simulado y calibración económica. La cotización NO equivale a capital político real. Una estimación con gran incertidumbre debería mostrar intervalos/advertencias, no precisión decimal aparente.

Separar tres magnitudes: `market_price` (resultado endógeno de pujas fantasy), `forecast_points` (resultado estimativo) y `institutional_influence` (constructo sociológico con validez no demostrada). Mezclarlas es error de medición.

## Modelos estadísticos mínimos

Definir primero outcome observable: `Y_{i,w+1}` = número de actuaciones registradas de tipo predefinido atribuibles a persona i durante la semana siguiente, con `exposure_{i,w+1}` = nº oportunidades formalmente elegibles *conocidas o estimables en el corte*. Usar Poisson/NB de recuentos, modelos de dos partes para ceros, interceptos de persona/grupo/institución; calibrar con ranked probability score, deviance, MAE y cobertura. Si el futuro denominador no se conoce, modelarlo como variable incierta; no filtrar por número futuro de eventos.

Competidores profesionales: (a) tasas por rol e historial móvil, (b) Poisson jerárquico con calendario, (c) binomial negativa, (d) boosting de árboles con features disponibles al corte, (e) dinámica de redes. **La comparación debe tener paridad de acceso y presupuesto razonable**; un transformer de texto sin baseline temporal sería metodológicamente insuficiente.

Validación temporal `rolling-origin`: entrenar en periodos anteriores, validar en semanas posteriores, bloqueando futuras revisiones; evaluar cambios de legislatura y régimen, cobertura y cold start. Bootstrap por grupos temporales/institucionales o intervalos dependientes: no tratar eventos correlacionados de una misma sesión como independientes.

## Simulación de sistemas políticos y de usuarios

Proponer dos modelos separados, que no se justifican mutuamente:

A. **Institucional**, agentes: políticos/grupos/órganos y aristas de coalición/control. Reglas calibradas en transiciones empíricas, agenda endógena y negociación. Falsador: un baseline Markov/temporal o modelo descriptivo sin agentes reproduce las predicciones; simulación puede ilustrar mecanismos pero no estimar efectos causales sin identificación.

B. **Mercado fantasy**, agentes jugadores con presupuestos, pujas y elecciones adaptativas; analizar concentración, desigualdad de acceso, estrategias, inflación y respuesta a scoring. Pruebas de ablación: sin precios dinámicos, sin transferencias, sin penalización/bonus por exposición; distinguir efectos introducidos por las reglas de patrones emergentes.

Un hallazgo de A no valida B, ni viceversa; B puede ser un interesante sistema de observación de segundo orden cuando las calificaciones influyen en atención pública, pero esa retroalimentación en personas reales se debe **medir**, no asumir.

## TFM: opción de núcleo investigable

*Pregunta fuerte candidata*: ¿cuánto mejora la predicción de actividad parlamentaria individual semanal un modelo longitudinal relacional con oportunidades institucionales y estructura de agenda frente a baselines temporales y jerárquicos, usando solo datos accesibles antes del corte? Una pregunta rival: ¿cuándo la gamificación induce sesgos sistemáticos de visibilidad y ventaja institucional? Ambos requieren un trabajo empírico distinto.

Para TFM priorizar ámbito Congreso (legislatura suficientemente cubierta), ventana verificable y una única predicción, no una 'valoración global' moral de toda la política española. Construir el fantasy sólo hasta prototipo experimental.
