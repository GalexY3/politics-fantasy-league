# Validación, límites, seguridad y ética

## Separaciones obligatorias

- `record`: hecho documentado con URL, sello temporal y hash.
- `interpretation`: taxonomía atribuida a evento con trazabilidad, calidad, auditor humano cuando proceda.
- `forecast`: distribución o intervalo sobre un resultado predefinido, estimado sólo con información disponible antes del corte.
- `points`: convención reglamentaria de juego, no juicios sobre persona/ideología.
- `counterfactual`: escenario bajo un modelo y sus supuestos, no hecho.

## Cuatro tipos de contaminación

**Temporal**: usar texto de una votación publicada después del snapshot. Control: dos relojes (`occurred_at`, `first_public_at`) y features congeladas.

**Intraexpediente**: una iniciativa sufre múltiples votaciones, cuya división train/test no puede fragmentar arbitrariamente la cadena si se evalúa generalización de expedientes. Control: agrupar por expediente y bloquear dependencias, además de validación futura.

**Identidad**: homónimos, cambios de grupo y cargos, duplicidades entre Congreso y Senado. Control: IDs institucionales por autoridad y relación temporal, resolución reversible con nivel de confianza y cola manual.

**Outcome proxy**: intervenciones o iniciativas como medida de representación eficaz. Control: declarar qué constructo realmente miden, confrontar validez de contenido, discriminante y sensibilidad al oficio, género, lengua, grupo y periodo; no inferir mérito normativo.

## Métrica científica ≠ métrica de juego

Un score por cantidad puede incentivar verborrea, polarización performativa o inventar relaciones entre acciones y éxitos. Simular y contrastar este riesgo antes de desplegar. Publicar fórmula, fuentes, correcciones, topes y adjudicación de revisiones; mecanismo de impugnación factual sin perfiles ideológicos.

No convertir automáticamente noticias desfavorables, investigaciones o acusaciones en puntuaciones negativas, ni valorar personas por acusaciones no resueltas o ideología. Para sanciones institucionales explícitas, separar acto probado, procedencia, fecha y derecho a corrección, y revisar necesidad y proporcionalidad.

## Riesgos de privacidad

La AEPD identifica las opiniones políticas como categoría especial de datos en el RGPD. No recopilar creencias, ideología inferida, intención de voto ni perfiles de usuarios fantasy. No confundir afiliación pública documentada de cargos electos para una función institucional legítima con permiso ilimitado para perfilar a personas. Conservar los mínimos datos personales, seguridad de cuentas, retención limitada y evaluación jurídica previa.

Referencia: https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0215-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-las-categorias-especiales-de-datos

## Riesgos jurídicos de la competición

Prototipo gratuito, sin apuestas, sin compras de ventajas con dinero real y sin premios de valor económico. La DGOJ describe tres elementos concurrentes en su ámbito estatal: contraprestación para participar, azar y premio patrimonial. Si cambia la monetización, los premios o la posibilidad de transferir valor, obtener criterio jurídico especializado antes del lanzamiento. Nada de esto presupone una autorización legal definitiva.

Referencia: https://www.ordenacionjuego.es/en/node/2722

## Protocolo de evaluación científica

El conjunto principal debe definirse antes de inspeccionar el futuro: unidad persona-semana (o grupo-semana), predictores disponibles `as_of`, outcome elegido y periodo, reglas de censoring y cambios de mandato.

Comparar baseline de historial móvil, calendario+rol, GLM Poisson/NB, boosting con iguales features, más relación temporal si aporta; separar evaluación de count/ranking/calibración. Métricas posibles: MAE y deviance, log-score y cobertura de intervalos, Brier en evento/binario, errores por cargo/grupo/periodo, coste y latencia. Usar **rolling origin**, no k-fold aleatorio.

La evidencia de simulación será `SUPPORTED_WITHIN_MODEL` como máximo hasta contar con contraste con datos externos. No usar ficticios como muestras humanas, ni evaluar una política mediante la misma función con la que se programó su ventaja.

## Governance AB

Contrato A–J; R1 estimando, R2 comparador competente, R3 selección real, R4 ablación del mecanismo, R5 detener si falta evidencia discriminante. O1 GitHub fuente versionada; O2 freeze antes de ejecución; O3 DRIFT con alternativas; O4 CT2 no probabilística/niveles 0–3; O5 distancia D0–D5; O6 informe/contabilidad.

Estado actual: ningún experimento ejecutado con datos políticos reales; sin independencia confirmatoria; CT2 tentativa sólo cualitativa. Si al reanudar las pruebas no existe dataset utilizable se registra `BARRERA_DE_ACCESO`, no se fabrican resultados.
