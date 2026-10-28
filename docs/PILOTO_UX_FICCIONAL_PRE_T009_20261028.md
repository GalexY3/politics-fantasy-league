# Preparación independiente de T009 · piloto de comprensión y usabilidad de Política Fantasy
**Fecha:** 28/10/2026 · **Estado:** protocolo diseñado; **NO ejecutado** · **Tipo de trabajo:** preparación de producto/investigación, **NO** ciclo AB-H, no consume presupuesto.

## Alcance y fuente de verdad
Se ha revisado el `main` de `GalexY3/Metodologia-AB` en commit `8a761cf3081b7d09dae6cacb9f58fa58192863e4`, mediante lectura de `src/politics_fantasy/web/index.html`, `src/politics_fantasy/web/app.js`, `docs/PRODUCTO_LOCAL_v0_2.md`, `docs/ARQUITECTURA.md`, `docs/VSDS_PROYECTO.md`, `docs/PLAN_TFM.md` y registro MAIN20B. **No se ha abierto el navegador, no se han reclutado personas ni ejecutado pruebas de interfaz.** El contrato de T009 es previo a pruebas de usuario con el prototipo actual.

El producto cuenta con pestañas **Visión general / Mi club / Mercado / Jornadas / Observatorio / Atlas electoral / Progreso del proyecto**; backend local en `127.0.0.1`, 10 figuras ficticias `F01–F10`, límite de cinco fichajes, tres titulares por jornada, créditos de prueba, puntuaciones sintéticas y observatorio separado. **No existe autenticación multiusuario ni un score político real validado**.

## Objetivo evaluable
**Pregunta de producto:** ¿puede una persona nueva manejar el prototipo ficticio y distinguir sus reglas lúdicas de los datos parlamentarios y del progreso científico real?

No confundir *completar una tarea de interfaz* con demostrar utilidad sociológica. Dos resultados independientes:
1. **Usabilidad del juego:** cumplimiento de tareas, errores, pasos, tiempos y explicaciones de los participantes.
2. **Comprensión epistemológica:** reconocer explícitamente que personajes y puntos son ficticios, que los agregados del observatorio son exploratorios y que el índice de progreso no mide probabilidad ni preparación para el lanzamiento.

**No** usar nombres de políticos reales, identificadores personales, datos nominales o interpretación de comportamiento político.

## Diseño preparatorio (NO trabajo de campo realizado)
- **Muestra propuesta:** 6–8 personas adultas voluntarias, varias sin experiencia en fantasy; conveniencia declarada, sin pretensión de representatividad estadística. Consentimiento específico si se ejecuta: observación local y notas desidentificadas. No grabar audio, pantalla, IP, nombre real ni correo sin una justificación y consentimiento separados.
- **Entorno:** localhost en máquina del investigador, con base sintética nueva por sesión. Primer ensayo interno solo **después de T009 PASS o de un entorno de pruebas verificado**, con copias del estado anterior; sin conexión a servicios externos ni acceso a información real.
- **Diseño:** protocolo intra-sujeto, tareas en un orden fijo, sin ayuda inicial; registrar ayudas como fallos de autonomía, no como éxito espontáneo. No comparar eficacia entre variantes inexistentes ni inferir causalidad.
- **Variables básicas:** éxito autónomo (0/1), segundos por tarea (si se cronometra con consentimiento), número de intentos/errores, ayuda requerida (0/1), comprensión final por pregunta, comentario libre. Registrar versiones exactas de código/interfaz y estado inicial de partida.
- **Evitar fingir métricas:** no fijar umbrales «alcanzados» a priori. Se proponen como objetivos iniciales tentativos: al menos 5/6 completan fichaje/guardado sin asistencia; al menos 5/6 distinguen scoring ficticio del observatorio; revisar metas con el investigador antes de analizar datos.

## Guion de tareas, órdenes neutrales y criterios de aceptación
| Código | Instrucción a participante | Evidencia observable | Riesgo |
|---|---|---|---|
| U1 | «Encuentra dónde se ve el dinero de tu club y explica qué representa.» | Identifica saldo como **créditos ficticios**, no dinero real. | Confundir créditos con dinero o premio. |
| U2 | «Busca una figura disponible y añádela a tu plantilla si tienes saldo.» | Navega a **Mercado**; entiende precio y disponibilidad; comprueba saldo posterior. | No entender propiedad exclusiva o precio fijo. |
| U3 | «Elige tres titulares y guarda la selección para la próxima jornada.» | Navega a **Mi club**, selecciona **tres** y guarda antes del bloqueo. | No entender «plantilla 5» frente a «titulares 3». |
| U4 | «Busca la jornada anterior y explica de dónde salen sus puntos.» | Encuentra **Jornadas**, reconoce que son eventos inventados, no una valoración real del diputado. | Leer score como mérito o productividad política. |
| U5 | «Mira el observatorio y dime si sus recuentos se usan para dar puntos a las figuras.» | Responde **no**; indica que los agregados son transcripción exploratoria separada. | Mezcla fuente real descriptiva con score ficticio. |
| U6 | «Abre el progreso del proyecto: ¿qué significa 36,9 %? ¿Permite lanzar un ranking real?» | Interpreta **madurez contractual**, no probabilidad, y responde **no** al lanzamiento. | Confundir progreso contractual, preparación jurídica y validez científica. |
| U7 | «Busca algún lugar donde se expliquen los límites o fuentes del atlas electoral.» | Encuentra **Atlas electoral** o advertencia de fuente, no interpreta candidatura como mandato efectivo. | Inferir identidad o cargo no certificado. |

