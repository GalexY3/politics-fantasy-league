# Politics Fantasy League · BRANCHING AB-H, continuación desde PR #49 (29/10/2026)

**Base verificada:** PR #49 abierta, head `6bbd306a7b336ab60dfe5407eeb8b832d32b0a05`; rama nueva `research/pfl-abh5b-c03-randomized-leaderboard-20261029`. **Autorización:** un bloque nuevo de 5 AB-H; C01/C02 ya ejecutados en PR #49; esta continuación ejecuta **solo C03**. Las 2 plazas AB-H históricas permanecen separadas y bloqueadas por STOP_R5.

**Cierre provisional de la campaña:** C01, C02 y C03 **3/5 válidos de alcance limitado**, los tres AB-R reanálisis de agregados publicados; **C04/C05 permanecen sin ejecutar**, dos plazas autorizadas nuevas libres. Los históricos siguen **2 sin gastar**. No hay estudio causal propio sobre participantes de PFL. CT2 prospectiva científica **22→20/100**, ordinal, no probabilidad; descenso justificado por fuerte antecedente original de aleatorización directa y estudio factorial de 8 brazos en el mismo mecanismo. **N1/N2/N3 nuevos 0/0/0**, gates producto 0/6. No se descargaron datos individuales ni se activó CI.

## Hallazgo adversarial más importante: hay que separar cuatro preguntas

1. **Z (oferta/asignación)**: que un usuario sea aleatorizado al brazo donde habrá leaderboard. En Kloc, Belo y Li (manuscrito octubre 2024) esto sucede al registrarse, con probabilidad 2/3 frente a un control 1/3.
2. **E (exposición efectiva)**: que un usuario sea elegible y reciba la clasificación. La asignación real de sala se realiza tres o más días después, si mantiene actividad. El ensayo analiza **3.762 usuarios elegibles**, no un padrón verificado de todos los registros iniciales; por tanto el resultado no se generaliza sin más a todos los recién llegados.
3. **G (composición del grupo de rivales)**: estar clasificado junto a usuarios con actividad inicial similar o distinta es una manipulación aleatorizada de diseño distinta de Z. El efecto de composición debe contrastarse por la **asignación original** al tipo de sala, conservando el estimando.
4. **R (ranking y distancia observados)**: la distancia de puntos entre rivales, posición en cada fecha o dispersión actual depende de la actividad e historia postasignación. **Una regresión de Y sobre R dentro de los tratados no identifica automáticamente el efecto causal de R**, aunque se controle por posición, porque puede permanecer confusión dependiente del tiempo. El signo positivo publicado para dispersión 0.092 (SE 0.012) es una asociación condicionada; no contradice directamente el contraste aleatorizado de oferta cercano a cero.

Se distingue además **Y (engagement)**: asistencia diaria, tiempo, aprendizaje, práctica o tiempo en materia difícil; y **S (pertenencia al riesgo)**: un usuario activo al tercer día, una persona que llegó a ver el tratamiento o una persona que respondió pueden representar diferentes poblaciones. Un número de filas usuario×día NO equivale al número de participantes y no puede presentarse como N individual.

## C03 completo A–J: confrontación de cinco métricas y multiplicidad

**A — Pregunta:** ¿cuán estricta es la lectura «el leaderboard no aumentó la actividad» cuando se debe distinguir una métrica elegida individualmente de cinco métricas publicadas simultáneas, y cuáles son los límites de identificación?

**B — Rivales:** (H1) el límite normal del 95 % para tiempo activo por sí solo excluye un aumento superior a un umbral ilustrativo de 0,05 desviaciones típicas, pero una familia conservadora Bonferroni de cinco métricas ya no lo excluye. (H0) ambos intervalos dan la misma decisión. Rival fuerte: este **umbral 0,05 fue elegido después de leer la fuente** y NO es un mínimo relevante validado ni preregistro previo de los autores; tratarlo solo como sensibilidad exploratoria, no prueba confirmatoria de equivalencia.

