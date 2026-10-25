# Diseño preliminar de un TFM con contribución falsable

## Título provisional (opción A)

**Predicción y evaluación de la actividad parlamentaria española mediante datos longitudinales y redes institucionales: diseño reproducible de un observatorio computacional.**

La aplicación fantasy aparece como demostrador, no como hipótesis principal.

### Pregunta y estimando

Se define una variable objetivo operacional transparente, por ejemplo el número semanal futuro de intervenciones parlamentarias **registradas nominalmente y verificables** de un subconjunto de diputados cuya exposición y cargo se conocen al corte. No es un índice de productividad ni calidad de la representación política.

Estimando predictivo: diferencia de pérdida esperada fuera de muestra cronológica entre un modelo que incorpora red institucional, calendarios, rol y trayectoria individual, y el mejor baseline temporal/jerárquico competente disponible con la misma información al corte.

\[
\Delta = \mathbb E\big[L(\hat{Y}^{\mathrm{relacional}},Y)-L(\hat{Y}^{\mathrm{baseline}},Y)\big]
\]

Cuando `Δ < 0`, el modelo relacional mejora para esa métrica, muestra y periodo. Esto no demuestra que las relaciones causen la actividad.

### Hipótesis rivales

H1: estructura de agenda y redes agrega información predictiva sobre series individuales y cargo. H0: no mejora significativa frente a baseline fuerte. H2: mejora observada proviene de filtración temporal o variable del futuro. H3: ventaja depende sólo de más parámetros, no de la estructura relacional. H4: cambios de régimen político deshacen la ganancia.

### Contrato científico

Unidad persona-semana, emparejamiento de periodo/fuente y código congelado antes de test. Evaluación walk-forward con varios cortes temporales, selección sólo en desarrollo, último tramo temporal retenido y adjudicación auditada de datos. Identidad/institución y exposición se reconstruyen desde datos publicables. Incluye intervalos de incertidumbre, sensibilidades y baseline de conteo móvil.

## Opción B, sociología de la cuantificación

**Gamificación y sesgo de visibilidad institucional en los indicadores de actividad política.** Estimando: diferencia de puntuación por rol/grupo tras corregir exposición, bajo varias reglas transparentes; el análisis puede ser observacional y/o experimental con participantes reclutados, NO atribuir causalidad por usar simulación de jugadores. Incluye teoría de sistemas, Goodhart/Campbell como marcos críticos y análisis de incentivos.

## Opción C, simulación política

**Modelo generativo y contrafactual de coaliciones parlamentarias**; más ambicioso. Evitar si no existen parámetros identificables, series históricas suficientes o baseline de red fuerte. La hipótesis debe expresar qué aspecto de la dinámica reproduce fuera de la muestra y qué aporta sobre modelos estadísticos sin agentes.

## Decisión de alcance

[Inferencia] Elegir A para un TFM de ciencia de datos con opción de B como capítulo metodológico y el fantasy como demostrador. Posponer C hasta disponer de una base operacional consistente.

## Etapas con puertas de evidencia

- Inventario y legalidad → decidir exactamente qué recursos pueden recolectarse y conservarse.
- Ingesta/auditoría → cobertura temporal, identidades, deduplicación y latencia de publicación cuantificadas.
- Baselines → si no pueden superar una media por rol/agenda, reparar datos antes de redes complejas.
- Relacional → ablations de identidad, calendario, calidad temporal, redes; paridad informativa.
- Preregistro confirmatorio → conjunto futuro sin exposición de labels en desarrollo.
- Fantasy experimental → simulaciones de incentivos y balance basadas en historial, con puntuación reglamentaria distinta del estimando sociológico.

## Criterio de publicación

Informe con datos admisibles y procedencia, código, pruebas, esquema bitemporal, base fuerte, periodos no reutilizados, tamaños de efecto y límites. Un dashboard sin predicción auditada ni identificación de constructo **no cumple por sí mismo** los objetivos de ciencia de datos del TFM.