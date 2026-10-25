# Fuentes y ontología multiactor — PF-BR20H (25/10/2026)

**Propósito:** separar políticos con escaños de todo el universo documentable de **actores políticos públicos** sin reducirlo al eje izquierda/derecha ni asumir que visibilidad = influencia. Categorías y enlaces verificados como **referencias documentales**, NO corpus nacional importado.

## Modelo explícito de unidad analítica
1. PERSON: persona con **rol político público documentado**, no ciudadanos ordinarios ni afiliados privados.
2. PARTY y FEDERATION: organización jurídica, existencia registral no demuestra participación electoral.
3. COALITION y ELECTORS_GROUP: formas de presentación electoral diferentes de partidos (LOREG art. 44).
4. CANDIDACY y CAMPAIGN: entidad/evento de ciclo electoral distinto de escaño.
5. CIVIC_PLATFORM, CIVIL_ORG, UNION, THINK_TANK, MEDIA_ORG: organizaciones con actividad pública documentable, **sin clasificación ideológica ni atribución causal**.
6. PUBLIC_BODY: institución distinta de actor afiliado.
7. Rol público documentado: candidatura, portavocía, liderazgo público, representación/mandato, declaración programática atribuida, acto público y alianza temporal. No inferir membresía por aparecer en una lista de candidatos.
8. Unidad de observación separada: evento públicamente documentado. Una declaración, noticia, reunión o convocatoria no certifica influencia causal; no puntuar calidad o mérito de actores reales.

## Fuentes oficiales y estado de acceso
| ID | Referencia | Para qué sirve | Estado verificado |
|--|--|--|--|
| RPP | https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos | Formaciones registradas; búsqueda con filtros y PDF de resultados | DOCUMENTED_ONLY; sin descarga exhaustiva ni parser verificado |
| LOREG | https://www.juntaelectoralcentral.es/cs/jec/normativa/estatal?idContenido=2741462&idLeyJunta=1&idLeyModificacion=2740214&p=1379061506503&paux=1379061506503&template=Loreg%2FJEC_Contenido | Modalidades distintas de candidatura, Art.44 | DOCUMENTARY_LEGAL |
| MIN_INT_DATA | https://sede.interior.gob.es/portal/sede/informacion-general/catalogo-de-datos | Recursos XLSX de resultados y cargos electos por modalidad | DOCUMENTED_ONLY; sin normalización en proyecto |
| PARTIES_LAW | https://www.boe.es/eli/es/lo/2002/06/27/6 | Entidad jurídica partido y registro | DOCUMENTARY_LEGAL |
| INTEREST | https://www.boe.es/buscar/doc.php?id=BOE-A-2026-18148 | Categorías previstas de grupos de interés, distintas de partidos | DOCUMENTARY_LEGAL; comprobar texto y vigencia antes de integrarlo como catálogo de campo |
| CONGRESO | https://www.congreso.es/es/opendata/votaciones | Voto parlamentario, subconjunto del ecosistema, no población general | DOCUMENTED_ONLY para esta campaña; BR30G secundario no certifica original |
| SUBSET | https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl | Archivo parlamentario secundario empleado en BR30G | SECONDARY, cobertura nominal parcial, ningún as-of validado |

## Modelo epistémico
**Registro de partido ≠ candidatura presentada ≠ candidatura proclamada ≠ cargo electo ≠ actividad política pública ≠ impacto causal.**
No adjudicar el rol de militante a personas sin declaración pública y contrato de datos legal específico. Tampoco equiparar ausencia en Congreso con inexistencia o irrelevancia.
Se requiere conservación de identidad estable, relaciones muchos-a-muchos, ventanas de efectividad, fecha de primera disponibilidad verificable, fecha de captura, fuente y licencia; si la primera disponibilidad es desconocida, las observaciones se excluyen por defecto de entrenamiento histórico as-of.

## Declaraciones y representación
Las posiciones programáticas son textos atribuidos a fuentes, no coordenadas numéricas de una supuesta ideología absoluta. Una candidatura por coalición no certifica la militancia en ninguno de sus partidos. Un registro de una organización no confirma que esté activa hoy. El estado de escaños solo se admite con SEAT_STATUS documentado y periodo/electoral; ausencia de tal dato equivale a UNKNOWN, no a cero.

## Adversarios a la ampliación
A) Un scraping indiscriminado de medios sesgaría cobertura por exposición mediática y no mediría incidencia política.
B) Un catálogo oficial de partidos, sin actividad, admitiría partidos inscritos sin evidencia de movilización o representación.
C) Una definición demasiado amplia incluiría gente sin rol público y vulneraría privacidad.
D) Alianzas, cambios de nombre y estructura territorial sin referencia temporal producirían duplicaciones.
E) Métricas de valoración de personas podrían confundirse con mérito político: separadas del registro factual; la herramienta BR20H no produce scores ni rankings.

## Objetivo de campo aún bloqueado
Probar un **extracto real** con licencia del Registro de Partidos Políticos, candidaturas proclamadas y, luego, evidencias públicas de portavocías y campañas. Solo después de resolver cambios de denominación, periodo electoral, procedencia y as-of se podrá pasar de software de fixtures a un observatorio descriptivo útil para políticas públicas.
