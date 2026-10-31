# PFL SYSTEM20 · cuarta ronda: contadores editoriales, inventario temporal y puerta de admisión

**Fecha:** 31 de octubre de 2026. **Estado:** documentación oficial y producto local con QA; NO un experimento AB-H confirmatorio. Programa teórico: reproducción y autorregulación del sistema político español, con acoplamientos económicos, jurídicos, empresariales y mediáticos sustantivos; no se ha seleccionado TFM definitivo.

## Hallazgos materiales auditados

Se reconciliaron Git local y remoto sobre el commit previo fb22f3dbd1c275536733f6e3be94953bc95e1ce5. PR #3, #4, #5, #6 y #7 permanecían abiertas como borradores apilados; no se modificó ni fusionó main. Atlas99 seguía con 99 lotes, 362 runs y SHA canónica bc4c7b094df4cb95f073a3d41f18c5c362bea80ca6b3ce275ed07593571c46e9, sin nuevas puertas científicas superadas.

Los cuatro originales CSV de Canarias fueron verificados nuevamente desde bytes fuera de Git: 2023/X/PPL 1 fila, 2024/XI/PE 686, 2025/XI/PE 543 y 2026/XI/PE 524. SHA-256 del JSONL primero: 7ed31c97be3928e306749972f5b3d746ca0c20a961818674ff0626e9c6679463; SHA-256 del incremental 2025: 88041ac88a6dcb6e8b5c20ca89ae07fcdb6f95548a209042b4d6dd06aaec2bcc. Se cotejaron **1.754 filas y 1.754 claves fuente-local únicas**, sin outcome o disponibilidad histórica introducidos en el resultado. Las 1.211 filas originales siguen intactas y separadas de las 543 incrementales.

**Nuevo cotejo de denominador por vista editorial:** el Árbol de iniciativas del Parlamento de Canarias muestra los mismos contadores PE 2024=686, 2025=543 y 2026=524 para legislatura XI; total **1.753 preguntas escritas** en los tres estratos. No se incluye la PPL de 2023 como si fuese PE. Se comprobaron los tres CSV locales contra esos números, sin claves duplicadas entre años, sin fechas o identificadores faltantes y sin fechas de creación ajenas al año del recurso. [Manifiesto de cotejo](../../data/source_manifests/parcan_editorial_crossview_20261031.json).

**Límite:** Árbol y CSV pueden proceder del mismo almacén institucional y tener los mismos filtros. Los tres HTML se leyeron desde un visor público, **sin bytes originales, cabeceras HTTP ni SHA**, porque no se adjudicaron todas las condiciones del acceso directo. Las URLs exactas están en el manifiesto; el recibo primario de la auditoría permanece fuera de Git, SHA b06c3324d27b1a4afdafd74f5a81ee56f04a5fe68bc3c71c855a33fd60a13054. Un resultado de búsqueda anterior mencionaba 415 para PE/2026, en contraste con 524 en la vista reciente; no se considera un vintage autenticado ni un aumento probado de 109 iniciativas. El cotejo no certifica exhaustividad sustantiva, desenlaces o primeras publicaciones.

**Rastro de trámites:** fichas oficiales canarias con URLs por expediente muestran clases documentales de entrada, corrección, calificación de Mesa, publicación en BOPC y actuaciones posteriores. Esta tipología es utilizable para diseñar un adaptador de eventos, **no** para afirmar que se ha descargado una población completa de transiciones o que las fechas de BOPC equivalen a la primera disponibilidad pública. Ausencia de respuesta visible no equivale a fracaso.

## Vía nacional recuperada sin recurrir al endpoint bloqueado

Se encontraron dos memorias institucionales retrospectivas del Congreso con conteos de propuestas legislativas que incluyen más trayectorias que las normas aprobadas:

| Memoria del Congreso | Proposiciones de ley: total editorial | Proyectos de ley: total editorial | Fuente oficial |
| --- | ---: | ---: | --- |
| IX legislatura | 356 | 147 | https://app.congreso.es/est_memoriaIX/resource?id=03%2F17.pdf |
| X legislatura | 278 | 163 | https://app.congreso.es/est_memoriaX/resource?id=03%2F16.pdf |

Se inspeccionó la primera página de ambas memorias desde el visor de fuentes público; HEAD a las dos rutas concretas respondió HTTP 200 con tipo application/pdf. **No se archivaron PDF originales ni hay SHA**: el aviso general de reutilización de www.congreso.es y la marca de Publicaciones del Congreso en app.congreso.es no bastaron para adjudicar sin duda el derecho de conservar/republicar documentos completos. Por tanto, los números son **totales editoriales retrospectivos**, no un dataset per-expediente o un marco longitudinal bitemporal reproducido.

El BOCG Serie D n.º 648 de 28/10/2011 incorpora subpoblaciones de iniciativas caducadas, pendientes de calificación y trasladadas al cierre de la IX legislatura. Es un complemento que evita ignorar fracasos, pero tampoco una lista de todas las iniciativas nacidas durante la legislatura. El propio aviso del Congreso advierte de la autenticidad de la edición impresa para boletines anteriores al 01/08/2012. No se repitió el endpoint de iniciativas anteriormente bloqueado por HTTP 403, ni se eludieron condiciones del Senado, SIIP o de otros portales.

