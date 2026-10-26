# Politics Fantasy League · BR8N · cierre de ocho ciclos AB 3.2.1 con BRANCHING

**Fecha:** 26/10/2026. **Autorización:** 8 ciclos. **Resultado metodológico:** 8/8 fichas A–J completas, siete aceptaciones técnicas/documentales y una decisión de identidad `PARTIAL_R5`. **No son ocho investigaciones empíricas independientes** ni ocho validaciones de personas o partidos.

## 1. Novedad documental: candidaturas originales, no solo escaños

Se obtuvo directamente mediante HTTPS institucional y con SHA256 computado sobre bytes originales el [BOE-A-2023-15066](https://www.boe.es/boe/dias/2023/06/27/pdfs/BOE-A-2023-15066.pdf), resolución de candidaturas proclamadas para Congreso y Senado de junio de 2023: **4.298.580 bytes**, SHA-256 **`d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`**. Es una **segunda fuente original independiente como documento** de [BOE-A-2023-18907](https://www.boe.es/boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf), de resultados electorales, cuya conciliación original de 312 celdas sigue vigente. Ambas informan de **la misma elección**, por tanto no son replicaciones temporales ni estadísticamente independientes de un fenómeno.

La extracción automática deliberadamente acotada a **Albacete, candidaturas al Congreso, antes de comenzar la sección Senado** recuperó exactamente ocho listas, corroboradas por el texto del documento institucional: PSOE, FO, PP, PACMA, PUM+J, SUMAR, VOX y RECORTES CERO. Se conservaron siglas y orden, no nombres de personas ni perfiles políticos.

El [cruce de fuentes con aceptación exclusiva de siglas exactas y únicas](../../scripts/audit_candidacy_crosswalk.mjs), comprobado en **cuatro pruebas Node reales**, encontró **8/8 coincidencias únicas** entre esas etiquetas del BOE y el archivo provincial/nacional secundario del Congreso de 2023. De ellas, **cuatro etiquetas con candidatura publicada** obtuvieron votos a escala nacional pero **ningún escaño** en esa elección: **Frente Obrero, PACMA, Por Un Mundo Más Justo y Recortes Cero**. Los votos/escaños enlazados son **nacionales**, no votos provinciales de Albacete.

Esta observación no demuestra influencia causal ni pertenencia a un partido legal. Las **candidaturas**, los **partidos inscritos**, las **coaliciones**, las **personas** y su **representación en una legislatura** son unidades distintas. De particular relevancia es [JEC, acuerdo 78/2026](https://www.juntaelectoralcentral.es/cs/jec/doctrina/acuerdos?anyosesion=2026&idacuerdoinstruccion=147056&idsesion=1106&template=Doctrina%2FJEC_Detalle): en el caso analizado reconoce límites explícitos para reconstruir adscripción a formaciones integrantes de una coalición desde ciertos documentos electorales. Ese problema de identificación no queda resuelto por una coincidencia de siglas.

**Límites explícitos:** únicamente una provincia en una elección de 2023; no se han añadido otras 51 circunscripciones, no hay corpus completo de candidaturas ni registro completo RPP; **cero partidos jurídicamente reconciliados y cero personas incorporadas con roles históricos auténticos**. No es una valoración de mérito, orientación ideológica o influencia de nadie.

## 2. Producto real ejecutado en el navegador

Se ha publicado [catálogo oficial limitado](../../data/observatory/boe_2023_albacete_verified.json), [API de solo lectura](../../src/politics_fantasy/candidacy_api.py) en `GET /api/verified-candidacies` y panel de [Atlas electoral](../../src/politics_fantasy/web/app.js) con ocho etiquetas, referencia BOE, checksum original y advertencia de identidad. El API nunca devuelve perfiles de candidatos, direcciones, militancia o puntuaciones.

Las pruebas [GitHub Actions run 40315022251](https://github.com/GalexY3/Metodologia-AB/actions/runs/40315022251) verifican de forma nativa **tres jobs verdes**: capturas originales, Node + Python/HTTP local, y Chromium. Se observaron **ocho suites con 95 pruebas Node y 59 pruebas Python superadas**; Chromium abrió el proyecto, su panel de progreso, el mercado ficticio y el atlas, comprobó la presencia de las ocho siglas oficiales, y no detectó excepciones JavaScript no controladas. Se confirmó también el rechazo con HTTP **403** de una cabecera `Host` externa.

La inspección posterior detectó una discordancia de interfaz con la política CSP: las barras de progreso utilizaban estilos inline y la cabecera restringía `style-src 'self'`. Se ha reparado mediante **`<progress>` semántico y reglas externas CSS**, sin relajar CSP; existe además un test Chromium de las diez barras. **La nueva comprobación nativa del CSS de esa revisión posterior queda pendiente hasta observarla en el job más reciente**; no se atribuye retrospectivamente al green run previo.

Ningún test implica un despliegue público probado, autenticación multiusuario, test integral de accesibilidad, estudio con usuarios ni pen-testing. La aplicación permanece **en loopback, con jugadores y puntuaciones ficticias**.

## 3. Métrica de avance: V3 36,35 % sobre el mismo scope

[Scope V3](../../product/progress_scope_v3_20261026.json) y [snapshot](../../product/progress_snapshot_v3_20261026.json). El denominador sigue siendo **PFL-V1-20261026 (9 sublíneas y 36 hitos)**, con los mismos pesos. La ganancia **+0,900 puntos** procede de dos hitos de ingeniería: `ui.pages` sube de nivel 2 a 3 y `qa.endtoend` de 2 a 3 por ejecución nativa de Chromium/HTTP/Node/Python. La fuente BOE original de 2023 fortalece cobertura documental, pero no eleva `src.registry` ni `id.real`: no constituye registro de partidos ni de personas validadas.

| Sublínea | Peso | Revisión 2 | Revisión 3 |
|---|---:|---:|---:|
| Fuentes y datos | 18 % | 45 % | 45 % |
| Identidad, coaliciones e historial | 12 % | 40 % | 40 % |
| Acontecimientos políticos | 10 % | 32,5 % | 32,5 % |
| Investigación y evaluación | 14 % | 27,5 % | 27,5 % |
| Motor de juego | 16 % | 45 % | 45 % |
| Interfaz y experiencia de usuario | 10 % | 27,5 % | **32,5 %** |
| Seguridad, privacidad y licencias | 8 % | 20 % | 20 % |
| Pruebas y reproducibilidad | 8 % | 40 % | **45 %** |
| Operación y lanzamiento | 4 % | 17,5 % | 17,5 % |
| **Global** | **100 %** | **35,450 %** | **36,350 %** |

**Efecto del trabajo:** +0,900 puntos. **Efecto de cambio de alcance:** 0. Permanecen **seis puertas críticas de lanzamiento**: RPP/candidaturas originales nacionales, identidades reales multifuente, eventos de persona con tiempo verificable, autenticación, E2E completo más profundo y despliegue seguro. La puntuación de figuras reales permanece deshabilitada.

## 4. Adversarios, fallos y trazabilidad A–J

- **N01**: original BOE 15066 recibido y SHA256 comprobado, sin publisher-signed hash ni derechos de datos derivados certificados.
- **N02**: ocho candidaturas en Albacete, no más; parser rechaza límites/códigos inesperados y Senado, no presupone partidos.
- **N03**: cruce 8/8, cuatro sin escaños; se añade control con FO duplicado que suspende el match en vez de adivinar identidad.
- **N04**: **PARTIAL_R5**. Reglas de identidad preservadas, pero sigue sin haber padrón RPP ni perfiles de rol público ligados a personas.
- **N05**: API y panel documental local contrastados, sin puntuaciones de personas.
- **N06**: Chromium verdadero en CI, navegación funcional con fuente original.
- **N07**: Host 403 y protección de loopback, no seguridad multiusuario.
- **N08**: 8/8 A–J, priors, CI, progreso versionado, seis bloqueos intactos.

[Preregistro, con exposición de fuentes reconocida](PREREG.json) · [Evidencia nativa](NATIVE_EVIDENCE.json) · [Resultados individuales](RESULTS.json) · [Ledger 8 A–J](LEDGER.json) · [Priors PF-N01–N06](PRIORS_DELTA.md). Son ensayos de integridad documental e ingeniería. No comparar sus 154 tests técnicos con 154 observaciones sociológicas independientes.

**Gobernanza científica inalterada:** VSDS 1/3, CT2 multiactor 20/100 y predictiva parlamentaria 24/100, ordinales y no probabilísticos; N1/N2/N3 científicos confirmados nuevos = 0.

## 5. Siguiente cuello de botella y próxima campaña propuesta

La prioridad es dejar de ampliar indefinidamente un atlas histórico de etiquetas y **construir una cohorte auténtica de personas con candidaturas públicas verificadas en varias provincias, cambios de cargo/rol y fuentes legales correlativas**. Primero debe adquirirse una muestra original de RPP o de candidaturas con IDs/procedencia, registrar explícitamente las incertidumbres y evitar deducir afiliación privada a partir de una lista o coalición. En producto, avanzar hacia cuentas seguras y un piloto observable, no publicar el servidor local.

**Solicitud razonable: 10 nuevos ciclos BRANCHING, condicionados a evidencia**, incluyendo extracción mínima de candidatos públicos de fuentes originales y cotejo legal de organizaciones; revisión de licencias; fechas de publicación; QA multi-navegador/usabilidad; y primera prueba de un evento público atribuible sin puntuación de mérito. No repetir los mismos ocho partidos/siglas ni inflar el contador AB si las fuentes no se adquieren.

**SOLICITO BRANCHING 10 CICLOS**
