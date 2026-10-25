# C01 · Auditoría de contraste del piloto agregados

**Bloque autorizado**: PF-AB20-20261024, 20 ciclos. **C01 ejecutado como prueba exploratoria documental con observaciones agregadas y auditoría programática**. **Grado de evidencia científico: 0/3**; no hay confirmación independiente.

Prerregistro local escrito y SHA-256 almacenado antes de comenzar a programar/ejecutar el análisis. **Limitación adicional:** el código aún no estaba congelado por commit GitHub ni respaldado por hash antes de su primera ejecución. Por tanto no satisface plenamente `freeze–run` AB O2/O3; no se lo etiqueta ensayo confirmatorio validado. GitHub rechazó escritura con HTTP 403 en la campaña de referencia. Se conservarán ambos estados y una nueva versión no reparará retroactivamente esa deficiencia.

## A–B
Pregunta: invariantes aritméticos y suficiencia de información de un conjunto de 20 recuentos oficiales agrupados por votación (muestra no aleatoria de una única sesión). H1: los tres recuentos suman ≤350. H_otra: diferencias respecto a 350 no permiten inferir inasistencias por diputado.

## C–E · Método y observaciones
Fuente de visualización: HTML del Congreso `https://www.congreso.es/es/opendata/votaciones` visualizado el 24/10/2026. Los 20 renglones de votación aparecen en la sesión 193 del 23/07/2026; CSV transcrito manualmente con líneas de navegación conservadas. Script: `scripts/ab20_c01_pilot.py`. N=20 renglones, **una sola sesión**, 0 series longitudinales, 0 políticos identificados.

Resultado aritmético: `20/20` sumas no superiores a 350; mínimo 344, máximo 348, mediana 348, media 347.45. Histograma de sumas: 344 (1), 346 (1), 347 (5), 348 (13). Esto valida **sólo consistencia de los triples tal como se copiaron**, no exactitud de extracción completa o de metadatos oficiales.

## F · Auditoría adversarial
18 tests Python superados (7 nuevos) en suite local del proyecto. Los controles negativos fabrican filas imposibles `si=351`, duplican row_id, mezclan sesión, usan voto negativo y URI de fuente ajena; el validador rechaza esas modificaciones sintéticas. El hecho de detectar datos artificialmente corruptos no demuestra cobertura del corpus real ni que el validador reconozca cambios de formato del Congreso.

**Interpretación adversarial dominante**: 20 observaciones correlacionadas dentro de la misma sesión, selección sin aleatorización y copiadas a mano. Un «gap» 350-total es únicamente diferencia aritmética: NO se puede equiparar a ausencias, ni a abstenciones no registradas, ni a productividad política. La población objetivo para el TFM es persona-semana, distinta de votación agregada, así que estos 20 renglones son insuficientes para entrenar o comparar pronósticos.

## G · Confirmación
Ausente: sin segundo canal JSON/XML, hash del recurso exacto, fecha de última actualización o primer momento de publicidad. Publicación de tabla no satisface confirmación independiente.

## H · Actualización de priors
P-PFL-01 (actualizado): los datos oficiales HTML contienen recuentos cuantificables, pero su estructura pública agregada no resuelve el problema de predicción nominal y bitemporal; estado `EMPÍRICO_OBSERVACIONAL_MANUAL_NO_VERIFICADO`, fuerza débil. P-PFL-02: la diferencia total-votos no debe denominarse inasistencia; corroborado como límite de identificación, sin inferir causa particular.

## I · Dictamen
Interna: comprobación aritmética reproducible condicionada al CSV. Identificación causal: no. Validez externa: no. Predictiva: no. Ética: ningún perfil privado. Reutilización: revisión pendiente de `last_updated` exigida por aviso legal. CT2 B3 se mantiene 24/100 (ordinal, no probabilidad). Hallazgos N1=0 N2=0 N3=0.

## J · AB-DECIDE
`REPAIR_ACCESS_AND_PROVENANCE`. No consumir 19 ciclos restantes como resúmenes documentales; obtener el JSON/XML nominal oficial y metadatos, confirmar licencias, establecer fuente temporal real y entonces prerregistrar primer contraste predictivo en commit previo. Conservar el piloto como exploratorio y su bloqueo en ledger.
