# Gobernanza de la ampliación — autorización de 45 bucles libres

**Fecha de la concesión del usuario:** 24-10-2026.

Interpretación secuencial explícita del encargo: **terminar primero el bloque experimental PF-AB20** (el piloto C01 está cerrado solo como exploración, C02–C20 pendientes/no ejecutados). **Después** quedan autorizados **45 bucles libres adicionales**, con branching entre producción, extracción/ingeniería de datos y ciencia aplicada. "Libres" significa autonomía para elegir las preguntas concretas, rutas y pivotes basándose en la evidencia; **no** significa falsear ejecuciones ni omitir controles AB 3.2.1.

Los 45 bucles se registran en `FREE45_LEDGER.json` con estado `AUTHORIZED_NOT_STARTED`. Ninguno se ha gastado artificialmente para justificar componentes construidos antes de su inicio. Los trabajos de producto hechos en este turno son **incrementos de preparación sin consumo de una plaza AB posterior**; su prueba está en código y tests y se recogen en `PRODUCTION_DELIVERY.md`.

## Condición de bifurcación investigación ↔ producción

La campaña deberá contener bucles de producción con comportamiento observable, no solo informes. El tipo se decidirá **antes de cada bucle**, anotando objetivo, alternativa más simple, entrada, diseño experimental o de aceptación, prueba automatizada o manual independiente, resultado, limitaciones y decisión `CONTINUE/REPAIR/PIVOT/STOP`. En ciencia se mantiene el contrato A–J, estimando y evidencia 0–3; en producto se mantiene A–J adaptado a invariantes y pruebas de integración sin disfrazar productos de descubrimientos.

**Foco inmediato de producto** (no son bucles ejecutados): cuentas/autorización, ofertas y subastas, ligas privadas, snapshots de mercado, eventos de scoring auditables, versiones de reglas y explicabilidad, UI móvil probada, CI visible en GitHub, migraciones, backups. **Foco científico**: obtener archivos RAW oficiales con licencia y SHA; compararlos con HTML; verificar fechas de disponibilidad, identificación nominal y denominadores de exposición; construir datos de aprendizaje temporal sin fuga; modelos baseline con walk-forward; hipótesis de red y ablaciones.

No imponer proporciones exógenas en un proyecto adaptativo: si la siguiente barrera a la investigación es de ingeniería, priorizar producto/data engineering y revisitar ciencia cuando exista evidencia. Pero queda **prohibido cerrar los 45 ciclos como solo papers/informes**. Cada "bucle productivo" debe entregar código/infraestructura comprobable y una prueba de aceptación con resultados archivados.

## Control de método

- Estado y costes reales, no hitos narrados como experimentos.
- Nunca usar fixtures sintéticos como resultado empírico de sociología política.
- No actualizar CT2 predictivo por producir más interfaz o documentación.
- Todo nuevo prior relevante se añade al ledger acumulativo con procedencia, incertidumbre y evidencia a favor/en contra.
- No claims de producción pública/robustez sin autenticación y auditoría. No afirmar que se publicó en GitHub hasta disponer de confirmación del servicio.
- El usuario autorizó **hasta 45**; no hay obligación de rellenar plazas si hay bloqueo crítico o R5/STOP.
