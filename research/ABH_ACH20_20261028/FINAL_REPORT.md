# Informe final · Politics Fantasy League · AB-H ACH20 · 28/10/2026

**Campaña:** `PFL-ABH-ACH20-20261028`. **Autorizadas 20; documentadas 20 A–J en alcance acotado; 0 inválidas; 0 de planificación; saldo 0.** Esta campaña es independiente de `MAIN20B`; C01 se había ejecutado en la sesión anterior y en esta continuación se completaron C02–C20. Cada ciclo tiene un `Cnn_PREREG.json` y un `Cnn_RESULT.json` versionados; [ledger](CAMPAIGN_STATUS.json) y [autorización](AUTHORIZATION.json). **20 ciclos no son 20 descubrimientos científicos**.

## Resultados verificados por ciclo

| Ciclo | Modo | Resultado concreto y prueba acotada | Límite explícito |
|---|---|---|---|
| C01 | AB-P | Catálogo de **90 logros** (10 por cada una de 9 ramas), interfaz de medallas en el Atlas y estado inicial 0/90. | Primera revisión estructural, sin navegador real. |
| C02 | AB-R | Localizados enlaces del catálogo oficial del Congreso a datos de votaciones JSON/XML/ZIP y una sesión concreta. | **Sin obtener bytes nominales originales, hash ni fecha de primera publicación.** |
| C03 | AB-R | Localizado XML de votación por expediente del Senado y condiciones institucionales generales de reutilización CC BY 4.0. | XML no recuperado; una licencia de reutilización no concede automáticamente base jurídica para crear rankings individuales. |
| C04 | AB-R | Identificados consulta del RPP y trámites de información/certificación del Interior con SIA. | **No hay corpus original completo** del Registro de Partidos descargado ni fechas individuales acreditadas. |
| C05 | AB-P | **JS original de logros ejecutado** en V8 con DOM simulado: 9 ramas, 90 medallas; control negativo por falta de baseline. | No Chromium, accesibilidad ni test real de usuario. |
| C06 | AB-P | Auditoría adversarial halló importaciones que aceptaban versión 999 y log de auditoría ausente, y desbloqueos sin evento. | Un historial sintácticamente coherente aún podría ser inventado. |
| C07 | AB-P | Guard de importación reforzado: versión/secuencia de eventos, nueve ramas congeladas y evidencia de desbloqueo. **10 controles V8** aprobados. | No hay firma criptográfica ni validación externa de la evidencia. |
| C08 | AB-R | **Cuatro recuentos agregados oficiales** en dos expedientes de la sesión del 23/07/2026: `130/000049` (348 y 344) y `130/000050` (348 y 347). | Refuta «expediente = votación», no valida votos nominales ni exhaustividad. |
| C09 | AB-META | Auditoría retrospectiva: medallas **Mi primer club** y **La puerta cerrada** adjudicadas de forma limitada, **2/90**; dos propuestas de logro rechazadas por evidencia insuficiente. | Historial de demo local; no certificación actual de seguridad o producto público. |
| C10 | AB-P | Prototipo de identificador compuesto de votación, separado del expediente; **5 controles V8** con cuatro agregados C08. | Índice interno de captura, **no** identidad nativa del voto ni integración real. |
| C11 | AB-R | Matriz de cinco finalidades que distingue reutilización institucional, RGPD art. 5/6/9 y perfiles políticos. | **Sin dictamen jurídico** ni autorización de scoring de personas reales. |
| C12 | AB-P | Reparado detector experimental de duplicados: el mismo ID externo de fuentes distintas ya no constituye automáticamente una colisión. Tres controles V8. | La clave de fuente no resuelve la equivalencia entre archivos del mismo emisor. |
| C13 | AB-P | Reparada auditoría de referencias de `claims` con fuente/persona ausente; antes devolvía `ok=true` en el caso negativo. | Control de integridad, no certificación de fuente. |
| C14 | AB-P | Rechazo de fechas imposibles/etiquetas arbitrarias y booleanos en `rolling_origin_splits`; nuevo pytest; **5 comprobaciones de reconstrucción aislada** validadas posteriormente. | No se ha importado/ejecutado el módulo en un checkout limpio ni la suite pytest de ese cambio. |
| C15 | AB-P | Guarda contra identificadores vacíos en red de covotación, que podían crear pares espurios; nuevo pytest; **4 controles aislados** comprobados posteriormente. | No hay análisis de relaciones políticas reales ni ejecución de toda la suite Python. |
| C16 | AB-P | Fuente JS antes aceptaba URL HTTPS con credenciales `usuario:contraseña@`; guarda acotada y **3 controles V8**. | Limpieza sintáctica no prueba autenticidad de un editor institucional. |
| C17 | AB-P | La pestaña activa de la interfaz tiene ahora `aria-current="page"`; **4 controles de DOM simulado**. | No es un certificado WCAG ni prueba de lector de pantalla. |
| C18 | AB-P | Diferenciados **CT2 predicción histórica 24/100** y **CT2 identidad 29/100** en la pantalla, sin alterar valores. Cinco verificaciones estáticas. | No se ha recalibrado ninguna serie CT2. |
| C19 | AB-META | **18 pares** prereg/resultado con A–J completos, E sustantiva, **5 contrastes** de ancestro Git positivos. | Auditoría documental; solo muestra temporal de cinco pares. |
| C20 | AB-META | Auditoría de cierre: **19 pares preexistentes**, **38 archivos**, C19 con A–J, **75 lotes Atlas documentales**, registro de logros v3 y T009/T010 reconciliados; cronología adicional C19 verificada. | **No** existe replay nativo Atlas75 ni test Linux sobre todos los cambios de esta campaña. |

### Contraste de fuentes institucionales

