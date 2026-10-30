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

Los documentos operativos apuntan al repositorio nuevo. Los informes históricos y recibos se conservan como fuentes fechadas; sus enlaces originales no se sustituyen a ciegas. Los puntos de entrada del repositorio AB se convertirán en redirecciones solo después de publicar y verificar este destino.

## Verificación y corte

La migración todavía requiere QA íntegro sobre el commit adaptado, integridad del Atlas, catálogo, autorización y estado. Se registrarán sus resultados y el corte efectivo antes de retirar la copia activa de AB. No se ejecutan nuevos ciclos AB por esta operación, ni se infieren concesiones de otros chats que no consten en el ledger migrado.

La CI remota queda manual. Datos raw/private/local_field no versionados y credenciales no forman parte de la extracción.
