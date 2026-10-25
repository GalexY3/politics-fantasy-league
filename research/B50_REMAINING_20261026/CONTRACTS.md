# PF-B50-39–50: fuente electoral nueva y producto · contratos adaptativos

Fecha 2026-10-26. Doce plazas autorizadas heredadas de PF-B50. **Los desarrollos electorales de esta sesión comenzaron antes de congelar este documento**, por lo cual los contrastes son **post-exposición**, no preregistro confirmatorio. No se comparan resultados oficiales originales.

- 39: capacidad de NO simular descarga gubernamental inexistente, fail-closed para fuente oficial.
- 40: parser RFC4180 para CSV con comillas, columnas y valores Unicode.
- 41: fichero histórico secundario de rOpenSpain, 1.057 filas, años y códigos, sin igualar código a partido jurídico.
- 42: fichero provincial 2023 de anerodata: todos los 52 registros tienen columnas homogéneas y números válidos.
- 43: labels con votos sin escaños representados explícitamente, sin ranking ni inferencia de influencia.
- 44: metadato 2023 incluye 59 etiquetas y 52 circunscripciones; no son 59 partidos independientes.
- 45: manifiestos de SHA Git y URL, sin simular validación criptográfica original externa.
- 46: tipificación UNKNOWN independiente de ABSENT y PRESENT; no imputación de cargos personales.
- 47: no fusionar nombres ni codes de fuentes que no comparten años (1977-2019 vs 2023).
- 48: adaptador lectura JSON rechazando datos no certificados, pruebas de integridad.
- 49: capa visual con 59 opciones en orden alfabético y alerta de evidencia.
- 50: API local /api/electoral-atlas y capa de juego separados, prohibición de score personas reales.

Todos A–J: A endpoint anterior, B rival «parlamento basta, no importan escaños cero» y alternativas de artefacto fuente; C test en harness + controles; D scripts; E resultado real de suite reproducible o impedimento explícito; F sesgo de fuente; G sin replicación oficial independiente; H actualización instrumental, no sociológica; I VSDS1/3, N2/N3=0; J CONTINUE/REPAIR/STOP.
