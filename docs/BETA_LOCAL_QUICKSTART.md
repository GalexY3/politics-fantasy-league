# PFL · recorrido de evaluación local de la beta científica

**Alcance:** prototipo en un único ordenador, con datos sintéticos y HTTP
exclusivamente en 127.0.0.1. No autoriza publicar un servicio, incorporar
originales españoles ni puntuar personas políticas reales. La centralidad
corresponde al Observatorio y al Laboratorio; Fantasy es subordinado.

## Una sesión supervisada local desde cero (Windows PowerShell 5.1)

Realizar en un ordenador bajo control de la persona supervisora, desde
la raíz de ESTE checkout y con Python/Node instalados. Este ejemplo crea
solo ficheros fuera del repositorio; no genera ni simula participantes. Elegir
una carpeta de sesión nueva en el perfil local, con espacio y acentos válidos:

    $base = Join-Path $env:LOCALAPPDATA 'PFL prueba científica supervisada'
    New-Item -ItemType Directory -Force (Join-Path $base 'participante'), (Join-Path $base 'sqlite') | Out-Null
    python -B scripts/beta_science_operator_protocol.py --new-private-dir (Join-Path $base 'supervisor')
    python -B scripts/beta_science_operator_protocol.py --audit-private-dir (Join-Path $base 'supervisor')
    python -B scripts/beta_science_operator_protocol.py --self-check
    python -B scripts/beta_science_operator_protocol.py --prepare-form (Join-Path $base 'supervisor\observaciones-v2.json') (Join-Path $base 'participante\hoja-v2.html') (Join-Path $base 'supervisor\rubrica-privada-v2.json')

Se requieren los estados `OPERATOR_PRIVATE_DIR_CREATED`,
`OPERATOR_PRIVATE_DIR_CHECKED`, `OPERATOR_INSTRUMENT_VALID`
y `OPERATOR_FORM_PREPARED`. Para cada sesión se utiliza una carpeta
`supervisor` **nueva**: el comando no modifica ACL de directorios
preexistentes ni sobreescribe materiales.

En Windows con Python 3.13 o posterior, `--new-private-dir`
crea una carpeta con herencia de permisos restringida; el protocolo
lee su descriptor NTFS mediante las API nativas y exige propietario
actual, herencia DACL desactivada y solo entradas de acceso permitidas
para titular, derechos de propietario, SYSTEM y Administradores.
Una carpeta que permita lectura a `Everyone`, `Users`, o grupos
no contemplados se rechaza con `OPERATOR_PRIVATE_DIR_UNVERIFIED`.
Se inspeccionan los alias y la DACL por ruta, pero la lectura v2
además abre el archivo una sola vez y compara el identificador del
archivo abierto con el inspeccionado. En Windows se vuelve a consultar
la DACL del **mismo HANDLE** mediante `GetSecurityInfo`, y los bytes
se consumen por ese descriptor, nunca reabriendo la ruta tras la
auditoría. Una sustitución de inode entre inspección y apertura se
rechaza antes de registrar una revisión o publicar puntuaciones.
En NTFS, un archivo `ficha.json:stream` puede compartir inode y DACL
con `ficha.json` mientras contiene bytes diferentes: el lector privado
v2 rechaza **también los ADS de origen**, no solo los destinos ADS, con
`OPERATOR_PRIVATE_FILE_ALIAS_FORBIDDEN`. Se comprobó con streams
alternativos reales de ficha codificada y rúbrica, sin alterar los
archivos base. No considerar las mismas identidad y ACL de un ADS
como evidencia de que sus bytes proceden de la ficha autorizada.
Para las salidas privadas v2, el publicador audita también la DACL del
archivo temporal recién abierto mediante su HANDLE **antes de escribir**,
revalida permisos de archivo/carpeta antes de enlazar el nombre final y
comprueba la DACL del inode publicado mientras conserva su alias temporal.
El publicador contrasta además el inode enlazado (`dev`, `ino`,
recuento de enlaces) y los **bytes completos del nombre final** con
los escritos y sincronizados originalmente. Si el inode stage se
sustituye o su contenido cambia antes del hardlink, devuelve
`OPERATOR_*_PUBLISHED_BYTES_MISMATCH` y retira solamente el
nombre final cuyo inode corresponde al enlace que acaba de crear.
El SHA de salida no depende solo de la intención de escritura.
La retirada de nombres stage/final se hace en Windows sobre un
`HANDLE` obtenido con autorización de borrado, tras comparar el
`fstat` de ese HANDLE con el inode original del escritor; se aplica
`SetFileInformationByHandle(FileDispositionInfo)` al objeto abierto.
Así, un reemplazo del nombre del destino **después** del hardlink
no se toma como identidad propia y no se borra un inode ajeno;
una sustitución del alias stage tampoco puede ocasionar que el
escritor borre otro archivo por nombre. En POSIX el equivalente
portátil disponible aquí solo comprueba `lstat` inmediatamente
antes de `unlink`: no se certifica una operación atómica
comparar-inode-y-borrar frente a otra identidad con control del directorio.
Si un tercero introduce un inode ajeno en el nombre final durante
una carrera, la operación falla sin declarar éxito; ese alias ajeno
puede permanecer porque su eliminación tampoco sería segura.
Una ACE heredable `Everyone READ` introducida entre la comprobación
inicial del supervisor y la creación del temporal produce rechazo
`OPERATOR_PRIVATE_OUTPUT_UNVERIFIED` o
`OPERATOR_PRIVATE_DIR_UNVERIFIED`, sin exportación válida. Se aplica a
ficha/rúbrica de `--prepare-form`, a `--record-form`, a `--evaluate-form`
y al recibo `--verify-chain-to`; el HTML participante es público por diseño.
En POSIX se usa `O_NOFOLLOW` cuando está disponible y se comprueba
`fstat` sobre el descriptor abierto. Se siguen rechazando
alias simbólicos y archivos con varios hardlinks. Esto **no** prueba
acceso desde un segundo token de
Windows, no impide acceso de administradores o del propio
supervisor ni certifica la confidencialidad en un equipo comprometido.

