# PFL-CODEX-T028 · resultado técnico nativo y verificado (29/10/2026)

**Estado: NÚCLEO TÉCNICO VERIFICADO, CON LIMITACIONES CIENTÍFICAS Y DE LANZAMIENTO.** La ejecución se hizo directamente desde ChatGPT mediante **dos trabajos específicos y breves de GitHub Actions** en un **checkout privado autorizado**; **Codex no fue invocado**. Al registrar estos resultados, la rama base era la PR #41, HEAD `d8c6f59f391fb16de1fa157a809b12de87cfaa58`. La PR sucesora y las evidencias son draft y no se han fusionado en `main`.

| Subtarea | Estado y ejecución real | Límites |
|---|---|---|
| Replay oficial Atlas `check` | **PASS 80/80 lotes**, 63 nodos, SHA256 **`e41270a7897817f626611208f4ec483318950af59d8d27f78c925d83a93eb54f`** | Solo semántica original de Atlas, no descubrimiento científico |
| CLI oficial `brief --limit 8` | **PASS**; mismo SHA256, 81 relaciones, `head_batch=0080`, scope `PFL-V1-20261026-r3`, readiness false | 0/6 release gates |
| Chromium real vía Playwright sobre HTTP | **PASS 21/21 controles** en `http://127.0.0.1:8787/` | Piloto de 4 condiciones, NO E2E global del proyecto |
| CSS/JS/CSP/privacidad ficticia | **PASS** en pruebas seleccionadas: 4 brazos, 12 radios etiquetados, tutoriales, reset, módulo, sin solicitudes externas, POST=405, secreto=404, sin cookies/almacenamiento, móvil sin overflow | No certificación WCAG completa, pentest, autenticación multiusuario ni despliegue |
| Fuentes individuales para prueba científica | **STOP_R5** | Falta una fuente legal con oportunidad visible antes de responder y asignación de feedback |

## A. Python Atlas original — ejecución en checkout íntegro

