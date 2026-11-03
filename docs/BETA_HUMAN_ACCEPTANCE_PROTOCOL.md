# Protocolo instrumentado de aceptación humana: beta científica local

**Estado: instrumento operativo para sesiones voluntarias futuras.**
Ninguna persona ha participado en esta ejecución. Las pruebas Chrome CDP
y HTTP usan fixtures sintéticos: no equivalen a comprensión, satisfacción,
usabilidad humana ni evidencia empírica sobre instituciones españolas.

## Preparación y fronteras de privacidad

Preparar un único equipo aislado con Python, Node y Chrome. Abrir una base
SQLite desechable, distinta de cualquier cuenta del usuario. Arrancar:

    python -B run_demo.py --science-only --port 0 --db RUTA_SQLITE_DESECHABLE

Utilizar la URL de loopback mostrada en el terminal. El participante puede
parar cuando quiera. No abrir servidores públicos, túneles, cuentas,
documentos originales ni sistemas administrativos. Registrar por
separado (a) el efecto técnico visible y (b) la respuesta conceptual.
Un éxito Chrome no es una respuesta de participante.

No se recogen nombre, correo, IP, identidades, tiempos personales, voz,
pantalla, cookies, credenciales, URLs completas, texto libre ni historial.
Cualquier registro humano es local y voluntario; no se sube a Git.

## Recorrido y criterios observables

Los códigos son identificadores de tareas técnicas usados por Chrome CDP.
El participante realiza las mismas acciones sin ver primero las soluciones.
Las expectativas científicas de la tercera columna son para la persona que
evalúa, no instrucciones que deban mostrarse antes de obtener la respuesta.

| ID | Acción observable | Criterio operativo y de interpretación |
| --- | --- | --- |
| `LAB_B0_B3` | Abrir Laboratorio, Mecanismos, e indicar si los datos publicados identifican la causa de no publicación de E3 | B0 y B3 son observacionalmente equivalentes: no permiten decidir entre calendario y selección; E2 pendiente y E4 censurado no son rechazos |
| `LAB_S3_TEMPORAL` | Inspeccionar las cotas S3 en late y cambiar a early | Intervalo de cambio exacto `-11/52` a `47/119` sujeto a hipótesis de selección, no causal; early carece de esas cotas, sin anticipación |
| `LAB_S7_20` | Examinar testigos S7 y diferenciar contradicción de fallo del servidor | Veinte conjuntos, seis estados; NEITHER/CONFLICT/INADMISSIBLE son científicos, no HTTP 503 ni resultados administrativos reales |
| `LAB_S8_DESCRIPTORS` | Explorar distribuciones, revisiones, primeras publicaciones y derechos | Filtrado por primera publicación ficticia y captura anterior a as_of; SHA de fixture no certifica emisor, derechos ni cobertura |
| `S9_EIGHT_TABS` | Visitar las ocho pestañas S9 e identificar fuente-localidad, eventos, revisiones y preadmisión | No confundir persona, documento, episodio, decisión, revisión ni identidad de otro emisor |
| `S9_FAMILY_SCOPE` | Filtrar CHAIN en Preadmisión e Incorporaciones y regresar a Todas | Fuera del filtro de familia no equivale a cero global ni rechazo. Una SQLite genuinamente vacía en Todas puede informar cero incorporaciones sintéticas |
| `S9_TEMPORAL_COMPARE` | Cambiar valid_at, as_of y techo first_public; comparar early/late | Dos SHA independientes, sin mirar hacia el futuro. Diferencia en visibilidad ficticia no demuestra cambio real ni efecto causal |
| `S9_SINGLE_EXPORT_OFFLINE` | Descargar snapshot S9 y verificarlo con CLI offline | Archivo Chrome real y CLI verify_scientific_snapshot.py PASS sobre sus bytes; no autentica institución |
| `S9_PAIR_EXPORT_OFFLINE` | Descargar pareja early/late y verificarla offline | Exactamente dos snapshots, recibos SHA originales más pair_receipt sobre JSON UTF-8 canónico; compare_scientific_exports.py --pair PASS |
| `RESTART_DOCTOR_GUEST_LINK` | Guardar marcador de siete campos; reiniciar misma SQLite con puerto distinto y recuperar consulta | Puerto viejo deja de acreditar servicio; el doctor solo ofrece URL con puerto actual tras PASS y nuevas consultas GET/SHA |

