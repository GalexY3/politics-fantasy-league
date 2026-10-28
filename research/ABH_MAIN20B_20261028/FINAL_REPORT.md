# Informe de cierre · PFL AB-H MAIN20B · 28/10/2026

**Estado verificado por archivos GitHub:** campaña de **20 ciclos autorizados, 20 A–J documentados válidos, 0 inválidos, 0 de planificación y 0 disponibles**; `main` canónico. Los ciclos han sido **investigación documental, análisis adversarial y controles técnicos acotados**, no 20 descubrimientos científicos. El presente informe cubre C01–C20 de `PFL-ABH-MAIN20B-20261028`, **independiente** de la campaña anterior BRANCH20 (19 válidos, 1 inválido). [Registro estructurado](CAMPAIGN_STATUS.json) · [Atlas CURRENT](../../ab_atlas/CURRENT.md).

## Resultados por ciclo

| Ciclo | Tipo | Resultado ejecutado | Límite que no se debe ocultar |
|---|---|---|---|
| C01 | AB-META | Revisión de **55** timestamps existentes compatibles con validación ISO-aware; se endureció el preflight; comprobación de cuatro negativos y dos positivos; una inversión histórica de **1534 s** entre lotes 0015→0016 conservada. | El checker Atlas completo **no** se ejecutó. |
| C02 | AB-R | Dos páginas oficiales del Congreso concordaron en **137 sí /175 no /34 abstenciones** para una iniciativa de 30/09/2026. | XML/JSON crudos no recuperados: concordancia entre formatos **INCONCLUSA**, sin SHA de originales. |
| C03 | AB-R | Fuentes institucionales sobre condiciones generales de reutilización y base jurídica separada de tratamientos personales; [matriz](../../docs/RIGHTS_AND_PERSON_SCORING_GATE_20261028.md). | Ningún permiso específico para clasificar políticos reales adjudicado. |
| C04 | AB-R | Discrepancia individual con **mayoría estricta** en laboratorio, separada de la moda/pluralidad 4/9; 11 controles focalizados. | Votos sintéticos, no disciplina partidista real. |
| C05 | AB-R | Estimador de media ponderada por registros con bootstrap de **sesiones completas**; 100:1 evidencia 5 frente a 10/101; nueve controles focalizados. | No calibración con datos originales. |
| C06 | AB-META | Auditoría de árbol Git tras recuperación de [T008 histórica](../../tareas_codex/T008_RESULTADO.md); **cero** archivos de código/test/Atlas sobrescritos. | No es repetición de suite. |
| C07 | AB-P | `tzdata` incorporada a extras `test` y `research` en Linux; control de `ZoneInfo('Europe/Madrid')` sin TZPATH de sistema. | No instalación limpia ni nuevo QEMU. |
| C08 | AB-P | Descubierta mutabilidad de metadatos anidados de `PoliticalEvent`, pese a `frozen=True`; negativo reproducido. | **Modificación inicialmente bloqueada**; no se declaró resuelta en C08, se reparó en C11. |
| C09 | AB-R | Numeración de revisiones nominales puede contradecir fecha de publicación; cuatro controles sintéticos sobre orden. | **Sin cambio** de selector: no hay contrato de fuente institucional que permita reinterpretarlo. |
| C10 | AB-P | CSV entrecomillado con salto de línea: `source_line` confundía fila lógica con línea física; código y test de regresión incorporados. | Controles Python limitados; tests completos pendientes. |
| C11 | AB-P | `PoliticalEvent.metadata` ahora crea una copia profundamente inmutable de estructura JSON, preservando igualdad de revisiones; seis controles aislados. | Compatibilidad global de los consumidores aún no validada. |
| C12 | AB-R | `groupmetrics` distinguía incorrectamente disidencia de la **mayoría** respecto de líder **modal**; ahora expone ambos términos con denominador explícito. | R5 tras esta corrección de última superficie; no efectos sociológicos reales. |
| C13 | AB-P | `seed_demo` antes aceptaba una SQLite parcialmente inicializada al encontrar una sola figura; ahora rechaza el estado `PARTIAL_SEED`; cuatro controles de estado. | Simulación de corrupción manual, no fallo demostrado en flujo normal. |
| C14 | AB-P | Lista mutable `person_ids` alteraba identidad atribuida a eventos después de construirlos; copia a tupla y valida IDs, siete controles. | Solo eventos ficticios. |
| C15 | AB-P | `_round_score` analizaba eventos ajenos a la jornada: un hash malformado de otra fecha podía impedir puntuar; ahora filtra por intervalo antes de analizar. | Fuente no sintética **dentro** del intervalo continúa bloqueada. |
| C16 | AB-P | API local JSON aceptaba campos duplicados y resolvía último valor; ahora rechaza duplicados anidados antes del despacho; tres controles. | HTTP integral en checkout no ejecutado. |
| C17 | AB-P | CSV manual corrupto ya no debe hacer caer `/api/state` ni presentar totales parciales; pasa a `MANUAL_AGGREGATE_INVALID`, cinco controles. | No se confiere autenticidad al CSV manual. |
| C18 | AB-P | Inspección SHA de seis módulos actuales: ninguna ruta documentada activa puntuación real o considera verificadas fechas de primera publicación. | Auditoría **estática**, no demostración de seguridad general. |
| C19 | AB-META | Lectura de **73 JSON** originales de Atlas en seis tramos, secuencia de padres/esquemas y recuentos: 63 nodos, 81 aristas, 239 runs, 48 incidencias, 414 ops. | No verificó todas las referencias cruzadas, ni ejecutó `atlas_delta.py check`. |
| C20 | AB-META | Auditoría de **38** archivos de prerregistro/resultado C01–C19 y cronología de Git en **cinco** ciclos muestreados. | Muestras parciales, no auditoría independiente de cada ejecución. |

