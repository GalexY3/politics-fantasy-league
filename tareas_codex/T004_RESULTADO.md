# T004 · Revisión local de seguridad: ejecución parcial con fallos de plataforma

**Resultado: COMPLETADA_CON_FALLOS.** Se comprobaron las fronteras HTTP locales y la política aislada de redirecciones con fixtures ficticios. No se ha validado el almacén privado ni la recuperación ante caída en Windows: están diseñados para primitivas POSIX y no había WSL instalado. No se ha demostrado explotación de una ruta pública ni seguridad para Internet; no se cambian los gates.

## Entorno y alcance

- HEAD inicial `6e359a89e74f06927e51ca4dc8a9ea1714e37acd`, rama `research/pfl-codex-contributions-20261027`; Python **3.12.14**, Node **v24.16.0**, Windows. Cwd `C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league`.
- Revisión guiada por `security-best-practices`, referencia `javascript-general-web-frontend-security.md`. La skill no incluye referencia específica para el servidor Python `http.server` de biblioteca estándar; las comprobaciones HTTP quedan acotadas a los ensayos descritos.
- Solo clientes `127.0.0.1`, temporales y bytes ficticios. Los tests de redirección aislados llaman el control en memoria; no contactan instituciones ni demuestran por sí solos una captura completa.

## Pruebas y negativo preservado

Con `PYTHONPATH=src` y `PYTHONDONTWRITEBYTECODE=1`, se ejecutó la suite específica solicitada:

```text
python -m pytest -q -rs tests/test_ingest.py tests/test_quarantine_ingest.py tests/test_ingest_full_local_e2e.py tests/test_ingest_http_boundary.py tests/test_ingest_redirect_security.py tests/test_private_audit.py tests/test_private_audit_cli.py tests/test_secure_store.py tests/test_private_store_process_boundaries.py tests/test_simulation_http.py tests/test_product.py tests/test_local_http_guards.py
exit 1
56 failed, 53 passed, 27 skipped, 10 subtests passed in 21.14s
```

La traza completa se conservó localmente en `%TEMP%\pfl-T004-security-tests.txt`, SHA-256 `7f3f292cd11183538554f356fea747084ea0deaf3b437d0c7b488b928c2ac9f4`. El almacén falla de forma explícita con `SECURE_STORE_UNSUPPORTED_PLATFORM` en Windows (`src/politics_fantasy/secure_store.py:19-24`); esto impide a múltiples tests llegar a sus comprobaciones posteriores. Dos casos intentan crear enlaces simbólicos que esta cuenta Windows no puede crear, y las pruebas SIGKILL/dirfd POSIX se omitieron. No se presenta el resultado como suite superada ni se presume que todo fallo tenga causa única. `wsl.exe --list --quiet` devolvió que WSL no está instalado.

Se añadieron pruebas autocontenidas que no sustituyen a la suite anterior:

```text
python -m pytest -q tests/test_local_http_guards.py tests/test_redirect_guard_isolated.py
exit 0
18 passed in 4.79s
```

Salida local `%TEMP%\pfl-T004-isolated-tests.txt`, SHA-256 `a7e3f43017ffe2f8752fba1809672633418b73738ffa8984412b2bdcd8c3953f`. En la matriz HTTP, ocho casos rechazados incluyen Host y Origin ajenos, Content-Type incorrecto, longitud ausente, inválida, cero, negativa y superior al máximo; el callback sintético comprueba que no se ejecuta la acción. Un caso válido llega al callback. En la política aislada, se rechazaron siete destinos inseguros (otro host, sufijo engañoso, otra fuente oficial, HTTP, userinfo, puerto y loopback), se aceptó el host vinculado y se verificó el máximo de saltos.

## Riesgos y límites

1. **Alto para cualquier despliegue público; conocido y fuera del alcance de esta demo.** `server.py:128` enlaza a `127.0.0.1`; la cabecera del módulo y el aviso de arranque declaran que no hay autenticación ni protección CSRF multiusuario. Los controles de Host/Origin y JSON (`server.py:49,89`) y el CSP (`server.py:44`) no convierten el servicio en apto para Internet. No se probó explotación remota.
2. **Medio, limitación comprobada en esta plataforma.** La captura y auditoría del almacén privado no son operativas en Windows; cierran antes de abrir una fuente. Tests de POSIX, `flock`, señales y escritura multiproceso (`tests/test_secure_store.py`, `tests/test_private_store_process_boundaries.py`) siguen pendientes en un sistema POSIX adecuado. No se ha validado tolerancia a pérdida de energía, escritores no cooperantes ni atomicidad entre dos ficheros de registro. El código prevé rechazo de JSONL incompleto y recuento de objetos huérfanos (`private_audit.py:53,78,96`), pero aquí no se ha demostrado su comportamiento POSIX.
3. **Bajo, condicionado a manipulación de datos locales; reparado para los dos paneles BOE.** El escape HTML no valida el esquema de `source_url`. Tras registrar [el contraste](T004_ENLACES_PREREG.md), `node --test tests/test_ui_source_links.mjs` dio inicialmente **1 fallo y 1 aprobado**, demostrando que un valor ficticio `javascript:alert(1)` producía un enlace. Ahora los dos paneles admiten solamente HTTPS con host exacto BOE y sin credenciales ni puerto no estándar; otros valores se muestran sin enlace. Tras la reparación, `node --test tests/test_ui_source_links.mjs tests/test_ui_vote_bars.mjs` dio **5 aprobados**, exit 0; `node --check src/politics_fantasy/web/app.js` exit 0. Esta prueba no demuestra explotación ni autentica el contenido de fuentes remotas. La salida inicial está en `%TEMP%\pfl-tasks-20261028\T004_source_links_initial.txt`.

No se han cambiado controles del servidor, TLS, gates ni decisiones científicas. Próximo paso: ejecutar la suite y los casos de caída en POSIX aislado, documentar allí sus resultados y decidir por separado un diseño seguro si se desea admitir almacenamiento privado en Windows.
