# Politics Fantasy League — AB-H BRANCHING5: continuación C03–C04

**Fecha:** 29/10/2026. **Rama:** `research/pfl-abh5-cluster-interference-20261029`, derivada de la PR #46 en commit `e9c6a3f90fcd70e0fbddf6aaba27bf870ea73d23`. **Método:** AB 3.2.1, anexos O1–O7, A–J, DRIFT y STOP_R5.

## Resultado y presupuesto

Autorización nueva original: **5 ciclos** independientes de **2 plazas históricas**. C01 y C02 constaban como AB-P sintéticos en PR #46. En esta continuación se ejecutaron **C03 (AB-P de interferencia/ponderación, 8/8 pruebas)** y **C04 (AB-R con agregados publicados, 7/7 pruebas)**. El C05 sigue **sin abrir**, y las dos plazas históricas siguen intactas. **4/5 ejecutados**, 1/5 disponible. C02 conserva su defecto y reparación anteriores, sin contar el intento fallido como otro ciclo.

Los planes no ejecutados originalmente asociados a los identificadores C03 (padrón GJP) y C04 (acceso OSF Erat) se han preservado sin contarlos como experimentos: están en `../ABH_BRANCHING5_EXPOSURE_20261029/CAMPAIGN_STATUS.json` bajo `superseded_unexecuted_plan`. La nueva rama redefine esas plazas mediante BRANCHING, sin borrar sus bloqueos. Grados científicos nuevos N1/N2/N3: **0/0/0**. CT2 prospectiva científica ordinal **22/100 → 22/100**. Puertas de lanzamiento **0/6**; el éxito técnico de una suite de pruebas no implica eficacia humana.

## C03. AB-P: interferencia en salas y cambio de estimando

**A. Pregunta:** ¿una clasificación compartida permite tratar independientemente a sus integrantes cuando la condición de tratamiento difiere por persona? ¿Los contrastes por participante y por sala se mantienen al cambiar el tamaño de la sala?

**B. Rivales:** (i) mezcla de brazos en salas interfiere con la exposición y ponderaciones distintas cambian el objetivo; (ii) supuesto nulo: ambos contrastes coinciden; (iii) rival fuerte: asignación individual podría ser válida bajo un modelo de interferencia/exposure mapping explícito; **no demostramos que aleatorizar salas sea la única opción**.

**C. Prerregistro discriminante:** fixture puramente ficticio de 16 participantes, ocho salas, cuatro brazos `control/transparency/leaderboard/both`, dos salas por brazo con tamaños 1 y 3. En control la tasa por personas es 3/4=0,75 y la media de salas es (0/1+3/3)/2=0,5. Efecto factorial *transparency* por personas 0,25 y por salas 0,5; interacción 1,5 por personas frente a 1,0 por salas. Son **dos estimandos descriptivos distintos**, y uno no puede sustituir al otro sin fijar población objetivo y esquema de asignación.

**D. Congelación:** [A–J y hashes antes de ejecutar](C03_PREREG_FREEZE.json), commit `b6409e2c7715f5f1bc6bcab572c3945860248e2e`. Código [fictional_cluster_gate.mjs](../../src/politics_fantasy/fictional_cluster_gate.mjs), SHA256 `bb196e1dda902e76b6557f985e94038814a6a7f5600abed93a5ffd7debf9dbcf`; test [test_fictional_cluster_gate.mjs](../../src/politics_fantasy/test_fictional_cluster_gate.mjs), SHA256 `d4cb5be09151c74ea37ad048483e90c3c970f836fdae1d40fa5e4ad8b9490126`. Identidad de blob Git corroborada.

**E. Ejecución:** Node v22.16.0, contenedor local aislado, `node test_fictional_cluster_gate.mjs`, **8/8 PASS, exit 0**, sin red. [Recibo exacto](C03_RUN_RECEIPT.json).