En POSIX se exige propietario actual y modo `0700`. El estado
`POSIX_MODE_0700_ONLY` **no certifica** ACL extendidas,
montajes remotos, políticas MAC ni aislamiento real entre personas.
En POSIX, el temporal privado nuevo se ajusta adicionalmente a
modo `0600` con `fchmod` antes de escribir, pero este camino no se
ha ejecutado en Linux durante la aceptación Windows.
La comprobación de identidad del descriptor tampoco certifica
ausencia de sustituciones en los directorios ancestros, uso de ACL
extendidas ni resistencia frente a un adversario que controle la
misma cuenta o los permisos del sistema.
No se certifica ausencia de exposiciones transitorias con cambios
arbitrarios de ACL ni resistencia a cambios posteriores del supervisor,
administradores o el mismo token. Los falsadores NTFS usaron una
única identidad Windows, no un atacante con cuenta separada.
Si los permisos no se pueden comprobar, la preparación v2 se
detiene antes de crear la clave. El supervisor debe custodiar
la cuenta y el directorio privado y comprobar las ACL reales
con las herramientas apropiadas del sistema operativo.
**La ficha de observaciones y la rúbrica deben crearse dentro de la
misma carpeta privada auditada.** La hoja HTML debe estar en otra
carpeta accesible a la participante. El CLI rechaza ahora una
preparación con dos carpetas supervisoras distintas mediante
`OPERATOR_FORM_PRIVATE_PARENTS_MISMATCH`, porque el registro y la
evaluación posteriores exigen la misma carpeta privada para fichero
de origen, rúbrica y resultado. No se crean archivos ante ese error.

Si una ficha v2 histórica se creó cuando todavía se admitían dos
carpetas supervisoras distintas, sus bytes y asignación A/B **no
cambian**. Para evaluarla, la supervisora debe colocar una copia
íntegra de la rúbrica en la carpeta privada auditada de la ficha
(con permisos seguros y sin alterar contenido), comprobar
`rubric_sha256` y continuar usando las rutas de esa carpeta.
No ejecutar `--prepare-form` otra vez para sustituirla ni considerar
que esa copia prueba por sí sola cuándo se distribuyó el formulario.
La operación `--prepare-form` genera tres ficheros UTF-8 propios de
**una sola versión v2**, con asignación real de posiciones correctas
A/B obtenida mediante CSPRNG y equilibrada 6/6. No reutilizar un formulario
entre participantes, compartir rúbricas ni generar el HTML por separado
mediante los comandos v1. La referencia corta de formulario en el HTML
es un código aleatorio local para cotejo, no una identidad personal ni
autenticación criptográfica. El SHA del HTML y el de la rúbrica quedan
vinculados a la ficha, pero no acreditan que alguien haya leído el papel.
La hoja HTML se abre localmente sin conexión; muestra preguntas bilingües
derivadas de las doce tareas **ya existentes**, pero la traducción al español
es un apoyo no validado psicométricamente. La rúbrica y el JSON de
observaciones quedan fuera del directorio `participante`, bajo el control
del supervisor. No compartir respuestas correctas, nombres, credenciales,
capturas ni URL privadas; no crear repositorios en estas carpetas.
Las carpetas separadas no aplican ACL protectoras por sí mismas:
esta modalidad verifica el descriptor real de la carpeta privada y
de los archivos leídos antes de procesar códigos o rúbricas.
La supervisora debe custodiar igualmente la cuenta y los ficheros,
fuera de la vista de la participante. Un usuario con
acceso al repositorio puede ver las soluciones históricas v1; un
usuario con acceso a la rúbrica v2 puede conocer las de esa variante.
Si un archivo existe, el protocolo NO lo sobrescribe: usar una carpeta
vacía para otra sesión, sin borrar ni reutilizar fichas anteriores.

En una **segunda consola** y desde el mismo checkout:

    python -B run_demo.py --science-only --port 0 --db (Join-Path $base 'sqlite\fantasy-no-usado.sqlite3')

Abrir solo la URL `http://127.0.0.1:PUERTO/` anunciada al enlazar el
socket. En la primera consola verificar ese puerto efectivo:

    python -B scripts/diagnose_live_science_beta.py --origin http://127.0.0.1:PUERTO

Se exige `status=PASS` con GET y SHA de ambos cortes antes de presentar
la pantalla. La persona participante puede recorrer Laboratorio (B0/B3,
S3, S7), las ocho vistas de Observatorio S9 y descargar/exportar
documentos públicos sintéticos verificables. La supervisora observa por
separado la ejecución técnica, la comprensión y la facilidad de uso,
sin introducir claves SCI ante la participante. El HTML es de lectura:
no recoge clics, respuestas ni métricas. Toda observación legítima
se codifica localmente, sin PII, preferentemente mediante
`--record-form`, en una sucesión de archivos externos; una tarea
técnica fallida o bloqueada exige respuesta
científica `NOT_OBSERVED`. **En v2, la columna `scientific`
de `observaciones-v2.json` solo acepta `A`, `B` o `NOT_OBSERVED`;
nunca transcribir códigos internos `SCI_OP...` de la rúbrica ni las
respuestas a un formulario distinto.** No alterar los campos `schema`,
`form_id`, `handout_sha256` o `rubric_sha256` de la ficha creada.
La ficha y sus revisiones pueden conservarse tras una interrupción;
no hay borrado automático ni almacenamiento de respuestas en la web.
Las tareas no observadas permanecen marcadas expresamente.

