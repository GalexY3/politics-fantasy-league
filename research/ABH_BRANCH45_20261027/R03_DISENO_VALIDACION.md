# Evaluación AB-R de Politics Fantasy — revisión R03, 27/10/2026

## Separación de resultados realmente observados
- **Descriptivos oficiales:** en dos BOCG se documentaron bajas, altas y credenciales con fechas efectivas; en 2026 un Diario de Sesiones y la ficha de diputado corroboran la condición plena de una persona. Uniones de documentos de un mismo editor no son independencia causal ni prueba de disponibilidad exacta en el momento del evento.
- **Controles positivos de identidad:** once coincidencias históricas de nombres se conectan con biografías oficiales que relacionan mandatos; en la muestra seleccionada **no existe un homónimo exacto negativo adjudicado**.
- **Error de enlace falsado:** en la fuente BOCG XV-D-390, unir listas por ordinal genera **2/3 correspondencias falsas**. Esto es un contraejemplo de método, **no** una tasa poblacional.
- **Conflicto atributivo:** fecha de nacimiento discordante para la misma diputada histórica entre editores oficiales. **La fecha correcta no está adjudicada**.
- **Ingeniería AB-P:** controles puros y archivos de prueba, algunas suites locales verificadas y otras solo autoradas, sin E2E de recepción de fuentes certificadas por el servidor.

## Por qué CT2/VSDS/N1–N3 no suben

[VSDS_PROYECTO.md](../../docs/VSDS_PROYECTO.md) exige para **2/3** un estimando sustantivo, corpus de campo certificado con denominadores, comparador competente, casos negativos y evaluación temporal. Tenemos pruebas documentales de un pequeño número de casos seleccionados, pero **no** un corpus evaluable ni un comparador validado. La columna predictiva CT2 y las pruebas científicas N1–N3 tampoco pueden heredar confianza por número de commits o ciclos AB.

[PLAN_TFM.md](../../docs/PLAN_TFM.md) define el estimando (\\Delta = E[L(\\hat Y_{rel},Y)-L(\\hat Y_{base},Y)]), una tarea persona-semana futura de intervenciones verificables, ajustada por rol, exposición y agenda. **No se ha construido una cohorte original de entrenamiento** con marcas de disponibilidad histórica por fuente ni intervalos de pertenencia suficientes, y el test cronológico fue reutilizado exploratoriamente en otras campañas. Por ello no hay afirmación de mejora predictiva.

## Siguiente diseño AB-R falsable sin filtración

1. **Unidad y observación:** persona-documentada × semana, distinguiendo cargo y oportunidad institucional de conteos de intervenciones; fuera de cobertura hay missingness, no cero.
2. **Corte temporal estricto:** no utilizar en `as_of=t` ningún documento cuya disponibilidad públicamente acreditada sea posterior a (t); fuente del BOE 2023 cuenta solo bajo la cota condicional documentada, no trasladarla a BOCG. Guardar `event_day`, `issue_day`, `first_public_at` y `ingested_at` como columnas distintas.
3. **Personas/organizaciones:** adjudicación manual doble de muestra adversarial; al menos un **homónimo exacto NEGATIVO**, un cambio de adscripción y un mismo individuo con DOB discordante, más puentes entre legislaturas. No usar `codParlamentario`, `asiento` o nombre como identidad universal.
4. **Baselines a vencer:** (a) recuento semanal móvil individual, (b) media jerárquica rol×semana×cámara y (c) calendario/agenda conocido en el corte. Todas las variantes con **las mismas fuentes y latencias**. Test de ablation sin red, sin historial, sin fechas de disponibilidad.
5. **Prerregistro y validación:** fijar cohortes y splits cronológicos, últimos cortes ocultos hasta congelar código/modelos, baseline e hiperparámetros. Comparar por pérdida de conteos (por ejemplo desviancia de Poisson y MAE), intervalos bootstrap por bloques de semana/persona, grupos/roles y robustez a cambios de legislatura.
6. **Daños y semántica:** diferencia de visibilidad por rol, grupo, género u otra categoría **solo cuando sea lícito, justificado y voluntariamente evaluada**, y representación cuidadosa; los conteos no miden mérito político, influencia causal ni calidad democrática.

**Falsadores antes de probar:** una media rol×agenda igual o superior; mejora debida a datos futuros; sensibilidad extrema a partidos grandes; datos incompletos que atribuyen ausencias ficticias; falta de robustez en la legislatura siguiente. **R5:** sin cohorte etiquetada y auditable no lanzar 20 iteraciones sobre fixtures repetidos.

## Recomendación para el producto

Hasta contar con las observaciones anteriores, el producto debe mostrar fuentes y estados **documentales en cuarentena** y permitir demo íntegramente sintética; no adjudicar puntos individuales reales. El avance contractual V4 (36,90%) es un juicio de especificación, no una calificación de precisión predictiva.
