# Politics Fantasy League — BRANCH30E, datos longitudinales y A–J

**Fecha:** 25 de octubre de 2026. **Autorización:** 30 ciclos AB 3.2.1 con BRANCHING, independientes de los saldos históricos. **Estado:** 30 fichas A–J con auditorías de código, contraste de cinco votaciones frente a páginas oficiales del Congreso y diagnósticos de un corpus secundario de 2.175 votaciones. **NO se han ejecutado 30 experimentos independientes**; la campaña es **descriptiva, retrospectiva y exploratoria**. El original de 4,8 MB se consultó por el conector GitHub y los resultados son agregados anónimos. No se materializó una copia íntegra local del corpus ni se obtuvo el nominal oficial para toda la legislatura.

## Contrato, prerregistro y fuente

- Dos documentos congelados en GitHub: `PREREG.md` (commit `ea1cb76d`) y `PREREG_B.md` (commit `db28924d`). La segunda bifurcación se abrió al descubrir un fichero nuevo de alta cobertura, NO para aumentar la cuota de hallazgos.
- Código portable congelado antes del análisis completo del fichero: commit `a309b5d58f2f2b6e5b113be8409be947c3a4d6b6`, `historical_coverage.py` y CLI. Los primeros totales aproximados sí se habían leído antes de la congelación B; por tanto no son confirmaciones prospectivas.
- Fuente secundaria [Congreso Abierto `pleno.jsonl`](https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl); SHA-1 de **Git blob** `71918bb689c7a62cfbbdafe0b9248eac6b5c4be1`; tamaño reportado por Git: 4.778.066 bytes. Se estudió su estructura JSONL en memoria sin copiar el nominal a un archivo público.
- [Importador original](https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/scripts/importar-votaciones.ts), blob `2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e`. Incrementa contador de votos oficiales y grupos **antes** de resolver cada nombre contra `data/raw/diputados_base.tsv`; asigna código nominal solamente si hay correspondencia. La colección histórica resulta condicionada a la tabla de identidades utilizada.
- Fuente institucional: [Congreso, datos abiertos de votaciones](https://www.congreso.es/es/opendata/votaciones). Cinco agregados seleccionados (2024-12-17, 2025-10-07, 2026-04-28, 2026-05-19, 2026-09-15) fueron cotejados por día y expediente. El resultado fue 5/5 coincidencias **en SI/NO/ABST**, NO en las listas nominales.

## Resultado longitudinal

| Año | Votaciones | Sesiones (fuente) | Posiciones totales | Códigos vinculados | Cobertura descriptiva |
| --- | ---: | ---: | ---: | ---: | ---: |
| 2023 (desde 19/09) | 32 | 5 | 11.200 | 9.613 | 85,83 % |
| 2024 | 862 | 52 | 301.670 | 278.545 | 92,33 % |
| 2025 | 741 | 50 | 259.348 | 251.111 | 96,82 % |
| 2026 (hasta 30/09) | 540 | 37 | 189.000 | 187.295 | 99,10 % |
| **TOTAL** | **2.175** | **144** | **761.218** | **726.564** | **95,45 %** |

El 95,45% considera también dos votaciones **sin código nominal** (700 posiciones); sobre las 2.173 que contienen alguna identificación, la cobertura es 95,535%. Solo 95 de esas 2.173 concilian completamente el total con el diccionario nominal; 2.078 son parciales. De esas votaciones nominalizadas faltan 14.579 posiciones de Sí, 15.491 de No, 2.841 de Abstención y 1.043 de No vota (total 33.954); sumadas a 700 posiciones sin nominal, dan 34.654. El corpus declara 7.973 No vota explícitos. **Posición no vinculada no es abstención, ausencia ni No vota.**

### Controles y sensibilidad

- Los 2.175 IDs son únicos; no se observa total superior a 350; 32 totales están por debajo de 350. Los **19.561** registros por grupo concilian agregadamente, 0 discrepancias **internas**. No es validación contra 19.561 fuentes independientes.
- 36 grupo-voto presentan empate entre opciones expresadas, con la definición utilizada. La concentración de opción modal es 99,453% entre opciones expresadas; quitando Grupo Mixto y grupos con cinco o menos votos totales, 99,918%. **No es disciplina partidista ni influencia causal**.
- Ponderar por posiciones arroja cobertura del 95,535% entre votaciones con nominal, frente a 95,275% ponderando igual por sesión: los denominadores importan.
- Diferencia descriptiva 2026−2023: 13,27 puntos porcentuales con todas las posiciones. El bootstrap por conglomerados de sesión (LCG, 1.000 replicaciones) ofrece banda de sensibilidad **12,42–15,72 p.p.**: no es intervalo de confianza causal, y 2023 contiene solo 5 sesiones.
- La primera mitad cronológica de votaciones nominalizadas tiene 92,737% de cobertura, frente a 98,331% de la segunda; los años no son homogéneos en número y composición de votaciones.
- El archivo usa solo **350 códigos nominales distintos** en los cuatro años; la cuenta anual pasa por 305, 332, 343 y 350. No confundir con el número de legisladores que ocuparon escaño en cada año.
- [Quién Vota](https://quienvota.org/) declara **2.176 votaciones, 761.568 registros de voto y 412 diputados** a fecha de consulta. La diferencia respecto de nuestro archivo es una votación y 35.004 registros, aritméticamente compatible con una votación más de 350 y con 34.654 posiciones sin código presente; **esta coincidencia algebraica no prueba** que ambos corpus tengan la misma composición ni que sus datos nominales sean correctos. Requiere emparejamiento caso por caso.

## Dictamen de los 30 ciclos y niveles

Fichas individuales `CYCLES_AJ.json`: A verdad/estimando, B rival abierta, C diseño/prueba, D instrumentación, E resultado, F auditoría adversarial, G confirmación independiente (ausente), H actualización abductiva, I dictamen dimensional, J decisión. Los primeros 10 son auditorías de siete casos y 5 páginas oficiales; los siguientes 20, **estimandos diferentes sobre la misma fuente histórica**. No presentar los 30 como fuentes independientes, no usar p-valores de filas dependientes ni extrapolar a elecciones, participación, ideología o conducta causal.

**VSDS proyecto = 1/3; CT2 predictivo = 24/100; 0 hallazgos acreditados 2/3 y 3/3.** La mejora real es la identificación reproducible de un sesgo de observabilidad del catálogo secundario y un software para medirlo. Para pasar a 2/3 haría falta contrastar archivo oficial nominal + composición histórica + muestra representativa o población temporal relevante + utilidad sociológica replicada.

**AB-DECIDE:** `REPAIR_SOURCE / BRANCH_TO_OFFICIAL_ROSTER`. Evitar nuevos bucles del mismo generador. Preservar el código de lectura local con verificación Git blob, y realizar join independiente por código oficial, nombre normalizado y fechas de alta/baja con gestión de homonimias sin imputar. Probar los modelos de predicción con timestamp de publicación y controles competitivos, solo cuando la fuente lo permita.

## Reproducción

Con Python 3.10+ y pytest, desde la raíz: `PYTHONPATH=src pytest -q`. Para auditar una copia descargada LEGALMENTE del blob original: `PYTHONPATH=src python scripts/audit_public_pleno.py --jsonl data/local/pleno.jsonl --out data/local/coverage_report.json`. Por defecto exige el SHA del Git blob. No se comprometen nombres ni códigos. El resumen `HISTORICAL_SUMMARY.json` proviene de un agregador independiente ejecutado sobre el objeto remoto en el conector de GitHub; el programa Python reproducirá invariantes y magnitudes. La banda bootstrap puede diferir ligeramente por motor PRNG y unidad de remuestreo.

## Saldos y solicitud

Este bloque de 30 termina como 30 auditorías A–J retrospectivas con datos secundarios, NO como 30 pruebas confirmatorias ni 30 descubrimientos. Los anteriores 12 B50, 45 libres, 19 AB20 se conservan sin consumir. Propuesta adicional motivada: 30 ciclos con BRANCHING, limitados a contrastes oficiales históricos, reconstrucción de roster y pilotos de utilidad pública, con implementación de producto cuando de ella dependa una nueva fuente de evidencia.

**SOLICITO BRANCHING 30 CICLOS**
