# Reconciliación de ramas AB-H — 27/10/2026

Esta revisión compara estados versionados; no constituye un ciclo AB ejecutado, una adjudicación científica ni una autorización adicional. Su objetivo es evitar duplicar presupuesto o perder evidencias al reanudar Politics Fantasy.

## Dos historiales independientes

Ambas ramas derivan de `main` en `f430a085fa1606c4fc7919a768b7b77976da5699`; ninguna es antecesora de la otra. Sus documentos se refieren a un nuevo bloque de 20 ciclos BRANCHING tras AB20 y AB20B, pero los archivos disponibles no demuestran si las dos ejecuciones proceden del mismo acto de autorización humana o de dos autorizaciones independientes.

| Rama y punta examinada | Documento y blob Git | Contabilidad declarada en esa rama |
|---|---|---|
| [`research/pfl-abh-atlas-c20-20261026` · `6887d505bc9d360eca379b95fd1d62fd93667ec2`](https://github.com/GalexY3/Metodologia-AB/tree/6887d505bc9d360eca379b95fd1d62fd93667ec2/proyectos/politics-fantasy-league/research/ABH20_ATLAS_20261026) | `REPORT.md`, blob `cd841a22d7b387d8778aef95f951aff504a73a0c` | C01–C09: 9 consumidos, 11 restantes; STOP_R5 en C06 y C09. |
| [`research/pfl-abh-branch20-20261026` · `17d7c7730225fce1f43f16c307076e9896dbf1b9`](https://github.com/GalexY3/Metodologia-AB/tree/17d7c7730225fce1f43f16c307076e9896dbf1b9/proyectos/politics-fantasy-league/research/ABH_BR20_20261026) | `CAMPAIGN.json`, blob `e9db8848f81ac32935162bf6a1148b006dfaf502` | C01–C04: 4 consumidos, 16 restantes; STOP_R5. Este es el cierre citado en el texto aportado por el usuario. |

Los números C01–C04 coinciden como etiquetas, pero designan trabajos distintos en las dos carpetas. Los registros de la rama de nueve ciclos incluyen observaciones, especificación, reparación y dos paradas; la de cuatro contiene contrastes documentales, una consulta registral inconclusa y pruebas técnicas acotadas. La existencia de archivos `PREREG`/`RESULT` y los saldos declarados no prueban por sí sola validación experimental independiente de cada ciclo.

Si ambos historiales hubieran consumido **una misma** autorización de 20, la reserva conservadora sería `20 - 9 - 4 = 7` como máximo, suponiendo que no existan otras ejecuciones correspondientes al mismo permiso. Esa resta contabiliza reservas declaradas y no demuestra que todas las pruebas sean independientes ni resuelve la identidad del permiso. Si fueran autorizaciones distintas, sus saldos declarados serían 11 y 16. Hasta reconstruir esa procedencia, planificar como máximo siete plazas y señalar el saldo efectivo como **no reconciliado**, sin presentar siete como cifra definitiva.

Los bloques previos AB20 y AB20B constan como 20/20 en los informes posteriores; AB20 presenta discrepancia con su ledger legado, que indica 12/20. La PR #15 de AB20B sigue fuera de `main` según el estado observado. Atlas O7 tiene su propio bloque y no se suma a Politics Fantasy. No convertir pruebas de ingeniería, recuentos de ciclos o paradas R5 en nuevos N1/N2/N3 ni en gates de lanzamiento acreditados. Los dos informes conservan CT2 identidad 29/100, VSDS 1/3, progreso contractual 36,35 % y seis gates pendientes para sus respectivos cortes; no son una medición nueva del estado actual.

## Evidencias y límites que deben conservarse

- Rama de nueve: C07–C09 reúnen fuentes oficiales sobre el nombre completo de una parlamentaria y una ficha XV candidata; el enlace longitudinal queda **sin adjudicar**. También registra una política de elegibilidad, una reparación local, un endpoint aún sin aceptación HTTP completa y la activación accidental de cuatro ejecuciones de Actions. La evidencia exacta y las tres complaints se conservan en su informe, resultados y delta.
- Rama de cuatro: se documentan dos casos seleccionados en los que el código parlamentario difiere entre legislaturas, sin tasa poblacional ni crosswalk universal; la consulta del Registro de Partidos no obtuvo ficha registral original. `typed_refs.py` se importó y probó localmente, sin integración HTTP acreditada. Sus tres complaints y el estado de `atlas_delta.py check` constan en el informe y delta originales.
- Conservar los resultados negativos, los preregistros y su orden. Verificar las fuentes y las pruebas antes de heredar sus conclusiones como hechos nuevos. No fusionar las dos ramas ni marcar un gate como superado solo por esta reconciliación.

## Enlace mínimo propuesto en Atlas

El checkout de continuación se basa en la rama de nueve ciclos y ya contiene `updates/0001-PFL-ABH20-20261026.json`, batch `0001-PFL-ABH20-20261026`, blob Git `fbafa54cbd4ee9f01c838bff9d6ad6dca753fd1a`. La otra rama conserva `updates/0001-abh-br20-20261026.json`, blob `98498287dcdecfc4627e85fbcf39fc7fb29912d0`; ambos deltas tienen `parent_batch` vacío y **no pueden reproducirse consecutivamente tal cual**.

Para un futuro lote incremental, conservar el primero y crear `0002-...json` con `parent_batch: "0001-PFL-ABH20-20261026"`. Añadir un nodo bloqueado `PFL-ABH-RECON-AUTH-20261027` bajo `root` con relación `related_to`, enlazando este documento y los informes/delta de ambas puntas mediante URLs fijadas por commit. Su detalle debe explicar el conflicto 9/11 frente a 4/16 y la reserva condicional de siete. Referenciar el delta externo como artefacto histórico **no equivale** a haberlo aplicado ni a importar sus cuatro runs y tres complaints al grafo estructurado. Si se requiere integración estructurada posterior, trasladarlos con IDs sin colisión y procedencia explícita mediante operaciones nuevas, sin reescribir el seed ni fingir un mismo linaje. Validar el replay con `atlas_delta.py check`; el HTML sigue siendo un snapshot hasta que se regenere deliberadamente.

## Actualización de la continuación del 27/10

Se ejecutaron **tres ciclos nuevos RC01–RC03**, identificados de forma distinta de ambos C01–C04. Por prudencia, bajo la hipótesis de un solo permiso de 20 y sin otras ejecuciones, el cálculo pasa a `20 - 9 - 4 - 3 = 4` plazas como máximo. No acredita que el permiso sea común ni que el saldo real sea exactamente cuatro. Las capturas realizadas antes de los preregistros RC01 y RC03 se reconocen como exposición previa; su repetición no es evidencia ciega ni réplica independiente.

El lote `0002-pfl-recon-20261027.json` añade operaciones nuevas que trasladan los cuatro runs, tres complaints y nodos de la rama de cuatro ciclos, con enlaces fijados a su commit original; conserva también los tres nuevos runs. Eso no convierte los dos `0001` en un mismo linaje ni mueve el código de esa otra rama a esta. Un primer replay rechazó la severidad `moderate`; se reparó a `minor`, se conservó la incidencia y el replay estricto posterior pasó.

Tras RC04, y al indicar el investigador que no recuerda si las autorizaciones son la misma, se mantiene el criterio conservador: `20 - 9 - 4 - 4 = 3` como máximo si existe un único bloque y no hay otras ejecuciones. El lote `0003-pfl-rc04-20261027.json` recoge este cambio y el contraste RC04; no reescribe el lote anterior.
