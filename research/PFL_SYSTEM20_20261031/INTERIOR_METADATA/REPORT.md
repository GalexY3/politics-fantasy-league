# Informe exploratorio de cobertura de metadatos (31 de octubre de 2026)

**Estado:** FASE1 y FASE2 ejecutadas localmente; pruebas 14/14 OK; código congelado y hashes verificados después de la agregación. Investigación exploratoria de procedencia y calidad, sin resultados de contraste AB-H.

## Fuentes y verificaciones

| Original conservado por el usuario | Bytes originales | SHA-256 verificado | Hoja | Dimensión declarada |
| --- | ---: | --- | --- | --- |
| `Elecciones-Congreso-cargos-electos.xlsx` | 326.847 | `cafc4e0f3fc53f01d1370dd47ac841c6cad43a5394e8a8d1afe2495897fbdad4` | Congreso cargos electos | `A1:H5604` |
| `Elecciones-Congreso.xlsx` | 1.151.199 | `dba3394f1812f338067231bce68acf56af1e13ddf8cfb709a814bcc46357ebc2` | Congreso | `A1:BE6207` |

El paquete tiene 13 entradas ZIP en cada archivo y el XML principal de hoja ocupa 2.682.915 y 13.971.061 bytes descomprimidos, respectivamente. Se usó la documentación original de procedencia en `PFL-trabajo/data/source_manifests/interior_congreso_20261031.json` **solo lectura**; SHA del manifiesto `ce5172fe9e8a7f3b8bd97c6bc9b7c51218aa623f72a58de37cf6ed31315cefea`. La FASE1 identificó la fila 4 como encabezado real después de una fila vacía y dos filas de título. Hay 8 y 57 columnas encabezadas, respectivamente. El segundo fichero contiene 52 encabezados de provincias y una columna de escaños nacionales, ninguna de ellas procesada en la fase agregada.

## Cobertura de campos autorizados

| Archivo | Filas de datos leídas | Años presentes | Filas con año identificable | Missing en columnas permitidas | Repeticiones de clave parcial |
| --- | ---: | --- | ---: | ---: | --- |
| Cargos electos | 5.600 | 1977–2023, 15 años electorales diferentes | 5.600 | 0 en A–E | 4.768 de 5.600 filas comparten clave fecha/código elección/provincia con otra fila |
| Resultados Congreso | 6.203 | 1977–2023, 15 años electorales diferentes | 6.203 | 0 en A–C | **No estimable** sin disponer de una clave natural ajena a outcomes |

Los años documentados son 1977, 1979, 1982, 1986, 1989, 1993, 1996, 2000, 2004, 2008, 2011, 2015, 2016, 2019 y 2023. El archivo de cargos presenta 832 claves distintas de fecha/código elección/provincia, con 0 claves incompletas. **Esas 4.768 colisiones no son registros duplicados**: las claves de fecha/territorio son deliberadamente compartidas por distintas candidaturas y observaciones de un mismo proceso. La granularidad completa no puede comprobarse sin datos excluidos por esta tarea. De la misma manera, no se puede afirmar que ambos ficheros contengan todos los procesos electorales ni que cada fila corresponda a una unidad comparable. El año 2019 concentra más filas del primer archivo; esto por sí mismo no prueba ningún resultado político.

El inventario exhaustivo de frecuencias **de filas** por año, separado por archivo y sin otra variable, se conserva en `runs/2026-10-31/phase2.json`. Los recuentos allí no son votos, escaños, efectos institucionales ni probabilidades de aprobación. No se han producido distribuciones por candidato, partido o provincia, ni datos personales.

## Fechas, derechos y límites

Los originales se capturaron anteriormente el 31-10-2026, según el manifiesto, mediante dos GET HTTPS públicos del Ministerio del Interior. Esta tarea realizó **0 nuevas solicitudes de red**. El manifiesto recoge `Last-Modified: Fri, 26 Jun 2026 05:50:13 GMT` para cargos electos y `Fri, 26 Jun 2026 05:50:08 GMT` para resultados: fechas de revisión del servidor que no permiten inferir el instante histórico de primera disponibilidad de cada fila. `first_public_at=null` continúa siendo el estado correcto. Tampoco se ha certificado versionado histórico de los XLSX, coherencia con actas electorales originales ni población de riesgo de iniciativas del Congreso.

El catálogo oficial vinculado por el manifiesto es [Resultados electorales, datos.gob.es](https://datos.gob.es/es/catalogo/e00003801-resultados-electorales), con referencia [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/deed.es). Toda reutilización posterior deberá citar fuente y licencia e indicar las transformaciones, y revisar separadamente derechos de datos personales y límites de finalidad. El código solo produjo informes agregados y no exportó filas.

## Evidencia de orden y congelación

En `runs/2026-10-31/` constan tres comprobaciones iniciales de posición de cabeceras, la FASE1 final (`phase1_final.json`, SHA-256 `d19878f709adf1273aa215e9c468c7865ac55ee902327f13a68c438142fa2252`), recibo de tests, congelación y FASE2 (`phase2.json`, SHA-256 `e2128f79c6bb06ca51953d99746a5c0267fcb5fc89f4a119356fa2c344d04207`). Congelación del lector: `7f773959121dc0e039a71fb90ca5be08e54c6e4c0c252a017bf638013ed71f8b`; tests: `35d681e6100e21c6562f846e6ff3836d23622115ffc6eb967afe09ac7c5f618a`. La política de metadatos A–E/A–C tiene SHA-256 `bfb0548942cf0f6f03336d0a4eb86c0d7408118bb9594abbe4975217b2e7e929`. Se releyeron hashes de los scripts después de ejecutar la FASE2 y coincidieron con los de la congelación.

**Siguiente dependencia para otro estudio:** obtener definiciones oficiales de unidad de registro, diccionario de campos, versiones históricas y una población de riesgo de iniciativas congresuales independiente de estas estadísticas de resultados electorales. Estos archivos son fuentes contextuales electorales; no sirven para decidir quién inicia o supera trámites parlamentarios sin un diseño específico, preregistrado y una unión temporal validada.
