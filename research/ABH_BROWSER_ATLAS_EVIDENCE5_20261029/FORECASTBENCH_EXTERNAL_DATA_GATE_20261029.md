# PFL · nueva fuente independiente revisada: ForecastBench · 29/10/2026

**Tipo:** auditoría preparatoria de disponibilidad y antecedentes; NO nuevo ciclo AB-R/A–J, NO experimento, NO análisis de outcomes, NO alteración de presupuesto (quedan dos plazas AB-H sin ejecutar). Se comprobó información de un repositorio público con el conector GitHub y documentación primaria de ForecastBench.

## Fuente exacta y licencia

- Proyecto: [ForecastBench](https://www.forecastbench.org), Forecasting Research Institute.
- Repositorio de datos: [forecastingresearch/forecastbench-datasets](https://github.com/forecastingresearch/forecastbench-datasets), rama `main` observada en commit `e1defb1a70d10311670b12701c837f712c672c03`.
- Licencia del repositorio y los datos: **Creative Commons Attribution–ShareAlike 4.0 (CC BY-SA 4.0)**, ver [README](https://github.com/forecastingresearch/forecastbench-datasets/blob/main/README.md) y [LICENSE](https://github.com/forecastingresearch/forecastbench-datasets/blob/main/LICENSE). No se extiende esta licencia de forma automática a contenidos externos enlazados ni a datos de terceros no contenidos en el repositorio.
- Citación declarada: Karger, Bastani, Chen Yueh-Han, Jacobs, Halawi, Zhang y Tetlock, «ForecastBench: A Dynamic Benchmark of AI Forecasting Capabilities», ICLR 2025.
- Metodología original: [Documentación oficial](https://www.forecastbench.org/docs/), que especifica **difficulty-adjusted Brier score** y explica que ajusta las diferencias en la dificultad de los conjuntos de preguntas para hacer comparaciones más justas. No presentar ajustes por dificultad o exposición heterogénea como novedad sin contraste frente a este baseline.

## Archivos públicos efectivamente inspeccionados mediante GitHub (solo esquema/metadatos)

| Archivo | SHA de blob Git verificado por GitHub | Metadatos observados |
|---|---|---|
| `datasets/question_sets/2026-10-25-human.json` | `c76e424acafdda1575989313cc174ccede1855d8` | 200 preguntas; `id`, `source`, `freeze_datetime`, `market_info_open_datetime`, `market_info_close_datetime`, `resolution_dates`, `resolution_criteria` y otros campos |
| `datasets/question_sets/2024-07-21-human.json` | `ae7014c0e2bc0b2117b3b20efcb59c401e24976a` | 200 preguntas; conjunto histórico, mismo esquema general |
| `datasets/resolution_sets/2026-09-27_resolution_set.json` | `5fd032d0df1eea0dc47880bb3c640e6f75ab7fcd` | `forecast_due_date`, `question_set`, `resolutions`; cada resolución incluye `id`, `source`, `resolution_date`, `resolved_to`, `resolved` |
| `leaderboards/csv/leaderboard_baseline.csv` | `fa76366ba425a0597d0af3c847197cd4be2d2fe7` | CSV con ranking, nombres públicos de modelos/grupos, `N dataset`, `N market`, Brier y CI |
| `leaderboards/csv/leaderboard_tournament.csv` | `10f814bbd57e52209032c14d44508ac574feda08` | Ranking público, recuentos de preguntas y métricas comparables |
| `README.md` | `1edea28cb04516a41d3878860bfca905ee1fa094` | Declaración de licencia CC BY-SA |
| `LICENSE` | `4a771ccadef06d2509ca54ea80e8427a14e5c667` | Texto legal CC BY-SA 4.0 |

Los SHA anteriores son **SHA Git de blob obtenidos en GitHub**, no SHA-256 de copias locales. No se descargó un paquete completo en un contenedor ni se verificó checksum SHA-256 de bytes externos a GitHub. No se calculó ningún outcome, diferencia de rendimiento, tasa de participación ni estadístico inferencial.

## Alcance para PFL y límites adversariales

Aporta una fuente externa con preguntas distribuidas en rondas, fechas de congelación, resoluciones, recuentos de preguntas respondidas (`N dataset`/`N market`) y un **baseline competente ya publicado de Brier ajustado por dificultad**.

**No identifica el efecto causal de mostrar leaderboards**, porque los participantes/modelos no han sido aleatorizados entre condiciones T×L del piloto PFL. Tampoco acredita por sí sola el denominador contrafactual de «todas las oportunidades efectivamente disponibles para cada persona», ni ausencia de selección estratégica. El número de preguntas de un conjunto publicado no prueba que cada actor las viera o tuviera igual posibilidad de participar. No equiparar dificultad con exposición ni imputar los `missing` a fracasos.

El repositorio también contiene un directorio `datasets/forecast_sets/2024-07-21` con ficheros de pronósticos individuales humanos. **No se descargaron ni analizaron esos registros**, que pueden contener `user_id`, justificaciones y otros contenidos personales. Para cualquier uso de tales registros, exigir revisión adicional de minimización, consentimiento, licitud y derechos específicos, aunque el repositorio sea público.

La página oficial de ForecastBench permite inspeccionar datos y codebase. La licencia CC BY-SA permite reutilización conforme a atribución/share-alike, pero **no elimina obligaciones de privacidad** ni equivale a una autorización ética sobre un ensayo humano de PFL.

## Hipótesis futuras, SIN ejecutar

Una posible prueba metodológica con métricas agregadas y datos publicados, **antes de calcular**: contrastar un ajuste por oportunidades contra el **difficulty-adjusted Brier de ForecastBench**, manteniendo bloqueadas las preguntas, fechas, segmentos y outcomes, y separando la selección de preguntas de la dificultad. Requiere fijar estimando/holdout y comprobar que la pregunta es verdaderamente nueva respecto a la documentación/paper de ICLR 2025. El dato público por sí solo no aporta un experimento causal sobre el efecto del leaderboard.

**Dictamen R5:** fuente verificable y potencialmente legal para instrumentación metodológica no personal; **no** abrir C05 ni consumir los dos ciclos AB restantes hasta contar con un diseño discriminante, variables suficientes, derechos claros para los datos concretos y prerregistro congelado. Actualizar priors, no grado N1/N2/N3 ni CT2 sin evaluación integral.