Se preservan PP04 INCLUIDAS/NO INCLUIDAS, negativos explícitos,
pendencia y censura; ninguno es un denominador independiente ALL_RECEIVED.
El recorrido técnico también contrasta HTTP 400/503, SHA adversarial,
no POST ni cuentas en modo visitante y persistencia SQLite del fixture.

## Clasificar incidencias sin simular personas

**Técnica:** falla una transición o contrato verificable (panel, GET, SHA,
archivo, recuperación, reloj, enlace o derechos). **Interpretación:** el
programa funcionó y una respuesta humana voluntaria contradice el
significado de los estados. **Usabilidad:** el programa funciona, pero
no se encuentra/completa la acción sin ayuda. Si la lectura estaba
bloqueada por fallo técnico, la interpretación queda **NO EVALUADA**,
no marcada como error humano. Una tarea sin respuesta es NO OBSERVADA,
nunca acierto ni fallo ficticio.

## Instrumento ejecutable y registro local opcional

La CLI dispone de quince rutas independientes que no llaman al servidor
ni modifican SQLite:

    python -B scripts/beta_science_operator_protocol.py --self-check
    python -B scripts/beta_science_operator_protocol.py --participant-sheet
    python -B scripts/beta_science_operator_protocol.py --participant-handout RUTA_HTML_EXTERNA
    python -B scripts/beta_science_operator_protocol.py --template
    python -B scripts/beta_science_operator_protocol.py --template-to RUTA_RUBRICA_JSON_EXTERNA
    python -B scripts/beta_science_operator_protocol.py --blank-session
    python -B scripts/beta_science_operator_protocol.py --new-session RUTA_JSON_LOCAL_EXTERNA
    python -B scripts/beta_science_operator_protocol.py --evaluate RUTA_JSON_LOCAL
    python -B scripts/beta_science_operator_protocol.py --evaluate-to RUTA_JSON_LOCAL RUTA_RESULTADO_JSON_EXTERNA
    python -B scripts/beta_science_operator_protocol.py --prepare-form FICHA_V2_JSON HOJA_V2_HTML RÚBRICA_PRIVADA_V2_JSON
    python -B scripts/beta_science_operator_protocol.py --record-form FICHA_V2_ACTUAL_JSON FICHA_V2_SIGUIENTE_JSON OP01 TECH_COMPLETED A UX_CLEAR
    python -B scripts/beta_science_operator_protocol.py --evaluate-form FICHA_V2_JSON RÚBRICA_PRIVADA_V2_JSON RESULTADO_V2_JSON
    python -B scripts/beta_science_operator_protocol.py --new-private-dir DIRECTORIO_SUPERVISOR_EXTERNO
    python -B scripts/beta_science_operator_protocol.py --audit-private-dir DIRECTORIO_SUPERVISOR_EXTERNO
    python -B scripts/beta_science_operator_protocol.py --verify-chain-to RECIBO_JSON PRIVADA_RÚBRICA_JSON RESULTADO_JSON FICHA_RAÍZ_V2_JSON REVISIÓN_1_JSON REVISIÓN_2_JSON

**Modalidad preferente para una primera sesión nueva: v2 versionada.**
`--prepare-form` genera con un solo mandato tres artefactos vinculados:
hoja bilingüe HTML de las mismas doce tareas, fichero JSON de
observaciones y rúbrica cerrada exclusiva del supervisor. Usa una
fuente de aleatoriedad criptográfica del sistema operativo para elegir
la asignación A/B de **cada nueva ficha**, imponiendo seis opciones
correctas en A y seis en B. Es asignación aleatoria real por sesión
local, no la asignación determinista pública del formulario v1.
Las posiciones pueden coincidir entre dos sesiones por azar; el
protocolo no promete secuencias únicas ni el cegamiento de una
persona que haya visto la rúbrica. Esta asignación no significa que
personas hayan sido asignadas experimentalmente ni valida la
equivalencia de los doce ítems o de la traducción española.

