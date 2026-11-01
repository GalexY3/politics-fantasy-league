# R27 · Córdoba: avisos, incidencias, quejas y reclamaciones municipales (PREACCESO)

**1 de noviembre de 2026 · revisión documental externa preliminar · NONCYCLE.**
La fuente se propone como **nueva candidata territorial**, no como corpus
admitido. Este documento no incorpora datos originales, personas, registros,
desenlaces, capturas, ficheros de distribución ni derechos adquiridos. No se
consultaron URL de CSV, XLSX, JSON o XML; tampoco se aceptaron términos o
cookies ni se intentaron accesos a endpoints bloqueados.

## Procedencia exacta de la observación

La búsqueda se limitó a resultados indexados y metadatos visibles en el
**catálogo nacional datos.gob.es**, antes de acceder a las distribuciones del
portal editor. Como contraste de la familia editorial se utilizó solo una
ficha indexada de un conjunto hermano, no sus datos. Estos testigos no son
independientes del proceso de catalogación ni autentican los bytes publicados.

| Catálogo público / identificador visible | Afirmación documental, NO auditada en original |
| --- | --- |
| `https://datos.gob.es/es/catalogo/l01140174-avisos-incidencias-quejas-sugerencias-y-reclamaciones` | Ayuntamiento de **La Carlota**, serie descrita como comunicaciones dirigidas al ayuntamiento, formatos CSV/JSON/XLSX/XML. El catálogo indica cobertura desde 2021-12-31 23:00 UTC, frecuencia mensual y un timestamp de alta/actualización del catálogo en 2026-01-01. |
| `https://datos.gob.es/es/catalogo/l01140673-avisos-incidencias-quejas-sugerencias-y-reclamaciones1` | Ayuntamiento de **Villafranca de Córdoba**, nombre y esquema de publicación comparables pero otra administración local. Cuatro distribuciones anunciadas. |
| `https://eprinsa-opendata.e-admin.es/dataset/avisos-incidencias-quejas-sugerencias-y-reclamaciones138` | Ficha indexada del conjunto **diferente** de Encinas Reales en el mismo ecosistema editorial EPRINSA: aparece CC BY-SA 4.0 en esa ficha. **No** es prueba de licencia aplicable a La Carlota ni a Villafranca. |

El catálogo nacional presenta para los conjuntos de La Carlota y Villafranca
una cadena de licencia con estructura anómala:
`http://creativecommons.org/licenses/by-nc/2.0/cc-by-sa-4.0`.
No se ha autenticado que esa cadena resuelva a una licencia vigente válida,
ni que prevalezca sobre términos específicos del portal o del recurso; **no
debe interpretarse como una concesión**. Un catálogo hermano que declara
CC BY-SA 4.0 demuestra heterogeneidad de señales, no un conflicto de licencias
probado para el mismo activo. La finalidad académica local y una eventual
redistribución/publicación tienen que adjudicarse separadamente.

## Pregunta diferenciada y tres rutas rivales

**A: población inicial local.** Si el conjunto recoge efectivamente todos los
avisos y comunicaciones recibidos antes de su clasificación, podría ofrecer
una unidad `entrada × entidad × fecha` acotada por municipio y canal. Falsador:
exclusión de presentaciones presenciales, quejas inadmitidas, entradas fuera de
un sistema específico o una extracción solo de expedientes visibles.

**B: artefacto editorial seleccionado.** El título agrupa avisos, incidencias,
quejas, sugerencias y reclamaciones, cuyas reglas de admisión, duplicados y
competencias podrían ser distintas. Falsador de la hipótesis A: una tabla sin
identificador estable de recepción y sin definición de `all-received`.

**C: heterogeneidad territorial.** La Carlota y Villafranca son autoridades
administrativas distintas, pero comparten un ecosistema técnico de
publicación. Falsador: cambios de cobertura y campos, categorías homónimas
incompatibles o un censo derivado del mismo índice editorial. **No** suponer
dos mediciones independientes de un mismo universo por compartir formato.

## Barreras de promoción y criterio de STOP

En la evidencia actual **NO** constan: términos de acceso adjudicados por
distribución, SHA de originales, padrón externo de entradas, definiciones
auténticas de captación por canal, tratamiento de rechazos, pendientes y
censura, unión `asiento→resolución`, reglas territoriales comparables, dos
vintages históricas autenticadas ni `first_public_at` por versión o caso.
La cobertura temporal del catálogo no es evidencia de primera disponibilidad
pública de una edición. Tampoco se conoce si la serie se diseñó para
evaluación sociopolítica, resolución de incidencias técnicas o ambas.

**Decisión:** `NEW_CATALOG_LEAD_STOP_LOCAL_R5`. No aporta aún un corpus
admisible ni justifica descargar distribuciones. Para reabrir deben aparecer,
mediante documentación lícita y revisión humana, la licencia/condiciones
específicas, documentación de esquema y censo de recepción independientes,
con reglas de negativos y versiones. Si no aparecen, aparcar sin repetir
búsquedas equivalentes. **0 AB, 0 fuentes reales admitidas, R5 STOP.**

## Control de no duplicación

Búsqueda textual sobre la rama protegida y la rama de PR #19 en `src`, `tests`,
`research`, `docs` y `data`: sin coincidencias para `eprinsa`, `La Carlota`
ni el identificador literal `41ac6ba6`. Esto acredita únicamente que esas
cadenas no constaban en los archivos inspeccionados, no novedad científica
frente a la literatura o todos los repositorios.

Rutas descartadas por historia previa: Madrid 300517 y 300594 ya en R11;
Madrid 300044 ya en R26, con 403 y condiciones por mero uso. No se reabrieron.
