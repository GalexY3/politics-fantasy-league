# Politics Fantasy League — PF-AB30-FULL, 30 ciclos A–J reales de trabajo

**Fecha:** 25 de octubre de 2026. **Tipo de ejecución:** 18 auditorías descriptivas retrospectivas de archivos reales seleccionados + 12 experimentos metodológicos condicionados a un generador simulado. **No** son 30 experimentos de campo independientes, ni 30 hallazgos sociológicos sobre la población parlamentaria. El A–J de cada ciclo está en `C01.json` … `C30.json` y agrupado en `LEDGER.json`. El primer requisito del usuario («bucles completos AB») se implementa con las diez secciones en cada ficha, más resultados y controles. El tipo real del ciclo importa más que completar una cifra.

## 1. Integridad preregistrada y procedencia

- Metodología: AB 3.2.1, O1–O6 (Repositorio `GalexY3/Metodologia-AB`). Preregistro publicado **antes de ejecutar**: `3bfd2815cf3baf2eabe77830fd2e9a750aafe10f`. Archivo de código + cuentas agregadas anónimas congelados **antes de ejecutar**: `d08a90bae7cb2176b137a3e15b547ec3482303b6`. El ciclo A–C era inevitablemente **post hoc**: ya se habían inspeccionado los siete casos al redactar el diseño. Los ciclos sintéticos se ejecutaron después del commit de congelación, pero su mecanismo es impuesto.
- Fuente secundaria real: `https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/congreso/votaciones.json`, objeto Git `ecaf3b02b9a453265d6bcb588a9121ddaae9ed78`, marca publicada de generación `2026-10-05T13:47:46.103Z`. **Solo siete votaciones escogidas por temas**, no muestra aleatoria ni los ~2.175 votos de la web. Anonimización: en nuestro árbol publicamos totales de cuatro categorías, listas por grupo y *histogramas* del objeto `votos`, **no nombres ni códigos nominales**.
- Segundo insumo: 20 filas de **recuento agregado transcrito manualmente** desde página Congreso para una **sola sesión** (23 de julio de 2026) en `data/pilot_official_webview/20260723_vote_totals_MANUAL.csv`. Sin cotejo del JSON nominal oficial y **sin** independientes cross-source apareados por votación. Los contrastes C13–C18 son descripciones, no inferencia causal temporal.
- El recuento numérico anónimo tiene SHA-256 en `RESULTS.json`. Los datos originales permanecen en el repositorio del proveedor con su propia licencia/atribución. La verificación de 42 casos se reprodujo con un **segundo algoritmo de agregación** sobre el mismo archivo, no con una fuente independiente.

## 2. Resultado observacional principal, C01–C06

Las **siete votaciones** tienen totales declarados de **350** y las sumas de nueve grupos coinciden con esos totales (7/7). Sin embargo, el diccionario nominal público incluye **346, 350, 346, 346, 346, 342 y 332** entradas respectivamente: en **6/7** quedan huecos (4, 0, 4, 4, 4, 8 y 18), **42 posiciones** al sumar las siete votaciones (no 42 personas únicas). Descomposición respecto de los totales: **21 Sí, 16 No, 0 Abstenciones, 5 No vota**. Los valores explícitos «No vota» ascienden a **26**, por lo que no pueden identificarse con los 42 huecos. Estas diferencias son características del fichero secundario seleccionado, **no errores certificados del Congreso**. Una hipótesis rival plausible es que el diccionario de diputados utilizado para indexar los votos no cubra históricamente todos los miembros; se necesita reproducir la votación nominal oficial y las altas/bajas para verificarla.

En los 63 pares grupo-voto con opción expresada, **55** aparecen unánimes, pero NO inferimos disciplina partidista de un resultado seleccionado y ecológico. El grupo Mixto no representa una unidad programática uniforme. La agregación e indicadores pueden haber sido derivados de los mismos datos subyacentes (no corroboración independiente).

## 3. Resultado de medición C07–C12

La definición de tasa **Sí entre expresados** vs **Sí entre 350** altera el indicador (diferencia media **0,47 puntos porcentuales** en estos siete casos). Incluir abstención al medir margen reduce el margen de la iniciativa que registra 127 abstenciones de **0,598** (Sí-No solamente) a **0,379** (tres categorías expresadas). La diferencia media de concentración modal grupo-vs-pleno es **0,472**, efecto aritmético potencialmente derivado de agregación por bloques; no demuestra causalidad institucional. Al retirar una sola votación, la media de Sí/350 varía sobre una amplitud de **6,38 puntos porcentuales**: selección elevada para n=7.

**Errata conservada C05:** la clave inicial `spearman_approx_corr=-0.828510` calculaba **Pearson con rango cronológico**; el rho de Spearman verdadero con empates es **-0.906327**. Se conserva el original, corrección explícita en `C05_ERRATA.json`. Por tanto la afirmación de Spearman de C05 original es **INVALID**. Ninguno de los dos estadísticos autoriza afirmar tendencia institucional: muestra seleccionada, n=7.

## 4. Triangulación exploratoria C13–C18

