# T028 — T027 continuación: reproducción canónica Atlas 0078–0080 y navegador con HTTP real

**Estado: NEEDS_EXECUTOR · no ejecutada · no cuenta como ciclo AB nuevo.**
Base: rama `research/pfl-abh5-browser-atlas-independent-20261029`, verificar HEAD de la PR draft sucesora antes de actuar. No CI costosa, no ChatRelay, no fusionar main, no reclutar personas ni puntuar políticos reales.

## 1. Atlas: requisito central aún abierto
En entorno **con checkout Git autenticado**, leer `AGENTS.md`, `ab_atlas/atlas_delta.py`, `ab_atlas/abmap.py`, `proyectos/politics-fantasy-league/ab_atlas/seed.json` y los 79 lotes 0001–0079 más el lote 0080 si existe al ejecutar. El conector de chat comprobó que los **79 JSON históricos se pueden parsear** y sus `parent_batch` son consecutivos, pero **no ejecutó el replay nativo Python ni el validador `abmap.require_valid(strict=True)`**.

Ejecutar:

```bash
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
python ab_atlas/atlas_delta.py brief --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates --limit 8
```

Registrar HEAD, Python, exit codes, stdout/stderr, batch final, hash SHA-256 del estado, `runs`, nodos, `release_gates`, IDs nuevos 0078–0080 y cualquier `complaint`. Comprobar si el lote **0079 tenía `at=2026-10-29T01:00:00Z` que puede no corresponder al momento cronológico de creación**: no reescribir eventos históricos; documentar anomalía y criterio de timestamp.
Solo **si el validador pasa**, actualizar `ab_atlas/CURRENT.md` canónico a estado con hash real, manteniendo el histórico. Si falla, preservar error y marcar `BLOCKED`.

## 2. Navegador: diferencia entre DOM aislado y HTTP integrado
La sesión anterior logró Chromium 144.0.7559.96 sobre `about:blank` + `page.set_content()`, con fuentes originales DOM cargadas **inline exclusivamente en el test** (18/18 comprobaciones y capturas locales). Sin embargo, el entorno prohibía navegación Chromium a `http://127.0.0.1`, `file://` y `data:` por un control de administrador. **No es bug confirmado del servidor PFL**.
En el checkout local real, arrancar `node proyectos/politics-fantasy-league/pilot_local/server.mjs` y verificar acceso HTTP con Chromium/Firefox, importación real de `/materials.mjs`, CSP, teclado, responsive móvil, ausencia de solicitudes remotas, de `localStorage` y de rutas de claves/POST. Guardar **capturas, versiones y log de peticiones**. No declarar PASS de HTTP browser por el anterior DOM aislado.

## 3. Ciencia: puerta de datos independientes
Antes de calcular cualquier medida nueva de incentivos, obtener **derechos, licencia/permiso, bytes, hash, variables y marca temporal** de un paquete de replicación comparable. Contrastarlo con Frongillo et al. (2025) correlación de eventos, Monroe et al. (2025) hedging, Lemus y Marshall (2021), Lemus (2025) premios contingentes, y Marshall (2019) información política reputacional. Si no hay microdatos legalmente reutilizables de diseño comparable, **STOP_R5** sin hacer otro simulador.

## Aceptación
Emitir `T028_RESULT.json` con PASS/FAIL/SKIP real, hash de commits, fuente y entorno; actualizar Atlas y priors únicamente por cambios ejecutados. No confundir un resultado de browser o checker con causalidad científica, ni reusar el cupo AB sin contraste aprobado.
