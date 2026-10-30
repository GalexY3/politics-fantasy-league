# Politics Fantasy League — nuevo BRANCHING AB-H de cinco plazas (29/10/2026)

**Estado de cierre:** de **5 ciclos nuevos explícitamente autorizados**, **2 AB-R de reanálisis de agregados publicados ejecutados y válidos de alcance limitado**, **2 investigaciones documentales solamente en planificación y 1 plaza no abierta**. Las **3 plazas nuevas sin consumir** continúan autorizadas; las **2 históricas** permanecen por separado y tampoco se consumieron. No se ha abierto un ciclo sólo para gastar presupuesto. Ningún estudio de personas se ha replicado a partir de datos individuales.

**Punto de partida:** PR #48, commit `08deb85b00db09429a78c37383127e5eb9c8060f`, rama sucesora `research/pfl-abh5-original-feedback-sensitivity-20261029`. Método AB3.2.1 O1–O7, A–J, DRIFT, STOP_R5 y actualización acumulativa de fuentes/priors en `../ABH_BROWSER_ATLAS_EVIDENCE5_20261029/SOURCES_AND_PRIORS.json`. **CT2 prospectiva científica 22/100 ordinal antes y después**. N1/N2/N3 nuevos **0/0/0**. Gates de lanzamiento **0/6**.

## C01 · AB-R de fuente humana original publicada, **sin microdatos**

**A — Pregunta:** ¿el contraste de interés/disfrute que Pickal et al. (2026) publica sobre casos con motivación es identificable para los 427 participantes de las cinco condiciones cuando no se dispone del reparto por brazo de las observaciones ausentes?

**B — Hipótesis rivales:** (H1) con 82 observaciones no representadas y escala 1–5, los extremos factibles permiten cambios de signo; (H0) toda distribución admisible conserva el signo positivo. Rival fuerte: las medias y ANOVA publicadas sobre casos disponibles pueden ser correctas y válidas para esa población; la inexistencia de un ITT completo sobre todos no demuestra que la publicación sea incorrecta. Una diferencia de denominadores **no identifica automáticamente abandono**, y el cálculo presupone un ANOVA de cinco grupos ordinario.

