# Politics Fantasy League — cierre BR20H, 20 ciclos A–J con BRANCHING

**Fecha:** 25/10/2026. **Autorización:** 20 nuevos ciclos completos AB 3.2.1 con branching del investigador. **Estado:** 20/20 ciclos A–J de ingeniería ejecutados y registrados, 20 endpoints de prueba superados tras dos reparaciones visibles. **0 validaciones nominales o censales externas, 0 ensayos empíricos sobre una muestra de personas o partidos españoles, 0 descubrimientos 2/3.**

## Marcadores

| Métrica | Verificado / juicio |
|---|---:|
| Ciclos nuevos concedidos | 20 |
| A–J instrumentados, test observacional de software ejecutado | **20** |
| Primer pase | 18 PASS, 2 FAIL |
| Después de errata de fixtures | **20 PASS / 0 FAIL** |
| Entidades inventadas en el ejemplo de integración | 9 (2 personas y 7 organizaciones) |
| Fuentes inventadas en ejemplo | 2 |
| Relaciones inventadas | 5 |
| Eventos públicos inventados | 2 |
| Corpus de partidos reales completo y auditado | **NO DISPONIBLE** |
| Grupos de personas reales validados con fuentes independientes | **0** |
| VSDS proyecto | **1/3 → 1/3** |
| CT2 predicción parlamentaria (rama histórica) | 24/100, sin cambio |
| CT2 nueva rama multiactor | **20/100 → 20/100**, ordinal y no probabilística |
| Descubrimientos N1, N2, N3 nuevos | **0, 0, 0** |
| Restante del bloque BR20H | **0** |

La CT2 multiactor tiene una **identidad de rama diferente** de la predicción parlamentaria, conforme a AB O4/O5. No comparar 20 y 24 como si una rama hubiera perdido cuatro puntos de probabilidad. La rama nueva apenas posee fuentes documentales; el software no prueba cobertura empírica.

## 1. Población, teoría y falsadores

Se sustituye el supuesto de que representación parlamentaria delimita a las personas políticamente activas. Un actor puede estar documentado por registro organizativo, candidatura, cargo de partido, portavocía, intervención pública atribuida, campaña, actividad de plataforma y participación colectiva, **sin necesidad de tener escaños**. En sociología política, esto separa poder institucional formal, acceso a agenda, relaciones colectivas y observabilidad pública; **no identifica causalmente «influencia»**.

No imponer una jerarquía en el continuo izquierda–derecha. La capa de contenido consiste en descripciones y declaraciones programáticas con tema, texto, emisor, fuente, fecha y controversias, no una calificación global de actores. Un movimiento ciudadano puede estar documentado sin convertirse por inferencia en partido; una candidatura no equivale a afiliación privada. Se evita registrar militancia no publicada o perfiles de ciudadanos ordinarios.

