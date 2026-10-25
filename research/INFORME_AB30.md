# Dictamen de campaña — PF-AB30, 24 de octubre de 2026

## Marcadores

- **Autorizados:** 30 ciclos AB A–J.
- **Completados como evaluación documental/planning:** 30 fichas A–J.
- **Experimentos con datos políticos ejecutados:** 0.
- **Pruebas técnicas locales ejecutadas:** 11 tests unitarios Python; 1 simulación de reglas de mercado con agentes inventados; 1 auditoría streaming de 100.000 registros **SINTÉTICOS**.
- **Confirmaciones externas independientes:** 0.
- **N1 nuevos, N2, N3:** 0 / 0 / 0.
- **CT2 rama B3:** 24→24 (valor ordinal interno, confianza baja, no P(descubrimiento)).
- **Otras ramas:** B1 18; B2 18; B4 14; B5 18, todas sin variación. No se comparan las puntuaciones como efecto de un pivote.
- **Holdout:** ninguno abierto ni establecido; no existen series políticas normalizadas en esta entrega.
- **Prerregistro congelado antes de pruebas políticas:** no procede, porque no se han ejecutado pruebas políticas.
- **GitHub:** repo de destino `GalexY3/polictics_fantasy_league` localizado, vacío; **escritura BLOQUEADA** por HTTP 403 `Resource not accessible by integration` tanto en create_file como create_blob y create_issue. Este informe y código se entregan en ZIP local verificado, no en remoto.

## Hallazgos de evaluación documental, NO descubrimientos 1/3

El diseño fantasy de seleccionar parlamentarios no es original per se. Politiparty (EEUU) y Fantasy Parliament (RU) implementan aproximaciones con eventos parlamentarios/noticias. Pronóstika fue un juego español de previsión de acontecimientos políticos. La predicción de votaciones en parlamentos mediante ML también está publicada (Guadarrama Rios et al., 2025; Kreutner et al., 2026). Estas observaciones rebajan reclamaciones de novedad general, pero no prueban ni refutan una ventaja predictiva de una tarea española concreta.

Los catálogos primarios de Congreso (votos, intervenciones, iniciativas), Senado y BOE **existen**. No se ha verificado el tamaño real ni la coherencia de un dataset extraído. La primera pregunta experimental viable es auditar cobertura, cambio de esquema, identidad de cargos y los dos tiempos, no entrenar una GNN directamente.

El juego es un mecanismo de retroalimentación entre observadores y comunicaciones: su sistema de puntuación es observación de segundo orden y podría inducir estrategias si se implanta. **No tenemos evidencia de que ya induzca comportamientos**. Esto constituye hipótesis, no resultado de sistemas complejos.

La investigación debe tratar como dimensiones diferentes la actividad observable, la calidad de la representación (constructo no medido), la cuota de poder/agenda, la predicción de eventos y la cotización fantasy. Una suma numérica no resuelve esa ontología. Proponer índices compuestos sin validación invita a Goodhart y desigualdad de oportunidad institucional.

**Antecedentes adicionales de control:** Congreso Abierto y «Qué se vota» prueban que no es original tampoco la mera estructuración española de votaciones por parlamentario/partido; y el reglamento de Politiparty ya usa topes por volumen de actividad. No se reivindican estas ideas como descubrimientos. Se requiere aportar mejora de calidad/temporalidad y validación cuantificada frente a estos referentes.

## Grupos de los 30 ciclos y decisiones

**B1 C01–C06, datos:** iniciar Congreso nominal/intervenciones, construir raw immutable, enlazado de identidades y bitemporalidad; Senado y BOE después de una muestra mínima verificada. Prioridad: evitar sesgo de cobertura y fuga de datos futuros.

**B2 C07–C12, medición:** el número de discursos no es productividad democrática, la votación colectiva no prueba mérito individual y la ausencia no es abstención. Separar taxonomía observacional de scoring fantasy y comparar reglas de puntuación por rol.

**B3 C13–C18, predicción:** problema TFM preferido: anticipar recuentos de intervenciones o actos institucionales de persona-semana contra tasas simples, Poisson/NB y calendario+rol; añadir redes sólo si proporcionan información predictiva incremental en walk-forward.

