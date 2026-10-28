# T008 · Suite completa Python en Linux mediante QEMU

**Resultado: COMPLETADA_VERIFICADA en el checkout y entorno descritos.** No es un ciclo AB ni una certificación de producción, de fuentes reales o de resistencia a pérdida de energía.

## Entorno y procedencia

- Checkout íntegro del commit `b0344d1a1549e66274a347333239b81fc7575100` de `research/pfl-codex-contributions-20261027`, a partir de un `git bundle` local completo, SHA-256 `13765438109e098e65028a4dbc60c3bd6606beae3cb758a23046ba26fda1a921`. El checkout en el invitado quedó en HEAD separado, limpio; no se trasladaron archivos ignorados o no versionados, incluidos originales privados.
- Windows como anfitrión; QEMU 11.1.0 en carpeta temporal, emulación TCG, 2 CPU y 2 GiB. Instalador QEMU descargado del distribuidor enlazado por QEMU y comprobado con su SHA-512 `5bcf9eed634e8575a37b74f445af41a2fe4106da512d0c30c368301d4c105037fdfab40a5287367a28a957624cddebbc8c07e16c88ab6634f554cdf3d16bf543`. Imagen oficial Alpine virt 3.24.3 contrastada con el SHA-256 publicado `cdc1bc0efc64d8d611bf3733f54868172a545888dfd726f518bf279bcb0ff1af`.
- Invitado Linux `6.18.58-0-virt`, x86_64; usuario `pfl` UID/GID 1000; checkout y temporales en **tmpfs Linux**, no en FAT de Windows. Python 3.14.10, pytest 9.0.3, Node 24.22.1, NumPy de los paquetes de Alpine, base de zonas horarias Alpine `tzdata` 2026e-r0. Se instalaron dependencias en la máquina temporal y después se desactivó su interfaz externa; el loopback se mantuvo activo en las ejecuciones finales. Ningún original institucional fue consultado ni incluido.

## Ejecuciones completas preservadas

Desde `/home/pfl/repo/proyectos/politics-fantasy-league`, con `PYTHONPATH=src`, `python3 -B -m pytest -q -rs`:

1. **Primera ejecución, exit 1:** 13 failed, 608 passed, 30 errors, 28 subtests passed. La interfaz loopback no había sido activada al cortar la red externa: múltiples pruebas HTTP fallaron con `Address not available`. También faltaba la base `Europe/Madrid`. Log local `%TEMP%\pfl-linux-vm\share\first.out`, SHA-256 `8629c3c851d83c4c323bb5d2c151e4e6958a9cd450828a1716f1b3116cd10ad4`.
2. **Loopback activado, exit 1:** 7 failed, 644 passed, 28 subtests passed; los siete fallos eran `ZoneInfoNotFoundError` para `Europe/Madrid`. Log local `second.out`, SHA-256 `c97f5cfa24f8fc2c8130fca982c0c9beff20409c49df625b3a90bfc01954887b`.
3. **Loopback activo, interfaz externa desactivada y `tzdata` del sistema instalado, exit 0:** **651 passed, 28 subtests passed, 0 failures, 0 skips**, en 72,16 s. Salida íntegra versionada en [T008_POSIX_FINAL_STDOUT.txt](T008_POSIX_FINAL_STDOUT.txt), SHA-256 `e7cf1269d4c6aae0a2f8d436bc027908153a7063fc033991d926d8e7cbea8485`; stderr vacío (SHA-256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`).

No se modificaron tests ni código entre las tres ejecuciones. La base de zonas horarias es una dependencia del entorno; el extra de tests del proyecto solo declara el paquete Python `tzdata` en Windows, por lo que un Linux mínimo sin base IANA requiere instalarla o declararla expresamente. El resultado no demuestra compatibilidad de almacenamiento privado con Windows ni generaliza automáticamente a otros sistemas o commits.

Tras guardar los logs se apagó la máquina virtual. Se mantienen los informes anteriores y el resultado independiente de ChatGPT de 89 pruebas seleccionadas; no se suman como ensayos independientes. V4, CT2, VSDS y los seis gates no cambian.
