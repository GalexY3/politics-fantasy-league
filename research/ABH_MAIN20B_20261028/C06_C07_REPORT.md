# MAIN20B · T008 recuperada, C06 y C07 · 28/10/2026

## T008: evidencia histórica recuperada

El [informe original](../tareas_codex/T008_RESULTADO.md) y la [salida íntegra](../tareas_codex/T008_POSIX_FINAL_STDOUT.txt) de Codex en `0c940f0` están preservados en `main` con **idénticos blobs Git**. T008 se completó en `b0344d1`: Alpine Linux/QEMU, **651 PASS +28 subtests PASS, cero fallos, cero skips** tras dos corridas iniciales fallidas por entorno (loopback y base IANA). La comprobación canónica de Atlas **35 lotes** se había completado por separado en `9d0ef84`, ver [avance Atlas35](../tareas_codex/T008_AVANCE_ATLAS35.md).

La comparación original de `b0344d1` frente al `main` `894e1b7a` previo a la importación fue **diverged**: 162 ahead, cuatro behind, 119 archivos distintos; no se fusionó aquella rama, ni se sobreescribió código de MAIN20B. [Informe de conciliación](../tareas_codex/T008_RECONCILIACION_MAIN_20261028.md).

## C06 · auditoría independiente de seguridad de la conciliación

Prerregistrada después de importar T008, contrastó los árboles SHA `894e1b7a` y `bab2ddea` antes de cambiar el expediente. Resultado: 13 rutas añadidas/modificadas —siete documentos modificados y seis nuevos de evidencia y prerregistro—; **ningún blob en `src/`, `tests/`, `ab_atlas/` o deltas históricos se alteró**, ninguna ruta eliminada, lotes **60→60**. El archivo T008 histórico en `main` coincidió con el blob del commit de Codex `64cc8fb8...`. Esta es una auditoría AB-META de la importación, **no una nueva ejecución Linux**. [C06 resultado](C06_RESULT.json).

## C07 · reparar la dependencia opcional de zonas horarias

La corrida inicial de T008 mostró que Alpine sin base IANA no resolvía `Europe/Madrid`. El `pyproject.toml` previo tenía `tzdata>=2024.1; sys_platform == 'win32'` únicamente en `test` y `research`. Se prerregistró y ejecutó control Linux: `PYTHONTZPATH=''` dejó `TZPATH=[]` y Python 3.13.5 resolvió `ZoneInfo('Europe/Madrid')` utilizando paquete pip `tzdata 2026.2`. El manifiesto de `main` ahora declara `tzdata>=2024.1` en ambos extras sin marcador Windows; **la instalación base sigue con `dependencies=[]`**. Se verificaron contenidos del manifiesto en GitHub. **No** se hizo una instalación limpia de extras ni se repitió QEMU o el full pytest. [C07 resultado](C07_RESULT.json).

## Estado y STOP_R5

MAIN20B: **7 válidos, 0 inválidos, 13 autorizaciones disponibles**; C01–C05 no cambiaron. Atlas al último lote `0062`: recuentos **documentales** 63 nodos, 81 relaciones, 228 runs, 48 incidencias, 403 operaciones. **Checker canónico 62 NOT_RUN**, SHA canónico desconocido. T008 histórica **COMPLETADA_VERIFICADA solo en b0344d1**; nueva [T009](../tareas_codex/T009_MAIN_LINUX_ATLAS60.md) **PENDIENTE para main HEAD actual y 62 lotes**, debe verificar instalación limpia y tests nuevos.

CT2 identidad sigue 29/100 ordinal, V4 36,90 % contractual, VSDS 1/3, nuevos N1/N2/N3 = 0/0/0, gates superados 0/6. No habilitar perfiles/puntuación de políticos reales ni CI costosa.

**Decisión R5:** no gastar los 13 restantes en releer el mismo informe histórico, reconfirmar el mismo blob ni simular repetidamente el mismo error de `tzdata`; un siguiente ciclo requiere mecanismo nuevo, evidencia institucional original o ejecución completa actual con control independiente. La autorización continúa abierta.
