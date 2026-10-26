# Politics Fantasy League — continuación 26/10/2026

**Conclusión:** 76 plazas AB preautorizadas adjudicadas. No equivalen a 76 experimentos de campo; hubo **57 ejecuciones de pruebas de ingeniería y datos secundarios** y **19 investigaciones de viabilidad cerradas por STOP_R5 ante falta de originales verificables**. No se declaran nuevos resultados confirmatorios, descubrimientos 2/3, ni valoraciones de personas políticas.

## Contabilidad de gobernanza

| Campaña | Plazas cerradas en esta continuación | Tipo y evidencia |
|---|---:|---|
| PF-B50 C39–C50 | 12 | QA de fuentes secundarias y software; 12 PASS, C46 falla inicialmente por namespace de fixture y se repara |
| PF-AB20 C02–C20 | 19 | Cribado A–J; 19 STOP_R5, sin ejecutar estimandos causales o de predicción de personas |
| PF-F45 | 45 | QA de fuente y motor multiactor; 45 PASS en V8, ninguna replicación de campo |
| **Total** | **76** | **57 pruebas ejecutadas + 19 cribados de evidencia R5** |

La cuenta B50 anterior se reconcilió: 8 originales C01–C08 + 30 ciclos B30 previamente publicados y referenciados *sin contarlos de nuevo* como C09–C38 + 12 QA nuevas C39–C50 = 50 de 50. Los ledgers conservan A–J individuales. El antiguo saldo de B50 de 12, el AB20 de 19 y el F45 de 45 está cerrado; no consumir una sola plaza dos veces.

- [Ledger B50 actualizado](../BRANCH50_20261025/CYCLES.json)
- [Resultados B50 C39–C50](../B50_REMAINING_20261026/RESULTS.json) y [contratos](../B50_REMAINING_20261026/CONTRACTS.md)
- [AB20: 19 cribados STOP_R5 con A–J](../AB20_REALES_20261024/FINAL_R5_20261026.json). La hipótesis original NO queda verificada.
- [F45: 45 fichas A–J](../AB65_20261024/FREE45_LEDGER.json)
- [F45: contratos](../FREE45_20261026/PREREG_45.json) y [salidas 45/45](../FREE45_20261026/RESULTS.json)

Las pruebas de F45 fueron especificadas antes de ejecutar la nueva batería, pero **el corpus y el código ya eran conocidos**. No hay prerregistro confirmatorio sobre población política. Los tests se ejecutaron en V8 ECMAScript y no en una instalación limpia de Node o un banco independiente. Las pruebas científicas AB20 se DETUVIERON porque faltan microdatos nominales originales, roster por fecha y first-public-at. Un STOP_R5 no equivale a experimento ejecutado.

## Aporte nuevo: actor político con o sin escaño