La rúbrica JSON y la ficha JSON deben estar en un directorio de
supervisión **común y auditado**, distinto del directorio del HTML
participante; el
comando rechaza compartir directorio de rúbrica o ficha con HTML, rutas
repetidas, rutas dentro de cualquier Git o ADS NTFS. Deben existir
previamente los directorios de destino. El directorio del supervisor
debe comprobarse primero con `--audit-private-dir`, o crearse
siempre vacío y fuera de Git con `--new-private-dir`. En Windows,
la auditoría es nativa sobre SID, propietario y DACL (herencia
desactivada; solo titular, OWNER RIGHTS, SYSTEM y administradores).
La clave y las fichas se leen únicamente si el inode no tiene alias
de hardlink o symlink y no tiene ACE de lectura adicional. Tras la
inspección previa de la ruta, una apertura única verifica `fstat`
e identidad del inode y, en Windows, `GetSecurityInfo` sobre el
HANDLE del fichero **realmente leído**. Esto cierra la carrera
demostrada entre auditoría DACL por nombre y reapertura posterior
del origen; una sustitución detectada rechaza el registro y la
evaluación sin crear archivos sucesores. En POSIX se añade
`O_NOFOLLOW` cuando está disponible, sin certificar ACL extendidas.
Se rechazan asimismo los *Alternate Data Streams* NTFS de entrada
(`archivo.json:stream`): comparten inode y DACL con el archivo base,
pero pueden almacenar bytes distintos; se falsó una aceptación anterior
tanto al registrar una ficha como al evaluar contra una rúbrica ADS.
Un token sin privilegio de crear symlinks no pudo ejecutar el caso
positivo de alias simbólico en este equipo (WinError 1314); ello no
constituye una prueba de ese ataque. Tampoco se ha ejecutado una
prueba adversarial con cambio concurrente de directorios ancestros.
En escritura, una carrera NTFS **distinta** permitía que el temporal
heredase una ACE `Everyone READ` introducida entre la comprobación
de la carpeta supervisora y la apertura real del archivo nuevo.
Dos falsadores RED PREPATCH publicaron así una revisión codificada
y una evaluación sintéticas con DACL amplia. La publicación privada
v2 ahora audita el HANDLE nuevo antes de escribir bytes, revalida
la DACL y carpeta antes del hardlink, y comprueba el inode publicado
mientras conserva su alias temporal. El HTML participante continúa
siendo público por diseño. No se acredita con ello aislamiento
entre cuentas Windows diferentes, protección frente a cambios
posteriores de administradores ni un ensayo en Linux.
Otro defecto RED PREPATCH independiente del control ACL era la
sustitución del inode stage, o de sus bytes sin alterar el inode,
después de fsync y antes del hardlink. En ambos casos `--record-form`
o `--evaluate-form` devolvía un SHA de bytes distintos de los
realmente publicados. La operación ahora exige que inode stage,
inode final abierto y bytes íntegros coincidan con la escritura
original, y rechaza la discrepancia con
`OPERATOR_*_PUBLISHED_BYTES_MISMATCH`, sin atribuir autenticidad
externa a la huella ni proteger frente a mutaciones posteriores
realizadas por la misma identidad con acceso al fichero.
Dos intercalaciones NTFS de junction de la carpeta supervisora,
antes de crear el stage o del hardlink, se rechazaron sin publicación
pública ni escritura en Git sintético; son controles negativos,
no defectos adicionales ni pruebas de aislamiento entre usuarios.
Una carrera posterior al hardlink mostró otros dos defectos
independientes: la limpieza podía tomar la identidad de un archivo
ajeno que sustituyese el destino después del enlace, o eliminar
un archivo ajeno que ocupase el nombre stage durante el `unlink`.
Dos falsadores RED PREPATCH con archivos NTFS reales reprodujeron
ambas pérdidas. La limpieza Windows ahora abre cada nombre con
permiso DELETE y `FILE_FLAG_OPEN_REPARSE_POINT`, coteja el HANDLE
contra el inode creado y solicita el borrado por
`SetFileInformationByHandle`, sin un `unlink` posterior basado
solo en el nombre. Si aparece un alias ajeno falla sin destruirlo.
POSIX conserva una protección por `lstat` antes de borrar, no una
garantía atómica frente a carreras concurrentes. El fallo inyectado
de metadatos tras un hardlink real pasó su prueba de reversión;
no equivale a ensayar pérdida de energía real.
El supervisor
no debe compartir la misma cuenta del sistema con la participante.
En POSIX se comprueba el modo `0700` y propietario, no ACL extendidas.
No se ha ejecutado una comprobación positiva con dos tokens humanos
independientes. Los tres archivos se crean
exclusivamente, sin sobreescribir; si se detecta un error recuperable
durante la creación se intenta revertir solo los ficheros nuevos.
Una preparación con dos directorios privados diferentes se rechaza
ahora con `OPERATOR_FORM_PRIVATE_PARENTS_MISMATCH`, antes de escribir:
de otro modo `--prepare-form` aceptaba archivos que el contrato de
`--evaluate-form` no podía puntuar por la discrepancia de carpetas.
Las fichas v2 antiguas creadas en esa disposición no se migran:
la supervisora puede trasladar una copia byte-a-byte de la rúbrica
original a la carpeta privada auditada de la ficha y conservar su
identificador y hashes, sin generar una hoja distinta ni alterar
las observaciones previas.
No se promete atomicidad de los tres archivos como transacción ante
corte brusco de alimentación. Cada archivo individual se escribe a
un temporal exclusivo, se sincronizan sus bytes y se publica con
un enlace de creación exclusiva sin sobrescritura. Un corte puede
dejar temporales huérfanos, por lo que la recuperación se verifica
contra el contenido y no por la sola existencia de un nombre.
Tener carpetas diferentes NO constituye por sí solo control de permisos:
la persona supervisora debe custodiar la rúbrica y la
ficha fuera de la vista y del acceso de quien participe (por ejemplo,
cuenta del sistema o soporte separado); el HTML no lleva la clave,
pero tener acceso al repositorio o a la carpeta privada permite
descubrirla. No atribuir cegamiento efectivo a una prueba automatizada.
Cada ficha recibe un identificador de formulario aleatorio
de 128 bits no derivado de persona; únicamente su referencia
corta aparece en el HTML para cotejo local, sin captura de
nombre, correo ni actividad de la participante.

