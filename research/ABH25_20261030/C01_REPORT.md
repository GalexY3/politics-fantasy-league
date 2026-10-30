# ABH25-C01 · procedencia temporal en fuente original independiente

**Ejecución documental original limitada**: tras congelar [A–J](C01_PREREG_AJ.json) y el [instrumento](c01_source_audit.js) en GitHub antes de abrir código, se leyó el archivo original `scripts/fetch-reunions.mjs` del repositorio [Suite à donner](https://github.com/Clemsrec/suiteadonner/blob/a627cc26f255231d67faebb14e265523e46c0a66/scripts/fetch-reunions.mjs), commit `a627cc26`, blob `4d6b24a1d65ac6293793da3ffc2a0f41df9ba61b`, 36.917 caracteres.

**A–B:** ¿La instrumentación inspeccionada conserva para cada decisión su primera publicación pública y versión, o solamente la fecha de reunión/lectura actual? No es una medición causal, ni observación de sujetos humanos.

**C–E:** 3 coincidencias automáticas con términos de archivo/historia, 1 con marcas temporales, 12 con numeración y 0 con términos de hash/snapshot. Revisión adversarial de contexto: las tres primeras coincidencias son **archivos ZIP**, no historial del evento; `updatedAt: Timestamp.now()` en línea 869 actualiza un documento agregado de Firestore, no la primera aparición pública. En línea 696 `r.timeStampDebut` es la fecha de la reunión. `compteRenduRef` vincula el acta a la reunión, con lógica conservadora de numeración; esto no equivale a primer `first_public_at`.

**F–G:** el instrumento es búsqueda de patrones más revisión de código fuente; **no se ha ejecutado el pipeline de terceros**, y la ausencia en un archivo no excluye otra capa externa. El README de terceros ya advertía las decisiones omitidas; ningún reclamo de novedad de ese mecanismo. Antecedente MIT verificado, sin reutilizar ficheros.

**H–J:** el resultado es negativo acotado: la hipótesis de procedencia temporal por evento **no queda demostrada en el script inspeccionado**. Se actualiza un prior instrumental; 0/3, CT2 20 ordinal, puertas 0/6. Se registra un único ciclo AB-R de auditoría documental limitada, no confirmación empírica humana. No repetir esta fuente para consumir cuotas. Continuar solo con archivo oficial históricamente versionado o marco de agenda nuevo verificable; aparcar causalidad sin `first_public_at`.

Fuente y detalles reproducibles: [recibo JSON](C01_RUN_RECEIPT.json). No se ha fusionado `main`.
