# T025 RELEASEPATH · QA nativa y reparación del snapshot de logros

**Alcance: rama `research/pfl-abh5-release-criticalpath-20261028`, base `853bd666190dca0fa2d200671bc009c9e079c95e`; código ensayado `6992eee108cec67b0a246a4f575e87daa8efd5ad`.** Existe otra T025 de mecanismos en ramas posteriores: son tareas distintas. El resultado siguiente no certifica las ramas divergentes ni `main`.

## Defecto y reparación

La primera suite Node en Windows dio 176 PASS y 1 FAIL: el JSON embebido del HTML de logros seguía en v3 mientras el registro canónico era v6. Se conservó la salida original y se fijó el [plan de reparación](T025_REPAIR_PLAN.md) antes de modificar el HTML. Se sincronizó exclusivamente el snapshot embebido y su documentación; el registro y V4 no se modificaron. La suite Node final pasó 177/177.

## Evidencia nativa del commit ensayado

| Control | Resultado |
| --- | --- |
| Linux Alpine 3.24.3 en QEMU, Python 3.14.10 | 784 pruebas y 28 subpruebas PASS; 0 omitidas |
| Atlas Linux | 38 pruebas y 86 subpruebas PASS; checker original 75 lotes, 63 nodos, SHA-256 `118e95d9f34fcace52e21a6b92e09eac7a62ffc92ae6c20ac62512bb7d9d9692`; replay PASS |
| Node Linux y Windows | 177/177 PASS en cada entorno |
| Registro de logros y guard | v6, 5/90; 9/9 pruebas guard PASS; CLI devuelve 3 esperado con release bloqueado 0/6 |
| Navegador Windows | Smoke y flujo jugable en Chromium PASS; HTTP muestra 5/90, y el fallback ante registro HTTP 503 también muestra 5/90 |

Linux ejecutó el checkout limpio con usuario no privilegiado, red externa desactivada y loopback activo. [Manifiesto, comandos y salidas Linux](T025_EVIDENCIA/linux/MANIFEST.json); [manifiesto y salidas Windows](T025_EVIDENCIA/windows/MANIFEST.json). Los logs preservan la primera ejecución fallida y la final. Playwright CLI impidió abrir `file:` por su política; no se afirma que se haya probado directamente ese protocolo. La consola recoge un 404 de favicon y el 503 provocado para probar fallback.

El guard usa un verificador de evidencia externo que por defecto devuelve falso; el `()=>true` de una prueba es simulado, no una implementación de confianza. No se abrieron gates, no se alteró V4 ni se ejecutaron ciclos AB. Esta QA demuestra comportamiento en el commit citado, no preparación para producción, identidad real ni validez científica. T011 y T024 tienen avances documentales parciales y no se declaran cerradas.

## Dependencias siguientes

1. Integrar y volver a validar el cambio únicamente en la línea correspondiente, revisando primero ramas más recientes para no sobrescribir evolución ajena.
2. Completar T011 y T024 bajo sus contratos de base, semántica y derechos; mantener datos originales fuera de Git.
3. Cerrar los seis gates con sus fuentes y evidencias independientes, incluida autorización humana cuando corresponda; no desbloquear el guard con un verificador ficticio.
