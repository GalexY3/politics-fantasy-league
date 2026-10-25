# Verificación de enlaces públicos (24-10-2026), sin certificado de descarga nominal

Fuente 1: Página de datos abiertos **Votaciones**, Congreso, `https://www.congreso.es/es/opendata/votaciones`. La pantalla consultada mediante servicio de lectura web permite listar una sesión del 23 de julio de 2026 con veinte recuentos y enlaces separados al detalle XML y JSON. Ejemplo del enlace JSON anunciado para una votación: `https://www.congreso.es/webpublica/opendata/votaciones/Leg15/Sesion193/20260723/Votacion001/VOT_20260723211929.json`. **El cuerpo no se descargó/validó localmente, y su estructura no se ha certificado**. Al intentar usar el entorno Python, la resolución DNS hacia el host es inaccesible; las URL de detalle son evidencia de enlace, NO de schema ni de disponibilidad as-of.

Fuente 2: Congreso, `https://www.congreso.es/es/opendata/intervenciones`. Ofrece intervenciones por tipo de iniciativa y por orden cronológico, cada una en CSV/JSON/XML. No se han obtenido bytes y no se certifica parseo.

Fuente 3: Congreso, `https://www.congreso.es/es/web/guest/opendata/diputados`. Ofrece listados de diputadas/diputados en activo y en anteriores legislaturas. Es candidato a normalización de identidades y mandatos; falta auditoría sobre atributos y fechas de cambios.

Fuente 4: AEBOE, `https://www.boe.es/datosabiertos/api/api.php?lang=es`. La documentación describe `GET /datosabiertos/api/boe/sumario/{fecha}` en `AAAAMMDD` con respuestas JSON/XML, junto a recursos de legislación consolidada. No se ha hecho descarga local ni validación de semántica o licencia por documento. No equiparar actividad legislativa BOE a actividad individual de un diputado.

**Riesgos pendientes:** licencia/atribución y última modificación de cada recurso; IDs nominales y cambios de mandato; captura de `first_public_at` no inferible a partir de la fecha del acto; duplicación de votaciones dentro de un mismo expediente; representatividad temporal; ausencia no observada. Se evita toda afirmación causal y toda etiqueta de absentismo a partir de 350 menos recuentos.
