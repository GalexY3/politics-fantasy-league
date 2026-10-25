# C01 — Prerregistro local previo a análisis (2026-10-24)

**Origen de autorización:** «Concedidos», a solicitud de 20 ciclos AB adicionales; 20 son un máximo, no una cuota de hallazgos. **Tipo:** `EXPERIMENTAL_AB`/auditoría descriptiva de micro-piloto documental, no ensayo causal ni predictor real. `PREREG_LOCAL_ONLY`: no fue posible congelar un commit GitHub antes de ejecutar por denegación HTTP 403.

## A · Pregunta, unidades y estimando
¿Una muestra de conveniencia de los **20 renglones con votos numéricos publicados** en la página oficial de votaciones del Congreso para la sesión plenaria 193 (23/07/2026) satisface invariantes aritméticas elementales y exhibe información suficiente para deducir asistencia individual? Unidad = votación listada, no político, iniciativa, diputado-semana ni jornada fantasy. Universo del piloto = los 20 renglones de votos numerados identificados por posición en la página tal como fue recuperada mediante lector web el 24/10/2026. Estimandos: fracción de renglones con suma Si+No+Abstenciones <= 350; distribución descriptiva de sumas; faltantes de datos nominales y publicación previa documentada. No inferir ausencias individuales.

## B · Hipótesis y alternativas
H0: la contabilidad total puede exceder 350 en al menos un renglón por error de transcripción, duplicación de filas o interpretación. H1: ninguno supera 350. H_otra: el número de votos expresados podría diferir de 350 por ausencias, vacantes, no voto u otras situaciones no identificables con la tabla. No se reivindica novedad científica ni un test independiente de veracidad electoral.

## C · Contraste discriminante
Comparar cada triple tal como consta en el HTML público con las identidades aritméticas; registrar fuente, número de línea del lector, identificador de posición y fecha. Calcular máximo, mínimo, mediana, distribución de `350-suma` solo como discrepancia aritmética; no llamar «ausencias». Control negativo: añadir artificialmente un total imposible en fixture **synthetic**, que el validador debe rechazar.

## D · Instrumentación
Datos extraídos a mano desde el HTML accesible en https://www.congreso.es/es/opendata/votaciones, líneas 30–315 recuperadas del lector web; no se dispone del HTML byte-exacto, su ETag ni fecha de última modificación. Clave de fila = `legislature-session-date-ordinal`; se mantiene un link textual al contexto y líneas. Es una transcripción trazable, NO snapshot oficial firmado ni ETL automático. Hash local del CSV y del presente prereg; la captura fuente no puede verificarse byte a byte aquí.

## E · Ejecución y paridad
Ejecutar validador reproducible y obtener `RESULT_C01.json`. Sin aprendizaje automático, sin entrenamiento y sin estimación fuera de muestra. Presupuesto: 20 renglones, datos agregados; no hay replicación independiente.

## F · Auditoría adversarial
Comprobar errores de transcripción, duplicados de posición, sumas imposibles, que los 20 renglones correspondan a una sola sesión, extrapolación, construcción arbitraria y diferencia entre conteo de votos y asistencia. Un renglón con menos de 350 no demuestra una ausencia.

## G · Confirmación independiente
Requiere cotejo de los 20 renglones con JSON/XML oficial descargado y firmas/fechas, por otro canal. **No disponible ahora**. Si hay desacuerdo, INVALID + errata, no borrado.

## H · Actualización
Actualizar prior «una página oficial aporta datos observables de votación, pero no identificadores ni dos relojes completos para pronóstico». Ninguna conclusión sobre predicción parlamentaria o calidad de representantes.

## I · Dictamen
Admisible como contraste mínimo de calidad aritmética de una tabla histórica de conveniencia; no como conjunto de entrenamiento, afirmación representativa o prueba de un mecanismo sociológico.

## J · Decisión
Si la fuente no es accesible en bytes o no hay fecha de primera disponibilidad, abrir `REPAIR` y mantener C02–C20 sin ejecutar. Parar antes de consumirse el bloque por más semillas sintéticas.

### Congelación local
Se conservará SHA-256 del prereg inmediatamente después de escribirlo y ANTES de ejecutar su analizador. No se presenta el SHA local como prueba de publicación temporal GitHub.