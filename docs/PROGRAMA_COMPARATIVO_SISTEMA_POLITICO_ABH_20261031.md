# PFL — programa comparativo y falsable de reproducción del sistema político español

**Versión:** propuesta prospectiva, 31-10-2026. **Estado epistémico: DISEÑO / NO VALIDADO**. Este documento no es prerregistro de resultados y no consume ciclos AB-H. Su objeto es delimitar el programa, no alterar el alcance total de PFL ni cerrar la pregunta del TFM. Se preservan el marco sistémico adoptado, las rutas alternativas y los hallazgos negativos.

## 1. Delimitación: sistema, operaciones y observables

En una lectura estricta de teoría de sistemas, el sistema político no se define por la suma de políticos, escaños y organizaciones, sino por una reproducción específica de comunicaciones orientadas a decisiones colectivamente vinculantes. Es una **hipótesis de modelización**, no un hecho establecido automáticamente por los datos. Los expedientes parlamentarios son unidades documentales; las organizaciones son sedes de decisiones y reglas de pertenencia; la actividad económica, jurídica, mediática y social puede actuar como entorno relevante o acoplamiento. **Una entidad de la base de datos no equivale ontológicamente a una operación del sistema político.** Véanse Niklas Luhmann, *Law as a Social System*, cap. 9, [Politics and Law](https://doi.org/10.1093/oso/9780198262381.003.0010) y la introducción de Hugh Baxter (2013), [Niklas Luhmann's Theory of Autopoietic Legal Systems](https://doi.org/10.1146/annurev-lawsocsci-102612-134027).

Definir tres límites diferentes antes de cada estudio:

- **Límite teórico-funcional:** comunicaciones/decisiones con capacidad y pretensión de vinculación colectiva; ni una noticia ni un indicador económico se convierten en operación política por estar correlacionados.
- **Límite jurídico-organizativo:** ámbito de competencias de Congreso, Senado, Gobierno, comunidades autónomas, autoridades administrativas e instituciones implicadas; cada cual tiene procedimientos distintos.
- **Límite de observación:** lo que la fuente primaria efectivamente registra, con identidad, granularidad, fecha del acto, fecha de publicación, fecha de captura y limitaciones. Este límite es un sesgo de medición potencial y nunca una frontera teórica suficiente.

Granos ontológicos distintos: `institution`, `process` (expediente y legislatura), `procedural_communication`, `procedural_decision`, `document`, `actor_role`, `organization`, `environmental_series`, `observed_relation` y `hypothesized_influence`. Solo los cuatro primeros pueden constituir candidatos a secuencias operativas; una referencia BOE puede registrar publicidad de un resultado, no generar retrospectivamente la iniciativa que no apareció allí.

## 2. Tres mecanismos competidores y qué los diferenciaría

**M1 — Autorregulación institucional (hipótesis interna):** trayectorias de procesos anteriores y reglas formalizadas modifican la probabilidad o tiempo hasta ciertas nuevas decisiones, una vez considerado el calendario, la composición y las competencias. Evidencia mínima: **universo completo de nuevas iniciativas** con eventos de resultados y fechas anteriores, nunca solo éxitos BOE. Predicción diferencial prospectiva: una historia temporal elegible mejora el log-loss de tránsito frente a un baseline institucional de igual complejidad, fuera de la legislatura/cohorte usada para entrenar. Falsadores: mejora nula tras controlar calendario, fuga `as-of`, permutación de historias o cambios de composición; tasa de ausentes diferencial entre estados.

**M2 — Dependencia de entorno e instituciones acopladas:** perturbaciones económicas, legales o comunicativas *anteceden temporalmente* cambios en agenda, respuestas o salidas, sin presuponer causalidad. Fuentes candidatas: fechas oficiales BOE de cambios normativos, indicadores INE/EUROSTAT económicos con vintages, publicidad institucional y series mediáticas legalmente reproducibles. Medir ventanas y retardos definidos antes de outcomes; contrastar rival de tendencias compartidas y calendario legislativo. **Un enlace temporal es una asociación**, mientras que atribuir efecto causal exige un diseño de identificación y una definición de exposición independiente.

**M3 — Reproducción aparente por selección documental:** una mayor tasa de «finalización» entre casos presentes en BOE, bases consolidadas o boletines más completos surge al seleccionar únicamente salidas publicadas y omitir pendientes, no por una dinámica institucional. Predicción diferencial: el efecto desaparece o cambia al reconstruir población en riesgo desde expedientes de entrada, con censura derecha y cobertura estratificada. Falsador de M3: marco fuente de todas las entradas y observación homogénea de desenlaces, incluyendo negativos, en un corte temporal auditable.

**No adoptar un único relato.** Las tres explicaciones pueden coexistir, pero la distinción de grados de evidencia y la competencia entre rivales resulta obligatoria.

La literatura de *policy feedback* ofrece antecedentes específicos sobre recursos/incentivos y aprendizaje/interpretación (Pierson, 1993, [When Effect Becomes Cause](https://doi.org/10.2307/2950710)). Béland, Campbell y Weaver (2022), [Policy Feedback](https://www.cambridge.org/core/elements/policy-feedback/3231877106C458D0CF766173080B0409), distinguen mecanismos económicos, sociopolíticos, informativos, fiscales y administrativos. **Ni su plausibilidad teórica prueba que un patrón observado en España esté causado por feedback.**

## 3. Población: requisito anterior a outcomes

**Programa principal Congreso:** una sola familia procesal homogénea por legislatura/ventana, *todos* los expedientes con acto de entrada observable, incluidos aquellos sin seguimiento, caducados, retirados, no considerados, rechazados o aprobados. Cuantificar estratos `(legislature, family)`, totales publicados/descargables, claves únicas, páginas, lagunas y cobertura del ciclo completo. BOE se trata como **fuente de posibles eventos de salida** enlazados a una clave explícita y validada; ningún documento BOE define el denominador.

**Piloto alternativo autonómico:** Parlamento de Canarias, clases oficiales de iniciativas con catálogos PDDL específicos por año, legislatura y tipo. El [catálogo de iniciativas de 2023/X/PPL](https://datos.parcan.es/dataset/iniciativas_tipoppl_anio2023_xlegislatura/resource/dd23200f-d3df-4360-92d9-45807ba5da87) y las preguntas escritas PE de 2026/XI aportan rutas concretas. No equiparar categorías autonómicas con las del Congreso. El acceso al subportal de datos abiertos del Senado presenta aceptación explícita de condiciones **por mero uso**, así que la línea queda excluida de nuevas descargas automáticas hasta una decisión humana. Las distribuciones PDDL no acreditan por sí mismas integridad de series, desenlaces, bases jurídicas de tratamiento de personas ni disponibilidad histórica.

Como condición de avance no basta un fichero de 200 bytes: se requieren una definición estable de unidad, una cardinalidad independiente de los casos con éxito, cobertura de entradas y **eventos de transición con fechas** (o, si solo hay estado actual, etiquetar el análisis como fotografía de estado con tiempo desconocido, no supervivencia).

## 4. Estados, censura, riesgos competitivos y temporalidad

Ontología tentativa, sujeta al diccionario jurídico de la fuente: `registered` → `admitted` → `under_consideration` → `decision_recorded`, con terminales **mutuamente excluyentes en el estimando elegido** (`accepted`, `rejected`, `withdrawn`, `lapsed_dissolution`, `other_recorded_termination`) y `still_pending` como **censura a derecha**, no fracaso. El tránsito de una iniciativa entre cámaras o una reintroducción en otra legislatura son relaciones entre expedientes, no una identidad colapsada automáticamente.

Registrar `valid_from`/fecha de actuación y `first_public_at` acreditada separadamente, y `recorded_at` de adquisición. Cuando solo consta el día oficial de un boletín, conservar granularidad `DATE_ONLY`, eventualmente `available_by` con justificación como cota **posterior o igual** a la disponibilidad, nunca transformarla en instante exacto. Una captura de 31-10-2026 no permite simular retrospectivamente la disponibilidad de una actualización de 2024 sin un archivo/versionado histórico. Toda validación `as_of=t` requiere que dato e inferencia fueran conocibles entonces.

Si los estados terminales no incluyen fechas, **no** estimar hazard/incidencia acumulada por causa: limitarse a recuentos de estado actual, estratificados por antigüedad y año, con incertidumbre por selección. Si fechas están acreditadas, comparar Kaplan–Meier solo para desenlaces conjuntos, incidencia acumulada de riesgos competitivos y modelos discretos con censura; evitar el uso ingenuo de `1-KM` como incidencia de una causa particular.

## 5. Prerregistro y rivales que impedirían hallazgos espurios

Tras superar las condiciones de datos, crear **antes de abrir outcomes** un contrato A–J por ciclo con población/cohorte, ventana, fecha de corte, granularidad, tratamiento de missingness, rivales, estimandos, métrica principal, intervalos, coste y seeds. Congelar código + hashes de fuentes y contrato en un commit remoto reproducible. Especificar tres rivales competentes:

1. **B0 calendario y exposición:** edad del expediente, familia procedimental, legislatura/cohorte, interrupciones y disponibilidad documental; predicción constante por estrato y modelo de duración flexible.
2. **B1 institución y competencia:** B0 más órgano, reglas, composición de mayorías y cambios procedimentales conocidos en la fecha de predicción.
3. **B2 memoria temporal/coupling:** B1 más historial anterior documentado de materias y decisiones, shock económico-jurídico o agenda, distinguiendo señal interna y ambiente.

Evaluar en *rolling origin* o cohorte/legislatura retenida posterior, sin intercambiar observaciones del mismo expediente entre entrenamiento y test. Exigir log-loss/Brier y calibración; para decisiones con riesgos competitivos, puntuación de probabilidades por causa y horizonte, no solo AUC. Placebos obligatorios: historial **posterior** (debe bloquearse por as-of), perturbaciones futuras como control negativo, permutación estratificada de historias, cambio de vintage documental, deduplicación alternativa y restricciones de cobertura. Comparar parsimonia y costes, no convertir significación en superioridad teórica.

**R5 y tamaño:** un corpus de solo una o muy pocas iniciativas no identifica un mecanismo de reproducción; detener inferencias de supervivencia o modelos complejos antes de gastar ciclos. No sustituir faltantes por ceros, no seleccionar ejemplos notorios ni aprovechar una fuga ya observada como contraste confirmatorio. Si alguien vio los resultados previamente, marcar explícitamente `EXPLORATORY_AFTER_OUTCOME_EXPOSURE`, reservar una nueva muestra auténticamente independiente y no reescribir el historial como prerregistro perfecto.

## 6. Transferencia entre investigación y producto

El observatorio puede mostrar: procedencia original, SHA, licencia, censo documentado frente a desconocido, año/familia, número de registros efectivamente verificados, estados descriptivos actuales, motivos de cuarentena y semántica de fechas. Solo tras pasar la admisión temporal puede ofrecer consultas históricas `as-of`. Una visualización de estados procesales no es un ranking de mérito; ninguna puntuación a personas reales ni inferencia de influencia empresarial/media se habilita por la presencia de enlaces relacionales. La Fantasy League sigue como uso secundario ficticio mientras no se superen los gates jurídicos y epistémicos.

**Decisión actual:** preservar alternativas Congreso/Canarias/BOE/Interior, sin equivalencias injustificadas. No hay contraste de mecanismo M1–M3 ejecutado o confirmado en este documento.
