# Conciliación de la evidencia T008 entre rama Codex y main

**Fecha:** 28/10/2026. **Acción: incorporación selectiva de evidencia sin fusionar ni sustituir la evolución de `main`.** No se ha ejecutado ninguna prueba adicional al escribir esta nota. El usuario señaló la [evidencia histórica T008](https://github.com/GalexY3/Metodologia-AB/blob/0c940f02690668d34f0bbe151bab7c77788302ce/proyectos/politics-fantasy-league/tareas_codex/T008_RESULTADO.md) y solicitó distinguir su alcance del código actual.

## Evidencia exacta recuperada por GitHub

| Archivo original en commit `0c940f02690668d34f0bbe151bab7c77788302ce` | SHA del blob Git original | Estado en main |
|---|---|---|
| `T008_RESULTADO.md` | `64cc8fb8cf0c1b38bdb29677f55403bdc8996915` | Copia **byte-a-byte coincidente**, sin reescribir informe |
| `T008_POSIX_FINAL_STDOUT.txt` | `3e1ed4989bf53755ea60b0df50aa661c305a9640` | Copia **byte-a-byte coincidente** |
| `T008_AVANCE_ATLAS35.md` | `d20e8d7596176e2ff4a2f14ace267391a558db00` | Copia **byte-a-byte coincidente** |

La prueba final T008 fue realizada por Codex sobre el checkout Git `b0344d1a1549e66274a347333239b81fc7575100` con Linux Alpine 3.24.3 temporal mediante QEMU (anfitrión Windows, guest Linux 6.18.58-0-virt, Python 3.14.10, pytest 9.0.3). Tras preparar loopback y la base IANA `tzdata` del invitado, el comando `PYTHONPATH=src python3 -B -m pytest -q -rs` obtuvo **651 pruebas PASS, 28 subtests PASS, cero fallos y cero omisiones**, salida final `exit 0`. SHA256 stdout **informado por Codex** `e7cf1269d4c6aae0a2f8d436bc027908153a7063fc033991d926d8e7cbea8485`; se conserva el stdout textual íntegro en el archivo SHA-idéntico. El informe preserva dos ejecuciones fallidas: (1) 13 FAIL, 608 PASS, 30 ERROR /28 subtests por ausencia de loopback y `Europe/Madrid`; (2) 7 FAIL, 644 PASS /28 subtests, únicamente falta de base IANA. Codex declara que no cambió tests ni código entre ejecuciones. Los dos logs fallidos se referencian por ruta local y hashes declarados, **no están versionados aquí**.

Se comprobó también el Atlas en otro checkout histórico `9d0ef8433f92749b3f3364f31139b07320f1ec16`: **35 lotes, 63 nodos, 81 aristas, 201 runs, 44 complaints y 370 ops**, checker canónico y `replay` con exit 0; SHA256 de estado reportado `bff6978684b0d6d4cdfcd8211656750430b956f6ebb92c0faeff042e13758d81`. El informe histórico [Atlas35](T008_AVANCE_ATLAS35.md) explicita que se hizo en Windows/Python 3.12.14, no en el invitado Alpine y no en el HEAD `main`.

## Comparación exacta con main

Comparación GitHub `b0344d1a1549e66274a347333239b81fc7575100...894e1b7a48c83bd84cc4c38cfb7e7699bf077ac1` (HEAD de main **anterior** a importar la evidencia): **historias divergentes**, `ahead_by=162`, `behind_by=4`, **119 archivos modificados**. NO procede fusionar en bloque el branch Codex, pues incluye cuatro commits de linaje separado y podría pisar las modificaciones posteriores.

Diferencias relevantes, comprobadas por SHA Git:

- El `ab_atlas/atlas_delta.py` probado históricamente es blob `b47fc8e58b722b5b92830e91514cca253074bb90`; `main` ahora contiene blob `8af1c74784c5f60892a038c026990619d1c95a85` con validación ISO-aware de `batch.at` y test `ab_atlas/tests/test_delta_timestamps.py` **nuevo**.
- `src/politics_fantasy/evaluation.py` antiguo `985846a93b8665bab15fd0db7144c3e4e458c5c3`, actual `0c35692887a5e0e10321286a24115faee2c3d6cf`: bootstrap por registros añadidos.
- `src/politics_fantasy/sociometrics.py` antiguo `e1d68756824b0a3f629c88f31beddc5a0001b680`, actual `8ec74f0d1d7e52ff464f40bc2038d5ee90b91857`: mayoría estricta en indicador de discrepancia.
- `src/politics_fantasy/lab.py` antiguo `8cf4e2e7b5449c13952bc77f65774f93aaf90f22`, actual `6c8ab1cd64b07e86e699cfb188d5f887d617b89e`.
- Diferencia completa GitHub contabilizó **14 archivos de test añadidos/modificados** (uno es Node), así como fuentes históricas recuperadas, cambios a `majority_sign.py`, `scoring.py`, `forecast.py`, `groupvotes.py` y frontend. Los nuevos tests no estaban en el checkout `b0344d1`.

**Por tanto:** T008 es **COMPLETADA_VERIFICADA solo para `b0344d1`/Linux Alpine**, y el Atlas **35 lotes** fue completado en otro checkout `9d0ef84`. El estado del **main actual, 60 lotes, suite completa y checker Python es NOT_RUN**. No se afirma que el resultado antiguo sea erróneo; tampoco que avale los cambios posteriores. Reproducir la prueba sobre HEAD actual es la **nueva tarea T009**, no una T008 ficticiamente pendiente.

## Acciones y límites

Se copiaron solo los tres archivos históricos originales con blobs SHA exactos. **No se importaron** versiones antiguas de `CURRENT.md`, `BACKLOG.json`, `README.md`, tests, fuentes o Atlas. Se mantuvieron los cambios posteriores y la campaña MAIN20B (5 válidos, 15 restantes; **ningún ciclo se consume por conciliación de pruebas**).

T008 queda etiquetada como `COMPLETADA_VERIFICADA` con `verified_checkout=b0344d1`; T009 queda `PENDIENTE` para `main` y su Atlas 60. No publicar datos nominales, no activar scoring real, no fusionar ramas divergentes ni lanzar CI costosa. Los seis gates continúan 0/6, CT2 identidad 29/100 ordinal, V4 36,90 % contractual, VSDS 1/3 y nuevos hallazgos 0/0/0.
