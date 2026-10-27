# Politics Fantasy: contribuciones Codex, 27/10/2026

Esta campaña AB-H responde a la autorización abierta del usuario para contribuir en una rama propia. Parte de `8f75b73b720592f3651e2f65a0a44271b2ec2dbc`, tras BRANCHING20C, y es independiente de la campaña de 45 ciclos que ChatGPT ejecuta en paralelo. No se ha integrado en `main` ni en esa rama. La autorización no establece un cupo numérico; R5 sigue aplicándose cuando no hay evidencia discriminante o beneficio concreto.

| Ciclo | Resultado y alcance |
| --- | --- |
| CDX01 | Replay oficial Python del Atlas heredado: 11 lotes, 45 nodos, hash consignado en el resultado; se refiere a esta base, no a la rama paralela. |
| CDX02 | Integración selectiva de correcciones locales anteriores; pruebas de Python, Node y navegador registradas en el resultado. |
| CDX03 | Jornada sintética local: reloj, eventos ficticios, liquidación persistente e idempotente, puntuaciones congeladas y jornada siguiente. No utiliza datos políticos reales. |
| CDX04 | API y pantalla de la jornada; prueba de navegador con compra, alineación, vaciado, simulación y puntuación. No es despliegue ni prueba con usuarios reales. |
| CDX05 | XML de Senado: con categorías preregistradas coinciden 7 votaciones y 3 son indeterminadas. La correspondencia 10/10 requiere interpretar «NO VOTAN» mediante un mapeo posterior no certificado. Coherencia interna, no confirmación independiente de identidad ni disponibilidad. |
| CDX06 | El reconciliador deja de presentar como coincidencia individual completa la igualdad parcial cuando faltan nombres. |
| CDX07 | Hosts oficiales candidatos reconocidos sin levantar cuarentena; entradas de tipo inválido se rechazan. No autentica fuentes. |
| CDX08 | Extras de test e investigación corregidos; instalación limpia en Windows: 361 pruebas y 2 subtests. La primera ejecución falló en 7 pruebas por falta de tzdata y se conservó el negativo. |
| CDX09 | El ZIP de exportación excluye rutas locales y archivos privados conocidos y no copia metadatos históricos de publicación y pruebas. Suite posterior: 362 pruebas, 2 subtests y 1 omitida. |

El test de enlaces simbólicos de CDX09 quedó omitido porque esta cuenta Windows no permitió crearlos. Una lista de exclusiones no puede detectar secretos contenidos en archivos con nombres aparentemente normales. El extra de instalación base sigue sin incluir tzdata y no se han validado otras plataformas.

El Atlas de esta rama conserva el seed y añade el lote 0012 sobre 0011; `atlas_delta.py check` devuelve 12 lotes, 47 nodos y SHA-256 `5fdbea922fa403e53a97ef0a9b425049e45ebf934fa12a1f705307b23121a5bc`. El validador verifica consistencia estructural, no verdad de las fuentes. Antes de integrar con la rama de ChatGPT hay que reconciliar el `parent_batch`, los IDs de lote, los deltas y los cambios concurrentes: ambos parten de 0011 y no se deben concatenar a ciegas.

La CT2 ordinal de identidad permanece en **29/100** durante CDX01–CDX09; VSDS sigue en **1/3** y los gates acreditados en **0/6**. Las mejoras de producto no elevan esas medidas. El [gráfico CT2](CT2_CDX01_CDX09.png) muestra escala completa y ampliada; cada punto está respaldado por el campo `I` del resultado correspondiente.

Quedan abiertas, entre otras, la semántica oficial de «NO VOTAN», la prueba de enlaces simbólicos en un sistema que los permita, la disponibilidad temporal `first_public_at`, la adjudicación de homónimos y la validación externa. Los archivos locales de origen no se incluyen en Git.
