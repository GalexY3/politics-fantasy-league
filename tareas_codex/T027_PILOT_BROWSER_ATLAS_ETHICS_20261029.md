# T027 · PFL piloto local: checkout, browser, Atlas y ética (PENDIENTE)

**No cuenta como ciclo AB ejecutado.** Rama inicial `research/pfl-abh5-pilot-native-integration-20261029`; comprobar HEAD real antes de trabajar. No fusionar main, no ChatRelay, no CI costosa, no puntuar personas políticas reales, no habilitar captura de participantes.

## Trabajo verificado ya, no repetir como descubrimiento
- Los cinco módulos previos de PR35 se reconstruyeron por sus hashes Git exactos y se ejecutaron **84/84 asertos nativos Node v22.16.0** en entorno aislado. Después de endurecer tres validadores, los 84 siguen pasando. El script aislado original tiene hash Git `de4084d749518b7b426da1ee753d234870334287` antes de parches; no estaba integrado en el checkout privado y NO se da por persistido en GitHub.
- El piloto local `pilot_local/` tiene servidor loopback GET/HEAD, cuatro condiciones ilustrativas sin asignación real, cuatro ítems ficticios y sin clave o endpoint de respuestas. **15/15 checks HTTP nativos** ejecutados; `pilot_local/smoke_http.mjs` está versionado en GitHub.
- Cinco contraejemplos de herencia/`Symbol` encontrados en anteriores validadores y parcheados. El mock de revisión ética **sigue falsificable por diseño**, no apto para enrolamiento.
- Chromium headless intentado, pero ejecución produjo timeout y ningún DOM confirmatorio: **NO dar por aprobado E2E o accesibilidad de navegador**.

## Criterios de aceptación pendientes
1. En un checkout completo limpio de la rama, `node --check` y `node pilot_local/smoke_http.mjs`; ejecutar suites existentes y añadir tests Node nativos persistentes con pruebas equivalentes a las 84 de PR35 (registrar fixture y hash). Contrastar código con Git blob y documentar diferencias; la reproducción aislada NO demuestra CI/repositorio íntegro.
2. Verificar navegador real (preferentemente Chromium/Firefox) en 4 condiciones, móvil y teclado; tomar capturas sin datos personales, comprobar renderizado de campos X1–X4, reinicio local, CSP, ausencia de consola red y de claves en la respuesta. Actualizar recibo con PASS/FAIL/SKIP.
3. Revisar amenaza local: simbolos, propiedades heredadas, accessors, `Proxy`, prototipo extraño, `__proto__`, payloads grandes, solicitudes HEAD/GET, callback y recursos no declarados; determinar si se necesita endurecer más. Probar no filtración de clave ni respuestas, y sin persistencia.
4. Reproducir formalmente en Python/Node el lote Atlas 0078 y nuevo 0079. La `ab_atlas/CURRENT.md` canónica estaba **sin sincronizar** desde 0078 por bloqueo de actualización de fichero grande; resolver mediante herramienta Git segura o documentar imposibilidad. No transformar delta en estado canónico sin checker.
5. Solicitar orientación al [CEI USAL](https://investigacion.usal.es/es/comite-bioetica), en caso de que el estudio vaya a acogerse al ámbito USAL, y completar evaluación de privacidad aplicable (AEPD), protocolo de consentimiento y plan estadístico definitivo. El ejecutor **no** debe reclutar ni recolectar datos hasta aprobación externa documentada. Ningún `approval` mock valida esa autorización.
6. Guardar recibos con HEAD, Node/navegador/versiones, stdout/stderr, artefactos y SHA; registrar arreglos con errata y no reescribir resultados anteriores; comprobar que `main` no se ha tocado ni se han activado costes.

**Terminación segura:** si la revisión ética o browser no están disponibles, dejar `NEEDS_EXTERNAL_APPROVAL` / `BROWSER_NOT_RUN` y detener ese subtrabajo. No inventar un estudio sociológico.
