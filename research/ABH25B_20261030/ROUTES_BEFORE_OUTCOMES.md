# ABH25B — rutas elegidas ANTES de nuevos outcomes

Base: PR #3 draft `f347900cf3524e39a8049973e3c63573626d5ad8`, no merge. Concesión **nueva** 25; anteriores intactas. Tres vías diferenciadas:

**R1. Respuesta institucional del Reino Unido: latencia.** Fuente oficial `petition.parliament.uk`; no volver a inspeccionar páginas 1/2 anteriores. Estimando descriptivo: días entre `response_threshold_reached_at` y `government_response_at` por cohortes congeladas, con controles de censoring, cierre, respuesta nula y cronología invertida. Rival: diferencias de periodo/cohorte y ranking de resultados, no efecto causal de firmas. Falsador: campos ausentes, selección no reproducible, fechas incoherentes o ausencia de soporte suficiente. Contraste independiente del signo francés C38.

**R2. Peticiones de Canadá: semántica de la fuente.** Editor oficial Cámara de los Comunes, feed XML `https://www.ourcommons.ca/petitions/en/Petition/Search?Category=All&output=xml` enlazado desde Open Data (la ruta anterior redirige). Pregunta: ¿el feed presenta una unidad de respuesta gubernamental vinculable a la petición, o solo firmas, etapas y certificación? Falsador: feed sin ID estable, origen no verificable o XML distinto; sin valores, no imputar ausencia. R5 tras dos intentos fallidos. **No equiparar instituciones ni umbrales UK, Francia, Canadá**.

**P1. Producto local ficticio: inteligibilidad de puntuaciones y estado de jornada.** Añadir API de desglose por figura y categoria con reglas y cobertura; comprobar identidad de suma por club antes de introducir UI. Rivales: desglose inconsistente o información de rondas ajenas expuesta por estado compartido. Falsadores: inconsistencias de puntos tras liquidación, acceso sin login, base compartida o retroceso de seguridad CSP. Prueba funcional no implica aceptación humana.

Método: contractos A–J, código y SHA en Git ANTES de outputs, controles de nulo/errores, registro de priors y Atlas. Calificar resultados empíricos/documentales/producto por separado. Sin autorizar merge a main ni despliegue. R5 bloquea una vía, no la campaña; la cuota máxima no autoriza estudios redundantes.
