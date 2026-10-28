# Cola de tareas pendientes para Codex — Politics Fantasy League

**Estado actualizado por Codex el 28/10/2026:** se ejecutaron T001, T002, T003, T004 y T006. T002 y T004 conservan fallos por limitaciones y pruebas no completadas en Windows; T005 sigue bloqueada. Los informes y logs identifican resultados reales y límites. La ejecución de esta cola no equivale por sí sola a ciclos AB A–J. El histórico `research/CODEX_CONTRIB_20261027/` corresponde a otra etapa.

## Contexto y punto de partida

- Repositorio privado: `GalexY3/Metodologia-AB`.
- Rama de trabajo existente: `research/pfl-codex-contributions-20261027`. **No trabajar sobre `main`**.
- HEAD observado *antes de crear la carpeta*: `8f21411b0c4caf267d77721510d06129fe2eedbe`. **Al empezar**, Codex debe leer y registrar de nuevo el HEAD real, no presumir que este SHA sigue siendo el último.
- Autoridad: [AGENTS.md](../../../AGENTS.md), protocolo AB 3.2.1 O3–O7, [CURRENT](../ab_atlas/CURRENT.md) y [continuidad](../docs/CONTINUACION_INTEGRADA_CODEX_CHATGPT.md).
- Atlas en la base de esta ejecución `6e359a8`: **31 lotes**; replay canónico Python ejecutado con 63 nodos / 81 relaciones / 191 runs / 44 incidencias / 360 operaciones. Ver [resultado T001](T001_RESULTADO.md); comprobar el HEAD de nuevo porque ChatGPT trabaja en paralelo.
- Producto: V4 36,90 % contractual, CT2 identidad 29/100 ordinal, VSDS 1/3, gates de lanzamiento **0/6**. Nada de scoring político real.
- [Incidencia GitHub #17](https://github.com/GalexY3/Metodologia-AB/issues/17): índice público dentro del repo privado; **no es evidencia de ejecución**.

## Orden propuesto

| Prioridad | Expediente | Dependencia | Estado |
|---|---|---|---|
| P0 | [T001 — Replay canónico de Atlas](T001_RESULTADO.md) | Checkout íntegro y Python local | COMPLETADA_VERIFICADA |
| P0 | [T002 — Suites completas Python y Node](T002_RESULTADO.md) | Checkout íntegro | COMPLETADA_CON_FALLOS |
| P1 | [T003 — Paridad nativa V3/V4](T003_RESULTADO.md) | T002 o entorno local equivalente | COMPLETADA_VERIFICADA |
| P1 | [T004 — Seguridad del servidor local e ingesta](T004_RESULTADO.md) | T002 para baseline | COMPLETADA_CON_FALLOS |
| Bloqueada | [T005 — Originales institucionales y certificados](T005_ORIGINALES_CONDICIONALES.md) | Documento legítimo y permiso específico | BLOQUEADA; [matriz preliminar](T005_MATRIZ_PRELIMINAR.md) disponible |
| P1 | [T006 — Verificar migración XI/XII de códigos BOCCL y HTTP](T006_RESULTADO.md) | T002; checkout íntegro y tests HTTP | COMPLETADA_VERIFICADA |

[Índice de estado legible por herramientas](BACKLOG.json). Cada tarea tiene objetivo, comandos o procedimiento reproducible, criterios de aceptación y límites.

## Reglas para Codex

1. Antes de tocar código: comprobar HEAD, leer `AGENTS.md` y `CURRENT.md`, inspeccionar modificaciones locales (`git status --short`) y registrar herramientas/versiones.
2. Ejecutar **solo** la tarea seleccionada, con pruebas y evidencia de comandos reales: directorio de trabajo, stdout/stderr, exit code, hashes, archivos afectados y límites. Un comando planificado no se contabiliza como prueba.
3. Si hay fallos: conservar el resultado negativo, reparar únicamente un defecto reproducido, reejecutar controles y documentar. Cada ciclo AB requiere A–J y prerregistro cuando corresponda; **la cola no concede nuevos ciclos automáticamente**.
4. No activar GitHub Actions de alto coste, no fusionar a `main`, no subir originales nominales, tokens ni credenciales, no desactivar TLS, no exponer el servidor a Internet y no puntuar personas reales.
5. No convertir un PDF listado, metadato de licencia o fecha de actualización de catálogo en original firmado, certificación de identidad o `first_public_at`.
6. Guardar entregables en la **rama de investigación**, con ruta y commit verificable; en esta carpeta actualizar el estado de cada tarea solamente **después** de observar el resultado. La ejecución de Codex requerirá la acción explícita del usuario cuando tenga acceso.

**Convención de estados:** `PENDIENTE`, `EN_EJECUCION`, `BLOQUEADA`, `COMPLETADA_VERIFICADA`, `COMPLETADA_CON_FALLOS`. No marcar nada como completado por el mero hecho de redactar estas fichas.

**Revalidación posterior a C71 y C72:** [T007 — Atlas actual de 31 lotes y HTTP con enlaces BOCCL](T007_REVALIDACION_ATLAS30_HTTP.md). T001 y T006 constan ejecutadas en checkout anterior de 29 lotes; no extienden automáticamente su validación al HEAD actual.