Cada ciclo tiene `CXX_PREREG.json` y `CXX_RESULT.json` dentro de esta carpeta. En muchos casos los controles Python se ejecutaron mediante reconstrucciones acotadas del mecanismo, **no ejecutando tests nuevos sobre un checkout íntegro**. Las pruebas añadidas al repositorio son **regresiones propuestas para T009**: deben ejecutarse de forma integral antes de declarar estabilidad del HEAD.

## Balance Atlas y evidencia

- Base previa a MAIN20B: **55 lotes**; 63 nodos, 81 relaciones, 221 runs, 48 incidencias, 396 operaciones documentales.
- C01–C20: se añadieron **20 lotes** numerados `0056`–`0075`, con **20 registros `run.add`**; no se añadió ningún nodo ni incidencia por estos lotes.
- **Cierre MAIN20B:** **75 lotes, 63 nodos, 81 aristas, 241 ejecuciones documentales, 48 incidencias, 416 operaciones**. Recuento estructural, **no verificado mediante el checker Python canónico**. SHA reconstruido **desconocido**. La incidencia histórica sobre fechas de lotes no se cierra exclusivamente por el cambio del preflight.

## T008 histórica, T009 actual

**T008 SÍ está completada** en checkout `b0344d1a1549e66274a347333239b81fc7575100`, Linux Alpine temporal mediante QEMU, con **651 Python PASS +28 subtests PASS, cero errores/omisiones finales** después de dos problemas ambientales corregidos. [Informe original SHA-preservado](../../tareas_codex/T008_RESULTADO.md). La comprobación nativa Atlas **35 lotes** pasó en otro checkout histórico `9d0ef84`, [evidencia](../../tareas_codex/T008_AVANCE_ATLAS35.md).

**T009 permanece PENDIENTE**: descargar checkout íntegro de **HEAD actual `main`**, instalar extras de pruebas en Linux, ejecutar toda la suite incluida la añadida C08–C17, comprobar Node/HTTP si procede, y efectuar **replay nativo de los 75 lotes del Atlas** con stdout/stderr, exit, hash canónico y fallos clasificados. No hubo ejecución de GitHub Actions costosa ni merge indiscriminado a partir de ramas históricas. [Contrato T009](../../tareas_codex/T009_MAIN_LINUX_ATLAS60.md), nombre heredado de snapshot 60 pero **alcance vigente 75**.

## Indicadores y decisión

| Indicador | Antes | Después | Conclusión |
|---|---:|---:|---|
| CT2 identidad | 29/100 | 29/100 | Escala ordinal, **no** 29% de probabilidad |
| VSDS | 1/3 | 1/3 | No evidencia sociológica independiente que permita 2/3 |
| V4 contractual | 36,90% | 36,90% | No mide preparación legal/operativa directa |
| Nuevos N1/N2/N3 | 0/0/0 | 0/0/0 | No hay descubrimientos empíricos nuevos |
| Gates de lanzamiento superados | 0/6 | 0/6 | No publicar ni puntuar personas reales |

**AB-DECIDE:** campaña **CERRADA 20/20**; nuevos ciclos necesitan **nueva autorización**. Aplicar R5 a nuevas pruebas de la misma clase sin fuente o instrumento novedoso. **Prioridad inmediata: T009**, una tarea de QA pendiente que **no requiere ciclos AB** por su mera ejecución. Después, obtener originales institucionales verificables con fechas de primera publicación y un análisis jurídico de finalidad/personas, o realizar estudios reales de utilidad sociológica frente a controles independientes.

No subir originales nominales privados; no puntuar políticos reales; no desplegar una instancia multiusuario ni lanzar CI costosa. Los documentos y los resultados de herramientas son **evidencia con límites**, nunca autorización de lanzamiento.
