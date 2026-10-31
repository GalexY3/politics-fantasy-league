# P03 · Autoridad temporal y contexto MemPalace

**Antes de resultados. AB-P de continuidad, solo datos sintéticos.** No es prueba de memoria automática de un LLM entre chats.

**A. Pregunta.** ¿Un índice de PR actuales con SHA y precedencia de decisiones evita que un informe obsoleto gane como vigente pese a una similitud semántica mayor? Endpoint: decisiones vigentes correctas en diez consultas sintéticas, sin acceso a fuentes privadas.

**B. Rivales de igual información.** B0: FTS textual con todos los documentos y metadatos de autoridad disponibles. B1: primero restringir versiones por HEAD y estado, luego FTS y reglas explícitas de supersesión. B2: búsqueda semántica MemPalace sobre MISMO inventario como referencia exploratoria; si no se puede ejecutar modelo real, declarar B2 INCOMPLETE en vez de un mock. H1 B1 10/10 y mejora respecto al control B0 de igual información. H0 B0 ya alcanza 10/10 y B1 solo añade coste, o B1 falla con cambios concurrentes.

**C. Diez adversarios prefijados.** Dos PR hermanas mismo archivo; hija atrasada; decisión corregida; PR nueva no en lista manual; PR fusionada/cerrada; SHA distinto; checkout sucio; fuente no leída en realidad; títulos idénticos de edición distinta; indisponibilidad de GitHub. Textos ficticios, sin PII ni conversaciones reales.

**D. Instrumentación.** Medición explícita del recuento de decisiones correctas, rechazos fail-closed, falsos reclamos de lectura. Controles con misma información en ambos brazos.

**E. Freeze.** Prerregistro, fixtures, código y tests antes del primer ensayo, resultados archivados en Git y recibos SHA.

**F. Auditoría.** Inyección de títulos repetidos, timestamps futuros, colisión de versiones, rutas privadas y error retirado muy similar. Asegurar paridad de fuentes y presupuesto.

**G. Confirmación.** Variaciones sintéticas no usadas para escribir diseño; no es replicación con chats reales ni prueba tras reinicio.

**H. Actualización.** Separar propiedades de un sistema de fuentes de ventajas del algoritmo vectorial. Prohibido inferir que MemPalace recuerda todo por sí mismo.

**I. Alcance.** QA de producto para continuidad bajo herramientas COS, no metodología de LLM validada empíricamente, no rights, no R5.

**J. Regla.** Un máximo de un AB-P si hay diferencia útil frente a B0 y oráculos completos; si no, STOP o REPAIR, sin gastar ciclos por escribir tests.
