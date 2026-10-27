# AB-R · Auditoría documental de «NO VOTAN» (27/10/2026)

**Clasificación:** AB-R, examen documental A–J **retrospectivo / POST_HOC_AUDIT**, no experimento prospectivo ni ciclo AB-H nuevo contabilizado. La fuente se descubrió **antes** de redactar este registro; prohibido denominarlo prerregistro. No modificar CT2, VSDS ni gates por una sola referencia.

## A. Pregunta / estimando
¿Existe evidencia institucional directa de que el Senado distingue en su información de votaciones a los senadores **presentes que expresamente no votan**? Unidad: categoría de asistencia/participación en el Pleno. No es un estimando causal ni una medida de conducta individual.

## B. Rivales
H1: la documentación del Senado distingue explícitamente el estado «presente pero no vota». H0: la documentación institucional consultada no distingue tal estado. H2: esa distinción existe, pero no está acreditada la equivalencia exacta con el literal XML `NO VOTAN` ni su aplicación universal a sesiones, épocas o cámaras.

## C. Contraste discriminante
Leer fuente institucional original sobre asistencia, no una paráfrasis de terceros; diferenciar prueba de concepto institucional de diccionario técnico del XML. Falsador de una interpretación fuerte: un esquema o manual del feed que asigne el literal `NO VOTAN` a otra definición o a varias situaciones.

## D. Instrumentación
Inspección de la página oficial en español del Senado con URL y texto de las fechas; sin descarga de originales privados, sin uso de HTTP ingestion local y sin pruebas automatizadas. La página declara última actualización 07/10/2022.

## E. Observación documental
La página oficial señala que desde la sesión plenaria 34, de **04/06/2013**, los datos de votaciones permiten identificar senadores que **están presentes pero expresamente no votan**. La misma página distingue los votos telemáticos registrados desde la sesión 44, **09/12/2013**.

Fuente primaria: https://www.senado.es/web/composicionorganizacion/senadores/asistencias/index.html?lang=es_ES (sección «Sesiones plenarias»; consulta 27/10/2026).
Fuente auxiliar institucional: https://www.senado.es/web/diccionarioterminosparlamentarios/index.html?lang=es (definiciones de abstención y votación). No proporciona un diccionario XML inequívoco.
No se ha inspeccionado en este examen el esquema/contrato de serialización de la etiqueta de cada XML de 2025.

## F. Auditoría adversarial
Un estado «presente y no votante» **no es sinónimo** de ausencia, abstención, voto contrario ni inasistencia culpable. Tampoco justifica suponer intención estratégica. La evidencia no prueba que *cada* `NO VOTAN` del parser corresponda sin excepción a esa clase: es imprescindible relacionar el literal con el formato, edición y publicación concreta. Los resultados numéricos previamente atribuidos a fixtures no se reproducen aquí.

## G. Confirmación
**NO EJECUTADA:** falta un manual de datos/XML oficial o respuesta editorial explícita y comprobación cruzada de una votación con listado nominal/acta contemporánea. La segunda fuente institucional del mismo Senado no constituye replicación editorial independiente.

## H. Actualización doble
H1 queda respaldada al nivel de **definición pública institucional**. H2 permanece activa para el literal técnico y su efecto en scoring. Nueva hipótesis: los esquemas y las normas de captura varían históricamente (ruptura indicada en 2013); test: comparar los códigos de períodos anterior/posterior y documentación de versiones. No hay actualización numérica justificable de CT2.

## I. Dictamen
Validez documental acotada: **favorable** para la existencia de presentes que no votan. Equivalencia XML literal, transportabilidad a otras fechas/cámaras, causalidad y criterio de puntuación individual: **NO ACREDITADOS**. Novedad científica: ninguna establecida. No elevar 0/6 gates, VSDS 1/3 ni CT2 identidad 29/100.

## J. AB-DECIDE
**STOP_R5** para repetir la misma cita. **PIVOT condicionado** a obtener diccionario/esquema XML oficial y alinear `NO VOTAN` con una votación original, número de sesión, identidad y estado de asistencia documentado. No exponer datos nominativos privados ni activar scoring real.

**Procedencia/limitaciones:** investigación de fuente pública realizada mediante navegación web del 27/10/2026. Este archivo es un registro retrospectivo y no acredita pruebas de repositorio ejecutadas, preregistro previo ni replicación externa.