**Captura cerrada recomendada sin editar JSON:** el comando nuevo
`--record-form` anota exactamente una tarea en una **copia sucesora**
de la ficha v2. Las opciones son cuatro argumentos cerrados tras las
dos rutas: ID `OP01`–`OP12`, ejecución
`TECH_COMPLETED` / `TECH_FAILED` / `TECH_BLOCKED` /
`NOT_OBSERVED`, respuesta `A` / `B` / `NOT_OBSERVED`
y observación de uso `UX_CLEAR` / `UX_FRICTION` /
`UX_BLOCKED` / `NOT_OBSERVED`. No escribir respuesta A/B
si la ejecución no ha sido `TECH_COMPLETED`. Por ejemplo,
**solo para ensayar la sintaxis con una tarea ficticia, nunca
para afirmar que alguien ha participado**:

    python -B scripts/beta_science_operator_protocol.py --record-form (Join-Path $base 'supervisor\observaciones-v2.json') (Join-Path $base 'supervisor\revision-v2-01.json') OP01 TECH_BLOCKED NOT_OBSERVED UX_BLOCKED

Un resultado `OPERATOR_FORM_OBSERVATION_RECORDED` devuelve
`source_sha256` y `destination_sha256` de los bytes exactos,
sin imprimir la ruta ni las respuestas. La ficha anterior **no se
sobrescribe ni elimina**. En tareas posteriores se utiliza como
primera ruta el fichero sucesor más reciente y un nuevo nombre
como destino. Si se detecta un error de transcripción, volver a una
revisión anterior aún intacta y generar otra rama con nuevo nombre:
`OPERATOR_OBSERVATION_ALREADY_RECORDED` rechaza una segunda
anotación sobre la misma tarea de una revisión. Los doce IDs se
conservan siempre, con ausencia explícita, pero una tarea no
registrada permanece `NOT_OBSERVED`. No generar observaciones
ficticias para completar cuotas. El comando NO requiere leer ni
mostrar la clave de respuestas.

Cada sucesor conserva `predecessor_sha256` de los **bytes originales**
de su predecesora. Las fichas raíz v2 ya publicadas siguen teniendo su
esquema histórico sin ese campo: no se les atribuye retrospectivamente
una cadena verificada. Las revisiones nuevas mantienen el mismo
`schema` v2 e incorporan el enlace opcional. Solo una revisión
que realmente añade una tarea puede ser eslabón válido.

Para una **interrupción o reinicio**, detener con Ctrl+C y conservar
únicamente la ficha externa. El marcador `pfl_guest=v1` conserva siete
campos de selección, NO el puerto válido ni la evidencia. Reiniciar con
la misma `--db` y `--port 0`, y ejecutar el diagnóstico del nuevo
`--origin` usando `--guest-query 'URL_ANTIGUA_COMPLETA'` y
`--emit-verified-guest-url`. Abrir únicamente `verified_guest_url`
tras PASS; el doctor no resucita el puerto viejo ni asume que su SHA sea
válido. Las descargas S9 se verifican offline con los comprobadores
`verify_scientific_snapshot.py` y
`compare_scientific_exports.py --pair` descritos más abajo.

Tras la observación, y solo si hay alguna tarea realmente codificada:

    python -B scripts/beta_science_operator_protocol.py --evaluate-form (Join-Path $base 'supervisor\ULTIMA-REVISION-v2.json') (Join-Path $base 'supervisor\rubrica-privada-v2.json') (Join-Path $base 'supervisor\resultado-verificado-v2.json')

Para cerrar una cadena real, suministrar los nombres *efectivamente
guardados y en orden*, desde la ficha original hasta la última
revisión. Por ejemplo, para un caso de **solo dos revisiones**
(la sintaxis es ilustrativa, no observaciones humanas):

    python -B scripts/beta_science_operator_protocol.py --verify-chain-to (Join-Path $base 'supervisor\cadena-verificada.json') (Join-Path $base 'supervisor\rubrica-privada-v2.json') (Join-Path $base 'supervisor\resultado-verificado-v2.json') (Join-Path $base 'supervisor\observaciones-v2.json') (Join-Path $base 'supervisor\revision-v2-01.json') (Join-Path $base 'supervisor\revision-v2-02.json')

El estado `OPERATOR_FORM_CHAIN_VERIFIED` exige que cada eslabón
cite el SHA exacto del fichero anterior, que añada una sola tarea
previamente no codificada, que todas las demás permanezcan idénticas,
que se mantengan forma/versión/rúbrica y que el resultado final
coincida íntegramente con la puntuación obtenida de los mismos bytes.
El recibo final, creado exclusivamente en la carpeta privada, incluye
SHA de raíz, último fichero y resultado, sin respuestas originales.
Una revisión editada, omitida, reordenada o con otro formulario produce
rechazo sin crear recibo. El encadenamiento no certifica autoría,
consentimiento ni ausencia de reconstrucción intencionada de archivos
por una persona con control de todos ellos.

