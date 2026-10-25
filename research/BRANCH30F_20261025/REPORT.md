# Politics Fantasy League — PF-BR30F, informe de 30 auditorías AB A–J

**Fecha:** 2026-10-25. **Ámbito:** ciencias sociales cuantitativas, integridad de datos parlamentarios y diseño de un observatorio. **Estado:** `POST_HOC_AUDIT` para las 30 fichas A–J; **no** constituye 30 pruebas empíricas independientes ni 30 hallazgos nuevos. Los diseños se prerregistraron genéricamente antes del nuevo análisis en el commit `5b5a85a6c470beb6f3d86084f883c4806220e3fd`, aunque buena parte de las preguntas habían sido orientadas por los resultados previos. No se dispone de holdout institucional independiente.

## 1. Fuente, estimando y procedencia

Se extrajo mediante el conector GitHub un archivo público de **Congreso Abierto**: `MarcoAnarmo/CongresoAbierto/data/raw/votaciones/pleno.jsonl`, blob Git **`71918bb689c7a62cfbbdafe0b9248eac6b5c4be1`**. El importador `scripts/importar-votaciones.ts`, blob **`2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e`**, registra los votos en totales y grupos incluso cuando un nombre no se resuelve en la tabla de diputados que alimenta el diccionario nominal. **Este mecanismo está explícito en el código**; la identidad exacta y causa de cada entrada no resuelta aún no se han contrastado con el JSON oficial correspondiente.

El resultado central es **cobertura del catálogo de identificadores de diputados**, NO tasa de participación, ausentismo o abstención real. Un «No vota» explícito es una opción distinta de un registro no indexado.

## 2. Hallazgos exploratorios dentro de la fuente secundaria

| Medida | Resultado |
|---|---:|
| Votaciones | 2.175 |
| Sesiones con fecha | 144 |
| Votos nominales identificados | 726.564 |
| Posiciones contabilizadas en los agregados | 761.218 |
| Diferencia nominal-agregado | **34.654** |
| Diferencia en votaciones con nominal no vacío | 33.954 |
| Votaciones sin ningún registro nominal | 2 (700 posiciones) |
| Filas de grupo | 19.561 |
| Discrepancias grupo-agregado / ids de votación repetidos / códigos individuales duplicados dentro de un voto | 0 / 0 / 0 |
| Votaciones cuyo total es 349 en vez de 350 | 32 |
| Identificadores distintos en todo el archivo | 350 |

Las 34.654 posiciones no identificadas se desglosan en 15.264 «Sí», 15.491 «No», 2.841 abstenciones y 1.058 «No vota». Las dos votaciones sin diccionario nominal son `s89-v005` (2025-01-22) y `s202-v021` (2026-09-30). Sus 700 posiciones **no** se imputan como abstenciones ni ausencias. La consistencia perfecta grupo-total es *interna a un solo generador*, no una verificación contra el Congreso.

## 3. Sesgo temporal de cobertura

| Año | Votaciones | Sesiones | Identificados/total | Códigos distintos | Cambio de signo de mayoría |
|---|---:|---:|---:|---:|---:|
| 2023 | 32 | 5 | 85,83 % | 305 | 15 |
| 2024 | 862 | 52 | 92,33 % | 332 | 124 |
| 2025 | 741 | 50 | 96,82 % | 343 | 4 |
| 2026 | 540 | 37 | 99,10 % | 350 | 6 |

La diferencia descriptiva 2026−2023 es de +13,27 puntos porcentuales; un bootstrap por sesiones (5 frente a 37, 3.000 remuestreos) produjo IC 95 % descriptivo **[+12,18, +15,49] puntos**. 2025−2024: **+4,49 puntos**, IC descriptivo **[+3,40, +5,51]**. Estos intervalos reflejan variación entre sesiones de la *misma fuente*, no muestran efecto causal, ni controlan sustituciones, ni constituyen replicación externa. Hay solo cinco sesiones de 2023.

El aumento de identificadores únicos por año (305 → 350) es compatible con resolución de identidades anclada al catálogo de miembros actuales. No permite atribuir a una causa única cada hueco.

## 4. Consecuencia sustantiva para inferencias

En **149 de las 2.173 votaciones que contienen algún voto identificado** —**6,86 %**—, el signo de `Sí − No` calculado con **solo los identificados** difiere del calculado con los agregados de la misma fuente. Por año: 15, 124, 4 y 6, respectivamente. El criterio incluye empates como categoría distinta. **Esto no cambia ni cuestiona los resultados oficiales**: demuestra que un algoritmo ingenuo que utiliza exclusivamente el subconjunto nominal sesgado puede invertir el sentido de mayoría.

El error absoluto medio del margen `(Sí−No)/(Sí+No+Abst)` al pasar de agregado a nominal es 0,00801. Esa media por sí sola disimula inversiones localizadas. Dentro de la fuente, las siete votaciones seleccionadas por tema tienen un 44,55 % de «Sí» entre expresados frente al 46,55 % del resto; su cobertura es 98,29 % frente al 95,44 % del resto. Son **siete casos escogidos adrede**, sin inferencia muestral.