**F. Auditoría adversarial:** rechaza mezcla de brazos en una sala, participantes duplicados, brazo inventado, campos de identificación no previstos, getters, falta de grupo, fixture de estudio real simulado; comprueba invariancia de orden. Es una comprobación de programa, no una auditoría de personas.

**G. Independencia:** no hay réplica humana, muestra real ni comprobación desde un clon limpio. El antecedente Felkey et al. (2023) incluye equipos y efectos de ranking/anonimato; Chen et al. (2024) trabaja ligas locales, con datos no compartibles.

**H. Priors:** se refuerza necesidad de declarar unidad de asignación, exposición entre pares y pesos del estimando.

**I. Dictamen:** AB-P limitado **0/3 científico**, sin evidencia de resultado en PFL.

**J. Decisión:** contar **un ciclo AB-P C03**; no contar ocho tests como ocho ciclos. DRIFT D1.

## C04. AB-R limitado: sensibilidad a exclusiones en un RCT publicado

**A. Pregunta:** ¿una exclusión global de ~5,6% garantiza que las tasas de inclusión sean casi iguales entre grupos?

**B. Rivales:** (i) lectura ingenua de pérdida global 13/232 como límite por brazo; (ii) exclusiones pueden concentrarse en un solo brazo y producir una diferencia mayor; (iii) los autores pueden legítimamente estimar resultados *condicionados a sesiones de al menos un minuto*, sin afirmar un ITT completo.

**C. Evidencia publicada:** Karabiber y Gürol (2026), *Acta Psychologica* 266:106908, https://doi.org/10.1016/j.actpsy.2026.106908, sección 4.2 y tabla 2. El artículo informa 219 participantes incluidos repartidos en seis grupos con tamaños `[36,37,36,36,37,37]`, y **13 registros de menos de un minuto excluidos**. **No proporciona el desglose de los 13 por brazo** en las líneas documentadas. El cómputo asume condicionalmente que cada excluido pertenecía a uno de los seis brazos; *no hemos verificado que los 232 registros fueran todos aleatorizados*.

**D. Diseño congelado:** determinar exactamente la mayor diferencia factible entre tasas de inclusión `n_j/(n_j+e_j)`, con `e_j` enteros no negativos y suma 13. Enumerar todas las `C(18,5)=8.568` asignaciones posibles, comparar con la solución analítica de concentrar todos los excluidos en un grupo de 36 incluidos. [Prerregistro A–J y SHA](C04_AGGREGATE_PREREG_FREEZE.json), commit `9d0a42fa573c7a6fe05b790a4bc944e6894f6e8d`. Python 3.13.5, sin paquetes externos ni datos personales; [código](published_attrition_bounds.py) SHA256 `4fc060733744af727562d20ca51bd6e953eb79d27098f7820dc4631a4bd06d97`, [tests](test_published_attrition_bounds.py) SHA256 `8de28081fd0a5ca396e16cf87014758e5ba98c2864fcecbdee1cabafb1bfc89d`. Los blobs Git y bytes ejecutados coinciden.

**E. Ejecución:** enumeración completa, **8.568/8.568 asignaciones**, y **7/7 pruebas PASS, exit 0**. Total condicional 232, exclusión agregada 13/232=**5,60345%**. Cota máxima factible entre brazos **13/49 = 26,53061 puntos porcentuales**, si los trece excluidos pertenecieron a uno de los grupos con 36 retenidos y no hubo excluidos en el resto. La asignación testigo `[0,0,0,13,0,0]` se verifica en código. [Recibo](C04_RUN_RECEIPT.json).

**F. Adversario:** rechaza grupos distintos de los documentados, evita enumeraciones de tamaño arbitrario, contrasta solución cerrada con enumeración, comprueba suma de exclusiones; no interpreta excluidos como puntuaciones cero ni inventa exposición o respuesta. La cota es **posibilidad matemática**, no tasa de abandono observada, sesgo estimado, efecto del leaderboard, CI ni valor p.

