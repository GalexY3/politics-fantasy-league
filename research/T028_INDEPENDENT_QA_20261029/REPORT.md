# Politics Fantasy League · T028 — continuación independiente QA y puerta de evidencia · 29-10-2026

**No constituye un ciclo AB adicional:** campaña nueva ABH30 cerrada 29 válidos acotados y C01 incompleto; **dos plazas históricas PR37 siguen sin consumir**. Esta intervención es una reparación/QA y una revisión de antecedentes, no una nueva evaluación causal. Rama sucesora de PR #40, sin fusión a `main`.

## Entregables nuevos y evidencia efectivamente ejecutada

**Asignador ficticio C06, prueba independiente tras reparación:** [prerregistro](SEED_HOLDOUT_PREREG.json) `a4fe5b87d5c3571155926702dc9c96f45f23ea16`, [código Node portable](../../src/politics_fantasy/pilot_assignment_holdout_qa.mjs) y [resultado A/B de robustez](SEED_HOLDOUT_RESULT.json).

Sobre Git blob fuente `44e194c7d52826e4adcf8c966060734ade6956cb`, se ejecutaron tres ventanas **no usadas para elegir el parche C06**:
- Semillas 4.096–8.191 (4.096): máxima desviación relativa posición×brazo **6,1523 %**.
- Semillas 2.147.483.648–2.147.487.743 (4.096): **6,3477 %**.
- Semillas 4.294.963.200–4.294.967.295 (4.096): **5,2734 %**.

Cada ventana cumple el umbral preregistrado **≤12 %** y presenta las 24 permutaciones; se verificó balance exacto por bloque, invariancia de 4 condiciones, repetibilidad, congelación de array, tamaños 8 y 10.000 y seis negativos de validación. Total **12.288 semillas nuevas**, más n grande en controles. La suite anterior **84/84** se ejecutó sobre el espejo parcial. Esto avala **solo** el simulador determinista de asignación; no acredita secreto, aleatorización criptográfica, ausencia de selección en personas ni validez causal.

**T028 preflight sin Codex:** [runner portable](../../tareas_codex/T028_NATIVE_PREFLIGHT.py), [recibo estructurado](T028_PREFLIGHT_RECEIPT.json). En un espejo parcial de los archivos originales identificados con Git blob se ejecutó un runner Python local equivalente; la **versión exacta de runner subida a GitHub no se ha ejecutado en un checkout completo**, por lo que cualquier repetición debe ejecutarse y validarse en el destino.

Resultados locales observados:
- `node pilot_local/smoke_http.mjs`: **15/15 PASS**.
- **9 comprobaciones HTTP** adicionales en loopback `127.0.0.1:8787`: positivas 200 y negativas 404/405, CSP `connect-src 'none'`, `no-store`, `nosniff` y sin cookies; **9/9 PASS**.
- Playwright `APIRequestContext`: GET 200, pero Chromium `page.goto`: **`net::ERR_BLOCKED_BY_ADMINISTRATOR`**. Se registró como bloqueo ambiental, no como fallo de la aplicación, y **no se eludió**.
- **Atlas Python canónico:** `NOT_RUN_MISSING_SOURCE` en el espejo local. La PR #40 había verificado por GitHub los **80 JSON**, sus blobs y **79 parent_batch**; **no equivale** a `python atlas_delta.py check` ni a `abmap.require_valid(strict=True)`. SHA256 del estado canónico sigue **UNKNOWN**; `ab_atlas/CURRENT.md` no se actualiza.

## Nuevo antecedente adversarial, no ciclo AB-R

Hudja, Roberson y Rosokha (2025), **«Public Leaderboard Feedback in Sampling Competition: An Experimental Investigation»**, `Review of Economics and Statistics` 107(2), 555–569, DOI `10.1162/rest_a_01259`. [Ficha bibliográfica](https://ideas.repec.org/a/tpr/restat/v107y2025i2p555-569.html) y [página académica del autor](https://web.ics.purdue.edu/~yrosokha/research.html). Estudia concursos de muestreo secuencial con esfuerzo costoso y final fijo. La teoría y el experimento de laboratorio encuentran configuraciones donde publicar el leaderboard **reduce el número esperado de observaciones y la calidad del resultado ganador**, frente a la alternativa sin esa información. Es una objeción fuerte a inferir que **mostrar rankings siempre aumenta la participación o calidad**. 

Este antecedente no estima el efecto del piloto PFL T×L ni demuestra que ocurrirá en PFL. Tampoco justifica promediarlo indiscriminadamente con Lemus y Marshall (2021), que estudian otra arquitectura de concursos y obtienen mejora media en su entorno. Para defender novedad ahora es necesario identificar el **mecanismo y contexto que prediga el signo** (horizonte, coste de intento, posición, reputación, visibilidad de oportunidades) y contrastarlo con controles competentes; no basta con contraponer narrativas publicadas.

**Licencias:** se localizó la página académica y referencias a software experimental, pero **no** se ha comprobado permiso específico para reutilizar microdatos individuales ni se han recuperado archivos de exposición o asignación; ningún cálculo con participantes fue realizado.

## Gates de lanzamiento, inspección del seed

Se recuperaron del `seed.json` original de GitHub los seis `release_gates`. Su semántica se mantiene:

| Gate | Estado de partida | Requisito no demostrado |
| --- | --- | --- |
| `data_registry` | BLOCKED | RPP/candidaturas originales suficientes y reconciliadas |
| `identity` | BLOCKED | Identidad individual multifuente con vigencia temporal |
| `events` | BLOCKED | Eventos verificables por persona y fecha |
| `authentication` | PENDING | Autenticación y autorización multiusuario |
| `e2e` | PENDING | E2E de aplicación completa, no solo piloto ficticio |
| `deployment` | PENDING | Despliegue público seguro |

**0/6 aprobados**. Las 9 pruebas HTTP locales no son el `e2e` global ni autorizan publicar datos reales. El modo ficticio offline puede servir para probar usabilidad sin avanzar artificialmente release gates.

## Qué falta para cerrar de verdad T028

1. Ejecutar en checkout privado autorizado, desde raíz, el runner versionado con `python proyectos/politics-fantasy-league/tareas_codex/T028_NATIVE_PREFLIGHT.py --repo . --out /tmp/T028_PREFLIGHT_RESULT.json`. Registrar SHA de HEAD y stdout/stderr/exit del original **`python ab_atlas/atlas_delta.py check` y `brief`**. Solo con `PASS` y SHA256 canónico se puede reconciliar `CURRENT.md`; no reescribir lotes 0079/0080 ni sus marcas de tiempo.
2. Ejecutar Playwright Chromium navegando al servidor HTTP real en un entorno donde esa navegación esté **permitida**. Si continúa el bloqueo administrativo, mantener `BLOCKED_BY_ENVIRONMENT` y conservar la evidencia API/DOM parcial sin afirmar E2E.
3. Para la línea científica, obtener documentación y bytes legítimos con exposición/eligibilidad individual pre-respuesta o diseño de asignación; congelar prereg y competidores antes del cálculo. Sin esos datos, **STOP_R5** para causalidad y 2/3.

**Métricas sin cambios:** CT2 prospectiva **22/100 ordinal**, N1/N2/N3 nuevos **0/0/0**, madurez V4 **36,90 % contractual**, gates **0/6**, T028 **NEEDS_EXECUTOR para checker y browser**, sin ChatRelay, CI costosa, publicación, fusión a main, reclutamiento ni scoring de políticos reales.
