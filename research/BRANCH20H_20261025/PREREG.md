# PF-BR20H — ampliación de universo político (AB 3.2.1, branching)

Fecha de apertura: 25 octubre 2026.
Autorización explícita: **20 ciclos A–J con BRANCHING**, independientes del saldo previo PF-B50 12, PF-AB20 19, PF-F45 45.
**No confundir autorización, pruebas de fixtures, investigación documental y verificación empírica.**
Bloque abierto en conversación del usuario después de BR30G. Se autoriza explorar más allá de Congreso: partidos con o sin representación y otras personas/organizaciones documentadas que intervienen en el ámbito político.

## Fundamentos DOCUMENTALES (no corpus nominal auditado)
- Ministerio del Interior, Consulta de Registro de Partidos Políticos: https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos. Búsqueda y exportación PDF declaradas; **NO se afirma descarga de la lista completa**.
- Ministerio del Interior, catálogo electoral: https://sede.interior.gob.es/portal/sede/informacion-general/catalogo-de-datos. Distribuciones XLSX de candidaturas/resultados; **NO se afirma importación del contenido**.
- LOREG art.44 https://www.juntaelectoralcentral.es/cs/jec/normativa/estatal?idContenido=2741462&idLeyJunta=1&idLeyModificacion=2740214&p=1379061506503&paux=1379061506503&template=Loreg%2FJEC_Contenido: partidos/federaciones, coaliciones y agrupaciones de electores son modalidades distintas de presentar candidaturas; candidatura no equivale a partido ni a representación.
- LO 6/2002 https://www.boe.es/eli/es/lo/2002/06/27/6: registro de partidos como categoría jurídica; inscripción no prueba actividad electoral ni influencia.
- RDL 21/2026 https://www.boe.es/buscar/doc.php?id=BOE-A-2026-18148: categoría de grupos de interés distinta de partidos; no suponer que disponer de obligación normativa implique disponer ya de microdatos descargables. Contrastar vigencia/revisiones antes de producto.
**No inferir ideología, militancia no documentada, voto personal, redes privadas o influencia causal. No crear perfiles de ciudadanos corrientes. Personas incluidas solo en roles políticos públicos y documentados.**

## Estimando global y alternativas
Se busca validar a nivel SOFTWARE si un modelo de datos basado en **actor + rol + organización + candidatura + acto + fuente + historia temporal** representa sin pérdida varios tipos de participación política, con la misma admisibilidad estructural para actores que carecen de escaños. Outcome primario: invariantes de datos, no poder político ni calidad del actor.
- H1: ontología multiactor con proveniencia permite registrar cargos, candidaturas, activismo público documentado y acción política sin representación legislativa.
- H0: modelo parlamentario restringido no los registra sin inventar escaños o cambiar semántica.
- H_otras: fuente insuficiente, identidades homónimas, privacidad, etiquetas ambiguas, fuga temporal, sesgo de cobertura.
- Comparador: implementación mínima basada en diputado/código-voto; comparar **capacidad de representación de fixtures** sin afirmar mejor exactitud empírica.
- EVIDENCIA: fuente documental oficial para categorías + fixtures *inventadas* para ingeniería. G externo no disponible hasta tener corpus real.

## Contratos C01–C20 (un ciclo A–J completo por unidad; branching guiado por falsadores)
Los endpoints de cada ciclo se congelan ANTES de escribir ejecutor y tests. Los datos de fixtures no confirman hipótesis sobre España.
| ID | Branch | Pregunta y estimando operacional | Endpoint de aceptación | Falsador/rival |
|--|--|--|--|--|
| C01 | fuentes | ¿Se puede inventariar fuentes por alcance, sin confundir referencia con datos descargados? | Catálogo de origen, licencia/estado y límites | Afirmar descarga inexistente |
| C02 | ontología | ¿Acepta entidades jurídicas diferentes? | partido, federación, coalición, agrupación y asociaciones separadas | Mapear todos a partido |
| C03 | ontología | ¿Acepta personas sin cargo electo? | Actor PERSON con rol público documentado y sin seat | Exige número de escaños |
| C04 | identidad | ¿Prohíbe homonimia automática? | La igualdad de nombre no fusiona IDs | Fusión espuria |
| C05 | identidad | ¿Es estable identidad con ID de fuente? | Stable ID namespace+external ID | Dependencia de nombre |
| C06 | procedencia | ¿Toda afirmación política exige fuente verificable? | claim rechaza source_id ausente | Fuente sin especificar |
| C07 | tiempo | ¿Distingue fecha de acto y registro? | validAt/observedAt separados | Confundir eventos y capturas |
| C08 | temporalidad | ¿Se conservan cambios de cargo? | Roles con intervalos históricos correctos | Aplicar posición actual retroactivamente |
| C09 | org | ¿Se distingue afiliación org de candidatura? | candidate no implica member | Afiliación deducida |
| C10 | org | ¿Admite coaliciones multipardistas? | relaciones tipadas many-to-many por fecha | Coalición = partido único |
| C11 | política | ¿Evita eje derecha-izquierda obligatorio? | issue-position registrada solo con fuente y declaración explícita | Forzar coordenada numérica |
| C12 | eventos | ¿Admite acontecimientos fuera del parlamento? | public_statement, registered_initiative, public_meeting etc. | Solo votos |
| C13 | causalidad | ¿Evita inferir influencia por participar? | events no contienen influence_score ni causal_attribution | Puntuación de influencia implícita |
| C14 | privacidad | ¿Excluye dato privado de militancia? | ordinary private member/secret belief rechazados | Doxxing |
| C15 | calidad | ¿Conserva contradicciones de fuentes? | claims rivales sin overwrite | Selección silenciosa |
| C16 | as-of | ¿Bloquea uso retroactivo de futuras fuentes? | snapshots con first_public_at y observed_at | Leakage temporal |
| C17 | búsqueda | ¿Puede consultar por tipo, rol y jurisdicción? | filtrado igualdad, sin ranking | Sesgo priorizando escaños |
| C18 | inclusión | ¿Mide cobertura por estratos, sin jerarquizar actores? | matriz source/type/seat yes-no-unknown | «sin escaño» equivale cero actividad |
| C19 | producto | ¿Impide puntuar individuos reales sin validación? | gate de id+fuente+vigencia y regla externa pendiente | Real fantasy con datos ficticios |
| C20 | integración | ¿Pasa flujo de extremo a extremo con varios partidos y personas ficticias? | audit + snapshot + cross-validation de fixture multiactor | Implementación acoplada al Congreso |

## Reglas de actualización
Por ciclo registrar A verdad/estimando, B rivales, C contrato, D instrumento/pruebas, E ejecutado, F auditoría, G independiente, H prior, I calificación científica y VSDS/CT2, J decisión. Las pruebas pueden invalidar un ciclo; mantener fallos y repairs; nuevos hallazgos no se suman por cantidad de tests. No usar posiciones ideológicas deducidas ni puntuaciones reales de personas. CT2_espacial original LARP NO se traslada: rama PF actual CT2_predictive=24/100 y VSDS=1/3 hasta evidencia externa. DRIFT en esta rama estimado D2.0 (cambia población, conserva sociología política, temporalidad y estimando general de observabilidad).
