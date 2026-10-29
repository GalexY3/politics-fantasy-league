# Politics Fantasy League · BROWSER_ATLAS_EVIDENCE5 · cierre limitado R5 · 29 octubre 2026

**Autorización 5 ciclos A–J. Resultado real: 2 válidos, 1 intento incompleto/no válido y 2 no ejecutados.** **No se han gastado artificialmente las plazas**: quedan **2 sin ejecutar** que pueden usarse cuando una fuente o ejecutor competente permita un nuevo contraste. Tres preregistros adicionales C02/C04/C05 no constituyen resultados válidos. Rama `research/pfl-abh5-browser-atlas-independent-20261029` creada exactamente desde HEAD verificado de PR #36 `9ce1ecbfe35038c4723f0765a1c6b817fa4ea5d6`.

[Ledger y límites](CAMPAIGN_STATUS.json) · [fuentes y priors](SOURCES_AND_PRIORS.json) · [CT2 escala completa + ampliada](CT2_FULL_AND_ZOOM.svg) · [tarea T028](../../tareas_codex/T028_BROWSER_ATLAS_REPLAY_20261029.md).

## C01 · AB-P válido acotado: Chromium real, sin navegación HTTP

[Prereg](C01_PREREG.json) `75cee495e3c5de60e04e7c4276b4dc9292bb76ae`, [resultado A–J](C01_RESULT.json).

Pregunta A: ¿puede Chromium representar y operar la interfaz PFL ficticia? Rivales B: UI operativa; error app; o limitación del navegador/entorno. C: cotejar código original por Git blob, probar 4 brazos, 4 preguntas, 12 radios, textos, cambio de condición, reinicio, visualización 375 px y errores JS. D–E: Chromium real **144.0.7559.96**, fuente local igual que los cinco Git blobs del servidor/cliente originales. **Se intentó navegar por HTTP a localhost, file:// y data:** y en los tres casos Chromium devolvió `ERR_BLOCKED_BY_ADMINISTRATOR`. Por tanto **NO hay test HTTP browser completo**. En una página Chromium `about:blank` se cargó el HTML/CSS/JS del cliente original, sustituyendo **solo** el import de módulo por la función fuente inline para evitar la navegación vetada. Se comprobó 18/18 comportamiento DOM y versión móvil sin desbordamiento; imágenes en sesión local (no subidas como PNG a GitHub).

**Errata del harness:** 16/18 al principio porque dos asertos esperaban el literal «denominadores», cuando el texto auténtico es «Cómo se contabilizan las oportunidades». Se corrigieron los asertos de test, no el código, y se repitieron: **18/18**. F: el resultado **no valida CSP real ni integración HTTP**, no demuestra accesibilidad completa, paridad cognitiva de los tutoriales o despliegue. G: ingeniería local, no replicación científica. H: prior de imposibilidad total de DOM en Chromium debilitado. I: 0/3, CT2 no sube. J: continuar por Atlas independiente.

## C02 · intento de Atlas incompleto, NO contado

[Prereg](C02_PREREG.json) `4df22b87d4229cf6aa04514f5616fd7ac34588b4`, [resultado parcial con límites](C02_INCOMPLETE.json).

A: ejecutar `python ab_atlas/atlas_delta.py check` realmente desde repositorio completo. B: cadena válida o errores de operaciones/grafo. C–D: parser oficial identifica `batch_check`, `replay` y `abmap.require_valid(strict=True)`, y requiere `seed.json` más **79 lotes**. E: se obtuvieron y parsearon por conector GitHub los **79 lotes 0001–0079** en grupos y se verificó continuidad de `parent_batch` (sin fallos observados). F: esa comprobación NO sustituye la reproducción canónica; el contenedor no dispone de checkout autenticado ni de todos los ficheros para ejecutar Python y el estado/hash del grafo no se calculó. La carpeta histórica `CURRENT.md` estaba desincronizada desde 0078. El lote 0079 declara `at=2026-10-29T01:00:00Z`, posterior a la hora real de creación de este 0080 (`00:26Z`); se conserva el timestamp auténtico del nuevo lote y se advierte la anomalía temporal. G: sin repliegue independiente. H–J: bloqueo local de reproducción, **intento incompleto no válido**; T028 requiere ejecución nativa, no se falsean puntos ni éxito.

