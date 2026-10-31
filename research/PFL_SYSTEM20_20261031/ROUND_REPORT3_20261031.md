# PFL SYSTEM20 · tercer incremento: recuperación verificable de PE/2025/XI

**31-10-2026.** Continuación de la segunda ronda y de la rama
`research/pfl-system20-process-corpus-gates-20261031`. Trabajo real de
descubrimiento, captura, normalización y observatorio documental. **No** es
un contraste confirmatorio AB-R, ni se han observado estados de terminación
como outcomes de investigación. Pregunta TFM sin cerrar.

## Laguna resuelta y fuente primaria

La API oficial CKAN del Parlamento de Canarias respondió HTTP 200 a
`package_search?q=Iniciativas PE 2025` y a `package_show` para
`iniciativas_tipope_anio2025_xilegislatura`. El recurso CSV figura con
identificador `df9e92ed-8f51-495f-b275-4fd26109cddc` en paquete
`864c06c6-0174-4e7c-aaf1-b30c7d16eb0f`, licencia de catálogo `odc-pddl`.
[Catálogo oficial](https://datos.parcan.es/dataset/iniciativas_tipope_anio2025_xilegislatura).
El enlace publicado es `https://www.parcan.es/api/iniciativas/2025/11/PE?format=csv`;
HEAD mostró un 301 a `/api/iniciativas/2025/11/PE/?format=csv`.
Se utilizó **una sola petición GET** al destino canónico previamente
comprobado, sin seguir redirecciones, usar cookies, credenciales ni aceptar
términos interactivos. HTTP **200**, **165.663 bytes**, SHA-256 original:

`13350568f6ef8f311b7bd8cb41791da1028550c98f3ef73bcc8bb4a78a7809ba`

Los originales y recibos quedan **fuera de Git** en
`../PFL-raw-primary/parcan_PE2025_20261031/`. El manifiesto con URLs,
licencia, huellas, rutas y límites es
[`data/source_manifests/parcan_pe2025_20261031.json`](../../data/source_manifests/parcan_pe2025_20261031.json).
El código de captura y cinco pruebas sintéticas se comprobaron y
congelaron **localmente antes del GET**, SHA del instrumento
`3ba15e1fd5beeddca90f1ec785779413691ab63618e16e8675348e454b382219`
y de su archivo de congelación
`8ffab701bf241fbb591e9a37673497b57cb2ce544a7fe766c6c19c12d11a247a`.
No hubo prerregistro remoto A–J de hipótesis políticas: **esta congelación
no se presenta como un estudio científico preinscrito**.

## Cobertura observada, no denominador

La ejecución offline con parser de estructura previamente congelado observó
**543 filas con 543 claves fuente-local ID+legislatura distintas**, ninguna
sin ID, legislatura o fecha de creación, sin duplicados de claves, y 543
fechas con forma `YYYY-MM-DD`. El CSV tiene columnas de resultado, pero
no se analizaron ni agregaron sus contenidos; el parser decodificó todas
las celdas estructuralmente. Resultado de auditoría agregado:
`PE2025_METADATA_ONLY_RECEIPT.json` SHA-256
`0ce42317bd0802f7e7546483d26abcb63f1a9c128350fbe4f30ea007a2ce7ce3`.

El nuevo normalizador `scripts/build_parcan_pe2025_local.py` verificó el
original, el recibo y los instrumentos congelados; depositó **543 filas**
de metadatos de ID/fecha fuente-local en
`../PFL-local-processes-pe2025-20261031-r1/`, sin títulos, personas,
estados terminales ni texto de iniciativas en Git. JSONL SHA:
`88041ac88a6dcb6e8b5c20ca89ae07fcdb6f95548a209042b4d6dd06aaec2bcc`.
El JSONL anterior de 1.211 registros NO se sobreescribió.

Una comprobación local adicional verificó los SHA de **ambos** JSONL
y comparó `(legislatura, tipo, ID)` sin mostrar identificadores:
**1.754 filas, 1.754 claves distintas, 0 colisiones entre archivos
y 0 registros con outcomes o `first_public_at` indebidamente admitidos**.
Este cotejo posterior a la captura verifica consistencia interna de
los artefactos disponibles, no cobertura editorial de todas las
iniciativas ni independencia histórica de publicación.

| Fuente conservada | Filas | Semántica |
| --- | ---: | --- |
| 2023/X/PPL | 1 | Proposiciones, clase y legislatura diferentes |
| 2024/XI/PE | 686 | Preguntas escritas, distribución anual capturada |
| **2025/XI/PE** | **543** | **Nuevo estrato oficial capturado** |
| 2026/XI/PE | 524 | Preguntas escritas, corte sujeto a censura del año |
| **Total de las 4 distribuciones** | **1.754** | **No equivale a censo parlamentario completo** |

No se conoce un total editorial independiente que certifique que el CSV
incluye todas las preguntas del año, ni la colección de transiciones con
fechas históricas verificadas. `F_CREACION` no es `first_public_at`.
El estado **actual** del CSV de 2025 no puede usarse como predictor de
2025 o de eventos anteriores sin contaminación temporal.

## Observatorio bitemporal conservador

`src/politics_fantasy/parcan_cohort_status.py` conserva **dos cortes de
conocimiento local inmutables, con SHA de recibo independiente**:

- **31-10-2026 05:19:18 UTC**, primera auditoría: **1.211** filas de
  tres distribuciones. Un corte anterior devuelve recuento `null`,
  no cero registros parlamentarios.
- **31-10-2026 05:34:51 UTC**, nueva auditoría: **1.754** filas de
  cuatro distribuciones, incorporando el estrato PE/2025.

El GET local `/api/spanish-process-cohorts?as_of=` respeta ambos cortes.
Ninguno es el momento histórico de publicación de un expediente. No
incluye identificadores individuales ni permite valoración de políticos.
Ante manipulación de un recibo, el endpoint se pone en cuarentena.

## Verificación y saldos

La auditoría local y los tests de captura fueron **cinco tests sintéticos
PASS** antes del GET y nuevamente tras los cambios, sin red. La ampliación
de pruebas Python sobre fuentes, normalización, temporalidad, admisión,
enlaces documentales, recibos y API sumó **121 PASS**; el grupo Node de
observatorio/fuentes y seguridad de enlaces alcanzó **9 PASS**; y
`node --check src/politics_fantasy/web/app.js` pasó. El panel se corrigió
para que no describa estáticamente un vacío de 2025 después de incorporar
esa fuente; se comprueba tanto la vista antigua como la nueva.
Estas suites son **focalizadas**, no equivalen a la suite completa Linux.
No se inició CI costosa.

**Hallazgo de reproducibilidad Git/Windows:** el recibo de congelación
`PE2025_PRECAPTURE_FREEZE.json` nació con saltos CRLF en la plataforma
Windows. La normalización Git automática lo transformaba en LF, cambiando
su SHA histórico. Se añadió una excepción puntual `-text -eol -diff` en
`.gitattributes` y se renormalizó el índice. La comparación directa
de los bytes de trabajo con `git show :ruta` confirmó igualdad exacta
y SHA `8ffab701bf241fbb591e9a37673497b57cb2ce544a7fe766c6c19c12d11a247a`.
No se reescribió ni recalculó retroactivamente la congelación original.

**SYSTEM20 permanece 20 autorizados, 0 AB-R/AB-P válidos, 0 inválidos,
0 de planificación y 20 disponibles.** La obtención de originales y
el desarrollo del observatorio son ingeniería e inspección documental,
no evidencia de autorregulación, policy feedback, mecanismos causales
o desempeño de personas reales. No se eleva CT2 ni se adopta pregunta
definitiva del TFM.

## Gate próximo

Contrastar el recuento con **un denominador independiente de la Cámara**
para una familia/ventana definida, identificar versiones y fechas
procesales de entrada/terminación, y acreditar disponibilidad pública
histórica o limitar formalmente el estudio a un corte descriptivo.
Canarias no reemplaza el universo español ni el Congreso nacional.
No reintentar fuentes bloqueadas/condiciones pendientes sin nueva evidencia
o autorización.
