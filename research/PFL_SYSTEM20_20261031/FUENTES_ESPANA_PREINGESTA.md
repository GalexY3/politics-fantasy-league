# Auditoría de factibilidad de fuentes españolas, sin ingestión de outcomes

**Fecha:** 2026-10-31. **Modo:** exploración documental, **0 ciclos AB-H**. No hay aquí ninguna evaluación confirmatoria ni corpus prospectivo. Las fichas y documentación consultadas en las herramientas no certifican un dataset de todas las iniciativas o normas. No se han aceptado licencias ni depositado originales de terceros en Git.

## Tres rutas sustantivamente distintas

### I. Congreso: procesos de iniciativas e intervenciones

**Oficial:** https://www.congreso.es/es/datos-abiertos ; https://www.congreso.es/es/opendata/iniciativas ; https://www.congreso.es/es/opendata/intervenciones ; aviso legal https://www.congreso.es/es/cem/aviso-legal .

La vía es pertinente para observar reproducción de procedimientos, tramitación, cambios de fase y adaptación entre legislaturas. Un expediente exige clave compuesta de **legislatura, tipo y número**. Una ficha pública individual de ejemplo `184/015125` de la XV legislatura muestra fechas de presentación, calificación y publicación parlamentaria diferentes; eso no certifica la disponibilidad bitemporal individual del dataset completo. El acceso web automatizado al catálogo de iniciativas produjo HTTP 403 en una herramienta, mientras que una comprobación HEAD local de la ruta dio 200: **acceso estructurado todavía no verificado**. No declarar un CSV importable hasta obtenerlo y validar sus campos.

**Población requerida:** procesos presentados incluidos pendientes, retirados y caducados; no solo aprobados. **Amenazas:** selección por finalización, censura a disoluciones, filtración de estados finales y enlaces textuales injustificados al BOE. **Falsador:** no poder recuperar identificadores y transiciones en un marco de muestreo completo o no poder identificar su disponibilidad temporal.

### II. BOE: publicaciones normativas e institucionales

**Oficial:** https://www.boe.es/datosabiertos/api/api.php ; https://www.boe.es/datosabiertos/faq/boe.php ; https://www.boe.es/datosabiertos/faq/consolidada.php ; https://www.boe.es/boe/dias/2026/10/30/ ; condiciones https://www.boe.es/informacion/aviso_legal/index.php .

La agencia describe sumarios diarios desde septiembre de 1960 y API con enlaces a documentos en XML/HTML/PDF. En exploración documental, `GET/HEAD` de la API diaria `20261030` devolvió HTTP 500; la versión HTML del día funcionó. Una ficha pública individual `BOE-A-2026-22716` identifica una disposición de fecha 28/10 publicada 30/10. El identificador BOE-A y ELI son prometedores para el enlace, pero **fecha de disposición y fecha de primera publicación no son la misma variable**. La consolidación puede introducir modificaciones posteriores, por lo que no debe usarse como histórico as-of sin control.

**Ventaja:** fuente oficial y serie de publicaciones históricas, ruta HTML comprobada. **Población:** documentos publicados, con estratificación por sección, rango y organismo. **Límite decisivo:** el universo de normas publicadas no representa propuestas no aprobadas ni todas las demandas políticas; no puede usarse como si fuera un modelo completo del ciclo decisional. **Comparador futuro:** recuentos históricos estacionales por organismo, rango y calendario, fijando población y horizonte antes de outcomes.

**Condiciones:** el aviso legal describe una licencia-tipo de reutilización y atribución. La documentación dice expresamente que reutilizar información comporta condiciones: para esta fase se registra la situación, **no** se descargan corpus para redistribución ni se aceptan términos en nombre del promotor. La admisión y publicación de originales requerirá resolver este gate específico.

### III. Plataforma de Contratación del Sector Público: relaciones Estado-empresa

**Oficial:** https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/licitacionescontratante.aspx ; https://www.hacienda.gob.es/es-es/gobiernoabierto/datos%20abiertos/paginas/datosabiertos.aspx ; https://contrataciondelestado.es/datosabiertos/DGPE_PLACSP_OpenPLACSP_v.2.1.pdf .

La documentación oficial presenta ficheros históricos y sindicación con cobertura que cambia entre órganos y años. El identificador de licitación y la clave expediente+órgano deben distinguirse. Primera publicación, actualización, adjudicación y formalización son eventos diferentes; la primera publicación puede excluir anuncios previos o anulados según contrato técnico. Un archivo ZIP enlazado no se ingirió en esta auditoría; su accesibilidad de bytes, estructura, cobertura y licencia aplicada siguen pendientes.

**Población:** licitaciones de órganos/perfiles representados en la plataforma en el periodo seleccionado, no todas las compras de todas las administraciones españolas. **Amenazas:** cobertura territorial cambiante, lotes, actualizaciones repetidas, filtración de adjudicación posterior y confusión entre contrato y relación de influencia. **Comparador futuro:** historial por CPV/órgano/procedimiento y presupuesto disponible a la fecha de inicio, antes de outcomes.

## Comparación y siguiente resultado mínimo

La ruta BOE HTML parece la **más accesible para un primer adaptador técnico de publicación**; Congreso resulta conceptualmente más adecuado para estudiar la **reproducción decisional** porque incluye procesos que no desembocan en norma; PLACSP conecta con los acoplamientos económicos. Por tanto, se recomienda distinguir un **piloto de ingesta** de la **primera investigación TFM**. Una decisión de ingeniería no selecciona por sí sola el objeto teórico central.

**Próximo gate:** aprobar condiciones concretas de reutilización/almacenamiento por fuente, probar acceso de bytes y esquema en un rango pequeño, congelar un contrato de extracción y elaborar cobertura y ausencia. Para contraste AB-R: preregistrar A–J, identificación de población y código SHA antes de resultados. No abrir un ciclo por el mero hallazgo de una URL o por una prueba sintética.
