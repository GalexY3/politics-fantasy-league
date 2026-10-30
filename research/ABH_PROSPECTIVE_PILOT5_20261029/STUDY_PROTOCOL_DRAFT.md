# PFL · Protocolo prospectivo de transferencia — BORRADOR NO APROBADO
**29/10/2026 · 2×2 factorial, solo actos y personajes inventados · NO PARTICIPANTES RECLUTADOS.**

## 1. Objetivo, población y riesgos
Investigar si una explicación de **qué constituye una oportunidad verificable** y la presencia de una **clasificación ficticia de juego** interactúan para cambiar la comprensión de qué significan las puntuaciones derivadas de acontecimientos institucionales. Hipótesis adaptativas formuladas a partir de C01-C05 de INCENTIVE_MECHANISMS5; no es un hallazgo, ni un estudio humano ejecutado. En esta fase solo existe software de ensayo *dry-run*.

Población prospectiva: personas adultas (18+) que voluntariamente consientan un estudio de percepción de reglas de juego con instituciones ficticias; no se recogerán preferencia de voto, religión, ideología, afiliación, historias personales ni opiniones sobre políticos. Cualquier cuestionario y alojamiento real requieren revisión previa del comité de ética/organismo responsable, información y consentimiento inequívoco y evaluación RGPD aplicable. No hay servidor o servicio de captación construido.

## 2. Diseño 2×2 y comparadores
Unidad de aleatorización: una persona participante (no sesiones repetidas sin identidad auditable). Factores:
- **T** información transparente sobre denominadores/cobertura (1) frente a tutorial neutro igual duración, volumen y formato (0).
- **L** marcador/leaderboard de avatares **inventados** (1) frente a pantalla de seguimiento sin orden clasificatorio, tamaño/tiempo análogo (0).

Cuatro celdas: control T0L0, transparencia T1L0, leaderboard T0L1 y ambas T1L1. Mismos datos ficticios de agenda, 4 casos de transferencia no utilizados en el tutorial y mismas opciones de respuesta. Sin perfiles políticos, campañas, votos de personas reales, recomendaciones electorales, apuestas o recompensas monetarias. La aleatorización de bloques de cuatro está instrumentada para **reproducción local únicamente**: `pilot_assignment.mjs` genera asignaciones predecibles por semilla, **no garantiza ocultación ni seguridad en captación real**.

**Control competente y paridad:** controlar longitud y dificultad de tutorial, tiempo de atención y carga gráfica; el leaderboard debe representar avatares sintéticos y no convertir respuestas personales en ranking; evaluar tanto la transparencia sola como el efecto combinado; no comparar un tratamiento rico contra un control trivial.

## 3. Outcome y falsadores (FUTUROS, NO OBSERVADOS)
Primario: puntuación 0–4 en **cuatro casos de transferencia nuevos**. X1 cobertura desconocida no permite inferir ausencia; X2 cobertura completa y cero observaciones permite afirmar cero observado sin inferir mérito; X3 cinco actos de votación sobre dos expedientes no equivalen a cinco expedientes; X4 tres éxitos entre veinte oportunidades anunciadas equivalen a 0,15 sobre esa base, no 3/4. La clave reside en módulo investigador `fictional_transfer_key.mjs` y **nunca debe exponerse al navegador público**.

Estimandos descriptivos preregistrables: media T1 menos media T0, promedio de niveles de L; media L1 menos L0, promedio de T; interacción `(T1L1 − T1L0) − (T0L1 − T0L0)`. Para sujetos reales, los contrastes serán causales de asignación aleatoria solo si hay cumplimiento, calidad de aleatorización, suficiente tamaño, datos válidos y gestión preestablecida de pérdidas. También medir la tasa de selección de cuatro tareas fáciles frente a las veinte programadas como outcome secundario, con estímulos y recompensas predefinidos aún NO implementados.

Rivales: T mejora transferencia; L induce heurísticas rápidas sin mejorar comprensión; solo atención explica diferencias; H0 nula. Falsadores: efectos no diferenciales tras control de tiempo; ausencia de diferencia; techo de test; confusión de instrucciones; attrition por tratamiento; sesgo por no aleatorización real. No introducir variables políticas sensibles de participantes como covariables.

## 4. Contrato de recogida y ética (GATE)
**NO ACTIVAR ENCUESTAS NI INVITAR PARTICIPANTES AÚN.** `pilot_dryrun_intake.mjs` solo procesa objetos marcados `SYNTHETIC_DRY_RUN_ONLY` sin almacenamiento ni red; su bandera de aprobación es **un mock trivialmente falsificable**, no dictamen de comité ni base RGPD. Se prohíbe usar ese guard para reclutar de verdad. Los datos ficticios de pruebas no son observaciones.

Antes de captación, registrar: responsable del tratamiento; aprobación/dispensa de ética aplicable, hoja informativa con objetivos, duración, riesgos, retirada, uso/retención/publicación; base jurídica validada; consentimiento específico e independiente, consentimiento y respuestas almacenados de forma separada y minimizada, derechos/borrado; medidas de seguridad, amenazas y control de acceso; protocolo para menores (excluidos); gestión de incidencias; accesibilidad; traducción pilotada en castellano. No se debe solicitar IP/email ni publicar raw logs sin revisión. Consentimiento retirado después de anonimización irreversible puede no poder vincularse: explicarlo por adelantado y definir procedimiento.

## 5. Análisis, missingness y preregistro definitivo
El programa `pilot_analysis_dryrun.mjs` solo acepta `FICTIONAL_TEST_ONLY`, calcula medias de cuatro celdas y contrastes factoriales de **casos completos**. Si faltan respuestas devuelve `COMPLETE_CASE_NOT_ITT`; nunca imputa ceros ni inventa intención de tratar. El test con fixtures **NO** estima potencia, incertidumbre o efectos sobre personas.

**Antes de estudiar personas:** bloquear reclutamiento, n objetivo y justificación de potencia/sensibilidad a pérdidas; criterios de inclusión y exclusión; asignación segura y ocultación, condiciones/timing definitivos; traducción y validación cognitiva del test; análisis ITT prespecificado y supuestos explícitos para datos ausentes (por ejemplo límites de Manski/sensibilidades bajo MNAR); errores estándar/IC según diseño; corrección por multiplicidad de secundarios; estrategia de duplicados y semilla inaccesible a operadores. Preregistro público fechado o embargo formal antes de observar outcomes. Si no es posible, registrar estudio como **exploratorio**.

## 6. Puertas de evidencia
- Instrumento técnico local (C02-C05): comprobaciones V8; **no QA nativa completa**.
- Prototipo accesible y fiable: NO probado.
- Aprobación ética y RGPD: NO concedida.
- Pilotaje cognitivo: NO realizado.
- Consentimientos reales y captación: **0**.
- Resultados y falsación en participantes: **0**.
- Replicación externa, VSDS-2, 2/3, gates lanzamiento: NO acreditados.

### Antecedentes
[Contests gamification persistent engagement (2026)](https://doi.org/10.1007/s11129-026-09311-3); [team leaderboard, performance and confidence (2024)](https://doi.org/10.1016/j.lindif.2024.102565); [RCT gamification cognition (2025)](https://link.springer.com/article/10.1007/s40692-025-00366-x); [civic gamified pilot (2025)](https://www.ipr.northwestern.edu/our-work/working-papers/2025/wp-25-27.html); [preregistration APS](https://www.psychologicalscience.org/publications/psychological_science/preregistration); [informed consent UAB](https://www.uab.cat/en/research-ethics/informed-consent). Estudios de otras poblaciones y medidas; no demuestran nuestro mecanismo específico.
