# PFL · identificabilidad de procesos, selección documental y vínculos registrales (R8)

**Estado:** instrumento prospectivo + teoría de la identificación; **NO resultado empírico**, **NO prerregistro A–J** ni decisión sobre TFM. Las comprobaciones de software usan exclusivamente fixtures sintéticos. No se han consultado nuevos desenlaces políticos a causa de este instrumento.

## 1. Tres preguntas que no deben mezclarse

La unidad **asiento de entrada** pertenece al acto de recepción documentado por un Registro General; el **expediente** puede abrirse o ser calificado posteriormente, y el **acto de decisión** tiene un origen, fecha, fundamento y objeto que no coincide necesariamente con ambos. Un documento del boletín, un dictamen emitido, una disposición del BOE o una fila en un índice editorial constituyen otras unidades de observación. La frontera jurídico-organizativa (competencia y fase), la funcional (comunicaciones/decisiones políticas) y la empírico-documental (qué publica cada sistema) siguen separadas.

El estimando de *todas las entradas recibidas* requiere un marco de Registro General con familia, órgano, plazo y unidad fijados antes de incluir expedientes. La alternativa **admission-first** puede ser legítima como población de expedientes admitidos, pero cambia expresamente la pregunta: nunca estima rechazos previos a admisión. Las publicaciones del BOE solo pueden ser documentos asociados por una relación oficial, no el universo inicial de oportunidades.

## 2. Conciliación explícita de asientos y expedientes

El contrato offline `src/politics_fantasy/procedural_official_links.py` distingue claves `institution × legislature × family × namespace × local_id`, y exige para cualquier arista propuesta un identificador de entrada, otro de expediente, URI documental HTTPS y SHA de un supuesto original. Ninguno de estos campos autodeclarados constituye por sí solo prueba de que el documento sea auténtico, se haya capturado con licencia suficiente o contenga realmente ambos identificadores: solo un registro de fuentes **servidor, con bytes cotejados y derechos adjudicados**, podría promover esa evidencia. El módulo **no contiene** un parámetro para autocertificar el enlace.

Una inscripción puede permanecer sin expediente; más de un asiento puede referir un mismo expediente y viceversa. Los conteos de no enlazados son **faltantes de la conciliación**, nunca decisiones negativas. El contrato detecta colisión de namespace, cambio de institución/legislatura/familia, duplicación, fechas imposibles y vínculos con entradas/expedientes no observados. Los resultados muestran únicamente agregados sin IDs ni textos. El tiempo de captura se vuelve visible de forma conservadora desde el **segundo UTC siguiente**; una consulta `as_of` anterior no recibe ni hashes, contadores ni relojes posteriores. La fecha documental tampoco se transforma en `first_public_at`.

**Limitación importante:** el instrumento no verifica realmente los bytes de un original; sin archivo primario y recibo externo, la clasificación sigue siendo `DOCUMENTARY_LINK_CANDIDATES_NOT_SCIENTIFIC_ADMISSION`. Un enlace oficial futuro puede suplir parcialmente una clave faltante, pero su existencia no convierte un índice de admitidas en censo de todas las presentadas.

## 3. Por qué un índice sesgado no identifica la tasa de resultado

Sea `R` el universo de entradas elegibles, `S=1` la inclusión en el índice observable y `Y_t=1` que un evento de interés se haya producido *hasta el corte común t*. La tasa de interés sería:

\[
p_t=\Pr(Y_t=1\mid R).
\]

Lo que calcula un índice editorial seleccionado, si sus desenlaces fueran incluso correctos, es una cantidad diferente:

\[
p_t^{obs}=\Pr(Y_t=1\mid R,S=1).
\]

En general \(p_t^{obs}\ne p_t\), especialmente si la publicación/selección depende del propio resultado, la tramitación, la familia o el calendario. Esto no permite concluir por sí solo que exista un efecto causal de selección específico; lo convierte en **rival metodológico necesario** ante M1 (autorreproducción) y M2 (acoplamiento).

Si se conociese por testigo **independiente** un total de entradas \(N\), y una fuente adecuada certificase en un mismo corte \(Y\) eventos y \(Z\) no-eventos, dejando el resto sin clasificar, los límites de peor caso para la prevalencia acumulada en ese corte serían:

