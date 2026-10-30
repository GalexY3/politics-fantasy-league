# ABH25-C02 · flujo HTTP completo con dos usuarios ficticios

**A–D:** [prerregistro](C02_PREREG_AJ.json) congelado en commit `bb3d1cca` y [test de integración](../../tests/test_abh25_p1p2_journey.py) congelado en `d8466ced` antes de la ejecución. Pregunta funcional: ¿pueden dos cuentas crear clubes, comprar, alinear y simular una jornada sin interferencia, conservando estado tras reiniciar? Rival H0: fallo de aislamiento, CSRF, selección o persistencia.

**E:** [GitHub Actions #41018524103](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41018524103), commit `ef92bad4`, Ubuntu, Python 3.14.9, código original del repo con **2/2 pruebas HTTP PASS** en 1,911 segundos; `compileall` y sintaxis `node --check` correctos.

**F–G:** clientes con cookies separadas; clubes, equipos y alineaciones ficticios; cross-account club 404 y CSRF ajeno 403; simulación solo de una cuenta, la otra conserva jornada pendiente; asentamiento repetido devuelve `already_settled`, reinicio del servidor preserva puntuación y sucesora. Control sin login: `/api/state` y `/api/simulate-round` devuelven 401 y no se abre base legada.

**Incidencia no ocultada:** `ResourceWarning` al limpiar excepciones `HTTPError` esperadas 404/403/401; aviso de higiene de test, no defecto de aislamiento demostrado, reparable sin nuevo ciclo.

**H–J:** un ciclo **AB-P limitado** de capacidad funcional ejecutada. No equivale a aceptación humana de P1, browser E2E, seguridad de internet, evidencia institucional ni lanzamiento. CT2 ciencia 20 ordinal, N1/2/3 cero, gates 0/6. [Recibo](C02_RUN_RECEIPT.json). No fusionar `main`.