La escritura de un **archivo individual** sigue un protocolo
de publicación íntegra: archivo temporal de nombre impredecible
en el mismo directorio, escritura/flush/fsync, aparición del nombre
definitivo mediante enlace exclusivo, retirada del temporal y,
cuando el sistema lo permite, sincronización del directorio.
Un corte súbito puede dejar un temporal `.pfl-stage-*.tmp` o un
enlace adicional; no reutilizar esos ficheros sin inspección,
no borrarlos automáticamente y no asumir atomicidad de la
generación de los tres materiales originales como conjunto.
En Windows no se certifica la durabilidad del metadato de directorio
ante fallo eléctrico.

`OPERATOR_FORM_EVALUATION_EXPORTED` implica solamente que el archivo local
de códigos superó el contrato, no que una persona realmente participara
ni que se superase una puerta científica. La evaluación obliga a que la
rúbrica y la ficha sean de **la misma versión v2, formulario aleatorio,
SHA de hoja y SHA de clave**; un formulario mezclado se rechaza antes
de escribir resultado con `OPERATOR_FORM_MISMATCH`. La salida distingue
la ejecución técnica, la comprensión clasificada solo tras
`TECH_COMPLETED` y la usabilidad, y marca
`instrument_binding=MATCHED_V2_FORM_AND_RUBRIC`. No constituye prueba
de integridad frente a un supervisor que modifica deliberadamente
todos los archivos; las huellas son comprobaciones de consistencia,
no firmas digitales.

`coded_input_sha256` y `coded_input_bytes` identifican los
**bytes realmente leídos** de la última revisión codificada
(incluidos espacios y salto final); permiten contrastar el informe
contra ese fichero conservado, pero no acreditan identidad, consentimiento
ni autenticidad externa. La ruta `ULTIMA-REVISION-v2.json`
es un marcador que la persona supervisora debe sustituir por el
nombre realmente creado, no un archivo creado automáticamente.
Si las doce tareas siguen totalmente `NOT_OBSERVED`,
`OPERATOR_NO_OBSERVATIONS` es correcto y **no** debe existir
`resultado-verificado-v2.json`. Otros rechazos incluyen
`OPERATOR_SESSION_INCOMPLETE`, `OPERATOR_INPUT_INVALID`,
`OPERATOR_JSON_INVALID`, `OPERATOR_OUTPUT_EXISTS`,
`OPERATOR_OUTPUT_PATH_FORBIDDEN` y, en Windows, el veto ADS
`OPERATOR_OUTPUT_PATH_INVALID`. Los errores no revelan rutas ni PII.
No redirigir el resultado con `>` en PowerShell 5.1.

**Compatibilidad explícita:** las nueve acciones anteriores
`--participant-sheet`, `--participant-handout`, `--template`,
`--template-to`, `--blank-session`, `--new-session`, `--evaluate`,
`--evaluate-to` y `--self-check` permanecen disponibles para fichas
históricas **v1**. Ese instrumento tenía una clave A/B pública, fija
y repetible y permitía códigos internos SCI sin identificador de
formulario; por ello sus resultados nuevos llevan
`instrument_binding=LEGACY_UNBOUND` aunque incluyan la huella de la
rúbrica actual. **No** debe puntuarse una ficha v1 como si fuese v2,
ni trasladar el resultado antiguo a una nueva variante. Para una
primera sesión supervisada nueva, usar preferentemente v2.

Cerrar con Ctrl+C, comprobar que el puerto antiguo ya no responde y
conservar o suprimir **manualmente** los ficheros propios fuera de Git
según la decisión legítima de la persona supervisora. La aplicación
no borra de forma automática documentación humana ni realiza
telemetría. El único ensayo automatizado de este procedimiento usa
fixtures inventados y no acredita validación humana.

## Comprobar el núcleo científico

Desde la raíz del repositorio, con Python y Node.js instalados (esta
validación local se ejecutó con **Python 3.14.3 y Node.js 24.16.0**;
la compatibilidad de versiones anteriores no se ha revalidado en esta tanda):

    python scripts/beta_scientific_smoke.py

El comando no reutiliza cuentas, originales ni bases persistentes del usuario.
Crea un servidor HTTP local y bases SQLite temporales, consulta realmente
/api/health, /api/beta-readiness, /api/scientific-integration-lab y
/api/scientific-registry, verifica SHA-256 del snapshot y los 20 testigos S7
del corte tardío.
Incorpora mediante procesos CLI independientes sandbox_alpha_v1,
sandbox_beta_v1 y sandbox_bad_issuer: dos fuentes lógicas ficticias y un
rechazo. Comprueba cortes early/late, errores HTTP 400/403/503 e integridad
fail-closed al adulterar solamente su propia base temporal. Al finalizar
cierra el servicio y elimina el entorno de prueba.

Un resultado de status PASS y nueve controles acredita **solo** este
recorrido local; no sustituye un ensayo de seguridad de una instalación real,
una revisión de accesibilidad o evidencia externa. Si status es FAIL, el
campo error_code informa del paso sin imprimir datos privados; el proceso
devuelve código no cero. Su regresión reproducible es:

    python -m pytest -q tests/test_beta_scientific_smoke.py

La **aceptación focal conjunta**, que incluye reinicios sobre SQLite
persistente, separación de dos cuentas, acceso científico sin cuentas,
exportación SHA y recorridos de navegador Chromium, se ejecuta con:

    python scripts/beta_acceptance.py

Produce un recibo JSON con las pruebas realmente superadas, HEAD Git y
hashes SHA-256 de sus ficheros de prueba. Sale con código no cero si falta
una dependencia, un test esperado, Chrome o un contraste falla. El resultado
se limita a esta beta local; no sustituye el conjunto histórico de tests,
una revisión de seguridad de producción o un gate científico.

## Reutilizar los recibos sin abrir el servidor

