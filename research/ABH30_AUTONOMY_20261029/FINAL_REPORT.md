# Politics Fantasy League · Campaña AB-H 30 (20 investigación + 10 autonomía) · cierre R5

**Fecha:** 29/10/2026. **Rama de trabajo:** `research/pfl-abh30-autonomy-research-20261029`, PR draft #40 apilada sobre #39. **Autorización nueva: 30 ciclos; intentados: 30; válidos A–J de alcance acotado: 29; intento incompleto preservado: 1 (C01); pendientes de intentar: 0.** No equivale a 30 descubrimientos científicos ni a 30 experimentos causales.

**Presupuesto previo distinto:** campaña PR37: 5 concedidos, 2 válidos, 1 incompleto, **2 sin ejecutar**. No se reapropió ni fusionó su saldo con estos 30. No se solicitó financiación/cupo adicional.

- [Autorización reconciliada](AUTHORIZATION_AND_GATE.json) · [estado final](STATUS_20261029.json) · [CT2 JSON](CT2_TRAJECTORY.json) · [gráfico CT2 completo y ampliado](CT2_FULL_AND_ZOOM.svg) · [hallazgos negativos y priors](FINDINGS_AND_PRIORS.json) · [T028 pendiente](../../tareas_codex/T028_BROWSER_ATLAS_REPLAY_20261029.md).
- Cada ciclo: `Cxx_PREREG.json` antes del `Cxx_RESULT.json` o `C01_INCOMPLETE.json`, y `Axx_PREREG.json` antes de `Axx_RESULT.json`; originales, reparaciones y erratas conservados. **A04_INCOMPLETE.json** se mantiene, aunque A04 se reparó en ocho lotes y cerró como el **mismo ciclo**, no un segundo ciclo.
- Protocolo [AB 3.2.1 O1–O6](../../../../docs/METODO_AB_3_2_1.md): R1 estimando, R2 rival competente, R3 exposición a selección, R4 ablación, R5 stop por cuello de botella. Las 10 pruebas de autonomía son ensayos técnicos, no estudios sociológicos experimentales.

## Marcadores al inicio y cierre

| Magnitud | Inicio | Cierre |
|---|---:|---:|
| Fase I · válidos/incompletos/no intentados | 0/0/20 | 19/1/0 |
| Fase II · válidos/incompletos/no intentados | 0/0/10 | 10/0/0 |
| Total nuevos | 0 válidos, 30 disponibles | **29 válidos, 1 incompleto, 0 por intentar** |
| CT2 prospectiva ordinal | 22/100 | **22/100** |
| N1/N2/N3 nuevos | 0/0/0 | **0/0/0** |
| VSDS contractual | 1/3 | 1/3 |
| V4 contractual | 36,90 % | 36,90 % |
| Puertas de lanzamiento | 0/6 | 0/6 |
| Experimentos causales con humanos | 0 | 0 |

**CT2** es confianza ordinal de trayectoria hacia 2/3, **no P(descubrimiento)**. No aumentó porque fueron mayoritariamente pruebas de QA, documentación y datos agregados sin atribución causal. No se aplicó artificialmente una subida por haber realizado 30 intentos.

## Fase I: resultados A–J, evidencia positiva y adversarial

**C01 incompleto:** preregistro del enlace preguntas–resoluciones ForecastBench 2024, test de 200 preguntas, composite key `(source,id)`, recuentos y control negativo. La fuente de resoluciones (≈2,7 MB) no se recuperó íntegramente del conector: `JSON.parse` falló. La consulta alternativa al espejo público tampoco proporcionó bytes completos. No se calcularon joins ni resultados; permanece incompleto. No confundir metadatos Git con SHA256 real del JSON.

