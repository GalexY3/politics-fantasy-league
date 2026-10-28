# Corrección de alcance C61 — captura anterior del XLSX del Interior

**Fecha: 28/10/2026.** C55 (CONT60) confirma condiciones de licencia `CC_BY_4_0` en el catálogo «Resultados Electorales» y señala «No XLSX descargado». Debe leerse estrictamente «no se descargó *en C55*», **no** «jamás hubo captura ni auditoría».

**Evidencia anterior**: [`docs/CATALOGO_FUENTES.md`](../../docs/CATALOGO_FUENTES.md), apartado 1, y [`RC01_PROFILE.json`](../ABH_RECON_20261027/RC01_PROFILE.json): captura local exploratoria del 27/10/2026 de `Elecciones-Congreso-cargos-electos.xlsx`, **326.847 bytes**, SHA-256 `cafc4e0f3fc53f01d1370dd47ac841c6cad43a5394e8a8d1afe2495897fbdad4`, una hoja, ocho cabeceras, **5.600 filas** distribuidas en 16 fechas de elección (350/fecha). El perfil se creó exploratoriamente **antes** del prerregistro; no es muestra ciega ni auditoría exhaustiva de nombres o identidades. [Script de perfil](../../scripts/audit_interior_elected_20261027.py).

**No obtenido/verificado en C61:** el fichero binario original directamente accesible en este contenedor, reproducibilidad actual del hash, firma del editor, momento real de primera publicación de cada versión, correspondencia de nombres entre elecciones, adquisición de escaño, inscripción RPP o licitud de puntuaciones individuales.

**Consecuencia:** mantener `CC BY 4.0` acotada a las distribuciones identificadas; usar el perfil RC01 como historial documentado, solicitar original o reconstrucción solo si una pregunta precisa necesita sus bytes. Gates 0/6, CT2 29/100 y V4 36,90% sin elevar. No reescribir C55 retroactivamente; esta errata deja constancia versionada.
