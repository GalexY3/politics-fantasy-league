# T001 · Replay Python canónico de los 28 lotes AB Atlas

**Prioridad P0 · Estado PENDIENTE · Encargo para Codex, no ejecutado.** [Volver al índice](README.md).

## Por qué existe

Hasta CONT60 (28/10/2026), el proyecto tiene 28 deltas JSON versionados. En C58 se comprobaron sus enlaces padre y su aritmética **leyendo archivos de GitHub**, no ejecutando el motor original `ab_atlas/atlas_delta.py` que valida invariantes y calcula el hash canónico. Es la principal deuda verificable del Atlas.

## Instrucciones ejecutables

Desde la raíz del repositorio privado, **en la rama de investigación**, registrar antes de nada:

```bash
git status --short
git branch --show-current
git rev-parse HEAD
python --version
git ls-files 'proyectos/politics-fantasy-league/ab_atlas/updates/*.json'
```

Comprobar que hay exactamente **28** lotes `0001…0028` antes de ejecutar (si hubiera nuevos, detenerse y actualizar la tarea y su base; **no** alterar evidencias anteriores para acomodar resultados).

```bash
python ab_atlas/atlas_delta.py check \
  --base proyectos/politics-fantasy-league/ab_atlas/seed.json \
  --updates proyectos/politics-fantasy-league/ab_atlas/updates
```

Este comando está **confirmado en el script raíz** `ab_atlas/atlas_delta.py`: imprime `OK <N> lotes <M> nodos SHA256 <digest>` si el replay/las validaciones se completan. Si interesa auditar el estado, usar `replay` con los mismos `--base` y `--updates`, y `--out` apuntando a una ruta temporal **fuera del árbol versionado**. El SHA informado por `check` es el hash de serialización canónica interna; **no comparar directamente con un hash de un JSON pretty-print**.

## Criterios de aceptación

- 28 deltas detectados en orden, `exit code 0` y stdout original conservado **sin manipular**.
- Registrar **SHA canónico informado por el checker**, HEAD Git, versión Python, cwd, comando exacto y stderr (incluso si está vacío).
- Comparar el recuento de operaciones documental de CONT60 —63 nodos, 81 relaciones, 179 runs, 44 complaints, 348 operaciones— contra el replay. El comando `check` solo informa lotes/nodos/SHA: extraer las otras cifras del estado reconstruido, sin darlas por certificadas de antemano.
- Revisar `project_contract.release_gates`: **ningún gate se marca passed por este trabajo**. Cualquier diferencia es una incidencia, no una mejora automática.
- Si falla: conservar código de salida, primer lote/invariante que falla, motivo verificable y reproducción mínima; proponer reparación de lote *nueva* y append-only **sin reescribir históricos**, previa revisión metodológica.

## Entregables

Informe `T001_RESULTADO.md` (crearlo al ejecutar, no ahora), salida de terminal, hash canónico, recuentos, resumen de invariantes y enlaces a commits reales. Estado `COMPLETADA_VERIFICADA` solo si todos los criterios se satisfacen. **No** cuenta como 10 nuevos ciclos AB ni autoriza cambios de madurez.