Los investigadores no deben sugerir el botón concreto antes de cada tarea. Se pueden recoger los errores y reformular instrucciones **en una siguiente versión**, documentándolo como cambio del instrumento.

## Comprobaciones de comprensión, antes/después
Al principio, sin explicar el producto: «¿Qué esperarías que midiese un fantasy de política?» (respuesta abierta, para identificar expectativas).

Al final, sin enseñar respuestas:
- «¿Las diez figuras representan personas del Congreso?» **Correcto:** no, son figuras ficticias.
- «¿Una puntuación baja indicaría que un político real es peor representante?» **Correcto:** no; el juego no valida esa interpretación.
- «¿Los recuentos parlamentarios que ves se transforman ahora en puntos?» **Correcto:** no; capa observatorio y demo segregadas.
- «¿El porcentaje de progreso equivale a la probabilidad de que la web sea segura para publicar?» **Correcto:** no; índice ponderado de madurez contractual con gates sin superar.
- «¿Qué cambiarías para entender mejor cuándo una fuente es auténtica o solo exploratoria?» Abierta.

**Código de análisis propuesto:** respuestas correctas, erróneas, inciertas y «no sabe», separando comprensión de usabilidad. No imputar una respuesta equivocada como desinformación política del usuario; puede señalar copy o arquitectura de interfaz confusa.

## Auditoría documental estática detectada antes del piloto
En `src/politics_fantasy/web/app.js`, la función de vista **`overview()`** contiene texto visible: `CT2 para investigación predictiva: 24/100` y el indicador **vigente de MAIN20B** es `CT2 identidad 29/100 ordinal` (métricas vinculadas, pero **no necesariamente idénticas**; debe aclararse a qué submétrica se refiere cada número antes de cambiarlo). Por tanto, **no sustituir 24 por 29 automáticamente**: verificar definiciones y versión de ambas series. Registrar como **riesgo de copy desactualizada o ambigua**, sin declarar defecto demostrado hasta contrastar el alcance exacto de CT2.

El documento `docs/PRODUCTO_LOCAL_v0_2.md` conserva una frase histórica («no se ha conseguido guardar este árbol en GitHub», error 403) que ya no es un estado vigente, puesto que `main` sí está disponible. **No reescribir el informe histórico**; enlazar al `ab_atlas/CURRENT.md` actual si se expone al usuario.

La UI conserva un encabezado de prototipo **v0.6.0** mientras el estado backend declara `version: 0.2.0-product-demo`; podría ser versionado distinto de frontend/producto, **no debe imponerse igualdad sin definir semántica**.

## Entregables posteriores (dependencias)
1. **T009**: checkout limpio del HEAD posterior, suite Python/Node, checker canónico Atlas 75 y pruebas de nuevas regresiones; sus fallos quedan separados de este protocolo.
2. **Ensayo técnico interno**: una única sesión con base sintética nueva; revisar que U1–U7 no requieren estado imposible ni información externa. Registrar los errores sin elevar el nivel de progreso.
3. **Estudio piloto real**: reclutar voluntarios y recabar notas anónimas solo con consentimiento y procedimiento adecuado; no iniciar por el mero hecho de haber escrito este documento.
4. **Resultado**: tabla de tareas, completitud y comprensión con N real y versiones exactas; decisión de producto que revise el copy/tareas si se observan fallos. Un N=6 descriptivo no valida validez externa ni el diseño sociológico.
5. **Línea científica complementaria**: mantener el estimando predictivo del `docs/PLAN_TFM.md` separado del ensayo de UX; la versión de juego sirve como instrumento y no sustituye corpus temporal original, baseline fuerte ni evaluación fuera de muestra.

## Decisión
**SE PUEDE AVANZAR EN DOCUMENTACIÓN Y PREPARACIÓN DE UX SIN T009.** Se ha terminado el protocolo, no el piloto. No se han consumido ciclos AB-H nuevos, ni se ha modificado código o tests, ni se ha validado un scoring real. Si T009 falla, **congelar ensayos de usuario** y reparar por un proceso trazable, sin borrar esta versión de protocolo.
