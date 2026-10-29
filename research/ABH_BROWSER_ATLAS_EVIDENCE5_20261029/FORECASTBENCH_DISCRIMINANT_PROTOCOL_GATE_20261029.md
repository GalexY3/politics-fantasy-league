# ForecastBench → PFL: puerta de identificación y contraste (sin experimento ejecutado)

Fecha 2026-10-29. **Investigación de factibilidad y protocolo de identificación, no ciclo A–J, no consumo de las dos plazas AB-H pendientes.** Rama sucesora de PR #38. Se basa en la auditoría de fuente y licencia `FORECASTBENCH_EXTERNAL_DATA_GATE_20261029.md`.

## Pregunta discriminante

¿Mejora un ajuste por *oportunidades efectivamente visibles/eligibles* la comparación de pronosticadores frente al **difficulty-adjusted Brier score** ya publicado por ForecastBench, manteniendo fijas dificultad, calendario, selección de preguntas y precisión probabilística? Esta pregunta **no equivale** a preguntar si los modelos difieren en dificultad: ForecastBench ya aborda esa cuestión. La variable de exposición visible es el requisito identificador crítico.

### Datos y niveles de observación disponibles

La fuente pública CC BY-SA 4.0 `forecastingresearch/forecastbench-datasets` publica:
- `datasets/question_sets/*`: preguntas, fechas de freeze, mercado, criterios de resolución, identificadores.
- `datasets/resolution_sets/*`: resultados y fechas por pregunta.
- `leaderboards/csv/*`: rankings agregados con N por dataset/market y Brier.
- `datasets/forecast_sets/2024-07-21/*`: al menos un archivo de pronósticos individuales humanos; **no se ha descargado ni inspeccionado su contenido**; requiere revisión legal/privacidad adicional.

Las tablas de leaderboard agregadas no contienen asignación aleatoria de leaderboard ni trazas de exposición. Los conjuntos de preguntas describen disponibilidad pública, **no exposición real a cada pronosticador**. Los recuentos `N` indican respuestas contabilizadas, no oportunidades de elección.

## Estimando propuesto y falsación

- Unidad objetivo: pronosticador `i` × pregunta `q` × ronda `t`.
- Outcome técnico: Brier `(p_iqt-y_q)^2` únicamente para predicciones observadas y legalmente utilizables.
- `E_iqt`: oportunidad efectivamente mostrada/elegible **antes** de responder, con fuente de timestamp independiente. No inferir `E` desde ausencia de respuesta.
- Baseline fuerte B0: difficulty-adjusted Brier ForecastBench según documentación y código oficiales.
- B1 candidato: ajuste por exposición elegible, manteniendo ajuste de dificultad y dependencia por pregunta/ronda; contrastar en holdout temporal fijado ex ante, comparando error predictivo y robustez al patrón de participación.
- Controles negativos: permutar exposición dentro de bloques temporales/preguntas, falsos denominadores por respuestas, evaluación con ausencia codificada como cero (debe rechazarse), fuga temporal de resolución (debe fallar).
- Auditoría adversarial: confusión por autoselección, competencia, incentivos y missing-not-at-random; errores por preguntas correlacionadas; cambios de scoring rule; derechos de datos personales.

**Puerta R5 de identificabilidad:** sin `E_iqt` observada legalmente y temporalmente anterior a `p_iqt`, B1 NO identifica una corrección por exposición, y cualquier contraste agregado es a lo sumo sensibilidad descriptiva. No adjudicar novedad ni aumentar CT2 por ello. Tampoco estimar efecto causal de leaderboard sin asignación aleatoria o diseño causal defendible.

## Requisitos para abrir ciclo A–J con plazas restantes

1. Inspeccionar documentación y licencia de cada archivo concreto y consentimiento/privacidad cuando haya pronósticos humanos.
2. Obtener bytes y SHA-256 del dataset realmente usado; congelar versión, columnas, fechas, sujetos y missingness.
3. Identificar una variable independiente de exposición/eligibilidad pre-predicción; si no existe, STOP_R5 o pivot explícito hacia una pregunta distinta.
4. Prerregistrar estimando, unidad, split temporal, comparadores B0/B1, controles negativos, inferencia robusta por pregunta y sensibilidad MNAR antes de calcular.
5. Ejecutar A–J real con logs, resultados negativos y actualización de priors/CT2 si corresponde. No consumir cupo por escribir este documento.
6. No reclutar, no puntuar políticos reales, no tratar datos personales sin revisión ética y base legal, no publicar identificadores individuales.

## Dictamen actual

**No supera la puerta de identificación.** La existencia de un leaderboard y de preguntas fechadas permite comprobar la plausibilidad de un análisis futuro, pero no demuestra que el denominador de oportunidades individuales sea observable. El camino más corto es revisar documentación de exposición del proveedor o encontrar un torneo con registros de asignación aleatoria/visibilidad, sin acceder a pronósticos humanos personales sin autorización.

T028 continúa en la cola Codex, sin ejecutar. Campaña anterior: 2 válidos, 1 incompleto, 2 plazas AB-H autorizadas sin ejecutar. CT2 prospectiva permanece 22/100 y N1/N2/N3 0/0/0.