En el **Observatorio**, «Exportar snapshot S9 + SHA» descarga un archivo JSON
correspondiente al corte, familia, vigencia y límite de primera publicación
ficticia actualmente seleccionados. Se puede comprobar ese archivo **sin
cuentas, navegador, bases SQLite, red ni fuentes originales**:

    python scripts/verify_scientific_snapshot.py "mi-snapshot-s9.json"

El verificador offline valida el contrato cerrado, la serialización canónica
exacta, SHA-256, longitud, límites temporales, revisiones, fuente-localidad,
privacidad, derechos y estado R5. Su salida JSON contiene solo un resumen
seguro, o un código de rechazo si encuentra una contradicción. La coincidencia
del hash prueba consistencia de bytes con el recibo, **no** que el emisor sea
una autoridad real ni que los derechos permitan republicar datos.

Tras exportar por separado un corte temprano y otro tardío con los mismos
`valid_at` y filtro de familia, se puede generar una comparación offline:

    python scripts/compare_scientific_exports.py "temprano.json" "tardio.json"

Este segundo comando verifica ambos recibos de forma independiente antes de
comparar. Solo representa **visibilidad documental bajo relojes ficticios
estipulados**: no implica que un documento ausente fuera rechazado, que una
revisión equivalga a otra decisión, que se conozca el denominador ni que haya
cambiado realmente una institución española. En la interfaz, la pestaña
«Comparar cortes» ofrece la misma distinción mediante dos consultas GET
independientes SHA-verificadas, sin iniciar sesión de Fantasy.

Para evitar dos descargas manuales, desde la pestaña **«Comparar cortes»**
puedes guardar una única **pareja verificable**. Se trata de un sobre JSON
con **dos exportaciones S9 completas, cada una con su SHA-256 canónico**, y
un tercer recibo SHA-256 del sobre conjunto. Tras guardarlo, también es
posible comprobarlo y compararlo sin servidor ni cuenta:

    python scripts/compare_scientific_exports.py --pair "pareja-s9.json"

El modo `--pair` verifica de manera independiente las dos exportaciones y
la serialización exacta del sobre antes de producir los mismos contadores
descriptivos. Los dos archivos individuales siguen siendo válidos mediante
el comando anterior. La pareja **no** es un documento firmado oficialmente,
un reconocimiento de derechos, una observación institucional auténtica ni
una prueba de cambio causal. Una selección que cambie durante la digestión,
un HTTP 400/503 o una consulta obsoleta bloquean la descarga en vez de
reutilizar los datos anteriores.

## Arrancar el prototipo interactivo

    python run_demo.py

Abrir http://127.0.0.1:8787. A diferencia del smoke, este lanzador
**sí conserva** datos locales en data/demo/game.db y cuentas de prueba en
data/demo/accounts.sqlite3. Estas cuentas locales no equivalen a identidad
para internet, TLS ni despliegue multiusuario seguro. No exponer el puerto
mediante NAT, túneles, proxies públicos o interfaces distintas de loopback.

Si el puerto está ocupado, se puede seleccionar otro. Para una base aislada
de prueba, se puede elegir una ruta distinta:

    python run_demo.py --port 8788 --db data/demo/beta_separada.sqlite3

El parámetro --port 0 pide al sistema un puerto libre y muestra la URL real.
No existe una opción --host para habilitar interfaces públicas.

## Modo recomendado para examinar solamente el núcleo científico

    python run_demo.py --science-only --port 0

El modo **science-only** no inicia ni escribe ninguna cuenta Fantasy, no
ofrece endpoints de estado de juego, mercado, fichajes o jornadas y **deniega
cualquier POST**. Solo permite los activos web, la señal de sesión
no autenticada, el estado de salud, la preparación de beta, el Laboratorio
y el registro científico con sus consultas/exportaciones sintéticas. La
interfaz inicia directamente la visita científica de solo lectura cuando
detecta este modo. El puerto continúa limitado a 127.0.0.1.

La prueba focal de reinicio `tests/test_beta_restart_isolation.py` también
abre y cierra **dos procesos reales science-only** contra el mismo registro
SQLite sintético de prueba, verifica sus recibos antes/después de inscribir
fixtures ficticios por CLI, y comprueba el HTTP 503 de una copia deliberadamente
adulterada. El registro original no se modifica durante esa prueba de
recuperación; ninguna cuenta o base Fantasy se crea por este recorrido.

Por defecto, el registro SQLite se crea en
data/science_beta/scientific_registry_synthetic.sqlite3, un directorio
**distinto de** data/demo/ y excluido expresamente de Git. También puede
elegirse otra ruta de base independiente mediante --db; el registro científico
se ubica junto a ella, sin necesitar un fichero de juego.

**Primera visita, sin cuenta:** desde la pantalla de acceso, pulsa
«Entrar al Observatorio y Laboratorio». El visitante dispone únicamente
de esas dos pestañas; puede examinar los cortes del laboratorio y el
registro sintético S9 con su SHA verificado, sin crear una cuenta ni
acceder al mercado, los clubes o las operaciones POST. El botón de retorno
devuelve al formulario de acceso. Un HTTP 503 o un recibo SHA incompatible
bloquean la vista en vez de conservar datos obsoletos. La exportación S9
se permite únicamente para la proyección **pública sintética con SHA
verificado**; la preadmisión interactiva, la exportación S8 independiente
y cualquier escritura quedan fuera del modo visitante.

