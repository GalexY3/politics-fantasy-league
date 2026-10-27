# Alcance del almacén privado de ingesta · 27/10/2026

**No confundir el importador experimental con la demo del juego.** `run_demo.py` y `start_windows.bat` siguen siendo vías de demo sintética local y no dependen de `secure_store.py`. El capturador `python -m politics_fantasy.ingest` sí depende ahora de primitivas POSIX.

## Estado y limitación de Windows

Desde IC04, el almacenamiento de originales emplea aperturas con descriptor de directorio (`dir_fd`) y `O_NOFOLLOW`, creadas con permisos privados y objetos enlazados atómicamente por nombre SHA-256. Es una protección frente a enlaces simbólicos preexistentes en los directorios del almacén y la escritura de manifest/review fuera de `root` **en Linux/POSIX**.

**En Windows nativo el importador rechazará `SECURE_STORE_UNSUPPORTED_PLATFORM` antes de solicitar una fuente.** No debe sustituirse por un `Path.resolve()` aislado o por un `open()` normal: con un proceso no confiable concurrente, esas comprobaciones tienen ventana TOCTOU y la ruta podría redirigirse después de ser verificada. Tampoco se considera segura una prueba simulada de `os.name='nt'`: únicamente confirma rechazo anticipado en Linux, no un almacén Windows funcional.

### Trabajo local desde Windows, sin Codex obligatorio

- Para **jugar y probar la demo sintética** utiliza `start_windows.bat`, sin cambios.
- Para **la ingesta privada experimental**, utiliza una distribución Linux/WSL2 ya instalada y autorizada, con los ficheros y `root` dentro del sistema de archivos POSIX de WSL2, idealmente un directorio nuevo que posea el usuario (`0700`). No guardar originales nominativos en Git, Windows `C:\` ni carpetas compartidas sin auditoría adicional de permisos.
- Si no está disponible Linux/WSL2, **no se ejecuta la ingesta desde Windows nativo**; no se degradan las garantías silenciosamente. Una implementación Win32 segura con handles, reparse-point protections y pruebas sobre Windows real sería una línea futura independiente.

El directorio raíz y sus padres deben estar bajo control del operador. Los ficheros privados previos con permisos amplios se **rechazan**, no se modifica el modo de esos archivos automáticamente. La existencia de un objeto en el almacén no certifica autoría, términos de reutilización ni `first_public_at`.

Las pruebas de IC09 verifican que un sistema marcado como no compatible se rechaza **antes de llamar al opener**. No demuestran que la implementación POSIX sea portable ni que la aplicación completa esté lista para producción.

**Invariantes:** V4 36,90 %, CT2 identidad 29/100, VSDS 1/3, gates 0/6. `NO VOTAN` pendiente de semántica institucional.
