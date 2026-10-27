# Politics Fantasy — continuación AB-H, 27/10/2026

## Contabilidad y decisión

El cierre aportado hablaba de 4/20 y 16 pendientes. Se localizó además una rama paralela con nueve ciclos distintos para un bloque descrito también como la nueva autorización de 20. Ambas parten de `f430a08` y no son ancestrales. Se desconoce si hubo un permiso común o dos. Se documenta su procedencia en [reconciliación](RECONCILIACION.md).

En esta continuación se ejecutaron **4 ciclos RC01–RC04**. Si los 9 y los 4 anteriores consumieron una misma autorización y no hay otras ejecuciones, son 17 registros contabilizados y quedarían **como máximo 3**. Es una reserva prudente, no un saldo definitivamente conciliado. El investigador indicó que no recuerda si ambos bloques tenían el mismo permiso. Los cierres incluyen comprobaciones de ingeniería, observaciones y STOP_R5, no 17 experimentos científicos confirmados. Se detiene esta tanda con R5 en identidad longitudinal: los nuevos archivos todavía no resuelven equivalencias entre personas o primera publicación por fila. No se solicita otro bloque.

| Ciclo | Resultado | Alcance |
|---|---|---|
| [RC01](RC01_RESULT.json) | XLSX oficial de Interior recuperado por HTTPS; 5.600 filas, 16 elecciones entre 1977 y 2023; SHA reproducido. | Electos electorales; nombre no equivale a ID o mandato. Exploración previa al protocolo. |
| [RC02](RC02_RESULT.json) | Endpoint local de elegibilidad: 13 tests pasan; rechazo de Host externo. Replay inicial Atlas: 1 lote, 18 nodos. | Aceptación técnica local y parcial; no E2E integral o preparación para lanzar. |
| [RC03](RC03_RESULT.json) | XML oficiales del Senado recuperados; composición con 2.521 registros y sesión con 10 votaciones; hashes reproducidos. | Par `(legislatura, ultCredencial)` único en este snapshot, no ID longitudinal certificado. Exploración previa al protocolo. |
| [RC04](RC04_RESULT.json) | 259 cadenas nominales distintas de la sesión: cada una encuentra un candidato nominal en la composición XV capturada. | Cotejo exploratorio, sin validación independiente de identidad, falsos enlaces o pertenencia en la fecha de la sesión. |

El cotejo RC04 supera un [control técnico ficticio](RC04_QA.json) posterior que distingue coincidencias únicas, ambiguas y ausentes. No es una adjudicación de personas reales ni un ciclo adicional.

Se ha añadido el [catálogo central de fuentes](../../docs/CATALOGO_FUENTES.md), incluyendo inventarios antiguos, originales del Congreso documentados en otras ramas, Interior, Senado, BOE y fuentes secundarias. Para cada fuente describe uso, grano, acceso, fechas, permisos conocidos, evidencias y bloqueos. Los originales de Interior y Senado están en `data/raw/` del checkout local y no se han publicado en GitHub; las URL, hashes y perfiles agregados sí se conservan.

## Atlas e incidencias

El lote [0002](../../ab_atlas/updates/0002-pfl-recon-20261027.json) añade las operaciones necesarias, incluidos los cuatro runs y tres complaints de la rama paralela con enlaces a su commit, tres runs nuevos y la pregunta abierta de autorización; [0003](../../ab_atlas/updates/0003-pfl-rc04-20261027.json) registra RC04 y la respuesta del investigador. No modifican el seed ni reescriben los deltas anteriores. El replay completo pasó con **3 lotes y 25 nodos**, SHA-256 de estado `a599a4985803117f335f94a4f4d9ba50c7576dd7bf32f2f71f651b91fb42f75e`. El HTML continúa siendo la fotografía anterior.

Incidencias conservadas: exposición de las fuentes antes de los preregistros RC01 y RC03; dos linajes con permisos potencialmente solapados; y una primera validación del delta rechazada por usar `moderate` como severidad, reparada a `minor`. En una comprobación adicional posterior al protocolo, la suite de Atlas produjo 33 aprobados y un fallo de decodificación en Windows: la prueba abría HTML UTF-8 con la codificación predeterminada. Se corrigió la lectura/fixture y la suite pasó **34/34**. El éxito del replay no autentica las fuentes ni garantiza que todas las ramas estén incorporadas.

CT2 de identidad histórica se conserva en **29/100**, ordinal; [trayectoria con escala completa y vista ampliada](CT2_IDENTIDAD.png). VSDS **1/3**, hallazgos nuevos N1/N2/N3 **0/0/0**. El 36,35 % es el último índice contractual heredado, no una nueva medición. Ninguno de los seis gates se acredita como superado. El examen descriptivo y las pruebas de software no validan una teoría ni habilitan puntuación de personas reales.

## Siguiente contraste útil

Diseñar una muestra pequeña con fuentes originales recuperables y un control de homónimos y de códigos cambiantes; adjudicar manualmente coincidencias y no coincidencias mediante evidencia institucional independiente y fechas de disponibilidad. Antes de cargarla en el producto, auditar licencias y retención. Para fijar el saldo exacto hace falta comprobar si las dos ramas nacieron de un mismo permiso o de autorizaciones independientes; hasta entonces se aplica el techo prudente.