**G. Replicación:** la fuente del artículo es externa a PFL y los números son públicos. El cálculo es propio, pero **no constituye replicación independiente del efecto reportado por sus autores**; no se consultaron filas de OSF ni personas.

**H. Priors:** la ausencia de reparto por brazo impide garantizar tasas de inclusión balanceadas solo a partir de la cifra total de 13. La exclusión de sesiones menores de un minuto genera una cuestión legítima sobre población y estimando, **no invalida por sí sola los resultados publicados**.

**I. Dictamen:** AB-R de alcance **metodológico y agregado** ejecutado, grado **0/3 científico** por falta de nueva hipótesis sustantiva y contraste externo independiente. CT2 22 sin incremento.

**J. Decisión:** contar **C04 como un ciclo A–J analítico limitado**, nunca como validación causal de PFL. DRIFT D2.

## Antecedentes y accesos

- **Felkey, Dziadula y Chiang (2023)**, https://doi.org/10.1257/pandp.20231047, experimento de competición con 400 estudiantes y moderación por anonimato/rango. **Paquete original localizado** https://doi.org/10.3886/E189681V1 en OpenICPSR: catálogo muestra fichero Stata (~497 KB) y sintaxis .do (~6,7 KB). **No se descargaron** ficheros de personas ni se aceptaron términos. La asignación de *rank alto/bajo* es postratamiento y no debe leerse como aleatorización del rango.
- **Chen, Dobrescu, Foster y Motta (2024)**, https://doi.org/10.1016/j.labeco.2024.102602. Ensayo de feedback por ligas pequeñas (hasta 30), con efectos heterogéneos sobre esfuerzo, estrés y calificaciones. Los autores señalan que **no tienen autorización para compartir datos**; no insistir en acceso improcedente.
- **Karabiber y Gürol (2026)**, https://doi.org/10.1016/j.actpsy.2026.106908, distingue clasificaciones, barras de progreso y control, además de contextos individuales/colectivos. Los autores concluyen que ambos mecanismos pueden aumentar contribuciones; no es PFL y no se reproduce aquí.
- Los antecedentes de Palikot 2026, Erat 2026, GJP y Nelson/Ryvkin 2024 siguen preservados en el ledger previo. Se añadieron actualizaciones **PF-BR19–PF-BR23** al [registro cumulativo de fuentes y priors](../ABH_BROWSER_ATLAS_EVIDENCE5_20261029/SOURCES_AND_PRIORS.json).

## C05, riesgos y continuidad

**C05 sin abrir, STOP_R5**: ninguna inspección documental posterior justificó abrir otra A–J con originalidad y controles superiores a la literatura localizada. El acceso a paquete de replicación no implica automáticamente reutilización ética, derechos sobre datos personales o disponibilidad de asignación/exposición de no participantes. GJP continúa bloqueado para identificación causal de efectos de rankings. No se ejecutó CI costosa, ChatRelay, análisis político sobre personas reales, reclutamiento ni fusión a main.

**Balance final:** cuatro ciclos de los cinco nuevos autorizados, **tres AB-P sintéticos y un AB-R de sensibilidad agregada**, todos 0/3 científico; **uno nuevo sin consumir y dos históricos intactos**. **CT2 prospectiva 22/100 ordinal**; N1/N2/N3 0/0/0, lanzamiento 0/6. [Estado canónico actualizado](../ABH_BRANCHING5_EXPOSURE_20261029/CAMPAIGN_STATUS.json). [Gráfico CT2 completo y ampliado, sin cambios reales](../ABH_BRANCHING5_EXPOSURE_20261029/CT2_FULL_AND_ZOOM.svg).

**Siguiente acción sustentable:** inspección documental de archivo AEA E189681V1 (licencia, sintaxis no personal, variables de asignación y si existe un padrón de no respondientes), y del enlace OSF del estudio 2026, **sin abrir microdatos ni consumir C05** hasta demostrar discriminación y derechos. No se solicita un bloque nuevo: las plazas previamente concedidas siguen disponibles.