**C — Predicción y fuente original:** [Pickal, Stadler, Sailer y colaboradores, *The winner takes it all*, 2026, DOI 10.1016/j.lindif.2025.102836](https://doi.org/10.1016/j.lindif.2025.102836); [PDF original universitario CC BY 4.0](https://opus.bibliothek.uni-augsburg.de/opus4/files/127063/127063.pdf), pp. 5, 7, 9 y 10. Condiciones n=86 posición alta/subida, 81 alta/bajada, 75 baja/subida, 95 baja/bajada, 90 sin feedback; **n total=427**. El manuscrito informa F(4,422) para el rendimiento inicial (427 casos bajo ANOVA estándar) y F(4,340) para interés/competencia (345 casos bajo la misma suposición). **82 de 427 no están representados en ese ANOVA**, sin atribuir su causa ni grupo. Interés medio alto/subida 3,37; control 3,00. Se definió antes de calcular el **contraste primario de interés**, y se añadió competencia como control secundario (3,62 vs 3,12). Si los 82 restantes pudieran pertenecer a cualquier brazo, con valores 1–5 y por lo menos dos observados por brazo, la media general por grupo es parcialmente identificable, no exactamente recuperable. Las medias del texto están redondeadas y se tratan como exactas sólo para la operación de sensibilidad.

**D — Prerregistro:** [C01_PREREG_AJ.json](C01_PREREG_AJ.json), commit `b120259533672e2a05293eecb586b3c204ddb596`, realizado **después de congelar código y tests pero antes de ejecutarlos**. Fuente Python `pickal_aggregate_bounds.py` SHA256 `265f2d736982fb7f2d1aea29f81fa77bdd3c4acfde3b85c4dedd7a273165216e`, blob Git `ec5bf6b63699e78beb2880d0eaa82fa0a04911b1`. Primer test `test_pickal_aggregate_bounds.py` SHA256 `6439ca0ce743014927c44cf6a1a183036f4b7aaa9b0aae684b94b11fb2257ade`.

**E — Ejecución con negativo conservado:** la primera pasada del test dio **5/7** grupos satisfactorios y **2 errores en el propio test** porque `float('-4063/2150')` no analiza una fracción de texto; el cálculo fuente separado finalizó correctamente. Esta ejecución inicial **no cuenta por sí sola como ciclo válido**. Se documentó y prerregistró la reparación en `C01_TEST_REPAIR_PREREG.json`, commit `eeb2e4f54c19b42671b5c2129c5d0ea0d90a4803`; después se modificaron exclusivamente las aserciones para llamar `float(Fraction(...))`, se guardó el nuevo SHA antes de repetir en `C01_REPAIR_SHA_FREEZE.json`, commit `95ff3dba28ecbd650163f605defa2d02fd3cb2bc`. El test final SHA256 `1afa975678069f3e080ef3c4fbf3ed6a0626e92fa57744cdcf69e1bb5f3cc04c`. **Repetición nativa Python: 7/7 PASS, exit 0**.

**F — Auditoría adversarial:** enumeradas **3.486** distribuciones factibles de casos no representados en los dos brazos focales, con el resto atribuible a los otros tres. El contraste publicado es **+0,37**. La cota inferior bajo esos supuestos es **−1,889767** (82 no representados del brazo alto/subida, valores extremos bajos) y la superior **+2,192222** (82 del control, valores extremos bajos). El contraste secundario de competencia +0,50 también atraviesa cero bajo límites extremos: **[−1,99814, +2,431556]**. Los límites son sensibilidad matemática, **no intervalos estadísticos de confianza, valores p, observaciones reales ni correcciones causales de la publicación**.

**G — Independencia y ausencia de datos personales:** fuente independiente de PFL, PDF original con condiciones y resultados publicados. El propio artículo enlaza código/datos/prerregistro en [OSF](https://osf.io/f6dxq/?view_only=09e9393a77bf47fcb858683c325e5eaf), pero no estuvo accesible en la herramienta; **no se obtuvieron filas ni se aceptaron licencias**. Sin réplica externa ni mecanismo original aislado.

**H — Priors:** actualización PF-BR26 y PF-BR27. Ya existe un ensayo de ranking ficticio con posición × tendencia: PFL no puede reivindicar como nuevo ese contraste. Publicar sólo resultados de casos completos no puede sustituir sin más el denominador de aleatorizados o una especificación de datos ausentes.

**I — Dictamen:** **0/3 científico**; aportación metodológica acotada a la lectura de resultados agregados. No se ha demostrado el efecto causal de PFL ni un descubrimiento independiente.

**J — Decisión:** **C01 válido únicamente AB-R de sensibilidad a agregados**, tras reparación, sin incrementar CT2 ni N1. [Recibo de ejecución](C01_RUN_RECEIPT.json).

## C02 · AB-R de segundo ensayo publicado, separando ventanas y mecanismos

**A:** ¿qué parte aritmética del cambio en historias y usuarios activos publicados tras una intervención de concurso puede describirse por el margen de usuarios activos, frente a la intensidad condicional, para dos ventanas de observación distintas?

**B:** rivales: (i) concurso escolar completo ITT sí tiene interpretación causal al nivel de asignación; (ii) atribuir el efecto al ranking solo es incorrecto porque hubo premios, notificaciones y leaderboard especial, mientras el control ya tenía uno convencional; (iii) condicionar en estar activo (variable posterior al tratamiento) **impide identificar una mediación causal**; (iv) la actividad positiva podría no ser equivalente a al menos una historia completada, en cuyo caso no se justifica la identidad con esos indicadores publicados.

**C:** [Fuente original Palikot, Agrawal, Kanodia y Athey 2026](https://doi.org/10.1007/s11129-026-09311-3) registra **138 escuelas y 9.327 estudiantes aleatorizados** en su figura temporal. Cuatro semanas tras concurso: historias completadas control **0,146**, ITT adicional **0,178**, actividad control **6,5%** y tratamiento **9,6%**. Doce semanas: control **0,395**, adicional **0,301**, actividad control **12,2%** y tratamiento **14,3%**. La pareja 9,6%/6,5% es **de cuatro semanas**, aunque el resumen inicial mencione en una misma frase el resultado de historias a doce semanas. Esta diferencia temporal importaba para el estimando y no estaba aclarada en nuestro prior anterior PF-BR15. El tratamiento es un paquete, no la exposición aleatoria individual a un leaderboard.

**D:** [C02_PREREG_AJ.json](C02_PREREG_AJ.json), commit `b40d4bae29c443c07d29dc29862818ab49ef77da`; código `palikot_aggregate_margin.py` SHA256 `ba5fc19630ba31cacd8ab4a9ffc8badc7e8fe798fb7396e6ef9d8839c817a2df`, test `test_palikot_aggregate_margin.py` SHA256 `82d954c5ae8ae5660240424b19c17a2f64d9c56a810d8a77b7b355da9516e0f2`, equivalentes a blobs verificados en GitHub. Fórmula aritmética simétrica (*Kitagawa/Shapley*): para `mu=p*r`, `Delta mu = (p1−p0)(r0+r1)/2 + (r1−r0)(p0+p1)/2`. Aplica sólo si `p` define actividad compatible y del mismo periodo que `mu`. Test adversarial sobre denominadores cero, ventana equivocada y lectura causal.

**E:** corrida nativa Python stdlib, **7/7 PASS, exit 0**. Cuatro semanas: `Delta historias=0.178`, `Delta activos=+3.1pp`, componentes simétricos descriptivos **0,08712788** (extenso) y **0,09087212** (intensivo), aprox. **48,95%** frente a **51,05%** de la diferencia. Doce semanas: `Delta historias=0.301`, `Delta activos=+2.1pp`, componentes **0,0851008** (extenso) y **0,2158992** (intensivo), aprox. **28,27%** frente a **71,73%**. **Difieren porque las ventanas acumuladas son distintas** y se aplican definiciones y datos publicados redondeados.

**F–G:** son identidades aritméticas sobre medias publicadas, no descomposiciones causalmente identificadas. El ensayo fuente usa estimaciones ajustadas por estratos y errores agrupados por escuela; combinarlas con proporciones descriptivas podría no reproducir exactamente medias de las mismas unidades ponderadas. La condición de usuario activo está posterior a la asignación; por tanto **no es posible concluir que el 72% del impacto sea una vía causal de intensidad**. Tampoco se observa competencia política ni desempeño de adultos; no se ha replicado el análisis de los autores.

**H:** PF-BR15 se actualizó con los tamaños y periodos correctos; PF-BR28 documenta la identidad condicional.

**I:** resultado **0/3 científico** y no un resultado nuevo de PFL; informativo para definir métricas de compromiso, ventanas y población de riesgo de cualquier piloto futuro.

**J:** **C02 válido de análisis AB-R agregado de alcance limitado**. [Recibo](C02_RUN_RECEIPT.json).

## C03, C04, C05 · R5 sin inflar número de experimentos

**C03 planificación:** el PDF de Pickal identifica un OSF con protocolo, materiales, código y microdatos, pero la herramienta no pudo abrirlo; la prueba causal sobre acceso individual, presencia de no respondientes y datos ausentes no está permitida ni identificada. **No se consume plaza**.

**C04 planificación:** [Regaço 2026, Mendeley Data v2](https://doi.org/10.17632/3bhp6zd2cw.2), licencia CC BY 4.0 con R y dos CSV de Matching-to-Sample. Se comprobó sólo catálogo original, **no diseño de leaderboard causal ni derechos de datos de personas**. No se descargó material individual. No justifica abrir A–J con novedad en PFL.

**C05 sin abrir:** no ha aparecido una tercera vía diferenciada, con instrumentos idóneos, acceso/ética verificados y novedad capaz de competir con Pickal, Palikot, Felkey, Chen, Lumsden, GJP o Lemus–Marshall. **STOP_R5**; no reproducir micro-simulaciones ni repetir un ensayo documental como ciclo.

## Balance y continuidad

[CAMPAIGN_STATUS.json](CAMPAIGN_STATUS.json) contiene el recuento y sus límites; [CT2_TRAJECTORY.json](CT2_TRAJECTORY.json) y [CT2_FULL_AND_ZOOM.svg](CT2_FULL_AND_ZOOM.svg) muestran la CT2 científica 22→22, escala completa y ampliada. Citas y priors PF-BR26–PF-BR29 quedaron incorporados al ledger histórico, sin borrar negativos. El primer intento fallido de C01 sigue trazado.

**Presupuesto:** bloque anterior 5/5 cumplido; **bloque nuevo ahora 2/5 ejecutado y válido muy limitado, quedan 3/5**; **plazas históricas pendientes 2**, separadas. No se ha descargado microdatos personales, puntuado políticos, aceptado licencias o contactado autores. No se disparó GitHub CI costosa ni ChatRelay ni se hizo merge a main.

**Decisión STOP_R5:** continuar solo si existe nueva fuente original de exposición/participación legítima, comparador que realmente discrimine o protocolo de prueba no cubierto por antecedentes. **No se solicita nueva autorización mientras queden tres nuevas y dos históricas autorizadas.**