Existen 19.500 filas grupo-voto con alguna opción expresada. Su concentración modal media es 97,56 %; entre grupos con hasta diez expresados es 95,68 % y en grupos con al menos treinta es 99,93 %. Son descripciones ecológicas, contaminadas por tamaño y composición; **no** se deduce disciplina individual, cohesión causal ni responsabilidad de representantes.

## 5. Auditoría adversarial y controles negativos

- Un diccionario nominal no puede usarse para deducir ausencia a partir de la inexistencia de una fila. «No vota» explícito no equivale a «no indexado». La primera categoría representa 7.973 posiciones totales, de las cuales 1.058 carecen de correspondencia individual.
- Ninguna votación tiene un recuento nominal que supere a su total por categoría ni códigos individuales duplicados. Las 19.561 filas de grupos agregan correctamente cuando existe desglose; cuatro filas tienen grupo `?`.
- **Dependencia estadística**: las 2.175 votaciones están agrupadas en 144 sesiones. Un bootstrap descriptivo por sesiones para la fracción global de posiciones no identificadas produjo un intervalo aproximado [3,75 %, 5,46 %]; no reemplazarlo por precisión calculada tratando 726.564 votos como muestras independientes.
- La cuenta anual de 350 identificadores distintos en 2026 **no** es una lista de titulares elegibles para cada votación, ni los agregados de 350 posiciones garantizan 350 diputados presentes.
- El esquema de la fuente contiene opciones por código y recuentos por grupo, pero no un join individual-grupo histórico certificado para todos los votos. No crear esa unión por imputación retrospectiva.
- La ausencia de marcas históricas de primera publicación impide construir validación predictiva «as-of» con este archivo retrospectivo sin fuga temporal.

## 6. Informe de los 30 ciclos y calificación

`LEDGER.json` contiene las **treinta entradas de A a J**, cada una con pregunta, rivales, diseño/limitación de preregistro, instrumentación, ejecución, auditoría adversarial, confirmación ausente, actualización abductiva, dictamen y decisión. **Tipo: `POST_HOC_AUDIT`**, una única fuente secundaria. Esto cierra 30 auditorías documentales/analíticas del bloque, pero **cero experimentos confirmatorios sobre un corpus nominal oficial independiente**. No deben presentarse como 30 investigaciones independientes.

**VSDS 1/3**, **CT2 rama predictiva 24/100**, **hallazgos 2/3 = 0**. Se puede conservar un hallazgo exploratorio de tipo 1/3 —el riesgo de inversiones de mayoría por cobertura retrospectiva— únicamente como resultado técnico-reproducible de la fuente secundaria; no conceder originalidad científica ni acreditación de causalidad.

**AB-DECIDE:** `REPAIR_SOURCE / STOP_NONINDEPENDENT_MULTIPLICATION`. Priorizar: obtener originales JSON del Congreso correspondientes a las mismas votaciones, reconstruir tabla histórica de diputados y grupos desde actas, identificar nombres no resueltos, obtener fecha de disponibilidad de cada campo, preparar dataset longitudinal con cobertura publicada/fecha de ingesta, contrastar previsiones contra baseline temporal competente y no puntuar individuos reales antes de ese paso.

## 7. Estado de publicación

El repositorio de alojamiento sigue siendo `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league` por la incidencia de permisos de escritura en `GalexY3/polictics_fantasy_league`. Migrar conservando historia y SHA. El auditor `scripts/audit_pleno_full.py` se ejecuta localmente sobre un fichero `pleno.jsonl` descargado por el investigador; no necesita dependencias. En esta sesión las cifras de campo se computaron directamente sobre el objeto obtenido mediante **conector GitHub**, mientras que las pruebas unitarias del script Python se ejecutaron sobre fixtures sintéticas: estos dos procedimientos no constituyen replicación de fuente independiente.

**Solicitud recomendada al cierre:** BRANCHING 30 CICLOS, **solo si aparece nueva evidencia externa**, o producción orientada a adquisición y conciliación oficial de identidad histórica. Registrar autorización por separado: este bloque nuevo de 30 no consume la campaña anterior inconclusa ni los saldos históricos.

## Apéndice adversarial sobre el signo de mayoría (C22)

La cifra de **149 cambios de signo** se descompone en **125 inversiones estrictas** (Sí> No pasa a Sí< No, o inversamente) y **24 cambios con empate**. Es una taxonomía añadida retrospectivamente sobre el mismo archivo secundario, no confirmación externa ni cambio del resultado oficial. Véanse [auditoría A–J](C22_ADVERSARIAL_APPENDIX.md), [código](../../scripts/audit_majority_sign.py), [pruebas](../../tests/test_majority_sign_audit.py) y [gráfico](strict_reversals_by_year.png). No se cuenta como ciclo adicional; VSDS y CT2 permanecen sin cambios.
