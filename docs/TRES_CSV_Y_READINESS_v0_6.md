# Tres CSV, sociometría prudente y readiness · v0.6

**Fuente de esquema (no descargada aquí):** [Congreso Abierto / Datos](https://congresoabierto.org/datos/), licencia declarada CC BY 4.0, atribución obligatoria: «Congreso Abierto (congresoabierto.org), a partir de datos oficiales del Congreso de los Diputados». Comparar una muestra contra [JSON oficiales del Congreso](https://www.congreso.es/es/opendata/votaciones) antes de certificar.

## Uso

Desde la raíz del proyecto y con Python >=3.10:

```sh
PYTHONPATH=src python -m politics_fantasy.field_cli \
  --individual data/local_field/votos_diputados.csv \
  --aggregate data/local_field/votaciones.csv \
  --group data/local_field/voto_por_grupo.csv \
  --acquired-at 2026-10-25T10:30:00+01:00 \
  --out data/local_field/report.json
```

Sustituir la fecha de adquisición de ejemplo por la real; el programa no la adivina. `--group` es opcional. Se guardan hashes, conteos y límites; el informe no incluye nombres ni identificadores de diputados. El CSV original no se publica en el repositorio. No volver a usar el mismo `--out`: la exportación es exclusiva y atómica.

## Contratos

- CSV nominal (voto por diputado), agregado (votación) y opcional por grupo, con columnas fijadas por la página de origen.
- `read_group_snapshot`: valida grupos únicos por votación, cantidades enteras no negativas, tamaño, fechas y SHA-256 del archivo exacto.
- `reconcile_groups`: contrasta sumas por grupo con totales; cuando se proporciona nominal, detecta nominal superior/inferior al agregado por grupo, sin imputar ausencias. Un match solo significa consistencia entre CSV.
- `group_vote_measure`: NO_VOTE solo explícitos. `modal_share_expressed` y `dissent_from_group_majority` son **dispersión descriptiva**, no disciplina, influencia ni mérito político. Los empates devuelven disidencia indefinida.
- `group_period_summary`: agrupa por año y etiqueta que tenía la fila publicada; no utiliza afiliación actual. La atribución histórica exacta **no está validada independientemente**.
- `observed_label_transitions`: detecta etiquetas diferentes en días distintos sin deducir transfuguismo, ideología ni motivación. No devuelve IDs.
- `as_of_snapshot_gate`: si el archivo se adquirió DESPUÉS de un corte, queda excluido; si se adquirió antes, sigue sin garantizar cuándo se publicó por primera vez. Por defecto NO habilita entrenamiento histórico.
- `yes_share_bounds`: sin censo verificable, el resultado es desconocido; solo con número de elegibles validado externamente puede acotar matemáticamente tasas entre elegibles, sin inventar NO_VOTE.
- `research_readiness`: nunca concede aptitud empírica por conciliación interna de tres tablas; persisten puertas de fuente, censo, calendario y baseline de campo.

## Interpretación y límites

No se han importado los 726.564 registros mencionados en el portal. No se puede hablar de votación individual española validada en esta versión. El hash del propio reporte es un checksum, **no una firma de origen confiable**. El panel local `/api/field` devuelve exclusivamente métricas agregadas; no se deben abrir puertos a Internet sin sesiones, CSRF y seguridad integral. El usuario conserva potestad para importar datos licenciados manualmente, con procedencia y cumplimiento de las condiciones de uso. Las 147 pruebas usan fixtures sintéticas.

**Protocolo AB:** contratos 30C C01–C30 de ingeniería A–J, 0 hallazgos científicos 2/3; grado de valor VSDS del proyecto 1/3; CT2 predicción 24/100 sin incremento por más código. Pendientes: auditoría de fuente real, variaciones de esquema real, roster fechable, temporalidad primera publicación y validación externa.
