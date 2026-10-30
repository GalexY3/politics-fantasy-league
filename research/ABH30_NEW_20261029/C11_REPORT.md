# Politics Fantasy League · ABH30-C11 — CLI local con versiones Git públicas fijadas

**Fecha:** 29/10/2026 · **AB-P técnico, DRIFT D1**. Rama `research/pfl-abh30-c11-pinned-original-cli-20261029`, sucesora de PR #61. Independiente de las dos plazas históricas `STOP_R5`.

## Resultado

Se añade el ejecutable local `scripts/offline_forecastbench_revision_audit.mjs` que importa el **auditor C09 original sin cambios** y verifica SHA-1 de objeto Git de ambos ficheros de resoluciones **antes de analizar ninguna fila**. El CLI admite solo tres pares exactos identificados en C10, cuyos 6 Git blobs y commits están **fijados en código**, y no acepta un manifiesto de confianza proporcionado por el usuario. Compara todas las claves `(source,id)`, detecta altas, bajas, mutaciones y retenciones y entrega **únicamente un JSON de agregados**. Un error provoca código de salida 1 y salida estándar vacía; stderr no contiene IDs ni rutas. Rechaza enlaces simbólicos directos, archivo vacío y tamaño mayor de 5 MB; no escribe los archivos originales.

**Ejecución verificada:** contratos y hashes congelados en [C11_PREREG_AJ_SHA.json](C11_PREREG_AJ_SHA.json) commit **`5d386f40ade3148296c30780af15f9ef72cefcc3` antes de ejecutar**; código blob `2b6e910c998f99de121050badfab83adaf345220`, SHA256 `1ad4adc05680c5dcfe6b5eb3d5ce25575fcf4c3b2a36f8e8e59e6a140b7154cc`, test blob `d81e5197104bbd0dad287cd3519950a5dad1f196`, SHA256 `17e39790c88d66f50935dc76b1032fbe1439776f8021d39af741b6f6e4c4af2b`, dependencia C09 blob `2e1ed7f5e23bbad79c81013505882830907cb258`. **Node v22.16.0 `node --test tests/test_offline_forecastbench_revision_audit.mjs`: 17/17 PASS, exit 0.** Hashes locales cotejados con GitHub antes de ejecutar. SHA256 de salida TAP guardada localmente `c46653bbba7d179bd52e40bad648f0066c27be0e08b7b9f602f835398930ad5e`. Recibo [C11_RUN_RECEIPT.json](C11_RUN_RECEIPT.json).

## Uso, sin descargar ni distribuir fuentes ajenas

Desde el directorio raíz `proyectos/politics-fantasy-league/`:

```bash
node scripts/offline_forecastbench_revision_audit.mjs --pair sep07to08 --source-dir ./originales_publicos
```

El directorio debe contener **dos ficheros originales íntegros**, nombrados `sep07to08.before.json` y `sep07to08.after.json`. Para los otros dos pares se usan `sep11to12` y `oct23to24`, sustituyendo el prefijo en ambos nombres. Se obtienen por vías legales del repositorio original `forecastingresearch/forecastbench-datasets`, en los commits publicados y SHA fijados en el programa. No usar archivos reserializados; el Git blob SHA depende de cada byte. No hay descarga automática ni contacto con autores.

**Estado de aplicación positiva:** se ha probado con **buffers sintéticos compatibles y hashes sintéticos** únicamente por la API de biblioteca. Se han probado realmente ejecuciones del proceso CLI rechazando archivos sintéticos incorrectos respecto a los pins originales. **NO se ha ejecutado una comparación positiva del CLI con los seis ficheros originales desde disco**, porque no se ha conseguido recuperarlos localmente; el contenedor no puede resolver `github.com`. C10 sí verificó seis blobs originales **en V8 por conector GitHub**. No atribuir los resultados de C10 a la nueva ruta nativa.

## Contrato A–J

**A — Verdad / unidad.** Unidad = fila de metadatos públicos de resoluciones por `source,id` entre dos Git commits. Objetivo de producto = evidencia de que la ruta local exige byte identity antes de comparar, no precisión de predicciones ni causalidad humana.

**B — Rivales.** H1, control obligatorio de bytes originales + CLI sin fugas. H0, se aceptan bytes incorrectos, fechas inversas, claves duplicadas, symlinks o entradas sin contrato. Rival de valor: C09 podía emplearse en una aplicación manual, así que una nueva CLI podría ser redundante si no añade integridad. Resultado: pruebas de integración del CLI, pero falta ensayo positivo original.

**C — Discriminación.** 17 casos congelados de hash, seleccionador fijo, adaptador positivo sintético, negativos de schema/hora/duplicados/bytes, lectura de ficheros y ejecución CLI en subproceso; sin personas.

**D — Instrumentación.** Nuevo script y tests con blobs y SHA256 verificados; importación del comparador C09 intacto; prerregistro antes del primer test. No se introduce fuente de datos nueva.

**E — Ejecución.** 17/17 Node tests nativos PASS, sin reparaciones posteriores, resultado TAP descrito. Revisión de 19/19 pruebas nativas C09 precedió este ciclo pero no se vuelve a contar.

**F — Auditoría.** No se confunde una coincidencia con Git SHA1 de un objeto anclado con certificado del editor original ni licencia para registros personales. La API `auditRawPairBuffers` permite recibir pins sintéticos para test; el **CLI no acepta pins personalizados**. Un `lstat` seguido de `readFileSync` no proporciona seguridad ante carrera concurrente de filesystem hostil; la herramienta está destinada a uso local sin adversarios con acceso de escritura simultáneo.

**G — Comparador.** Antes, C09 aportaba API pura, C10 ejecución original por conector V8 y otro CLI de publicación sobre snapshots/preguntas. Ahora hay un camino de ejecución nativo CLI para pares de revisiones históricas fijados. No se mide rendimiento ni cobertura de datos originales completos por CLI.

**H — Priors.** Preservar PF-BR49 y fuente; no añadir un nuevo prior sustantivo ni grado 1/3 por QA. Evidencia solo para el ledger técnico de producto.

**I — Dictamen.** **AB-P válido limitado al módulo ejecutable y sus pruebas sintéticas**, no producto validado ni nuevo efecto científico. CT2 prospectiva PFL **20/100 ordinal**, N1/N2/N3 nuevos **0/0/0**, puertas de lanzamiento **0/6**. El lote Atlas 0081 solo pudo verificarse **estáticamente** contra el chequeo de batch y `run.add` de `atlas_delta.py`; no se ejecutó el replay Python de los 81 deltas ni se certifica SHA canónico.

**J — Decisión.** Contar **un** ciclo nuevo C11: **11/30 válidos limitados, 19 disponibles**, 2 plazas históricas intactas STOP_R5. No gastar otro ciclo hasta obtener una prueba original positiva por ruta legal o nueva evidencia verdaderamente independiente y útil; no `main` merge, CI costosa, ChatRelay, scoring real ni tratamiento de datos personales no autorizados.

