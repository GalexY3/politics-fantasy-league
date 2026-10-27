# AB Atlas · Politics Fantasy · 27/10/2026

- **Modo:** AB-H; separar producto AB-P, investigación AB-R, CT2, VSDS y gates.
- **Estado del mapa:** seed inalterado, lotes `0001-PFL-ABH20-20261026`, `0002-PFL-RECON-20261027` y `0003-PFL-RC04-20261027`. Replay estricto: 3 lotes, 25 nodos, SHA-256 `a599a4985803117f335f94a4f4d9ba50c7576dd7bf32f2f71f651b91fb42f75e`. El HTML es una foto anterior, no se ha regenerado.
- **Autorización sin conciliar:** ramas independientes registran 9 y 4 ciclos para bloques descritos como BRANCHING 20; el investigador no recuerda si son el mismo permiso. Esta continuación añade RC01–RC04: si fuera uno solo y no hay otros consumos, quedarían **como máximo 3**, no una cifra definitiva. [Reconciliación](../research/ABH_RECON_20261027/RECONCILIACION.md).
- **Fuentes:** [catálogo central](../docs/CATALOGO_FUENTES.md). Interior: 5.600 filas electas en 16 elecciones, 1977–2023. Senado: composición y una sesión nominal reproducidas. RC04 cotejó 259 cadenas de nombres de la sesión y encontró un candidato nominal por cadena en la composición XV del snapshot; la identidad y pertenencia temporal no están validadas. Las capturas se exploraron antes de los preregistros; no hay crosswalk individual certificado ni `first_public_at` por fila.
- **Producto:** 13 pruebas unitarias/HTTP locales de elegibilidad aprobadas (RC02). Solo aceptación de esos casos, no E2E de usuarios ni servicio público. La guarda tipada de la rama paralela sigue fuera del servidor de esta rama.
- **Incidencias:** se conservan ambas historias, sus complaints, la exposición pre-preregistro y un fallo de replay nuevo por severidad inválida, reparado. Una prueba Atlas falló en Windows por codificación y se reparó; las 34 pruebas de Atlas pasan. La integridad estructural no autentica evidencia.
- **Indicadores heredados sin cambio:** PFL-V1 rev.3 36,35 %, CT2 identidad 29/100, VSDS 1/3, N1/N2/N3 0/0/0. Seis gates críticos siguen sin acreditación.

## Próximas acciones condicionadas

1. Determinar si las dos ramas consumen el mismo permiso; el investigador no lo recuerda y se mantiene el techo prudente de tres hasta reconciliarlo.
2. Fijar muestra pequeña y controles contra homónimos, IDs cambiantes y falsos enlaces; adjudicar contra fuentes institucionales independientes antes de unir personas.
3. Revisar si los artefactos temporales anteriores del Congreso siguen accesibles; las nuevas capturas en `data/raw/` son locales y no se subieron a GitHub.
4. Auditar licencias y fecha de primera publicación por distribución/registro antes de usar los datos en un backtest o producto.
5. Integrar funcionalidades de ramas solo con revisión de conflictos y pruebas; no mezclar ejecución documental con aceptación de usuario o gates de lanzamiento.

Informe y ciclos A–J: [continuación 27/10](../research/ABH_RECON_20261027/REPORT.md). Mantener R5 y no consumir plazas para rellenar la cuota.
