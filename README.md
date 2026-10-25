# Politics Fantasy League — Political Data Science Laboratory

## 25/10/2026 · v0.7: 30 ciclos A–J completos (PF-AB30-FULL)

Se ejecutaron **18 auditorías retrospectivas** sobre siete votaciones seleccionadas del JSON público de Congreso Abierto y 20 recuentos agregados transcritos de una sola sesión, más **12 experimentos metodológicos sintéticos** con 600 realizaciones cada uno. Cada ciclo tiene ficha A–J, resultado, hipótesis rival, falsador, auditoría, decisión y procedencia. El informe principal es [`research/AB30_FULL_20261025/REPORT.md`](research/AB30_FULL_20261025/REPORT.md); hay `LEDGER.json`, `C01..C30.json` y errata inmutable de C05.

La fuente secundaria seleccionada contiene **7/7 votaciones con totales 350**, pero **6/7** tienen menos registros nominales, sumando **42 entradas omitidas** en esos siete ejemplos. No significa ausencias reales ni afectación de 42 diputados distintos. No hay fuente oficial nominal independiente cotejada; no se extrapola a la legislatura. Ver cuenta anónima con enlace/hash de fuente en `data/upstream_curated_7/`.

**Pre-reg GitHub:** `3bfd2815cf3baf2eabe77830fd2e9a750aafe10f`; **código y datos congelados antes de ejecutar:** `d08a90bae7cb2176b137a3e15b547ec3482303b6`. Los 18 ciclos A–C siguen **POST_HOC_AUDIT** porque los datos ya se habían visto al diseñar; los 12 D–E son experimentos **dentro de generador sintético**, no replicaciones externas. En C05 se conserva errata Pearson/Spearman sin sobrescribir el valor original. **VSDS 1/3** y CT2 predictivo **24/100**, sin cambio; grados científicos originales 2/3 = 0. La suite global supera **152 tests**.

Reproducir investigación (extra: `pip install numpy scipy matplotlib pytest`): `python scripts/ab30_full.py --prereg-commit 3bfd2815cf3baf2eabe77830fd2e9a750aafe10f --code-commit d08a90bae7cb2176b137a3e15b547ec3482303b6`; `python scripts/plot_ab30_full.py`. Para las 147 pruebas previas del producto solo se requiere pytest.

El proyecto permanece alojado temporalmente en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`, y se migrará a `GalexY3/polictics_fantasy_league` cuando se habilite escritura. Las autorizaciones antiguas pendientes 12 B50, 45 libres y 19 AB20 son independientes y no se consumen.


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
