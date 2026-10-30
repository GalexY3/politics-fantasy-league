# Revisión de incorporación a main · 30/10/2026

**Revisor: Codex, por delegación expresa del investigador.** Esta revisión decide la incorporación del código y su organización a `main`; no certifica un lanzamiento público ni nueva evidencia sociológica. Codex participó en la integración, por lo que esta revisión no es una auditoría independiente.

## Alcance inspeccionado

- Diferencias de código ejecutable frente a `main`, integraciones PR44/45/75/79, semántica de conflictos resueltos y las pruebas asociadas.
- Motor Atlas comparado también con su última base íntegra histórica: se conserva el replay y sus reglas; el añadido funcional es el validador ISO con zona explícita. Se contrastan lotes y equivalencia de la importación CODEX20.
- Servidor local, persistencia y rutas del juego: se revisó que esta integración no introduzca exposición pública ni una falsa autenticación multiusuario. Se mantienen los límites de la demo y sus gates.
- Guardas de fuente, versiones y corte temporal; herramientas offline y hashes fijados; distinción de simulación, registro documental, observación externa y afirmación causal.
- Recibos sintéticos, versiones de reglas, validadores, runner de pruebas, estado vivo y organización. Los artefactos históricos se revisan por trazabilidad e inventario; no se reevalúa científicamente cada campaña.

## Hallazgos corregidos

1. **Fecha imposible firmable.** `fictional_receipt_auth.mjs` usaba `Date.parse` sin comprobar normalización; podía firmar 30 de febrero o 24:00 como si fueran instantes canónicos. Se conservó una regresión roja y se exige correspondencia ISO exacta. La fecha bisiesta válida sigue pasando.
2. **Versión de regla dependiente del orden.** Dos versiones de la misma regla/sala con igual instante de vigencia podían seleccionar una según el orden del array. Se rechaza `AMBIGUOUS_RULE_EPOCH` en ambos órdenes; las revisiones cronológicas existentes siguen válidas.
3. **Handoff con publicación fijada en texto.** Siempre decía «pendiente de revisión según GitHub» sin consultar GitHub. Ahora distingue la declaración del estado y la observación de una referencia Git local, que requiere fetch. No presenta esa referencia como una consulta remota en vivo.
4. **Metadatos de progreso insuficientemente comprobados.** Se añaden consistencia aritmética de presupuesto, existencia del commit de un hito DONE y dependencias conocidas/acíclicas. Estas comprobaciones no sustituyen la aceptación semántica del resultado.

Los negativos y regresiones están en `research/MAIN_REVIEW_20261030/`; son QA correctiva y no ciclos AB nuevos.

5. **Carrera de escritores del almacén privado.** La suite Linux de revisión detectó `UNSAFE_EXISTING_OBJECT` en un escritor concurrente: un peer instalaba un objeto válido después del primer open ENOENT pero antes del segundo stat, que volvía a lanzar el error anterior. Se elimina esa segunda consulta ambigua, se distingue la causa del open original y se verifica el inode ganador tras el enlace exclusivo. Se añade una regresión determinista para objeto válido, corrupto y symlink, sin relajar permisos ni O_NOFOLLOW. La primera suite negativa (816 PASS/1 FAIL, Node511 PASS) se conserva.

## Organización incorporada

- `PROJECT_MAP.md`: rutas por tarea y responsabilidad de carpetas.
- `PROJECT_INDEX.json`: catálogo de archivos versionados, con categorías y finalidad de las entradas clave.
- `research/INDEX.md`: navegación por series/preguntas históricas y sus informes/ledgers, sin inferir estado de ejecución por un nombre.
- `scripts/project_index.py build|check|find`: regeneración, detección de inventario obsoleto y búsqueda. El estado vivo comprueba también la frescura del catálogo.

Solo se indexan rutas versionadas; se excluyen raw/private/local_field. Las copias de módulos archivadas bajo evidencia no se presentan como código del producto. Se preservan rutas y bytes de los historiales. La organización futura se hace por responsabilidad y pregunta, en vez de añadir otro resumen duplicado en cada conversación.

## Criterio de decisión

La incorporación es aceptable si el árbol final tiene replay canónico, suites completas Linux, pruebas del catálogo/continuidad, integridad de evidencias y un diff delimitado al proyecto y sus instrucciones de gobernanza. Una carencia ya explícita y fuera del alcance de la demo (autenticación o fuente institucional pendiente) no se presentará como resuelta ni como bloqueo para incorporar mantenimiento correcto a main.

**Decisión actual: revisión completada; QA final del commit corregido en ejecución.** La resolución y el commit efectivamente incorporado se registrarán aquí después de observar los resultados y la operación GitHub. No se fusionará una cabeza que haya cambiado respecto a la revisada.
