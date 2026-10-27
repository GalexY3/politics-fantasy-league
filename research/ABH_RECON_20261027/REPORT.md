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