**B4 C19–C24, sistemas:** co-voto como red descriptiva, secuencias de agenda, simulaciones multiagente de coalición con comparador Markov; mercado fantasy con sensibilidad a reglas de subasta y popularidad, no inferir sociología española desde juguetes sintéticos.

**B5 C25–C30, producto, ética y TFM:** evitar copiar roles futbolísticos, balancear exposición, descartar inferencia de opiniones de usuarios, mantener piloto sin apuesta/premio, seleccionar una tesis falsable y exigir replicación independiente.

## Instrumentación realmente ejecutada

Tests unitarios para clocks, disponibilidades, deduplicación, caps fantasy, forecast anti-leakage, splits cronológicos, reproducibilidad sintética de subastas, checksums raw y lectura de calidad y red de co-voto. `pytest` reportó **11 passed**. La simulación de mercado con seed 47 y 10 clubs, 100 activos, 12 rondas produjo Gini de precios **0.103676** y cuota top-20% **0.248340**. Se trata íntegramente de reglas y números simulados inventados. **No es distribución de valor político, ni resultado del mercado real.**

La prueba de ingeniería de auditoría JSONL con 100.000 registros sintéticos en este entorno procesó **100.000 filas / 31.189.000 bytes / 0,7417 s de auditoría**; no mide coste de tráfico oficial, ETL distribuido, acceso a red ni rendimiento de PostgreSQL y no es un benchmark replicado en otra máquina.

## Falsadores prioritarios de la tesis

1. Baseline histórico con cargo y calendario iguala/supera modelo de red fuera del desarrollo.
2. Atribución nominal no cubre suficientes periodos o su latencia pública no puede reconstruirse.
3. La supuesta ventaja predictiva desaparece al eliminar features publicadas después del corte.
4. Si un índice compuesto sólo premia exposición institucional, el ranking fantasy no puede presentarse como mérito individual.
5. Un ABM no aporta predicción o reproduce exclusivamente sus reglas impuestas.

## Dictamen por dimensiones

Disponibilidad documental: viable a nivel de catálogo. Licencias por recurso, coverage e ingesta: no auditadas. Validez de constructo: principal riesgo científico. Originalidad: descartada para el fantasy político genérico, abierta para hipótesis concretas. Predicción: no probada. Simulación: sólo prototipo de mercado sintético. Riesgos éticos/jurídicos: relevantes pero gestionables mediante diseño conservador y revisión. Viabilidad TFM: **condicional** a completar una prueba de datos real con horizonte cronológico suficiente y un estimando estrecho.

## Decisión AB-DECIDE

**STOP a más teoría documental sin instrumentos nuevos. REPAIR acceso GitHub e INGESTIÓN LICENCIADA, después CONTINUE experimental.** No entrenar modelos espectaculares ni declarar 2/3 hasta tener observaciones bitemporales, baselines y contrastes externos.

## Evidencias y rutas

- `research/AB30_C01_C30.md`: A–J completo por ciclo, con estado documental explícito.
- `research/AB30_CYCLES.json`: índice legible por máquina.
- `research/CAMPAIGN.json`: autorización, CT2 y estado de GitHub.
- `research/CT2_TRAJECTORY.csv`: trayectoria sin cambios empíricos de B3.
- `figures/CT2_full.png` y `figures/CT2_zoom.png`: gráfico 1–100 y ampliado, generados por `research/visualize_ct2.py`.
- `research/FINDINGS_1_3.json`: N1=0, N2=0, N3=0.
- `research/stress_result_SYNTHETIC.json`: prueba de software, no evidencia política.
- `docs/ANTECEDENTES_Y_NOVEDAD.md`: fuentes limitadoras de novedad.

## Saldo y siguiente permiso

Se han usado las **30 autorizaciones sólo para evaluaciones documentales**, no para ensayos de campo; no existe asignación previa de 20 experimentos. Sólo después de acceso legal al corpus puede formularse una campaña experimental nueva con prerregistro por commit. Propuesta: 20 ciclos focalizados en calidad/estimandos/baselines y un primer modelo relacional con disyuntiva STOP/REPAIR, antes de abrir pivotes más lejanos.