## C03 · AB-R válido documental, novedad contraria

[Prereg](C03_PREREG.json) `05c4695254243bbbd9dc40ded9ad509225bae703`; [resultado A–J](C03_RESULT.json).

La búsqueda independiente de trabajos recientes concluye que la novedad de los **mecanismos generales** ya tiene antecedentes fuertes:
- [Frongillo et al., AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/33517): competiciones predictivas con acontecimientos correlacionados, con límites matemáticos según correlación por bloques.
- [Monroe et al., AAAI 2025](https://ojs.aaai.org/index.php/AAAI/article/view/33533): el ganador por scoring total puede incentivar coberturas de predicciones incluso con numerosos eventos.
- [Lemus, RAND Journal 2025](https://onlinelibrary.wiley.com/doi/10.1111/1756-2171.70019): premios contingentes, modelo estructural y RCT en concursos.
- [Lemus y Marshall, JPE 2021](https://www.journals.uchicago.edu/doi/10.1086/711762): rankings públicos, participación/abandono y evidencia de estudiante/concursos; editor publicita un «Data Archive».
- [John Marshall, Journal of Politics 2019](https://www.journals.uchicago.edu/doi/10.1086/700199): señalización/reputación y adquisición de información política en investigación experimental/observacional.

Estos trabajos son **evidencia independiente de antecedente** y reducen la justificación para anunciar una teoría novedosa de leaderboards, señales de conocimiento o correlación de eventos en PFL. No demuestran automáticamente el efecto específico de una combinación «explicación de denominador × leaderboard ficticio»: queda como pregunta a verificar con personas bajo protocolo ético. **No se recuperó ningún panel longitudinal de contestantes con bytes originales, licencia, hash, esquema y marcas temporales verificadas**; no hubo ensayo, regresión ni causalidad con usuarios PFL. La novedad general se rechaza; la particular permanece no contrastada. Por esta mayor presión de antecedentes, CT2 prospectivo pasa ordinal/provisional de **25 a 22**; identidad 29 y mecanismos sintéticos 20 son líneas separadas, no comparables como mejora.

## C04 y C05 · NO EJECUTADOS

C04 dependía de un **defecto real de aplicación** para reparar, pero la navegación fue bloqueada por política del entorno y la lógica DOM pasó 18/18: no se abrió ciclo de parche redundante. C05 requería datos empíricos independientes con permiso de reutilización y variables verificadas; no se consiguieron. Ambos permanecen preregistrados como **NOT_EXECUTED**, sin ocupar plazas ejecutadas.

## Estado y reglas de gobierno

Se ha creado el lote append-only [0080](../../ab_atlas/updates/0080-pfl-abh-browser-atlas-evidence-partial-20261029.json), con **solo dos `run.add`** para los ciclos que sí se ejecutaron. `CURRENT.md` canónico **no se ha regenerado**, ya que sería incorrecto certificar replay Python sin haberlo realizado. Se conserva un [resumen Atlas complementario](../../ab_atlas/CURRENT_BROWSER_ATLAS_EVIDENCE5.md).

R1: resultado de UI no es conducta política. R2: Chromium contra fuente idéntica; control de dependencia nativa Atlas aún ausente. R3: hashes fuente y prereg antes de operaciones; selección de ramas adaptativa. R4: fallos harness, bloqueo administrador, error cronológico previo y fuerte prior art. R5: **STOP_LOCAL** sin acceso a ejecución Python canónica o microdatos independientes; las dos plazas no ejecutadas no se queman. Sin ChatRelay, CI costosa, merge a main, recogida personal, participantes o puntuaciones de políticos reales.

VSDS 1/3, V4 contractual 36,90%, logros 2/90, gates 0/6, N1/N2/N3 nuevos 0/0/0. No se propone autorización nueva mientras queden plazas concedidas; para reanudar el siguiente contraste hay que satisfacer el bloqueo de T028, o presentar una fuente de nueva calidad.
