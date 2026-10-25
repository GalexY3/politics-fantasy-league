# Fuentes, procedencia y obligaciones de reutilización

Fecha de inspección documental: 24-10-2026. **Sólo disponibilidad de portales verificada**; no consta prueba reproducible de descarga y normalización integral ni licencia final validada para cada archivo.

| Nivel | Fuente primaria | Datos anunciados | Formatos documentados | Enlace | Estado |
|---|---|---|---|---|---|
| 1 | Congreso — votaciones | Resultados de votación y detalle nominal | XML, JSON y ZIP por sesión | https://www.congreso.es/es/opendata/votaciones | Página y enlaces verificados |
| 1 | Congreso — intervenciones | Intervenciones por iniciativa y cronología | CSV, JSON, XML | https://www.congreso.es/es/opendata/intervenciones | Página y enlaces verificados |
| 1 | Congreso — diputados | Composición parlamentaria | Portal de datos abiertos | https://www.congreso.es/es/opendata/diputados | Página verificada, campos por inspeccionar |
| 1 | Congreso — iniciativas | Expedientes/tramitación | Portal de datos abiertos | https://www.congreso.es/es/opendata/iniciativas | Página verificada, campos por inspeccionar |
| 1 | Senado | Pleno, comisiones, iniciativas, votaciones, senadores | Portal de datos abiertos | https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/index.html?lang=es_ES | Catálogo verificado |
| 1 | AEBOE | Sumario, normas consolidadas y metadatos | API documentada | https://www.boe.es/datosabiertos/api/api.php?lang=es | Documentación verificada |
| 2 | Ministerio de Hacienda | Contrataciones y licitaciones | Datos abiertos, esquema por verificar | https://www.hacienda.gob.es/gl-ES/GobiernoAbierto/Datos%20Abiertos/Paginas/licitaciones_plataforma_contratacion.aspx | Página verificada; **no inferir atribución a ministro** |
| 2 | Agenda Gobierno | Actividad y calendarios | Catálogo por verificar | https://servicios-mpr.sede.gob.es/pagina/index/directorio/catalogo_datos_abiertos/language/es_ES | Catálogo verificado |
| 3 | El Congreso en tu mano | Datos consolidados cívicos / API pública | API publicada, terceros | https://elcongresoentumano.es/api | Documentación localizada; no sustituye fuente primaria |

**Observación técnica puntual:** el catálogo oficial contiene enlaces individuales a JSON de votaciones; ejemplo publicado por Congreso en julio de 2026: `https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion001/VOT_20260723211929.json`. URL encontrada como enlace real, pero contenido no inspeccionado/normalizado en este paquete: **NO_DATA_DOWNLOADED**. No generalizar el patrón de URL para fabricar URLs.

## Control de fuentes requerido antes de ingesta a volumen

1. Inspección humana de condiciones de reutilización, licencia, restricciones de caché, datos personales, `robots.txt`, rate limits y cambios de esquema **por fuente**.
2. Registrar `source_id`, recurso exacto, fecha observada, fecha de recuperación, respuesta HTTP, ETag, Last-Modified, SHA-256 y versión del parser. Guardar originales en almacenamiento inmutable y una capa normalizada separada.
3. Confirmar si la información histórica describe el momento del evento o es una corrección retroactiva: guardar ambos relojes.
4. Registrar cobertura: fechas, cámaras, % de eventos con documento, % de intervenciones con autor resuelto, cambios institucionales, duplicados y distribución de retrasos de publicación.
5. **No extraer afiliaciones o preferencias políticas de usuarios del fantasy.** La adscripción institucional pública de cargos para seguimiento de funciones tiene régimen diferente de perfilar creencias de particulares.

## Riesgos específicos de los datos

- Fuente oficial ≠ muestra exhaustiva de actividad política: actos no parlamentarios, negociación informal, entidades locales y trabajo ejecutivo pueden quedar fuera.
- El Congreso/BOE pueden publicar información después de que ocurra el hecho. Nunca reconstruir pronósticos históricos con una corrección cuya primera disponibilidad pública es posterior al corte.
- Ausencia de intervención en un canal no equivale a inactividad política.
- Parlamento y Gobierno tienen sesgos estructurales de oportunidad medibles, por lo que toda puntuación o comparación deberá detallar universo elegible y exposición.
- Un mismo expediente contiene tramitaciones y votaciones diferentes; deduplicar por identificador de **evento** y preservar expediente y ronda de decisión.

## Fuentes jurídicas públicas

AEPD, categorías especiales: https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0215-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-las-categorias-especiales-de-datos  
DGOJ, elementos concurrentes de actividades reguladas: https://www.ordenacionjuego.es/en/node/2722

Este inventario NO concede licencia por sí mismo ni certifica que los endpoints soporten scraping intensivo.