# Índice de madurez de Politics Fantasy League — PFL-V1-20261026

**Baseline fijado:** 26 de octubre de 2026. **Alcance y datos:** [product/progress_scope_v1.json](../product/progress_scope_v1.json), 9 sublíneas, 36 hitos; [snapshot inmutable V1](../product/progress_snapshot_v1_20261026.json).

## ¿Qué mide?

El **porcentaje de madurez del trabajo frente a un alcance versionado, no la probabilidad de éxito ni horas restantes**. Cada vía posee peso propio y cada hito evidencia un nivel. Una vía completa vale el peso íntegro y solo al cumplirse todos sus hitos. Las evidencias enlazan al repositorio, con lo que el juicio queda discutible y auditable.

| Nivel | Valor de madurez | Condición |
|---|---:|---|
| 0 | 0% | No iniciado, imposible de evaluar o bloqueado |
| 1 | 10% | Especificación diseñada |
| 2 | 40% | Implementación sin prueba completa |
| 3 | 60% | Comprobación local registrada |
| 4 | 85% | Contrastado contra una fuente/documentación de campo delimitada |
| 5 | 100% | Operativo y verificado para el ámbito definido |

**Estos coeficientes son una convención de seguimiento del proyecto, NO una estimación empírica del trabajo ya completado.** Se aplican de forma determinista después de adjudicar el nivel de cada hito. No subir a 4–5 por un test sintético, ni subir a 3 simplemente por existir código sin ensayo observado.

Formalmente, si la vía `t` tiene peso `w_t`, el hito `i` tamaño `q_i` y nivel `l_i`, siendo `f(l)` la escala anterior:

`P_t = 100 × Σ_i q_i f(l_i) / Σ_i q_i`

`P_global = Σ_t w_t × P_t / 100`

con `Σ_t w_t = 100`. Se preservan sus ponderaciones en un manifiesto versionado.

## Resultado V1

| Sublínea | Peso global | Índice vía | Aporta al global |
|---|---:|---:|---:|
| Fuentes y datos | 18% | 38,75% | 6,975 pp |
| Identidades y coaliciones | 12% | 40,00% | 4,800 pp |
| Acontecimientos públicos | 10% | 32,50% | 3,250 pp |
| Investigación y evaluación | 14% | 27,50% | 3,850 pp |
| Mecánicas y motor del juego | 16% | 45,00% | 7,200 pp |
| UI y experiencia de usuario | 10% | 27,50% | 2,750 pp |
| Seguridad, privacidad y licencias | 8% | 20,00% | 1,600 pp |
| Pruebas y reproducibilidad | 8% | 32,50% | 2,600 pp |
| Operaciones y lanzamiento | 4% | 17,50% | 0,700 pp |
| **Global** | **100%** | | **33,725% → 33,7%** |

**6 gates críticos impiden publicar un juego público con figuras reales** aunque el índice sea distinto de cero: registro auténtico RPP/candidaturas, identidades individuales, eventos individuales con atribución comprobable, autenticación multiusuario, pruebas nativas end-to-end y despliegue seguro. Estos gates son **un indicador de preparación aparte**, no un descuento encubierto sobre el porcentaje.

El prototipo SQLite local con fichas ficticias y contratos de puntuación existe y fue probado históricamente; actualmente los originales jurídicos/personales siguen ausentes. Por tanto, no confundir demo completada parcialmente con producto público para España.

## Revisión de alcance y cómo manejar retrocesos aparentes

Al añadir sublíneas, reponderar vías o añadir requisitos dentro de una vía, **guardar una nueva versión** sin modificar los resultados históricos ni falsear la fecha de evidencias. Los niveles solo se actualizan con nueva prueba o corrección de un dictamen previo. **Nunca renombrar un objetivo distinto usando el mismo ID**: una definición nueva exige hito/ID nuevo y registro del cambio.

El modelo separa el cambio por **trabajo** y el cambio por **alcance** con una descomposición secuencial declarada:

1. Calcular el porcentaje anterior con alcance antiguo.
2. Recalcular la madurez de los hitos originales usando la evidencia nueva, conservando denominador/pesos antiguos: esto es `work_effect_pp`.
3. Recalcular con denominador y pesos del alcance nuevo: `scope_effect_pp` es el residuo.
4. Así, `P_nuevo − P_anterior = efecto_trabajo + efecto_alcance`. La descomposición es de orden trabajo-primero (no única).

**Ejemplo puramente hipotético, NO adoptado como V2:** incorporar la obligación de cobertura municipal nacional exhaustiva, sin evidencia adicional, añade un quinto hito a la vía de fuentes. La madurez global baja de **33,725%** a **32,330%**. Cambio total **−1,395 puntos**, 0 puntos por trabajo y −1,395 por alcance. Conservar el baseline V1 real. [Escenario y diferencia](../product/progress_scope_change_example.json), [escenario no adoptado](../product/progress_scope_v2_EXAMPLE_NOT_ADOPTED.json).

## Herramientas entregadas

- [Motor JS](../src/politics_fantasy/progress_model.mjs): validar, calcular, versionar y comparar scopes. [20 tests Node](../tests/test_progress_model.mjs) probados en extracción V8; ejecución en Node limpio aún por verificar.
- [CLI offline](../scripts/progress_report.mjs) para recalcular un archivo o comparar dos versiones. Su ejecución como proceso Node nativo también requiere una corrida verificable.
- [Adaptador Python](../src/politics_fantasy/progress_api.py) + `GET /api/progress` en el [servidor local](../src/politics_fantasy/server.py) + pestaña «Progreso del proyecto» en la [interfaz](../src/politics_fantasy/web/app.js). Sintaxis JS de la interfaz verificada en V8; falta QA navegador, Python y HTTP.
- [Pruebas del adaptador Python](../tests/test_progress_api.py) y [HTTP loopback](../tests/test_progress_http.py) publicadas. Ejecución real CI pendiente.
- [Informe final de campaña y ledger AB](../research/BRANCH20K_20261026/REPORT.md), [scope de baseline](../product/progress_scope_v1.json).

## Gobernanza

- Métrica global y sublíneas no sustituyen **CT2** ni **VSDS**: CT2 es otro juicio ordinal por rama; VSDS evalúa valor sociológico/data science; descubrimientos AB son un tercer registro.
- El índice debe revisarse **al cierre de cada campaña AB, ante evidencia material nueva o cambio significativo de alcance**, con causas explícitas, no subir simplemente por consumir ciclos.
- Las metas vagas se convierten en hitos medibles antes de modificar un denominador. Si el alcance aumenta, no conservar artificialmente el porcentaje previo.
- No representa progreso por horas ni tiene un intervalo de confianza estadístico; la incertidumbre reside en la adjudicación manual del nivel de madurez y en el alcance del producto.
