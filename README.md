# Politics Fantasy League · WIP

Prototipo fantasy con datos ficticios e investigación sociológica/institucional. **Producto e investigación tienen objetivos y evaluaciones separados.** La aplicación sigue siendo una demo local; autenticación multiusuario, fuentes institucionales y lanzamiento tienen sus propios requisitos pendientes.

## Por dónde empezar

- **[Continuar el proyecto o empezar un chat](START_HERE.md)**
- [Mapa: dónde está cada cosa](PROJECT_MAP.md) · [Índice de investigación](research/INDEX.md)
- [Estado e hitos actuales](PROJECT_STATE.json) · [Último handoff](HANDOFF.md)
- [Prompt reutilizable](NEW_CHAT_PROMPT.md) · [Cola técnica](tareas_codex/README.md)

## Ejecutar la demo

Desde la raíz de este repositorio, con Python 3.10 o superior:

```sh
python run_demo.py
```

En Windows también puedes usar `start_windows.bat`; en Linux/macOS, `start_linux_mac.sh`. El servidor escucha solo en loopback. Los controles de almacenamiento privado requieren POSIX; la demo del juego y ese importador son capacidades distintas.

## Comprobar el proyecto

```sh
python -m pip install '.[test]'
PYTHONPATH=src python -m pytest -q -rs
node scripts/run_node_tests.mjs
python -m pytest -q -rs tools/ab_atlas/tests
python scripts/project_status.py check
python scripts/project_index.py find T005
```

Los comandos de pruebas anteriores usan sintaxis de shell POSIX; en PowerShell establece `$env:PYTHONPATH='src'` antes de ejecutar pytest. La CI remota es manual para no disparar trabajos por cada commit.

## Relación con AB

PFL **utiliza** AB; el repositorio del método es [Metodologia-AB](https://github.com/GalexY3/Metodologia-AB). [METHOD_REFERENCE.json](METHOD_REFERENCE.json) fija la versión documental adoptada y las adaptaciones locales. Actualizar el método no modifica automáticamente las reglas o resultados del proyecto.

El motor Atlas necesario está fijado en `tools/ab_atlas/`; el estado y los lotes de PFL están en `ab_atlas/`. Ni una medalla, ni un test, ni un porcentaje de madurez acreditan por sí solos evidencia humana o preparación de lanzamiento.

## Historia y migración

El proyecto se extrajo de AB conservando su historia relevante. [Procedencia y mapa de commits](docs/migration/README.md). Los SHA originales y enlaces históricos siguen identificando sus fuentes en AB; el mapa permite localizar sus equivalentes en esta historia filtrada. Se conservaron los blobs originales antes de adaptar las rutas operativas.

El README extenso anterior sigue en [el archivo histórico](README_HISTORICO_HASTA_20261029.md). Los originales locales no versionados no se han incorporado a la migración.

## Trabajo reciente incorporado para revisiÃ³n

La migraciÃ³n de la [PR #81 histÃ³rica de AB](https://github.com/GalexY3/Metodologia-AB/pull/81)
se prepara y valida **en este repositorio**. Incluye cuentas multiusuario locales ficticias (P1),
C38 observacional negativo sobre documentaciÃ³n institucional y Atlas 0094. Consultar
[estado](PROJECT_STATE.json), [revisiÃ³n P1](docs/P1_ACCOUNTS_REVIEW.md) y
[manifiesto del traspaso](docs/migration/CUTOVER_PR81_TRANSFER_MANIFEST.json).
Las pruebas de origen no equivalen a ejecuciÃ³n en el nuevo commit; el estado de revisiÃ³n se
mantiene hasta completar QA y aceptaciÃ³n. Todas las futuras tareas de PFL se realizan aquÃ­.
