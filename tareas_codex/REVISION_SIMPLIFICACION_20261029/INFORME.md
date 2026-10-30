# Revisión de simplificación

Se concentra la cola vigente en una tabla desde BACKLOG y se archivan sus cabeceras históricas sin borrar evidencia. Se corrigen conversión implícita de rule_version y arrays que esconden eventos mediante iteradores o getters. Tres regresiones nuevas fallan antes y la suite completa pasa 307/307 después.

PR45 es la propuesta de integración del trabajo reciente. PR44 sigue separada: su registro v6 no sustituye el v3 de este linaje sin revisar los logros y su trazabilidad. No fusionar los estados CURRENT de Atlas75 sobre Atlas80. La rama RCT solo añade metadatos y un workflow manual; puede incorporarse conservando los commits GJP posteriores. Main permanece pendiente de revisión e integración global.
