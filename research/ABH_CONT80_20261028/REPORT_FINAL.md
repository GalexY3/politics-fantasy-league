# Politics Fantasy League · AB-H C61–C68 · STOP_R5

**28/10/2026. Autorización: máximo 20 ciclos C61–C80. Ejecutados 8 ciclos completos A–J; 12 plazas no utilizadas.** Esta campaña se detiene por R5: después de resolver una colisión real de referencias institucionales, no hay un original adicional ni un instrumento independiente que justifique fabricar doce variaciones. **No se declara C69–C80 ejecutado.** [Estado](CAMPAIGN_STATUS.json) · [prerregistro](CAMPAIGN_PREREG.json) · [Atlas 0029](../../ab_atlas/updates/0029-pfl-abh-cont80-c61-c68-20261028.json).

## Hallazgos y trabajo realizado

| Ciclo | Modo | Resultado verificable |
|---|---|---|
| C61 | AB-R | Se reconcilió C55 con el perfil original RC01: Interior Congreso cargos electos ya tenía captura exploratoria **27/10/2026, 326.847 bytes, SHA256 `cafc4e0f3fc53f01d1370dd47ac841c6cad43a5394e8a8d1afe2495897fbdad4`, 5.600 filas, 16 elecciones**. No hubo nueva descarga en C61 ni identificación de personas. [Errata](C61_ERRATA_ORIGINAL_INTERIOR.md). |
| C62 | AB-R | El Senado distingue la abstención expresada del hecho de estar presente sin votar; el literal concreto del **XML nominal `NO VOTAN` sigue sin esquema original contrastado**. [Diccionario Senado](https://www.senado.es/web/diccionarioterminosparlamentarios/index.html?lang=es). |
| C63 | AB-R | Separadas fecha de actualización del conjunto Interior **21/08/2026**, fin de cobertura **11/03/2026**, fecha de otra distribución y **`first_public_at` del XLSX de cargos electos: desconocido**. [Recibo temporal](C63_TEMPORAL_PROVENANCE.md). |
| C64 | AB-P | Publicado [recibo de versión estructurado](../../data/observatory/interior_congreso_source_version_receipt_20261028.json) sin datos personales, con `first_public_at=null`. Archivo SHA Git `ead2b8b60405dc9a165cb8dd2e354f71a7b631e0`; longitud y digest de captura anterior coinciden con RC01. |
| C65 | AB-R | El conjunto [Paridad Electoral](https://datos.gob.es/es/catalogo/e00003801-paridad-electoral-candidatos-as-y-cargos-electos.xml) es distinto de «Resultados Electorales». [LOREG art. 44 bis](https://www.boe.es/eli/es/lo/1985/06/19/5/con): cambio normativo de representación equilibrada a alternancia tras LO 2/2024, aplicable atendiendo a la **convocatoria electoral**, no solo al año de una fila. No se extrapola licencia entre conjuntos. [Memoria](C65_NORMAS_PARIDAD.md). |
| **C66** | **AB-R** | **Hallazgo discriminante:** `ESE/000002-01` está reutilizado entre BOCCL **XI 2022 (CVE BOCCL-11-000084)** y **XII 2026 (CVE BOCCL-12-000986)**. No es un ID global de original. Documentos primarios: [BOCCL XI PDF](https://sirdoc.ccyl.es/SIRDOC/PDF/PUBLOFI/BO/CCL/11L/BOCCL1100013A.pdf) y [BOCCL XII HTML](https://www.ccyl.es/Publicaciones/TextoEntradaBOCCL?Fichero=%5C%5CSIRDOCfiles%5Csirdoc%24%5CXML%5CEBOCCL%5C12L%5CBOCCL1200032%5CBOCCL-12-000986.xml). No se insertaron nombres particulares en Git. |
| **C67** | **AB-P** | Corregido `source_event_registry.py`: claves **`CCYL:BOCCL-12-000986`** y **`CCYL:BOCCL-12-001042`**, referencia abreviada solo descriptiva, código antiguo denegado con `AMBIGUOUS_UNQUALIFIED_ESE_REF`, fecha de primera publicación aún nula. Inicialmente, **cinco fallos por cambio deliberado de contrato**; tras migrar explícitamente tests originales, **28/28 pytest nativos PASS (0,07 s)** en fuente y tests con SHA Git idéntico. No se levantaron gates. |
| C68 | AB-P | Lectura real de servidor, interfaz y test HTTP existente: el servidor devuelve catálogo dinámico y no se encontraron abreviaturas antiguas en los archivos inspeccionados. **No se ejecutaron pruebas HTTP ni suite íntegra**; se añadió [Codex T006](../../tareas_codex/T006_CVE_CROSS_LEGISLATURE.md) para resolverlo. |

Los ocho `C61_RESULT.json`–`C68_RESULT.json` contienen A–J. Parte de las búsquedas web exploratorias de C62/C65/C66 precedió a su prerregistro Git; consta en los resultados, sin afirmar congelación previa. Las lecturas de originales y la ejecución de pruebas son tipos de evidencia distintos; ningún registro de un ciclo puede usarse como prueba de otro.

## Límites, autocrítica y Atlas

El registro fuente BOCCL tiene **colisión de identificador corto demostrada**, pero no se ha certificado una identidad personal ni la primera publicación exacta de los originales. El código en C67 resuelve la ambigüedad del *lookup* local; es un **cambio de contrato**, por lo que la migración de fixtures no debe confundirse con confirmación independiente de toda la aplicación. Falta el HTTP real y el rastreo exhaustivo de clientes.

AB Atlas: añadido append-only `0029-PFL-ABH-CONT80-C61-C68-20261028` con **8 `run.add`**, sin cambios de gates. Totales **derivados**: **29 lotes, 63 nodos, 81 aristas, 187 ejecuciones, 44 incidencias, 356 operaciones**. `python ab_atlas/atlas_delta.py check` canónico **NO EJECUTADO**; SHA de estado desconocido.

Métricas **sin promoción**: V4 contractual **36,90 %**; CT2 identidad **29/100 ordinal**; VSDS **1/3**; N1/N2/N3 científicos nuevos **0/0/0**; gates de lanzamiento **0/6**. No datos nominativos en Git, no scoring de figuras reales, no CI costosa ni merge a `main`.

**Codex sigue pendiente**, nunca ejecutado en esta campaña. La carpeta [tareas_codex](../../tareas_codex/README.md) contiene T001 (Atlas), T002 (suites completas), y nueva T006 (HTTP e inventario de referencias XI/XII). La ejecución requiere disponibilidad de Codex y acción del usuario.

**Decisión final STOP_R5:** **8/20 ejecutados, 12 no consumidos.** Reanudar solo si se consigue un original institucional nuevo, se dispone de checkout para pruebas integrales o se plantea otra prueba que discrimine una hipótesis real. **No se solicitan más ciclos** mientras quede autorización sin utilizar.