**Fuente 1, julio 2023:** [anerodata, 202307.csv](https://github.com/anerodata/data-elecciones-congreso-espana/blob/main/202307.csv), Git SHA1 59a7734f0deba570ea87681236ecd4c9008ebd33. Se procesaron 52 provincias, 59 etiquetas de candidaturas/opciones electorales con votos registrados y sus respectivos escaños. **48 etiquetas presentan votos positivos y cero escaños, y 11 poseen algún escaño** en esta elección. La unidad NO equivale necesariamente a un partido legalmente independiente: incluye denominaciones de listas y potenciales coaliciones. No medir influencia, relevancia, mérito ni preferencias personales por votos o escaños.

**Fuente 2, histórico:** [rOpenSpain/infoelectoral, partidos_generales.csv](https://github.com/rOpenSpain/infoelectoral/blob/master/data/partidos_generales.csv), SHA1 bc899d599e9c22d3215a60c0b02344f5771eeae3. CSV con 1.057 registros para 14 años electorales entre 1977 y 2019, y 260 códigos propios del archivo. **149 códigos** aparecen asociados a más de una cadena de denominación. No declarar 149 cambios de nombre legales: podrían ser coaliciones o reglas de codificación. **No unir** sus claves a las 59 etiquetas de 2023 sin fuente puente. Son 2 fuentes secundarias, no validación independiente del [XLSX del Ministerio del Interior](https://datos.gob.es/es/catalogo/e00003801-resultados-electorales). El intento de descarga oficial encontró DNS inaccesible y el JSON nominal del Congreso devolvió cache miss.

Se publicaron [datos descriptivos y procedencia de ambos archivos](../FIELD_EXPANSION_20261026/SECONDARY_ELECTORAL_AUDIT.json), el [parser de fuentes](../../scripts/electoral_source_audit.mjs) y [un atlas de 59 etiquetas](../../data/observatory/electoral_atlas_2023.json).

## Software creado e integrado

1. Parser CSV con tratamiento de comillas, validaciones de enteros y pares voto/escaño, provincias duplicadas, anomalías de fuente y resúmenes con dos universos temporales no fusionados.
2. Atlas JSON de 59 opciones electorales de 2023 con valores históricos y procedencia, ordenado alfabéticamente y sin clasificación de valor personal o ideológico.
3. Nuevo [adaptador Python de lectura y validación](../../src/politics_fantasy/electoral_atlas.py) y nuevo endpoint local GET /api/electoral-atlas en [servidor](../../src/politics_fantasy/server.py).
4. Pestaña web **Atlas electoral**, añadida al [HTML](../../src/politics_fantasy/web/index.html) y [JavaScript](../../src/politics_fantasy/web/app.js). Ofrece votos y escaños históricos como hechos descriptivos; sin clasificación de influencia.
5. [Suite de 45 pruebas](../../scripts/free45_suite.mjs) y [runner reproducible Node offline](../../scripts/run_free45.mjs).

**No se probó** en clon limpio que el servidor Python HTTP y la nueva pestaña funcionen como E2E completo. La comprobación de frontend fue estática. No se activan puntuaciones de personas reales. El prototipo continúa exclusivamente en localhost, sin autenticación pública.

## Priors / actualizaciones AB

- **PF-CONT-01 (descriptivo secundario):** un universo definido solo por escaños omitiría en este CSV a 48 etiquetas que sí registran votos, sin que pueda estimarse su influencia por esa ausencia.
- **PF-CONT-02 (precaución de identidad):** los códigos de los archivos históricos no equivalen a claves jurídicas universales. Variantes de denominación no prueban error ni continuidad legal; contrastar con un registro oficial.
- **PF-CONT-03 (límite de causalidad):** presencia electoral, visibilidad documental, representación y producción de influencia son constructos diferentes; estos dos archivos no permiten medir influencia.
- **PF-CONT-04 (instrumental):** el sistema multiactor puede modelar personas públicas, alianzas y candidaturas sin inferir afiliación privada; los tests se ejecutaron sobre figuras inventadas, no sobre personas verificadas.
- **PF-CONT-05 (riesgo abierto):** no existe cohorte longitudinal persona-semana con first-public-at verificado y fuente primaria suficiente. No usar el éxito retrospectivo en datos finales como pronóstico prospectivo.

Se conservan las evidencias negativas: un intento de acceso externo fallido, falta de censo actual, ausencia de microdatos originales, cero personas cotejadas, y pruebas de código que no constituyen inferencia sociológica. **VSDS=1/3, CT2 predictiva=24/100, CT2 multiactor=20/100; ambas ramas ordinales sin cambios. N1/N2/N3 nuevos=0.**

## Decisión y propuesta de ampliación

**CLOSE_B50 / CLOSE_AB20_R5 / CLOSE_F45**. El usuario pidió continuar hasta agotar autorizaciones previas; se han cerrado formalmente, pero NO equivale a haber conseguido 76 nuevos resultados científicos ni desplegar un fantasy de personas reales.

Próximo bloque sugerido: **30 ciclos con BRANCHING** enfocados en:
- C01–C08: obtener datos RAW del Registro de Partidos, candidaturas oficiales y otras instituciones autonómicas/locales, licencia, fechas, hashes, cobertura real.
- C09–C14: identidad estable, homónimos, sucesiones y coaliciones, adscripciones y cargos fechados; sin inferir militancia privada.
- C15–C20: acontecimientos políticos documentados más allá de cámaras legislativas (declaraciones públicas, campañas, acciones institucionales, organizaciones).
- C21–C25: auditorías sociológicas de subrepresentación documental, visibilidad y no representación, cobertura e incentivos, sin medir influencia causal sin identificación.
- C26–C30: unificar ETL y UI Python, pruebas HTTP/buscador/aplicación y protección de personas, sin crear rankings políticos o puntuar actores reales.

El branching permitirá pasar entre ramas según evidencia. **Las 30 plazas sugeridas NO se consideran autorizadas ni ejecutadas.**

SOLICITO BRANCHING 30 CICLOS
