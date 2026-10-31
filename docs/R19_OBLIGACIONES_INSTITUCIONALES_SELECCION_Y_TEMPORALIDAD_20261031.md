# R19 · Población de obligaciones, selección documental y conocimiento retrospectivo

**Programa:** Politics Fantasy League, investigación principal del sistema político español y sus acoplamientos institucionales. **Fecha documental:** 31/10/2026. **Condición:** `STOP_R5` en fuentes reales; esta nota contiene investigación documental limitada y pruebas exclusivamente sintéticas, no resultados causales. Método AB 3.2.1 y O1–O7 fijado al commit `69ed402dd4a3f25207d9e620ede568b5e92ad8af`; sin cambio metodológico unilateral.

## 1. Tres fronteras distintas: obligación, entrada y publicación

La auditoría documental delegada en R19 encontró una **familia distinta de las solicitudes/denuncias/expedientes de las rondas R5–R18**: la obligación anual de rendición de la Cuenta General de las entidades locales ante el Tribunal de Cuentas y órganos de control externo participantes. La evidencia fue obtenida **únicamente de fragmentos de indexación pública** de tres documentos institucionales, no de originales ni de un acceso directo al portal. Los resultados y límites del trabajador constan en `/cos-prueba/PFL-scratch-congreso2-20261031/ronda19` y en el [manifiesto saneado](../data/source_manifests/r19_local_accounts_obligation_documentary_redacted_20261031.json).

La población jurídicamente interesante no son las cuentas publicadas ni los expedientes recibidos. Es el conjunto hipotético de pares **entidad local obligada × ejercicio** que cumplen las normas de su clase, competencia y periodo. Al menos conceptualmente, permite formular la pregunta sobre **no presentación** sin excluir a priori las entidades que no generaron documento público. Ello no acredita que el observatorio indexado publique un censo exhaustivo históricamente correcto: el propio índice de sede describe un censo *continuamente actualizado*. Los nacimientos, disoluciones, fusiones y cambios de dependencia pueden alterar retroactivamente el denominador si se toma una fotografía editorial actual como población de riesgo de ejercicios anteriores.

La identidad `O(e,y)` designaría una obligación jurídica de una entidad `e` en el ejercicio `y`. Una posible remisión `R(e,y,k)` no es la obligación; una validación previa a remisión no es un rechazo administrativo de documento recibido; una cuenta publicada no equivale a todas las presentadas, y un estado editorial `NO ENVIADA` no constituye por sí solo una decisión terminal. La relación de trabajo es potencialmente `O(e,y) → múltiples intentos de remisión → múltiples validaciones y actuaciones`, con enlaces **1:N y N:M** pendientes de acreditar por identificadores oficiales. Sin un inventario anterior al registro de presentación, no debe importarse el estimando de duración de expedientes de otras fuentes. El posible estimando de cumplimiento de obligación requeriría su propio origen legal del tiempo, plazos, exenciones, censura e historial de presentaciones.

Las tres superficies documentales indexadas fueron:

