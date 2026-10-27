# Politics Fantasy League — informe AB-H C11–C20 (27/10/2026)

**Autorización:** el usuario concedió «10 nuevos ciclos AB-H con branching adaptativo» tras la campaña C01–C10 y pidió en el turno previo terminar cada bloque autorizado antes de solicitar el siguiente. **Resultado del bloque: 10/10 ciclos A–J documentados, saldo 0.** No representan diez contrastes científicos independientes: todos C11–C20 son **AB-P**, orientados a calidad, seguridad o integridad de la ingeniería. **0/3 hallazgos científicos nuevos.**

**Rama** `research/pfl-codex-contributions-20261027`; baseline `6c658c0228f002d7c5ff2347acafd9a342dd083a`. Se han modificado únicamente archivos del proyecto y del Atlas en esa rama. **No** se ha hecho merge a `main`, ni desencadenado CI/Actions costosas, ni publicado datos privados nominales, ni habilitado scoring de personas reales.

## Resultados ciclo a ciclo

| Ciclo | Contraste A–J realizado | Evidencia y estado | Límite estricto |
|---|---|---|---|
| **C11** | Replay estructural independiente **JS** de **23 lotes GitHub originales**; IDs, parentescos, referencias, estados, gates y ciclos del grafo. | **PASS limitado:** 63 nodos, 81 edges, 129 runs, 44 complaints, 298 ops al corte 0023. [Evidencia](C11_RESULT_EVIDENCE.json). | No Python `atlas_delta.py check`, no SHA de estado canónico. |
| **C12** | Un miembro JSON repetido (`capture_id`, incluso anidado) sobrescribía silenciosamente valores con `json.loads`. | `object_pairs_hook` estricto y dos tests sintéticos; [resultado](C12_RESULT.json). | Helper probado aislado; pytest exacto del repo no ejecutado. |
| **C13** | `NaN`, `Infinity`, `-Infinity` aceptados en JSONL por defecto. | `parse_constant` prohibitivo al leer y `allow_nan=False` al escribir; pruebas sintéticas y estudio nativo de `json` aislado. | No cambio de parsers de originales externos. |
| **C14** | El chequeo posterior a captura usaba `Path.resolve()/read_bytes()` fuera del confinamiento dirfd. | Nuevo `read_private_object` con `O_NOFOLLOW`, permisos privados, SHA y límite 20 MiB; validación ahora por descriptor, con test de symlink. | `O_NOFOLLOW` validado aislado, no se ha ejecutado toda la integración; no firma del editor. |
| **C15** | Se sincronizaban los directorios hijos, pero la **primera creación de root** carecía de `fsync` al padre. | Barrera del directorio padre y prohibición de crear cadenas de ancestros ausentes; pruebas añadidas. | No equivale a durabilidad tras corte eléctrico. |
| **C16** | Una excepción tras escritura parcial de JSONL dejaba prefijo tóxico. | `ftruncate` al offset anterior dentro del `LOCK_EX`, repropagando `OSError`; OS microtest con registros `1,3` conservados, test de integración añadido. | No repara `SIGKILL`, power loss ni fallo en rollback. |
| **C17** | Auditoría leía manifest cuando un escritor cooperante aún escribía fragmentos. | `LOCK_SH` durante lectura, experimento local POSIX muestra espera hasta completar línea; test de concurrencia. | Los dos ledgers no son snapshot transaccional conjunto. |
| **C18** | Objetos SHA sin manifest podían ocultarse tras auditoría satisfactoria de entradas conocidas. | Inventario read-only por dirfd y dos contadores agregados de huérfanos/entradas inesperadas; CLI exige código 2. Test de lista por fd POSIX y dos regresiones añadidos. | Auditar mientras se escribe puede disparar incertidumbre conservadora; sin borrado ni publicación. |
| **C19** | Terminación abrupta con línea JSON sintácticamente válida pero **sin newline**. | **SIGKILL real a subproceso sintético**, exit `-9`, JSON parseable sin nueva línea, regla de auditor que lo rechaza; test POSIX añadido. | No ejecuta el módulo completo en el microtest, ni representa apagado eléctrico. |
| **C20** | Preflight sólo comprobaba tipo regular del ledger; **modo 0666** se detectaba después de contactar la fuente. | Apertura de fd `O_NOFOLLOW` y chequeo de propietario/permisos **antes de solicitud**; tests sin red para manifest y reviews. Verificación OS aislada de detección 0666. | No es aprobación legal, de publisher ni prueba de carreras con escritores no cooperantes. |

