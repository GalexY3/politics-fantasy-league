# Bloque experimental PF-AB20 autorizado el 24/10/2026

**Autorizados 20**. Hasta este cierre, **0 ciclos experimentales AB plenamente validados con microdatos**, **1 piloto observacional exploratorio C01 ejecutado**, **19 ciclos aún disponibles y NO_EXECUTED**. La ejecución C01 cuenta como una unidad de trabajo del bloque por transparencia, pero es `INCOMPLETE_FREEZE` según O2/O3, sin graduación 1/3 ni consumo de confirmación. Saldo provisional: 19. No equiparar C01 con una replicación ni convertir C02–C20 en ciclos consumidos.

- `PREREG_C01.md` y `PREREG_SHA256.txt`: congelación local anterior a la evaluación aritmética, insuficiente frente a GitHub freeze.
- `C01_AUDIT_AND_READOUT.md`: resultados verificables contra CSV y límites.
- `RESULT_C01.json`: datos derivados por script, no un nuevo dataset oficial.
- `C02_C20_BACKLOG.md`: sólo instrumentación condicionada, no experimentos ni preregistros.
- `campaign.json` y `CYCLES_LEDGER.json`: estados, saldo y bloqueo.
- `PRIORS_DELTA.md`: evolución limitada de priors.
- `../../data/pilot_official_webview`: CSV de fuente transcrita y limitaciones.
- `../../scripts/ab20_c01_pilot.py`: instrumento ejecutable.

**BLOQUEO**: el puerto de red del contenedor no resuelve el dominio oficial; intento de descarga dedicada también falló; el lector web encontró JSON individual pero no puso a disposición el cuerpo legible. Se requiere acceso a descarga oficial con fechas/condiciones de reutilización antes de entrenar modelos. GitHub rechazó writes; no hay prueba de commit remoto. **No convertir cualquier timestamp de la descarga tardía en una primera fecha histórica disponible.**