# T002 · Ejecutar TODAS las pruebas del proyecto, no solo el subconjunto reconstruido

**Prioridad P0 · Estado PENDIENTE · Sin ejecución de Codex.** [Volver al índice](README.md).

## Justificación

En CONT50 hubo **173 Python + 9 Node PASS** sobre una selección de 12 módulos y 18 archivos de test, coincidentes por blob SHA. En CONT60 hubo **47 PASS** nativos del subsistema de privacidad/procedencia. Son subconjuntos superpuestos; **no sumar como si fueran pruebas independientes ni afirmar que son toda la aplicación**. Faltan suites completas (Python, Node e integración del servidor), ahora sí posibles con checkout íntegro.

## Preparación mínima

```bash
git branch --show-current
git rev-parse HEAD
git status --short
python --version
node --version
```

Leer `AGENTS.md`, el `pyproject.toml` del proyecto y su documentación. No activar GitHub Actions ni conectarse a endpoints de instituciones para completar tests locales. Si faltan dependencias, documentar el error y pedir autorización antes de instalaciones significativas; preferir entorno virtual limpio.

## Comandos candidatos (desde el directorio del proyecto)

```bash
cd proyectos/politics-fantasy-league
PYTHONPATH=src python -m pytest -q
node --test tests/test_*.mjs
node --check src/politics_fantasy/web/app.js
```

No se ha verificado aquí que **todos** los tests sean autocontenidos ni que estas órdenes pasen; se solicitan precisamente para descubrir el estado real. Si el glob `tests/test_*.mjs` no abarca alguna suite JavaScript documentada o si existen tests con fixtures externos, identificar y ejecutar/explicar expresamente esos huecos. La CI histórica `.github/workflows/ci.yml` utilizaba Python 3.10/3.13: idealmente repetir en ambas versiones **localmente** si existen, sin consumir Actions costosas.

## Criterios de aceptación

- Inventario real de tests y archivos cubiertos, incluyendo `tests/test_ingest.py`, `test_quarantine_ingest.py`, suites de privacidad, evaluación, alcance, registros originales y servidor.
- Por cada suite: **comando, cwd, stdout/stderr, exit code, versión Python/Node, nº de pruebas PASSED/FAILED/SKIPPED**, motivo concreto de cada skip.
- Diferenciar fallos de entorno (dependencia/red/OS) de regresiones de código. Conservar la primera ejecución **sin editar tests ni eliminar fallos**.
- Si se corrige un defecto: prerregistro según AB, commit antes/después, test rojo antes y verde después, rerun de la suite relacionada. No convertir una modificación de fixture en confirmación del comportamiento de producción.
- No modificar el alcance V4, CT2 ni gates sin criterios propios y evidencia independiente. **Nada de datos nominativos originales.**

## Entregables

`T002_RESULTADO.md`, logs locales versionables si no incluyen datos sensibles, tabla de casos y commits. No marcar `COMPLETADA_VERIFICADA` si se omitieron suites sin explicación; `COMPLETADA_CON_FALLOS` es admisible con evidencias verificables.
