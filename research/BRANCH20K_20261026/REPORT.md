# Politics Fantasy League — BR20K, 20 ciclos AB con métrica de avance versionable

**Fecha:** 26/10/2026. **Autorización:** 20 ciclos AB 3.2.1, BRANCHING. **Estado:** 20 fichas A–J completadas; sin datos originales nacionales de partidos/personas adquiridos en esta campaña; el avance científico no queda confirmado por los tests de producto.

## Producto principal: métrica PFL-V1-20261026

[Scope congelado, 36 hitos](../../product/progress_scope_v1.json), [snapshot calculado](../../product/progress_snapshot_v1_20261026.json), [metodología íntegra](../../docs/PROGRESO_Y_ALCANCE_v1.md).

La métrica es el **grado de madurez de tareas relativo al alcance v1**, NO porcentaje de horas restantes, probabilidad de éxito o predicción de fecha de lanzamiento. Son 9 sublíneas, peso total 100%; cada una integra cuatro hitos específicos con ID, evidencia, justificación y nivel 0–5. Niveles normalizados 0, 10%, 40%, 60%, 85%, 100%, según inexistente/diseñado/implementado/probado local/validado con campo delimitado/operativo. Estos niveles y los pesos son **adjudicaciones revisables**, no mediciones estadísticas. No hacer pasar cantidad de ciclos por trabajo completado.

| Sublínea | Peso | Madurez | Contribución global |
|---|---:|---:|---:|
| Fuentes y datos | 18 | 38,75 % | 6,975 pp |
| Identidades, coaliciones e historial | 12 | 40,00 % | 4,800 pp |
| Acontecimientos políticos | 10 | 32,50 % | 3,250 pp |
| Investigación, predicción y evaluación | 14 | 27,50 % | 3,850 pp |
| Mecánicas y motor del juego | 16 | 45,00 % | 7,200 pp |
| Interfaz y experiencia | 10 | 27,50 % | 2,750 pp |
| Seguridad, privacidad y licencias | 8 | 20,00 % | 1,600 pp |
| Pruebas y reproducibilidad | 8 | 32,50 % | 2,600 pp |
| Operación, pilotos y lanzamiento | 4 | 17,50 % | 0,700 pp |
| **Global** | **100** | — | **33,725 %** |

Este porcentaje describe un roadmap propuesto: exige registro comprobable de organizaciones políticas españolas y actores públicos con y sin escaños, datos de acontecimientos institucionales y extraparlamentarios, fantasy real basado en observables admisibles, pruebas científicas y despliegue seguro, sin intentar registrar toda interacción política privada de España. Fuera de alcance: perfiles individuales de votantes, inferir ideología o mérito, aplicación nativa móvil en V1.

**Estado de lanzamiento: NOT_PUBLIC_RELEASE_READY.** Seis condiciones quedan bloqueadas: registro original de partidos y candidaturas; identidad jurídica de personas reales; eventos/persona verificados; autenticación y autorización; tests nativos E2E; despliegue público. No derivar readiness de 33,725 %. No puntuar personas reales.

## Dinámica de scope y metrología

El motor [progress_model.mjs](../../src/politics_fantasy/progress_model.mjs) permite validar niveles, evidencia, pesos, versiones, calcular sublíneas y descomponer variación como efecto de trabajo y de cambio de scope. Hay un [runner offline](../../scripts/progress_report.mjs), y se congeló un [ejemplo de segunda versión NO ADOPTADA](../../product/progress_scope_v2_EXAMPLE_NOT_ADOPTED.json) y su [descomposición](../../product/progress_scope_change_example.json).

**Experimento contrafáctico de alcance:** añadir un objetivo de cobertura municipal nacional exhaustiva, nivel 0, sin trabajar más, reduce 33,725 a **32,330 %**: efecto trabajo **0**, efecto de alcance **−1,395 puntos**. La V1 **no ha sido reemplazada**; este ejemplo muestra cómo reinterpretar una caída de porcentaje sin declarar retroceso técnico. La separación es secuencial (trabajo primero) y depende de esa convención, no es una identificación causal única.

## Integración en producto

El adaptador [progress_api.py](../../src/politics_fantasy/progress_api.py) calcula las mismas ponderaciones en Python, lee el manifesto v1 con validación y bloqueo frente a estructuras no admisibles. [server.py](../../src/politics_fantasy/server.py) incorpora GET /api/progress de solo lectura. La [interfaz](../../src/politics_fantasy/web/app.js) y [navegación](../../src/politics_fantasy/web/index.html) añaden una pestaña con barras de avance, 9 sublíneas, 36 hitos y enlaces individuales a evidencia, estado de bloqueo para lanzamiento y explicación de revisiones.