**C — Fuente original:** Agnieszka Kloc, Rodrigo Belo y Ting Li, *Climbing the Ladder or Falling Behind: The Role of Leaderboard Composition in User Engagement*, [PDF original de los autores (octubre 2024)](https://rodrigobelo.com/assets/pdf/leaderboards.pdf), páginas 9–10 diseño y 16 tabla 3. No se ha verificado publicación final revisada por pares ni disponibilidad de microdatos. Experimento sobre estudiantes de preparación de exámenes de Países Bajos en 2022, con panel de 3.762 usuarios elegibles y 108.171 filas usuario-día para cuatro outcomes, 79.956 para materia difícil. La tabla 3 reporta estimaciones (β, SE): login (0,008;0,006), tiempo activo estandarizado (0,009;0,016), aprendizaje (0,008;0,014), práctica (0,002;0,020), materia difícil (0,007;0,015). SE agrupado a nivel persona. La mera significancia de los coeficientes en la tabla no ofrece una declaración de equivalencia.

**D — Diseño e instrumentación congelados antes de ejecutar:** [contrato A–J](C03_PREREG_AJ.json), commit `db06458f74dc77c6990971d58ff4486431d07c0b`. Código `kloc_aggregate_ci.py`, Git blob `4ccf4b5721dcdd5088e496f1d8ed682fd00bea6f`, SHA256 `269691294827cae3bf37438963a92d802b91599c73c511a1e8354f81feb64888`. Ocho pruebas `test_kloc_aggregate_ci.py`, blob `19e72edd55411ae914c9dc600e444face3c005bd`, SHA256 `18e4d39c843b0f06339193b77d2c5f3d90ad1710f0937e458199a995b8996c07`. **Coincidencia Git SHA de código local y remoto verificada antes del freeze**, sin cambios posteriores.

**E — Ejecutado de verdad:** Python estándar local, **8/8 tests PASS, exit 0**, código fuente exit 0. El tiempo activo tiene 95 % normal [−0,02235942, +0,04035942] SD y Bonferroni de cinco endpoints, confianza familiar 95 %, [−0,03221327, +0,05021327] SD. El umbral ilustrativo +0,05 SD queda **fuera** del intervalo individual pero **dentro** del simultáneo. Las cinco CI normales incluyen cero. [Recibo exacto](C03_RUN_RECEIPT.json).

**F — Auditoría adversarial:** falso asumir `108171` personas (son filas panel); falso equiparar ausencia de significación a efecto exactamente cero; falso universalizar 3.762 elegibles a todos los recién registrados; falso inferir causalidad del β dispersión de tabla 4 a partir de coeficiente posasignación; y falso usar el umbral postseleccionado como test de equivalencia prospectivo. Bonferroni puede ser conservador si outcomes correlacionan: no se dispone aquí de la covarianza conjunta ni se ha rehecho inferencia con registros personales.

**G — Replicación:** fuente editorial independiente de PFL; los números se han transcrito de una tabla directamente comprobada en el PDF. Se ejecutó análisis propio solo sobre **cinco β/SE publicados**, pero **NO se replicó la aleatorización de campo, su inferencia robusta ni se obtuvo un dataset de participantes**.

**H — Priors:** [PF-BR30](../ABH_BROWSER_ATLAS_EVIDENCE5_20261029/SOURCES_AND_PRIORS.json) registra que **existe ya un ensayo original de oferta de leaderboard versus ausencia**; PF-BR31 delimita el problema de familias de cinco endpoints y umbral ilustrativo. Un segundo ensayo directo distinto, Lovász et al. (2023), [DOI 10.1016/j.socec.2022.101954](https://doi.org/10.1016/j.socec.2022.101954), asignó **5.191 usuarios a ocho brazos**: leaderboard sí/no × apoyo, premio, crítica o ausencia de feedback. Esto es un **rival científico especialmente fuerte** con resultados de persistencia y rendimiento: no se considera nuevo hallazgo nuestro ni consume C04 solamente por registrar sus medias (PF-BR32).

**I — Dictamen:** C03 **AB-R de reanálisis cuantitativo agregado válido, alcance limitado, 0/3 científico**; no hay nuevo efecto causal descubierto. La CT2 prospectiva de PFL pasa ordinalmente de 22 a 20 porque nuestra aparente novedad mecanicista resulta más difícil de defender frente a pruebas directas publicadas, no porque se haya calibrado probabilidad alguna.

**J — Decisión:** conservar C03 y sus negativos, **STOP_R5** para C04–C05 mientras no haya una fuente o intervención con una predicción nueva que discrimine rival fuerte, derechos y diseño verificables.

## Por qué los dos siguientes no se abren

**C04**: la fuente de Lovász et al. tiene una aleatorización factorial directa y resultados publicados: copiar los ocho promedios o ejecutar una nueva identidad aritmética para contar otro ciclo es **repetición científicamente insuficiente**. Se necesitan datos auténticos de exposición o una propuesta de diseño verdaderamente novedosa, no otro contraste condicionado en participantes ya incorporados. El acceso ético y legal a filas individuales no se ha establecido.

**C05**: el mecanismo de «ranking vs feedback» y sus heterogeneidades ya estaba estudiado en Kloc y Lovász, además de Pickal/Palikot/Chen; una nueva simulación o simple prueba de esquema tendría novedad 0/3 y escaso valor marginal. **R5 detiene la apertura.** Ambas plazas **concedidas pero no consumidas**, no ciclos inválidos ejecutados.

Las **dos plazas históricas** para GJP y exposición de rankings siguen diferenciadas y sujetas a [sus propias puertas](../ABH_BRANCHING5_DYNAMIC_ROOM_20261029/LEGACY_R5_GATE.json). Ni CC0 ni localización de un repositorio autorizan automáticamente tratamiento de datos personales.

## Estado, recursos y decisiones

- Estado de 5 plazas **3 válidas limitadas (C01–C03), 2 pendientes (C04–C05)**; aparte 2 históricas intactas. Primera ejecución fallida de tests C01 anterior y reparación permanecen en el historial, no consumen una plaza adicional.
- [Gráfico CT2 completo y ampliado](CT2_FULL_AND_ZOOM.svg) y [ledger ordinal](CT2_TRAJECTORY.json): 22 → 20, motivación y confianza baja en este juicio. N1/N2/N3 = 0/0/0, release gates 0/6.
- Trabajo hecho en rama nueva y PR de borrador apilada sobre la #49; no `main`, ChatRelay ni CI costosa.
- Ningún registro de persona descargado, ninguna licencia aceptada ni autor contactado, ningún político real puntuado.
- Siguiente trabajo con sentido científico: *primero* localizar y auditar documentación no personal de procedimientos de asignación, denominadores, campo temporal y derechos de los datos experimentales de **Kloc/Lovász** o generar un ensayo propio con ética y objetivos longitudinales claros. *Solo después*, si cambia el estado de la evidencia, justificar A–J con un nuevo estimando.

**No solicitar nuevo bloque mientras queden dos plazas AB-H nuevas y dos históricas ya autorizadas; permitir continuidad con STOP_R5 sin forzar su gasto.**
