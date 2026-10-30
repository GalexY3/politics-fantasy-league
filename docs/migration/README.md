# Extracción de Politics Fantasy desde AB · 30/10/2026

## Fuente y alcance

- Fuente: `GalexY3/Metodologia-AB`, commit `69ed402dd4a3f25207d9e620ede568b5e92ad8af`.
- Destino: `GalexY3/politics-fantasy-league`, antes repositorio vacío `polictics_fantasy_league`.
- Se extrae `proyectos/politics-fantasy-league/` a la raíz y el motor `ab_atlas/` a `tools/ab_atlas/`.
- Se filtra la historia canónica con git-filter-repo 2.47.0, sin incorporar archivos de otros proyectos ni crear una segunda rama activa por cada campaña.
- Antes de adaptar rutas se verificó **identidad exacta de blob Git y modo de 2.743 archivos**. [Inventario de origen](SOURCE_TREE.json).

## Identificadores históricos

[COMMIT_MAP.tsv](COMMIT_MAP.tsv) es el mapa original→extraído generado por git-filter-repo. Filtrar una historia cambia sus SHA; no se afirma que los commit IDs sean idénticos. Los contenidos originales, preregistros y resultados conservan sus bytes y referencias a la fuente original.

Los verificadores de hitos resuelven SHA históricos mediante ese mapa. La existencia de un commit y un recibo no sustituye la evaluación sustantiva del hallazgo. Las ramas alternativas antiguas siguen disponibles en AB y se documentan en [el inventario fuente](SOURCE_BRANCHES.json); no se reactivan automáticamente en el repositorio nuevo.

## Adaptaciones operativas

La raíz del proyecto pasa a ser la del repositorio. Se adaptan catálogo, briefing, importación del motor Atlas y su prueba de compatibilidad; la app, las reglas y las evidencias no se reescriben por una mudanza. Se regenera la navegación y se fija la metodología mediante enlaces a una revisión concreta de AB.

Los documentos operativos apuntan al repositorio nuevo. Los informes históricos y recibos se conservan como fuentes fechadas; sus enlaces originales no se sustituyen a ciegas. Los puntos de entrada de AB se convirtieron en redirecciones después de publicar y verificar este destino.

## Verificación y corte

QA íntegro sobre `3d66e813a422572b2a2ce7a3155df8dac667e224`: **822 Python +32 subtests, 511 Node y 38 Atlas +104 subtests PASS**, cero fallos/skips. Instalación desde `.[test]`, catálogo, continuidad, logros y replay PASS. [Resultados y hashes](linux/MANIFEST.json), [comandos](check.sh), [preparación Linux](bootstrap.sh), [adaptación de código/configuración](PORT_CODE.patch). Linux Alpine 3.24, Python 3.14 y Node 24; UID sin privilegios, red externa desactivada durante pruebas. La instalación genera `build/` y `*.egg-info/` en el entorno efímero; no cambia archivos versionados.

**Corte completado y comprobado** en AB `385d6a21958cbe3bf18d7fd6f01d50538f6da2c5`, ramas `main` e `integration/pfl`. Doce entradas antiguas redirigen; el código activo y los workflows PFL ya no están allí. La etiqueta `pfl-monorepo-final-20261030` fija el snapshot previo. [Recibo de publicación y traslado de seguimiento](PUBLICATION_RECEIPT.json). Las copias locales principales `Metodologia-AB` y `PFL-unified` se actualizaron por fast-forward; los worktrees de investigación antiguos son históricos, sin reescritura. No se ejecutan nuevos ciclos AB por esta operación, ni se infieren concesiones de otros chats que no consten en el ledger migrado.

La CI remota queda manual. Datos raw/private/local_field no versionados y credenciales no forman parte de la extracción.

## Workflows del monorepo

Se conservan además los **16 workflows históricos de PFL** de la raíz de AB, con bytes y SHA-256, en [source_workflows/SOURCE.json](source_workflows/SOURCE.json). Son archivo inerte fuera de `.github`; sus rutas y contratos pertenecen al monorepo original. La única CI activa del destino es el workflow manual adaptado y completo. Sus historiales originales siguen consultables en AB; no se incluyeron estos paths de raíz en el filtrado de commits del proyecto.
