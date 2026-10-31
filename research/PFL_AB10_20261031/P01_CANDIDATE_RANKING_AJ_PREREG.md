# P01 · Evaluación de recuperación de candidatos documentales

**Antes de resultados. AB-P experimental sintético.** No AB-R y ninguna autorización de crosswalk jurídico. Baseline B0 = SequenceMatcher del PP04C, actualmente generador de sugerencias UNKNOWN sobre títulos.

**A. Estimando.** Recall@3 de correspondencia sintética conocida, sobre 198 propuestas ficticias por semilla. Secundarios recall@1, destinos top1 distintos, colisiones y desagregación por perturbación. Población: generador artificial de títulos normativos españoles de juguete, nunca muestra de España ni casos políticos reales.

**B. Rivales.** B0 SequenceMatcher, B2 Jaccard de tokens uniforme y B1 Jaccard con IDF computado sobre títulos de las candidatas, con componente ligero de similitud textual. Paridad: las tres técnicas ven los mismos títulos y máximo tres posiciones, ninguna conoce ID de verdad, outcome IAEN o estatus de aprobación. H1: B1 supera B0 al menos 0.05 de recall@3 macro y no queda más de 0.02 por debajo de B2 ni más de 0.10 en ningún estrato. H0: no hay valor añadido a Jaccard, la ventaja depende del generador o empeora ciertos títulos.

**C. Diseño.** 198 pares sintéticos, >=45 distractores por semilla, reordenación de tokens, abreviaciones y nombres de apariencia similar. Exploración solo semilla 4711. Tres semillas confirmatorias reservadas 991, 992, 993. No modificar generador ni algoritmo al observar una semilla confirmatoria; si hay reparación, declarar INVALID de corrida afectada y freeze nuevo. Tres oráculos de privacidad: todas las sugerencias UNKNOWN, no derechos afirmados, no uso de estados retrospectivos.

**D. Instrumentación.** Solo Python estándar y versionado. Oráculos de N, unicidad, top-k, origen, SHA y clipping. Tests con entradas enteramente inventadas antes de ejecutar el benchmark.

**E. Ejecución.** Prerregistro+instrumentos+tests en commit Git remoto antes de ver resultados. Archivar JSON por semilla, versiones de code/fuente y salidas adversariales.

**F. Red team.** Controles de títulos duplicados, varios candidatos nominalmente iguales, fuente vacía, caracteres inesperados, misma información para baseline B0 y B2. Ablación del peso IDF. El mejor método no debe construir una identidad jurídica a partir de un score.

**G. Confirmación.** Tres semillas reservadas son nuevas realizaciones del MISMO generador, no réplica externa. Aceptar H1 únicamente si cumple todos los criterios.

**H. Abducción.** Si falla por reordenamiento/duplicados, actualizar hipótesis de forma cualitativa y declarar la necesidad de ID oficial; ninguna posterior observación sintética demuestra identidad española.

**I. Dictamen.** Validez interna limitada a generador, no identificación causal, derechos, autenticación editorial, first_public_at o transportabilidad; grado científico 0, R5 STOP.

**J. Regla.** Un máximo de un ciclo AB-P, estatus READY_REVIEW_SYNTHETIC si H1 supera todos los umbrales y queda reproducible. Si falla, STOP o PIVOT sin maquillarlo; pruebas y reparaciones no son ciclos extra. CT2 y logros científicos sin cambios.
