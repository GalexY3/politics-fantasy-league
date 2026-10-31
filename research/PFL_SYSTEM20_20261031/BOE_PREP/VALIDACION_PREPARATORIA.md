# BOE — validación sintética, fuente real bloqueada

**Fecha:** 2026-10-31. **Carácter:** preparación de software, cero ciclos AB-R o AB-P. No contiene datos del BOE ni resultados políticos.

## Instrumento y ejecución local

- Python estándar: `boe_capture.py`, SHA-256 local `33a6942e17029721b3f052dfd55cfddc0ec6e06aebdd6327b74b3840868e3cb4`.
- Prueba: `python -m unittest -q test_boe_capture.py` desde este directorio; **11/11 PASS**.
- Prueba adicional: `python boe_capture.py smoke` **EXIT 0** con fixture completamente ficticio.
- Fixture sintético de 862 bytes: SHA-256 `188dff922c83307797e279ee90a9d15db9762e3893c6e0bbad5cf5233ccca3e5`. El análisis produjo 2 IDs ficticios y 1 duplicado exacto. No son registros públicos observados.
- Los archivos de ejecución `runs/2026-10-30/receipt.json` y `coverage.json` se encuentran localmente en una carpeta ignorada por Git. Dejan `http_get_attempted=false`, `http_get_count=0`, `http_status=null`, `http_date=null`, `terms_accepted=false`, `real_html_downloaded=false`.
- El primer intento de lanzar `unittest -v` desde PowerShell se detuvo por tratamiento de su salida `stderr` como error nativo (`NativeCommandError`), **antes de terminar la suite**. No se ocultó ni se convirtió en resultado de test. La segunda ejecución con control de código de salida completó 11/11.

## Gate no superado

El [aviso legal de AEBOE](https://www.boe.es/informacion/aviso_legal/index.php) dispone condiciones de reutilización que pueden vincular al agente reutilizador desde el uso o descarga. **No se ha aceptado ninguna condición por cuenta del usuario.** La red está deshabilitada en el instrumento, y ni la accesibilidad real del documento ni su cobertura se han probado mediante este programa.

La fuente diaria contiene publicaciones (resultados documentales), no todas las propuestas, demandas ni oportunidades de decisión del sistema político. No puede usarse para inferir persistencia o eficacia institucional sin definir una población en riesgo desde otra fuente como el Congreso. Véase el borrador `../CONGRESO_AJ_DRAFT.md`, todavía no congelado ni ejecutado.

## Próximos criterios de apertura

Confirmar derechos y condiciones aplicables; verificar formato, IDs, fechas y cobertura de un original de manera lícita; fijar una muestra elegible y un contrato A–J con comparadores y código SHA remoto **antes** de observar outcomes. R5 impide contabilizar el presente instrumento como evidencia científica nueva.
