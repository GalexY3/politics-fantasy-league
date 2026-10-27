# Politics Fantasy League — Cierre de 20 ciclos AB-H de ingesta IC04–IC23

**27 de octubre de 2026.** Única rama: `research/pfl-codex-contributions-20261027`. Campañas independientes, no sumables: **ChatGPT AB-H45 cerrado (45)**, **Codex CDX01–CDX09 (9)**, **ChatGPT IC01–IC03 cerrados (3)** y **esta continuación IC04–IC23 (20)**. No se creó otra rama, no se fusionó a `main`, no se publicaron originales privados.

## Resultado

Se ha obtenido **un flujo operativo local verificable**: importador por HTTPS con validación previa de cada redirección y editor, almacén SHA con confinamiento POSIX y permisos privados, validadores de fuente específicos, cuarentena que nunca autoriza puntuación política real, auditoría de lectura y herramienta de consola que devuelve solo contadores y un código de error.

No se ha obtenido **un flujo HTTP de ingesta en el servidor**, una fuente de publicación histórica certificada, identidad longitudinal independiente, uso jurídico autorizado de registros personales ni un producto desplegable. Los tres primeros campos no deben deducirse de la coincidencia de SHA. `NO VOTAN` sigue siendo **etiqueta operativa de XML**, pendiente de documentación institucional sobre su semántica.

## Evidencias por ciclo

| Ciclo | Aportación observada, corregida o delimitada |
|---|---|
| IC04 | Bloqueados enlaces simbólicos en objetos SHA y manifiestos mediante descriptores POSIX, `O_NOFOLLOW`, contenido enlazado por hash; tests de concurrencia y ataque ficticio |
| IC05 | Ledger `quarantine_reviews.jsonl` también protegido contra enlaces simbólicos |
| IC06 | Comprobaciones de rutas locales y permisos antes de efectuar una solicitud HTTPS ficticia |
| IC07 | Rechazadas respuestas HTTP cuya longitud declarada no corresponde con los bytes recibidos; sin atribuir autenticidad editorial |
| IC08 | Bloqueados permisos inseguros de directorios/objetos y propietario distinto; no alterar silenciosamente ficheros existentes |
| IC09 | Documentado rechazo explícito del importador seguro en Windows nativo; demo sintética Windows intacta; Linux/WSL2 sujeto a instalación y permisos |
| IC10 | Limpieza de temporales cuando falla una escritura parcial en Python; **no** garantiza recuperación tras corte de energía |
| IC11 | Auditor privado que compara SHA y emite únicamente contadores, no URLs ni nombres |
| IC12 | Auditor deja de crear carpetas SHA inexistentes durante lectura |
| IC13 | `capture_id` opaco distinto del SHA; identifica una **operación**, nunca una persona |
| IC14 | Emparejamiento manifiesto/revisión por `capture_id`; huérfanas, duplicadas y legado sin IDs quedan visibles |
| IC15 | Auditor rechaza raíz inexistente sin crearla |
| IC16 | Dos manifestaciones con igual `capture_id` cuentan como dos operaciones inciertas, no una conciliada |
| IC17 | Auditor verifica además el tamaño declarado en el manifiesto; legado sin campo marcado como incompleto |
| IC18 | Nueva CLI local agregada con salida JSON, `0` solo para capturas íntegramente revisadas (aunque su esquema sea rechazado), `2` para anomalías. `0` **no** es permiso de publicación |
| IC19 | Tres E2E ficticios en Python: formato correcto, formato incorrecto y dos capturas idénticas con una revisión pendiente |
| IC20 | Rechazo de línea final JSONL sin terminador, aun cuando su JSON sea sintácticamente válido |
| IC21 | Python ingesta/seguridad/auditoría **67 passed + 14 subtests**, JavaScript **110 passed**; **la suite Python completa agotó 120 s al ~58 % sin errores visibles**. CI opcional incluye tests nuevos, pero **no se ejecutó Actions** |
| IC22 | Cadena Atlas existente verificada con Python oficial en checkout local (19 lotes, 60 nodos); el lote 0019 se reconstruyó para ese control local con operaciones equivalentes, **no** bytes idénticos. No citar su SHA local como estado canónico GitHub |
| IC23 | Cierre de prerregistros y resultados, delta 0020, actualización `CURRENT.md` y documentación. Validación de cadena final separada, con limitaciones explícitas |

El trabajo incorpora varios tests negativos que se observaron en estado **rojo antes de la reparación** (escape del almacén, respuesta incompleta, contador por captura duplicada, auditor que creaba directorios, JSONL sin salto final). Esto avala los defectos específicos, no una superficie de ataque remota. El importador sigue local y no se ha conectado al HTTP público.

## Reproducción, compatibilidad y seguridad

El checkout procede del ZIP del commit anterior `4faf31a`, sobre el que se reconstruyeron y probaron los cambios de esta campaña. La verificación de los archivos de código se contrastó en varios pasos con sus SHA de blob en GitHub. Existen diferencias menores en algunos archivos de test locales frente a los contenidos finales de GitHub; no afirmar que el **árbol entero** se ha descargado de nuevo de forma byte-idéntica.

El sistema POSIX exige propietario y permisos privados. **Windows nativo no está soportado por el importador endurecido** y falla de modo deliberado; el juego/demo Windows sigue siendo independiente. Cualquier futuro backend Win32 requeriría desarrollo y tests en Windows real. No se ha probado la supervivencia ante caída total del proceso o del sistema ni la atomicidad transaccional entre objeto y manifest/review.

Los 67 tests Python de la línea modificada y los 110 tests JS pasaron; el conjunto Python completo **no** se considera verde porque agotó el tiempo. El workflow opcional está actualizado para CI, sin ejecutar CI en esta campaña. La prueba visual Chromium anteriormente fue bloqueada por restricciones del entorno, no se ha reclasificado.

### Pendientes con prioridad

**P1:** ejecución completa de pytest y revisión del flujo en checkout de la rama actual; recuperación ante fallos de durabilidad de disco, comprobaciones de carreras/ruta raíz y seguridad del sistema operativo.

**P2:** diseño de operador de ingesta autenticado, aislado de internet público, con política de egress, permisos y auditoría; actualmente no hay `POST /api/ingest` ni ruta de cuarentena HTTP.

**P3:** recibos históricos de publicación y reutilización de fuentes originales, inscripción RPP original por entidad, identidad longitudinal adversarial (incluido homónimo negativo). No asignar puntuaciones a personas reales.

**P4:** evidencia institucional sobre `NO VOTAN`. La correspondencia de etiqueta XML con significado político/jurídico no queda acreditada por el parser ni por este trabajo.

## Estado y método

**V4 36,90 %**, **CT2 29/100**, **VSDS 1/3**, **N1/N2/N3 nuevos 0/0/0**, **gates 0/6**. El trabajo sobre parsers y pruebas no cambia esos valores por sí mismo. No hay métrica de éxito confirmatorio novedoso.

**R5:** la línea de variaciones de un mismo XML o de un mismo error de almacenamiento se detuvo cuando dejó de aportar hipótesis discriminantes. Se consumieron los veinte ciclos autorizados exclusivamente como presupuesto y se documentaron las limitaciones. Siguiente bloque requiere nueva autorización; el usuario ha indicado preferencia por solicitudes de **5 a 15 ciclos**.