La ficha de observaciones usa el esquema
`pfl.beta_science_operator_observations.v2`. Los campos superiores
`form_id`, `handout_sha256` y `rubric_sha256` se conservan sin
modificar durante pausas, reinicios del servidor o ediciones
manuales. Solo se rellenan los cuatro campos cerrados de cada una
de las doce observaciones; en v2 el campo `scientific` acepta
exclusivamente `A`, `B` o `NOT_OBSERVED`, NO los códigos
`SCI_OP...` internos de v1. La distinción de `TECH_COMPLETED`,
`TECH_FAILED`, `TECH_BLOCKED` y `NOT_OBSERVED` se mantiene:
ninguna comprensión se puntúa sin finalización técnica. Las
respuestas ausentes o tareas no observadas se consignan de forma
explícita y no se convierten en errores de interpretación.

`--record-form` permite **registrar una tarea por mandato** sin
editar el JSON a mano: exige ficha v2 existente, las doce tareas,
identificador y códigos cerrados y un nombre nuevo de archivo externo.
Comprueba la ausencia de campos adicionales, respuestas A/B con
`TECH_COMPLETED`, códigos incoherentes, identificadores repetidos,
y rechaza la repetición de una tarea ya anotada con
`OPERATOR_OBSERVATION_ALREADY_RECORDED`. La ficha de origen y
las revisiones anteriores permanecen sin sobrescribir; el archivo
sucesor conserva `form_id` y ambas huellas de hoja/rúbrica. Una
revisión nueva incorpora además `predecessor_sha256`, SHA del
archivo exacto que dio origen a esa revisión; las fichas v2
anteriores no se modifican retrospectivamente para simular un
historial de cambios que no guardaron. `--verify-chain-to`
comprueba un listado **ordenado** de raíz, revisiones y evaluación
contra la clave privada, sin fusionar sesiones distintas:
una tarea nueva por eslabón, cero modificaciones a tareas previas,
igualdad de hashes y resultado final recalculado. Un resultado
compatible sólo acredita continuidad entre los archivos ofrecidos,
no firmas ni autoría, derechos o consentimiento humanos. Una
corrección legítima se realiza desde una revisión previa intacta,
con destino nuevo, y se documenta como bifurcación, no como
reescritura silenciosa. Los acuses de cada paso exponen únicamente
`source_sha256` y `destination_sha256` de bytes leídos/escritos,
ID de tarea, referencia corta y estado seguro, nunca respuestas
ni rutas. No se crea fichero si la observación es vacía o el
destino está ocupado, dentro de Git o es NTFS ADS. Estos SHA
no autentican quién introdujo los códigos, ni convierten un
harness sintético en una sesión humana.

