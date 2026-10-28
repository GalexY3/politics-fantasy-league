# T009 · Suite Linux de main y checker Atlas

**COMPLETADA_CON_FALLOS.** Primera ejecución sin cambios de producción ni de tests. No es un ciclo AB; no se corrigen los defectos en esta tarea. El estado de los indicadores científicos y los seis gates no cambia.

## Procedencia y entorno

- HEAD remoto de `main` al comienzo y commit del checkout Linux: `8a761cf3081b7d09dae6cacb9f58fa58192863e4`. `git status --short` vacío antes de las pruebas. Checkout completo y limpio desde bundle, en `/tmp/repo` sobre Linux, sin archivos privados no versionados. Bundle SHA-256 `9c4916ad82f2e73e01d1a8af4ee601a326b6efdda847766f7f0f243e62c58903`.
- Windows anfitrión; Alpine Linux 3.24.3 x86_64 bajo QEMU 11.1.0, TCG, una CPU, 2 GiB. Primer arranque con dos CPU sufrió kernel panic de temporizador IO-APIC antes de ejecutar pruebas; arranque funcional con `noapic` y una CPU. ISO SHA-256 `cdc1bc0efc64d8d611bf3733f54868172a545888dfd726f518bf279bcb0ff1af`; instalador QEMU SHA-512 `5bcf9eed634e8575a37b74f445af41a2fe4106da512d0c30c368301d4c105037fdfab40a5287367a28a957624cddebbc8c07e16c88ab6634f554cdf3d16bf543`.
- Python 3.14.10, pytest 9.0.3, pytest-subtests 0.15.0, Node 24.22.1, NumPy 2.4.6 y paquete Python tzdata 2026.6; dependencias y proyecto instalados en un entorno virtual con paquetes de sistema, extra `test`, `--no-build-isolation`. `PYTHONTZPATH=''` resolvió `Europe/Madrid` (exit 0). Loopback activo; interfaz externa `eth0` desactivada durante las pruebas. No se usaron originales privados ni GitHub Actions.
- Durante la ejecución avanzó `main` a `e706fa59e36df460846326a8b992037f84fd006c`; el único cambio entre ambos commits añade `docs/PILOTO_UX_FICCIONAL_PRE_T009_20261028.md`. No se ha ejecutado la suite sobre `e706fa5` y estos resultados corresponden exclusivamente a `8a761cf`.

## Resultados de primera ejecución

| Comprobación | Exit | Resultado |
|---|---:|---|
| Checker canónico Atlas | 1 | SyntaxError en `ab_atlas/atlas_delta.py:24`; no se reconstruyó el estado. SHA canónico **UNKNOWN**; 75 lotes son un recuento documental previo, no validado aquí. |
| `ab_atlas/tests/test_delta_timestamps.py` | 2 | Un error de colección por el mismo SyntaxError; ninguna prueba de ese archivo ejecutada. |
| Suite Python completa del proyecto | 1 | **757 passed, 1 failed, 28 subtests passed, 0 skipped**, 71,76 s. |
| `node --test tests/*.mjs` | 0 | **127 passed, 0 failed, 0 skipped**; incluye `test_overview_readiness_copy.mjs`. |

El checker no pudo calcular lotes, nodos, aristas, incidencias ni operaciones; no atribuirle los recuentos documentales. La salida positiva de los tests Node y Python que pasaron no acredita procedencia real, identidad, scoring ni preparación de despliegue.

## Fallos y clasificación

1. **Defecto de código confirmado:** `ID_RE = re.compile(r'^[A-Za-z0-9_./:-]{1,100}` carece de cierre de literal y paréntesis en `ab_atlas/atlas_delta.py:24`. Se verificó el mismo contenido directamente en el objeto Git del commit probado. Impide ejecutar el checker y recoger los tests de timestamps.
2. **Fallo de prueba HTTP confirmado:** `tests/test_http_duplicate_json_keys.py:31` espera 200 para `Club Único` pero recibe 400; los dos rechazos anteriores de claves duplicadas pasan. El test entrega un `str` a `http.client`, cuya codificación de cuerpo es Latin-1; JSON recibido como bytes exige una codificación válida UTF. Una comprobación independiente de codificación mostró `Ú` como `da` en Latin-1 y `c39a` en UTF-8. Esta explicación es consistente con el fallo; no se ha modificado ni repetido la prueba con bytes UTF-8, por lo que no se declara reparación ni se descarta otra causa adicional.

## Evidencia y reproducibilidad

Salidas, errores, códigos, versiones, comandos y hashes en [T009_EVIDENCIA_8a761cf](T009_EVIDENCIA_8a761cf/). Los ficheros de salida vacíos se recrearon como vacíos tras una incidencia `cluster 0 used more than once` de la carpeta FAT compartida de QEMU; todos sus hashes, y los de los ficheros no vacíos, coinciden con el manifiesto SHA-256 calculado en Linux antes de transferirlos. Los logs originales de prueba no se han editado.

- `pytest.out`: SHA-256 `68f5492c8d920114213d4044281d97c5a09747247253d8df184adff419b0b0cc`.
- `atlas.err`: SHA-256 `8f0c985586dfa45b0005114913cabeca0a02ccd53ffc5820193107a59170aac7`.
- `atlas_tests.out`: SHA-256 `7dac9884ee4bfa382d3c32f90b6dc7d7ceda389db1ae2fad0dea9b5772b5e0c4`.
- `node.out`: SHA-256 `c4c28e2d448c16fd07049cb0f011c2e8167e89d286fc0d5ca1ffb2506655c229`.
- Las salidas stderr vacías y `status.txt` tienen SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`.

**Siguiente paso:** revisar y reparar ambos defectos con la autorización pertinente; después ejecutar de nuevo las comprobaciones completas sobre el nuevo commit, conservando esta primera ejecución. No se ha hecho commit, push ni merge de este informe.
