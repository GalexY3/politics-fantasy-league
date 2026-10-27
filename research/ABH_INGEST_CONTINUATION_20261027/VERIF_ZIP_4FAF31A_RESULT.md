# Verificación nativa del checkout adjunto `4faf31a` — 27/10/2026

**Objeto:** cerrar los bloqueos de ejecución que quedaron abiertos después de IC01–IC03 sin abrir ni contar otro ciclo AB-H confirmatorio. Es una **verificación post hoc de software**, no una nueva campaña científica. Rama: `research/pfl-codex-contributions-20261027`; commit de entrada **`4faf31a30111ef980a43409dbe87de8c7609b29f`**. Antes de escribir se contrastó en GitHub `4faf31a...research/pfl-codex-contributions-20261027`: estado **identical, ahead 0, behind 0**. No se creó otra rama ni se fusionó `main`.

**Paquete suministrado:** `Politics-Fantasy-ChatGPT-4faf31a.zip`; SHA-256 `34979452ba718f823df60fb6f7cba3d3ff053511233c2155bb37da8617bf3d39`, 2.719.919 bytes, **821 entradas** y 6.719.918 bytes descomprimidos; `zipfile.testzip() = None`, extraído con validación de rutas y enlaces. Es snapshot de archivos versionados, **sin `.git` ni originales privados**. Entorno local Python 3.13.5, pytest 9.0.2, Node.js (ejecución native), Chromium de sistema.

## Ejecución real y verificable

Desde la raíz del ZIP extraído:

| Acción / comando | Resultado |
| --- | --- |
| `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates` | **PASS**: `OK 18 lotes 60 nodos SHA256 532ff19bc2073dca8e906fe9be12ee76642ef00caf37ab07c7fde73609c07f78`. Este es un resultado **canónico Python**, no un replay JS. |
| `python -m pytest -q ab_atlas/tests` | **34 passed** |
| Desde `proyectos/politics-fantasy-league`: `PYTHONPATH=src python -m pytest -q --disable-warnings --maxfail=1` | **421 passed, 28 subtests passed**, 0 failures, 15,15 s |
| `node --test tests/*.mjs` | **110 passed**, 0 failures |
| `PYTHONPATH=src python -m pytest -vv tests/test_ingest_http_boundary.py tests/test_ingest_redirect_security.py tests/test_quarantine_ingest.py tests/test_source_stage_http.py` | **20 passed y 14 subtests passed**. Incluye la prueba **HTTP local real** con `ThreadingHTTPServer`. |

Las 20 pruebas HTTP/ingesta **están contenidas en las 421 anteriores**; no sumarlas como 441 pruebas únicas. Los 34 casos de Atlas son una suite separada; subtests no equivalen automáticamente a nuevos casos de test.

### Alcance HTTP acreditado

`test_ingest_http_boundary.py` se **ejecutó** y pasó sobre el servidor local completo:

- `GET /api/source-stages` 200 con catálogo en cuarentena, sin `first_public_at` ni scoring real.
- `GET /api/health` 200, `SYNTHETIC_DEMO`.
- `POST /api/ingest`, `/api/source-import`, `/api/capture` → **404**; `GET /api/ingest` y `/api/quarantine` → **404**.
- Host `attacker.invalid` → **403**.
- No crea `manifest.jsonl` ni `quarantine_reviews.jsonl` desde esas rutas.

Esta es una **verificación positiva de la ausencia de una ingesta HTTP**. El pipeline `quarantine_ingest.py` sigue siendo local, sintético y separado del servidor. La prueba no autoriza a exponer un endpoint de ingesta, ni acredita fuentes externas, derechos, identidad o `first_public_at`.

## Smoke visual Chromium: fallo de infraestructura y contrato obsoleto

Se detectó que `tests/run_browser_smoke.py` aún esperaba **`revision=3` y 36,4 %** pese a que el estado vigente es **V4, 36,9 %**. Se actualizó **solo el contrato de QA** a V4 y el nombre del artefacto visual; se añadió una ruta opcional `PF_CHROMIUM_EXECUTABLE` para que el Chromium de sistema pueda emplearse sin alterar el runner de CI, que usa los binarios normales de Playwright. Archivo nuevo en GitHub: blob SHA **`327be2cc7d213c7e12e3f65fa9e881164632a0e8`**, 8.128 bytes, comprobado con SHA de blob Git sobre la copia local. `python -m py_compile` **PASS**.

**No atribuir PASS al navegador:** primera ejecución no encontró el browser Playwright empaquetado (`BrowserType.launch: Executable doesn't exist`); al habilitar `/usr/bin/chromium`, el navegador arrancó, pero `page.goto(http://127.0.0.1:18787/)` devolvió **`net::ERR_BLOCKED_BY_ADMINISTRATOR`** por política del entorno. Se detuvo la prueba sin eludir esa restricción. Los checks HTTP con `http.client` sí ejecutaron contra loopback. El navegador y sus expectativas V4 deben probarse en Windows/CI autorizado antes de certificar la UI.

## Separación de límites y métricas

- **No ejecutar GitHub Actions** en esta verificación; no instalar ni pedir secretos.
- **No publicar originales nominativos privados**, ni extraer contenido del ZIP de fuentes parlamentarias al repositorio.
- **No** certificar `NO VOTAN` semánticamente: se trata solo de normalización operativa del XML pendiente de fundamento institucional.
- **No** afirmar E2E captura HTTPS externa→servidor→validación→jugador; solo pruebas de fichero local y HTTP de rutas que no capturan.
- Campañas **AB-H45 (45/45)**, **CDX (9)**, **IC01–IC03 (3)** quedan separadas; esta verificación **no suma IC04 ni aumenta CT2**.
- **V4 36,90 %**, **CT2 identidad 29/100**, **VSDS 1/3**, **0/6 gates** siguen invariantes. Un smoke actualizado no es evidencia de superación de release gate.

**Decisión R5:** la ejecución del checkout sí produjo evidencia nueva suficiente para cerrar el bloqueo de Python/Atlas/HTTP; el smoke browser requiere otro runtime autorizado. No seguir creando fixtures similares por inercia. Prioridades futuras: prueba Chromium/CI sin restricciones sobre el último commit, análisis de autorización/egress para cualquier endpoint de ingesta real, documentación institucional de `NO VOTAN` y respaldo de las fuentes originales antes de puntuación real.
