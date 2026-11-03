# Protocolo instrumentado de aceptaci`n humana: beta cient`fica local

**Estado: instrumento operativo para sesiones voluntarias futuras.**
Ninguna persona ha participado en esta ejecuci`n. Las pruebas Chrome CDP
y HTTP usan fixtures sint`ticos: no equivalen a comprensi`n, satisfacci`n,
usabilidad humana ni evidencia emp`rica sobre instituciones espa`olas.

## Preparaci`n y fronteras de privacidad

Preparar un `nico equipo aislado con Python, Node y Chrome. Abrir una base
SQLite desechable, distinta de cualquier cuenta del usuario. Arrancar:

    python -B run_demo.py --science-only --port 0 --db RUTA_SQLITE_DESECHABLE

Utilizar la URL de loopback mostrada en el terminal. El participante puede
parar cuando quiera. No abrir servidores p`blicos, t`neles, cuentas,
documentos originales ni sistemas administrativos. Registrar por
separado (a) el efecto t`cnico visible y (b) la respuesta conceptual.
Un `xito Chrome no es una respuesta de participante.

No se recogen nombre, correo, IP, identidades, tiempos personales, voz,
pantalla, cookies, credenciales, URLs completas, texto libre ni historial.
Cualquier registro humano es local y voluntario; no se sube a Git.

## Recorrido y criterios observables

Los c`digos son identificadores de tareas t`cnicas usados por Chrome CDP.
El participante realiza las mismas acciones sin ver primero las soluciones.
Las expectativas cient`ficas de la tercera columna son para la persona que
eval`a, no instrucciones que deban mostrarse antes de obtener la respuesta.

| ID | Acci`n observable | Criterio operativo y de interpretaci`n |
| --- | --- | --- |
| `LAB_B0_B3` | Abrir Laboratorio, Mecanismos, e indicar si los datos publicados identifican la causa de no publicaci`n de E3 | B0 y B3 son observacionalmente equivalentes: no permiten decidir entre calendario y selecci`n; E2 pendiente y E4 censurado no son rechazos |
| `LAB_S3_TEMPORAL` | Inspeccionar las cotas S3 en late y cambiar a early | Intervalo de cambio exacto `-11/52` a `47/119` sujeto a hip`tesis de selecci`n, no causal; early carece de esas cotas, sin anticipaci`n |
| `LAB_S7_20` | Examinar testigos S7 y diferenciar contradicci`n de fallo del servidor | Veinte conjuntos, seis estados; NEITHER/CONFLICT/INADMISSIBLE son cient`ficos, no HTTP 503 ni resultados administrativos reales |
| `LAB_S8_DESCRIPTORS` | Explorar distribuciones, revisiones, primeras publicaciones y derechos | Filtrado por primera publicaci`n ficticia y captura anterior a as_of; SHA de fixture no certifica emisor, derechos ni cobertura |
| `S9_EIGHT_TABS` | Visitar las ocho pesta`as S9 e identificar fuente-localidad, eventos, revisiones y preadmisi`n | No confundir persona, documento, episodio, decisi`n, revisi`n ni identidad de otro emisor |
| `S9_FAMILY_SCOPE` | Filtrar CHAIN en Preadmisi`n e Incorporaciones y regresar a Todas | Fuera del filtro de familia no equivale a cero global ni rechazo. Una SQLite genuinamente vac`a en Todas puede informar cero incorporaciones sint`ticas |
| `S9_TEMPORAL_COMPARE` | Cambiar valid_at, as_of y techo first_public; comparar early/late | Dos SHA independientes, sin mirar hacia el futuro. Diferencia en visibilidad ficticia no demuestra cambio real ni efecto causal |
| `S9_SINGLE_EXPORT_OFFLINE` | Descargar snapshot S9 y verificarlo con CLI offline | Archivo Chrome real y CLI verify_scientific_snapshot.py PASS sobre sus bytes; no autentica instituci`n |
| `S9_PAIR_EXPORT_OFFLINE` | Descargar pareja early/late y verificarla offline | Exactamente dos snapshots, recibos SHA originales m`s pair_receipt sobre JSON UTF-8 can`nico; compare_scientific_exports.py --pair PASS |
| `RESTART_DOCTOR_GUEST_LINK` | Guardar marcador de siete campos; reiniciar misma SQLite con puerto distinto y recuperar consulta | Puerto viejo deja de acreditar servicio; el doctor solo ofrece URL con puerto actual tras PASS y nuevas consultas GET/SHA |

Se preservan PP04 INCLUIDAS/NO INCLUIDAS, negativos expl`citos,
pendencia y censura; ninguno es un denominador independiente ALL_RECEIVED.
El recorrido t`cnico tambi`n contrasta HTTP 400/503, SHA adversarial,
no POST ni cuentas en modo visitante y persistencia SQLite del fixture.

