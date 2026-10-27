# Continuación coordinada de Politics Fantasy

Trabaja desde la rama **`research/pfl-codex-contributions-20261027`**, que integra el cierre de ChatGPT `1f2dd59` y los nueve ciclos CDX01–CDX09 de Codex. Lee primero `AGENTS.md`, `ab_atlas/CURRENT.md` y los resultados de la pieza que vayas a modificar. Conserva ambos historiales y no fusiones a `main` por tu cuenta.

La campaña AB-H45 cerró A01–A20, R01–R05 y B01–B20: **45/45**, sin ciclos pendientes de ese bloque. El usuario también autorizó a Codex una línea abierta separada. No presentes los nueve CDX como parte de los 45 ni inventes cuotas o resultados. Antes de continuar ciclos en este chat, interpreta la autorización vigente del usuario y aplica R5 y el contrato AB; si hace falta una autorización adicional, solicítala con un objetivo concreto.

El Atlas integrado conserva la secuencia de ChatGPT 0012–0015 y reencadena el lote Codex como 0016, conservando el original en Git. Se ejecutó el validador Python oficial: 16 lotes, 58 nodos y hash `3168eab0eadab0f2900e2ab0bb0c2aa6f40a4a381e83fca9cf782d84899aeb4d`. Haz `fetch` y comprueba el último lote antes de escribir otro: si hay trabajo concurrente, reconcilia padres y contenido en vez de sobrescribirlo.

Prioriza el flujo de ingesta y sus fronteras, con una comprobación reproducible y fixtures ficticios:

1. Examina `src/politics_fantasy/ingest.py`: el cliente local usa redirecciones de `urlopen` y actualmente comprueba el destino final después de abrirlo. Verifica cada salto antes de contactar un destino no permitido, incluye cadena de redirecciones y emparejamiento fuente/host, con pruebas negativas controladas. Esto es un hallazgo local de código; no se ha demostrado una ruta HTTP explotable.
2. Diseña y prueba un flujo integral de captura/ingesta, validadores originales y cuarentena, con pruebas HTTP solo donde exista esa interfaz. Distingue el catálogo HTTP de fuentes y la simulación de jornada de una ingesta real completa: ambos se prueban, pero no son ese E2E. No introduzcas originales privados ni datos nominativos en Git.
3. Mantén la semántica de `NO VOTAN` como interpretación operativa pendiente de documentación institucional. La coherencia interna de los XML y JSON no certifica identidad, semántica jurídica ni `first_public_at`.
4. Registra evidencia, negativos, límites y cualquier delta de Atlas; ejecuta la suite pertinente y mantén explícitamente V4 36,90 %, CT2 identidad 29/100, VSDS 1/3 y gates 0/6 salvo que una evaluación válida y documentada justifique cambiarlos. Sin Actions innecesarias.

La validación posterior a la integración produjo 404 tests Python y 14 subtests aprobados, 1 omitido por enlaces simbólicos en Windows; 110 tests JavaScript y el smoke de juego Chromium aprobados. Son resultados locales en ese entorno, no validación de producción ni de fuentes reales de extremo a extremo.