## Mejora técnica de temporalidad y observación

Se observó un problema de fuga de información temporal en el endpoint local de Canarias: un sello de auditoría con segundos enteros no acredita que su contenido ya estuviese disponible al **inicio** de ese segundo. El corte se endureció: la primera instantánea resulta visible con seguridad desde 05:19:19 UTC, la segunda desde 05:34:52 UTC, y la nueva agregación posterior solo desde su segundo de disponibilidad conservador. Un recibo futuro malformado ya no invalida ni revela las cohortes de un corte anterior; una derivada mensual manipulada queda en cuarentena independientemente de los metadatos anuales acreditados.

Se implementó una reconciliación **offline** sobre los dos JSONL originales fijados por SHA: rechaza IDs repetidos entre archivos, datos de outcome indebidamente admitidos, fechas imposibles, cambios de año/legislatura/tipo, esquema ajeno, hashes inesperados y datos fuente-local dentro de Git. Produce solo un agregado de **34 combinaciones positivas de distribución y mes declarado de creación**. No se rellenan meses sin observaciones como ceros. El agregado se conserva en [parcan_source_local_months_20261031.json](../../data/source_manifests/parcan_source_local_months_20261031.json), SHA-256 c86e3d8f6d889bede76f2c215e61e9bea880c3fabc3db40c97317ccd6fc5927f.

La API local **/api/spanish-process-cohorts?as_of=** conserva las fotografías anteriores y ofrece el agregado mensual únicamente después de su auditoría y verificación SHA. El observatorio de interfaz muestra los meses solo en una tabla desplegable de **observaciones de metadatos**, claramente diferenciada de un historial de primera publicación o rendimiento institucional. Ni el grafo oficial_temporal_links.py ni la capa de scoring han recibido procesos reales, cambios de categoría o asociaciones no probadas.

## Revisión de agentes y pruebas de no-contaminación

El agente documental trabajó exclusivamente en el scratch de Congreso/Canarias y entregó un recibo con SHA, un script de cotejo congelado y **6 pruebas sintéticas PASS**; el agente temporal trabajó en scratch independiente y entregó un verificador PDDL para la instantánea previa de tres distribuciones, con **48 tests PASS**. Los hashes de recibos y código se comprobaron desde la sesión principal; no se copiaron versiones redundantes de official_temporal_links.py.

El verificador temporal del scratch es **alternativa técnica no integrada** porque el observatorio principal ya tiene la auditoría de tres y cuatro distribuciones y controles más conservadores de la precisión del segundo; incorporar otro servicio duplicado empeoraría el contrato. Sus pruebas sobre bloqueo de joins Congreso–BOE, personas y usos indebidos siguen disponibles como material adversarial reutilizable, no como evidencia causal.

**QA ejecutado localmente tras los cambios de esta ronda (Windows, Python 3.14/Node):** 134 pruebas Python focalizadas PASS de fuentes, as-of, almacenes y normalización; 10 pruebas Node de paneles, links y seguridad PASS, además de `node --check` PASS; 5 pruebas independientes del instrumento de captura 2025 PASS. En scratch, se reprodujeron también 6/6 adversariales del cotejo editorial y 48/48 del gate temporal PDDL aislado. Es QA de infraestructura, **no** experimentos AB-R/AB-P ni equivalente a la suite completa Linux. No se activó CI remota costosa ni Linux en esta ronda. Los dos campos del CSV con posibles resultados, SITUACION y TIPO_FINALIZACION, fueron decodificados estructuralmente por el lector CSV, pero **no inspeccionados, agregados ni exportados sustantivamente**.

## Dictamen metodológico y programa de continuación

La primera etapa gana **dos evidencias adicionales**: cotejo de cardinalidades PE en segunda vista editorial Canarias y un par de denominadores agregados nacionales que incluyen procedimientos no exitosos. No se satisfacen por completo los requisitos de **población individual, estados, transiciones, desenlaces competitivos, censura y first_public_at histórico** para estimar persistencia o feedback. La incertidumbre editorial y el carácter de fotografías actuales persisten.

La nueva [propuesta de contrato ontológico](../../docs/CONTRATO_ONTOLOGICO_SISTEMICO_TEMPORAL_PFL_20261031.md) distingue operaciones comunicativas, decisiones, organizaciones, fuentes, tiempos y selección documental, y compara rutas de Luhmann, Easton y Deutsch sin asimilarlas. El programa AB-H sigue con M1 (historia/reproducción interna), M2 (acoplamientos) y M3 (sesgo de observación), rivales cronológicos e institucionales, y negativas como resultado admisible. No se selecciona pregunta final del TFM.

**SYSTEM20:** 20 autorizados / 0 ciclos AB-R o AB-P válidos / 0 inválidos / 20 disponibles. Atlas99, CT2 y puertas de lanzamiento permanecen sin promoción. El siguiente gate científico es una enumeración fuente-local **por expediente** vinculada a actas y boletines con transiciones fechadas y estados explícitos, o una pregunta descriptiva transversal formalmente separada. Cualquier outcome nuevo exige A–J, código y SHA remoto congelados *antes* de observarlo; no se reutilizan controles exploratorios post hoc como contraste confirmatorio.