- Job real: [GitHub Actions 40805714464](https://github.com/GalexY3/Metodologia-AB/actions/runs/40805714464), job `123224069258`, commit original `85f5513f801f0c34a03b2d73cbf95d5ae3e5c5d1`, **conclusión SUCCESS**.
- Workflow limitado: [`.github/workflows/pfl-t028-atlas-native-20261029.yml`](../../../.github/workflows/pfl-t028-atlas-native-20261029.yml). **Un job, timeout 3 min, ninguna instalación de dependencias**, sin lanzar la CI integral de PFL.
- Comandos realmente ejecutados:

```bash
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
python ab_atlas/atlas_delta.py brief --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates --limit 8
```

- Líneas de log reales: `CHECK_STDOUT: OK 80 lotes 63 nodos SHA256 e41270a7897817f626611208f4ec483318950af59d8d27f78c925d83a93eb54f`; `CHECK_STDERR:` vacío; `PFL_T028_CANONICAL_PASS` con 80 lotes, 63 nodos, 81 aristas, mismo SHA, readiness false.
- El código original aplica `abmap.require_valid(strict=True)` al seed y después de cada lote, con transacción por batch. Esto **sí sustituye el anterior control documental de padres 79/79**, que por sí solo no validaba el estado.
- El programa Python no exige fechas monótonas: **0079 declara 01:00:00Z y 0080 00:26:37.468Z el 29/10/2026**. Se preserva el material original y se documenta el defecto cronológico, sin modificar historia.
- La cabecera de [`ab_atlas/CURRENT.md`](../ab_atlas/CURRENT.md) se actualizó **después** del PASS nativo y contiene el SHA canónico. Los 80 deltas y seed permanecen idénticos. La rama no cambia `main`.
- Recibo JSON: [`NATIVE_ATLAS_CHECK_RECEIPT.json`](../research/T028_DIRECT_ATLAS_20261029/NATIVE_ATLAS_CHECK_RECEIPT.json).

## B. Navegador real HTTP autorizado y controles negativos

- Job: [GitHub Actions 40806035386](https://github.com/GalexY3/Metodologia-AB/actions/runs/40806035386), job `123225098835`, commit original `f9a9f8f06e119005d92e796968fd1a1f806bf8f9`, **conclusión SUCCESS**.
- Workflow [`.github/workflows/pfl-t028-browser-native-20261029.yml`](../../../.github/workflows/pfl-t028-browser-native-20261029.yml). **Un job, timeout 4 min**, paquete Python Playwright 1.56.0 y Google Chrome preinstalado en el runner, **sin descarga/instalación de navegador ni suites costosas**.
- Se inició `node pilot_local/server.mjs` escuchando en `127.0.0.1:8787`; Playwright Chromium usó **`page.goto()` HTTP real** y el módulo `/materials.mjs` cargó. Esto no es una página DOM `about:blank` ni una petición API de Playwright.
- Log `PFL_T028_BROWSER_HTTP_PASS 21 of 21`. Los 21 checks incluyen HTTP 200, cuatro `fieldset`, doce radios etiquetados, misma batería de preguntas en las cuatro condiciones, selector y mensajes T×L esperados, progreso/reinicio, JS sin excepciones, GET sin otros orígenes, CSP, `no-store`, `nosniff`, POST 405, clave privada 404, cero cookies o localStorage y viewport móvil 375 px sin scroll horizontal.
- Las solicitudes observadas de la página fueron cuatro y del mismo origen; `page_errors=[]`. Se apagó el servidor al cerrar.
- El contenedor local de ChatGPT **continúa** devolviendo `ERR_BLOCKED_BY_ADMINISTRATOR`; no se alteró ni eludió esa política. El trabajo se ejecutó en un entorno **distinto y autorizado**.
- No se generaron ni se alegan capturas de pantalla. No se simuló conformidad completa WCAG ni se efectuó prueba multiusuario o producción.
- Recibo JSON: [`NATIVE_BROWSER_E2E_RECEIPT.json`](../research/T028_DIRECT_ATLAS_20261029/NATIVE_BROWSER_E2E_RECEIPT.json).

## C. Antecedentes nativos, auditorías y reparaciones previas

La campaña [ABH30](../research/ABH30_AUTONOMY_20261029/FINAL_REPORT.md) ya había probado un espejo local de Git blobs originales (84/84 controles Node y 15/15 smoke HTTP) y posteriormente tres ventanas inéditas de 4.096 semillas del asignador ficticio, todas dentro de los umbrales prerregistrados. **Estas cifras históricas no fueron reejecutadas en los dos nuevos jobs**. El parche C06 inicial corrigió una desviación de distribución de asignaciones para semillas contiguas; es un dispositivo **no criptográfico**, apto solo para rehearsal ficticio. [PR #41](https://github.com/GalexY3/Metodologia-AB/pull/41) y recibos conservan los negativos.

En la presente continuación se descargaron **legalmente mediante el conector conectado a GitHub** y se inspeccionaron los 80 JSON originales, con 438 operaciones, y se ejecutó un **shadow replay JS independiente** de invariantes de grafo (63 nodos, 81 relaciones, 263 runs, 48 complaints, 6 gates) más cuatro controles negativos de fuente modificada **solo en memoria**. [`SHADOW_REPLAY_RESULT.json`](../research/T028_DIRECT_ATLAS_20261029/SHADOW_REPLAY_RESULT.json) no se confunde con el PASS posterior del Python original.

## D. Investigación científica, permisos y novedad: R5

La nueva auditoría [`EXTERNAL_PRIOR_ART_AND_DATA_GATE.md`](../research/T028_DIRECT_ATLAS_20261029/EXTERNAL_PRIOR_ART_AND_DATA_GATE.md) compara Hudja/Roberson/Rosokha 2025 (ranking público puede reducir esfuerzo en ciertas competiciones de horizonte finito), Lemus/Marshall 2021 y 2025 (efecto medio positivo condicionado al tipo de competición e incentivos de premios), ForecastBench (Brier ajustado por dificultad) y Bo/Budescu/Lewis/Tetlock/Mellers 2017 (IRT ajusta dificultad/discriminación y considera autoselección no aleatoria de preguntas en Good Judgment Project). La pregunta general sobre «mejor puntuación bajo oportunidades distintas» **ya tiene antecedentes sólidos**.

Candidatos: IARPA/Good Judgment Project publicó pronósticos humanos en Dataverse; **no se han recuperado microdatos con licencia concreta, hashes, esquema de exposición observable y base de tratamiento verificados**. Metaculus exige autenticación y permisos específicos para exportar y restringe usos de API, IA y comercial. No hay extracción de usuarios, scraping o afirmaciones causales.

**Resultado científico:** 0 nuevos descubrimientos N1/N2/N3, **CT2 prospectiva 22/100 ordinal sin cambios**. El producto sigue con **0/6 gates críticos**, VSDS 1/3 y V4 36,90 % contractual. La validación del piloto ficticio **no satisface el E2E de la plataforma completa** ni autoriza publicación de políticos o datos humanos.

## E. Contabilidad AB, seguridad, cierre

La campaña ABH30 previa sigue cerrada 29 A–J válidos acotados y 1 incompleto, según sus recibos. **Esta continuación es QA/previa documental, no un ciclo nuevo.** Conservar **2 plazas antiguas AB-H autorizadas sin ejecutar**. Sin ChatRelay, sin fusión a `main`, sin CI costosa (dos trabajos puntuales limitados a 3 y 4 minutos), sin reclutamiento, sin scoring real, sin despliegue público y sin afirmar aprobación ética.

**Dictamen:** `T028 CORE_TECHNICAL_VERIFIED_WITH_LIMITS`. Las dos dependencias P0 originales —Atlas Python completo y navegación Chromium HTTP real— **se han satisfecho con registros reproducibles**. El siguiente bloqueo ya no es Codex: es **obtener datos legalmente accesibles de exposición/decisión individual o un protocolo experimental con supervisión ética** para una prueba científica discriminante. No gastar ciclos por volver a reproducir el mismo resultado.
