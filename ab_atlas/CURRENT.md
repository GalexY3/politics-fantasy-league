# AB Atlas · Politics Fantasy · 27/10/2026

- **Modo:** AB-H; separar producto AB-P, investigación AB-R, CT2, VSDS y gates.
- **Estado del mapa:** seed inalterado, lotes `0001`–`0004`. Replay estricto: 4 lotes, 26 nodos, SHA-256 `fbfda826bc2af5dee8e4f9408f0cdfc35f6e8c9e94362a17c973961907c35828`. El HTML es una foto anterior, no se ha regenerado.
- **Autorización sin conciliar:** ramas independientes registran 9 y 4 ciclos para bloques descritos como BRANCHING 20; el investigador no recuerda si son el mismo permiso. Esta continuación añade RC01–RC04: si fuera uno solo y no hay otros consumos, quedarían **como máximo 3**, no una cifra definitiva. [Reconciliación](../research/ABH_RECON_20261027/RECONCILIACION.md).
- **Fuentes:** [catálogo central](../docs/CATALOGO_FUENTES.md). Interior: 5.600 filas electas en 16 elecciones, 1977–2023. Senado: composición y una sesión nominal reproducidas. RC04 cotejó 259 cadenas de nombres de la sesión y encontró un candidato nominal por cadena en la composición XV del snapshot; la identidad y pertenencia temporal no están validadas. Las capturas se exploraron antes de los preregistros; no hay crosswalk individual certificado ni `first_public_at` por fila. Se recuperaron localmente tres artefactos de Actions próximos a caducar, y hay un paquete local de fuentes para ChatGPT: [recibo](../research/ABH_RECON_20261027/RESCATE_FUENTES_20261027.json), [guía](../docs/CONTINUIDAD_CHATGPT_20261027.md). El rescate no consumió ciclos ni publicó originales en GitHub.
- **Producto:** 13 pruebas unitarias/HTTP locales de elegibilidad aprobadas (RC02). Solo aceptación de esos casos, no E2E de usuarios ni servicio público. La guarda tipada de la rama paralela sigue fuera del servidor de esta rama.
- **Incidencias:** se conservan ambas historias, sus complaints, la exposición pre-preregistro y un fallo de replay nuevo por severidad inválida, reparado. Una prueba Atlas falló en Windows por codificación y se reparó; las 34 pruebas de Atlas pasan. La integridad estructural no autentica evidencia.
- **Indicadores heredados sin cambio:** PFL-V1 rev.3 36,35 %, CT2 identidad 29/100, VSDS 1/3, N1/N2/N3 0/0/0. Seis gates críticos siguen sin acreditación.

## Próximas acciones condicionadas

1. Determinar si las dos ramas consumen el mismo permiso; el investigador no lo recuerda y se mantiene el techo prudente de tres hasta reconciliarlo.
2. Fijar muestra pequeña y controles contra homónimos, IDs cambiantes y falsos enlaces; adjudicar contra fuentes institucionales independientes antes de unir personas.
3. La recuperación local conserva dos artefactos del Congreso y uno BOE; cotejar otras capturas si hacen falta. Todos los originales en `data/raw/` son locales y no se subieron a GitHub.
4. Auditar licencias y fecha de primera publicación por distribución/registro antes de usar los datos en un backtest o producto.
5. Integrar funcionalidades de ramas solo con revisión de conflictos y pruebas; no mezclar ejecución documental con aceptación de usuario o gates de lanzamiento.

Informe y ciclos A–J: [continuación 27/10](../research/ABH_RECON_20261027/REPORT.md). Mantener R5 y no consumir plazas para rellenar la cuota.
