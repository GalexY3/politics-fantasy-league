# Informe final: PFL-BR30B, 30 ciclos con branching

Fecha de corte: 2026-10-25. Bloque **nuevo de 30 ciclos autorizado** tras la solicitud «SOLICITO BRANCHING 30 CICLOS»; no consume los saldos heredados PF-B50 (12), PF-F45 (45) ni PF-AB20 (19). Alcance: ingeniería reproducible, herramientas de sociología cuantitativa y producto local. Estado: **30/30 contratos de producción ejecutados en suite local**, **0 experimentos empíricos de predicción política validados**. No se afirma que las 30 pruebas sean independientes científica o estadísticamente.

## Resultados

1. A, B30B-01–06: adaptación a dos tablas CSV documentadas, vocabulario español cerrado, IDs históricos sin pérdida de ceros iniciales, validación de duplicados, SHA-256 de fuente. 6 tests nuevos.
2. B, B30B-07–12: conciliación por voto entre registros nominales y conteos agregados, separando *match* de filtrado/incompleto, conflicto, falta de agregado y cambios de instantánea. 6 tests nuevos.
3. C, B30B-13–18: límite temporal según fecha de descarga efectiva, requisito de zonas horarias, alerta de capacidad, puerta de certificación externa, clustering por sesión y temas no oficiales. 6 tests nuevos.
4. D, B30B-19–24: comando local offline que exporta auditorías JSON agregadas, deterministas, hashadas y minimizadas; guardado exclusivo atómico. 6 tests nuevos.
5. E, B30B-25–30: `GET /api/field` de solo lectura para recibos validados, rechazo de informes alterados, ninguna fila nominal difundida, integración en panel de observatorio y conservación de juego sintético separado. 6 tests nuevos.

Total **117 pruebas superadas** (87 anteriores y 30 nuevas). `node --check` también superado. Benchmark independiente (no uno de los 30 ciclos): 70.000 registros nominales completamente sintéticos procesados en 0,3599 segundos en la ejecución local. Es rendimiento de parseo en este equipo, no garantía de throughput ni análisis político.

### Evidencia que NO existe

Descarga real de los CSV, cotejo nominal independiente con JSON oficial, roster temporal, primera publicación de cada observación, cortes train/test en archivos políticos, modelo predictivo empírico, validación causal, usuario externo y validación visual cross-browser. Intento de navegador de prueba con Chromium bloqueado por política de red del entorno (`ERR_BLOCKED_BY_ADMINISTRATOR`); se mantiene como déficit de QA. La batería de pruebas cubre contratos concretos, no una certificación de seguridad.

### Adaptatividad y método

El diseño general se registró antes de ejecutar (GitHub commit `23d66bc5...`). Lote E se congeló antes de implementación (commit `d284d710...`); lotes B–D se concretaron durante el trabajo y no fueron congelados individualmente con commits pre-run. **La ejecución de código no precedió a una congelación completa de código GitHub**, por lo que el programa es ingeniería exploratoria, no confirmación empírica prerregistrada bajo AB O2/O3. El ledger adjunto describe A–J en cada uno de 30 incrementos. Los ensayos rechazaron opciones imposibles; no se crearon votos reales ficticios atribuidos a políticos.

La documentación de [Congreso Abierto](https://congresoabierto.org/datos/) expone campos CSV y licencia CC BY 4.0, y su [metodología](https://congresoabierto.org/metodologia/) explica casos omitidos y temas derivados del título. El [Congreso](https://www.congreso.es/es/opendata/votaciones) mantiene enlaces institucionales oficiales. Ni esa documentación ni nuestros tests prueban haber obtenido un corpus nominal íntegro. El entorno local carece de resolución DNS para descargas exteriores.

### VSDS, CT2, contabilidad

Valor VSDS del proyecto **1/3**, sin incremento por cantidad de tests. AB original de novedad científica **0/3**; N1=0, N2=0, N3=0. CT2 individual predictivo = **24/100** sin actualización, por no existir información contrastiva nueva. Se preservan en `CT2_full.png` y `CT2_zoom.png` gráficas sin aumentos artificiales. Estructura de score por persona real sigue no autorizada. Se conservaron 12 ciclos PF-B50, 45 PF-F45, 19 PF-AB20, y el bloque nuevo B30B queda en 0 tras ejecutar 30 contratos de producción.

### Dictamen AB-DECIDE

**CONTINUE PRODUCT + REPAIR FIELD ACCESS**. La limitación decisiva no es computacional sino disponer de archivos longitudinales verificables con recuentos oficiales, grupos fechados, censos y momento de disponibilidad. Una vez obtenidos, priorizar auditoría por muestreo aleatorio, estimandos con denominador y análisis descriptivos comparativos (por agenda y temporalidad) antes de pronósticos. No publicar datos crudos ni rankings normativos de diputados.

## Solicitud excepcional al investigador

Recomiendo reservar la siguiente fase para trabajo de campo computacional e instrumentación en producción. Una autorización nueva sería distinta de los bloques ya abiertos; no debe consumirse por planificación repetitiva. Se solicita **BRANCHING 30 ciclos** para recopilar corpus nominal verificado, cotejarlo, evaluar comparadores temporales y profundizar producto, si el cuello de botella de acceso se resuelve. La solicitud no es ejecución automática.

SOLICITO BRANCHING 30 CICLOS