El Laboratorio muestra modelos rivales B0/B3, sensibilidad condicional S3,
testigos S7 y el registro histórico-relacional sintético S9. Una validación
de sandbox no es admisión científica, licencia, evidencia histórica
española ni estimación causal. El contrato técnico está en
docs/S9_DURABLE_SYNTHETIC_SCIENTIFIC_REGISTRY_20261101.md.

## Recuperar una consulta anónima tras cerrar o reiniciar

El **modo visitante** conserva la selección científica en la **URL del propio
navegador**, no en cuentas, almacenamiento local ni bases Fantasy. Se puede
copiar la dirección de la pestaña del Observatorio después de seleccionar
el corte, la vigencia `valid_at`, la familia, el techo ficticio de
publicación, el escenario del Laboratorio y «Comparar cortes». Al reabrirla
tras recargar la página o reiniciar `run_demo.py --science-only` contra el
mismo directorio SQLite, se restablecen **los filtros**, pero **no** los
resultados ni los recibos previos: el navegador vuelve a solicitar al
servidor ambas proyecciones y recalcula sus SHA-256. Sin servicio disponible
no se recupera un registro del pasado desde la URL.

Para que el mismo enlace funcione tras reiniciar, utiliza **el mismo puerto
local**, por ejemplo `python run_demo.py --science-only --port 8787`, y el
mismo directorio SQLite. Con `--port 0`, el sistema puede seleccionar un
puerto diferente en cada arranque: en ese caso, hay que sustituir el
protocolo/host/puerto del enlace por los del nuevo servidor local antes de
abrirlo. No se redirige automáticamente a otro servicio ni se habilita el
acceso desde fuera de 127.0.0.1.

El lanzador dispone además de un procedimiento explícito para recuperar el
**enlace de consulta** sin arrastrar un puerto caducado. Cierra el proceso
anterior y ejecuta, sustituyendo el ejemplo por una URL de visitante realmente
copiada desde el Observatorio (entre comillas por los caracteres `&`):

    python run_demo.py --science-only --port 0 --resume-guest-query "http://127.0.0.1:8787/?pfl_guest=v1&cut=late&valid_at=2026-09-15&family=all&published_until=as_of&scenario=baseline&view=compare"

La primera línea del terminal anuncia **el puerto local efectivamente
asignado**. Solo después de enlazar el socket correctamente, una línea
`REANUDAR CONSULTA CIENTÍFICA` debe mostrar la URL validada con **ese
puerto nuevo**, no el del marcador antiguo. Debes abrir o copiar esta
**nueva** dirección; la antigua no se considera disponible. También se
acepta únicamente la consulta relativa, comenzando por `?pfl_guest=v1`,
para no depender de una dirección anterior. El enlace entrante ha de ser
una selección visitante cerrada, no una URL con usuario/contraseña, fragmentos,
identificadores internos o un dominio externo. Una selección inválida
impide el arranque antes de abrir el servicio o crear bases.

La dirección nueva acredita únicamente que el socket local ha conseguido
abrirse: **no certifica que SQLite esté sano ni que la consulta científica
sea admisible**. Si los endpoints devuelven HTTP 400/503, la pantalla debe
rechazar datos y descargas hasta un nuevo GET y verificación SHA satisfactorios.
Si se cierra el servidor, la URL deja de estar disponible; ni el viejo
marcador ni la salida anterior del terminal constituyen un servicio activo.

## Diagnosticar una instancia científica local que ya está ejecutándose

El smoke `scripts/beta_scientific_smoke.py` crea un servidor desechable para
probar el código. No comprueba si **tu propio proceso** iniciado en otro
terminal está vivo. Para ese caso, toma la dirección local que acaba de
anunciar el lanzador (cambia el puerto si fue elegido con `--port 0`) y
ejecuta en otro terminal:

    python -B scripts/diagnose_live_science_beta.py --origin http://127.0.0.1:8787

También puedes añadir `--guest-query` con la URL anterior de visitante
entre comillas. El diagnóstico utiliza solo la **selección** de esa URL
para contrastarla contra la **instancia actualmente indicada en --origin**;
no contacta con el servidor antiguo ni confía en datos o SHA contenidos
en un marcador. Comprueba GET de sesión anónima, modo científico exclusivo,
salud/preparación del servidor, contrato del Laboratorio, dos respuestas del
registro S9 independientes (early/late), sus recibos canónicos mediante el
verificador offline existente y su comparación sintética.

La salida es una línea JSON `PASS` o `FAIL` con contadores/SHAs públicos
o un código seguro de error. No escribe cuentas, no ingiere originales, no
altera SQLite y no incluye respuestas brutas. Un servidor detenido debe
aparecer como `SERVER_UNAVAILABLE`; errores HTTP 400/503, contratos,
derechos o integridad incorrectos se indican como fallos distintos. El
resultado `PASS` es un **diagnóstico de ingeniería local**, nunca una
firma, certificación histórica, licencia, aprobación humana o puerta R5.
Solo acepta una dirección de **127.0.0.1** con puerto explícito: no es
un auditor remoto ni se debe exponer el servidor para ejecutarlo.

El argumento solo puede usarse junto con `--science-only`; no habilita
cuentas, redirecciones, acceso público ni ninguna escritura. No convierte
un marcador en evidencia: después de abrir el navegador hay que volver a
verificar los recibos SHA y, para las exportaciones emparejadas, ejecutar
`scripts/compare_scientific_exports.py --pair` sobre la nueva descarga.

