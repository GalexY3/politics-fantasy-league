# PFL · ABH30-C12 — Evidencia independiente de laboratorio sobre incentivos, feedback ordinal y errores de medición

**29/10/2026 · AB-R documental, DRIFT D2 · C12 válido LIMITADO a verificación de documentación primaria externa.** Rama `research/pfl-abh30-c12-independent-rank-rct-20261029` desde PR #62. Este ciclo no procesa microdatos, no reproduce el estimando humano original ni representa validación causal de PFL.

## Resultado principal

Se identificó un estudio experimental independiente y directamente relacionado con la tesis de juego de pronósticos con incentivos y feedback social: **Debmalya Mandal, Goran Radanović, David C. Parkes (2020), “The Effectiveness of Peer Prediction in Long-Term Forecasting”, AAAI, DOI [10.1609/aaai.v34i02.5591](https://doi.org/10.1609/aaai.v34i02.5591)**. Original experimental repo: [debmandal/PP-MTurk-AAAI2020](https://github.com/debmandal/PP-MTurk-AAAI2020) commit **`a5ac7fcc0eec4325f603f0de9085e3021def9830`**. Se comprobaron contra GitHub los blobs **README `d4197dbdb69b6934b6ad565cfe070ae9009ee046`** y **`src/analysis.Rmd` `9ec6e3cd0cdc10bc7cbf1a590c643a01575ef07c`**. El preregistro de las discriminaciones documentales se guardó **antes de inspeccionar el Rmd completo**, commit [`eec8c9ce4bdc847c6b30f8527a5e14d0cc55cd68`](https://github.com/GalexY3/Metodologia-AB/commit/eec8c9ce4bdc847c6b30f8527a5e14d0cc55cd68). Se **declara explícitamente piloto pre-prereg**: antes de congelar ya se había leído el abstract, README, Rmd inicial y el campo licencia nulo. Estos hechos no se contabilizan como hallazgo ciego.

El artículo y README describen asignación aleatoria a **cuatro condiciones**: (1) regla Brier y recompensa diferida (SR); (2) pagos inmediatos por peer prediction (PP); (3) Brier diferido + **cuartil privado diario de puntuación por pares** (SR+PPRank); (4) Brier diferido + pagos adicionales diarios por peer prediction (SR+PP). No equivale a manipulación independiente de **leaderboard público social**: la condición 3 informa del cuartil, sin evidencia de mostrar identidad/posición de todos los jugadores. Duración 7–13 octubre **2018**, **18** preguntas (6 deportes, 6 política/economía, 6 entretenimiento). El paper indica 1400 trabajadores reclutados, 945 incorporados al HIT de pronóstico, y **891 analizados por estar presentes toda la semana**: SR 207, PP 220, SR+PPRank 238, SR+PP 226. No se verifica aquí la variación de la tasa de exclusión por brazo ni la entrega individual del estímulo.

**Resultado científico external publicado, no nuestro:** los autores informan que el feedback diario por pares aumenta la participación y que SR y SR+PPRank rinden bien en precisión agregada para determinadas particiones; ese hallazgo supone **antecedente contrario a reivindicar como originalmente novedoso el mecanismo general «feedback comparativo eleva engagement»**. Se necesita nueva predicción diferencial PFL, p. ej. **cuartil privado** frente a **ranking social visible** frente a **feedback individual no comparativo**, manteniendo el mismo scoring Brier, información, oportunidades y economía virtual. Sin datos humanos de PFL, este antecedente es **prior art y apoyo de plausibilidad** pero no validación externa del simulador.

## Hallazgo adversarial de código original (post hoc, impacto real sin comprobar)

La auditoría estática del **Rmd de los autores** (`src/analysis.Rmd`, 1169 líneas, Git blob verificado) detectó:

1. **Error de indexación de actualizaciones 13/oct:** en línea **222**, `Updates13$updates` invoca `CountUpdates` con `var2 = 5`, mientras la rama **5** de la función en líneas **183–186** compara los registros acumulados del **11→12**, y la rama **6** de líneas **188–192** compara **12→13**. Los seis argumentos de llamada para 8→13 son **[1,2,3,4,5,5]**, frente a [1,2,3,4,5,6] esperados para días sucesivos. Contraejemplo sintético, sin datos humanos: acumulados 11=2, 12=4, 13=7 ⇒ código etiquetado «13/oct» devuelve **4−2=2**, incremento específico del 13/oct **7−4=3**. Se verifica el error de selección **del código**, NO el tamaño/signo del sesgo de las estimaciones del artículo.
2. **Último día ausente en otra medida:** la sección `Change.oct <- rbind(...)` de líneas **313–316** termina en **Change12** y no incluye **Change13**, pese a que este dataframe sí se genera en línea 302. Las asignaciones `avg_change` terminan en Change12 (líneas 306–310). Esto afecta el *script documentado*, sin demostrar qué figuras o tablas finales usan realmente esa rama. **R no está instalado y el script original no se ha ejecutado sobre datos reales**.

Los errores, descubiertos **después** de congelar el objetivo documental C12, se clasifican **POST_HOC_SOURCE_CODE_AUDIT**, sin consumir ciclos extra y sin reivindicación confirmatoria. La fuente primaria permanece intacta; no se ha comunicado a autores ni reescrito resultados externos.

## Licencia y derechos

El repo de los autores es público, pero GitHub devuelve **`license:null`** y no tiene fichero LICENSE en su raíz. El README declara que `data/workers.csv` contiene identificadores de trabajadores de MTurk y `answers-oct*.csv` contiene pronósticos por trabajador/tarea. **No hemos descargado, inspeccionado ni almacenado ningún CSV de participantes** ni aceptado términos. No deducir que visibilidad pública concede licencia para procesar información individual. No está acreditada la presencia de logs de **exposición entregada** aparte de asignación, pronósticos y feedback computado; su ausencia en los documentos inspeccionados no prueba inexistencia.

## Contrato A–J ejecutado

**A.** Estimando de este ciclo: existencia de un contraste experimental humano publicado, con tratamientos distinguibles y resultados operativos, y suficiencia de documentación técnica para transferir un prior a PFL. No efecto causal estimado por nosotros.

**B.** H1: ensayo real de cuatro incentivos que distingue rank ordinal vs feedback monetario y mide compromiso y precisión; H0: sin exposición/intervención original. Rivales: estímulo cuartil ≠ ranking social, población MTurk ≠ PFL y selección postratamiento; cambios de pagos y señales pueden estar confundidos.

**C.** Antes de examinar Rmd completo se fijaron SHA de original README/Rmd, el estudio y las preguntas de auditoría; se reveló el material de piloto ya visto antes de ese freeze. Comparador competente: regla Brier retardada y PP no monetario vs PP monetario.

**D.** Instrumento: estudio primario y scripts originales Rmd/README en commit fijo, Git blob verificado. Sin crear código propio de inferencia causal. El análisis estático ejecutado en V8 mapeó los seis selectores del Rmd y confirmó un único desacople de día (línea 222). No se ejecutó el programa R original.

**E.** Documentación contrastada: diseño 4 brazos, 891 analizados, endpoints longitudinales, Git metadata, presencia de IDs y `license:null`; dos anomalías Rmd etiquetadas post hoc. [Recibo estructurado](C12_RUN_RECEIPT.json).

**F.** Análisis adversarial: selección 945→891 puede causar attrition/survivor conditioning; no afirmar sesgo efectivo sin attrition por brazo; rango ordinal entregado ≠ clasificación pública con identidades; endpoints de engagement, exactitud y diferencias de señal monetaria no se colapsan. Dos errores de script no invalidan automáticamente el artículo.

**G.** Publicación AAAI previa e independiente de ForecastBench y PFL; no es réplica de Politics Fantasy, ni evidencia del comportamiento de agentes simulados, ni licencia humana validada.

**H.** Nuevos priors PF-BR50 (prior art experimental cuartil vs ranking, estado fuente externa) y PF-BR51 (alerta de instrumentación longitudinal / script original verificada, impacto no estimado). No se elevan hallazgos PFL a nivel 1/3.

**I.** **C12 AB-R válido limitado a auditoría documental primaria**. Ciencia PFL **0/3**, CT2 científica **20/100 ordinal** sin crecimiento, N1/N2/N3 nuevos 0/0/0, launch gates 0/6. El dataset individual no se ha procesado.

**J.** Contar **un** nuevo ciclo C12 de 30, **12/30 completos, 18 nuevos pendientes**, dos históricas separadas STOP_R5. **Pivot sustantivo próximo:** comparación factorial PFL en pilotos **ficticios** y/o búsqueda de microdatos verdaderamente autorizados con exposición real; nunca usar la etiqueta científica «original» para reproducir solo una tesis publicada.

