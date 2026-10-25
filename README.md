# Politics Fantasy League — Political Data Science Laboratory

**Estado (24-10-2026): prototipo de investigación + aplicación local de fantasy v0.3.0. No desplegado, sin autenticación, sin predicciones políticas validadas.**

Repositorio preparado para `GalexY3/polictics_fantasy_league`. El nombre de la carpeta es legible; se conserva la grafía real del repositorio remoto cuando se publique.


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

Intento de escritura mediante conector GitHub, 24-10-2026: rechazado con HTTP 403 `Resource not accessible by integration` para archivos, blobs e incidencias del repositorio nuevo. Este árbol es un **entregable local verificado**; no afirmar que está publicado en GitHub. Reintentar después de revisar permisos de instalación del conector.

## Alojamiento y autorización nuevos (25/10/2026)

Alojamiento temporal en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`; **migrar obligatoriamente** a `GalexY3/polictics_fantasy_league` cuando la integración pueda escribir allí. Ver `research/BRANCH50_20261025/MIGRATION.md`.

50 ciclos con branching autorizados; ejecución inicial: 8 incrementos de ingeniería locales (no experimentos científicos confirmatorios) y 42 ciclos nuevos pendientes. Consultar `research/BRANCH50_20261025/CYCLES.json`. Las 45 plazas libres anteriores NO se consumen con este bloque; AB20 mantiene 19 ciclos pendientes.