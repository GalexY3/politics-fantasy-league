> **Actualización tras integrar ACH20:** la rama incorpora `main` hasta `968f2b1723bd7961a6fe08d003b165d6a9e93c81`. La primera suite Linux integrada en `a3a68a6` registró 2 fallos Python por comparar el reloj variable y 2 fallos Node porque las expectativas antiguas no distinguían fuentes; se conservan los [logs originales](T010_EVIDENCIA/linux_ach20_first/sha256.txt). Se corrigieron solo esas pruebas, manteniendo los controles de estado y de duplicados de la misma fuente. En el commit `c2ff3386798eb51040559510e88040a234cbcce5` una repetición Linux completa obtuvo **770 Python y 28 subtests, 144 Node, 38 tests Atlas y 86 subtests, todos PASS**. Checker y replay: 75 lotes, 63 nodos, 81 relaciones, 241 runs, 48 incidencias, 416 operaciones y SHA canónico `118e95d9f34fcace52e21a6b92e09eac7a62ffc92ae6c20ac62512bb7d9d9692`. [Logs y hashes finales](T010_EVIDENCIA/linux_ach20_final/sha256.txt). El traslado de una ejecución intermedia falló por una aserción del disco FAT de QEMU y no se pudo conservar; esta ejecución se repitió desde un checkout limpio y recuperó los registros por consola serial, con todos los hashes verificados. Los commits posteriores únicamente documentan los resultados. No se han ejecutado ciclos AB-H ni CI de pago.

> **Otros dos riesgos identificados, no corregidos en T010:** el módulo experimental `src/politics_fantasy/vote_key_research.mjs` admite fechas con formato pero imposibles y el separador `|` dentro de componentes, permitiendo colisiones de claves; se ha reproducido con entradas sintéticas. No hay uso público ni afectación a datos reales demostrados. Requieren una reparación y pruebas propias.

# T010 · Reparación de Atlas y test HTTP

**SUCCESS EN RAMA, PENDIENTE DE REVISIÓN Y FUSIÓN HUMANA.** T010 es mantenimiento y QA, no un ciclo AB-H. No modifica CT2, VSDS, V4, hallazgos ni gates. T009 permanece `COMPLETADA_CON_FALLOS` para el checkout histórico.

## Alcance y procedencia

- Rama `fix/pfl-t010-atlas-http-20261028`, base `main` `08b244972012bde9a2572f4aa464d1b908258726`. Las pruebas integrales aquí registradas corresponden al commit de código **`63e71a3ecbe08bb13ad286c19bb203a414ff0a6e`**, checkout limpio en Linux; el commit posterior de documentación no se presenta como un checkout probado integralmente.
- El informe T009 original en Git permanece con blob `fab47ada673b6c3867fedcc5327cfeaada07c7b1`. Los ficheros de `T009_EVIDENCIA_8a761cf` se recuperaron del ordenador; sus blobs en el commit de trabajo coinciden byte por byte con todos los hashes del manifiesto. No se borran sus fallos ni se modifican fuentes privadas.
- Reproducción focal previa en Windows sobre `08b2449`: `py_compile` exit 1, test de timestamps exit 2 por colección y test HTTP exit 1. Las salidas están en `T010_EVIDENCIA/pre_*`; no se interpretan como ejecución Linux.

## Reparaciones

- `ab_atlas/atlas_delta.py`: restaurada la versión íntegra de `e3c25259765d6a71b20d41a07db0d7a7794ccdec`, blob `b47fc8e58b722b5b92830e91514cca253074bb90`, con un único `batch_check`, `cli` y `valid_batch_timestamp`. El único cambio respecto a esa base es validar fecha y hora ISO con zona explícita (`Z` o `±HH:MM`), calendario/offset reales y `datetime.fromisoformat`. Se rechazan offsets con minutos inválidos. No se han modificado reglas de operaciones, digest ni lotes históricos; no se impone orden cronológico entre fechas de lote. El error introducido en C01 sigue documentado en la errata previa.
- `ab_atlas/tests/test_delta_timestamps.py`: dos controles negativos añadidos, offset de minutos imposible y valor nulo.
- `tests/test_http_duplicate_json_keys.py`: el helper transmite bytes UTF-8 y verifica expresamente la secuencia de la letra acentuada. Conserva los dos rechazos `400 BAD_REQUEST` para claves duplicadas y el `200` para `Club Único`; el servidor no se ha relajado. La hipótesis de T009 quedó confirmada prospectivamente por este test corregido, no retroactivamente.

## Primera revalidación Linux del commit reparado

Linux Alpine 3.24.3 x86_64, QEMU 11.1.0 TCG, una CPU, 2 GiB, `noapic`; Python 3.14.10, pytest 9.0.3, pytest-subtests 0.15.0, Node 24.22.1, NumPy 2.4.6, tzdata 2026.6. Entorno virtual con dependencias del sistema y extra `test`; `PYTHONTZPATH=''` resolvió `Europe/Madrid`. `lo` activo y `eth0` desactivado en pruebas. No se ejecutaron originales privados ni Actions. El bundle de la rama tiene SHA-256 `b90e259cd3660c5dc554d5c70c9ec8845b4da94d45de2d094f118ed0b03c3632`.

| Comprobación | Exit | Resultado |
|---|---:|---|
| Checker canónico | 0 | 75 lotes, 63 nodos; SHA-256 canónico `118e95d9f34fcace52e21a6b92e09eac7a62ffc92ae6c20ac62512bb7d9d9692`. |
| Replay y recuentos | 0 | 75 lotes, 63 nodos, 81 relaciones, 241 runs, 48 incidencias, 416 operaciones; coincide con el recuento documental. |
| Todos los tests `ab_atlas/tests/` | 0 | 38 passed, 86 subtests passed. |
| Suite Python completa de Politics Fantasy | 0 | 758 passed, 28 subtests passed, sin skips; 71,54 s. |
| Test HTTP focal | 0 | 1 passed; incluye negativos y acento. |
| Todos los tests Node | 0 | 127 passed, 0 failed, 0 skipped. |

Las órdenes exactas están en `T010_EVIDENCIA/linux/check.sh`. Los ficheros vacíos de stderr se recrearon como vacíos tras errores `cluster 0 used more than once` y `Error in short name (-1)` de la carpeta FAT compartida, igual que en T009; todos los hashes de `linux/sha256.txt` coinciden con los calculados antes de la transferencia en Linux. El stdout HTTP adicional coincide con el hash calculado en Linux `3b4875dc515d55439d8abed80997ab1489b094e334bc63b66b9e80213b49f41e`; su stderr vacío tiene SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

Hashes destacados de evidencia Linux: `atlas.out` `5fb896d27a967a9395209db01b3c518c612f0c9477be2ead0d2e95462ca7a84b`; `atlas_tests.out` `ab67a5d80a7155131503b88fe03948669002e39cc9f1502d7d866129e9bffc21`; `pytest.out` `0ea22f29418e5471114cab7afd190b572226aa0cf38541f4b43cb95e5a938c47`; `node.out` `b8e7d798a081e3d5ec9af19078fd53589b7075faaf59e5fc70fbec87c74cebe5`. [Evidencia y manifiesto](T010_EVIDENCIA/linux/sha256.txt).

[PR #18](https://github.com/GalexY3/Metodologia-AB/pull/18) · [Compare rama contra main](https://github.com/GalexY3/Metodologia-AB/compare/main...fix/pfl-t010-atlas-http-20261028). Los resultados de QA no acreditan las fuentes parlamentarias, los derechos, la identidad, la primera publicación ni un despliegue público.
