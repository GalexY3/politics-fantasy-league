# T010 · Reparar las dos incidencias de T009 y revalidar en Linux

**Estado: PENDIENTE — tarea de ejecución para Codex, NO ciclo AB-H.** Esta tarea es de mantenimiento y QA correctiva. La campaña MAIN20B terminó con **20 intentos utilizados y ninguna autorización restante**. No abrir, crear ni contabilizar ciclos AB con esta tarea. No modificar métricas científicas, CT2, gates ni puntuación de personas reales.

## Procedencia y evidencia inmutable

- **T009 primera ejecución real:** [informe original cargado por usuario, copiado byte-exacto](T009_RESULTADO.md), SHA Git **`fab47ada673b6c3867fedcc5327cfeaada07c7b1`**, correspondiente al checkout `8a761cf3081b7d09dae6cacb9f58fa58192863e4`. Linux Alpine 3.24.3 bajo QEMU 11.1.0, Python 3.14.10, pytest 9.0.3, Node 24.22.1.
- Resultado informado y archivado: Python **757 PASS, 1 FAIL, 28 subtests PASS, 0 SKIP**; Node **127 PASS**; checker Atlas `exit 1`, **SyntaxError line 24**; tests Atlas `exit 2` (error de colección); **SHA canónico UNKNOWN**. **No es una ejecución exitosa de HEAD actual.**
- Los archivos de evidencia y manifiesto de hashes originales `tareas_codex/T009_EVIDENCIA_8a761cf/` siguen **solo en el equipo local del usuario**: `C:/Programación/AB/proyectos/politics-fantasy-league/tareas_codex/T009_EVIDENCIA_8a761cf/`. Si Codex tiene acceso real, verificar hashes informados en T009 y copiarlos a un commit preservando bytes y nombres, **sin reescribir logs**. Si no tiene acceso, registrar **EVIDENCIA_LOCAL_NO_ACCESIBLE**, no inventar archivos ni calcular hashes ficticios.
- El `main` remoto avanzó después de la ejecución de `8a761cf` a `e706fa59...` **solo** mediante un protocolo UX; a posteriori se incorporó el informe T009. No atribuir a esos commits las pruebas anteriores.

## Diagnóstico de dos defectos en el commit T009

### D1 · Atlas roto por corrupción de código en C01 (P0)

El archivo `ab_atlas/atlas_delta.py` del commit `8a761cf` tiene Git blob **`8af1c74784c5f60892a038c026990619d1c95a85`**: **622 líneas** frente a **218** en el original íntegro y ejecutable, blob **`b47fc8e58b722b5b92830e91514cca253074bb90`**, recuperable del commit `e3c25259765d6a71b20d41a07db0d7a7794ccdec`. Problemas observados al leer GitHub:
- Línea 24: `ID_RE = re.compile(r'^[A-Za-z0-9_./:-]{1,100}` **sin** cierre de cadena/regex.
- El archivo contiene **tres definiciones de `batch_check` y tres de `cli`**, código triplicado, cierres sueltos en torno a las líneas 217 y 415 y otras regex incompletas; **no** basta con añadir una comilla en la línea 24.
- La última definición de `batch_check` vuelve a usar la antigua comprobación de cadena no vacía, incluso si se resolviera el `SyntaxError`, y por tanto sobreescribiría la validación de fechas. Esto contradice la reclamación previa de C01 de que la reparación estaba integrada correctamente. **Dejar esta errata explicitada**, sin borrar el historial C01 ni falsificar los resultados.

**Reparación mínima exigida:** partir de la versión **única y completa** del blob histórico `b47fc8e...`, no de segmentos del archivo concatenado; introducir **una única** función `valid_batch_timestamp(value)` compatible con ISO-8601 con zona explícita, `Z` o `±HH:MM`, día/hora reales, `datetime.fromisoformat`, y **una única** llamada en `batch_check`. Mantener `ID_RE` completo y `cli` una sola vez; no mover ni cambiar reglas de operación, hashes de estado, política de fechas ni archivos históricos de lote. Rechazar `not-a-timestamp`, fecha sin hora, timestamp ingenuo, 31 de febrero y offset imposible; aceptar dos timestamps con zona. Conservar el hecho documentado de que los lotes históricos `0015` y `0016` tienen una inversión temporal de 1534 segundos: **no imponer monotonía temporal**, solo formato válido. El fichero de regresiones `ab_atlas/tests/test_delta_timestamps.py` ya existe; ejecutarlo (y si hace falta adaptarlo claramente, sin relajar las condiciones por conveniencia).

### D2 · Test HTTP envía un cuerpo JSON Unicode sin bytes UTF-8 (P1)

En `proyectos/politics-fantasy-league/tests/test_http_duplicate_json_keys.py`, el control positivo `{"name":"Club Único"}` se pasa a `http.client.HTTPConnection.request(..., body=payload)` como **cadena `str`**. La librería codifica ese cuerpo en Latin-1, mientras que el servidor `json.loads(bytes)` exige JSON con codificación UTF válida. T009 observó **400** frente al 200 esperado en línea 31. La hipótesis de causa es plausible y coherente con los bytes **`da`** (Latin-1) frente a **`c3 9a`** (UTF-8), pero **no se confirmó con una segunda ejecución del test**. No presentarla retroactivamente como verificada.

