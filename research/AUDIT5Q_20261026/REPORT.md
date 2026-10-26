# AUDIT5Q: cinco ciclos AB de revisión integral con reparación

**Cerrados 5/5**, completos A–J; [PREREG](PREREG.json), [RESULTS](RESULTS.json), [LEDGER](LEDGER.json). Se revisó procedencia documental, API, seguridad de ingestión, navegador, puntuación de progreso y estado de fuente.

**Hallazgo 1.** El original BOE 2023 tiene 52 secciones provinciales. La extracción previa llamaba verificadas a 25 con secuencia continua cuando **9 además contenían avisos sobre no proclamación**. Se ha distinguido 16 sin avisos conocidos, nueve que requieren interpretación, 27 con numeración incompleta; 263 candidaturas extraídas. Fuente única histórica, no registros jurídicos actuales.

**Hallazgo 2.** El almacén `evidence_warehouse.mjs` comprobaba claves sensibles solo en el nivel superior; aceptaba atributos anidados como `participants[].metadata.party_member_guess` pese a que más tarde se eliminaran en la normalización. Se reparó con recorrido recursivo, límites de profundidad y rechazo de claves especiales de prototipo. Se añadieron **seis tests Node adversariales**, con fallo-antes/reparación-después. No supone una auditoría de seguridad completa.

**Hallazgo 3.** Una nueva prueba real de Chromium fallaba al comparar «Provincias comprobadas» literalmente, cuando CSS `text-transform` había mostrado la etiqueta en mayúsculas; el texto sí estaba visible y la API local devolvía los datos. Se sustituyó por comparación insensible a mayúsculas, se añadió verificación explícita de la API y se reparó la etiqueta demasiado optimista. El atlas usa 16/9/27 y advertencias.

**Hallazgo 4.** La métrica de progreso se revisó sin manipularla: **V3 36,350 % permanece** durante la auditoría. Los hitos de registro jurídico/identidad temporal/usuarios reales/despliegue no se cierran por 263 siglas y los seis bloqueos críticos siguen activos.

**Hallazgo 5.** [GitHub Actions run 40324283292](https://github.com/GalexY3/Metodologia-AB/actions/runs/40324283292) terminó con tres trabajos `success` (pruebas Node/Python, extracción fuente oficial y Chromium). Los fallos anteriores están preservados; no se finge primera pasada perfecta.

**Decisión J:** `CLOSE_AUDIT5Q / FOCUS_NEXT20_ON_ORIGINAL_SOURCE_QUALITY`. Los cinco ciclos de revisión están agotados. La corrección sustantiva es precisar la confianza en lo observado, no elevar VSDS ni CT2. N1/N2/N3 nuevos = 0.