## Clasificar incidencias sin simular personas

**T`cnica:** falla una transici`n o contrato verificable (panel, GET, SHA,
archivo, recuperaci`n, reloj, enlace o derechos). **Interpretaci`n:** el
programa funcion` y una respuesta humana voluntaria contradice el
significado de los estados. **Usabilidad:** el programa funciona, pero
no se encuentra/completa la acci`n sin ayuda. Si la lectura estaba
bloqueada por fallo t`cnico, la interpretaci`n queda **NO EVALUADA**,
no marcada como error humano. Una tarea sin respuesta es NO OBSERVADA,
nunca acierto ni fallo ficticio.

## Instrumento ejecutable y registro local opcional

La CLI dispone de cuatro rutas independientes que no llaman al servidor
ni modifican SQLite:

    python -B scripts/beta_science_operator_protocol.py --self-check
    python -B scripts/beta_science_operator_protocol.py --participant-sheet
    python -B scripts/beta_science_operator_protocol.py --template
    python -B scripts/beta_science_operator_protocol.py --evaluate RUTA_JSON_LOCAL

La hoja `--participant-sheet` incluye preguntas y opciones, pero no revela
la solucion, las explicaciones de evaluacion ni los IDs de automatizacion.
La rubrica `--template` es SOLO para el observador y contiene los
criterios, el codigo de respuesta correcta y los valores validos de la
ficha. No mostrar la rubrica al participante antes de registrar
respuestas. `--self-check` comprueba la estructura del instrumento,
no comprueba un servidor activo ni la comprension humana.

La ficha voluntaria `--evaluate` se construye manualmente fuera de
Git, con esquema `pfl.beta_science_operator_observations.v1` y
un array `observations`, cada una con solo `task_id`, `technical`,
`scientific` y `usability`; deben elegirse los codigos cerrados
del operador. No se permite anadir nombre, contexto de persona, captura,
URL, comentario libre o timestamp. No reutilizar datos individuales
entre sesiones. Si la tarea tiene `TECH_BLOCKED` o `TECH_FAILED`,
la respuesta cientifica DEBE ser `NOT_OBSERVED`; introducir una
opcion de comprension en esas condiciones es un error de contrato que
la CLI rechaza. La salida contiene codigos de estado y conteos
por tarea/dimension, pero no atribuye numero de participantes.

Las pruebas del parser emplean solamente fixtures temporales inventados
para demostrar rechazo de campos prohibidos; no son personas,
respuestas reales, resultados de un estudio ni telemetria.

La CLI local `scripts/beta_science_operator_protocol.py` suministra
una plantilla con opciones y criterios cerrados y un evaluador para
registros voluntarios. No incluir datos personales, narraciones libres,
rutas locales, timestamps de navegaci`n ni identificadores `nicos.
Los archivos de trabajo humanos opcionales no se versionan ni publican.
Su ausencia es un estado v`lido.

**No existe tasa humana de `xito, comprensi`n ni satisfacci`n** mientras
no haya observaciones humanas efectivas. Una muestra futura requerir`
definir condiciones de participaci`n y denominadores observados antes
de calcular cualquier proporci`n.

## L`mites

R5 permanece STOP_R5, 0/6 puertas y 0 AB-R nuevos. Este instrumento
no acredita autenticidad editorial, derechos de difusi`n, vintages
institucionales, fuente de ALL_RECEIVED ni causalidad. La validaci`n
humana sigue pendiente aunque el navegador t`cnico apruebe.
