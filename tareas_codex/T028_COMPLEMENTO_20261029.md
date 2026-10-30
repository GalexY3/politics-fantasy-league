# T028 · Controles complementarios del navegador

El [núcleo técnico T028 ya estaba verificado](T028_RESULTADO.md) en la rama antecesora. Esta ejecución cubre controles adicionales de la ficha que no figuraban entre los 21 anteriores. No vuelve a atribuir al ensayo previo pruebas que no contenía.

Se ejecutó en Windows con Chromium 155 y Playwright CLI, sobre los archivos `pilot_local` extraídos exactamente del commit `7a6876f71b6cbc286f86ff4bf1393889e4f22851`. El tar de fuente tuvo SHA-256 `53f7658dc158ecc57218843219e558f5cbce3fdf3a8ef161d96964f1f6c63b24`. El servidor local se inició y cerró para la prueba, sin participantes ni información personal.

**11/11 controles PASS:** foco de selector, radio y reinicio mediante Tab; selección con Espacio y limpieza con Enter; carga de la hoja CSS; viewport de 375 px sin desbordamiento horizontal; `Referrer-Policy: no-referrer`; PUT y DELETE rechazados con 405; y generación de dos capturas. Se revisaron las [capturas de escritorio](T028_EVIDENCIA_COMPLEMENTARIA/desktop.png) y [móvil](T028_EVIDENCIA_COMPLEMENTARIA/mobile.png). [Resultados](T028_EVIDENCIA_COMPLEMENTARIA/supplement_result.json) y [transcripción](T028_EVIDENCIA_COMPLEMENTARIA/supplement_transcript.json).

El [script exacto ejecutado](T028_EVIDENCIA_COMPLEMENTARIA/t028_complement.py) es para Windows y requiere Node, `npx`, Playwright CLI y Chromium autorizado. Para repetirlo, copiarlo a la raíz de un checkout limpio del commit indicado y ejecutarlo allí: utiliza rutas relativas a esa raíz, puerto loopback 8787 y genera sus resultados y capturas en la raíz. Este control no acredita conformidad WCAG completa, ensayo con personas ni preparación de lanzamiento. No consume ciclos AB ni abre gates.
