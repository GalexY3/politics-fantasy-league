# T004 · Revisión de seguridad local del servidor y la ingesta

**Prioridad P1 · Estado PENDIENTE · Ejecución Codex no realizada.** [Volver al índice](README.md).

## Alcance y riesgos

El servidor `src/politics_fantasy/server.py` se anuncia **solo para loopback** y dice expresamente que no hay autenticación de sesiones ni protección CSRF para hosting multiusuario. `source_eligibility.py` sigue en `release_ready=false` y `real_person_scoring=false`. La infraestructura de ingesta y almacén recibió controles POSIX `flock`, `fsync` y auditoría de cuarentena en campañas previas, pero **no fue validada como servicio público seguro**.

La tarea consiste en comprobar **controles existentes en un entorno local desechable**, no en desplegar un servicio público ni probar una red externa.

## Prerrequisitos

T002 (baseline de tests), checkout exacto y entorno aislado. Trabajar con datos puramente sintéticos y directorios `tmp_path`. Nunca descargar originales nominales ni abrir el servidor en interfaces públicas; no conectar a dominios institucionales en los tests.

## Controles a ejecutar

- Tests originales de `test_ingest.py`, `test_quarantine_ingest.py`, `test_ingest_full_local_e2e.py`, `test_ingest_http_boundary.py`, `test_ingest_redirect_security.py`, `test_private_audit.py`, `test_private_audit_cli.py`, `test_secure_store.py` y `test_private_store_process_boundaries.py` si su plataforma lo admite.
- Pruebas locales de `Host`, `Origin`, `Content-Type`, `Content-Length`, redirección y límites de tamaño, desde un cliente de pruebas y **solo** `127.0.0.1`. Verificar que host/origen no autorizados retornan error sin ejecutar una acción.
- Detectar lagunas de autenticación/multiusuario como **gates pendientes**, no corregirlas forzando el lanzamiento. Examinar si existen rutas que escriban/expongan evidencias nominales sin pasar por los controles.
- Comprobar que fallos transitorios (SIGKILL, parcial JSONL, objeto huérfano) se detectan y no se convierten en “reparado” automáticamente; documentar límites de crash/power-loss y escritores no cooperantes.

## Criterios de aceptación

Registro reproducible de comandos/exit codes/fixtures y cada propiedad probada. **Separar** errores de entorno, hallazgos de código, vulnerabilidades solo plausibles y casos efectivamente explotados en la demo sintética. Si aparece fallo reproducible, conservar primer resultado rojo, corregir mínima superficie y repetir tests. No exigir pentest externo como si fuera prueba local; no llamar “seguro para Internet” a un PASS.

**Entregable:** `T004_RESULTADO.md`, lista de riesgos con severidad y fuente exacta, pruebas versionadas si proceden. Los seis gates permanecen pendientes salvo análisis y autorización independientes.
