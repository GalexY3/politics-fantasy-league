# PFL · Contrato V0 de trazabilidad documental entre fases de políticas públicas

**Fecha:** 2026-10-31. **Estado:** instrumentación exclusivamente sintética, pendiente de revisión. **R5: STOP**. No es un estudio de políticas públicas españolas, un contrato de ingesta real, un modelo predictivo, una estimación causal, una fuente de puntuaciones sobre personas ni un ciclo AB.

## A. Pregunta y objeto

¿Puede una infraestructura longitudinal expresar, sin deducciones implícitas, una ruta documental entre compromiso público, iniciativa, decisión, instrumento normativo, presupuesto, implementación e indicador, conservando sus distintas unidades, fechas de referencia y límites de observación? La hipótesis instrumental es que los enlaces tipados y con referencia exacta permiten distinguir una cadena documental explícita de una yuxtaposición de documentos temática o temporalmente próximos.

## B. Población y unidades

Solo fixtures con ID `SYNTHETIC:`; nodos de siete **clases documentales diferentes** y aristas de referencia exacta entre clases adyacentes. No hay población española, censos de entrada, expedientes, políticos, empresas, presupuestos, importes, outcomes ni originales admitidos. El grafo documental no constituye un padrón, una cadena causal ni un proceso político completo.

## C. Explicaciones alternativas y baseline

- **B0 sin enlace:** proximidad cronológica, actor coincidente, asunto o nombre similar. El baseline competente de abstención no afirma vinculación sin referencia documentada.
- **B1 referencia explícita:** el documento de destino incluye una clave exacta del documento de origen, la arista tiene clase semántica permitida y un testigo propio de cuándo se conoció. Una referencia puede relacionar documentos, **no demostrar que el primero causase el segundo**.
- **B2 hipótesis de mecanismo:** autorregulación, acoplamiento ambiental, selección de publicación y temporalidad son proposiciones adicionales. Un B1 positivo no valida B2. Los comparadores predictivos B0-calendario, B1-competencia y B2-memoria acoplada del programa sistémico requieren datos reales admisibles y quedan sin ejecutar.

## D. Registro, temporalidad y derechos

`event_on`, `document_on` y `captured_at` son separados. `first_public_at` permanece nulo porque una captura no autentica primera publicidad histórica. Cada nodo y arista tiene su propio `captured_at`; se filtran primero por `as_of` y después por `cut_on` civil, con huso jurídico declarado. Un documento de fecha antigua obtenido meses después no entra en una consulta histórica anterior a su captura. Se exige día civil ya cerrado. No se obtienen fuentes ni se heredan derechos de uso por el catálogo.

## E. Contrato de aristas

`COMMITMENT_CITED_IN_INITIATIVE`, `INITIATIVE_REFERENCED_IN_DECISION`, `DECISION_REFERENCED_IN_NORM`, `NORM_REFERENCED_IN_BUDGET`, `BUDGET_REFERENCED_IN_ACT` y `ACT_ASSOCIATED_WITH_INDICATOR` son las únicas clases en V0. El último enlace significa **asociación documentada**, jamás impacto causal.

Para admitir una arista en el fixture se exigen: pareja de clases correcta, IDs de documentos origen/destino que coincidan exactamente con los dos nodos, dos SHA-256 declarativos de documentos que coincidan con los SHA declarados en dichos nodos, secuencia de fechas coherente y testigo temporal propio de la arista. Estos SHA son **alegaciones del fixture**, no autenticaciones independientes de originales. Los enlaces incompletos aparecen como `unknown_or_unresolved_link_endpoints`, no como un rechazo, ocultación o ausencia de política. Los grafos admiten relaciones N:M; nunca unen documentos por nombre, tema, partido, homonimia o cercanía temporal.

## F. Prerrequisitos de admisión empírica

Resolver R5 por recurso: derechos para adquisición, transformación, conservación y distribución; originales, sha y capturas; registro anterior a selección y cobertura; identificadores oficial/namespace y correspondencias N:M; negativos, pendientes y censura; fecha de primera publicación acreditada o declaración honesta de indisponibilidad; versiones comparables. La prueba sintética no certifica ninguna de estas propiedades. Queda prohibido conectar este módulo a API pública o a personas reales mediante esta autorización.

## G. Evaluación técnica y controles

Tests contra falso enlace por documento o SHA declarado erróneo, cruce de etapas, selección retroactiva, captura futura, evento futuro, fecha civil Madrid, duplicado visible y duplicado todavía desconocido, reloj submicrosegundo, atributos de derechos/PII engañosos y cadena completa solo cuando las seis referencias están disponibles. No ejecutar entrenamiento ni leer outcomes reservados.

## H. Falsadores

Rechazar V0 si un `as_of` histórico ve una arista capturada después; si dos documentos parecidos se enlazan solos; si aparecen IDs personales en el reporte; si un estado incompleto se convierte en ausencia de intervención; si una referencia transforma automáticamente correlación en causalidad; si se confunde día civil jurídico con fecha UTC; o si un nodo con derechos no acreditados se presenta como listo para reutilización.

## I. Salida y limitaciones

La función devuelve solo cantidades sintéticas por etapa, enlaces exactos visibles, extremos desconocidos, existencia de alguna ruta completa en el fixture y flags negativos inmutables de evidencia real. No devuelve nodos, identificadores, casos, importes ni resultados. No pretende determinar responsabilidad, eficiencia, cumplimiento de promesas, impacto económico, crédito causal ni predicción.

## J. Decisión y seguimiento

Este bloque es **NONCYCLE**, no desbloquea R5, no cambia CT2/Atlas, no consume ninguna de las diez autorizaciones nuevas y no mueve `PROJECT_STATE.json` de la rama protegida. Podrá considerarse un componente de arquitectura investigadora solo tras revisar tests y contratos en la revisión Git efectiva. El siguiente contraste científico real exige universo completo y comparación de mecanismos rivales congelada A–J **antes** de consultar outcomes.