El único contrato permitido de URL visitante es
`pfl_guest=v1`, `cut`, `valid_at`, `family`, `published_until`,
`scenario` y `view`. Se exigen exactamente esas siete claves, sin
duplicados ni extras y con valores de las listas cerradas del fixture S9.
La publicación estipulada de 30/10 no puede elegirse con `cut=early`.
La vista `view` conserva cualquiera de las **ocho secciones existentes**
del registro: `sources` (distribuciones y revisiones), `compare` (cortes),
`chain` (actores y procesos fuente-locales), `chronicle` (roles y eventos),
`episodes`, `admission` (preadmisiones), `intake` (registro de
incorporaciones sintéticas) y `quality`. Al seleccionar una sección,
su URL se actualiza **sin capturar los contenidos**, y al volver a abrirla
se muestra esa misma sección únicamente tras GET y SHA nuevos. La selección
de tipo de nodo dentro de un grafo vuelve a `ALL` después de una recarga;
no debe confundirse el filtro visual con el estado de conocimiento
acreditado. En una base `science-only` recién creada, la sección `intake`
puede contener **cero** incorporaciones: no se crean registros ficticios
solo para rellenar una vista.
Las URL extrañas, repetidas o cronológicamente incompatibles se bloquean
**sin consultar el Laboratorio ni el Observatorio**, y ofrecen «Restablecer
consulta» para volver a una selección segura. Un HTTP 400/503 o un SHA
incompatible siguen invalidando el contenido y la exportación; el enlace
por sí solo **no** es un recibo, una copia de originales ni una autorización.

Esta persistencia se limita al modo **visitante**. Nunca implica sesión
de usuario, autenticación, escrituras HTTP ni almacenamiento de credenciales.
No se comparten identificadores privados, originales o bytes de fuente-local
en la URL. Una consulta guardada no prueba que el mismo corte estuviera
disponible históricamente: todos los relojes S9 siguen siendo ficticios.

## Explorador S8 de solo lectura en el Laboratorio visitante

El Laboratorio del visitante ofrece cuatro paneles: **mecanismos B0/B3**,
**sensibilidad condicional S3**, **testigos S7** y **distribuciones S8**.
El resultado procede del GET sintético del Laboratorio, no de fuentes
externas. No autoriza exportación S8, simulación de incorporación,
credenciales ni escritura de una cuenta; el Observatorio S9 conserva sus
exportaciones y verificadores offline separados.

B0 calendario y B3 selección editorial muestran la misma proyección
publicada; E2 pendiente y E4 censurado no son rechazos. Las cotas S3, solo
visibles en el corte tardío, dependen de un supuesto de selección,
no son causales ni estimaciones de expedientes reales. Los veinte testigos
diferencian NEITHER, CONFLICT e INADMISSIBLE como estados *científicos*
de fixtures: nunca equivalen a HTTP 400/503. Se preservan contradicciones.

En la tabla S8, el filtro de primera publicación ficticia reutiliza
el campo `published_until` de la URL visitante de **siete claves
exactas**, sin guardar contenido. Solo aparecen descriptores públicos
con `first_public_at_fixture` anterior al techo seleccionado y
`captured_at_fixture` no posterior a `as_of`. El corte
temprano prohíbe la fecha del 30 de octubre. Cambiar el filtro
refresca el registro S9 e invalida recibos anteriores. El SHA local no
demuestra autenticidad del emisor, derechos, censo ni primera publicación
histórica. Oculto en el filtro no es negativo ni rechazo ni ausencia.

Para aceptación humana (todavía pendiente): arrancar
`python run_demo.py --science-only --port 0`, abrir Laboratorio,
inspeccionar los cuatro paneles, comparar S3 early/late y los veinte
S7, cambiar el techo ficticio de publicación, regresar al
Observatorio, reanudar la URL de siete campos tras reinicio y verificar
offline una descarga S9 nueva. Este recorrido no convierte un test
automatizado en aceptación humana.

El dry-run S8 en cuenta local descarta las respuestas tardías
de un candidato anterior después de cambiar la selección,
incluido HTTP 503 y secuencias A→B→A. No permite admisión
científica real.

## Cancelación de consultas anteriores y alcance de familia S9

En una cuenta local, el dry-run S8 asocia cada respuesta con la generación
de selección: candidato, corte, escenario, primera publicación ficticia,
vigencias bitemporales, filtros S9, recarga, cambio de vista o cierre de
sesión. Ante A→B→A, un resultado, error HTTP 503 o finalización
tardíos de A no deben sobrescribir el nuevo A. Esta invalidación
de tickets no afirma cancelar físicamente una solicitud enviada.
Las exportaciones S8 comprueban la generación antes de descargar
y silencian el error de una sesión anterior tras salir de la cuenta.
Un SHA válido del fixture no autoriza reutilizar un archivo obsoleto.

En el Observatorio S9, las vistas Preadmisión e Incorporaciones usan
el universo fuente-local de familia Todas. Las familias CHAIN,
CHRONICLE o PP04 excluyen esa sección de la proyección, que puede
regresar cero filas sin que el ledger original esté vacío.
La UI informa «Fuera del filtro de familia» en esas dos vistas.
Volver a Todas permite distinguir la exclusión de la ausencia real
de incorporaciones en una base SQLite sintética vacía. No se
imputan negativos, cohortes ni denegaciones por la selección.

Para comprobar la exportación S8 en una cuenta de la demostración,
la prueba CDP Chrome utiliza el gestor de descargas real en un
directorio temporal aislado. El archivo se abre desde disco y se
verifican su JSON canónico, bytes, SHA y condiciones sintéticas;
una respuesta alterada no puede producir una segunda descarga.
Las exportaciones S9 individual y emparejada y los verificadores
offline Python conservan los contratos independientes existentes.

## Enlace recuperado de una instancia activa tras verificarla