`--evaluate-form` comprueba **antes de crear ningún resultado**:
esquema/versiones, correspondencia exacta de formulario y rúbrica,
huellas de hoja y clave, mapeo A/B cerrado contra el instrumento,
doce IDs únicos, veto técnico y ausencia de campos personales.
Publica solo clasificaciones de comprensión (`SCI_CORRECT`,
`SCI_INCORRECT`, `NOT_OBSERVED`) y conteos cerrados, nunca
identidades ni transcripciones originales. El resultado v2 declara
`instrument_binding=MATCHED_V2_FORM_AND_RUBRIC`; una discrepancia
de formulario/versión se rechaza fail-closed, sin generar archivo.
El resultado incluye además `coded_input_sha256` y
`coded_input_bytes` del archivo **exactamente leído**, incluyendo
su formato y saltos de línea, de modo que un informe puede cotejarse
con la revisión codificada concreta que originó la clasificación,
sin depender de volver a serializar JSON (o de CRLF en Windows).
Las huellas SHA-256 son de integridad y correspondencia de bytes,
no firmas, garantías contra un operador adversarial ni evidencias
de que los ítems se aplicaron realmente a seres humanos.
La evaluación v2 comprueba además el SHA de definición del instrumento
que incluye la rúbrica actual: una futura modificación semántica de los
ítems necesita una migración o evaluador específico explícito, nunca
reinterpretación silenciosa de una ficha v2 anterior.

**Histórico v1 preservado:** los nueve comandos anteriores no
reinterpretan formularios ni mutan registros. Las fichas
`pfl.beta_science_operator_observations.v1` pueden evaluarse
explícitamente por `--evaluate` o `--evaluate-to`, con su
anterior mapeo SCI y clave A/B pública, pero sus resultados
identifican ahora `instrument_binding=LEGACY_UNBOUND`.
La mera inclusión del SHA de la rúbrica actual en un resultado
v1 no puede probar qué hoja recibió una persona anteriormente.
Una ficha v1 no es admitida en `--evaluate-form` ni una v2
se puntúa con `--evaluate`: la compatibilidad no mezcla esquemas.

Las tres rutas nuevas de escritura producen directamente archivos UTF-8
en el directorio externo ya existente, con apertura exclusiva sin sobrescribir
y con una única respuesta de estado por consola, que solo comunica código,
SHA-256 y longitud cuando procede. No emplear `>` de PowerShell 5.1
para conservar resultados; la redirección puede codificar UTF-16LE.
`--participant-handout` contiene las doce preguntas existentes en un
HTML estático, imprimible, bilingüe (inglés original más traducción española
de apoyo), sin formularios, conexiones, JavaScript ni claves.
La traducción no se ha validado con participantes y su equivalencia semántica
no debe darse por supuesta. La rúbrica `--template-to` lleva las
correspondencias A/B→SCI y soluciones: guardarla en un directorio de acceso
exclusivo del supervisor y **no** presentarla junto a la hoja participante.
`--new-session` guarda la ficha de códigos aparte; nunca guardarla junto
al HTML destinado a la persona participante.

`--evaluate-to` valida primero el archivo de origen completo (doce IDs,
esquema cerrado, veto técnico y códigos), sin crear destino alguno si hay
error. Si es válido, guarda exclusivamente el resultado clasificado en otro
JSON UTF-8 y no sustituye ni altera la ficha fuente. La salida incluye
`operator_instrument_sha256`, SHA-256 de los bytes de la misma plantilla
`--template` / `--template-to` (incluido salto de línea), como referencia
reproducible de la versión de rúbrica empleada. No es una firma, no
acredita respuestas humanas y no enlaza automáticamente a ninguna identidad.
El resultado exportado no es reutilizable como ficha de observaciones; tiene
un esquema diferente. La creación de fichas, rúbricas, HTML y resultados
comparte restricciones fail-closed sobre checkout, Git ajenos, directorios
enlazados, existentes y NTFS ADS. Ante interrupción se conserva la ficha
original fuera de Git: una ficha toda NOT_OBSERVED no obtiene resultado
y las ausencias se codifican explícitamente sin imputar comprensión.

