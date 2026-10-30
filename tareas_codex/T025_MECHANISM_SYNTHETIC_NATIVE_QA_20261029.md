# T025 — Reproducción nativa y auditoría adversarial de mecanismos sintéticos PFL (PENDIENTE)

**Estado: NO EJECUTADA.** Esta ficha no concede nuevos ciclos ni autoriza cambios de producto público.

## Base y precauciones
Repositorio privado `GalexY3/Metodologia-AB`, rama `research/pfl-abh5-incentive-mechanisms-20261029`, campana `proyectos/politics-fantasy-league/research/ABH_INCENTIVE_MECHANISMS5_20261029`. No fusionar main, no activar CI de coste elevado, no usar ChatRelay, no leer/escribir ni puntuar actores políticos identificables. Solo datos `SYN-*` ficticios.

## Procedimiento de aceptación
1. Leer `AGENTS.md`, fuente PFL y el ledger `CAMPAIGN_STATUS.json`; comprobar HEAD actual en Git y registrar `git status`, `git rev-parse HEAD`, versiones Node/Python y hash SHA-256 de los módulos. No suponer el HEAD anotado aquí continúa actual.
2. Ejecutar con Node nativo `node --check src/politics_fantasy/synthetic_round_score.mjs` y `node --check src/politics_fantasy/synthetic_round_manifest.mjs` desde proyecto; importar ambos módulos en entorno ESM y reproducir **independientemente** todos los 18 asertos C03 y 18 C05 conservados en los JSON de resultados. No contar como ciclos nuevos. Añadir tests unitarios versionados para evitar depender del V8 del chat.
3. Ejecutar C01, C02 y C04 desde los **scripts congelados** `C01_ENGINE.js`, `C02_ENGINE.js`, `C04_ENGINE.js` con semillas exactas de cada preregistro; registrar diferencias numéricas esperadas y si el JS nativo necesita envoltorio, declararlo sin alterar lógica. Usar sumas exactas/tolerancias documentadas, no afirmar reproducibilidad antes de comprobarla.
4. Auditoría adversarial: tipos no ordinarios, propiedades heredadas, proxies, enteros fuera de rango, `NaN`, `Infinity`, `undefined`, cadenas muy largas, IDs sintéticos malformados, objetos mutables tras scoring, manifest anterior falsificado, cambio de regla y evidencia, importación de campos de persona/partido y caso sin cobertura. Los manifests **NO** tienen autenticación criptográfica: documentar el threat model y no promocionar gate.
5. Ejecutar suites focalizadas existentes y, **solo si son locales/baratas**, suite nativa completa desde checkout limpio; si no se ejecutan, marcar `NOT_RUN`. Nunca desbloquear puntuación de personas políticas ni afirmar listo para producción.
6. Archivar recibos con `run_id`, pruebas PASS/FAIL/SKIP, stderr/stdout, entorno, artefactos, hashes, commit anterior y posterior, problemas, correcciones con errata y reejecución. Si hay fallos, conservar el estado previo y no hacer reescrituras silenciosas. Actualizar Atlas y fuentes/priors si nueva evidencia.

## Criterios de aceptación
**PASS** únicamente si los 36 asertos nativos se reproducen, motores C01/C02/C04 reproducidos o límites declarados, ningún cambio de semántica sin nueva versión y se documenta el alcance local. **STOP/NEEDS_EXECUTOR** si falta checkout o runtime; no inventar éxito.

**Nota:** C03 primera ejecución V8 fue 14/18 por `structuredClone` ausente en runner, reparada dentro del mismo ciclo a 18/18 con JSON clone; existe `C03_ERRATA_AND_REPAIR.json`. Node nativo puede ofrecer structuredClone, pero no repetir como si fuera experimento científico nuevo.
