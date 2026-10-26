# Politics Fantasy League · BR30I · informe final de los 30 ciclos A–J

**Fecha:** 26 de octubre de 2026. **Autorización:** 30 ciclos AB 3.2.1 con BRANCHING, independiente de B50, AB20, F45, BR20H y BR30G. **Resultado:** 30/30 fichas A–J cerradas; 30/30 condiciones de la batería V8 superadas **después** de incorporar los cambios del atlas y UI. Ninguna de estas 30 pruebas debe interpretarse como 30 estudios causales independientes.

## Dictamen

Se ha avanzado de un atlas meramente secundario de etiquetas de candidaturas (59 columnas del CSV provincial de 2023, entre ellas 48 con votos pero sin escaño) hacia una **conciliación externa y documental con la Junta Electoral Central** para agregados provinciales y un subconjunto de opciones sin escaños, más un grafo histórico muy conservador de coaliciones.

| Indicador | Resultado | Clase de evidencia |
|---|---:|---|
| Ciclos A–J autorizados/cerrados | **30/30** | 30 contratos y decisiones documentadas en LEDGER |
| Circunscripciones del Congreso 2023 reconciliadas | **52/52** | BOE/JEC oficial **transcrito manualmente** × CSV secundario |
| Magnitudes oficiales por provincia | **6** | censo, votantes, válidos, candidaturas, blancos, nulos |
| Celdas confrontadas / discordancias | **312 / 0** | comprobación aritmética documental; un solo evento electoral |
| Sumatorio de 59 columnas electorales vs votos a candidaturas | **52/52** | consistencia secundaria corroborada por total oficial |
| Totales nacionales de opciones sin escaños contrastados con Cuadro III JEC | **5/5** | PACMA, CUP-PR, FO, NC-bc, PDeCAT-E-CiU; selección retrospectiva |
| Etiquetas de candidaturas con votos y sin escaño | **48 de 59** | participaciones históricas en archivo secundario, NO partidos legales necesariamente |
| Votos agregados de las 48 etiquetas sin escaños | **606.450 (2,4766 %)** | cuota histórica de votos a candidaturas en el dataset, NO influencia |
| Plazas registradas en páginas de coaliciones JEC/JEP 2023 | **12 + 4 = 16** | HTML JEC transcrito manualmente |
| Siglas de coalición con match exacto único en el atlas | **10** | enlace de acrónimo, NO validación de identidad jurídica |
| Referencias únicamente senatoriales | **2** | excluidas de identificación de candidaturas al Congreso |
| Grafo construido | **75 nodos, 10 aristas** | 59 opciones + 16 referencias de coalición, sin personas |
| Tests JEC/QA V8 después del merge | **30/30 PASS** | verificaciones locales en V8, NO CI limpio Node |
| Tests ejecutados en GitHub Actions / navegador E2E | **No verificados** | workflow creado, no se confirma ejecución |
| Personas públicas reales validadas individualmente | **0** | no se ha construido registro de personas |
| VSDS proyecto | **1/3** | no se eleva por ingeniería o una sola elección |
| CT2 multiactor | **20/100** | ordinal y sin cambio |
| CT2 predictiva parlamentaria | **24/100** | otra rama ordinal, sin cambio |
| Nuevos descubrimientos N1/N2/N3 | **0 / 0 / 0** | no se declara novedad empírica/teórica confirmatoria |

## A. Alcance y naturaleza de las fuentes

