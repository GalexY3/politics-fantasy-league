# Politics Fantasy League · RELEASEPATH5 · 28/10/2026

**ESTADO: CERRADO 5/5 AB-H A–J, cinco AB-P ejecutados válidos acotados, 0 AB-R, 0 inválidos, 0 de planificación, 0 restantes.** Partiendo de AECCHOICE5 / PR #31, base SHA `c98b93587e97dab34a93dfec7bba1df3be8b6b45`. Se reorienta el trabajo al objetivo declarado por el investigador: completar **el producto realmente definido** y los logros acreditables, no maximizar ciclos ni medallas artificiales. No ChatRelay, fusión a main, pruebas CI costosas, publicación pública ni scoring de políticos reales.

## Diagnóstico del progreso — no confundir tres contadores

**V4: 36,90 %** (exactamente recalculado desde `product/progress_scope_v4_20261027.json`, 36 hitos en 9 tracks y ponderaciones 100). Faltan **63,10 puntos** para cumplir el alcance ponderado vigente; 8 hitos nivel0, 9 nivel1, 2 nivel2, 15 nivel3, 2 nivel4 y ninguno nivel5. Estos porcentajes son adjudicación manual con evidencia, no probabilidades ni función del número de artículos investigados. Llevar los 8 de nivel0 hipotéticamente a nivel5 aportaría **20,50 pp**, pero NO se ha ejecutado ni adjudicado tal avance. [C01 matriz](C01_SCOPE_CRITICAL_PATH.json).

**Logros: 5/90 desbloqueados desde 2/90**, tras auditar tres criterios documentales verdaderos y su registro append-only; no hay premio por crear informe sin cumplir su criterio. **Gates reales de salida pública: 0/6** porque falta fuente original RPP/candidaturas y derechos, identidad real, eventos verificables, autenticación multiusuario, E2E, hosting/piloto. Ni el 100% de medallas ni un número V4=100 levantan estas puertas. **CT2 29/100, VSDS 1/3, N1/N2/N3 nuevos 0**: no se ha producido descubrimiento nuevo.

## A–J · cinco ciclos reales

| Ciclo | Trabajo realmente ejecutado, evidencia y límites |
|---|---|
| [C01](C01_RESULT.json), [prereg](C01_PREREG.json) | **Auditoría del contrato V4 vigente** mediante cálculo real de 36 hitos y sus pesos. Reconstrucción exacta de **36,90 %**, ocho nivel0 y 9 nivel1, y mapa de contribuciones pendientes; se conserva la diferencia entre niveles potenciales y niveles validados. [Matriz cuantitativa](C01_SCOPE_CRITICAL_PATH.json). |
| [C02](C02_RESULT.json), [prereg](C02_PREREG.json) | **Nuevo modelo operativo STRIDE y reputacional**: inspeccionados `server.py`, `scoring.py`, `events.py`, `evidence_warehouse.mjs` y gate jurídico. Publicado [modelo STRIDE](../../docs/THREAT_MODEL_STRIDE_PUBLIC_RELEASE_20261028.md) de cinco fronteras, diez ataques S/T/R/I/D/E, nueve pruebas negativas y criterios explícitos GO/NO-GO. **Documento de amenazas, NO pen-test, mitigación de auth ni validación legal**. |
| [C03](C03_RESULT.json), [prereg](C03_PREREG.json) | **Tres desbloqueos con criterio comprobable:** [Registro v6](../../ab_atlas/ACHIEVEMENTS_REGISTRY.json) actualizado con eventos seq 4–6, evidencias y verificador: `PFL-SCIENCE-01` se acredita con [PLAN_TFM.md](../../docs/PLAN_TFM.md) (estimando y rivales explícitos); `PFL-EVENTS-01` con [ARQUITECTURA.md](../../docs/ARQUITECTURA.md), `events.py` y warehouse (ontología tipada, roles y no-causalidad); `PFL-SECURITY-02` con STRIDE recién auditado (incluye abuso/reputación). 90 IDs únicos, dependencias comprobadas en V8. **2→5/90**, sin tocar V4 ni gates, y sin declarar ejecución del validador Python/HTML visual nativo. [Registro de adjudicación](C03_ACHIEVEMENT_ADJUDICATION.json). |
| [C04](C04_RESULT.json), [prereg](C04_PREREG.json) | **Instrumentación real fail-closed**, no simple checklist: [seis gates en JSON](../../product/release_gates_v1_20261028.json), [guardia CJS](../../src/politics_fantasy/release_guard.cjs) y [9 tests Node preparados](../../tests/test_release_guard.cjs). Se cargó el código Git *exacto* en V8 y se ejecutó con el V4 real, registro v6 y mutantes adversariales: primera pasada **8/9**, falla el patrón de fecha por sobreescape; corregido, **9/9**. Un 100% V4 inventado y 90 medallas inventadas siguen bloqueadas si gates no verificados. El callback `()=>true` demuestra **solo flujo de control ficticio**, NO atestación real. La CLI carece de verificador externo y es **NO-GO** permanentemente; ejecución Node nativa y suite integral pendientes T025. [Recibo rojo→verde](C04_GUARD_TESTS.json). |
| [C05](C05_RESULT.json), [prereg](C05_PREREG.json) | **Cálculo del grafo de dependencias** con los 36 hitos y los 90 logros v6: **9 logros ahora con prerrequisitos satisfechos** pero no automáticamente merecidos, **76 todavía bloqueados por requisitos previos**; cinco paquetes con propietarios/criterios verificables conectados a los seis gates. [Matriz ejecutada](C05_PRIORITY_MATRIX.json). [T025](../../tareas_codex/T025_RELEASEPATH_V6_QA_AND_GATE_EVIDENCE_20261028.md) entrega a Codex aceptación exacta de QA nativa, ledger v6, guardia, amenazas y separación demo/observatorio/juego real. **T025 preparada, NO ejecutada**. |

