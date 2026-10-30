# PFL-CODEX-T028 — EJECUTOR: replay canónico Atlas 0001–0080, navegador HTTP real y auditoría

**ESTADO VIGENTE 29/10/2026: NÚCLEO TÉCNICO P0 COMPLETADO Y VERIFICADO SIN CODEX.** Se han ejecutado **80/80 lotes Atlas con Python original y SHA256 canónico** ([GitHub Actions 40805714464](https://github.com/GalexY3/Metodologia-AB/actions/runs/40805714464)) y **21/21 comprobaciones Chromium/Playwright por HTTP real** ([GitHub Actions 40806035386](https://github.com/GalexY3/Metodologia-AB/actions/runs/40806035386)), ambos trabajos de un solo job y límites de 3–4 minutos. **Resultado completo:** [T028_RESULT.json](T028_RESULT.json) y [T028_RESULTADO.md](T028_RESULTADO.md). El `CURRENT.md` canónico se actualizó tras PASS. El piloto ficticio no supera las 6 puertas generales de lanzamiento ni aporta validación causal; R5 sigue bloqueando investigación humana sin fuente legal y asignación/exposición. **La orden histórica de ejecución se conserva a continuación por procedencia; no debe interpretarse como tarea aún pendiente.** Esta ficha es una orden autocontenida para Codex (checkout Git, Python, Node y Playwright), preparada por ChatGPT a petición del usuario el 29-10-2026. No es autorización de despliegue, reclutamiento, fusión ni gasto de CI.

## 0. Punto de partida, preflight y reglas

- Repo privado: `GalexY3/Metodologia-AB`.
- PR fuente **#37**: `https://github.com/GalexY3/Metodologia-AB/pull/37`, rama `research/pfl-abh5-browser-atlas-independent-20261029`; HEAD de referencia **`7d622850d0410db3b3e8b8d7acbe01a1bdea7a42`**.
- Esta ficha y BACKLOG pueden estar en una rama PR sucesora: si la cola se ha actualizado después del HEAD de PR37, **comprueba la PR de entrega de esta ficha y basa tu trabajo en el HEAD que contenga tanto PR37 como esta tarea**, sin perder cambios. No uses `main` como origen de trabajo.
- Al comenzar lee `AGENTS.md`, `README.md`, protocolo AB 3.2.1 O1–O7, `ab_atlas/README.md`, `proyectos/politics-fantasy-league/ab_atlas/{README.md,CURRENT.md}`, `T027_PILOT_BROWSER_ATLAS_ETHICS_20261029.md`, el ledger de `research/ABH_BROWSER_ATLAS_EVIDENCE5_20261029/` y su `FINAL_REPORT.md`.
- Verifica permisos reales, HEAD/base de PR37, rama de esta ficha, `git status`, commits y SHA de `main`; crea rama sucesora de trabajo desde el HEAD efectivo autorizado más reciente. Si ves cambios ajenos, haz análisis del diff antes de tocar nada. Sin force push, sin merge.
- **Prohibiciones:** no ChatRelay, no CI costosa, no main merge, no despliegue público, no reclutamiento ni tratamiento personal, no scoring de políticos/partidos/candidatos reales, no claves ni secretos en logs y no elusión de las restricciones del entorno.
- **Contabilidad AB-H congelada:** autorización 5; **2 ciclos válidos**, **1 intento incompleto C02**, **C04 y C05 no ejecutados (2 plazas sin usar)**. Completar una tarea Codex **no consume** esas dos plazas ni acredita causalidad. Si C02 llega a resolución técnica, preservar resultado previo y emitir recibo enlazado, sin borrar el intento ni contarlo dos veces. R5 prevalece.

## 1. PRIORIDAD P0 — Atlas Python canónico, no solo JSON encadenados

El control anterior analizó **79 archivos 0001–0079** y verificó continuidad de `parent_batch`; 0080 se añadió en PR37. Eso **NO equivale** a ejecutar el replay ni a validar la semántica del grafo.

Desde raíz de un checkout privado completo:

```bash
python --version
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
python ab_atlas/atlas_delta.py brief --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates --limit 8
```

Coteja la semántica de `atlas_delta.py` y `abmap.py`: 80 lotes y `parent_batch`, `batch_check`, `apply_one`, `abmap.require_valid(strict=True)`, ID único de cada run/complaint/nodo/arista, referencia, gate, timestamp ISO y ausencia de promover validación científica o release gates por mero cierre.

Registra **comando real, entorno, exit code y stdout/stderr**, HEAD, conteos (batch, run, node, edge, complaint, gates), IDs de 0078–0080, hash SHA-256 del estado canónico calculado por el código del repositorio y diferencias contra seed y parent 0077. Valida 0080: exactamente **2 `run.add`** (C01 y C03), no 5.

**Incidencia histórica:** 0079 declara `at=2026-10-29T01:00:00Z`; 0080 declara `2026-10-29T00:26:37.468Z`. Examina fecha real de commits, regla del parser y si la cronología irregular exige errata; **no cambies silenciosamente esos lotes ni inventes una fecha**.

**Solo si `check` pasa y el estado/hash está verificado**: actualiza `proyectos/politics-fantasy-league/ab_atlas/CURRENT.md`, preserva el historial y escribe cabecera veraz sobre 0080 y las plazas AB-H pendientes. Vuelve a comprobar replay y coherencia. Si falla, encuentra el **primer** lote/operación causante, guarda el error y haz la mínima reparación permitida (preferir nuevo lote/errata, no reescritura histórica); si no es seguro, marca `BLOCKED` y **no declares CURRENT sincronizado**.

## 2. PRIORIDAD P0 — navegador Playwright HTTP end-to-end real

El resultado anterior **18/18 en Chromium 144** fue una prueba DOM en `about:blank`, con import inline para esquivar restricción de administrador. NO acredita HTTP/browser real. También existen 15/15 checks nativos HTTP en una campaña anterior.

```bash
node --version
node proyectos/politics-fantasy-league/pilot_local/smoke_http.mjs
node proyectos/politics-fantasy-league/pilot_local/server.mjs
```

Abrir **`http://127.0.0.1:8787/`** con Playwright + Chromium y opcionalmente Firefox en un entorno autorizado. Comprobar **navegación HTTP, carga real HTML/CSS/JS/`/materials.mjs` y CSP aplicada**, más:

1. Cuatro condiciones T×L, mismo conjunto X1–X4 y 12 radios; cambiar condición cambia tutorial/leaderboard, no el contenido del test.
2. Ratón, tabulación, lector de etiquetas/fieldset, progreso, reset; escritorio/móvil sin overflow y sin errores JS.
3. Ausencia de envío de resultados, cookies, almacenamiento local, analítica, telemetría y peticiones a otros orígenes.
4. `fictional_transfer_key.mjs`, intake, análisis y rutas no autorizadas no son recursos públicos; POST/PUT/DELETE denegados; CSP `connect-src 'none'`, `no-referrer`, `no-store`, `nosniff`.
5. Capturas de ambas resoluciones, registro de peticiones/respuestas y consola **sin información sensible**.

Versiona tests Playwright deterministas y registra versiones, exit codes y PASS/FAIL/SKIP, con controles negativos. Si la política del navegador devuelve `ERR_BLOCKED_BY_ADMINISTRATOR`, **no la burles ni atribuyas el problema a la aplicación**; marca `BLOCKED_BY_ENVIRONMENT`, conserva el 18/18 DOM (sin recontarlo como E2E) y pide un host autorizado. Evita reescribir UI solo para pasar un harness que esperaba texto incorrecto.

## 3. PRUEBAS Y CORRECCIONES REALES

Ejecuta la suite relevante de Python/Node de alcance razonable, y las regresiones focalizadas de la nueva UI/Atlas. Respeta que la campaña anterior encontró campos ocultos heredados/`Symbol` en validadores basados en `Object.keys` y parcheó tres módulos: verifica que no se ha perdido esa garantía. `approval` en `pilot_dryrun_intake.mjs` es **mock falsificable**, nunca autorización ética.

Por cada defecto: prueba FAIL reproducible → versión y hash → parche **mínimo** → PASS del fallo → regresión → comprobación de no nuevas filtraciones. Conservar fallos y erratas. No declarar suites amplias PASS sin ejecutarlas ni adoptar cambios de arquitectura no solicitados.

## 4. FUENTES Y PRUEBA CIENTÍFICA (solo si aparece evidencia distinta)

Los prior art de Frongillo et al. y Monroe et al. (AAAI 2025), Lemus & Marshall (JPE 2021), premios contingentes (2025) y señalización política (2019) impiden afirmar novedad general. Para comprobar algo más, primero conseguir paquete empírico **legalmente reutilizable**, con licencia/permiso, archivos reales, SHA, fechas, variables, exposición, outcomes y comparador competente. **Prerregistra antes de calcular** y separa la novedad científica de la calidad de la aplicación. Si no, STOP_R5 sin más simulaciones de relleno.

## 5. ENTREGABLES + PR DRAFT

Crear:
- `proyectos/politics-fantasy-league/tareas_codex/T028_RESULT.json` (estatus específico PASS/FAIL/BLOCKED/SKIP/NOT_RUN, fecha y SHA del HEAD, entorno, comandos, stdout/stderr/exit, hash estado, tests, limitaciones).
- `proyectos/politics-fantasy-league/tareas_codex/T028_RESULTADO.md` (informe reproducible con comparación anterior, defectos y correcciones reales).
- Tests de browser y regresión versionados si los escribes y ejecutas; capturas sin datos personales.
- `CURRENT.md` **solo con replay canónico PASS**; no reescribir deltas históricos.
- Ledger/prior/CT2 **solo** si se obtiene evidencia realmente nueva. El cierre técnico no eleva N1/N2/N3 ni permite un scoring político real.

Abrir PR **draft sucesora** a la rama exacta que contiene PR37 y esta cola (apilada, sin fusionar). Título sugerido: `PFL T028: canonical Atlas 0080 replay and real browser E2E`. Mantén `main` sin modificar y CI costosa sin activar.

El informe final ha de contener: HEAD inicial/final, PR URL, check Atlas/80 lotes/estado SHA256, browser por HTTP y capturas, regresiones FAIL→FIX→PASS, derechos/fuentes si se investigaron, límites, estado exacto de las **2 plazas AB-H no ejecutadas**, y una única siguiente dependencia con criterios de aceptación.

**Empieza ejecutando, no únicamente planificando. No confirmes éxito antes del test. Si hay bloqueo, deja evidencia exacta y STOP_R5.**

## Evidencia nueva (ABH30, 29/10/2026): trabajo autónomo verificable, pero T028 sigue pendiente

- El conector GitHub obtuvo y parseó **80/80 archivos JSON** del Atlas mediante ocho recibos `research/ABH30_AUTONOMY_20261029/A04_CHUNK_01.json` … `A04_CHUNK_08.json`; los **80 blobs Git coinciden**, y los **79 enlaces parent_batch consecutivos** pasan. [A04_RESULT.json](../research/ABH30_AUTONOMY_20261029/A04_RESULT.json) conserva la prueba completa, además del intento inicial incompleto. No hay `0081`. Anomalía temporal 0079/0080 persistente. **Esto NO ejecuta el parser original ni el `abmap.require_valid(strict=True)`; el hash SHA256 del estado gráfico sigue no calculado y `CURRENT.md` no se sincroniza sin él.**
- Se ejecutaron Node y Python sobre un **espejo local parcial** cotejado por blobs Git, incluidos 84/84 controles Node, servicio HTTP `http://127.0.0.1:8787/` y Playwright APIRequest GET 200. [A07](../research/ABH30_AUTONOMY_20261029/A07_RESULT.json) · [A08](../research/ABH30_AUTONOMY_20261029/A08_RESULT.json) · [A09](../research/ABH30_AUTONOMY_20261029/A09_RESULT.json). En Chromium real `page.goto` permanece **ERR_BLOCKED_BY_ADMINISTRATOR**; HTTP API no sustituye E2E de navegador. No evitar la política de administración.
- La campaña 20+10 quedó cerrada **29 válidos de alcance acotado, C01 incompleto**. [Informe final](../research/ABH30_AUTONOMY_20261029/FINAL_REPORT.md). Las **2 plazas históricas** de PR37 permanecen sin consumir.
- **Subtareas T028 todavía a ejecutar por un entorno autorizado:** `python ab_atlas/atlas_delta.py check/brief` con repo privado íntegro, `abmap.require_valid(strict=True)`, reporte SHA256 canónico y actualización condicional de `CURRENT.md`; además Playwright Chromium/Firefox con navegación HTTP auténtica y regresiones. Si el entorno sigue bloqueando browser, registrar `BLOCKED_BY_ENVIRONMENT` y no afirmar PASS de ese extremo.

## Continuación del 29/10/2026 — QA independiente posterior a ABH30

**Estado: sigue PENDIENTE para validación íntegra.** Ver [reporte y código reproducibles](../research/T028_INDEPENDENT_QA_20261029/REPORT.md), [prerregistro holdout](../research/T028_INDEPENDENT_QA_20261029/SEED_HOLDOUT_PREREG.json), [resultado de 12.288 semillas](../research/T028_INDEPENDENT_QA_20261029/SEED_HOLDOUT_RESULT.json) y [recibo de preflight](../research/T028_INDEPENDENT_QA_20261029/T028_PREFLIGHT_RECEIPT.json). Esta continuación **no es otro ciclo AB** y no utiliza las dos plazas históricas disponibles.

**Ayuda directa sin Codex:** ejecutar desde un **checkout privado íntegro autorizado**:

```bash
python proyectos/politics-fantasy-league/tareas_codex/T028_NATIVE_PREFLIGHT.py --repo . --out /tmp/T028_NATIVE_PREFLIGHT_RESULT.json
node proyectos/politics-fantasy-league/src/politics_fantasy/pilot_assignment_holdout_qa.mjs
```

La herramienta es de solo lectura sobre el repositorio; inicia y detiene temporalmente el servidor ficticio loopback para pruebas y no toca `CURRENT.md`. Clasifica por separado `PASS_CANONICAL_CHECK`, bloqueo del checker, `PASS_NATIVE_HTTP_API` y estado del navegador. Ejecutar el script **en el checkout destino y adjuntar salida/exit**, ya que el equivalente probado en este chat solo tenía el espejo parcial. El helper subido a GitHub no se ha probado byte a byte en un checkout completo; no considerarlo recibo previo de éxito.

**Evidencia actual:** 15/15 smoke Node + 9/9 HTTP directos PASS, Playwright HTTP API 200, Chromium navegación `ERR_BLOCKED_BY_ADMINISTRATOR`. Atlas 80/80 JSON y 79/79 padres comprobados por API GitHub, **semántica Python canónica y SHA256 del estado NO calculados**. C06 reparado pasa tres ventanas independientes de 4.096 semillas (desviaciones máximas 6,15 %, 6,35 %, 5,27 % contra tolerancia 12 %), control no criptográfico.

**No promover:** `CURRENT.md`, `e2e` de lanzamiento, VSDS, N1/N2/N3 o CT2 por las pruebas anteriores. Buscar un entorno autorizado para la comprobación original y un origen de datos científicamente discriminante, sin eludir restricciones del navegador.