**Reparación preferida:** en el helper del test, enviar `body=payload.encode('utf-8')` con `Content-Type: application/json`, y dejar que `http.client` calcule `Content-Length` sobre bytes. El endpoint **no** debe flexibilizarse para aceptar JSON Latin-1 no conforme. Mantener ambos casos negativos (duplicados a nivel superior y anidados, `400 BAD_REQUEST`) y el positivo `Club Único` (`200`). No cambiar la expectativa `200` a `400` para hacer verde.

## Orden de trabajo y criterios de aceptación

1. Leer `AGENTS.md`, [informe T009 original](T009_RESULTADO.md), [contrato T009 histórico](T009_MAIN_LINUX_ATLAS60.md), [estado Atlas](../ab_atlas/CURRENT.md) y [cierre MAIN20B](../research/ABH_MAIN20B_20261028/FINAL_REPORT.md). Verificar `git status --short`, `git rev-parse HEAD` y `git fetch` real antes de trabajar. **No asumir** que `main` sigue en `8a761cf`; desarrollar en una rama nueva `fix/pfl-t010-atlas-http-20261028` basada en el HEAD más reciente de `main`. No fusionar automáticamente.
2. Guardar las evidencias históricas originales, sin cambios. Intentar incorporar `T009_EVIDENCIA_8a761cf/` desde el equipo local **solo si existe y los hashes originales coinciden**; si no existe, registrar limitación. No usar como datos de entrenamiento o difundir cualquier original nominal privado.
3. **Antes de editar producción**, ejecutar y registrar la reproducción focalizada en el checkout actual: `python -m py_compile ab_atlas/atlas_delta.py` (debe fallar en el viejo archivo), prueba HTTP exacta (control positivo original debe fallar) y pruebas de fechas de Atlas (errores de colección). Guardar primer stderr y exit, no ocultar el fallo.
4. Reparar D1 con **diff mínimo controlado respecto de la base histórica de 218 líneas + validador nuevo**. Verificar número de funciones: `batch_check` una vez; `cli` una vez; `valid_batch_timestamp` una vez; sin `SyntaxError`. Ejecución focalizada de `ab_atlas/tests/test_delta_timestamps.py` y los tests del propio Atlas, con registros.
5. Reparar D2 en el **test** con codificación UTF-8 y ejecutar `tests/test_http_duplicate_json_keys.py` completo. Confirmar con pruebas instrumentadas que se transmiten bytes UTF-8, se aceptan nombres con tilde y se siguen rechazando claves JSON duplicadas. Si el fallo persiste, revisar la traza y registrar el nuevo diagnóstico, **no cambiar expectativas para forzar PASS**.
6. Ejecutar el **checker canónico real** contra `ab_atlas/seed.json` y todos los lotes vigentes del `main` de la nueva rama. A fecha del encargo son **75 lotes**, pero usar el total real del checkout. Conservar stdout/stderr/exit y calcular **SHA256 del estado canónico**; comparar nodos, relaciones, runs, incidencias y operaciones con el Atlas documental, sin asumir igualdad si hay errores. Cualquier fallo de schema/parent/referencia debe quedar registrado sin reescribir lotes previos.
7. Revalidar en Linux/POSIX limpio la **suite Python completa**, `ab_atlas/tests/` y **todos los tests Node** (en T009 fueron 127 PASS). Registrar el primer resultado de la rama corregida y todas las dependencias/entorno, sin CI costosa, ni despliegue o scoring real. Si falla una comprobación nueva, clasificar causa, alcance y necesidad de reparación antes de afirmar completitud.
8. Entregar `tareas_codex/T010_RESULTADO.md` con commit exacto, diff de ficheros, fallos iniciales y resultados posteriores, comandos, exit, recuentos, SHA256 de logs y estado canónico, **más enlace a rama/PR**, o bloqueo específico. Incluir una nota breve en `ab_atlas/CURRENT.md` y actualizar el backlog **solo en la rama de trabajo**. No borrar/editar el T009 original y **no** marcar su resultado histórico como aprobado. Revisión humana antes de fusionar a `main`.

## Condiciones de salida

- `SUCCESS`: ambos defectos corregidos en la rama; compila el Atlas con un único motor, tests de timestamps/HTTP PASS, replay completo de lotes PASS con SHA canónico, suite Python integral y Node PASS. Es **QA técnico**, no sube CT2/VSDS/V4/N1-N3 ni gates.
- `PARTIAL/FAILED`: al menos un requisito falla; preservar primer stderr, pruebas y bloqueo; no declarar éxito global.
- `BLOCKED`: sin checkout, entorno o evidencia necesaria; informar exactamente qué falta sin simular ejecución.

**R5 / autorización:** ninguna parte de este encargo consume ni crea ciclos AB-H. No autoriza modificar fuentes de personas reales, resolver derechos de reutilización por inferencia, aprobar gates ni arrancar CI de pago. Los resultados son auditables, no cambios de autorización.
