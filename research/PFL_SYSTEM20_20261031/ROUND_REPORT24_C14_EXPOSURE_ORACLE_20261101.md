# R24 · C14A: falso equivalente observacional por agregación de canales y ventanas

**1 de noviembre de 2026.** Subtarea **NONCYCLE** del núcleo científico-computacional PFL, iniciada sobre PR #7, HEAD base 8df788007553c05890be08b962ffc24349ee1a6a. Checkout independiente, sin modificar PFL-trabajo, método AB, originales, desenlaces, PII o términos de uso. **R5 STOP**, cero AB empíricos y cero cambios de Atlas, logros, puertas o TFM.

## Pregunta, alternativas y falsadores

**A: C14A, comparabilidad de exposición y canal (elegida).** El comparador del laboratorio R19/C14 cotejaba el número total de publicaciones por periodo, la fecha de reforma, el corte de conocimiento y la zona legal, pero NO guardaba los intervalos efectivos, el desglose PAPEL/ELECTRÓNICO ni los testigos de captura. Rival: los tests R19 ya verifican ventanas iguales dentro de cada informe, pero no necesariamente *entre informes*. Falsador: dos informes individualmente válidos y con totales iguales pero ventanas distintas, canales redistribuidos o fotografías diferentes pasan como equivalentes.

**B: R18-C18, integridad de originales (aparcada).** Ya hay controles de bytes SHA y vintages; no repetir sin bypass diferencial alcanzable y evidencia nueva.

**C: R18-C20, reproducción institucional y mecanismos rivales (aparcada).** Requiere fijar estimando, universo all-received y observaciones compatibles con R5. La sensibilidad de cobertura no identifica causalidad de feedback, calendario o acoplamientos; C20 conserva su propia cola.

Formalmente, la proyección Y = P + E NO es inyectiva: (P=8,E=2) y (P=5,E=5) dan Y=10 pero no son el mismo vector visible por canal. Además, diez documentos publicados durante un día no representan la misma exposición que diez documentos publicados durante treinta días. Perder esas dimensiones invalida la afirmación de equivalencia del observable completo.

## Congelación y falsadores PREPATCH

Código base: src/politics_fantasy/synthetic_regime_capture_sensitivity.py, SHA256 **ae2a41b3735ad0ccbb1c44f6d9e3e2b9d19b2c332cb5b526bf55a2465146eeb6**.

Primera batería sintética: tests/test_r24_regime_exposure_oracle.py, SHA256 **99bc8cdc45afa61216a0c371e4aab48e42cd926b7bddfe3ba107274fc9d1b24f**, congelada antes de ejecutar QA.

Primera ejecución con PYTHONPATH=src y pytest de ese archivo: **4 FAIL esperados / 1 PASS de control**:

- **F1, ventana temporal:** 30 días frente a un día, idéntico cut de reforma y 10→20 observaciones; el código no rechazaba la comparación.
- **F2, canales:** informe A, antes 8/2 y después 8/12; informe B, antes 5/5 y después 15/5 en PAPER/ELECTRONIC. Misma suma 10→20, pero vector observado distinto; v1 decía que era la misma proyección.
- **F3, captura:** mismas sumas, pero fotografías locales del 30 de noviembre y el 1 de diciembre, sin recibo común; v1 atribuía equivalencia.
- **F4, esquema:** no existía desglose por canal en el reporte, imposibilitando comprobar la aritmética anidada y detectar su falsificación.
- **Control:** con ventanas, capturas, fixtures y vectores idénticos, variar solamente supuestos *hipotéticos* de fracción de cobertura sí puede mostrar una tendencia no identificada bajo esas premisas.

Todos los episodios y fechas son **sintéticos**, sin lectura de fuentes españolas, outcomes ni datos personales.

## Reparación y contrato v2

Cada periodo conserva exposure_window (first_day y last_day), visible_by_channel, capture_at_by_channel y synthetic_fixture_ids_by_channel, además de los totales y límites hipotéticos. Es un cambio declarado de esquema a pfl.synthetic_regime_capture_sensitivity.v2 y pfl.synthetic_regime_observational_equivalence.v2. El comparador distingue la falsa identidad debida solo a sumas (same_aggregated_totals_only) de una proyección por canales realmente igual.

El validador de informes exige tipos y claves cerradas, suma coherente por canal, fechas canónicas y ventanas iguales por exposición, contigüidad legal y días equiparables, corte de conocimiento suficiente, captura posterior al cierre del día local, cuatro IDs de fixtures sintéticos distintos y ausencia de campos contaminantes. Rechaza la comparación entre ventanas o identidades de captura incompatibles **antes** de diagnosticar equivalencia.

Una búsqueda estática de consumidores en el árbol identificó solo el módulo propio y sus tests R19; no se localizó endpoint HTTP del esquema anterior. La consulta estática no acredita ausencia de consumidores externos.

La última prueba focal tras la corrección, más cuatro falsadores adversariales adicionales, arrojó **30/30 tests Python PASS** (R19+R24), más compilación PASS. La regresión ampliada de ocho suites científicas y temporales pasó **104/104 Python PASS**, además de compileall del paquete. El Atlas99 permanece con digest bc4c7b094df4cb95f073a3d41f18c5c362bea80ca6b3ce275ed07593571c46e9, y el registro de logros v7 con 5/91 desbloqueados; ninguno fue adjudicado por esta QA.

Huella del código posterior: SHA256 **055d954e045d71646d54a45fd4cf52eaec8f3ffc6ea62799b03edcb876f65712**. Huella de la batería R24 final, ya ampliada: SHA256 **3cf55e88ab2904023cc772207a9c537f97d95d652a6974ce26b8638d0d7facd5**. Los hashes PREPATCH anteriores se conservaron sin sustituirlos.

## Alcance científico

El instrumento corrige una inferencia espuria **dentro de una simulación**. No demuestra que canales reales sean exhaustivos, excluyentes o de la misma población; los ID sintéticos no son certificaciones oficiales, los recibos de captura declarados no autentican fuentes reales y los límites de cobertura son premisas formales, no estimaciones españolas.

**R5 sigue STOP** por derechos individualizados, entrada all-received/admitted-first, casos negativos/pendientes/censurados, N independiente, correspondencias asiento→decisión, dos originales históricos y first_public_at autenticado. Ningún contrato de este informe avala causalidad española, validez externa, avance de grados científicos o un ciclo AB empírico. Se conservan las restantes subtareas sin inflar ejecuciones.
