# Auditoría adversarial de BR30G, 25-10-2026

**Clase:** POST_HOC_AUDIT, no ciclo adicional ni replicación independiente de campo.

## Atribución y alcance
La segunda implementación de comprobación (en el conector GitHub sobre el blob Git SHA1 `71918bb689c7a62cfbbdafe0b9248eac6b5c4be1`) contó de nuevo 2.175 votaciones, 761.218 posiciones, 726.564 códigos de voto y 34.654 no indexadas. Calculó 2.024 signos iguales, 125 inversiones estrictas y 24 discrepancias con empate en 2.173 votaciones nominalizadas, más dos casos sin nominal. Encontró 1.655 casos con `|S_nom-N_nom| > missing_total`, todos con mismo signo oficial. El recuento del primer analizador coincide. Las dos implementaciones comparten la MISMA fuente y no prueban verdad institucional externa.

## Precisión C29 (sin borrar bruto)
El objeto bruto `RESULTS_C03_C30.json` contiene `groupAggregateMismatchedVotes: 2`. Su comprobación suma grupos vacíos para las dos votaciones **sin lista de grupos** (`s89-v005` y `s202-v021`), cada una con 350 posiciones agregadas: **ausencia de desglose**, no desacuerdo de recuentos existentes. Para las 2.173 votaciones con grupos hay **0 discrepancias internas**. Las 19.561 filas de grupo conciliadas no constituyen 19.561 fuentes independientes.

Por tanto, cualquier frase «dos votaciones con grupos aritméticamente erróneos» es **INCORRECTA**. Conservar el indicador bruto y aplicar interpretación auditada: `missing_group_breakdown_votes=2`; `group_disagreement_when_present=0/2173`.

## Revisión de baselines
* C26: Brier baseline siempre-Sí es débil; la media acumulada es un comparador de mínima competencia, no un baseline óptimo.
* C27: mejora frente a media global (0,206260 vs 0,249226) es **retrospectiva**. No existe fecha de publicación as-of original, ni prueba oficial independiente; posible sesgo por tipo de votación y cambio de agenda.
* C28: predicción de completitud usando sesión anterior no predice comportamiento parlamentario, sino regularidad de una **representación incompleta producida por el importador**.
* C16–C22: grupos-voto y pares comparten votaciones y sesión; no se calculan errores iid ni se infieren preferencias, disciplina, influencia o efecto causal.
* C24: 0 registros `asentimiento=true`. El efecto en este estrato es **NO IDENTIFICABLE**, no «sin diferencia».
* C29/C30: los datos secundarios mantienen nominados no resueltos y no certifican elenco histórico ni timestamp de primera disponibilidad.

## Validez y reproducibilidad
El fichero `scripts/br30g_audit.mjs` es función pura y `scripts/run_br30g_audit.mjs` debe comprobar la huella Git del archivo UTF-8 íntegro. Se pasó una batería focal de siete aserciones sobre **fixtures fabricadas** en el intérprete JS, y se confrontaron separadamente los recuentos críticos anteriores. **No se ejecutó** en esta sesión un clon limpio completo con Node desde el GitHub remoto, ni 28 repeticiones de auditores externos. Se puede reproducir con `node scripts/run_br30g_audit.mjs /ruta/pleno.jsonl --out /ruta/salida.json` en la raíz del proyecto. No introducir nombres/códigos en reportes agregados.

## Decisión
Las 28 unidades C03–C30 están completadas como análisis descriptivos retrospectivos de fuente secundaria; C01 documental y C02 ingeniería completan las 30 fichas A–J. No se acreditan 30 experimentos independientes, causalidad ni descubrimiento 2/3. VSDS=1/3, CT2 predictivo=24/100, N1/N2/N3 nuevos=0. Acceder a originales y roster histórico sigue siendo el cuello de botella.
