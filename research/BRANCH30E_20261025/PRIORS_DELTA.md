# Actualización de priors — BRANCH30E

Fecha: 2026-10-25. Alcance: instrumentación y observación de corpus SECUNDARIO. NO es modificación normativa de AB global.

| Prior | Antes | Evidencia nueva | Después | Falsador crítico |
| --- | --- | --- | --- | --- |
| PFL-P001: el mapeo contra catálogo contemporáneo puede crear sesgo temporal | plausible, no cuantificado fuera de siete casos | importador `2a9d63c7...` cuenta agregados antes de resolver nombres; archivo 2175 muestra 85,8% (2023) vs 99,1% (2026) en posiciones nominalizadas | reforzado como mecanismo del repositorio secundario; origen exacto de cada hueco todavía no auditado contra JSON oficial | un reparse con roster histórico completo reproduce igual patrón a igualdad de fuente/fecha |
| PFL-P002: falta nominal ≠ No vota | prior alto | en votos con nominal hay 33.954 posiciones sin código, 1.043 en categoría X, pero fuente declara 7.973 X explícitos en todo el fichero | reforzado, *no* deduce presencia física ni absentismo | coincidencias exactas individualizadas entre roster, acta y códigos en cada fecha |
| PFL-P003: cuentas por grupo preservan agregados mejor que por IDs actuales | plausible | cero inconsistencias internas en 19.561 grupo-voto; solo 95/2.173 votos tienen cuenta nominal igual al agregado | reforzado exclusivamente como **consistencia intrafuente**, no corroboración independiente | discrepancias con grupos en JSON oficiales primarios |
| PFL-P004: con más observaciones se demuestra mérito predictor | cuestionado | 2.175 filas no aportan marcas de primera publicación por voto ni censo nominal independiente | no modificar; no entrenar scores fantasy sobre ellas | validación bitemporal de fuentes y comparadores competentes en cohortes históricas independientes |
| PFL-P005: las diferencias de tamaño entre observatorios son evidencia directa de error | incierto | Congreso Abierto 2.175 votos, 726.564 IDs; Quién Vota 2.176 votos, 761.568 registros y 412 IDs históricos según su portal | no confirmado: **parece coherente** con una votación adicional y distinta política de inclusión; no emparejado | join de IDs por votación y documento de extracción |

No fijar probabilidades numéricas artificiales. CT2 24/100, VSDS 1/3, N2=0.