- [Observatorio de rendición de cuentas](https://www.rendiciondecuentas.es/es/observatorioderendicion/index.html): el buscador muestra una relación descrita de entidades que no enviaron Cuenta General de alguno de los ejercicios 2022, 2023 y 2024, sin que eso pruebe el universo completo ni el estado original por cada corte.
- [Sede del Tribunal de Cuentas: entidades locales](https://sede.tcu.es/es/Tramites/fiscalizacion/rendicion-cuentas/.elements/InfoEELL.html): menciona un censo continuamente modificado, presentación privada con firma y validaciones previas; no certifica identificadores públicos de recepción a decisión.
- [Aviso legal del portal](https://www.rendiciondecuentas.es/es/avisolegal/): los fragmentos indexados describen aceptación mediante mera utilización, cookies/analítica y límites de reproducción. **No se accedió al dominio**, y la interpretación jurídica del alcance por activo sigue pendiente de revisión humana. Las URL son referencias, no una instrucción de visita ni una licencia.

**STOP local**: faltan derecho de consulta/reutilización verificable por distribución, censo histórico independiente de todas las obligadas bajo igual ámbito y ejercicio, enlace por ID entre obligación/recepción/validación/decisión, estados positivos/negativos/pendientes y censura en cada fecha, originales autenticados de dos ediciones del mismo activo y `first_public_at` independientemente probado. El aviso legal indexado impide tratar el mero acceso automatizado como autorizado; no aceptar condiciones ni navegar el portal hasta revisión humana. Una ruta documental sobre cuentas de partidos políticos queda `PARKED` como **otra** población y no se agrega a entidades locales.

## 2. Equivalencia observacional por régimen y canal

El laboratorio [synthetic_regime_capture_sensitivity.py](../src/politics_fantasy/synthetic_regime_capture_sensitivity.py) implementa una demostración *condicional*, enteramente ficticia. Separa dos periodos jurídicos contiguos, de idéntica duración, en dos canales `PAPER` y `ELECTRONIC`; la zona del calendario legal se declara explícitamente. Para cada celda se suministran un recuento observado `M` y un intervalo hipotético de fracción de captura `p` entre `L` y `U`. Si `0 < U` y las restricciones enteras son compatibles, la población de entradas ficticia `N` satisface:

\[
\left\lceil\frac{M}{U}\right\rceil\leq N\leq\left\lfloor\frac{M}{L}\right\rfloor.
\]

Con `L=0` no hay cota superior identificada. Con información sobre cobertura inexistente no debe sustituirse `L=1` por comodidad; la observación de `M` documentos no identifica automáticamente el número de entradas `N` ni su signo de variación. El laboratorio rechaza `float` para las proporciones, usa `Fraction`, detecta cotas incompatibles y mantiene `first_public_at`, censo independiente y desenlaces reales como `null` o falsos explícitos. Los periodos son estrictamente ficticios, aunque empleen etiquetas de fecha ISO comprensibles; no constituyen episodios del sistema político español.

El contraejemplo incluye exactamente la **misma proyección editorial** en tres mundos simulados:

| Mundo supuesto | Documentos publicados antes / después | Captura antes / después | Entradas subyacentes antes / después | Signo hipotético |
| --- | --- | --- | --- | --- |
| A | 10 / 20 | 1/2 y 1 | 20 / 20 | Igual |
| B | 10 / 20 | 1/2 y 1/2 | 20 / 40 | Creciente |
| C | 10 / 20 | 1/4 y 1 | 40 / 20 | Decreciente |

Por tanto, **una duplicación de lo publicado es compatible con tendencias subyacentes opuestas** si las reglas de captura/canal cambian y no están identificadas independientemente. Es una prueba lógica sobre modelos de medición supuestos, no una estimación de cobertura de ningún órgano español. La robustez añadida en R19 comprueba que un comparador no acepte fácilmente un informe de laboratorio modificado a posteriori con signo inconsistente, cotas imposibles o atributos de evidencia real indebidamente promovidos. Esta verificación aritmética tampoco autentica procedencia externa.

## 3. El tiempo histórico como doble condición, no simple fecha de suceso

En un grafo procesal, hay al menos dos ordenaciones irreductibles: la **ocurrencia jurídica del evento** y la **disponibilidad documental en el conocimiento del investigador**. A esto se añaden fechas del documento, edición del editor, captura local, y una primera disponibilidad pública histórica que no puede inferirse de las anteriores. La pregunta reproducible `¿qué se sabía en as_of respecto de eventos ocurridos hasta cut_on?` requiere seleccionar primero la última revisión **conocida** en `as_of` y solo después aplicar el filtro de fecha jurídica del evento.

El fallo prepatch `F01` de R19 aplicaba `event_on ≤ cut_on` a todas las versiones *antes* de resolver revisiones. Si una v1 situada en 2020 era corregida por una v2 conocida en 2026 que movía el evento a 2021, el inventario retrospectivo con `cut_on=2020-12-31` contaba indebidamente v1 pese a que v2 ya era la revisión efectiva al `as_of=2026-03`. La reparación conserva v1 para `as_of` anterior a captura de v2, permite la corrección conocida más tardía y mantiene por separado el número de versiones conocidas y vértices con eventos dentro del corte. Corregir lo que **sabemos** hoy de 2020 no equivale a atribuir ese conocimiento al observador de 2020.

El fallo `F02` era de precisión temporal: `datetime.fromisoformat` admite fracciones ISO de nueve cifras, pero `datetime` solo conserva microsegundos. Una captura de `00:00:00.000000001Z` y un corte en `00:00:00.000000000Z` quedaban convertidos al mismo instante, lo que hacía visible una afirmación documental un nanosegundo anterior a su conocimiento. La reparación de `utc` rechaza fracciones de más de seis cifras con error tipado, en lugar de truncarlas. Esta política fail-closed mantiene las marcas de seis cifras y los desplazamientos explícitos `+01:00`; **no reivindica soporte de precisión nanosegundo**. Los tests cubren ambos errores con fixtures congelados prepatch y controles contrafácticos de un segundo de separación.

Estos dos defectos son de **utilidades sintéticas y contratos reutilizables**: no se ha acreditado que una ingestión real ni un endpoint HTTP haya expuesto datos mediante ese camino. El riesgo es estructural para futuros instrumentos que reutilicen esas funciones; no se presenta como vulneración de una fuente real.

## 4. Mecanismos rivales y falsadores futuros

El núcleo teórico sigue siendo explicar persistencia y transformación del sistema político español, no clasificar actores individuales. La lectura luhmanniana de reproducción mediante decisiones y comunicaciones operativamente encadenadas compite con un modelo de flujos *input–output–feedback* de Easton y con una hipótesis de regulación y aprendizaje por corrección de desviaciones inspirada en Deutsch. Estas formulaciones **no son resultados**, sino mecanismos con pronósticos distintos que necesitarían un espacio de riesgo común. Como rival de medición `B0`, el mero cambio editorial/de canal puede imitar un cambio en rendimiento, latencia o capacidad política sin variación subyacente en entradas.

Un diseño contrastable deberá prerregistrar qué constituye *entrada*, *decisión*, *perturbación*, *retardo*, *respuesta* y *retroalimentación* y qué fronteras son funcionales, jurídicas o editoriales. Una variación legislativa que cambie el nombre de un procedimiento puede producir discontinuidad institucional real, cambio en captación o ambos. Un acoplamiento con derecho o economía no queda demostrado por la coexistencia de dos series temporales; requiere un comparador competente, precedencia de la exposición, intervención institucional trazable o restricciones de identificación defendibles, y control de selección/censura.

Los falsadores críticos son: (i) registro externo que demuestra que el universo editorial excluyó entradas o deberes; (ii) revisión conocida que desplaza una fecha jurídica y cambia retrospectivamente la elegibilidad; (iii) censo actualizado que incluye entidades no obligadas en el ejercicio antiguo; (iv) validaciones previas confundidas con recepciones fallidas; (v) versiones del mismo activo sin original autenticado; (vi) dos mecanismos rivales que generan la misma distribución observable bajo distintas coberturas; (vii) cláusula contractual que no autoriza el análisis de una distribución aunque su catálogo sea público.

**Decisión de cierre R19:** C14 queda `COMPLETED_NONCYCLE` con prueba sintética; R5 sigue `STOP_R5`, 0 AB válidos/inválidos/de planificación nuevos, 20 plazas SYSTEM20 sin gastar; C15–C20 permanecen candidatos independientes. Se mantiene separado el trabajo técnico verificable del contraste sustantivo aún imposible con los materiales admitidos.
