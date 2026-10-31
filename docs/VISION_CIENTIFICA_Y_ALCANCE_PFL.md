# Politics Fantasy League — visión científica, alcance real y mandato de no deriva

**Versión:** 1.0 — 31 de octubre de 2026  
**Naturaleza:** declaración de alcance y objetivos expresos del promotor; **no** resultado científico, validación empírica, especificación de funcionalidades terminadas ni autorización genérica para ejecutar campañas.  
**Objeto:** restituir y estabilizar el objetivo central de PFL para el desarrollo futuro y el TFM de Ciencia de Datos Aplicada a las Ciencias Sociales (DaSoc, USAL/UGR).  
**Confidencialidad:** documento deliberadamente apto para un repositorio público; no contiene nombres, contactos ni conversaciones personales de tutoría.

## 1. Declaración central del proyecto

**Politics Fantasy League (PFL) es, primordialmente, una infraestructura científico-computacional para recopilar, armonizar, comprender, analizar, modelizar, predecir y simular fenómenos de la política española real, con la máxima profundidad histórica que pueda alcanzarse legal y metodológicamente.**

Una liga fantasy política, con personas públicas e instituciones reales como referencias documentales, es **una aplicación y caso de uso del núcleo científico**, no el fundamento exclusivo del proyecto ni su sustituto. Otros casos de uso son un observatorio histórico, consultas y visualizaciones, análisis de redes e instituciones, predicciones auditadas y laboratorios de simulación. La simulación puede incluir mundos hipotéticos para contrastar mecanismos; eso no convierte el universo factual del producto en ficticio.

**El propio PFL —infraestructura de datos, modelos, análisis, simulaciones y aplicaciones— es el proyecto de TFM.** El videojuego no debe convertirse en una tarea ajena al TFM; tampoco puede degradarse la ciencia de datos a un complemento ornamental del videojuego.

El objetivo de largo plazo incluye política pública y política extraparlamentaria. No se reduce al Congreso de los Diputados, al Senado, a votaciones, a legisladores, a un partido ni a un único tipo de acontecimiento.

## 2. Alcance sustantivo y temporal

El universo representable es el conjunto de **actores y procesos políticos públicos documentables de España**, incluidos, según fuentes lícitas y calidad probatoria:

- Personas con función o actividad política pública verificable, tanto parlamentarias como extraparlamentarias; trayectorias, mandatos, cargos, roles, candidaturas y relaciones fechadas.
- Partidos, federaciones, coaliciones, agrupaciones electorales, candidaturas, gobiernos, grupos parlamentarios y organizaciones políticamente activas (plataformas, sindicatos, movimientos, grupos de interés y otras organizaciones cuando haya hechos públicos pertinentes).
- Instituciones y administraciones estatales, autonómicas, provinciales, insulares y locales; distintos poderes y organismos públicos, sin equiparar su naturaleza institucional.
- Elecciones, programas, campañas, representación, nombramientos, iniciativas, comparecencias, debates, preguntas, decisiones, votaciones, reglamentos, disposiciones y actividad ejecutiva.
- **Políticas públicas en sentido amplio:** agenda y problemas públicos, formulación, compromisos, decisión, normativa, instrumentos, presupuestos, ejecución, resultados y evaluación. Las fases son una ontología analítica revisable, no una atribución causal automática de impactos a actores.
- Territorio, calendario, acontecimientos externos y cambios de régimen institucional, cuando sean necesarios para interpretar tendencias y mecanismos.

**Profundidad histórica:** recuperar progresivamente todos los originales españoles pertinentes y jurídicamente reutilizables que permitan construir series longitudinales; registrar año inicial y final, instituciones, unidades, versión, cambios metodológicos, completitud y lagunas por cada familia de fuente. «Todo lo posible» es una estrategia de cobertura y trazabilidad; no una afirmación de exhaustividad ni un compromiso de terminar todos los periodos en el TFM.

La existencia de una persona, organización, intervención o política no se infiere de que aparezca en una única fuente. Ausencia de registro no es ausencia de actividad; candidatura no equivale a militancia, afiliación ni cargo; y observación de un acto no prueba influencia causal.

