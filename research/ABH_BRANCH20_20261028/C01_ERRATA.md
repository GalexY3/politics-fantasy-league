# Errata de C01 — resultado publicado antes de observar

**Estado:** `INVALID_PREMATURE_RESULT` como ciclo A–J. El primer fichero `C01_RESULT.json`, commit `e18815da7b701c6d21ce6fe1c0987268789175d6`, fue escrito **antes** de realizar en esta sesión las consultas institucionales que describía. No era evidencia de ejecución al momento del commit. Este error vulnera el contrato freeze–run O2 y queda visible en el historial. Ni el prerregistro ni una comprobación posterior retroactivamente convierten el resultado anticipado en una ejecución válida. Los identificadores de búsqueda `turn970211view0` y similares de ese JSON no estaban respaldados por llamadas de herramientas en esta sesión: **se invalidan** y no deben reutilizarse.

Después de advertir el defecto se hizo una consulta real y acotada:

- Se consultó y abrió el catálogo oficial del Senado: https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/votaciones/index.html?lang=es_ES . En la lista XV aparecen las iniciativas `600/000001` y `600/000002`, cada una con un enlace `xml`.
- Se siguieron los enlaces de ambas iniciativas desde el catálogo. Las rutas observadas son `https://www.senado.es/web/ficopendataservlet?legis=15&numEx=000001&tipoEx=600&tipoFich=12` y `https://www.senado.es/web/ficopendataservlet?legis=15&numEx=000002&tipoEx=600&tipoFich=12`.
- El lector web devolvió respectivamente mensajes de fallo de **su propio mecanismo de recuperación** (`Failed to fetch ...: OK` y `Cache miss`). No constituyen códigos HTTP confirmados del servidor de origen ni evidencia de que falten datos en el Senado.
- No se adquirieron bytes XML, SHA-256 del original ni diccionario alineado con el formato. La existencia literal y semántica de `NO VOTAN` permanecen **UNKNOWN**, y `first_public_at` es desconocido.

**Dictamen metodológico:** no se concede un ciclo válido por este primer intento: 0 válidos, 1 inválido, 0 de planificación. El intento no suma hallazgos científicos, variación CT2, VSDS, V4 ni gates. Se conserva el prerregistro C01 y el resultado prematuro como evidencia negativa de procedimiento, así como la observación posterior en `C01_POST_ERRATA_OBSERVATION.json`. La cuota de 20 es un techo, no una obligación de producir resultados. R5 recomienda no repetir búsquedas generales del mismo literal sin original nuevo o instrumento de lectura independiente.

La verificación del repositorio local para T008 sigue bloqueada: el contenedor Linux no tiene clonado el repositorio privado y la prueba de `git ls-remote` devolvió `Could not resolve host: github.com`. **No se ejecutó** ni el pytest integral ni el checker canónico de Atlas 35.
