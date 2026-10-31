# PFL — contrato ontológico y epistemológico para datos políticos españoles

**Estado:** propuesta de modelización V0, no validación empírica ni elección definitiva del TFM. Fecha 31-10-2026. Complementa la delimitación sistémica V0 y el programa AB-H comparativo ya existentes. No consume ciclos científicos.

## Tres marcos relacionados pero no intercambiables

**Luhmann: reproducción de comunicaciones y decisiones.** La unidad teórica candidata es una operación comunicativa cuya concatenación participa de la reproducción del sistema político. Organización, diputado, ministerio, expediente y documento constituyen categorías analíticamente distintas. Un registro de PFL no puede reconocerse automáticamente como operación luhmanniana por tener un emisor político. La vinculación a decisiones colectivamente vinculantes exige interpretación institucional y documentación de competencias, procedimientos y actos.

**Easton: entradas, conversión, salidas y retroalimentación.** El esquema de demandas y apoyos, procesos y productos permite proponer relaciones entre perturbaciones, decisiones y respuestas. No prueba que un indicador externo cause una decisión ni obliga a equiparar el entorno con una sola variable macroeconómica. Se propone delimitar ventanas verificables para entradas recibidas, respuestas documentadas y posibles consecuencias posteriores.

**Deutsch: información, memoria, retardos y control.** La cibernética política introduce hipótesis de aprendizaje, realimentación, capacidad de respuesta y desfases. Para identificar corrección por error hacen falta una referencia u objetivo, una señal accesible, un mecanismo de actualización, una intervención y un rival sin corrección. Persistencia estadística, inercia administrativa y autorregulación informacional no son equivalentes.

Estas tres tradiciones constituyen un **programa de mecanismos y rivales**, no etiquetas detectadas automáticamente desde bases de datos. Un modelo de rezagos puede predecir sin identificar feedback causal; un grafo correcto documentalmente puede no representar la autopoiesis del sistema.

## Granos distintos de observación

| Unidad | Observación candidata | Inferencia no autorizada |
| --- | --- | --- |
| Institución u organización | Cámara, órgano, competencia formal | Que identidad organizativa equivalga a operación funcional |
| Expediente fuente-local | Emisor, legislatura, familia e ID | Que sea idéntico a otro por título o temática |
| Comunicación procesal | Presentación, pregunta o comunicación fechada | Que la fase haya concluido |
| Decisión | Acto formal con competencia y resultado documentados | Que fuera público desde su fecha de actuación |
| Documento publicado | BOCG, BOE, diario, revisión | Que constituya todas las oportunidades procesales |
| Persona en rol | Cargo, mandato o relación formal | Que haya causado una decisión institucional |
| Contexto económico, jurídico o mediático | Indicador, norma o publicación externa | Que una asociación o co-movimiento identifique causalidad |
| Observación documental | Original, hash, licencia, captura | Que la ausencia de registro pruebe ausencia de acto |

**Tres fronteras permanentes:** funcional-sistémica (qué comunicaciones se interpretan como políticas), jurídico-institucional (quién posee competencia para qué acto) y documental (qué registra realmente la fuente y desde cuándo). España delimita el objeto empírico prioritario, no un cierre geográfico de todos sus acoplamientos.

## Contrato temporal y selección documental

Una revisión o hecho distingue: **occurred_at** o día del acto (tiempo válido); **document_published_on** (fecha editorial); **first_public_at** acreditado o desconocido; **available_by** como cota conservadora sustentada, no primer instante exacto; **captured_at/recorded_at** del observatorio; y **source_version/original_sha256/rights_state/coverage** de la fuente. La fecha HTTP, la creación administrativa, el boletín y la captura reciente no autorizan inventar la primera publicación histórica.

Para predecir en el corte temporal t, cada característica debe haber sido públicamente accesible según evidencia independiente antes de t. La disponibilidad al **observatorio local** exige además adquisición y auditoría. Si un recibo se registra con precisión de segundos, se considera con seguridad accesible solo desde el segundo siguiente. Una revisión futura tampoco debe revelar su existencia mediante contadores, diagnósticos, errores o visualizaciones retrospectivas.

Queda prohibido: seleccionar exclusivamente normas publicadas por BOE como denominador de iniciativas; convertir valores desconocidos en ceros; inferir rechazo o fracaso ante falta de trámite visible; convertir el estado actual de octubre de 2026 en estado histórico de 2024; o unir Congreso, BOE y empresas por coincidencias de fechas, textos, nombres o apellidos.

## Estado de evidencia y límites

Se han verificado cuatro distribuciones PDDL del Parlamento de Canarias: 2023/X/PPL (1), 2024/XI/PE (686), 2025/XI/PE (543) y 2026/XI/PE (524). Dos archivos JSONL conservan 1.754 identificadores fuente-local diferentes. En un derivado agregado se observaron 34 combinaciones de distribución y mes con fechas de creación declaradas, sin publicar identificadores, textos ni outcomes. Meses sin filas en este derivado permanecen como ausencia de observación, no como meses institucionalmente inactivos.

Los contadores de otra vista editorial pueden corroborar los CSV, pero ambas vistas pueden compartir sistema subyacente y filtros. Coincidir en cardinalidad no acredita versiones históricas, transiciones ni el universo general de la Cámara. Memorias retrospectivas del Congreso, si contienen categorías de expedientes admitidos, retirados, rechazados o caducados, pueden ofrecer denominadores agregados nacionales; por sí solas no reconstruyen microdatos históricos ni primera disponibilidad.

Actualmente no hay contrastes identificados de feedback causal, persistencia estratégica, efectos políticos, transparencia, influencia empresarial o reproducción luhmanniana. La pregunta y el estimando del TFM siguen abiertos.

## Falsadores y rivales

**M1 — Autorreproducción interna.** Probar si la historia institucional anterior y conocible en t reduce una pérdida predictiva de transiciones frente a un baseline competente que incluye calendario, procedimiento y composición. Falsadores: pérdida sin mejora en cohorte futura, mejora anulada al corregir fuga temporal, selección, duplicados o distinta complejidad del modelo.

**M2 — Acoplamientos.** Contrastar si antecedentes económicos, jurídicos o mediáticos temporalmente disponibles aportan señal incremental. Rivales necesarios: estacionalidad, composición de agenda, cambios de cobertura, shocks compartidos y tendencia. Una señal adelantada no identifica un efecto causal sin supuestos y diseño adicionales.

**M3 — Selección documental.** Comprobar si la aparente autorreproducción procede de observar solo publicaciones o procesos terminados, con supervivencia selectiva de las fuentes. Falsador: reconstruir un denominador de todas las entradas y repetir la inferencia con pendientes, retiradas, fracasos, censura a derecha y riesgos competitivos, sin que la señal cambie materialmente.

Cada estudio requiere contrato A–J, hipótesis rivales, población de riesgo, semántica de outcomes, censura y SHA de código congelados en remoto antes de observar resultados. Las cuatro cohortes actuales son **metadatos fuente-local**, no instancias automáticamente admisibles como decisiones, enlaces Congreso–BOE o estimadores de resultados políticos. El laboratorio Fantasy League sigue siendo aplicación secundaria y ficticia, sin valoraciones de personas reales.

Referencias teóricas a contrastar en el marco académico: David Easton, *A Systems Analysis of Political Life* (1965); Karl W. Deutsch, *The Nerves of Government* (1963); Niklas Luhmann, *Die Politik der Gesellschaft* (2000) y *Political Theory in the Welfare State* (edición inglesa de 1990). Las operacionalizaciones propuestas aquí son de PFL, no equivalencias atribuidas sin discusión a esos autores.