## 3. Arquitectura científico-informacional prioritaria

**Fuentes y originales → raw/bronze → identidades, relaciones y eventos versionados (silver) → vistas analíticas con corte temporal (gold) → modelos y evaluaciones → análisis, simulación y aplicaciones PFL.**

Los contratos deberán distinguir al menos:

1. Fuente: institución emisora, URI original, recurso y condiciones de reutilización verificadas, captura, versión, checksum, parser, advertencias y revisiones.
2. Entidad: identificador interno estable, tipo, identificadores externos con jurisdicción y periodo, cambios de nombre, homónimos y ambigüedades no resueltas.
3. Relación y rol: sujeto, objeto, papel explícito, institución, intervalo de vigencia, evidencia original; sin deducciones no documentadas.
4. Evento: clase, trámite/expediente, participantes y sus funciones, lugar/jurisdicción, fecha efectiva, fecha de publicación conocida, revisión y origen.
5. Política pública: iniciativa, instrumento normativo/administrativo, ámbito, fases observadas, decisiones, asignaciones presupuestarias, ejecución, productos, resultados, indicadores y conexiones **trazadas**; «resultado asociado» no es efecto causal atribuido.
6. Tiempo y cobertura: separación entre tiempo de vigencia, acontecimiento, publicación, adquisición y procesamiento; datos disponibles en cada corte as-of, población elegible, oportunidades, censura, selección, campos ausentes y cambios de definición.
7. Resultado analítico: población, unidad, estimando, código, conjunto de datos, versión, intervalo, supuestos, comparación, incertidumbre, limitaciones y evidencia de reproducción.
8. Resultado lúdico: reglas y versión, acontecimiento documentado, cálculo de puntos como **convención de juego**, liquidación y auditoría, sin convertir puntos en juicios sobre el mérito real de una persona.

La base histórica debe concebirse desde el principio como **multinivel, relacional, temporal y con procedencia explícita**, no como un único fichero de diputados, partidos o elecciones. No se instalarán tecnologías por prestigio o escala hipotética; se justificará su incorporación por necesidades observables.

## 4. Cuatro niveles de afirmación que no se pueden mezclar

**Hecho/documento:** un dato o acto recogido en una fuente identificada, con límites de cobertura y exactitud.

**Inferencia analítica:** una estimación, clasificación o relación inferida mediante reglas y modelos, explícitamente marcada como tal.

**Predicción:** distribución de acontecimientos observables futuros realizada con información disponible al corte y evaluada fuera de muestra; puede fracasar.

**Simulación:** evolución de estados y agentes según reglas y parámetros explícitos, con validación cuando exista evidencia suficiente. No es un pronóstico validado por defecto ni prueba de causalidad.

**Puntos fantasy:** convención pública y versionada de una aplicación, distinta de actividad política, influencia, efectividad, virtud, reputación o calidad democrática.

Ningún resultado de una simulación sintética ni prueba unitaria se promocionará a confirmación empírica de la política española. Un modelo más complejo solo se incorpora cuando demuestra valor incremental frente a rivales competentes bajo igualdad informativa, con incertidumbre y resultados negativos documentados.

## 5. Agenda científica: investigación y simulación con significado

PFL debe generar preguntas de ciencia de datos sociales **que se deriven de la estructura y las fuentes reales españolas**: evolución de redes institucionales, actividad de distintos roles y órganos, secuencias de políticas públicas, relaciones entre acontecimientos, información predictiva del calendario y trayectorias, asimetrías de exposición y cobertura, regímenes territoriales, institucionales e históricos.

Los objetivos predictivos concretos, estimandos, unidades y ventanas temporales se fijan **después** de auditar un corpus español viable, y **antes** de analizar los outcomes reservados. Se requiere baseline competente, separación temporal, controles de información futura y análisis de sensibilidad. No se preselecciona una técnica («redes», «LLM», «agentes», «deep learning») como respuesta a una pregunta todavía no operacionalizada.

