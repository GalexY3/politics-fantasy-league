# Revisión de pendientes y Atlas · 30/10/2026

## Resultado y alcance

La primera revisión del chat solo consultó la rama antigua de 35 lotes y resultó incompleta. `main` está en `968f2b1` (75 lotes, validador roto), mientras que PR45 contiene reparaciones/QA y la descendiente PR73 está en `56b5049` (91 lotes). **No hay un único estado integrado publicado en main.** La relación de ancestros se comprobó con Git: PR45 `aab3ec9c` es ancestro de PR73.

Esta revisión de mantenimiento parte de PR73. No es campaña AB, no adjudica hallazgos, no modifica originales ni gates y no fusiona main.

## Solucionado en esta revisión

- Replay Python canónico de los 91 lotes: exit 0, 63 nodos, 81 aristas, 285 runs, 48 incidencias, 460 operaciones. SHA256 `e67d7fe6a414a273811178e3810b67b67897b5722719fa25d7b1f51a6caf84a4`. Sin modificar seed ni lotes.
- Suite Atlas en Windows Python 3.14: 38 tests PASS. La primera ejecución con `-X utf8` sin propagarlo a hijos emitió excepciones de decodificación en lectores subprocess; se preserva esa limitación del primer intento y los logs versionados corresponden al rerun con `PYTHONUTF8=1` heredable y sin esas excepciones.
- Incorporados al O7 los 11 nodos del anexo C20–C30 y el negativo C18, con rutas de evidencia relativas a su directorio correcto. Una arista exacta duplicada preexistente fue retirada. 48 nodos/66 aristas, sin IDs duplicados ni referencias colgantes. Se conserva el anexo original como historia; la aplicación ocurre solo en esta rama.
- Corregidos dos imports rotos: `tests/test_fictional_pfl_impact_suite.mjs` apuntaba a `src/`, y `tests/test_forecastbench_raw_revision_guard.mjs` al directorio de tests; ambos módulos están en `src/politics_fantasy/`. Reproducción de los dos `ERR_MODULE_NOT_FOUND` preservada en `node-host.out`; después **49/49 PASS** sin cambiar expectativas. El primer Node global Windows dio 290 PASS/4 FAIL: dos imports y dos casos con falta de privilegios de symlink; no se omitieron esos controles.
- Recuperado el runner portable `scripts/run_node_tests.mjs` desde PR45, eliminado en el árbol posterior: descubre tests tanto en `tests` como en `src/politics_fantasy`. Esta rama vuelve a incluir el punto de entrada.
- Cola README/BACKLOG reconciliada: informes parciales ausentes del árbol se enlazan al commit inmutable PR45; no se descartan sus avances ni se atribuyen al último código. La eliminación de otras evidencias/código de PR45 requiere revisión de integración independiente, no restauración masiva a ciegas.

## Principales bloqueos y confianza de resolución futura

Escala subjetiva de capacidad de completar el bloqueo con las herramientas/evidencia disponibles: 0 imposible por esta vía; 1 baja; 2 limitada; 3 media; 4 alta; 5 muy alta. **No es una probabilidad, CT2 ni garantía.** Puntúa el resultado completo, no solo escribir código o un protocolo.

| Prioridad | Bloqueo real | Qué falta para cerrarlo | Confianza /5 |
| --- | --- | --- | ---: |
| P0 | Integración de ramas y seguimiento | Revisar PR45→PR73 y PR44 divergente, preservar evidencia eliminada, QA del árbol elegido, revisión y fusión humana | 4 |
| P0 | Gate `data_registry`: registro jurídico de partidos | Registro/certificado institucional por entidad y vigencia; candidaturas, siglas o agregados no lo sustituyen (T005) | 1 |
| P0 | Gate `identity`: identidad longitudinal | IDs multifuente, intervalos de mandato y adjudicación independiente de homónimos; evitar joins por nombre/asiento | 2 |
| P0 | Gate `events`: eventos atribuibles y temporales | Identidad válida, originales/versiones y primera disponibilidad verificable; significado oficial del literal `NO VOTAN` | 2 |
| P1 | Gate `authentication` | Autenticación, sesiones y autorización multiusuario, persistencia y pruebas de aislamiento | 5 |
| P1 | Gate `e2e` | Flujo íntegro autorizado fuente→cuarentena→identidad→evento→resultado; un smoke sintético no lo acredita | 3 |
| P1 | Gate `deployment` | Entorno concreto, TLS, gestión de secretos, operación/recuperación y QA integral; depende de los gates anteriores | 3 |
| P0 si hay personas reales | Derechos/finalidad y revisión jurídica | Alcance de tratamiento, licencias por recurso y valoración profesional; Codex puede preparar matriz y medidas, no otorgar derechos | 1 |
| P1 investigación | Evidencia social/causal independiente | Datos utilizables con asignación/exposición/oportunidades reales, o estudio humano autorizado y ejecutado; controles sintéticos no lo sustituyen | 1 |
| P1 reproducción | Completar T016–T024 y otras tareas parciales | Originales por emisor, resolver 403/snapshots/firma según expediente y ejecutar análisis reproducible; los informes PR45 identifican pendientes particulares | 3 |

Los seis gates anteriores proceden del replay real en `ATLAS91.json`, no de interpretar el porcentaje V4. Siguen 0/6. CT2 identidad histórica 29 y CT2 ciencia prospectiva 20 corresponden a ramas/preguntas diferentes; la revisión no los combina ni promueve. V4 36,90 % contractual y VSDS históricos sin cambio.

## Orden de continuación

1. Integrar y verificar la rama técnica elegida, junto con la evidencia documental: es el bloqueo que evita repetir tareas ya hechas.
2. Para continuar el prototipo ficticio: autenticación y pruebas multiusuario tienen alta resolubilidad sin depender de originales políticos.
3. Para políticos/datos reales: T005, identidad, semántica y temporalidad requieren evidencia externa; no se pueden dar por resueltos con tests nuevos.
4. Para investigación sociológica: definir el contraste humano y sus datos/permiso, separar mejoras técnicas de resultados científicos.

No se han intentado nuevas búsquedas repetitivas de originales ni se ha dado por conseguida autorización jurídica. Esos requisitos permanecen abiertos, descritos con un siguiente paso concreto.
