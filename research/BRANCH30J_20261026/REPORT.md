# Politics Fantasy League — BR30J, 30 ciclos AB 3.2.1 con BRANCHING

**Fecha:** 26 octubre 2026. **Concesión del usuario:** 30 ciclos adicionales. **Estado:** 30/30 A–J adjudicados; 30/30 tests de aceptación ejecutados en V8 con estado PASS. **El bloque NO contiene 30 nuevos experimentos empíricos ni un registro oficial completo.** No se han obtenido nuevos archivos RAW originales de RPP/Interior/Congreso ni conciliado individuos reales.

## 1. Resumen ejecutivo

Este bloque sustituye la estrategia de añadir más análisis sobre los mismos votos parlamentarios por una infraestructura **source-first** para representar actores y acontecimientos políticos públicos **con o sin escaño**. La infraestructura separa tipos jurídicos, identidades estables, roles públicos, coaliciones, acontecimientos, intervalo de validez, fecha de publicación, fecha de captura, integridad de bytes y condiciones de reutilización. No asigna valoraciones ideológicas ni de «influencia» a individuos.

| Hecho | Resultado | Validez |
|---|---:|---|
| Ciclos autorizados | 30 | 30 fichas A–J publicadas |
| A–J cerrados | **30/30** | 4 con STOP_R5 por no obtener filas originales, resto ingeniería/documentación |
| Comprobaciones V8 ejecutadas | **30/30 PASS** | Una fixture compartida e inspección de catálogos; no 30 replicaciones |
| Fuentes identificadas en el catálogo | **8** | 6 referencias oficiales y 2 fuentes secundarias, sin originales nuevos adquiridos |
| Filas originales oficiales nuevas incorporadas | **0** | Acceso a archivos RPP/XLSX/CSV de organismos no completado |
| Personas públicas reales individualmente conciliadas | **0** | No registrar afiliaciones privadas ni inferirlas |
| Extracto secundario municipal 2023 | **41 etiquetas** | Transcripción documental parcial de RTVE, no censo de partidos |
| Fixture de integración | 7 entidades, 4 roles, 2 versiones de evento, 3 fuentes, 1 declaración | Todas las personas/organizaciones ficticias |
| Duplicaciones de evento detectadas en fixture | 1 | Revisión pendiente, nunca autocausalidad |
| Captura as-of de eventos (mayo/noviembre 2026, fixture) | 1 / 2 | La captura tardía se excluye del corte temprano |
| Adaptador Python + ruta `GET /api/evidence-readiness` | Implementados | Python runtime/HTTP real no ejecutados en esta sesión |
| Importador offline SHA256 y pruebas Node de subprocess | Publicados | No ejecutados como Node real en esta sesión |
| GitHub Actions con nuevas suites | Actualizado | No se ha verificado un job PASS |
| Nuevos N1/N2/N3 científicos | **0 / 0 / 0** | Sin prueba independiente con universo político real |
| VSDS | **1/3 → 1/3** | No se eleva por la ingeniería |
| CT2 multiactor | **20/100 → 20/100** | Ordinal, no probabilidad |
| CT2 predictiva parlamentaria | **24/100 → 24/100** | Otra rama, ordinal |
| DRIFT | **D1.3** | Continuidad de población multiactor y prioridad a instrumentación |

## 2. Fuentes nuevas y resultados de adquisición

Se verificaron documentalmente las siguientes superficies oficiales:

- [Consulta del Registro de Partidos Políticos, Interior](https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos). Proporciona una aplicación con filtros y PDF de resultados; **no se descargó ni validó un padrón de organizaciones**.
- [Resultados electorales, Interior](https://datos.gob.es/es/catalogo/e00003801-resultados-electorales). Incluye XLSX de Congreso, Senado, electos, Parlamento Europeo y municipios; **no se obtuvieron los bytes de ninguna distribución de esta campaña**.
- [JEC, generales de julio 2023](https://www.juntaelectoralcentral.es/cs/jec/elecciones/Generales-julio2023). Publica candidaturas proclamadas y resultados; se preserva que un candidato/lista no es necesariamente un partido registrado. Los cuadros agregados de 2023 ya trabajados en BR30I son antecedentes, no nuevos datos individuales.
- [Congreso, open data de diputados](https://www.congreso.es/es/opendata/diputados). Admite CSV, JSON y XML de varias legislaturas, pero no es todo el campo político.
- [Open Data Bizkaia, elecciones municipales 2023](https://datos.gob.es/es/catalogo/l02000048-resultados-de-elecciones-a-juntas-generales-y-municipales), con distribuciones reutilizables; sin captura materializada en este entorno.
- [BOE/JEC, resultados locales 2023](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-16886), documentos oficiales de municipios y concejales.
- [votomunicipal.es, datos abiertos](https://votomunicipal.es/datos-abiertos/): publicación independiente, declara un JSON municipal 2023 de 2,3 MB con votos y concejalías por candidatura y licencia CC BY 4.0. **Se identificó la oferta y sus términos publicados, pero NO se descargó el JSON**.

**Resultado R5:** la adquisición de filas oficiales completas del RPP y la vinculación de la población de personas de organismos diferentes permanecen **STOP_R5** por falta de originales y control de primera disponibilidad. Se detuvieron como problemas empíricos, no se simularon descargas ni se crearon personas políticas inventadas atribuyéndolas a España. [SOURCE_CATALOGUE.json](SOURCE_CATALOGUE.json) distingue metadatos, fuente capturada y derechos.

### Otro universo: municipales 2023

Se preservó [una muestra documental secundaria con 41 etiquetas publicadas en los resultados municipales de RTVE](RTVE_MUNICIPAL_2023_SECONDARY_SAMPLE.json). Son datos de votos y concejalías históricas de 2023; varias etiquetas corresponden a coaliciones o agrupaciones y **no se afirma que sean 41 partidos jurídicos individuales ni que constituyan un censo exhaustivo**. No hay autenticación independiente de los datos originales municipales ni acuerdo conocido sobre licencias de distribución de la tabla completa. Esta muestra **no se incorporó como verdad oficial a los perfiles de personas**, ni se utilizó para calcular influencia, rendimiento o ranking.

La información municipal no se fusiona automáticamente con etiquetas de generales 2023 ni con códigos de rOpenSpain de 1977–2019. Coincidir en sigla no constituye evidencia suficiente de continuidad legal.

## 3. Software construido

### 3.1 Almacén de evidencias multiactor

[political_universe.mjs](../../src/politics_fantasy/political_universe.mjs), creado antes, permitía representar tipos de actores ficticios. La nueva pieza [evidence_warehouse.mjs](../../src/politics_fantasy/evidence_warehouse.mjs) amplía el sistema:
- Conjuntos explícitos `sources`, `entities`, `roles`, `events`, `claims`, `collisions` y revisiones. Identidad por namespace e ID, homónimos a cola de revisión.
- Partidos, federaciones, coaliciones, agrupaciones de electores, candidaturas, plataformas, sindicatos, organizaciones de interés, organismos y personas **con rol público documental**, sin escaño obligatorio.
- Rol `PUBLIC_CANDIDATE` no implica militancia de partido, `COALITION_PARTICIPANT` requiere afirmación y entidad explícitas. Los cargos/estados oficiales requieren documento de organismo o fixture declarada.
- `valid_from/valid_to` con intervalo semiabierto, `first_public_at` separado de `observed_at` y queries temporales as-of que bloquean observaciones incorporadas después del corte.
- Acontecimientos públicos fuera del parlamento, relaciones entre actores, declaraciones temáticas literales con fuente, modificaciones y detección de colisión de eventos por ID externo.
- Ausencia de censo => `known_population_denominator:null` y `coverage_rate:null`; nunca imputar cobertura española a partir del número de registros capturados.
- Controles de atributos sensibles y rechazo de puntuaciones de influencia/ideología. No se emiten perfiles ni valoraciones de personas reales.

### 3.2 Importación en bytes y trazabilidad criptográfica

[ingest_political_evidence.mjs](../../scripts/ingest_political_evidence.mjs) es una nueva CLI Node offline: recibe un JSON con referencias a ficheros fuente locales, confina la lectura al directorio del bundle, limita tamaños, recalcula **SHA256** del fichero y rechaza divergencias. Emite solo auditoría agregada, recuentos y advertencia `original_publisher_authenticated:false`. **Un hash correcto no prueba que el fichero sea oficial**; para certificar origen sería necesaria una descarga autenticada o comprobación independiente con URL, fecha, firma o hash publicado por el emisor.

Se han escrito pruebas de subprocess [test_evidence_ingest_cli.mjs](../../tests/test_evidence_ingest_cli.mjs) para rechazo de huella alterada, clases incorrectas, escape del directorio y as-of. **Su ejecución real en Node no se ha observado**. El motor y su suite de [30 assertions](../../tests/test_evidence_warehouse.mjs) sí se ejecutaron como funciones puras V8, con 30/30 PASS.

### 3.3 Producto local y pruebas Python

Nueva [API de estado sintético](../../src/politics_fantasy/evidence_warehouse_status.py) enlazada a `GET /api/evidence-readiness` en [server.py](../../src/politics_fantasy/server.py). La [interfaz](../../src/politics_fantasy/web/app.js) muestra que el universo multiactor es posible sin escaño, pero las siete entidades y los eventos son **inventados**, sin nombres personales expuestos ni rating político. La sintaxis de la versión actual del JS de interfaz ha pasado el parser V8.

Se publicaron [tests Python del adaptador](../../tests/test_evidence_warehouse_status.py) y [smoke HTTP sobre puerto local efímero](../../tests/test_evidence_http_smoke.py), incluido rechazo de cabecera `Host` externa. El [workflow CI](https://github.com/GalexY3/Metodologia-AB/blob/main/.github/workflows/politics-fantasy-evidence.yml) incorpora estos tests junto a los de Node. **No se ha observado su ejecución real aquí, ni se ha validado despliegue web público**. El servidor demo está limitado a loopback y carece de un modelo seguro multiusuario.

## 4. Resultados científicos por rama y contabilidad A–J

El [prerregistro exploratorio](PREREG.json) fijó 30 contratos antes del nuevo módulo, con un corpus anterior conocido, por lo que **no** es un experimento confirmatorio ciego. Cada ficha A–J individual está en [LEDGER.json](LEDGER.json).

| Rama | Unidades | Resultado J |
|---|---|---|
| C01–C04: fuentes RPP, Interior, JEC, municipios | 4 | Metadatos documentados; **STOP_R5** de ingesta de originales/individuos |
| C05–C08: manifest, revisión, SHA, licencias | 4 | Reglas de rechazo V8 PASS; autenticación de editor original y CLI nativa pendientes |
| C09–C14: identidad y roles | 6 | Aceptaciones sintéticas PASS, ninguna afiliación legal real cotejada |
| C15–C21: eventos extra-parlamentarios y privacidad | 7 | Aceptaciones sintéticas PASS, sin resultados causales |
| C22–C26: cobertura, denominadores, forecast | 5 | Reglas de medición PASS, **NO** se entrenó un forecast político real |
| C27–C30: producto, QA, gobernanza | 4 | Integridad de fixture/inspección de fuente PASS, Node/Python/HTTP nativo sin certificación |
| **Total** | **30** | 30 A–J concluidos, pero **cero estudios de campo independientes ejecutados** |

La ejecución `E` de todos los ciclos registra una comprobación de aceptación V8; la `E` de los cuatro primeros NO significa descarga y reconciliación de sus datos originales. Las decisiones J fijan si el trabajo queda cerrado como ingeniería o detenido por falta de fuente. Cada `G` distingue explícitamente ausencia de replicación externa; cada `F` incluye un adversario o riesgo concreto. Las pruebas comparten fixture y diseño, de modo que no puede reivindicarse error estadístico controlado por 30 falsadores independientes.

El resultado de [RESULTS_FINAL.json](RESULTS_FINAL.json) es 30/30 PASS, con 7 entidades, 4 roles, 2 versiones de evento, 3 fuentes y una declaración, todo sintético. El mismo evento externo aparece dos veces y el auditor deja una incidencia para revisión; no supone dos acontecimientos. Una captura tardía no entra en la consulta as-of anterior.

### Límites e incidencias preservadas

1. No existe actualmente un fichero nuevo con las filas oficiales RPP original + su huella autentificada + licencia y fecha histórica. Esto limita decisivamente la validez científica.
2. El módulo `RAW_CAPTURED` puede comprobar integridad de bytes aportados, pero una declaración de URL oficial por parte de un tercero sigue siendo **autodeclarada**. El sistema no eleva evidencias o puntúa personas por ello.
3. El ejemplo 7 entidades sirve para QA, no para estimar la proporción de partidos o plataformas nacionales, ni sesgos de cobertura empíricos.
4. Las cuentas RTVE municipales son secundarias, parciales, seleccionadas e históricas. No describen organizaciones actuales.
5. Las pruebas de subprocess Node, Python pytest, HTTP y GitHub Actions están escritas, pero no se reporta ningún PASS de esas ejecuciones en este entorno.
6. Se conserva la bifurcación de CT2 y su ordinalidad, con [trayectoria de 30 posiciones](CT2_TRAJECTORY.csv). No actualizar por cantidad de código.

## 5. Priors y propuesta de continuación

Ocho nuevos priors PF-J01–PF-J08 en [PRIORS_DELTA.md](PRIORS_DELTA.md), con contraevidencia, falsadores, procedencia y alcance. El ledger global [research/PRIORS.md](../PRIORS.md) debe integrar su índice sin eliminar PF-P ni los del BR30G, BR20H y BR30I.

**AB-DECIDE = CLOSE_BR30J / STOP_R5_ORIGINAL_SOURCE / CONTINUE_ENGINEERING_CONDITIONAL**. Los 30 ciclos concedidos están cerrados como trabajos A–J; **las preguntas científicas sobre personas y eficacia política siguen abiertas**, sin nuevas puntuaciones N1/N2/N3 y con VSDS 1/3. No crear ranking o scoring político de personas a partir de visibilidad documental.

### Próximo bloque propuesto: 20 ciclos BRANCHING bajo hitos de evidencia

- C01–C05: obtener y **ejecutar** capturas verificables del Registro de Partidos, candidaturas municipales 2023 (fuentes CC BY originales/terceros con atribución) y Congreso histórico; registrar licencias y checksums calculados. **Si siguen inaccesibles, aplicar STOP_R5 sin dedicar otros cinco ciclos al mismo catálogo.**
- C06–C10: ETL de fuentes reales con campos, schemas, fechas e IDs legales; evaluación de cobertura efectiva y cambios organizacionales; conflictos y homónimos.
- C11–C15: corpus público de eventos extradiputacionales con ventana temporal y fuentes adversariales, sin datos privados ni inferencia causal automática.
- C16–C20: verificar en Node/Python/HTTP los runners con datos materializados, pruebas de navegación, seguridad, reglas de liga separadas del conocimiento empírico y comparadores convencionales.

El nuevo bloque no está autorizado por cerrar este informe. **No recomendaría ampliar CT2 hasta contar con material oficial con fuente auténtica y contraste independiente.**

SOLICITO BRANCHING 20 CICLOS