La simulación social puede explorar mecanismos institucionales, incentivos, cooperación, competencia, decisiones y escenarios, pero debe discriminar lo que fue estimado con observaciones reales de lo que son supuestos hipotéticos. Los escenarios contrafactuales no acreditan efectos causales por sí mismos.

La ciencia de datos debe aportar algo verificable al producto: mejor acceso y consulta a datos históricos, pronósticos comparados, modelos interpretables, mecanismos sometidos a contrastes o nuevas formas de exploración de procesos sociales.

## 6. Aplicaciones del núcleo

**Observatorio español:** consulta histórica y contextual de personas de rol público, partidos, gobiernos, instituciones, decisiones, procesos y políticas, con fichas de evidencia, intervalos de vigencia y cobertura.

**Laboratorio científico:** reconstrucción de conjuntos analíticos, visualizaciones, comparaciones de modelos, redes temporales y simulaciones parametrizadas, con condiciones de reproducción.

**Politics Fantasy League (juego):** competición estratégica con un universo político español **real como referente**, mercado/equipos/jornadas/temporadas, persistencia y reglas transparentes. Su puntuación se define por eventos verificables y mecánicas aceptadas; los límites éticos, jurídicos y de fuente se superan mediante verificación real, **no** eliminando las barreras de seguridad del código. La demo sintética sigue siendo útil como fixture de QA mientras no exista admisión de hechos reales.

En la evolución futura podrían aparecer otras aplicaciones, pero ninguna debe desplazar la infraestructura científica como propósito principal.

## 7. TFM DaSoc 2026–27: relación entre ambición y entregable defendible

El **TFM es PFL**, entendido como sistema científico-computacional con resultados y artefactos, no una investigación distinta que menciona el juego al final. La prioridad del trabajo académico será una integración histórica española real y delimitada, un modelo analítico o predictivo formalmente evaluado, una simulación justificada cuando los datos la permitan, y al menos una aplicación funcional que dependa de ese núcleo.

La arquitectura persigue una cobertura nacional y multiescala a largo plazo, pero las **300 horas académicas de referencia** obligan a demostrar rigor en un subconjunto operacionalizado, sin prometer una ingesta total de toda la política española durante el TFM. Una serie limitada pero fiable, comparadores fuertes y resultados honestos valen más que cientos de fuentes sin reconciliar.

Se orientará la memoria al máximo rigor: teoría sociológica y politológica, estado de la cuestión, preguntas e hipótesis falsables, datos y licencias, limpieza, construcción de variables, modelos rivales, validación temporal y adversarial, resultados, impacto, límites y reproducibilidad. Registrar desde el comienzo las contribuciones y usos de IA generativa para atender las exigencias de transparencia académica. El objetivo personal de calificación no equivale a reconocimiento automático ni a evidencia científica.

**Normativa y tutoría:** verificar la convocatoria 2026–27 y los requisitos con coordinación/PRADO y tutores; no dar por vigentes las fechas de material 2025–26 que aún se muestra en Studium. La elección de tutor, la modalidad y la aceptación del tema no están certificadas en este documento público.

## 8. Lo que NO debe repetirse

- **No** sustituir España por peticiones británicas o francesas, una institución extranjera o un único proceso auxiliar como foco del juego y del TFM. Sus experimentos, positivos o negativos, se conservan como investigación secundaria y referencias metodológicas, sin borrarlos ni reetiquetarlos.
- **No** convertir la demostración de diez figuras ficticias, los bots o cualquier diseño de demo en decisión definitiva del universo político de PFL.
- **No** presentar el TFM como «desarrollo de un videojuego» sin contribución sustantiva de datos y metodología. El videojuego es un caso de uso del trabajo científico central.
- **No** reducir «toda la política española» a Congreso, diputados, grupos parlamentarios o resultados electorales. Es lícito comenzar por uno para validar el pipeline; no declararlo alcance final del proyecto.
- **No** confundir potencial histórico con corpus ya importado; fuentes indexadas con licencia autorizada; pruebas sintéticas con validación independiente; asociación con causalidad; o una puntuación convencional con evaluación moral/política.
- **No** afirmar nuevas autorizaciones AB-H, fusiones, instalación, permiso legal, acceso a fuentes, calidad predictiva o avance de P1/P2 por publicar esta visión.

