# Unificación y continuidad de Politics Fantasy · 30/10/2026

## Alcance autorizado

El usuario pidió unificar, orientar progreso futuro y conservar continuidad al cambiar de chat. Confirmó **ambos objetivos, producto e investigación, con progreso separado**. Esta sesión es consolidación, QA y gobernanza; no ejecuta ni solicita una campaña AB nueva.

## Integración real

La rama estable `integration/pfl` se inicia en PR79 `9354e4fe`, integra con merges reales PR75 `22fb79ec`, PR44 `d6db8fcd` y PR45 `aab3ec9c`. Se resolvieron conflictos de CURRENT, cola, grafo y test CLI conservando la API nueva `as-of-instant`, el cwd portable y los controles originales. Se recuperaron correcciones de versiones sintéticas, calendario, validación, pruebas y evidencias de CODEX20; el registro de logros v6 y el release guard de PR44 ya están presentes.

**Errata de la revisión anterior:** se afirmó que PR45 era ancestro de PR73. Esa afirmación era incorrecta: se confundió la selección de FETCH_HEAD al consultar varias referencias. PR45 es una línea paralela. Su ausencia de archivos en PR73 no demuestra que allí se borraran como descendiente. En esta sesión se comprobó la relación con `git merge-base --is-ancestor` por SHA y se integró mediante un merge real. Los artefactos históricos de PR75 se conservan; esta errata evita reutilizar esa conclusión equivocada.

El inventario `BRANCHES.json` clasifica 57 de las 62 cabezas de PR PFL observadas como ancestros incluidos, después de estos merges. Las cinco alternativas divergentes antiguas (PR11–15) se conservan como archivo, no se incorporan a ciegas ni se borran. Ancestría no equivale a aceptación funcional. No se han cerrado 57 PR ni afirmado su publicación en main.

## Atlas y O7

Dos ramas tenían un lote 0081 con el mismo padre 0080 y contenidos diferentes. El primer replay integrado falló por esa bifurcación. Se preservaron los bytes originales CODEX20 (`2d655c52657776a8e7fb8a3d9e4c6251674d40085b7215cca357943cd06324ab`) y se importaron sus 23 operaciones intactas mediante lote 0093 sobre 0092. Original y recibo de equivalencia están en `originals/` y `ATLAS_RECONCILIATION.json`. Los 20 runs son históricos; no se consumen 20 plazas nuevas. No se reescriben los otros lotes.

Replay93 PASS: 63 nodos/81 aristas/310 runs/51 incidencias/488 operaciones, SHA `7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d`. En O7 existían once nombres distintos para los mismos ciclos C20–C30 entre los dos linajes: se documenta un mapa de alias, se conservan los IDs de la continuación actual y se deduplican aristas. O7 queda en 54 nodos y 73 relaciones. Ninguna promoción científica ni gate nuevo.

## Continuidad que cambia con el proyecto

- `START_HERE.md`: enlace estable de lectura, sin copiar contadores en el prompt.
- `PROJECT_STATE.json`: dos líneas, hitos, aceptación, dependencias, última validación y siguiente acción.
- `scripts/project_status.py`: deriva Atlas, saldo del ledger y huella del código; rechaza snapshots y presupuestos desactualizados o completitudes sin evidencia. No sustituye las pruebas del producto ni verifica derechos.
- `HANDOFF.md`: briefing generado, con aviso de hacer fetch/resolver HEAD antes de continuar.
- `NEW_CHAT_PROMPT.md`: texto corto reutilizable que solo señala a los archivos vivos.
- `AGENTS.md` local y política: un hito activo por línea, aparcar bloqueos repetidos y tres rutas de exploración distintas; mantenimiento no se convierte en ciclos. Se sustituye para PFL la solicitud automática de nuevos ciclos. El núcleo científico y las autorizaciones históricas permanecen.

## Progreso y límites

P0 es la integración verificable. Después, P1 añade acceso multiusuario al prototipo ficticio y P2 verifica un recorrido usable de jornada. La investigación tiene su propia R0: escoger una pregunta factible y rival con observación accesible; R1 exige un resultado discriminante, también válido si es negativo. AEA/C37 y T005 quedan aparcados hasta una condición de reapertura concreta. Se preservan las cinco plazas ABH10 y dos históricas sin gastarlas por mantenimiento.

La tensión entre R5 y la obligación O6 de pedir más ciclos es observada en los textos; su contribución causal al estancamiento no está demostrada. Esta política es un piloto local para evaluar descriptivamente continuidad, cierres útiles y repetición de bloqueos. No se afirma que garantice creatividad ni eficacia científica.

## QA del candidato

La ejecución Linux íntegra del commit congelado terminó aprobada; se detallan sus resultados a continuación. Primer Node Windows: 506 PASS, 1 FAIL y 1 SKIP; los dos últimos son creación de symlinks sin privilegios. Se conserva el negativo y se ejecutarán esos controles en Linux sin omitirlos. Los 7 tests específicos de continuidad pasan, incluido rechazo de Atlas obsoleto, presupuesto reiniciado, finalización inventada, evidencia ausente y exceso de hitos activos.

No se ha fusionado main, borrado ramas, publicado datos personales, puntuado políticos reales ni ejecutado CI remota. Los gates siguen 0/6. La autenticación y el recorrido ficticio son trabajo siguiente, no capacidades que esta integración ya implemente.

## Resultado final observado

Checkout íntegro y limpio **`a4a730f3962edc0703ab0be8c3901a309366e7b6`**, Linux Alpine 3.24.3 bajo QEMU 11.1.0, usuario pfl UID1000 y tmpfs, Python 3.14.10, pytest9.0.3, Node24.22.1. Dependencias instaladas antes de cortar la red exterior; loopback activo durante pruebas. VM apagada al terminar. Sin CI remota.

| Comprobación | Resultado | Exit |
| --- | --- | ---: |
| Consistencia del estado vivo | PASS, Atlas y saldo derivados del ledger | 0 |
| Registro de logros | v6, 5/90 simbólicos, sin promover ciencia/gates | 0 |
| Checker y replay Atlas | 93 lotes; SHA7edd32ca6872071bd34de668c96a75f07b686a3cd4f676ca2237d5e1fde2227d | 0 |
| Tests Atlas | 38 PASS +104 subtests PASS, 9,07 s | 0 |
| Suite Python completa PFL | 806 PASS +32 subtests PASS, 59,49 s | 0 |
| Suite completa Node, incluye src y release guard | 508 PASS, 0 fallos/skips, 80,87 s | 0 |

Los siete tests de continuidad forman parte de los 806, no se suman dos veces. Los negativos Windows por symlink se preservan y los controles Linux se ejecutan sin omisión. Se verificaron tamaño y SHA256 de cada archivo contra el manifiesto generado dentro del invitado. Comandos y entorno en `linux/check.sh`, `linux/bootstrap.sh` y `linux/environment.txt`; resultados íntegros y hashes en `linux/MANIFEST.json`.

La [PR80 contra main](https://github.com/GalexY3/Metodologia-AB/pull/80) reúne la propuesta. `integration/pfl` es la entrada operativa estable desde ahora; `main` sigue sin fusionar. P0 queda READY_REVIEW, la continuidad entregada queda DONE, autenticación y flujo ficticio están QUEUED, la elección de pregunta social sigue IN_PROGRESS. No se afirma que el mantenimiento haya ejecutado esa investigación ni resuelto sus datos externos.
