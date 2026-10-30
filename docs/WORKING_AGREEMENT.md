# Política de progreso y continuidad · piloto PFL · 30/10/2026

## Motivo y alcance

El investigador pidió unificar ramas, continuar entre chats y evitar fijación en un problema sin progreso ni exploración sustantiva. Eligió **producto e investigación con objetivos y progreso separados**. Esta es una adaptación operativa prospectiva de PFL, no una declaración de superioridad de un método ni una nueva versión validada de AB.

Hay una tensión documental: AB 3.2.1 R5 dice que el cupo es un límite y J condiciona solicitudes a su justificación; O6 y AGENTS exigen solicitar más ciclos al cierre. Es un mecanismo plausible que favorezca prolongar campañas. La inspección del repositorio no identifica causalmente cuánto de la fragmentación o repetición se debe a esa regla, al modelo, al cambio de chat o a las instrucciones del usuario.

## Qué cambia

1. **Resultado antes de presupuesto.** Una petición comienza por una capacidad observable o una pregunta y su evidencia discriminante. Se elige el trabajo para llegar a ese resultado; no se rellena una cuota de ciclos.
2. **Dos líneas, sin marcador agregado.** Producto: integración, flujo, permisos, persistencia y aceptación. Investigación: estimando, rivales, datos, identificación, novedad y replicación. No sumar sus pruebas ni grados.
3. **Trabajo en curso limitado.** Un hito activo por línea. Completar, invalidar con evidencia o aparcar antes de añadir otro. Documentar una dependencia bloqueada no la resuelve.
4. **Parada con memoria.** Dos intentos equivalentes bloqueados sin evidencia nueva llevan a `PARKED`, con artefacto/condición de reapertura. No requiere agotar el presupuesto. Conservar el saldo de cinco ABH10 y dos históricos en sus propios ledgers.
5. **Creatividad contrastable.** Al cambiar de dirección, tres rutas diferentes por mecanismo/población/fuente; especificar por qué cada una podría fracasar y qué se aprendería. Reservar una exploración breve dentro del trabajo autorizado; si no produce un test o una decisión útil en esa sesión, aparcarla. El número de ideas no es resultado científico.
6. **Una sola línea técnica de integración.** Los cambios vuelven a `integration/pfl`; no encadenar una PR por ciclo. Los experimentos y ramas conceptuales siguen en ledgers y carpetas. Concurrencia real y cambios grandes sí pueden justificar una rama técnica adicional con propietario y destino declarados.
7. **Cierre verificable.** Estado vivo, evidencia, negativos, siguiente acción y condición de bloqueo guardados juntos. No obligar a solicitar más ciclos. Proponer mantenimiento o ejecución directa cuando eso sea lo que falta.

## Ruta inmediata por línea

**Producto:** integración validada e incorporada mediante PR80. El siguiente hito es acceso multiusuario de la demo ficticia con pruebas de aislamiento de clubes y persistencia; luego flujo completo de jornada. La autenticación no requiere resolver T005.

**Investigación:** aparcar la insistencia en el registro AEA/C37 y T005 hasta nueva evidencia. Seleccionar una pregunta sociológica concreta y factible; primero contrastar antecedentes y acceso real a la observación. Tres rutas iniciales para comparar: feedback de rango y participación humana con datos explícitamente utilizables; respuesta institucional a peticiones con cronología original y análisis observacional; mecanismos de incentivos con contraste formal/simulado etiquetado como condicionado al modelo. No asumir que una fuente existe, que es reutilizable o que esas preguntas son nuevas. El criterio de selección es qué hipótesis rival podría distinguirse con observaciones accesibles, no qué vía produce más tests.

## Hitos y aceptación

Cada hito en `PROJECT_STATE.json` incluye línea, resultado, estado, criterio de aceptación, dependencia y siguiente acción. `DONE` requiere un recibo que identifique evidencia y commit realmente probado. Un resultado listo para revisión humana queda `READY_REVIEW`; una imposibilidad externa queda `BLOCKED` o `PARKED` con condición de reapertura.

La investigación puede terminar correctamente en una refutación o un negativo discriminante. Un hallazgo positivo no es requisito para progresar. Tampoco se considera progreso científico una imposibilidad repetida ya conocida.

## Cómo evaluar este piloto sin fabricar un experimento

Registrar prospectivamente en cada handoff: capacidades aceptadas por el usuario, preguntas que cambiaron por evidencia externa, errores de traspaso detectados, bloqueos reintentados sin condición nueva y esfuerzo de mantenimiento. Comparar descriptivamente las próximas sesiones con este punto de partida; no inferir causalidad ni anunciar eficacia validada de AB por mejorar el registro. No ejecutar una campaña AB-META adicional por este documento.

## Continuidad entre conversaciones

El prompt estable remite a `START_HERE.md`; ese archivo remite al JSON de estado y a un briefing generado desde Git/Atlas/ledger. La información que avanza está en los artefactos versionados, no dentro del texto que pega el usuario. Si el chat no puede leer GitHub, debe decirlo y pedir la salida actual del briefing; no improvisar una continuidad basándose en cifras antiguas.