El doctor de una beta cientifica local ya ejecutandose en otro puerto
puede emitir opcionalmente una URL vigente de consulta con:

    python -B scripts/diagnose_live_science_beta.py --origin http://127.0.0.1:8787 --guest-query "http://127.0.0.1:8765/?pfl_guest=v1&cut=late&valid_at=2026-09-15&family=all&published_until=as_of&scenario=baseline&view=admission" --emit-verified-guest-url

Solo con status PASS se incluye verified_guest_url, compuesta con el
puerto actual de --origin y exactamente siete filtros publicos canonicos,
entre ellos la vista seleccionada de las ocho opciones S9. No se contacta
con el antiguo servidor. Sin la opcion, el JSON del doctor sigue igual
y no expone direcciones ni puertos. Ante servidor detenido, otra cuenta,
HTTP 400/503, SHA o contrato incompatible, FAIL no contiene enlace.

Este enlace refleja disponibilidad en el momento de los GET, no garantiza
continuidad futura ni autenticidad del emisor, licencia externa, censo
ALL_RECEIVED, causalidad ni desbloqueo de R5 STOP.

El export S9 individual y emparejado conserva sus bytes/contratos; errores
de una verificacion SHA antigua que terminan tras salir del Observatorio
no muestran avisos obsoletos en la pantalla de login, ni producen descarga.
Los errores de una consulta aun vigente siguen visibles.

## Aceptación científica instrumentada de tareas humanas

El instrumento de operador está descrito en
[Protocolo de aceptación humana](BETA_HUMAN_ACCEPTANCE_PROTOCOL.md).
No requiere cuenta, no recopila respuestas automáticamente y no equivale
a ejecutar un estudio con participantes.

Desde la raíz del repositorio, validar la integridad de la rúbrica,
consultar la hoja sin soluciones para un participante y mostrar la clave
y los criterios reservados al operador mediante comandos independientes:

    python -B scripts/beta_science_operator_protocol.py --self-check
    python -B scripts/beta_science_operator_protocol.py --participant-sheet
    python -B scripts/beta_science_operator_protocol.py --template
    python -B scripts/beta_science_operator_protocol.py --new-session RUTA_JSON_EXTERNA

La hoja del participante muestra opciones A/B opacas, no los códigos
SCI que revelan contenido ni una posición sistemática de la respuesta
correcta. La clave se contrabalancea 6/6 sin alternancia simple por paridad
de tarea, pero su orden fijo y público NO constituye aleatorización de
participantes ni validación humana. Solo la rúbrica del operador relaciona
A/B con SCI_OPxx.
La nueva ficha contiene las doce tareas OP01--OP12 con todos los valores
NOT_OBSERVED; por sí misma no prueba participación.

Para Windows PowerShell 5.1, usar --new-session y no redirigir
--blank-session con el operador de shell >: esa redirección puede
escribir UTF-16LE, incompatible con el contrato JSON UTF-8. La ruta
de salida debe existir solo como ubicación elegida FUERA del checkout
y la CLI no sobrescribe ficheros existentes. No imprime esa ruta ni
resultados humanos.
En Windows se rechazan asimismo los nombres de archivo con ':'
por los flujos alternativos de NTFS: un hardlink exterior podría
referenciar el mismo inode que un fichero de Git. No usar ADS como
almacenamiento de fichas; usar un JSON ordinario nuevo y externo.


El registro voluntario se limita a un JSON local con esquema cerrado
pfl.beta_science_operator_observations.v1 y observaciones de cuatro
campos task_id, technical, scientific y usability (códigos permitidos
por la rúbrica). Si la persona se abstiene o no se observó una tarea,
usar NOT_OBSERVED. Nunca asignar una respuesta científica si el acceso
técnico falló o quedó bloqueado. No registrar datos personales,
nombres, capturas, direcciones, tiempos ni texto libre. Para evaluar una
ficha local voluntaria, fuera del repositorio:

    python -B scripts/beta_science_operator_protocol.py --evaluate "RUTA_JSON_VOLUNTARIA"

La evaluación exige exactamente doce IDs de tarea, admitiendo
NOT_OBSERVED en tareas individuales. La ausencia de cualquier tarea
produce OPERATOR_SESSION_INCOMPLETE; una ficha con todas
NOT_OBSERVED produce OPERATOR_NO_OBSERVATIONS. Una tarea no completada
técnicamente no admite respuesta científica, ni correcta ni
incorrecta. Una respuesta humana no se deduce de los checkpoints
automáticos.

Este comando emite solo conteos y códigos seguros. No infiere
participantes ni índices de satisfacción; el operador deberá
conservar separado cualquier consentimiento/protocolo externo si fuera
necesario, nunca subir respuestas individuales a Git.

La comprobación técnica usa el recorrido CDP real ya existente,
que marca diez puntos de control después de verificar cada operación:
B0/B3, S3, S7, distribuciones S8, ocho pestañas S9, familia,
comparación temporal, exports individual/pareja y recuperación
tras reinicio con URL de puerto nuevo. El marcador
technical_task_ids_passed NO es evidencia de comprensión humana.
La aceptación general integra tests del instrumento, no respuestas
de participantes ni admisión científica R5.

## Bloqueos de la beta pública

STOP_R5 permanece, con **0/6 puertas** y cero ciclos AB-R nuevos.
Faltan universo independiente ALL_RECEIVED, denominador externo, episodios
con negativos/pendientes/censura verificables, dos vintages auténticas,
first_public acreditado, derechos por distribución/revisión/finalidad,
garantías de seguridad y revisión humana del producto. Esta fase es
**local, sintética, no pública**; superar un test HTTP no levanta R5.
