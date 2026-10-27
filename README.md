# Politics Fantasy League — Political Data Science Laboratory

**Cola de trabajo pendiente para Codex:** [tareas_codex/README.md](tareas_codex/README.md) y [BACKLOG.json](tareas_codex/BACKLOG.json). Las tareas están **pendientes o bloqueadas**, no ejecutadas; [issue #17](https://github.com/GalexY3/Metodologia-AB/issues/17). No requieren acceso a Codex para consultarse.

## Reanudación y fuentes — 27/10/2026

[Catálogo central de fuentes, acceso y límites](docs/CATALOGO_FUENTES.md) · [Estado del mapa y autorizaciones](ab_atlas/CURRENT.md) · [Continuación AB-H y reconciliación de ramas](research/ABH_RECON_20261027/REPORT.md) · [Guía para continuar en ChatGPT](docs/CONTINUIDAD_CHATGPT_20261027.md). Estas novedades están en la rama de investigación; el historial de campañas que sigue se conserva con sus fechas y alcances originales.

## BR8N — candidaturas originales y navegador real (26/10/2026)

**8/8 ciclos AB con BRANCHING completados:** siete pruebas o integraciones técnicas/documentales aceptadas y un **PARTIAL_R5** porque aún falta identidad real de personas y partidos. [Ledger A–J](research/BRANCH8N_20261026/LEDGER.json) · [Informe](research/BRANCH8N_20261026/REPORT.md) · [Priors](research/PRIORS.md).

**Dos fuentes BOE originales de la misma elección 2023 están capturadas y auditadas**: resultados 2023 BOE 18907 (52×6=312 cifras), y proclamación BOE 15066 (4.298.580 bytes, SHA256 `d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`). De la última se extrajeron **8 etiquetas de candidaturas al Congreso en Albacete**, en [archivo de evidencia](data/observatory/boe_2023_albacete_verified.json). Cruce por sigla única **8/8** con [atlas secundario 2023](data/observatory/electoral_atlas_2023.json): **4 con votos nacionales, cero escaños** (FO, PACMA, PUM+J, Recortes Cero). Son candidaturas, NO un registro jurídico de ocho partidos ni identidad individual de personas. [Analizador conservador](scripts/audit_candidacy_crosswalk.mjs) y [negativos](tests/test_audit_candidacy_crosswalk.mjs).

**Producto local:** `GET /api/verified-candidacies` devuelve siglas, fecha, provincia, fuente y SHA-256; [Atlas](src/politics_fantasy/web/app.js) integra el documento y advierte de límites. Ningún perfil ni puntuación sobre figuras reales. [GitHub Actions 40316425686](https://github.com/GalexY3/Metodologia-AB/actions/runs/40316425686): tres jobs verdes, **98 pruebas Node + 59 Python**, navegador Chromium real comprobó atlas, mercado, progreso **con 10 barras semánticas CSP-safe** y Host externo rechazado 403. No equivale a despliegue público ni acceso multiusuario seguro.

**Métrica vigente revisión 3: 36,350 % (36,4 % redondeado)**, antes 35,450 %; **+0,900 puntos por evidencia de UI/QA**, cambio de scope 0 (36 hitos/9 vías). [Scope V3](product/progress_scope_v3_20261026.json) · [snapshot V3](product/progress_snapshot_v3_20261026.json) · [tabla de nueve subvías](docs/PROGRESO_Y_ALCANCE_v3.md). Seis gates de lanzamiento sin cumplir. VSDS 1/3 y CT2 multiactor 20/100, predictiva parlamentaria 24/100 sin cambios.

## BR12M — primer documento oficial original y CI nativa, 12/12 (26/10/2026)

**12/12 ciclos AB 3.2.1 con BRANCHING cerrados**: 9 adjudicaciones técnicas/documentales exitosas y 3 STOP_R5 (dos rutas fuente oficiales inaccesibles y sin RPP/identidad de personas reconciliada). [Informe final](research/BRANCH12M_20261026/REPORT.md) y [ledger A–J](research/BRANCH12M_20261026/LEDGER.json).

**Resultados verificados, no solo código:** [GitHub Actions run 40258776701](https://github.com/GalexY3/Metodologia-AB/actions/runs/40258776701): siete suites con **91 tests Node**, pytest **50 tests Python**, todos PASS, dos jobs success. Se descargó mediante HTTPS y verificó SHA256 el PDF oficial [BOE-A-2023-18907](https://www.boe.es/boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf): **1.915.000 bytes, SHA256 `f2146cfbf00d2b6eb6f8dd0dcdebc1e10298019589b2254e244e0ebc513d2f8a`**. Reextracción real `pdftotext` del cuadro I: **52 provincias × seis cifras = 312/312 coincidentes** con nuestra transcripción de 2023. Se conserva el original temporalmente en artefacto privado Actions, expira 29/10/2026; la URL, SHA y script de captura persisten. El cuadro no es una cohorte de personas o partidos RPP.

Negativos: Congreso JSON de agosto 2026 devolvió 404 en las dos URLs probadas; el XLSX de Interior no pasó validación TLS; se dejó constancia R5 sin desactivar certificados. **0 personas públicas reales reconciliadas, 0 registros jurídicos originales RPP adquiridos**, sin puntuaciones reales.

**Progreso vigente: PFL-V1-20261026 revisión 2 = 35,450% (35,5% visible).** Antes era 33,725%; mejora **+1,725 puntos por trabajo verificado**, **0 por scope** (las 9 vías y 36 hitos siguen intactos). [Snapshot V2](product/progress_snapshot_v2_20261026.json), [scope V2](product/progress_scope_v2_20261026.json), [scope V1 histórico](product/progress_scope_v1.json) y [documentación](docs/PROGRESO_Y_ALCANCE_v1.md). **Seis condiciones bloquean lanzamiento público**; VSDS=1/3 y CT2 sin cambios.

Software añadido: [captura oficial y SHA](scripts/capture_official_sources.py), [reconciliación automática PDF](scripts/verify_boe_table_pdf.py), [tests adversariales](tests/test_verify_boe_table_pdf.py), [API progreso](src/politics_fantasy/progress_api.py) y [pestaña web](src/politics_fantasy/web/app.js). [Priors de BR12M](research/PRIORS.md). N1/N2/N3 científicos nuevos: 0.

## BR20K — avance del proyecto con alcance dinámico (26/10/2026)

**20/20 ciclos AB 3.2.1 con BRANCHING concluidos** (13 verificaciones locales/documentales satisfechas, 4 STOP_R5 de fuentes reales e identidades, 3 trabajos de código con ejecución nativa todavía no verificada). No se presentan como 20 estudios empíricos, ni hay nuevas filas oficiales RPP autentificadas.

**Índice de progreso PFL-V1-20261026 = 33,725 % (33,7 % redondeado)**, calculado sobre 9 sublíneas y 36 hitos ponderados. Estado de lanzamiento **NO LISTO**, seis dependencias críticas pendientes. Es madurez de trabajo contra un alcance acordado, **no la probabilidad de éxito, coste temporal o valor científico**. Si el alcance cambia, nuevo revisionado y comparación: añadir hipotéticamente cobertura municipal exhaustiva reduce el índice a **32,330 %** por efecto de scope **−1,395 puntos**, con efecto trabajo 0. El ejemplo **NO está adoptado como scope actual**.

- [Método, pesos y las nueve vías](docs/PROGRESO_Y_ALCANCE_v1.md) · [Alcance V1](product/progress_scope_v1.json) · [Snapshot congelado](product/progress_snapshot_v1_20261026.json)
- [Motor JS de cálculo/revisión](src/politics_fantasy/progress_model.mjs) · [CLI offline](scripts/progress_report.mjs) · [20 pruebas de modelo](tests/test_progress_model.mjs), **20/20 comprobaciones puras V8**.
- [Panel web Progreso y /api/progress](src/politics_fantasy/web/app.js) · [adaptador Python](src/politics_fantasy/progress_api.py); tests Python/HTTP publicados y CI actualizado, **sin ejecución nativa acreditada**.
- [Informe BR20K completo](research/BRANCH20K_20261026/REPORT.md) · [ledger individual A–J](research/BRANCH20K_20261026/LEDGER.json) · [resultados](research/BRANCH20K_20261026/RESULTS.json) · [nuevos priors PF-K01–PF-K06](research/PRIORS.md).

La meta v1 **no** incluye perfilar votantes, inferir mérito/ideología individual o recopilar toda comunicación informal. Fuentes y personas públicas auténticas siguen pendientes: se confirmó la legibilidad documental de un endpoint JSON del Congreso de julio de 2026, pero sus bytes íntegros no se integraron ni fueron autentificados. VSDS 1/3 y CT2 previas sin cambios.

## BR30J — universo multiactor con pruebas de evidencias (26/10/2026)

**Cerrados 30/30 contratos AB A–J con BRANCHING**, distinguiendo **4 cierres STOP_R5 por falta de archivos oficiales originales** de **26 aceptaciones de infraestructura/medición**, de las cuales algunas son revisión estática. **30/30 checks V8 PASS sobre un universo inventado y catálogos**, no 30 experimentos sociológicos independientes ni datos de personas reales validados.

- **Ocho fuentes catalogadas:** Registro de Partidos, Interior, JEC, Congreso, open data municipal, BOE y dos editoriales secundarias. Excepto el CSV de generales 2023 anteriormente analizado, las distribuciones son metadatos de acceso **sin ficheros oficiales originales descargados**. [Inventario](research/BRANCH30J_20261026/SOURCE_CATALOGUE.json).
- **Nuevo almacén de hechos** [evidence_warehouse.mjs](src/politics_fantasy/evidence_warehouse.mjs): actor/organización/candidatura/evento/rol, conflictos de identidad, intervalos históricos y capturas, control de eventos duplicados, sin inferir afiliación privada o influencia ni inventar denominador de cobertura.
- **Nuevo importador offline** [ingest_political_evidence.mjs](scripts/ingest_political_evidence.mjs) con SHA256 **recalculado** del archivo y rutas confinadas; su resultado sigue **sin autenticar al emisor** por disponer de un hash. [Tests V8](tests/test_evidence_warehouse.mjs) 30/30 comprobados. [Tests de CLI Node](tests/test_evidence_ingest_cli.mjs) escritos pero no ejecutados aquí.
- **Nuevo ejemplo íntegramente ficticio** [actor_evidence_fixture_30j.json](examples/actor_evidence_fixture_30j.json): 7 entidades, 4 roles, 2 versiones de evento, 3 fuentes, 1 declaración. Ninguna persona auténtica.
- [Resultados municipales 2023 de RTVE, 41 etiquetas históricas](research/BRANCH30J_20261026/RTVE_MUNICIPAL_2023_SECONDARY_SAMPLE.json): *muestra parcial de un portal secundario*, no censo de partidos ni fuente original. [votomunicipal.es](https://votomunicipal.es/datos-abiertos/) anuncia microdatos municipales CC BY 4.0; se documentó su disponibilidad, **no se descargaron**.
- **App**: `GET /api/evidence-readiness` con [adaptador Python](src/politics_fantasy/evidence_warehouse_status.py), panel integrado en [frontend del observatorio](src/politics_fantasy/web/app.js), datos agregados exclusivamente ficticios. [Pruebas Python](tests/test_evidence_warehouse_status.py) y [prueba HTTP loopback](tests/test_evidence_http_smoke.py) publicadas, no ejecutadas localmente en este turno; [CI de GitHub](https://github.com/GalexY3/Metodologia-AB/blob/main/.github/workflows/politics-fantasy-evidence.yml) actualizado, job no verificado.

**Artefactos de investigación:** [Informe BR30J](research/BRANCH30J_20261026/REPORT.md) · [ledger 30 A–J](research/BRANCH30J_20261026/LEDGER.json) · [prereg exploratorio](research/BRANCH30J_20261026/PREREG.json) · [resultados finales y límites de ejecución](research/BRANCH30J_20261026/RESULTS_FINAL.json) · [priors PF-J01–J08](research/PRIORS.md).

**VSDS 1/3; CT2 multiactor 20/100 y CT2 predictiva parlamentaria 24/100 sin cambio. N1/N2/N3 nuevos=0.** El siguiente bloque propuesto (no autorizado) es 20 BRANCHING condicionados a obtener primero originales con procedencia y a ejecutar el código nativamente; no más análisis repetidos del CSV 2023.

## BR30I — 30 ciclos AB con contraste oficial documental (26/10/2026)

**30/30 ciclos A–J completos** sobre una nueva rama de conciliación de los resultados electorales de 2023 con el cuadro oficial de la JEC/BOE, coaliciones y producto. **30 checks V8 PASS**, pero NO 30 experimentos de campo independientes; algunos son controles aritméticos dependientes, otros auditorías documentales y los últimos comprobaciones estáticas de integración.

La evidencia documental nueva: **52/52 provincias × seis magnitudes = 312/312 coincidencias** entre BOE/JEC Cuadro I, transcrito manualmente, y `anerodata 202307.csv`; **52/52 sumas de 59 opciones** igualan los votos a candidaturas; **cinco totales nacionales** de listas sin escaños concilian con Cuadro III JEC. Fuente primaria **consultada** pero PDF original **no descargado ni certificado criptográficamente**. En 2023, las **48/59 etiquetas con votos sin escaños** suman **606.450 votos (2,48% de los votos a candidaturas)**, sin medir mérito, influencia, ideología, ni número de partidos inscritos.

Se diferencian 12 referencias de coaliciones JEC y cuatro provinciales JEP; **10 enlazan por siglas exactas** con el archivo electoral, pero el vínculo no atribuye partidos integrantes ni personas. [Grafo fuente](data/observatory/electoral_actor_graph_2023.json): 59 etiquetas + 16 coaliciones, 10 aristas, **cero personas evaluadas**. El [Atlas](data/observatory/electoral_atlas_2023.json) y [pestaña web](src/politics_fantasy/web/app.js) muestran evidencia JEC por etiqueta. Se añadió [runner offline](scripts/run_jec2023_audit.mjs), [tests Node](tests/test_jec2023_audit.mjs), y [workflow CI](https://github.com/GalexY3/Metodologia-AB/blob/main/.github/workflows/politics-fantasy-evidence.yml) **creado pero aún sin ejecución verificada**; el servidor HTTP Python y E2E visual aún no verificados.

- [Informe final BR30I](research/BRANCH30I_20261026/REPORT.md)
- [Ledger 30 fichas A–J](research/BRANCH30I_20261026/LEDGER.json)
- [Priors PF-I01–I10 integrados al ledger](research/PRIORS.md)
- [Resultados individuales de la batería (30/30)](research/BRANCH30I_20261026/RESULTS_C01_C30_POST_MERGE.json)
- [Cotejo externo JEC](research/BRANCH30I_20261026/RESULTS_JEC_2023_FULL.json)
- [Transcripción JEC y limitación de fuente](research/BRANCH30I_20261026/JEC_2023_TABLE_I_TRANSCRIPTION.psv)
- [Referencias oficiales de coaliciones](research/BRANCH30I_20261026/JEC_COALITIONS_2023_TRANSCRIPTION.json)
- [Prerregistro exploratorio y exposición previa documentada](research/BRANCH30I_20261026/PREREG_C01_C30.json)

**CT2 predictiva 24/100 y multiactor 20/100 sin incremento, VSDS 1/3; N1/N2/N3 nuevos = 0.** Las 30 plazas recién autorizadas quedan cerradas; se solicita un nuevo bloque condicionado a NUEVAS fuentes primarias de actores y personas, no repetir la misma elección.

## Continuación del 26/10/2026 — fuentes electorales y cierres AB

**Documento de referencia:** [Informe y contabilidad final](research/CONTINUACION_20261026/REPORT.md).

Las **76 plazas previamente disponibles** se adjudicaron de forma explícita: **12 nuevos tests PF-B50** sobre fuentes/atlas, **19 cribados PF-AB20 cerrados STOP_R5** por falta de originales (NO experimentos empíricos ejecutados), y **45 tests de producción F45**. Las 57 pruebas nuevas tienen PASS tras reparar C46 del B50; no se verificaron originales del Ministerio ni se ejecutó un navegador E2E. B50 se reconcilió 8 previas + 30 del ledger B30 por REFERENCIA + 12 pruebas nuevas, sin volver a contabilizar los 30. VSDS 1/3, CT2 predictiva 24/100, CT2 multiactor 20/100; no se inventan descubrimientos.

Nuevo **Atlas electoral 2023**: 52 provincias, 59 etiquetas candidaturas en el CSV secundario y 48 con votos positivos pero cero escaños, que no son necesariamente 48 partidos jurídicos diferentes. Código y dataset: [atlas JSON](data/observatory/electoral_atlas_2023.json), [parser y contraste histórico](scripts/electoral_source_audit.mjs), [adaptador Python](src/politics_fantasy/electoral_atlas.py) y nueva pestaña HTML/JS. La fuente histórica rOpenSpain suma 1057 filas de 14 años 1977–2019; no se han enlazado sus códigos con etiquetas de 2023. **Sin scoring real de personas**, fuente original aún pendiente.

El nuevo bloque sugerido por AB O6 es **30 ciclos BRANCHING adicionales**, no autorizados ni ejecutados. Deben priorizar capturar registros oficiales originales y el universo de actores políticos con y sin escaños, reconstrucción histórica, ETL y pruebas en navegador, no 30 checks del mismo CSV.

## PF-BR20H — universo político no restringido al Congreso (25/10/2026)

Por autorización adicional, **20 ciclos AB A–J con branching terminados** como **ingeniería basada en categorías legales y fixtures ficticias**: primer pase 18/20, reparaciones C02/C16, segundo pase **20/20**. Ninguna de estas ejecuciones constituye un ensayo sociológico independiente con partidos/personas españoles. VSDS sigue **1/3**; CT2 de la NUEVA rama multiactor = **20/100** sin cambio (ordinal y distinta de la predictiva parlamentaria 24/100). N1/N2/N3 nuevos = 0. Permanecen intactos los saldos autorizados B50=12, AB20=19, F45=45.

El nuevo motor de actores y eventos distingue partidos, federaciones, coaliciones, agrupaciones electorales, plataformas, asociaciones, sindicatos, grupos de interés, medios, instituciones y personas con roles políticos públicos documentados. Los escaños son un dato temporal explícito, no condición de inclusión ni medida de poder. No se infieren afiliaciones privadas, etiquetas ideológicas o influencia causal. 9 figuras/entidades y 2 eventos del ejemplo son **totalmente inventados**.

- [Informe final y falsadores](research/BRANCH20H_20261025/REPORT.md)
- [Ledger de 20 fichas A–J](research/BRANCH20H_20261025/LEDGER.json)
- [Prerregistro anterior al código](research/BRANCH20H_20261025/PREREG.md)
- [Pruebas e integración ficticia](research/BRANCH20H_20261025/RESULTS.json)
- [Priors nuevos con evidencia negativa](research/BRANCH20H_20261025/PRIORS_DELTA.md)
- [Fuentes y límites de población](docs/UNIVERSO_ACTORES_POLITICOS_20261025.md)
- [Motor JS](src/politics_fantasy/political_universe.mjs) · [CLI offline](scripts/actor_universe_cli.mjs) · [tests JS](tests/test_political_universe.mjs)
- [Bundle completamente ficticio](examples/political_universe_fixture.json)
- [Ruta Python /api/actors](src/politics_fantasy/actor_api.py): devuelve cobertura agregada del ejemplo, no nombres ni scores. [Tests Python](tests/test_actor_api.py) con 4 comprobaciones superadas sobre una copia local del adaptador; no se ha probado el endpoint HTTP sobre checkout limpio.

**Bloqueos verdaderos:** falta descargar y conciliar un extracto oficial del Registro de Partidos Políticos, candidaturas proclamadas y roles documentados con identidad y temporalidad. Un catálogo público no equivale a dato capturado.



**Estado (25-10-2026): prototipo de investigación + aplicación local de fantasy v0.6.0. No desplegado, sin autenticación, sin predicciones políticas validadas.**

Repositorio preparado para `GalexY3/polictics_fantasy_league`. El nombre de la carpeta es legible; se conserva la grafía real del repositorio remoto cuando se publique.


## 25/10/2026 · v0.6: BRANCH30C, tres fuentes y puerta de identificabilidad

**30 contratos adicionales con BRANCHING completados como ingeniería**, en cinco ramas A–E, con pruebas sobre fixtures sintéticos. **147 pruebas superadas**, 0 experimentos independientes sobre datos políticos españoles, sin cambio de VSDS **1/3** ni CT2 **24/100**. El CSV opcional **Voto de cada grupo** (`votacion_id,fecha,grupo,si,no,abstencion,no_vota`) permite conciliación entre las tres tablas, medición de dispersión por grupo sin atribuir disciplina partidista, detección de grupos incompletos y revisión entre snapshots.

Ejemplo sin instalar: `PYTHONPATH=src python -m politics_fantasy.field_cli --individual RUTA_VOTOS.csv --aggregate RUTA_VOTACIONES.csv --group RUTA_GRUPOS.csv --acquired-at FECHA_REAL_CON_ZONA --out data/local_field/report.json`. El argumento `--group` es **opcional** para conservar compatibilidad con v0.5. Un `report_sha256` es detección de alteración, **no certificación de autenticidad**. El observatorio lee un resumen cerrado, nunca nombres ni filas nominales. Ver [manual v0.6](docs/TRES_CSV_Y_READINESS_v0_6.md) e [informe con ledger A–J](research/BRANCH30C_20261025/REPORT.md).

**Publicación**: rama main de `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/` como alojamiento temporal, no modificación de las normas del método; migrar a `GalexY3/polictics_fantasy_league` en cuanto sea posible. Nueva autorización independiente de BRANCHING 30; los saldos anteriores 12 B50 / 45 libres / 19 AB20 no se consumen.

## 25/10/2026 · v0.5: BRANCH30B, análisis de CSV parlamentarios offline

30 contratos de producción desarrollados en 5 ramas adaptativas A–E. La suite supera **117/117** pruebas; ninguna de ellas comprueba microdatos parlamentarios reales ni aumenta VSDS (**1/3**) o CT2 (**24/100**). El nuevo módulo `field_ingest.py` acepta exports CSV individuales y agregados documentados por Congreso Abierto, con identificadores/hashes, vocabulario cerrado, avisos de filtrado y conciliación sin inferir inasistencias. La CLI `python -m politics_fantasy.field_cli` permite preparar un recibo de auditoría JSON de forma offline y atómica; `GET /api/field` solo presenta indicadores agregados de un recibo local verificado. No puntúa diputados reales. Ver [manual de CSV](docs/CSV_CAMPO_OFFLINE_v0_5.md) e [informe BR30B](research/BRANCH30B_20261025/REPORT.md). 

Los datos de campo reales **NO fueron descargados** desde este entorno: la capa queda instrumentada y pendiente de cotejo externo contra la fuente del Congreso. El código está en alojamiento GitHub temporal, pendiente de migrar al repositorio dedicado. Este nuevo bloque de 30 ciclos BRANCHING está completo como ingeniería; no descuenta el saldo previo de 12 PF-B50, 45 PF-F45 y 19 AB20.

## 25/10/2026 · v0.4: escala VSDS y BRANCH30

**VSDS (0/3–3/3) valora sociología y data science para este proyecto, no descubrimiento original.** Actualmente VSDS-1/3 por herramienta reproducible y tests; AB científico 0/3, CT2 predicción 24/100 (sin cambio). Ver [`docs/VSDS_PROYECTO.md`](docs/VSDS_PROYECTO.md).

30 incrementos de producción con ensayos deterministas y ledger A–J, en 5 lotes prerregistrados previamente mediante commits GitHub: seguridad nominal histórica, indicadores sociológicos, comparación relacional, validación de pronóstico y panel local. Test suite 87/87; datos de laboratorio **100 % inventados**; no hay ingesta nominal española certificada ni validación científica externa. Ver [`research/BRANCH30_20261025/REPORT.md`](research/BRANCH30_20261025/REPORT.md). Esta tanda consume **30 de los 42** ciclos pendientes de B50 (saldo 12), no inventa un nuevo bloque de 30 adicionales. Siguen pendientes 45 F45 y 19 PF-AB20. El alojamiento GitHub en `Metodologia-AB/proyectos/politics-fantasy-league` es **provisional**, con migración obligatoria al repositorio propio.

El nuevo endpoint `GET /api/lab` y su panel de observatorio contienen once filas nominales **sintéticas**, tasas con desconocidos visibles, disidencia descriptiva, diversidad y baseline de acuerdo por marginales. **No influyen en el fantasy**. Detalles: [`docs/OBSERVATORIO_v0_4.md`](docs/OBSERVATORIO_v0_4.md).

## Producto ejecutable (nuevo, 24/10/2026)

La actualización v0.3 incluye auditoría operacional en `politics_fantasy.ops`, correcciones de revisiones bitemporales y defensas frente a Host malicioso. Ver `docs/OPERACIONES_v0_3.md`.

Esta versión **sí incorpora bucles de ingeniería de producto, además de investigación**. Se han preparado un juego local en SQLite y navegador, API local, fichajes, créditos, plantillas, alineaciones, jornadas, clasificación y un observatorio separado con recuentos transcritos. Funciona con diez figuras sintéticas ficticias, **no políticos reales**. No usar rankings sintéticos para atribuir mérito político.

**Ejecutar el juego sin instalar librerías externas:**

```bash
python run_demo.py
```

Abrir después en **http://127.0.0.1:8787** desde el mismo ordenador. En Windows se puede usar `start_windows.bat`; en Linux/macOS `start_linux_mac.sh`. La DB mutable está en `data/demo/game.db` (excluida de Git/ZIP). El servidor solo acepta conexiones locales, y **carece de autenticación**: NO publicar en internet. Ver `docs/PRODUCTO_LOCAL_v0_2.md`.

El almacén `warehouse.py` añade ingesta atómica de **JSONL YA NORMALIZADO** con SHA-256 y bitemporalidad, no parser validado de los JSON oficiales. Ver `docs/ALMACEN_BITEMPORAL.md`. Suite actual: **57 pruebas Python superadas en ejecución local (25/10)**, sintaxis JS comprobada, cobertura Python agregada 88 %; faltan QA visual en navegador, fuentes nominales verificadas y validación estadística. Bench sintético: 100.000 eventos de prueba en 2,84 s en un ordenador, no extrapolable.

**Autorización adicional:** después de cerrar PF-AB20, **45 bucles libres con branching de producción e investigación** (archivo `research/AB65_20261024/FREE45_LEDGER.json`). 45 autorizados, **0 consumidos**: avances de producción de esta entrega se describen por separado para no falsificar la cuenta. Los 19 ciclos PF-AB20 pendientes siguen bloqueados para ensayos empíricos hasta tener microdatos oficiales legalmente utilizables y registrados.

## Misión

Construir una infraestructura longitudinal, auditable, computacionalmente exigente y científicamente falsable de la política española. La experiencia fantasy es una aplicación y un instrumento de observación, NO el objetivo científico. La interfaz se inspira libremente en el género fantasy, sin reproducir marcas, textos, algoritmos propietarios ni reglas exactas de LALIGA.

**Capas separadas:** (1) fuentes públicas verificadas e inmutables → (2) reconstrucción de entidades y eventos con temporalidad doble → (3) estimandos y modelo predictivo retrospectivamente validado → (4) dinámicas institucionales y simulación multiagente → (5) reglas de juego transparentes, versionadas y auditables.

No se clasifican personas por 'bondad política', ni se atribuye mérito individual a votaciones colectivas sin diseño de imputación apropiado. El valor en puntos del fantasy no es una medida de virtud o rendimiento democrático.

## Estado real de las evidencias

- Verificada **disponibilidad documental** de fuentes oficiales: Congreso (votaciones, diputados, iniciativas, intervenciones), Senado y BOE, mediante consulta pública de las páginas citadas en `docs/FUENTES_Y_LICENCIAS.md`.
- El código de `src/` implementa **ingesta conservadora de documentos arbitrarios**, verificación de hashes, modelo de eventos explícito y un benchmark matemático/sintético pequeño; no pretende disponer de un parser validado de todas las estructuras oficiales.
- La campaña inicial contiene **30 ciclos de evaluación documental/diseño A–J**, identificados `PLANNING_AB_ONLY`. No hay 30 ensayos empíricos ni retrospectivos ejecutados, ni validación de predicción con datos parlamentarios históricos.
- La campaña adicional **PF-AB20** fue autorizada el 24/10/2026. Tiene **un piloto exploratorio C01** sobre 20 recuentos agregados de una sesión del Congreso transcritos manualmente, **19 ciclos pendientes**, 0 ensayos AB confirmatorios válidos y 0 modelos predictivos con datos políticos. Véase `research/AB20_REALES_20261024/README.md`. El prerregistro es local; GitHub no admite escritura y faltan bytes oficiales/as-of.
- Ingesta pública real en este entorno: **NO VERIFICADA**; las descargas deberán ejecutarse desde una máquina con acceso legal a las fuentes y quedar archivadas con sus licencias.
- Nivel AB de descubrimiento: 0/3 (ningún hallazgo experimental adjudicado); CT2 es juicio ordinal interno, no probabilidad.

## Estructura

- `docs/ARQUITECTURA.md`: unidades, teoría sistémica, modelo observacional, puntuación y TFM.
- `docs/FUENTES_Y_LICENCIAS.md`: inventario oficial, permisos a comprobar, clases de datos.
- `docs/VALIDACION_ETICA.md`: leakage, selección, fairness, reputación, seguridad, interpretación.
- `docs/TRANSFERENCIA_AB.md`: correspondencia con AB 3.2.1 O1–O6 y propuestas metodológicas, con límites reales.
- `docs/INGESTA_ALTO_VOLUMEN.md`: pipeline de recolección y explotación por lotes de gran escala.
- `docs/PLAN_TFM.md`: estimandos, contribución científica, fases y criterios de decisión.
- `docs/ANTECEDENTES_Y_NOVEDAD.md`: juegos políticos y observatorios españoles existentes, y literatura de predicción de decisiones, que limitan cualquier pretensión de novedad.
- `sql/schema.sql`: esquema PostgreSQL para procedencia, bitemporalidad, entidades, eventos, votaciones, fantasy.
- `src/politics_fantasy/`: ingesta, puntuación, almacén bitemporal y evaluación prequential; `server.py` y `product.py` implementan la demo SQLite/UI local.
- `run_demo.py`, `start_windows.bat`, `start_linux_mac.sh`: lanzadores de aplicación.
- `research/AB65_20261024/`: 45 bucles autorizados aún no iniciados + evidencia de entregas de producción.
- `R/`: análisis exploratorio y modelos de recuento con denominadores de exposición (plantilla, requiere datos normalizados).
- `research/AB30_C01_C30.md`: treinta fichas con protocolo documental A–J, rivales y falsadores.
- `research/PRIORS.md`, `research/CAMPAIGN.json`, `research/FINDINGS_1_3.json`: estado AB30 y límites.
- `research/AB20_REALES_20261024/`: campaña AB20 autorizada; datos oficiales agregados transcritos, preregistro limitado, informe C01, backlog C02–C20, priors y bloqueos.
- `tests/`: pruebas unitarias con datos completamente sintéticos.

## Primer uso local

```bash
PYTHONPATH=src python -m pytest -q
PYTHONPATH=src python -m politics_fantasy.simulation
PYTHONPATH=src python -m politics_fantasy.ingest --help
```

En un entorno sin instalación editable, desde la raíz: `PYTHONPATH=src python -m pytest -q`. Python 3.10+, pytest para tests; solo librería estándar para el núcleo. Opcional: R (ggplot2, MASS) para estadística y PostgreSQL para persistencia.

La ingesta **nunca debe iniciarse en masa** sin revisar licencias y condiciones de acceso. Ejemplo de URL aislada, sólo cuando se haya autorizado documentalmente: `PYTHONPATH=src python -m politics_fantasy.ingest --url URL_HTTPS_OFICIAL --out data/raw --source congreso --min-interval 3`.

## Procedencia metodológica

AB 3.2.1, anexos O1–O6 del repositorio independiente `Metodologia-AB`. Metodología de contraste provisional, sin eficacia superior demostrada. El proyecto LARP se consultó como ejemplo de *gobernanza de evidencia*, no como antecedente sustantivo transferible a ciencia política.

## Fuentes verificadas a 24-10-2026

Congreso: https://www.congreso.es/es/datos-abiertos  
Congreso votaciones: https://www.congreso.es/es/opendata/votaciones  
Congreso intervenciones: https://www.congreso.es/es/opendata/intervenciones  
Senado: https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/index.html?lang=es_ES  
BOE: https://www.boe.es/datosabiertos/api/api.php?lang=es  
LALIGA Fantasy: https://laligafantasy.zendesk.com/hc/es/articles/360025679853-Reglamento (referencia del género únicamente).

## Publicación remota

Incidencia histórica, resuelta mediante alojamiento alternativo: el intento de escritura del 24-10-2026 fue rechazado con HTTP 403 `Resource not accessible by integration` para archivos, blobs e incidencias del repositorio nuevo. Desde el 25-10-2026 se publica en la carpeta provisional de Metodologia-AB; el repositorio específico continúa pendiente de migración.

## Alojamiento y autorización nuevos (25/10/2026)

Alojamiento temporal en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`; **migrar obligatoriamente** a `GalexY3/polictics_fantasy_league` cuando la integración pueda escribir allí. Ver `research/BRANCH50_20261025/MIGRATION.md`.

50 ciclos con branching autorizados; ejecución inicial: 8 incrementos de ingeniería locales (no experimentos científicos confirmatorios) y 42 ciclos nuevos pendientes. Consultar `research/BRANCH50_20261025/CYCLES.json`. Las 45 plazas libres anteriores NO se consumen con este bloque; AB20 mantiene 19 ciclos pendientes.


## AB30D · 30 ciclos completos A–J (2026-10-25)

Investigación metodológica sobre generadores sintéticos — **no** resultado empírico español. [Informe y auditoría](research/AB30_COMPLETOS_20261025/REPORT.md), [ledger A–J auditado](research/AB30_COMPLETOS_20261025/RESULTS_AUDITED.json), [prerregistro congelado](research/AB30_COMPLETOS_20261025/PREREG.json). Ejecución reproducible: `pip install -e .[research,test]` y `python scripts/ab30d_full.py --out /ruta/result.json`; después `python scripts/audit_ab30d.py` para auditar el registro canónico sin sobrescribir el resultado bruto. Resultados: 30 pruebas computacionales ejecutadas, 0 ensayos empíricos nominales; VSDS 1/3, CT2 24/100.

## v0.8 — Auditoría longitudinal del corpus parlamentario secundario (25-10-2026)

En [PF-BR30F](research/BRANCH30F_20261025/REPORT.md) constan 30 auditorías **post hoc** A–J sobre un *único* archivo secundario `pleno.jsonl` de Congreso Abierto: 2.175 votaciones, 726.564 votos nominales identificados frente a 761.218 posiciones agregadas, 34.654 posiciones sin correspondencia nominal y 149 discrepancias en el signo de la mayoría Sí−No si se usa exclusivamente el subconjunto nominal. **No** son 30 experimentos de campo independientes ni resultados oficiales corregidos. VSDS 1/3, CT2 24/100 sin ascenso; sin atribución de ausencia personal. Prerregistro: [GitHub (commit 5b5a85a)](https://github.com/GalexY3/Metodologia-AB/blob/5b5a85a6c470beb6f3d86084f883c4806220e3fd/proyectos/politics-fantasy-league/research/BRANCH30F_20261025/PREREG.md).

Reproducción (descargar legítimamente la fuente por separado; no se redistribuye archivo nominal en este ZIP):

```
python scripts/audit_pleno_full.py /ruta/pleno.jsonl --strict-git-blob --out audit.json
```

La comparación estructural contra un voto oficial JSON descargado y un JSON secundario de votaciones se hace con `python scripts/compare_original_vote.py oficial.json fuente_secundaria.json --id s175-v003`. **No** verifica un censo histórico por sí misma. No utilizar la fuente de octubre de 2026 como si hubiese estado disponible en predicciones realizadas antes de esa fecha.


## BRANCH30G (25-10-2026) — 30 ciclos A–J CERRADOS, no confirmatorios

**30/30 unidades A–J completadas:** C01 documental, C02 de ingeniería (fixtures sintéticas), **C03–C30: 28 análisis distintos retrospectivos sobre un único archivo secundario real de 2.175 votaciones**. Las 28 pruebas **NO** son fuentes ni confirmaciones independientes ni 28 hallazgos. El prerregistro específico fue congelado antes de este nuevo lote, pero sus preguntas ya estaban influidas por BR30E/F. La nueva fuente original oficial nominal y el roster histórico permanecen sin cotejo, así que **0 validaciones oficiales nominales independientes**. VSDS=1/3; CT2=24/100; N1/N2/N3 nuevos=0.

Hallazgos locales: de 2.173 votos con códigos identificados, **1.655** tienen certificado conservador de mayoría; **125** inversiones estrictas del signo nominal frente a totales (todas con margen oficial absoluto ≤20); un predictor online retrospectivo de Sí/No condicionado a tipo obtiene Brier **0,2063** frente a **0,2492** sin tipo, sin validación as-of. Estas cifras **no** alteran resultados del Congreso, ni miden influencia de diputados ni acreditan predicción en vivo.

- [Informe final, 30 ciclos y dictamen](research/BRANCH30G_20261025/REPORT.md)
- [Ledger íntegro individual A–J](research/BRANCH30G_20261025/LEDGER.json)
- [Preregistro C03–C30](research/BRANCH30G_20261025/PREREG_C03_C30.json)
- [Resultados brutos de los 28 contrastes](research/BRANCH30G_20261025/RESULTS_C03_C30.json)
- [Auditoría y reparación de desglose por grupos](research/BRANCH30G_20261025/AUDIT_ADVERSARIAL.md)
- [Priors acumulativos, positivos y negativos](research/BRANCH30G_20261025/PRIORS_DELTA.md)
- [Código Node puro](scripts/br30g_audit.mjs) · [CLI SHA1 pinned](scripts/run_br30g_audit.mjs) · [QA sintética](tests/test_br30g_audit.mjs)
- [CT2 30 puntos (ordinal)](research/BRANCH30G_20261025/CT2_TRAJECTORY.csv)

Conservar los saldos independientes 12 B50 / 45 libres / 19 AB20. El nombre del repositorio separado `GalexY3/polictics_fantasy_league` se mantiene sin migración (históricamente vacío); este alojamiento es temporal.


## AB Atlas / AB-P: seguimiento visual y actualización incremental (26-10-2026)

[Mapa y protocolo de Politics Fantasy](ab_atlas/README.md): el proyecto se sigue como AB-H (producto AB-P + subinvestigaciones AB-R). Incluye [HTML navegable](ab_atlas/AB_Atlas_Politics_Fantasy.html), [seed versionado](ab_atlas/seed.json), [briefing](ab_atlas/CURRENT.md), [deltas append-only](ab_atlas/updates/README.md) y [herramienta Python universal](../../ab_atlas/README.md).

**Al finalizar bloques de X ciclos**, ChatGPT debe añadir únicamente los cambios relevantes al grafo, verificar la secuencia y el ledger, actualizar `CURRENT.md`, y evitar regenerar HTML innecesariamente. Un test de código no eleva CT2/VSDS ni convierte la demo en lanzamiento listo; persisten los seis gates críticos hasta evidencia independiente.