El elemento de mayor valor no es elevar el marcador mediante especificaciones triviales, sino **eliminar la confusión de fuentes, puntuación y lanzamiento** y dejar un mecanismo verificable para no declarar la versión pública completa sin evidencia.

## Orden crítico hacia producto real

1. **P0 Fuentes y derechos:** corpus RPP y candidaturas originales verificables, cobertura, `first_public_at`, licencias específicas y evaluación experta de finalidad/RGPD. Bloquea tres puertas de hecho: RPP/derechos, identidad, eventos.
2. **P0 Identidad y eventos:** resolver personas/cargos con claves institucionales y control de falsos matches; cadena bitemporal de eventos atribuidos sin inferir ideología ni ausencia=culpa.
3. **P0 Auth y seguridad de producto:** el servidor actual `server.py` es **solo loopback** sin autenticación multiusuario ni protección de recursos ajenos; no exponer mediante reverse proxy. Requiere auth, IDOR/CSRF, tasa y pruebas de carreras.
4. **P0 E2E y QA independiente:** replicar tests de Python/Node/navegador en mismo checkout con hashes, reproducción completa de fuentes admisibles y prueba de reglas sin fugas temporales.
5. **P1 Piloto y hosting:** tras revisión jurídica y de accesibilidad, piloto de usuario explícito, registros de errores y corrección. No suponer que un videojuego público queda autorizado por tener demo local.

**Modos diferenciados:** la demo sintética local no es lanzamiento comercial; un observatorio agregado seguro podría constituir otra versión **solo tras cambio de alcance y revisión de licencias**, sin contar como 100% del PFL actual; juego público de personas reales sigue **BLOQUEADO 0/6**. [Grafo de prioridades](C05_PRIORITY_MATRIX.json).

## Resumen de indicadores

| Indicador | Antes | Después |
|---|---:|---:|
| Ciclos concedidos / ejecutados | 5/0 | **5/5** |
| AB-P / AB-R / inválidos / planificación | — | **5/0/0/0** |
| V4 contractual | 36,90% | **36,90%** |
| Logros simbólicos | 2/90 | **5/90** |
| CT2 identidad | 29/100 | **29/100** |
| VSDS | 1/3 | **1/3** |
| Gates de lanzamiento | 0/6 | **0/6** |
| N1/N2/N3 científicos nuevos | 0/0/0 | **0/0/0** |

[Ledger A–J y commits](CAMPAIGN_STATUS.json) · [CT2 historial](CT2_TRAJECTORY.json) · [CT2 completo 0–100 y ampliado 27–31](CT2_FULL_AND_ZOOM.svg). No confundir los tres nuevos bronces con avances de V4; el HTML Hall V1 tiene snapshot embebido para `file://` y puede requerir importación del JSON v6 o regeneración **no realizada**. El validador Python oficial y el test Node nativo quedan para T025.

## Cuello de botella y estado verdadero del ejecutor

**T025** está especificada y **NO ejecutada**; se conservan **T011 y T016–T024** pendientes, sin atribuirles efectos o validaciones. El código del guard fue probado en V8 sobre exactos bytes Git; **no hay suite integral de un checkout limpio** ni certificación jurídica o pentest. El primer fallo en el regex se guarda para auditar reparación.

**SOLICITO BRANCHING 5 CICLOS AB-H ADICIONALES**, condicionado a autorización explícita, con prioridad de ingeniería verificable, QA y autenticación de fuentes e identidad —no volver a estudiar correlaciones ya conocidas en otros países para aparentar avance—, sin ChatRelay ni fusión a main. Al no existir evidencia para completar los seis gates desde este entorno, R5 aconseja paralizar cualquier llamada a “lanzamiento” hasta la verificación externa.