## RC05 — muestra documental adjudicada, controles de error y STOP_R5 (27/10/2026)

[Prerregistro antes del cotejo focalizado](RC05_PREREG.json) · [cinco pares con fuentes, clases y cronología](RC05_ADJUDICATION.json) · [resultado AB-H](RC05_RESULT.json).

**Alcance y sesgo de selección.** La selección de personas, enlaces y parte de los hechos se conocía antes del prerregistro; por tanto esta ronda es **exploratoria y post-expuesta**, no confirmatoria ni ciega. Se fijaron cinco pares sin ampliar la muestra tras mirar los resultados: 3 `SAME_PERSON` y 2 `DIFFERENT_PERSON`. Estas etiquetas están adjudicadas de forma contextual para los cinco registros contrastados; no son muestra representativa ni medición de sensibilidad/especificidad de RC04, y no hay segundo revisor humano independiente.

**Tres positivos verificables para este caso delimitado:**
- P1: **Maroto Aranzábal, Javier Ignacio**, fichas XIII/XIV/XV enlazadas por el propio Senado (`id1=18865` en XIV y XV), y nueva designación de las Cortes de Castilla y León el **10-09-2026**. El Senado registra cese del mandato anterior **10-09-2026** y fecha de la nueva designación **11-09-2026**. La entidad persona persiste, **el mandato no es un intervalo indiferenciado**; conservar credenciales y fechas separadas. La página del Senado en una captura indexada antigua mostraba fecha `11/05/2022` y en otra actualización la renovación `11/09/2026`; **misma URL no implica snapshot inmutable**.
- P2: **Clara María Martín García**, acta y boletín de designación de Castilla y León, confirmados por ficha individual del Senado XV (`id1=20042`, credencial `500/000322`, inicio 11-09-2026).
- P3: **Francisco Javier Iglesias García**, mismo acto de otra autoridad y ficha del Senado XV (`id1=12884`, credencial `500/000324`, inicio 11-09-2026).

**Dos negativos verificables de no-unión:**
- N1: **Lucía Yeves Leal** (`id1=19847`, baja 31-07-2026) **no es** su sustituta **Carmen María Díaz Ruiz** (`id1=20041`, alta 01-08-2026). Coincidir escaño, circunscripción y grupo no significa identidad.
- N2: **Juan Pablo Martín Martín** (`id1=18101`, Ávila) **no es** **Paloma Martín Martín** (`id1=19954`, Madrid). Dos apellidos iguales, personas distintas y enumeradas simultáneamente en una misma comisión del Senado. **Este control no cubre homónimos de nombre completo**.

**Granularidad temporal y procedencia.** Las Cortes de Castilla y León celebraron el acto **10-09-2026** y publicaron el BOCCL **16-09-2026**; las fichas del Senado recogen inicio **11-09-2026** para los tres designados. `act_at`, `mandate_effective_at`, `bulletin_published_day`, `first_public_at` no son equivalentes. Este último permanece **`null` para cada uno de los cinco pares**; ni la fecha de la firma, ni el día de portada del boletín, ni la captura actual certifican cuándo era visible cada campo en un backtest. El catálogo se ha actualizado con autoridad, enlaces directos y esas limitaciones.

**Integridad:** siete comprobaciones estructurales de la matriz RC05 en memoria, sin prueba de exactitud sobre archivos fuente originales: no se descargaron aquí los XML de RC03 conservados únicamente en el checkout local del investigador. El replay incremental del Atlas desde el seed y cinco lotes con reglas de integridad replicadas en JavaScript quedó **PASS: 28 nodos, 44 enlaces, 19 runs, 13 complaints**. **No se ejecutó el comando Python `atlas_delta.py check`** del repositorio en este entorno ni CI Actions. Un éxito técnico limitado no autentica páginas dinámicas ni produce prueba de backtest.

**Contabilidad:** bajo la hipótesis conservadora de un único bloque de 20 y ausencia de otros consumos, `9 + 4 + 4 + RC05(1) = 18` registros; **quedan como máximo 2**, no un saldo definitivamente conciliado. Se cierra **RC05 por R5**: homónimos de nombre completo, disponibilidad as-of original y validación longitudinal de todo el corpus siguen fuera de alcance. No gastar esos dos ciclos solo en nuevas variantes de búsqueda de nombres. No modificar 36,35 %, CT2 identidad 29/100, VSDS 1/3, hallazgos N1/N2/N3 0/0/0 ni gates 0/6.

**Siguientes pasos condicionados:** obtener prueba de `first_public_at` por versión, un caso real de homonimia exacta adjudicado por fuente independiente, revisar las condiciones de reutilización del BOCCL y del Senado y, si se autoriza la CI, ejecutar replay oficial `atlas_delta.py check` y contraste contra XML originales RC03. No inferir que RC05 confiere seguridad de uso con personas reales en el producto.