Antecedentes normativos/documentales que restringen el modelo:
- [Registro de Partidos Políticos del Ministerio del Interior](https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos): consulta con filtros y exportación PDF anunciados en catálogo; en BR20H **no se descargó una lista nacional exhaustiva**.
- [LOREG, art. 44](https://www.juntaelectoralcentral.es/cs/jec/normativa/estatal?idContenido=2741462&idLeyJunta=1&idLeyModificacion=2740214&p=1379061506503&paux=1379061506503&template=Loreg%2FJEC_Contenido): partidos/federaciones, coaliciones y agrupaciones de electores son formas distintas.
- [Ley Orgánica 6/2002](https://www.boe.es/eli/es/lo/2002/06/27/6): el registro jurídico no acredita por sí solo actividad ni representación electoral.
- [Ministerio del Interior, catálogo electoral](https://sede.interior.gob.es/portal/sede/informacion-general/catalogo-de-datos): distribuciones XLSX sobre resultados y cargos, aún **no ingeridas**.
- [Real Decreto-ley 21/2026](https://www.boe.es/buscar/doc.php?id=BOE-A-2026-18148): distingue legalmente grupos de interés de partidos. La existencia de marco normativo no prueba que exista ya un dataset operativo accesible; revisar vigencia/implantación antes de afirmarlo.

El fichero de referencia para la nueva población es [docs/UNIVERSO_ACTORES_POLITICOS_20261025.md](../../docs/UNIVERSO_ACTORES_POLITICOS_20261025.md).

## 2. Qué software se ha construido

[Motor de entidades, relaciones y eventos](../../src/politics_fantasy/political_universe.mjs) independiente de dependencias de terceros, que distingue 14 tipos de entidad y 11 tipos de vínculo documentado: partidos, federaciones, coaliciones, agrupaciones de electores, candidaturas, plataformas, sindicatos, medios, grupos de interés, instituciones y personas con rol público, entre otros. Admite relaciones múltiples y periodos, identidad estable por fuente, homonimias pendientes, documentos de procedencia, fecha de primer conocimiento público y fecha de captura.

- **Fuente vs evidencia:** una URL de catálogo DOCUMENTED_ONLY no puede por sí sola respaldar la creación de un actor o afirmación; se requiere una fuente capturada/fixture. La validación de forma de SHA no equivale a recomputación criptográfica del original: la ingesta RAW oficial todavía no está implementada.
- **Identidad:** no fusionar por cadenas de nombre. IDs con autoridad; conflictos retenidos, no actualizaciones silenciosas.
- **Mandatos y candidaturas:** CANDIDATE_FOR no genera MEMBERSHIP. SEAT_STATUS exige un registro fuente declarado oficial y referencia electoral. UNKNOWN no es ABSENT. Transiciones históricas sin fecha son ambiguas.
- **Tiempo:** FIRST_PUBLIC_AT y OBSERVED_AT independientes; consultas as-of no usan fuentes capturadas después del corte.
- **Eventos:** reuniones, declaraciones, anuncios, iniciativas, candidaturas y actividades civiles; registrar presencia no da influencia causal.
- **Privacidad:** no se aceptan PERSON sin rol público documental, atributos privados directos ni campos influence_score o ideology_score.
- **Producto:** no se emiten puntuaciones de mérito o influencia para personas reales.
- **Auditoría:** informe de cobertura anónimo por tipo de actor/fuente y estado de escaño.

Hay un [CLI local offline](../../scripts/actor_universe_cli.mjs) para leer un JSON contractual y emitir una auditoría agregada sin exponer identificaciones personales. El ejemplo [political_universe_fixture.json](../../examples/political_universe_fixture.json) es **completamente ficticio**. El CLI está escrito y publicado pero **no se probó como proceso real Node en checkout limpio**; el motor y sus tests puros se ejecutaron dentro de V8 de la sesión.

## 3. Contabilidad de los 20 ciclos A–J

Los criterios fueron congelados documentalmente ANTES del código en commit GitHub **2b4bddf77b0eb9b513fd153320413324642f4a86**. Las pruebas verificaron invariantes locales, no personas reales. Cada ciclo documenta rivales B, falsador C, ejecución E, auditoría F, ausencia de replicación externa G, revisión H, juicio I y decisión J individualizados en [LEDGER.json](LEDGER.json).

| Bloque | Ciclos | Resultado y límites |
|---|---|---|
| Fuentes, ontología y actores | C01–C03 | Tipos legales separados y persona pública sin escaños representable, solo fixtures y fuentes documentales |
| Identidad y procedencia | C04–C06 | Homonimia aislada, IDs estables, claims sin source rechazados |
| Historial temporal | C07–C08 | Roles con validez histórica, captura y efecto separados |
| Partidos, candidaturas, coaliciones | C09–C10 | Sin membresía inferida; pertenencia múltiples-a-múltiples |
| Contenidos, acontecimientos y causalidad | C11–C13 | Posiciones por tema atribuidas y eventos extraparlamentarios; sin influence_score |
| Privacidad, conflictos y as-of | C14–C16 | Perfiles privados rechazados; conflicto visible; no futuro retroactivo |
| Búsqueda, cobertura y producto | C17–C19 | Filtros no jerárquicos, UNKNOWN separado de ABSENT, gate de puntuación real cerrado |
| Integración | C20 | Fixture de referencia y controles de integridad; no validación de campo |

**Incidentes adversariales preservados**: C02 falló por afirmar que la fixture contenía 5 tipos cuando tenía 6; se reparó, añadió INTEREST_GROUP y volvió a pasar. C16 falló porque el test esperaba ver en junio una fuente capturada en octubre; se añadió una fuente ficticia efectivamente capturada antes del corte, mostrando que la restricción temporal funcionaba. Ambas reparaciones se registraron en commit **1e7c653180004baf1fd79d15efde490ef4d7d69e** y refuerzo ulterior **3a85cbb19fa2c4280ec2aa1c58c11c5e09f0ec70**. No se ocultó el primer pase 18/20.

La revisión de los 20 tests finales: **20 PASS / 0 FAIL**. La fixture actual pasó integridad referencial: 9 actores, 5 relaciones, 2 eventos y 2 fuentes inventadas. En el corte as-of 2026-10-01 había 0 eventos utilizables porque ambas fuentes ficticias se capturaron después; para corte 2026-10-26 hay 2. El baseline «solo diputados» no tendría relación ELECTED_TO sobre las 2 personas, pero **esa falta de registro no demuestra que carezcan de cargo real** (ni que el nuevo algoritmo sea superior ante datos de España).

## 4. Qué NO queda validado

No se ha realizado una descarga íntegra del Registro de Partidos Políticos, ni validación de proclamaciones electorales o roles territoriales con identificadores reales. No hay una cohorte de personas públicas españolas reconciliada a través de fuentes; tampoco medición comparativa de cobertura poblacional, identidad individual, causalidad de influencia, precisión predictiva o calibración de scoring.

Esto es ingeniería informada por fuentes legales y pruebas sintéticas. La mayor cantidad de tipos soportados es **una propiedad del esquema diseñado**, no un hallazgo de sociología sobre el número de actores realmente influyentes.

La actual aplicación Python/SQLite demo del fantasy conserva su capa separada de figuras inventadas y no se anuncia aquí integración end-to-end con el servidor Python. El nuevo motor Node constituye una infraestructura paralela para futura importación del universo ampliado. Falta puente backend, autenticación/QA navegador y fuentes verificadas.

## 5. AB-DECIDE y priorización

**CLOSE_BR20H**: los 20 ciclos concedidos se cierran como AB A–J de ingeniería, 0 experimentos confirmatorios externos. Actualizados nueve priors en [PRIORS_DELTA.md](PRIORS_DELTA.md), con límites, falsadores y evidencia contraria. CT2 multiactor 20/100 plana; VSDS 1/3; N1/N2/N3 nuevos 0.

Próxima evidencia indispensable: muestra RAW con licencias e identificadores del Registro de Partidos Políticos, proclamaciones oficiales, roles públicos y organizaciones; crear instrumento de extracción con hashes del contenido y procedencia independiente, seguido de motor de historiales e integración con el producto, sin inventar filiaciones privadas ni atribuciones de poder.

**Presupuesto ya autorizado que se mantiene intacto**: 12 ciclos PF-B50 pendientes, 19 ciclos PF-AB20 pendientes, 45 libres PF-F45 posteriores. Según AB O6, no pedir nuevos bloques mientras puedan emplearse autorizaciones abiertas. Ejecutar primero **PF-B50 C39–C50 (12 ciclos con branching)** para adquisición real / backend y después **PF-AB20 C02–C20 (19 ciclos)** con evidencia de campo. Solo una vez consumidos o justificadamente cerrados, decidir sobre PF-F45. **No se solicita nueva concesión para esta continuación.**
