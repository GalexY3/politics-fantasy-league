# Politics Fantasy: empezar o continuar

Este enlace es estable. **El estado se consulta en Git; no se copia de una conversación anterior.** Esta entrada sirve para ChatGPT, Codex y cualquier colaborador con acceso al repositorio.

**Para localizar cualquier pieza:** [mapa por tareas](PROJECT_MAP.md), [catálogo buscable](PROJECT_INDEX.json) e [índice de investigación](research/INDEX.md). No hace falta leer todos los informes para encontrar una ruta.

## Recuperación breve obligatoria

1. Leer este archivo, [AGENTS.md](AGENTS.md) y [PROJECT_STATE.json](PROJECT_STATE.json).
2. Resolver el HEAD remoto de la rama de integración indicada en `PROJECT_STATE.json`. Si tienes terminal: `git fetch origin` y comprobar rama, HEAD y cambios locales. Si tienes conector: leer la rama y sus archivos actuales, no confiar en resultados de búsquedas sobre la rama por defecto.
3. Ejecutar, cuando sea posible, `python scripts/project_status.py brief` y `python scripts/project_status.py check` desde este proyecto. El briefing deriva contadores del Atlas y saldo del ledger. Sin ejecución, declarar qué datos solo se leyeron y qué no se pudo verificar.
4. Informar en pocas líneas: rama/commit reales, hito activo de producto, hito activo de investigación, última prueba relevante y acción siguiente. Leer solo las fuentes de esos hitos; el resto del historial es archivo consultable.
5. Antes de editar, confirmar que nadie avanzó la rama estable. Una diferencia exige reconciliar, nunca sobrescribir ni inventar que ya se integró.

## Autoridad y ramas

- **`integration/pfl` es el punto de reunión operativo y la referencia estable de continuidad.** La base reunida se incorporó a `main` mediante [PR80](https://github.com/GalexY3/Metodologia-AB/pull/80), después de revisión y QA. Cada cambio posterior debe comprobar su propia incorporación; consultar `PROJECT_STATE.json` y Git.
- `main` es la rama de publicación/integración final. Su estado real se consulta en GitHub; no se presume actualizado.
- [Inventario de ramas](BRANCHES.json): indica qué cabezas se integraron y qué alternativas antiguas quedan archivadas para revisión. Una PR abierta de un ancestro no implica trabajo faltante.
- Para trabajo corto, una rama de cambio por hito, basada en `integration/pfl`, y una PR contra esa misma rama. **Una conversación o un ciclo AB no necesita su propia rama Git.** La rama conceptual de una hipótesis se identifica dentro del ledger.
- Mantener `integration/pfl` accesible incluso después de fusionar a `main`, o actualizar primero el enlace estable y los consumidores. No borrar ramas ni cerrar PR históricas automáticamente.

## Dos objetivos, dos evaluaciones

**Producto:** capacidad utilizable de principio a fin, con aceptación y regresiones. Próximo tramo: acceso multiusuario al prototipo ficticio y aislamiento entre cuentas. Originales políticos no son dependencia de ese tramo.

**Investigación:** preguntas sociales o institucionales, alternativas competentes, evidencia externa y límites de identificación. Un test de software o una réplica del mismo simulador no acredita una respuesta sociológica nueva. El siguiente trabajo se decide por la información que falta y la accesibilidad real de la evidencia.

Los hitos, su estado y su siguiente prueba están en `PROJECT_STATE.json`. Los porcentajes y CT2 históricos conservan su propio contrato; no se usa una cifra única para sumar producto, ciencia, medallas y ciclos.

## Regla de progreso adoptada para este proyecto

La solicitud del investigador del 30/10/2026 prioriza unificación, continuidad y progreso sustantivo. Para PFL **no es obligatorio pedir más ciclos al terminar cada informe**. Se conserva el núcleo AB y R5; [la política de trabajo](docs/WORKING_AGREEMENT.md) concreta este piloto. Su eficacia todavía no está demostrada.

Antes de continuar una línea estancada, proponer tres acciones materialmente distintas: cerrar una dependencia, probar otro mecanismo/población/fuente o entregar una capacidad de producto. Elegir por resultado verificable y coste, no por facilidad de generar más pruebas. Una fuente inaccesible se aparca hasta que cambie una condición concreta.

## Cierre de cada sesión

Actualizar `PROJECT_STATE.json` con avances observados, evidencia y próxima acción. Conservar los saldos en sus ledgers originales. Preparar los archivos previstos en Git; si cambió el inventario, ejecutar `python scripts/project_index.py build`. Ejecutar `python scripts/project_status.py check`, actualizar [HANDOFF.md](HANDOFF.md) con `python scripts/project_status.py handoff` y guardar los cambios en Git. El verificador también rechaza un catálogo desactualizado. Si falta acceso de escritura, entregar un parche/estado propuesto y declararlo **NO GUARDADO**; no afirmar sincronización.

La siguiente conversación vuelve a leer esta entrada y el estado actual. **El prompt reutilizable solo contiene este enlace y la instrucción de comprobarlo.**
