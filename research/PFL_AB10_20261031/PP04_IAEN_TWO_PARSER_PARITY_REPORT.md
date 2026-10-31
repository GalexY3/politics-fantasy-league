# PP04 · Auditoría portátil de dos segmentadores IAEN, fuera de ciclo AB

31/10/2026. Resultado NONCYCLE de ingeniería de calidad de fuente, no una cuarta ejecución AB-P ni una admisión AB-R. Código: scripts/pp04_iaen_crossparser_private.py y cinco pruebas sintéticas tests/test_pp04_iaen_crossparser_private.py. Las ejecuciones originales siguen almacenadas únicamente en el ordenador fuera de Git.

## Alcance, origen y control de bytes

Se reutilizan exactamente dos derivados de IAEN2024 ya autorizados: PR #11, su listado de iniciativas previstas (SHA256 0a46761441426183f08c86a1ba334640b8c402c059b777eb34cf2de8f571696b), y PR #12, listado de iniciativas previstas/no previstas (SHA256 db21a56f8ad69f3466f5a08799dd6b903d1c6de3afa2a1384cbca364e9e55131). Ambos proceden del **mismo PDF oficial IAEN2024**, no son observaciones institucionales independientes. El script exige hashes exactos, nombre de fichero, límites de tamaño, salida offGit y cero sobreescrituras.

## Resultado estructural y falsador localizado

| Atributo comparado para las 198 entradas previstas | Concordancia |
| --- | ---: |
| Ordinal fuente-local | 198/198 |
| Página física PDF | 198/198 |
| Número de subsección ministerial | 198/198 |
| Estado grueso aprobado/pendiente del IAEN | 198/198 |
| Primeras cuatro palabras normalizadas del candidato textual | **197/198** |

El segundo parser conserva además **259 entradas clasificadas como no previstas** fuera de esa cohorte. Existe **una discrepancia de extracción** del inicio de título: **ordinal fuente-local 79, página PDF 58, subsección ministerial 12**, con todos los demás atributos concordantes. La lectura privada focal muestra que la versión de PR #11 arrastra texto descriptivo y elementos de maquetación posteriores al título mientras PR #12 conserva el encabezado de viñeta de primera línea. No es evidencia suficiente para afirmar dos iniciativas jurídicas distintas: es un aviso de calidad de campo/texto y exige cotejo de maquetación antes de tratar el título completo como limpio. No se publica texto de caso ni resultado de disposición.

El recibo JSON detallado sin títulos permanece fuera de Git en PFL-AB10-PRIVATE-20261031/PP04_IAEN_PARITY_PORTABLE_V1 con SHA256 **693036282eb9a3fe2676905259e9c9f442b2f5aca0876927bd52038dc568fbf0**. Un primer contraste independiente de implementación con las mismas derivadas y un formato de recibo distinto produjo 198/198 páginas, secciones, estado y 197/198 primeras cuatro palabras. El nuevo script portable produjo el mismo patrón. Son **dos pruebas de dos extracciones del mismo activo**, no una tercera fuente oficial ni un censo independiente de 198.

## Límites y siguiente decisión

Concordancia interna de campos no certifica identidad PAN→IAEN, estado detallado de las 109 pendientes, aprobación a 31/12/2024, first_public_at, completitud all-received ni reutilización de datos individuales. Ningún vínculo normativo real se añade al observatorio, ningún PDF/JSONL original se distribuye y R5 sigue STOP. Se mantiene el presupuesto AB10 de **3 AB-P ejecutados / 7 pendientes** sin cargo por esta QA. Próximo paso material: cotejo visual privado de la entrada 79 en el documento original autorizado y reconciliación de las APIs de PR11/PR12 antes de cualquier integración, con pruebas de regresión para texto de rótulos concatenado.
