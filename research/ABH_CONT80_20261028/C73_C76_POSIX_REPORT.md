# Informe CONT80 C73-C76: validación POSIX de ingesta

28/10/2026. Cuatro ciclos AB-P ejecutados (C73-C76) dentro del presupuesto de veinte ciclos C61-C80. Balance total **16/20 ejecutados, cuatro sin usar; STOP_R5**.

Se verificaron los hashes Git exactos de siete módulos fuente y cuatro archivos de pruebas originales, y se ejecutaron en Linux Python 3.13.5 sin red ni datos de personas reales. Se conservaron salidas, códigos y hashes en [manifiesto](C73_C76_EVIDENCE_MANIFEST.json).

| Ciclo | Prueba original ejecutada | Resultado |
|---|---|---|
| C73 | test_ingest.py | 9 PASS, 2,11 s |
| C74 | test_ingest_redirect_security.py | 9 PASS, 14 subtests, 0,19 s |
| C75 | test_quarantine_ingest.py | 10 PASS, 0,12 s |
| C76 | test_ingest_full_local_e2e.py | 3 PASS, 0,08 s |

La ejecución conjunta de las cuatro suites dio **31 PASS, 14 subtests, cero fallos, exit 0, 2,30 s**. No hubo parches de producción. Los casos verifican captura sintética, redirecciones, permisos, SHA, cuarentena y auditoría CLI. El documento Senado con literal NO VOTAN en un test es ficticio y **no** certifica la semántica de fuentes institucionales.

**Límites:** no se ejecutó el pytest completo del repositorio ni el servidor HTTP original en C74; T007 tiene su propio registro de HTTP. No se infiere que todos los fallos Windows T002/T004 hayan desaparecido. No se certifican identidad, derechos de perfilado, primera publicación, caída eléctrica ni lanzamiento. Los seis gates siguen en 0/6, V4 36,90 %, CT2 ordinal 29/100 y VSDS 1/3.

Otra campaña incorporó lotes 0032 CR01 y 0033 CR02; no pertenecen a CONT80. El lote **0034**, padre 0033, contiene solo los cuatro run.add C73-C76. Recuento derivado tras ese lote: **34 lotes, 63 nodos, 81 aristas, 197 runs, 44 incidencias y 366 operaciones**. **El chequeo Python canónico de los 34 lotes no se ha ejecutado.**

Próxima tarea pendiente: [T008 suite completa Python en Linux POSIX](../../tareas_codex/T008_SUITE_COMPLETA_POSIX.md). Se detiene esta campaña bajo R5; quedan cuatro ciclos autorizados sin ejecutar. Ninguna tarea de Codex se ha ejecutado desde esta respuesta.
