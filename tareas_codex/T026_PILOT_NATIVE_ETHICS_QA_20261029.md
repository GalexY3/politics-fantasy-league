# T026 — Integrar y auditar piloto PFL ficticio antes de cualquier captación
**PENDIENTE · NO EJECUTADO · sin autorización para experimentar con personas ni para activar scoring de políticos.**

Base: `GalexY3/Metodologia-AB` rama `research/pfl-abh5-prospective-pilot-20261029`. Leer AGENTS.md, AB 3.2.1/O1–O7, `research/ABH_PROSPECTIVE_PILOT5_20261029/{FINAL_REPORT.md,STUDY_PROTOCOL_DRAFT.md,CAMPAIGN_STATUS.json}`, gates éticos y T025. No fusionar main, activar CI costosa, usar ChatRelay ni publicar capturas personales.

## Entregables verificables

1. Crear tests Node **nativos y persistentes** para `pilot_assignment.mjs`, `fictional_transfer_items.mjs`, `fictional_transfer_key.mjs`, `pilot_dryrun_intake.mjs` y `pilot_analysis_dryrun.mjs` reproduciendo los **84 checks V8**, desde checkout limpio; registrar SHA, version de Node, contadores PASS/FAIL/SKIP y logs con tiempo y evidencia. Abrir error si pruebas difieren, no asumir éxito.
2. Examinar bloque de cuatro condiciones (T y L) para comprobar paridad de estímulos y exposición, tutorial neutro equivalente en longitud/tiempo, distinción cobertura desconocida/cero, y que la **clave no se empaquete en el cliente**. Una prueba de importación y los 84 asertos no equivalen a test navegador/integración.
3. Diseñar interfaz local accesible que funcione solo con fixtures etiquetadas `SYNTHETIC_DRY_RUN_ONLY`, no envíe datos a terceros ni conserve respuestas reales. Añadir anti-leakage, CSP, navegación teclado, mensajes de retirada y controles sintéticos; no declarar interfaz probada sin un navegador real.
4. Revisar seguridad: el `status:APPROVED_BY_HUMAN_REVIEW` usado en el test es **mock falsificable** y no una puerta auténtica. Implementar arquitectura de aprobación/consentimiento separada únicamente tras obtener autorización y revisión legal; **no activar** almacenamiento o endpoints para sujetos reales por esta tarea.
5. Preparar documentación de protocolo definitivo pendiente: comité de ética/consulta DPO aplicable, responsables del tratamiento, reclutamiento adulto y derecho a retirada, retención y eliminación, plan de seguridad, tamaño de muestra justificado, minimización, manejo de no completadores y análisis ITT robusto. Marcar condiciones como NOT_APPROVED hasta resolverse.
6. Probar navegación y resultados en navegador local seguro si se dispone de él; guardar un recibo de pruebas separado por componente y actualizar Atlas con evidencia real. No gastar ciclos AB-R adicionales por QA de software; si el trabajo descubre investigación discriminante, exigir prereg y autorización correspondiente.

**Criterio de aceptación técnico:** 84/84 controles reproducidos en Node nativo, integridad semántica y pruebas de interfaz registradas sin hallazgos de filtración crítica, mock bloqueado fuera de fixture y documentación de límites. **Criterio humano independiente:** revisión ética/seguridad adecuada y consentimiento antes de invitar participantes; este encargo NO concede ninguno de ellos.

**Estado inicial verificado al crear ficha:** 0 personas reclutadas, 0 consentimientos, 0 outcomes humanos, 0 release gates; solo 84/84 comprobaciones de V8 durante ABH_PROSPECTIVE_PILOT5. No declarar ninguna tarea concluida hasta recibir salida del ejecutor.


## Seguimiento parcial 29/10/2026 — NO CERRAR T026
En la rama sucesora `research/pfl-abh5-pilot-native-integration-20261029`, el entorno Node aislado reprodujo 84/84 comprobaciones con hashes fuente verificados y se ejecutaron 15/15 tests HTTP del servidor local. Se construyó `pilot_local/`, se detectaron y corrigieron validadores con herencia/Symbol (84/84 regresión), y se documentaron condiciones éticas. **NO se dispone de checkout integral, prueba E2E Chromium concluida, aprobación de comité ni captación humana.** Por tanto T026 permanece **PARCIAL / ABIERTA**; ver tarea sucesora T027.
