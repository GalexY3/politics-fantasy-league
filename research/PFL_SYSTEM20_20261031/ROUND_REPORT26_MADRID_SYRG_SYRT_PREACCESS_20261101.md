# R26 · Madrid SYRG/SYRT: bifurcación de registros recibidos y terminados

**1/11/2026. Descubrimiento documental nuevo, NONCYCLE, STOP_LOCAL_R5.** Inspección de metadatos HTML públicos del portal del Ayuntamiento de Madrid, sin descargar ficheros, consultar expedientes/personas, aceptar cookies/términos ni contactar a su responsable. Se conserva como **hipótesis de fuente**; no licencia adquirida, cohorte empírica admitida, caso de éxito ni nuevo ciclo AB.

## Identidad y testigos públicos consultables

- Catálogo principal: https://datos.madrid.es/dataset/300044-0-syrg-syrt/information. El buscador documental describía hasta el 31/10/2026 el conjunto «Sugerencias y reclamaciones (tributarias y generales)», publicación desde 9/6/2016, cobertura temporal desde 1/1/2016, frecuencia declarada diaria y actualización declarada 31/10/2026. El intento de abrir directamente esta ficha en esta sesión devolvió **HTTP 403**, que no se reintentó ni rodeó: la información anterior procede de índice público rastreado, no del contenido original.
- Catálogo de formatos y periodos, página HTML: https://datos.madrid.es/dataset/300044-0-syrg-syrt/downloads. En el índice público se distinguen **SYRG** (sugerencias y reclamaciones generales) y **SYRT** (tributarias), y para cada una «Recibidas» frente a «Terminadas». Para 2016–2021 se ven CSV por ejercicio; 2022 tiene CSV/JSON/XML, y desde 2023 se publican ficheros acumulados por formato. Tamaños visibles grandes: SYRG desde 2023 recibidas CSV 98,6 MB y terminadas CSV 102,3 MB. **Ninguno fue descargado.**
- Condiciones oficiales: https://datos.madrid.es/pages/condiciones-generales-ayuntamiento-de-madrid. El texto publicado indica que las condiciones obligan «por el mero hecho de hacer uso» de los documentos afectados. Exige atribución, preservar fechas y condiciones, no desnaturalizar la información ni reidentificar a personas; no consta aceptación ni adjudicación jurídica de esos términos en este trabajo.
- Para descartar repetición, una búsqueda de la clave exacta 300044 en la rama protegida PR7 no devolvió coincidencias entre research, docs, data/source_manifests, src y tests; R11 sí había trabajado **otros** datasets Madrid AIP 300517/300594, por lo que no se reciclan como nueva evidencia.

## Tres estimandos y riesgos incompatibles

**Ruta A — cohorte de entradas SYRG/SYRT (candidata para estudio descriptivo futuro).** Unidad tentativa: reclamación/sugerencia **recibida**, fecha de entrada, canal y tipo, independientemente de si será resuelta. Falsador: el archivo «Recibidas» excluye entradas por motivos internos o no representa un padrón inicial completo; también puede no contener identificador único estable o faltar canal. Un nombre de fichero no prueba un all-received.

**Ruta B — eventos de terminación (no equiparables automáticamente a la ruta A).** «Terminadas en 2022» puede corresponder a solicitudes iniciadas antes de 2022: sumar terminadas de 2022 y recibidas en 2022 como un mismo denominador fabrica una tasa de resolución espuria. Falsador: expedientes terminados en un año que aparecen en archivos de recibidas de años anteriores o expedientes reabiertos/reclasificados. Hace falta comprobar crosswalk por ID, no por asunto, fechas o nombres.

**Ruta C — diferencias generales/tributarias y reforma de publicación.** SYRG y SYRT pertenecen a circuitos administrativos distintos; cualquier comparación exige denominadores y competencias comparables, una política de deduplicación entre canales y régimen temporal explícito. Los ficheros acumulados «desde 2023» no deben sumarse con capturas sucesivas como episodios nuevos. Falsador: dos descargas de la misma acumulación con nuevas filas antiguas o cambios de estado, sin hashes ni tiempo de primera publicidad observados.

## Puertas R5, fuente y ausencia de evidencia

| Control | Lo que acredita la página HTML | Lo que falta | Estado |
|---|---|---|---|
| Fuente y posible grano | «Recibidas» y «Terminadas», SYRG/SYRT, periodos visibles | Esquema original y semántica oficial por columna/ID, deduplicación | DOCUMENTARY_ONLY |
| Derechos | Página oficial con condiciones y catálogo de datos abiertos | Revisión humana del régimen aplicable a distribuciones concretas CSV/JSON/XML y finalidad; condiciones obligatorias por mero uso | STOP_PREACCESS |
| All-received | Etiqueta editorial «Recibidas» | Prueba externa de completitud, canales e incidencias/inadmisiones | UNKNOWN |
| Denominador | No existe contraste independiente en los metadatos examinados | Libro de registro o total institucional realmente independiente del mismo backend editorial | UNKNOWN |
| Negativos, pendientes y censura | Hay archivos «Terminadas» separados | Stocks pendientes conocidos a fecha de corte, causas negativas, historia de cambios, censura por caso y seguimiento íntegro | UNKNOWN |
| Identidad y temporalidad | Fechas de catálogo y tipos de archivo | ID estable entre entrada/terminación, primera publicidad individual, al menos dos vintages originales SHA y fecha de captura | UNKNOWN |
| Estudios empíricos | Ninguno realizado | Falsadores A–J prospectivos, fuentes admitidas, derechos y controles completos | STOP_R5 |

## Próximo paso condicionado, no ejecutado

Reabrir únicamente si se dispone de una adjudicación humana sobre las condiciones legales aplicables **antes** de acceder a los archivos, y de una prueba independiente y compatible del universo de entradas, con negativos/pendientes y trazabilidad histórica. Mientras tanto, no acceder a los 100+ MB de datos ni extraer identificadores. Para el observatorio puede describirse la existencia de la fuente y sus límites, **no** cifras o tasas no calculadas ni supuestos de cobertura.

La identificación de esta fuente es **nueva para el inventario versionado consultado**, pero no acredita novedad académica de una hipótesis ni completa R5. El programa y la prueba de false rights R25 son independientes de esta exploración; ninguno es un ciclo AB científico.
