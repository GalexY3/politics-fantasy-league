# T001 · Replay Python canónico

**Resultado: COMPLETADA_VERIFICADA**, en el checkout `6e359a89e74f06927e51ca4dc8a9ea1714e37acd` de `research/pfl-codex-contributions-20261027`, antes de los ajustes posteriores de esta cola. Es una validación estructural, no un nuevo ciclo AB ni una certificación de hechos.

Entorno: Windows, Python 3.12.14, directorio `C:\Github\Politics-Fantasy-Codex`; el árbol tenía `ab_atlas/__pycache__/` y `proyectos/politics-fantasy-league/src/politics_fantasy_lab.egg-info/` sin versionar, generados en la sesión anterior. `git ls-files 'proyectos/politics-fantasy-league/ab_atlas/updates/*.json'` contó **29** ficheros. La aceptación heredada de T001 que dice 28 es una errata documental: la instrucción y el estado de partida actualizado piden 29; no se alteraron lotes anteriores.

Comando, ejecutado desde la raíz, exit 0 y stderr vacío:

```text
python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates
OK 29 lotes 63 nodos SHA256 c06641eb51915d0a0a5b21a111cd91b8fb55db33b7c12c0dabcde14c8635275c
```

Se ejecutó además `replay` a `%TEMP%\pfl-atlas-20261028.json`, exit 0, y se contaron sus objetos y las operaciones de los deltas: **63 nodos, 81 relaciones, 187 runs, 44 incidencias y 356 operaciones**, coincidentes con el dato documental. El JSON reconstruido es temporal; su representación no tiene por qué tener el hash canónico anterior.

Seis gates: `data_registry`, `identity` y `events` bloqueados; `authentication`, `e2e` y `deployment` pendientes. Ninguno está `passed`. No se cambiaron fuentes, porcentajes ni gates. El replay no autentica procedencia ni contenido de las pruebas registradas.
