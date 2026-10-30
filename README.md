> **Continuidad entre chats:** leer [START_HERE.md](START_HERE.md), [estado vivo y hitos](PROJECT_STATE.json) y [prompt reutilizable](NEW_CHAT_PROMPT.md). La rama operativa estable es `integration/pfl`; la fusión a main se verifica por separado. Producto e investigación tienen objetivos y progreso distintos.

# Politics Fantasy League

Laboratorio en desarrollo: juego local con fixtures ficticias, observatorio de fuentes y subinvestigaciones metodologicas. El avance contractual V4 es 36,90 %; las puertas de lanzamiento siguen 0/6. Las pruebas tecnicas no acreditan validez predictiva ni autorizan puntuaciones sobre personas reales.

## Retomar trabajo

- [Cola vigente y resultados Codex](tareas_codex/README.md).
- [Estado y limites de Atlas](ab_atlas/CURRENT.md).
- [Campana CODEX20 cerrada](research/ABH_CODEX20_20261029/CAMPAIGN.json): su ledger es la autoridad del saldo, no esta pagina.
- [Catalogo de fuentes](docs/CATALOGO_FUENTES.md).
- [Instrucciones del repositorio](../../AGENTS.md).
- [Historial completo del proyecto](README_HISTORICO_HASTA_20261029.md), preservado con sus fechas, ramas y balances originales.

## Verificacion local

Desde la raiz del repositorio, usar los comandos del informe correspondiente y registrar el commit ensayado. Node tiene pruebas en tests/ y tambien en src/politics_fantasy/; no asumir que un unico glob las descubre todas. Comando Node desde raiz: `node proyectos/politics-fantasy-league/scripts/run_node_tests.mjs`. Python requiere los extras del pyproject del proyecto. Los controles POSIX y navegador deben reportarse por separado cuando el entorno no los permita.

Los originales potencialmente nominativos permanecen en data/raw/ fuera de Git. Consultar cada manifiesto de captura, derechos y limites temporales antes de reutilizarlos. El linaje RELEASEPATH de PR44 tiene un registro de logros distinto; sus snapshots no sustituyen los de este linaje automaticamente.