- **Congreso**: catálogo oficial [votaciones](https://www.congreso.es/es/opendata/votaciones), muestra agregada específica [C08](C08_CONGRESO_AGGREGATE_SAMPLE.json), y prueba de doble voto/expediente. La página HTML y la transcripción son una muestra exploratoria, no un original binario validado.
- **Senado**: [catálogo oficial de votaciones](https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/votaciones/index.html?lang=es_ES), enlace concreto a un XML y [condiciones de reutilización](https://www.senado.es/web/relacionesciudadanos/datosabiertos/reutilizacion/index.html). Sin bytes XML obtenidos.
- **Interior**: [consulta del RPP](https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos) y procedimientos de la sede para obtener información/certificados, sin corpus completo de partidos.
- **RGPD/AEPD**: [Reglamento (UE) 2016/679](https://eur-lex.europa.eu/legal-content/ES/TXT/?uri=celex:32016R0679) y matriz [C11](C11_LEGAL_PURPOSE_MATRIX.json). Finalidad, fundamento legal y derechos sobre fuentes son controles diferentes.

No se han subido originales nominales privados ni vinculado puntos de juego con personas públicas reales.

### Medallas en el Atlas

El [salón de logros](../../ab_atlas/ACHIEVEMENTS_Atlas_Politics_Fantasy.html) está integrado en la quinta pestaña del [visor AB Atlas](../../ab_atlas/AB_Atlas_Politics_Fantasy.html), usando el [registro versionado](../../ab_atlas/ACHIEVEMENTS_REGISTRY.json), **90 activos y dos adjudicados**: `PFL-GAME-01` «Mi primer club» (demo local funcional) y `PFL-SECURITY-01` «La puerta cerrada» (defensas limitadas de localhost). **2/90 = aproximadamente 2,22 % simbólico**. No significa que el resto de metas estén todas sin avanzar: falta adjudicar evidencia. Las nuevas pruebas no han desbloqueado insignias de investigación, UI completa o calidad de producción.

Los logros pueden editarse, crearse, retirarse y restaurarse con historial, pero **editar el navegador no escribe automáticamente en GitHub**; exportar/importar el JSON y revisar antes de un commit. El registro de logros nunca cambia por sí solo V4 ni los gates.

## Estado verdadero del proyecto al cierre

| Indicador | Valor | Qué significa |
|---|---:|---|
| **Madurez contractual V4** | **36,90 %** | Última evaluación aprobada de 36 hitos. **No recalculada por cantidad de ciclos.** |
| CT2 identidad | **29/100** | Escala ordinal; no probabilidad. |
| VSDS | **1/3** | Instrumento de utilidad local; no demostración de valor de campo de nivel 2. |
| N1 / N2 / N3 nuevos | **0 / 0 / 0** | Ningún descubrimiento nuevo de grado científico acreditado. |
| Gates críticos aprobados | **0/6** | **No lanzar una plataforma pública ni scoring de personas reales.** |
| Atlas de metodología | **75 deltas JSON documentales** | Conteo de archivos, **checker canónico y SHA del estado siguen UNKNOWN**. |
| T009 | **COMPLETADA_CON_FALLOS** | En `8a761cf`: 757 Python PASS, 1 FAIL, 28 subtests PASS, 127 Node PASS; Atlas SyntaxError. |
| T010 | **PENDIENTE** | Reparar checker Atlas y prueba de codificación HTTP, después volver a ejecutar las suites. |

**Precisión QA:** durante ACH20 se ejecutaron controles V8/DOM simulado y se escribieron nuevos tests Python/Node. Los **nuevos archivos de test aún no se han ejecutado mediante un runner integral del checkout**, ni se ha certificado el render en navegador real. Los controles aislados de C14/C15 se reprodujeron en Python por copia de la función, **no importando el módulo original instalado**. Los tests integrales de T009 corresponden a un commit anterior a ACH20; no cubrirían sus modificaciones posteriores. No declarar CI verde ni Atlas reparado.

## Bloqueos y decisión R5

1. **QA P0 T010**: corrupción previa de `ab_atlas/atlas_delta.py`, suite actual incompleta. Los deltas históricos no se reescribieron ni se hizo un «0076» para aparentar progresos.
2. **Originales accesibles**: faltan originales nominales autenticados XML/JSON con hashes y disponibilidad histórica, corpus completo RPP y reconciliación por institución. Un catálogo accesible no es un corpus.
3. **Estimando empírico**: faltan cohortes con denominadores y exposición verificable, controles fuertes y muestras temporales verdaderamente independientes. Ningún módulo sintético sustenta todavía VSDS 2/3.
4. **Protección de datos y lanzamiento**: faltan decisiones jurídicas por finalidad, autenticación multiusuario y los seis gates completos.
5. **Experiencia de usuarios**: no hay prueba independiente de accesibilidad ni un piloto consentido; las medallas de UX permanecen pendientes.

**AB-DECIDE:** **campaña ACH20 cerrada** por agotamiento de las veinte autorizaciones **efectivamente utilizadas**; 0 saldo. No consumir nuevos ciclos automáticamente. La próxima acción de mayor valor no es repetir controles sintéticos de la misma clase: ejecutar T010 sobre HEAD nuevo y asegurar originales institucionales que permitan un primer análisis de campo con denominadores y tiempo `as_of`. Sin esas dependencias aplicar R5 y detener la repetición de pruebas.

**Solicitud condicional para una siguiente fase:** una vez concluida T010 y obtenido un corpus original nuevo reproducible, tendría sentido pedir autorización para **PIVOT de 20 ciclos** centrados en evaluación real de identidad, cobertura, investigación sociológica y pilotos; esta frase es una propuesta, **no una autorización ni ejecución**.