\[
\frac{Y}{N}\leq p_t\leq\frac{N-Z}{N}.
\]

Son **límites lógicos**, no intervalos de confianza, riesgo instantáneo, incidencia causal ni una inferencia sobre desenlaces futuros. Los pendientes observados no equivalen a terminales; solo podrán contar como no-eventos **hasta t** si la fuente permite afirmar que el evento definido no ocurrió antes del mismo corte. Sin fechas de cambio de estado o vigilancia homogénea no se debe certificar `Z`.

El contrato `src/politics_fantasy/procedural_selection_bounds.py` ejecuta esa aritmética **únicamente** con namespace `SYNTHETIC:` y `evidence_class=SYNTHETIC_LAB_ONLY`. No acepta casos reales ni valores de derechos declarados; si falta el denominador simulado devuelve `DENOMINATOR_NOT_IDENTIFIED` y tasas nulas de información (`null`, no cero). Ejemplo **enteramente ficticio**: \(N=100\), \(Y=12\), \(Z=38\), 50 clasificaciones insuficientes → intervalo [0,12; 0,62]. Si se elimina `N`, desaparece el intervalo numérico; ni 70 filas editoriales ni una cuenta publicada por el mismo backend sustituyen ese `N`.

## 4. Tres rutas científicas y falsadores de elegibilidad

**Ruta A — registration-first parlamentaria.** Marco por institución, familia y legislatura con toda recepción, incluidos no calificados, pendientes y retirados; expediente enlazado por clave documental y secuencias fechadas. **Falsador de elegibilidad:** el registro excluye entradas que nunca tuvieron tramitación o usa solo el total del mismo índice; en ese caso no hay `ALL_RECEIVED`. Si más adelante supera derechos, cobertura, censura y vintages, M1/M3 podrán oponerse con rivales temporales.

**Ruta B — admission-first parlamentaria.** Permite estudiar duración/decisiones solo *desde admisión*, siempre que los admitidos y sus transiciones sean exhaustivos en ese marco. **Falsador de elegibilidad:** publicación limitada a debatidas, aprobadas o contestadas, o fechas terminales incompletas. No permite inferir inadmisiones previas ni tasas de éxito desde registro.

**Ruta C — entradas agregadas de otra institución.** Libros de consultas/expedientes de órganos consultivos o administrativos, si se acreditasen volumen de **entradas** y **salidas** y eventual stock pendiente para un mismo año y clase. Puede formular balances de flujo y estudiar autorregulación operativa institucional sin equipararlo al trámite legislativo del Congreso. **Falsador de elegibilidad:** contar dictámenes emitidos como consultas recibidas o disponer solo de cifras retrospectivas sin series/horizontes comparables; sin eventos individuales no hay riesgos competitivos por expediente.

Las tres rutas no son sustitutos mecánicos del gran objeto de ciencia de datos sobre política española: permiten estimandos diferentes con diferentes operaciones y sesgos. Tampoco equivalen automáticamente a la autorreproducción de comunicaciones en sentido luhmanniano; para ello se requiere una definición conceptual adicional y resultados discriminantes, no solo un flujo administrativo.

## 5. Condiciones para salir del laboratorio

Una muestra real necesitará originales con URI oficial, SHA de bytes cotejado, contrato de licencia y tratamiento personal por distribución, clasificación exacta de unidades y selección, libro independiente de registros y método de cruce, versiones históricas reales o límites temporales certificados, cronología de actos, pendientes y terminales, identificación de censura derecha y retención temporal externa. El testigo de una revisión publicada no acredita el instante de primera publicación; una captura nueva tampoco.

Solo con ese conjunto y tamaño informativo suficiente cabría congelar **contratos A–J e instrumentos SHA en remoto antes de abrir outcomes**, construir rivales B0/B1/B2, holdout temporal y placebos de futuro/selección. Si no existe, este documento y sus pruebas siguen siendo **ingeniería y diseño**, con 0 ciclos SYSTEM20 y sin validación causal.

**QA:** `tests/test_procedural_official_links.py` y `tests/test_procedural_selection_bounds.py`. Los fixtures no representan casos reales. Las limitaciones se integrarán en el informe R8 y en la solicitud institucional **sin enviarla**.