En Windows, evitar redirigir la salida de --blank-session mediante
PowerShell 5.1: su redirección puede generar UTF-16LE, que el evaluador
rechaza correctamente porque el contrato exige UTF-8. Usar la nueva
operación explícita para crear la ficha fuera del checkout, una sola
vez y sin sobrescribir archivos existentes:

    python -B scripts/beta_science_operator_protocol.py --new-session RUTA_JSON_LOCAL_EXTERNA

La CLI produce el fichero UTF-8 con las doce tareas OP01--OP12, todas
marcadas NOT_OBSERVED, y emite a la consola solo el código de éxito,
nunca la ruta ni el contenido. No crea nada si la ruta ya existe
o está dentro del repositorio. En Windows tampoco admite un nombre
de destino NTFS con dos puntos, porque podría apuntar a un flujo
alternativo de datos (ADS) de un archivo preexistente, incluso mediante
un hardlink exterior hacia un inode de otro repositorio. La salida
ante esa ruta es únicamente OPERATOR_SESSION_PATH_INVALID, sin crear
el flujo ni imprimir la ruta. La persona puede abstenerse; el
operador modifica exclusivamente los cuatro campos cerrados en
una copia local opcional, sin subirla a Git.

Una ficha incompleta, incluida una lista de tareas vacía, es rechazada
con OPERATOR_SESSION_INCOMPLETE. Una ficha con doce tareas todas
NOT_OBSERVED se rechaza como OPERATOR_NO_OBSERVATIONS: no hay
evidencia para evaluar. Esta diferencia permite conservar abstenciones
explícitas en tareas concretas sin presentar como completada una sesión
vacía. Respuestas semánticas sobre tareas TECH_FAILED,
TECH_BLOCKED o NOT_OBSERVED también se rechazan.

La hoja `--participant-sheet` incluye preguntas y opciones, pero no revela
la solución, las explicaciones de evaluación ni los IDs de automatización.
El orden de las respuestas A/B permanece equilibrado (seis correctas A y
seis B), pero ya no sigue la alternancia predecible A-B-A-B por número de
tarea. La asignación es determinista y reproducible a partir de un orden
público derivado de los identificadores del instrumento: no equivale a
aleatorización por participante ni acredita ausencia de sesgos de respuesta.
La correspondencia de cada elección con el código científico sigue estando
solo en la rúbrica del operador, y debe permanecer oculta al participante.
La rúbrica `--template` es SOLO para el observador y contiene los
criterios, el código de respuesta correcta y los valores válidos de la
ficha. No mostrar la rúbrica al participante antes de registrar
respuestas. `--self-check` comprueba la estructura del instrumento,
no comprueba un servidor activo ni la comprensión humana.

La ficha voluntaria `--evaluate` se construye manualmente fuera de
Git, con esquema `pfl.beta_science_operator_observations.v1` y
un array `observations`, cada una con solo `task_id`, `technical`,
`scientific` y `usability`; deben elegirse los códigos cerrados
del operador. No se permite añadir nombre, contexto de persona, captura,
URL, comentario libre o timestamp. No reutilizar datos individuales
entre sesiones. Si la tarea tiene `TECH_BLOCKED` o `TECH_FAILED`,
la respuesta científica DEBE ser `NOT_OBSERVED`; introducir una
opción de comprensión en esas condiciones es un error de contrato que
la CLI rechaza. La salida contiene códigos de estado y conteos
por tarea/dimensión, pero no atribuye número de participantes.

Las pruebas del parser emplean solamente fixtures temporales inventados
para demostrar rechazo de campos prohibidos; no son personas,
respuestas reales, resultados de un estudio ni telemetria.

La CLI local `scripts/beta_science_operator_protocol.py` suministra
una plantilla con opciones y criterios cerrados y un evaluador para
registros voluntarios. No incluir datos personales, narraciones libres,
rutas locales, timestamps de navegación ni identificadores únicos.
Los archivos de trabajo humanos opcionales no se versionan ni publican.
Su ausencia es un estado válido.

**No existe tasa humana de éxito, comprensión ni satisfacción** mientras
no haya observaciones humanas efectivas. Una muestra futura requerirá
definir condiciones de participación y denominadores observados antes
de calcular cualquier proporción.

## Límites

R5 permanece STOP_R5, 0/6 puertas y 0 AB-R nuevos. Este instrumento
no acredita autenticidad editorial, derechos de difusión, vintages
institucionales, fuente de ALL_RECEIVED ni causalidad. La validación
humana sigue pendiente aunque el navegador técnico apruebe.