**C02–C05, cuatro preguntas exploratorias distintas sobre la misma tabla agregada pública ForecastBench** (licencia CC BY-SA 4.0, [source repository](https://github.com/forecastingresearch/forecastbench-datasets), blob baseline `fa76366ba425a0597d0af3c847197cd4be2d2fe7`): C02 130 registros válidos y 63 valores de `N dataset` distintos entre 119 filas de modelos; control de suma de N pasa 130/130. C03 muestra que el índice Overall no es siempre la media aritmética de los índices por categoría (17/130 filas con diferencia >0,051; máxima 1,65). C04 solapamiento top-10 Dataset/Market 0, Dataset/Overall 2 y Market/Overall 8; Spearman con empates por rango Dataset/Market ≈0,664. C05 asociación negativa entre N y anchura de IC del 95 %: ρ de rangos Dataset ≈−0,875 y Market ≈−0,775. **No son cuatro réplicas independientes** ni estiman efecto de leaderboard en PFL. Ajuste por dificultad e incertidumbre son antecedentes ya existentes en ForecastBench.

**C06–C11, QA/identificación del piloto ficticio con código original cotejado por Git blob y Node local:**
- **C06 hallazgo negativo+reparación:** 4096 semillas consecutivas del asignador inicial mostraron desbalance posicional máximo del **33,50 %**, aunque cada bloque de cuatro tenía una condición de cada brazo. Se introdujo avalanche deterministic de 32 bits antes del LCG, con test de regresión versionado: desbalance máximo **6,35 %**, objetivo preregistrado ≤8 %; 84/84 tests nativos anteriores siguen verdes. El original y su reparación se conservaron como **un único ciclo**. No es asignación criptográfica ni ensayo real.
- **C07** un outcome ficticio ausente hace que el estimando complete-case 2 no equivalga al ITT; límites compatibles del efecto principal de transparencia **1,25 a 2,25** en escala 0–4. El analizador etiqueta correctamente `COMPLETE_CASE_NOT_ITT`.
- **C08** 240 rutas HTTP negativas rechazadas 404/240, 5 rutas permitidas respondieron 200/5 y CSP presente. Solo servidor local.
- **C09** `approval` mock permite `review_ref` arbitrario: es **una vulnerabilidad semántica de interpretación si se presenta como aprobación ética**, no autorización real.
- **C10** rechazo correcto de getters maliciosos y claves Symbol en validador/analizador, sin evaluación de getters de prueba.
- **C11** 80 solicitudes GET/HEAD/POST no cambiaron hashes SHA256 de cinco archivos fuente auditados; no demuestra seguridad completa.

**C12–C15, novedad de producto y guardarraíles:** antecedentes de fantasy politics (Politiplay, Politiparty, Fantasy Parliament) refutan novedad del mecanismo genérico roster/puntos/leaderboard, sin acreditar usuarios ni adopción de esos competidores. C13 literatura de gamificación muestra resultados de leaderboard **heterogéneos**, incluidos nulos/negativos; no extrapolar impacto en aprendizaje electoral. C14 revisión limitada de RGPD (arts. 5, 6 y 25) refuerza minimización, base jurídica y privacy-by-design. C15 comprobación DOM: 12/12 radios con etiquetas y cuatro `fieldset` con `legend`, más selector de brazo etiquetado; no certificación WCAG completa.

**C16–C20, incentivos, potencia y navegador:** C16 ejemplo exacto con verdad p=0,6, rival q=0,5: Brier esperado honesto 0,24 frente a reporte agresivo 0,3921, pero probabilidad de ganar evento único 0,6 en ambos; premios de un solo ganador no implican por sí mismos sinceridad y tienen antecedentes publicados. C17 ForecastBench aplica reglas propias de maduración/soluciones antes de torneos, no equivalentes a la demo ficticia PFL. C18 bajo outcomes 0–4, independencia y cuatro celdas balanceadas, una interacción de 0,5 requeriría aproximadamente **2008 observaciones totales** con varianza máxima para prueba normal 80 %/α=.05; **no es un plan de reclutamiento autorizado ni cálculo de poder validado para PFL**. C19 `textContent` presenta como texto literal una carga HTML maliciosa, sin elemento ejecutado; control `innerHTML` no. C20 flujo de teclado en Chromium `about:blank`: selector, cuatro radios, progreso y reinicio funcionales; **no HTTP navegador real ni validación WCAG integral**.

**Interpretación de fase I:** existe progreso técnico real y delimitación negativa de la novedad genérica. Sin exposición individual verificable, hipótesis causal de transparencia × leaderboard con humanos permanece sin estimar. Todos los grados científicos de novedad propia **0/3**, ningún N1/N2/N3 adjudicado. Se han documentado comparadores fuertes y selección adaptativa; no reusar el mismo conjunto público como nueva confirmación.

## Fase II: 10 ensayos autónomos frente a bloqueos Codex

| Ciclo | Prueba ejecutada | Resultado y límite |
|---|---|---|
| A01 | Leer PR40/AGENTS/T028 y HEAD autenticados por GitHub | **PASS:** acceso privado de lectura, sin shell del repo |
| A02 | Contrastar 10 blobs Git entre espejo local y GitHub | **PASS tras errata:** 10/10; primera transcripción falló 9/10, [errata](A02_ERRATA.json) conservada |
| A03 | Enumerar actualizaciones de Atlas | **PASS:** 80 archivos numerados, sin huecos ni 0081 |
| A04 | Parsear 80 JSON y enlaces por lotes | **PASS tras reparación:** 80/80 JSON, 80/80 blobs, 79/79 padres; [ocho recibos](A04_CHUNK_01.json) a `A04_CHUNK_08.json`; 0079/0080 cronología irregular; **no Python canónico** |
| A05 | Recuperación GitHub de archivos por tamaño | **PARTIAL/BOUNDED:** 120k y 553k legibles, ≈2,7 MB no recuperado; rangos grandes vacíos |
| A06 | Python local, fixture, integridad | **PASS local:** Python 3.13.5, SHA256 fixture; **sin `atlas_delta.py` completo** |
| A07 | Node local, 84 tests y prueba 4096 semillas | **PASS 84/84 y seed repair** con módulos originales cotejados; sin suite integral del repo |
| A08 | Servidor local y API HTTP | **PASS** localhost 200 y denegación POST/ruta secreta, CSP/no-store; no navegador E2E |
| A09 | Playwright API HTTP vs Chromium navegación | **NEGATIVO comprobado:** APIRequest GET 200, `page.goto` Chromium `ERR_BLOCKED_BY_ADMINISTRATOR`; no elusión |
| A10 | GitHub create→readback→draft PR | **PASS** escritura/lectura idéntica en rama, 404 negativo y `main` inmóvil; sin agentes `ollama`/`qwen`/`codex` instalados |

La mayor **reducción de dependencia de Codex** es demostrada: el acceso al repositorio, las pruebas Node y Python de subconjuntos, la revisión de 80 metadatos Atlas, el servidor HTTP, la creación de código/tests/PR draft pueden realizarse directamente con las herramientas actuales. **No se ha demostrado** poder ejecutar el checker canónico Atlas con grafo completo, ni HTTP Playwright Chromium, ni el checkout privado íntegro; T028 continúa **PENDIENTE**. La restricción Chromium es ambiental (`ERR_BLOCKED_BY_ADMINISTRATOR`), no un defecto confirmado de PFL.

## Auditoría adversarial transversal, DRIFT y decisiones

R1: simulación ficticia no equivale a comportamiento político. R2: ForecastBench ajuste por dificultad/IC y literatura de premios/leaderboards usados como controles competentes. R3: C02–C05 comparten tabla y selección; QA de C06 reparación fue guiada por datos, no holdout independiente. R4: pruebas nulas, controles negativos, ramas HTTP bloqueadas y reparación reproducible; no ocultar primer fallo. R5: campañas técnicas pueden cerrarse sin atribución científica.

Distancia DRIFT aproximada **D0–D1** dentro de PFL: C12–C15 cambian fuentes y dimensión de investigación, pero no estimando causal hacia 2/3. Fase II es un cambio instrumental (no nueva teoría sustantiva). No reivindicar DRIFT D3–D5 ni transferir grado científico de ingeniería a análisis social. El próximo experimento realmente discriminante requiere **datos legales con oportunidad individual visible, asignación/fecha y outcome** o protocolo ético defendible para personas, no más simulaciones con outcomes impuestos.

**Validez/ética:** Sin usuarios reclutados, identidades/políticos reales evaluados, datos personales recolectados, autorización ética humana ni despliegue público. No se ejecutó ChatRelay ni CI costosa; no se fusionó `main`. El estatus mock `APPROVED_BY_HUMAN_REVIEW` no constituye permiso externo. Las pruebas locales no certifican lanzamiento; V4 36,90 % y 0/6 puertas conservadas.

**Dictamen final:** **30 intentos documentados, 29 A–J válidos acotados, C01 incompleto; R5 STOP_CAMPAIGN**. Se recomienda **no pedir nuevos ciclos** porque todavía hay **2 plazas históricas concedidas y sin ejecutar**, y el cuello de botella científico no puede resolverse con más tablas agregadas; T028 debe permanecer pendiente hasta que un entorno autorizado ejecute Python Atlas canónico y Playwright HTTP. Mantener CT2 22, N1/N2/N3 0/0/0 y el historial negativo.