La fuente primaria de resultados de 2023 es la [Resolución de 30 de agosto de 2023 publicada en BOE el 1 de septiembre, BOE-A-2023-18907](https://www.boe.es/buscar/doc.php?id=BOE-A-2023-18907), también [vinculada por la JEC](https://www.juntaelectoralcentral.es/cs/jec/elecciones/Generales-julio2023). Se leyó el cuadro I de su PDF oficial y se transcribieron **manualmente** 52 filas con seis números por circunscripción, preservando [texto fuente y aviso de transcripción](JEC_2023_TABLE_I_TRANSCRIPTION.psv). No se descargaron los bytes del PDF al repositorio y **la transcripción no es una firma digital del original**.

Los 52×6 valores transcritos concilian por ID provincial con [anerodata 202307.csv](https://github.com/anerodata/data-elecciones-congreso-espana/blob/main/202307.csv), blob SHA Git **59a7734f0deba570ea87681236ecd4c9008ebd33**. Todos los totales estatales de la transcripción coinciden con los publicados: censo 37.469.458; votantes 24.952.447; válidos 24.688.087; a candidaturas 24.487.414; blancos 200.673; nulos 264.360. No hay discrepancias en este contraste, ni en las 52 sumas de columnas electorales, pero eso **no valida por sí solo todos los rótulos de listas o personas**.

Un segundo contraste contra **Cuadro III** de esa misma publicación JEC confirmó cinco totales de candidaturas sin escaños: PACMA **169.237**, CUP-PR **99.644**, Frente Obrero **46.274**, NC-bc **45.595**, PDeCAT-E-CiU **32.016**. **No son cinco fuentes independientes**: son cinco observaciones del mismo original oficial; además su selección fue posterior a la exposición del contenido secundario.

Para coaliciones se consultaron dos recursos oficiales distintos: [JEC central](https://www.juntaelectoralcentral.es/cs/jec/elecciones/coalicionesJEC?fechaeleccion=2023-07-23&tipoeleccion=Elecciones+Generales), 12 entradas, y [juntas provinciales](https://www.juntaelectoralcentral.es/cs/jec/informacion/enlaces/GENERALES_2023Abrl_CoalicionesJEP), 4 entradas. Se preservaron la autoridad, ámbito territorial, siglas y cámara indicada. El algoritmo enlaza **solo siglas textualmente idénticas y únicas**, sin inferir que dos denominaciones ambiguas sean la misma persona jurídica, ni la composición de los partidos integrantes. Diez enlaces exactos; cuatro restantes sin match de sigla y dos referencias solo senatoriales. «Sin match» no quiere decir «no es coalición».

## B. Interpretación sociológica y límites

El dato medible es **participación electoral documentada sin representación congresual**: 48 etiquetas históricas del CSV obtuvieron votos positivos y cero escaños; en conjunto, 606.450 votos (2,4766% de votos a candidaturas en el archivo). Este valor no permite ordenar partidos por «influencia», estimar su efecto causal sobre decisiones, atribuir calidad democrática, inferir ideología de personas, predecir una futura elección o asegurar que 48 registros son 48 partidos jurídicamente distintos. Los registros pueden referirse a **listas, agrupaciones y coaliciones**.

El número de etiquetas con al menos un voto por provincia varía entre 8 y 14 en esta fuente, sin que ese recuento mida por sí solo pluralismo social o diversidad ideológica.

Lo que se puede defender a partir del contraste es **mejor integridad documental de recuentos agregados de una elección concreta**, no una teoría de la influencia de actores políticos no parlamentarios. Los modelos de rol público, instituciones, afiliaciones temporalmente documentadas y eventos extraparlamentarios siguen sin un censo de personas reales con verificación individual.

## C. Trabajo de ingeniería y producto

Se añadieron estos artefactos al repositorio:
1. [scripts/jec2023_audit.mjs](../../scripts/jec2023_audit.mjs): parsers/validadores para tabla oficial transcrita, contraste por provincia, cinco totales BOE III, cruce conservador de coaliciones, diversidad de opciones, proporción de votos sin escaños, corrupción simulada y puerta de evidencia.
2. [scripts/run_jec2023_audit.mjs](../../scripts/run_jec2023_audit.mjs): replay Node offline con un CSV local de la versión secundaria 2023. La utilidad **no requiere internet**; el operador aporta el archivo.
3. [tests/test_jec2023_audit.mjs](../../tests/test_jec2023_audit.mjs): seis tests Node para BOE nacional, referencia corrupta, códigos duplicados, cinco totales BOE III, coaliciones y puerta temporal.
4. [data/observatory/electoral_atlas_2023.json](../../data/observatory/electoral_atlas_2023.json): 59 opciones con nueva evidencia de cinco contrastes directos y diez relaciones de siglas; además constancia explícita de **312 cotejos manuales**.
5. [data/observatory/electoral_actor_graph_2023.json](../../data/observatory/electoral_actor_graph_2023.json): 59 nodos opción y 16 nodos coalición JEC/JEP, 10 aristas de match estricto; ningún nodo de persona real ni afiliación inferida.
6. [src/politics_fantasy/electoral_atlas.py](../../src/politics_fantasy/electoral_atlas.py): adaptador read-only Python que clasifica y limita el estado documental. No utiliza datos para calificar personas.
7. [src/politics_fantasy/web/app.js](../../src/politics_fantasy/web/app.js): pestaña Atlas enriquecida con celdas conciliadas y distinción de referencia de coalición.
8. [.github/workflows/politics-fantasy-evidence.yml](https://github.com/GalexY3/Metodologia-AB/blob/main/.github/workflows/politics-fantasy-evidence.yml): CI declarado con pruebas Node/Python, recuperación de CSV, verificación SHA blob Git y replay oficial. **La creación del workflow está confirmada; no se ha observado su ejecución ni un job PASS.**

### Reproducción

Desde la raíz del proyecto, con Node 20:

```bash
node --test tests/test_jec2023_audit.mjs
node --test tests/test_political_universe.mjs
node scripts/run_jec2023_audit.mjs /ruta/al/202307.csv > reporte_JEC.json
```

El archivo 202307.csv esperado debe corresponder al blob Git SHA de procedencia **59a7734f0deba570ea87681236ecd4c9008ebd33**; el flujo CI verifica esa revisión y la utilidad CLI offline ahora **rechaza directamente** archivos cuyo blob Git SHA1 no sea `59a7734f0deba570ea87681236ecd4c9008ebd33`; también publica SHA-256 del archivo para auditorías reproducibles. Para evaluación prospectiva deberá emplearse un campo materializado con fecha de disponibilidad original comprobable.

## D. Contabilidad de los 30 ciclos A–J

Cada ficha individual en [LEDGER.json](LEDGER.json) contiene pregunta A, hipótesis rivales B, discriminante C, instrumento D, ejecución E, análisis adversarial F, independencia G, actualización H, juicio I y decisión J. La [batería de 30 endpoints](../../scripts/br30i_suite.mjs) pasó completa en **V8** después de enriquecer el atlas y el frontend, según [RESULTS_C01_C30_POST_MERGE.json](RESULTS_C01_C30_POST_MERGE.json).

| Rama | Ciclos | Evidencia |
|---|---|---|
| Conciliación oficial y conservación | **C01–C11** | BOE/JEC oficial manual × archivo secundario, suma interna, cinco opciones BOE III |
| Coaliciones, identidad y no representación | **C12–C20** | páginas JEC/JEP oficiales + grafo de siglas + historia 1977–2019 secundaria, descriptivos |
| Procedencia, tiempo y controles adversariales | **C21–C25** | gates de disponibilidad, mutate/duplicate control, prevención de inferencias privadas |
| Integración producto y cierre | **C26–C30** | lectura estática de Python/HTML/CI + batería V8; **sin HTTP real ni E2E ejecutado** |

Se conserva en [PREREG_C01_C30.json](PREREG_C01_C30.json) que parte del contraste documental (C01–C11) ya estaba visible **antes de congelar el contrato**. No es un prerregistro ex ante confirmatorio. Las 30 fichas constituyen un bloque de trabajo metodológico con branching ejecutado; **no 30 replicaciones independientes**. El antiguo expediente BR30G permanece distinto (un corpus de votos parlamentarios 2023–2026); no mezclar votos legislativos con votos de elecciones generales.

## E. Priors, fallos negativos y límites

Se añaden diez priors PF-I01–I10 a [PRIORS_DELTA.md](PRIORS_DELTA.md), con fuentes, evidencia a favor/en contra, falsadores y alcance. Se conserva todo antecedente de PF-B50, PF-AB20, PF-F45, BR20H y BR30G.

Tres advertencias nuevas decisivas:
- **Alfabeto legal**: una «opción electoral» y una «coalición JEC» pueden tener nombres parecidos, pero son unidades institucionales distintas; el enlace por sigla no certifica pertenencia de personas o partidos.
- **Aritmética no semántica**: 312 coincidencias oficiales permiten mayor confianza en los recuentos agregados, pero no autentican automáticamente cada atributo de cada persona o campaña.
- **Temporalidad**: la fecha de publicación del BOE es histórica; no certifica cuándo un dato derivado, una etiqueta del CSV o una revisión llegó a estar disponible para un modelo. Sin `first_public_at` no habilitar forecast as-of.

**AB-DECIDE:** `CLOSE_BR30I / CONTINUE_IF_NEW_PRIMARY_DATA`. No quedan plazas del bloque: 30/30 cerradas. CT2 multiactor 20/100 y predictiva parlamentaria 24/100 sin cambios; valor VSDS 1/3. N1/N2/N3 científicos nuevos = 0.

## F. Próximo bloque propuesto, pendiente de concesión

**30 ciclos con BRANCHING**, distribuidos adaptativamente, y sin rellenar cuotas cuando falte evidencia:
- 8 adquisición e ingesta de **Registro de Partidos Políticos y candidaturas proclamadas** con originales legalmente reutilizables, licencias y primer momento de disponibilidad.
- 6 resolución de identidad pública/roles históricos y coaliciones, sin inferir militancia privada.
- 7 eventos públicos municipales/autonómicos y no institucionales, con corpus temporal heterogéneo y comparación de fuentes.
- 5 metodologías de inferencia observacional/denominadores, sesgos de visibilidad y modelos temporales con comparadores competentes.
- 4 pruebas de producto en Node/Python y navegador E2E, mejoras de seguridad, versiones de reglas y despliegue local reproducible.

La nueva campaña requiere **otra fuente primaria de actores y personas**, no repetir 30 tests sobre el mismo 202307.csv. Solo si existe base documental comparable podrían efectuarse estudios reales de actividad e incentivos sin atribuir influencia o valor político global.

SOLICITO BRANCHING 30 CICLOS