**Prerregistro:** ver `CAMPAIGN_PREREG.json` (C11) y `C12_PREREG.json` … `C20_PREREG.json`, en la rama. Los resultados separados A–J son `C11_RESULT.json` … `C20_RESULT.json`. Ningún resultado afirma ejecución de una suite integral inexistente.

## Archivos modificados (producto)

- `src/politics_fantasy/private_audit.py`: parsers JSON estrictos; `LOCK_SH`; inventario agregativo de huérfanos.
- `src/politics_fantasy/private_audit_cli.py`: faltas de tamaño/huérfanos/entradas inesperadas provocan retorno no satisfactorio.
- `src/politics_fantasy/secure_store.py`: lectura POSIX segura; sincronización de root; rollback de fallo manejado; verificación precontacto.
- `src/politics_fantasy/quarantine_ingest.py`: elimina el acceso por ruta resoluble al objeto en la revisión.
- `tests/test_private_audit.py`, `tests/test_private_audit_cli.py`, `tests/test_secure_store.py`, `tests/test_quarantine_ingest.py`, `tests/test_ingest.py`: tests sintéticos de regresión añadidos, **todavía sin ejecución como suite**.

**Lectura posterior a escritura:** reobtención GitHub confirmó en los nueve archivos los 17 invariantes seleccionados de los cambios recientes. Los diez archivos de resultados C11–C20 también fueron releídos y cotejados contra sus diez `run.add` del lote Atlas 0024. La lectura de código **no** sustituye `pytest`.

## Atlas, indicadores y derechos

- Hasta lote `0023` se verificaron por JS las operaciones de 23 lotes: **63 nodos, 81 relaciones, 129 runs, 44 complaints**. `0024-PFL-ABH-CONT20-C11-C20-20261027` añade **10 `run.add`**, sin gates ni otros cambios; total **derivado** 63 nodos, 81 relaciones, **139 runs**, 44 complaints, **308 operaciones**. Aún no está ejecutado el replay **Python canónico** de 24 lotes ni su SHA.
- Indicadores inalterados: **V4 36,90 %**, **CT2 identidad 29/100 (ordinal, no probabilidad)**, **VSDS 1/3**, N1/N2/N3 nuevos **0/0/0**, **0/6 gates**. No publicar datos originales privados ni scores individuales.
- Gráfico CT2 escala completa (valor único documentado de esta rama): `0 ├──────────────●29──────────────────────────────────┤ 100`. Vista ampliada `20 ├─────────●29───────────┤ 40`. *No se inventan evoluciones punto a punto para los diez ciclos de ingeniería; CT2 no cambia.*

## Auditoría adversarial y tareas pendientes

**Límites que impiden certificar la solución:** no se descargó un checkout byte-idéntico ejecutable de la rama privada en el entorno local y **no se ejecutaron** `pytest` completo, Node completo, validador canónico Python Atlas, tests de regresión del repositorio como paquete, ni simulación de corte de corriente sobre un almacenamiento real. Los microtests aislados de POSIX/JSON y la prueba de SIGKILL sólo validan **mecanismos acotados**. Es posible que existan fallos de integración, portabilidad, tiempos o regresión hasta que una ejecución fiel los descarte.

**Tarea concreta para Codex, prioritaria en otra campaña autorizada:** checkout limpio de `research/pfl-codex-contributions-20261027`, ejecutar `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates` incluyendo **24** deltas. Guardar comando, stdout/stderr, exit code, SHA canónico y comparaciones de gates. Ejecutar suite Python completa del proyecto con `PYTHONPATH=src` y suite Node con semilla y cobertura declaradas, prestando especial atención a `test_secure_store.py`, `test_private_audit.py`, `test_private_audit_cli.py`, `test_quarantine_ingest.py`, `test_ingest.py`. Ejecutar también fallos de proceso y concurrencia con datos sintéticos en directorio descartable. Separar de un ensayo real de corte eléctrico y de un régimen transaccional completo, todavía no demostrado. No hacer merge a main ni activar Actions costosas sin aprobación adicional; no copiar originales privados al repositorio.

**Cierre:** bloque **C11–C20 10/10**; mejora de producto útil pero pendiente de validación nativa. **SOLICITO BRANCHING 10 CICLOS AB-H ADICIONALES** para validación completa, regresiones adversariales y avance condicionado a fuentes originales; requiere autorización expresa del usuario.