La media de categorías agregadas es **350** en la fuente seleccionada y **347,45** en la transcripción del día concreto, pero no son la misma unidad operacional porque este segundo archivo omite la categoría No vota. Es una comparación **no emparejada y parcialmente incompatible**. Las respectivas medias observadas de proporción Sí entre expresados son **0,446** y **0,652**; **no** se atribuye la diferencia a evolución temporal ni a cambios de políticos: selección temática, día y instrumento difieren. Los 20 recuentos de la segunda tabla pertenecen a **una sola sesión**, no a 20 sesiones independientes. Por tanto se rechaza tratar el total 27 como 27 observaciones aleatorias independientes de legislaturas.

## 5. Experimentos de mecanismo D/E, C19–C30

Todos son cálculos reproducibles de **600 realizaciones independientes del mismo generador artificial** por ciclo, con bootstrap de medias pareadas (500 réplicas); no son replicación de campo. La medida Δ es pérdida(error baseline) − pérdida(error alternativa); positivo favorece la alternativa, excepto donde Δ representa una diferencia de índices/sesgos/SE, especificada en cada JSON.

| Ciclo | Lectura del estimando sintético | Resultado condicionado |
|---|---|---|
| C19 | IPW constante con datos MCAR vs media observada | Δ = 0 exacto: tratamiento equivalente |
| C20 | Propensión MCAR mal aplicada a MNAR | sesgo medio de la tasa observada = −0,223; Δ = 0 |
| C21 | Denominador implícito 350 en respuesta parcial | ventaja de tasa sobre respondentes en error absoluto = +0,082 |
| C22 | Grupos actuales vs grupo histórico correcto | error de etiquetar retrospectivamente = +0,161 |
| C23 | Disponibilidad del agregado completo (más información) | ventaja aparente = +0,015 **no atribuible al modelo** |
| C24 | Concentración aparente en grupos n=5 vs n=130 | diferencia media = +0,157 por tamaño finito |
| C25 | Efecto de agrupar por sesión | cobertura IC ingenuo 34%; cobertura IC agrupado 95% (generador concreto) |
| C26 | Predicción con información del futuro | ventaja engañosa por target leakage = +0,459 |
| C27 | Baseline de grupo vs global con diferencias estables | mejora logloss grupo = +0,046 |
| C28 | Mismo contraste bajo estructura de grupo nula | Δ = −0,0046, modelo complejo pierde |
| C29 | Mismo contraste bajo inversión de estructura | Δ = −0,156, grupo pierde sustancialmente |
| C30 | 20 hipótesis nulas y corrección Bonferroni | FWER sin ajuste 66,17%; con Bonferroni 5,17% |

**Controles adversariales:** C19/C20 dan mejora exactamente nula, lo que descarta una victoria artificial del ajuste al no existir información discriminante. C28/C29 muestran pérdida del modelo más granular bajo nulo y cambio de régimen. C23/C26 son **ejemplos intencionados de desigualdad informativa**: no respaldan superioridad modelística. C25 demuestra, dentro del simulador, el problema de tratar miles de filas nominales como sesiones independientes. Un generador diferente podría cambiar magnitudes y signos; el diseño usa una sola familia de generadores y no contiene evidencia exterior de los mecanismos reales.

## 6. Estado de prueba, alcance y decisión AB

- Reproducción sintética fija del diseño con semilla y hashes; **152 pruebas de regresión** pasan en la revisión local. Las pruebas comprueban invariantes y resultados preregistrados, **no** convierten la muestra seleccionada en panel parlamentario completo.
- `G`: **ninguno de los 30** tiene confirmación empírica independiente. Para los ciclos sintéticos, sus 600 semillas solo replican **dentro del mismo generador**. C05 queda **INVALID para la etiqueta Spearman original**, con errata explícita; la correlación válida se estima separadamente. Grado original AB 2/3 = 0, nivel de valor VSDS = **1/3** por instrumentación y observación de la fuente secundaria, a la espera de corroboración oficial.
- `CT2` rama predictiva permanece **24/100**, ordinal no probabilidad. Variar semillas, commits o tests no justifica un aumento.
- **AB-DECIDE global: REPAIR_SOURCE / STOP_SYNTHETIC_EXPANSION**. Obtener **archivo nominal oficial de esas siete votaciones**, comprobar 42 entradas y miembros históricos, descargar toda la población elegible XV con marcas de primera publicación, y habilitar validación temporal real con baselines. El estudio muestra por qué **no** deben usarse todavía registros nominales de la plataforma para adjudicar puntos o afirmar cohesión causal. No hay hallazgos 2/3 confirmados.

## 7. Gobernanza de saldos y entrega

30 nuevos ciclos A–J terminados como auditoría retrospectiva o experimento metodológico; **0 experimentos confirmatorios sobre población parlamentaria real**, **0 hallazgos científicos 2/3**. Los saldos previos (12 B50, 45 libres, 19 AB20) **no se consumen**. Proyecto publicable temporalmente solo en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`, migración futura obligatoria a `GalexY3/polictics_fantasy_league`.

**Solicitud futura motivada:** 30 ciclos con BRANCHING condicional a obtener otra clase de evidencia real, orientados a validación cruzada oficial, reconstrucción de elegibilidad histórica y producto social de observatorio; si persiste bloqueo de acceso, orientarlos a interfaces de adquisición, exportación y auditoría, sin multiplicar este mismo generador.

**SOLICITO BRANCHING 30 CICLOS**
