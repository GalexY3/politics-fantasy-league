# PFL · demo local con datos institucionales completamente ficticios

**NO es un estudio autorizado para humanos.** No recoge, envía ni conserva respuestas. No califica políticos, candidatos o partidos reales.

Se requiere **Node 20+**. Desde `proyectos/politics-fantasy-league` ejecutar `node pilot_local/server.mjs` y abrir manualmente `http://127.0.0.1:8787`. Para parar el servidor, Ctrl+C. No publicar el puerto por proxy ni en internet.

La interfaz contiene cuatro vistas manualmente seleccionables: tutorial neutro o de denominador × información agregada o leaderboard de avatares imaginarios. Las cuatro preguntas de transferencia proceden de `src/politics_fantasy/fictional_transfer_items.mjs`. No incorpora `fictional_transfer_key.mjs`, `pilot_dryrun_intake.mjs` ni `pilot_analysis_dryrun.mjs` en las rutas del servidor. **Las respuestas no se puntúan**; el navegador solo recuerda temporalmente las selecciones hasta cerrar o recargar.

El servidor sirve únicamente `/`, `/index.html`, `/app.mjs`, `/style.css`, `/materials.mjs`. Vincula explícitamente `127.0.0.1`; solo GET/HEAD; POST/PUT/DELETE = 405; path o query no declarado = 404. Sin cookies, telemetría, almacenamiento, analytics, formulario de envío ni servicio de recogida. Cabeceras `CSP`, `no-store`, `nosniff`, `no-referrer`, permisos restrictivos. Verificar con `node pilot_local/smoke_http.mjs`.

## Límites y puertas

- El juego local permite **seleccionar libremente un brazo**; no es asignación aleatoria de personas.
- Los tutoriales difieren en contenido y pueden diferir en carga cognitiva; no hay paridad temporal comprobada con usuarios. No son aún estímulos finales de un experimento.
- No se ha medido usabilidad ni fiabilidad psicométrica con personas. Los cuatro ítems podrían filtrar enseñanza o presentar efecto techo.
- Un navegador local, extensiones o software del equipo podrían observar el contenido; no afirmar garantías de privacidad del host.
- Los validadores `pilot_dryrun_intake.mjs` aceptan una **aprobación simulada falsificable**, de modo que no deben usarse en enrolamiento ni RGPD real.
- No hay aprobación ética, tratamiento personal autorizado, reclutamiento ni seguimiento. Cualquier estudio de verdad necesitaría revisión institucional, infraestructura segura, información/consentimiento de adultos y preregistro final.
