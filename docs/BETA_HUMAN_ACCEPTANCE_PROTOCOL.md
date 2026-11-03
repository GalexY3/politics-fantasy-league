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

La CLI dispone de seis rutas independientes que no llaman al servidor
ni modifican SQLite:

    python -B scripts/beta_science_operator_protocol.py --self-check
    python -B scripts/beta_science_operator_protocol.py --participant-sheet
    python -B scripts/beta_science_operator_protocol.py --template
    python -B scripts/beta_science_operator_protocol.py --blank-session
    python -B scripts/beta_science_operator_protocol.py --new-session RUTA_JSON_LOCAL_EXTERNA
    python -B scripts/beta_science_operator_protocol.py --evaluate RUTA_JSON_LOCAL

En Windows, evitar redirigir la salida de --blank-session mediante
PowerShell 5.1: su redirección puede generar UTF-16LE, que el evaluador
rechaza correctamente porque el contrato exige UTF-8. Usar la nueva
operación explícita para crear la ficha fuera del checkout, una sola
vez y sin sobrescribir archivos existentes:

    python -B scripts/beta_science_operator_protocol.py --new-session RUTA_JSON_LOCAL_EXTERNA

La CLI produce el fichero UTF-8 con las doce tareas OP01--OP12, todas
marcadas NOT_OBSERVED, y emite a la consola solo el código de éxito,
nunca la ruta ni el contenido. No crea nada si la ruta ya existe
o esta dentro del repositorio. La persona puede abstenerse; el
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
