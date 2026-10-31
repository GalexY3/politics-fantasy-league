# PFL · C20: discriminación instrumental entre rivales de mecanismo

**V0, 31/10/2026.** Diseño e instrumento sintéticos, NONCYCLE. **No es un ciclo AB, un experimento confirmado, un estudio de datos de España ni un modelo predictivo validado.** R5 continúa STOP y el objetivo del TFM permanece abierto. Se complementa con `POLICY_TRACE_CONTRACT_V0_20261031.md`, no se infiere un mecanismo causal de una cadena documental.

## Contrato preparatorio A–J

**A — Pregunta:** ¿qué observaciones permitirían que rivales de continuidad interna y acoplamiento ambiental produjeran pronósticos *numéricamente distintos*, en lugar de ser solo narraciones compatibles con los mismos documentos?

**B — Población:** casos binarios y covariables 100 % ficticios, identificados por `SYNTHETIC:` y un único grupo holdout. No se importan expedientes, indicadores reales, actores, votos ni resultados reservados. La distribución de los casos sintéticos no representa a la política española.

**C — Competidores:** cinco reglas *fijas*, declaradas antes de ejecutar los tests: B0 calendario; B1 calendario + condición institucional; B2 memoria interna; B2 entorno; B2 conjunto. Las probabilidades exactas son `p0=1/2+(calendario−1)/10`, `p1=p0+(institución−1)/10`, `p_interno=p1+memoria/10`, `p_entorno=p1+entorno/10` y `p_conjunto=p1+(memoria+entorno)/10`. Los valores están acotados de modo que todas las probabilidades caigan entre cero y uno. **Son rivales didácticos, no baselines empíricamente competentes**. El programa científico real requerirá modelos temporales ajustados y validación fuera de muestra.

**D — Predicción:** cada registro declara `prediction_at`, `target_event_on` y `outcome_captured_at`. Las cuatro covariables poseen una marca independiente de captura; ninguna puede superar `prediction_at`. Un resultado binario solo se evalúa después de cerrar el día jurídico del evento y de capturarse. No se autentica `first_public_at` real a partir de esos relojes.

**E — Medida y decisión:** pérdida de Brier media exacta con números racionales por candidato. Reportar separadamente (i) si existen pronósticos divergentes y (ii) si los Brier en el fixture difieren. Una diferencia de pronósticos no implica superioridad empírica, y una diferencia de pérdidas **no identifica** causalidad.

**F — Código y congelación:** `MODEL_RULE_SHA256` canoniza reglas/modelos, debe coincidir con la declaración del evaluador. Debe acompañarse de SHA de código y tests previo a la ejecución. El hash de configuración **no sustituye** al SHA del código ni constituye un prerregistro empírico remoto.

**G — Controles:** entorno observado después de predicción, memoria conocida retrospectivamente, publicación del resultado antes de terminar el día legal, timestamp naive, precisión submicrosegundo, duplicados, dos grupos mezclados, zona jurídica incongruente, IDs reales, atributos de derechos falsos, evaluaciones anteriores a captura y cambios del hash de la regla.

**H — Falsadores del instrumento:** cualquier observación posterior al corte que altere los pronósticos; colapso silencioso de B2 interno y B2 entorno cuando señales opuestas; afirmación causal ante Brier menor; evaluación de etiqueta no conocida a `evaluation_as_of`; posibilidad de etiquetar un caso real como ficticio.

**I — Resultados permitidos:** pérdidas exactas por nombre de modelo, tamaño del fixture y banderas de discriminación; **sin** identificadores de casos, política española, ranking individual, predicciones reales ni claims sobre efectos de sistemas económicos. No hay estimandos causales ni validez externa.

**J — Siguiente decisión:** si el instrumento pasa pruebas, registrar que C20 tiene *capacidad técnica sintética* para distinguir vectores de pronóstico, **no** que C20 científico ha concluido. Las condiciones R5, dos vintages, derechos, población y `first_public_at` siguen pendientes. La reserva adicional de diez ciclos AB permanece intacta hasta que esos requisitos estén acreditados.

## Relación con la teoría sociológica

En el programa sistémico, M1 (persistencia de operaciones y autorregulación), M2 (respuesta ante el entorno) y M3 (selección documental) pueden generar observaciones coincidentes. El instrumento separa M1/M2 en covariables distintas bajo igualdad de calendario/competencia; **no** resuelve M3 por sí solo. Para M3 es necesario un universo de registros anteriores a la selección editorial y observación homogénea de negativos, pendientes y censura. En una futura aplicación real, incorporar retrospectivamente un indicador económico publicado después de la predicción produciría leakage incluso si su fecha de referencia fuese anterior. Una reducción de pérdida fuera de muestra sería evidencia predictiva condicional; la inferencia de feedback político-económico requeriría supuestos y diseños específicos adicionales.