## 9. Estado heredado y relación con la gobernanza existente

Esta declaración es un **contrato de intención del usuario**, no un nuevo marcador de progreso. Se conservan los ledgers de AB Atlas, los contratos A–J, preregistro, controles competentes y R5; **AB-R científico y AB-P producto permanecen separados**. El alcance y la madurez se leen de PROJECT_STATE.json, METHOD_REFERENCE.json y sus recibos, no se alteran retrospectivamente.

El diseño actual cuenta con ontologías y contratos multiactor españoles y una demo jugable sintética, pero no con una ingesta histórica nacional completa ni con todos los gates de puntuación nominal resueltos. Las PR #3 y #4 siguen sujetas a revisión y a su dependencia técnica, sin integrarse automáticamente. Ni el desarrollo del producto ni las campañas extranjeras autorizan puntuación pública de personas reales ni lanzamiento antes de acreditar los controles correspondientes.

Como fuentes de interpretación complementarias, consultar:
- docs/ARQUITECTURA.md — distinción ontológica entre hechos, inferencias, predicciones y juego.
- docs/UNIVERSO_ACTORES_POLITICOS_20261025.md — universo político multiactor y fuentes.
- docs/INGESTA_ALTO_VOLUMEN.md — cadena de procedencia y cobertura.
- product/progress_scope_v4_20261027.json — contrato de cobertura/madurez, no evidencia de completitud.
- docs/PLAN_TFM.md — **borrador de opciones científicas**, no autoridad para reducir el proyecto a un estudio parlamentario con fantasy accesorio.
- START_HERE.md, AGENTS.md, PROJECT_STATE.json, BRANCHES.json, METHOD_REFERENCE.json — entrada, reglas, estado, ramas y método.

## 10. Orden de trabajo consecuente, propuesto y sujeto a evidencia

**Primer resultado material:** auditar un conjunto concreto de fuentes primarias españolas con cobertura histórica suficiente para demostrar un pipeline extremo a extremo de adquisición legal, identidad, eventos, temporalidad, datos longitudinales, baseline y una pregunta predictiva discriminante. Registrar lo que **no** se puede unir y las fuentes ausentes. Mantener el inventario de cobertura de otros subsistemas para extenderse hacia ellos sin fragmentación.

**Segundo resultado material:** vincular el primer corpus admitido al observatorio y a un módulo aplicable a PFL; completar por separado las puertas del producto, de identidad/privacidad/precisión y del sistema científico. Una mecánica de juego real solo se declara disponible tras acreditar fuentes, derechos y comportamiento probado.

**Tercer resultado material:** construir y defender el caso de TFM sobre los resultados efectivamente validados, reservando horas suficientes para memoria, discusión crítica y defensa; mantener el desarrollo del proyecto completo como plan posterior.

No abrir más campañas o desarrollar sistemas de agentes por inercia: elegir trabajo por su valor informativo, por la reducción de bloqueos reales y por su capacidad de producir un artefacto verificable.

## 11. Mandato de continuidad para próximos chats/agentes

**Antes de programar, investigar o sugerir prioridades:** leer este documento junto con START_HERE.md, AGENTS.md, PROJECT_STATE.json y el método AB referenciado. Interpretar las últimas conversaciones, propuestas de arquitecturas británicas o francesas y demos sintéticas a la luz de este objetivo explícito. Si un proyecto propuesto convierte la política española real en un mundo ficticio o toma una fuente extranjera auxiliar como corazón de PFL, **marcarlo como deriva y no ejecutarlo como decisión del promotor**.

Aclarar cualquier decisión verdaderamente abierta (unidad predictiva, presupuesto de cobertura, primer proceso, tutor o modalidad), sin rellenarla con una asunción. Conservar trazabilidad de lo realizado, límites, saldos, pruebas, bloqueos y diferencias entre realidad, hipótesis, simulación y puntuación.

**Precedencia:** una nueva instrucción explícita del usuario puede revisar esta visión; hasta entonces no confundir una selección local de investigación con cambio de propósito del proyecto.