**Pruebas efectuadas:** 20 tests del [motor JS](../../tests/test_progress_model.mjs) ejecutados en funciones puras V8, 20 PASS; parser de JS del frontend PASS; existencia de **36/36 rutas de evidencia** comprobada contra el árbol de GitHub. Se publicó además [test_progress_api.py](../../tests/test_progress_api.py) y [test_progress_http.py](../../tests/test_progress_http.py), con integración en [workflow CI](https://github.com/GalexY3/Metodologia-AB/blob/main/.github/workflows/politics-fantasy-evidence.yml).

**Pruebas no ejecutadas / pendientes:** no hay confirmación de Node test sobre checkout limpio; no se ejecutó adaptador Python ni HTTP del servidor en esta sesión; no hay E2E real de navegador; ninguna ejecución exitosa de GitHub Actions quedó acreditada. No anunciar el nuevo dashboard como despliegue validado.

## Gobierno de la campaña, las 20 unidades AB

[PREREG.json](PREREG.json) distingue que los contratos C01–C06 de este bloque son **retrospectivos**, pues ya existían el manifiesto inicial y parte del motor antes de congelarlos. No venderlo como prueba ex ante. [RESULTS.json](RESULTS.json) registra acciones/obstáculos individualizados, y [LEDGER.json](LEDGER.json) contiene A–J con adversarios, replicación ausente, actualización y decisión.

| Rama | Ciclos | Resultado |
|---|---|---|
| C01–C06 alcance y cálculo | 6 | Baseline+20 assertions del índice y escenario de nueva versión |
| C07–C08 acceso fuentes RPP/roster Congreso | 2 | STOP_R5: catálogos y JSON observables; no originales capturados y normalizados |
| C09–C12 identidad/eventos/procedencia | 4 | 2 STOP_R5 para población real; reglas de integridad y temporalidad existentes, runtime limitado |
| C13–C14 metodología y demo | 2 | Plan TFM y QA antiguo verificados documentalmente; no campo nuevo |
| C15–C19 API/UI/QA/scope | 5 | Código publicado, parser V8, 20/20 checks puros; Python/Node/HTTP nativos pendientes |
| C20 integración/ledger | 1 | Cierre AB y actualización de priors, sin reivindicación científica |

Se incorporó [documento de fuente oficial legible](ORIGINAL_SOURCE_DISCOVERY.md): el enlace JSON de diputados en activo de julio de 2026 ofrece campos de alta y grupo, pero eso **no da un registro bitemporal ni una copia original autenticada en el almacén**. No se conservaron biografías personales ni se construyeron perfiles.

**Distinción epistémica:** 12 contrastes locales superados, 4 cierres R5, 3 entregas/ejecuciones nativas todavía no verificadas y un cierre de gobernanza (resultados individuales). Todos son ciclos A–J concluidos; no hay 20 estudios estadísticos de España.

## Priors y decisión

Nuevos PF-K01–PF-K06 en [PRIORS_DELTA.md](PRIORS_DELTA.md), con contraevidencia y falsadores. Se integran al índice acumulativo sin alterar PF-P/MG/H/I/J. Mantener **VSDS-1/3**, CT2 multiactor 20/100 y predictiva parlamentaria 24/100, cada una ordinal y diferente; nuevas N1/N2/N3 = 0.

**AB-DECIDE: CLOSE_BR20K / REPAIR_NATIVE_QA_AND_PRIMARY_SOURCE_ACCESS.** Los 20 ciclos están concluidos. El indicador de avance no debe aumentar por documentación de más ciclos si ningún hito incorpora evidencia nueva suficiente. El siguiente bloque de investigación no necesita centrarse en crear otra métrica: debe levantar los bloqueos de fuentes originales, identidad y ejecución nativa, revisando el scope solo mediante nueva versión explícita.

### Propuesta para el siguiente bloque (no autorizado)

**Solicitar 12 ciclos BRANCHING** acotados a dos hitos verificables: 1) capturar al menos un recurso original auténtico y reutilizable con checksum y esquema limpio (RPP/elecciones/roster), 2) ejecutar en entorno real toda la suite Node/Python/HTTP y reparar fallos observados, además de una revisión crítica de acceso al producto. Si los originales continúan sin acceso, agotar esa rama por R5, sin repetir trabajo documental.

**SOLICITO BRANCHING 12 CICLOS**
