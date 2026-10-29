# Politics Fantasy League · ABH30 cierre de C20–C30

**Fecha:** 29 de octubre de 2026. **Estado:** ejecución completada de los 11 ciclos del bloque restante, todos **AB-P técnicos de alcance limitado**. Una misma familia **preplanificada**, una fuente compartida, **NO 11 experimentos humanos independientes**. [Recibo maestro de ejecución](C20_C30_FINAL_RUN_MANIFEST.json); [registro inmutable de fallos originales](C20_C30_INITIAL_ADVERSARIAL_INVALIDATION.json).

## Resultado y contabilidad

El bloque autorizado de 30 ciclos nuevos queda en **30/30**, **0 nuevos pendientes**, **2 históricos STOP_R5 separados**. Cuatro ciclos C20/C23/C29/C30 completaron su prueba original sin la anomalía adversarial detectada. Los siete ciclos C21/C22/C24/C25/C26/C27/C28 tenían inicialmente 2/2 test PASS cada uno pero el control posterior encontró un error o una omisión real. Sus resultados iniciales quedaron INVALID/INCOMPLETE, sin consumo adicional. Se corrigió el código y se congelaron **7 contratos A–J R1 por commit** antes de volver a ejecutar: **C21 3/3; C22 3/3; C24 3/3; C25 3/3; C26 3/3; C27 4/4; C28 3/3**, todos nativos Node v22.16.0 con exit 0. Batería de regresión completa reparada **30/30 PASS**, SHA256 TAP `ed65356f5b81ec64f844161b33020b0faea4d0db16fedb386fa4d866689c65d3`.

**SHA congelados originales antes de outcomes:** módulo `src/politics_fantasy/fictional_pfl_impact_suite.mjs` Git blob `30ad118ad2ce286a302ebfbf64c6108a6fce4b38` (SHA256 `a736c7b480909fe1eba1d597075672eb39eae7956e58f9bdd9ac83b8bdb7208f`), tests Git blob `dfcf2ccf5d062b3823216446cf30aa20eb26d466` (SHA256 `5073564c97205eababd490ac3916206ae2a122c5f226b7b92e0730e35e1cad69`). Los once contratos individuales `C20_PREREG_AJ_SHA.json` … `C30_PREREG_AJ_SHA.json` están versionados **antes de la primera prueba nativa**.

**SHA reparados R1 congelados antes de rerun:** fuente Git `dde0f5b5e92e95e44b5088b5457e3d8f9b4a65b7` (SHA256 `ea161924354b7a6706b8aedf65705900c1be48626081918bf92f16cce7b6329e`); tests Git `365f56f6c6a8a15f46ca8c8a186cad4d9f3c739b` (SHA256 `46a8d75ec76c34a31def5a0c81a04d55e3864e814e1e467c725d013b6d840f24`). Contratos de reparación específicos `C21/C22/C24/C25/C26/C27/C28_REPAIR_R1_PREREG_AJ_SHA.json` guardados antes de repetir pruebas.

| Ciclo | Unidad y nuevo control | Ejecución válida | Adversario |
|---|---|---|---|
| C20 | Esfuerzo clasificado frente a esfuerzo no clasificado | 2/2 | Aumento +2 y pérdida −2, total 0: no interpretar beneficio neto |
| C21 | Estratificación medida antes de asignar | 3/3 R1 | Bloquear duplicado del mismo miembro |
| C22 | Redes e interferencia entre brazos/salas | 3/3 R1 | Bloquear doble contabilización de una arista |
| C23 | Ensayo equilibrado por salas de cinco tratamientos | 2/2 | No equivale a aleatorización segura/oculta real |
| C24 | Abandono frente a censura administrativa | 3/3 R1 | Rechazar un conjunto de riesgo vacío |
| C25 | Minimización de alias en información pública | 3/3 R1 | Rechazar campo oculto Symbol o propiedad accesora |
| C26 | Tiempo de publicación de pregunta y resultado | 3/3 R1 | Rechazar fecha imposible que Date.parse normalizaba |
| C27 | Normas e instituciones con versiones efectivas | 4/4 R1 | Admitir versiones sucesivas; impedir aplicar versión anterior o futura |
| C28 | Abstención estratégica y registros sin outcome | 3/3 R1 | Rechazar NaN para evitar cotas numéricas null |
| C29 | Corrección Holm de cinco contrastes | 2/2 | Rechazar un sexto contraste no preregistrado |
| C30 | Puertas de lanzamiento fiables | 2/2 | Incluso todos los booleanos ficticios positivos NO habilitan lanzamiento |

## Contrato de cierre A–J

**A — Estimandos:** cada intervención mide una **propiedad del instrumento** (estrato, arista, riesgo, alias, reloj, versión normativa, familia de contrastes), no efectos humanos o políticos reales. **B — Rivales:** en todos los casos, H1 verificaba una restricción y H0 permitía aceptación espuria; el rival competente es que estos invariantes son triviales/definidos por el propio código. **C — Diseño:** once endpoints diferentes y dos tests iniciales por ciclo, misma familia congelada por adelantado: no representar once confirmaciones independientes. **D — Instrumentación:** SHA de fuente y tests anteriores a outcome, más nuevo SHA y A–J de R1 para siete casos. **E — Ejecución:** 22 tests iniciales positivos insuficientes; tras falsadores reales, 22 pruebas de los siete casos reparados y 30/30 de regresión. El TAP de cada ciclo y sus hashes figuran en el recibo maestro. **F — Auditoría adversarial:** siete defectos concretos se encontraron **después** de las primeras pruebas y permanecen archivados; la corrección no borra los resultados invalidantes. **G — Comparadores:** controles anteriores medían ranking sin esfuerzo desplazado, clasificaciones posttratamiento, redes sin edge-dedupe, tiempo post hoc, derechos de entrega declarativos y condiciones de lanzamiento autodeclaradas; no se ha comparado la mejora con usuarios. **H — Priors:** PF-BR60–70 aportan *revisiones técnicas* del instrumento, no hallazgos científicos originales; PF-BR50–59 preservados. **I — Dictamen:** todos **AB-P válidos acotados solo de QA**, ciencia PFL **0/3**, CT2 de trayectoria científica **20/100 ordinal**, N1/N2/N3 nuevos **0/0/0**, puertas de lanzamiento **0/6**, cero experimentos humanos propios. **J — AB-DECIDE:** bloque nuevo terminado **30/30**, sin saldo; **2 plazas históricas STOP_R5** intactas. No continuar reproduciendo este generador para producir más número de ciclos. Siguiente clase de evidencia: exposición real autenticada y consentida o acceso legal a resultados humanos originales y a sus oportunidades, o replay original del Atlas Python; ningún permiso adicional inferido.

## Atlas y límites de sincronización

Se añadió lote append-only **0091** con 11 operaciones `run.add` diferenciadas para C20–C30, parent 0090. Se conserva la auditoría estructural de **89/89 lotes** anterior a 0090; **no se ejecutó el Python canónico** sobre 91 lotes, no atribuir digest final ni dashboard sincronizado. El conector rechazó modificar el grafo O7 canónico; los 11 nodos propuestos y el ajuste documental de C18 constan en [anexo pendiente](C20_C30_O7_ADDENDUM_PENDING.json), **no** en el grafo principal. Ninguna rama se fusionó a main; no se usó ChatRelay, CI costosa, datos de personas sin derechos, ni scoring de políticos reales.

**Resultado global de la campaña:** se fortaleció la instrumentación sintética y la trazabilidad, pero **no se demostró ninguna nueva explicación sociológica causal ni la eficacia del producto sobre una población real**.
