# PFL · ABH30-C09 — Auditoría de revisiones brutas de fuente pública

**29/10/2026.** Rama `research/pfl-abh30-c09-raw-revision-guard-20261029`, sucesora de PR #59. **AB-P técnico, D1**, nunca ensayo humano ni contrastación científica externa. Este ciclo aprovecha un hallazgo adversarial de C08: el número de filas brutas de resoluciones puede disminuir aunque el subconjunto binario aceptado permanezca monótono.

## Ejecución y evidencia congeladas

Contrato A–J y SHA congelados **antes de la ejecución** en commit [464b56c](https://github.com/GalexY3/Metodologia-AB/commit/464b56c0f78416701b015dff4467912bd7cb97b5). El código y las pruebas se guardaron previamente en commits `2a275334` / `e8504ef5`. Las copias locales verificadas tenían los mismos Git blob SHA que los originales del repositorio y SHA256 congelados en el [preregistro](C09_PREREG_AJ_SHA.json). Se ejecutó **Node v22.16.0**, `node --test test_forecastbench_raw_revision_guard.mjs`: **19/19 PASS**, 0 fallos, exit 0; [recibo](C09_RUN_RECEIPT.json).

La utilidad concreta es comparar toda la población de filas de cada archivo `resolutions` por clave compuesta `(source,id)`, sin limitarse a las resoluciones binarias admitidas por el motor de oportunidades. Se identifican **altas, bajas, mutaciones y retenciones**, incluso cuando una eliminación se compensa con un alta y el recuento agregado permanece idéntico. Se detectan modificaciones de `resolved_to` y de metadatos que no alteran Y. La comparación canoniza el orden de propiedades de objetos para evitar falsos positivos por serialización. Una baja o modificación activa una marca de revisión manual; no presume que la fuente original sea append-only.

## Contrato A–J ejecutado

**A — Pregunta.** ¿Puede detectarse con una auditoría pura y reutilizable toda pérdida o mutación de filas de la fuente pública entre versiones, algo que la simple inspección de recuentos o el filtro de elegibilidad del C08 no cubre por definición? Unidad técnica: fila de evento público por ruta/versionado, no persona.

**B — Hipótesis y rival.** H1: el detector descubre altas compensatorias, eliminaciones y mutaciones de campos tanto de resultado como de metadatos. H0/rival: comparar recuentos y el subconjunto binario del C08 basta y el componente no añade una comprobación diferenciable. Criterios negativos congelados: cambio de fila sin detección, duplicados aceptados, ruptura de orden temporal, cruce de cohortes o fuga de identificadores.

**C — Diseño.** Diecinueve fixtures públicos **sintéticos** con invariancias y adversarios: preservación de clave compuesta, repetición de claves, sustitución de igual tamaño, cambios de Y y de fecha, orden de campos, cadena multiversión, validación UTC y contención de propiedades peligrosas. No hay muestreo de pronósticos humanos ni inferencia causal.

**D — Código congelado.** `src/politics_fantasy/forecastbench_raw_revision_guard.mjs` Git blob `2e1ed7f5e23bbad79c81013505882830907cb258`, SHA256 `21882420a2713ee8490d819d9936d33a5123f6869d4b97e3c244098908653ee9`. Tests `tests/test_forecastbench_raw_revision_guard.mjs` Git blob `b9edf86d4a0609b9e4bb542fe85221857460a12d`, SHA256 `7abf599d3f8cbe6b9312484d1944cd3b8039c7ee926c48172e473165bf2a34ed`.

**E — Resultado observado.** 19 de 19 tests realmente ejecutados en Node y aprobados tras congelación. Se demuestra comportamiento del instrumento para fixtures; no se cuantifican correcciones de la fuente original ni capacidad científica.

**F — Auditoría adversarial.** Se rechazan fuentes incompletas, duplicados, claves inválidas, horas UTC no canónicas, inversión temporal, blobs no distintos, cruce entre cohortes, propiedades objeto peligrosas. La salida registra **solo conteos agregados y metadatos Git**, no las claves de eventos. No comprueba los hashes originales por sí mismo y explícitamente informa `original_git_bytes_authenticated_here:false`.

**G — Comparador.** El control simple de número de filas no detecta sustituciones de cardinalidad constante; C08 rastrea Y admisibles, no cada modificación bruta. Esta comparación lógica se prueba con fixtures, **no con las 19 versiones originales**. El cambio de API y su QA no justifican una reivindicación de originalidad científica.

**H — Priors.** Conserva PF-BR01–48, especialmente el contraejemplo de C08 sobre filas originales no monótonas. No se añaden priors empíricos ni hallazgos N1–N3 por un test informático.

**I — Dictamen.** **AB-P válido, limitado a verificación funcional con fixtures y Node nativo.** CT2 científica PFL **20/100 ordinal**, N1/N2/N3 nuevos **0**, lanzamiento **0/6**. Ni test de clon limpio integral ni reproducción positiva original 21-blob en disco. No se han tratado datos personales, puntuado políticos ni introducido automatizaciones de publicación.

**J — Decisión.** Se consume **un solo ciclo nuevo C09**, por el instrumento y su batería de adversarios; **9/30** nuevos consumidos, **21/30** nuevos disponibles, **dos plazas históricas separadas con STOP_R5**. Mantener rama draft, sin merge a `main`, sin ChatRelay ni CI costosa. El siguiente contraste de mayor valor sigue siendo aplicar el auditor a archivos originales autenticados y comprobar qué filas exactas cambiaron sin reproducir contenido personal, o abrir una nueva fuente de personas únicamente tras autorización legal/ética independiente. No gastar más ciclos solo en más casos de una misma suite.
