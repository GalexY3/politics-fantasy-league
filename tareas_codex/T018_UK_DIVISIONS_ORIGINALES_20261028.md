# T018 · Originales API UK Parliament y QA empírico de identidad/grano de votaciones

**PREPARADA PARA CODEX; NO EJECUTADA.** Este encargo técnico NO cuenta como ciclo AB ni autoriza métricas, logros, scoring personal, CI costosa o fusión.

## Rama y restricciones

Repo `GalexY3/Metodologia-AB`, rama de base `research/pfl-abh5-divisions-20261028`. Verificar HEAD y estado real (sin asumir SHA futuro); leer `AGENTS.md`, AB 3.2.1/O3–O6, `ab_atlas/CURRENT.md`, `research/ABH_DIVISIONS5_20261028/CAMPAIGN_STATUS.json` e `FINAL_REPORT.md`. Crear rama de ejecución aparte `exec/pfl-t018-uk-divisions-20261028`; PR borrador **contra rama base**, sin fusionar. Sin ChatRelay, sin CI costosa ni publicación de registros de personas en Git.

## Datos originales y acceso verificable

Publicador primario: **UK Parliament**:
- API documentada `https://commonsvotes-api.parliament.uk/swagger/ui/index` → `GET /data/divisions.json/search` (parámetros de fechas) y `GET /data/division/{divisionId}.json`. **El número de división parlamentaria NO es necesariamente el `divisionId` del API**. No construir IDs por aritmética de número de sesión. Capturar 20 y 21 octubre de 2026 y 15 julio 2026 como control, priorizando versiones más recientes. Para Lores comprobar por separado API oficial de Lords y documentación: no usar indebidamente la estructura Commons.
- Listado público `https://votes.parliament.uk/Votes/Commons` y fichas en `https://votes.parliament.uk/votes/commons/division/2411` (división diferida de 15/07/2026). `https://votes.parliament.uk/votes/lords/division/3729`, `/3730`, `/3731` (tres divisiones de 26/10/2026).
- Examinar [Fuente nacional UK](https://www.data.gov.uk/collections/government-and-parliament/parliament-voting-records) para diferencias entre *tellers* y conteo de nombres. Ficha 2411 incluye marcas `Proxy` y ausencia no registrada: **no atribuir presencia física** a proxy ni ausencia voluntaria a un voto no consignado.

Para **cada** descarga: URL exacta, HTTP/TLS, redirecciones, UTC comienzo/fin, MIME, tamaño, SHA-256 **del JSON/CSV original**, cabeceras de actualización si existen, licences y `PublicationUpdated` cuando el API lo declare. Diferenciar `date` del voto, timestamp de actualización y **`first_public_at` con evidencia de primer conocimiento externo**, normalmente UNKNOWN; no inferir primer conocimiento de `PublicationUpdated`. Si el API devuelve error, registrar el error real y terminar intentos repetidos R5, no inventar contenido ni claves.

**Conservar originales identificables SOLO en ubicación local gitignored**; en el repositorio manifest con hashes, recuentos, fuentes, y fixtures agregados por división/cámara/trámite, sin rankings de miembros/partidos o predicciones de opciones políticas.

## Comprobaciones discriminantes

- **C02**: Commons 21/10/2026, divisiones parlamentarias 101 y 103 tienen el mismo vector público Aye=345/No=108 pero títulos y división distinta. Deben tener IDs/filas separadas; **no** concluir coincidencia de votantes sin comparar personas y permisos. Contrastar datos de índice oficial `C02_UK_DISTINCT_DIVISIONS_COLLISION.json`.
- **C03**: Commons 20/10/2026, Northern Ireland Troubles Bill divisiones 96..100 con diferentes trámites y resultados. Verificar si los registros de denominadores, categorías y tiempos respaldan la transcripción agregada; no agrupar cinco votos como una sola toma de posición.
- **C04**: Lords 26/10/2026, divisiones 3729..3731: Content/Not Content y *tellers*; no mezclar con categorías Commons ni sumar tellers repetidos. Confrontar `C04_UK_LORDS_SAME_BILL_AGGREGATES.json`.
- **C05**: correr sobre archivos **exactos** de rama `node --test proyectos/politics-fantasy-league/research/ABH_DIVISIONS5_20261028/test_division_ontology_research.mjs`. Blobs ya comprobados en investigación: módulo `d209949e2c788691d6f0a4e0ccdef9f18e7fb0a7`, tests `17fd8c094768860d58180b6555262e3cea20e9b0`, 14 tests locales PASS. Ejecutar también suite completa Python/Node/Atlas del checkout limpio; registrar **primer fallo** y no cambiar tests para simular PASS.

## Entrega y condiciones de aceptación

Crear `tareas_codex/T018_RESULTADO.md` y `tareas_codex/T018_EVIDENCIA/MANIFEST.json`, logs/hashes de prueba y agregados no nominales con origen y cut temporal. `SUCCESS` solo con originales auténticos verificables y QA integral PASS, `PARTIAL` si solo algunas fuentes/QA, `BLOCKED` si se repite acceso no recuperable, **sin contar trabajo de Codex como nuevo ciclo AB**. Requiere revisión de fuentes de Open Parliament Licence v3.0 y licencias efectivas según el tipo de datos. Nada de `main`, rankings personales, inferencias de voto ausente, ni datos privados.
