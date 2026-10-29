# CODEX20 · Cierre de 20 ciclos autorizados

**20 ejecutados AB-P, 0 ciclos invalidados completos, 0 pendientes.** Hubo fallos y reparaciones de instrumentacion preservados; no se cuentan como ciclos adicionales. Bloque AB-H de producto/auditoria, no veinte experimentos cientificos independientes. CT2 de la linea prospectiva heredada 22 -> 22 ordinal, N1 nuevos 0, N2/N3 0; portfolio historico no auditado. No se atribuye a esta linea el CT2 de otras ramas.

## Resultados principales

- C01: versiones no implementadas v2/v999 recibian formulas v1; ahora rechazadas en score y manifest.
- C02: integrada la investigacion reciente sobre exposicion y publicacion sin sobrescribir la QA anterior.
- C03: fecha imposible de freeze normalizada por Date.parse; ahora calendario y hora se validan antes.
- C04-C06: procedencia, CLI y temporalidad verificadas por separado. Se corrigio el test dependiente del cwd y se anadio rechazo de symlink final con lstat; el control no promete eliminar carreras TOCTOU ni autenticar al publicador.
- C07-C11: replay nativo de oportunidad, salas, clusters y herramientas agregadas. Los resultados de retencion NO son efectos sobre outcomes. Son verificacion de implementaciones heredadas, sin nueva evidencia humana ni reivindicacion de novedad.
- C12-C16: README actual simplificado conservando historial, indice central de ocho fuentes, 30 enlaces comprobados, 67 artefactos con hashes correctos. De 139 archivos locales, 138 tienen hash registrado; el restante es una imagen derivada del PDF. Nuevo runner descubre 35 archivos Node en tests y src, excluyendo copias archivadas.
- C17: checkout limpio exacto `20e01950bc00044b546c7e7c658fab168232bb57`, Alpine/QEMU sin red externa durante tests, usuario no privilegiado: **799 Python +32 subtests; 314 Node, cero skips; Atlas38 +91 subtests**. Todas las salidas guest y hashes pasan. El host termino exit1 al imprimir Unicode DESPUES de recuperar/verificar el archivo; ese fallo se conserva, no se confunde con los exits0 de las pruebas.
- C18: ambos smoke Chromium HTTP y flujo jugable pasan con base aislada y fixtures ficticias.
- C19: V4 y registro de logros conservan bytes originales; ningun aumento de progreso, badge o gate.
- C20: Atlas **81 lotes, 63 nodos, 283 runs, 51 complaints**; SHA256 `ae363aff1be0bbe6e9f7873a7cbfd1c68c0db50d239f94987b7df120caac29c1`. Test Atlas posterior al delta: **38 +92 subtests PASS**. No se atribuye al ensayo Linux anterior el nuevo lote81.

## Lectura y limites

Cada Cxx_RESULT.json conserva A-J, controles, observacion y siguiente pregunta. LEDGER_COMMITS.json resuelve los compromisos de preregistro y resultados. Los ensayos con cambios aun sin commit lo indican en working_tree_status y hashes: code_commit identifica su base, no oculta esos cambios. Los errores de encoding Windows se preservaron con los primeros fallos. No se escribio en main ni se ejecuto CI costosa.

[Grafica CT2 completa y ampliada](CT2_FULL_AND_ZOOM.svg), [trayectoria](CT2_TRAJECTORY.json), [mapa navegable](GRAPH.html), [transferencia abstracta y falsadores](ABSTRACT_TRANSFER_NOTES.md). La abstraccion usada distingue formato, semantica, unidad, conocimiento y autenticidad; no constituye entrenamiento persistente del modelo ni un hallazgo metodologico independiente.

2/3: **NO ACREDITADO**. Los limites siguen siendo derechos por recurso, acceso a originales bloqueados, identidad real, diseno empirico y consentimiento/aprobacion pertinentes, ademas de auth multiusuario y despliegue. V4 36,90 %, gates0/6. R5 desaconseja repetir controles verdes como sustituto de una nueva clase de evidencia.

Siguiente direccion: resolver accesos/derechos originales y la procedencia temporal antes de disenar una prueba empirica identificable. SOLICITO CONTINUE 5 CICLOS centrados en esas dependencias, sin asumir autorizacion nueva.
