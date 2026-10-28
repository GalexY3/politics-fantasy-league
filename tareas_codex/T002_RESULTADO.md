# T002 · Suites completas

**Resultado: COMPLETADA_CON_FALLOS.** Baseline en `6e359a89e74f06927e51ca4dc8a9ea1714e37acd`, rama `research/pfl-codex-contributions-20261027`, Windows, Python 3.12.14 y Node v24.16.0. Cwd `C:\Github\Politics-Fantasy-Codex\proyectos\politics-fantasy-league`; `PYTHONPATH=src`, `PYTHONDONTWRITEBYTECODE=1`. Había dos carpetas generadas sin versionar, sin cambios en código rastreado. No se ejecutó Actions ni se contactaron fuentes institucionales.

## Primer resultado preservado

`python -m pytest -q -rs`: **exit 1; 59 failed, 535 passed, 28 skipped, 24 subtests passed**. La salida íntegra está localmente en `%TEMP%\pfl-tasks-20261028\T002_pytest_stdout.txt`, SHA-256 `bd7dc64d40fc9daa650d48b5deb9134e4b63e60652126add62d8f615c3c5989f`; stderr vacío. Se usaron los 83 archivos versionados `tests/test_*.py` detectados en la base, conforme a la configuración de pytest.

Los encabezados de fracaso se agruparon así: 45 muestran directamente `SECURE_STORE_UNSUPPORTED_PLATFORM`; siete pruebas de redirección no llegan al opener ficticio porque falla antes el preflight del almacén; tres intentan crear enlaces simbólicos y reciben WinError 1314; tres fixtures de tipo usaban un alias ESE ambiguo y se corrigieron en T006; un test de escritura cooperativa agota la espera de un hilo, compatible con la misma limitación del almacén pero sin excepción del hilo demostrada en la traza. Los 28 skips incluyen controles explícitamente POSIX y uno por privilegio de symlink. Esto no demuestra que las pruebas POSIX vayan a pasar.

`node --test` sobre los 13 archivos `tests/test_*.mjs` de la base: **exit 1; 118 passed, 1 failed**. Falló `wrong scope identity cannot be compared`: una familia ajena era rechazada con `BAD_SCOPE_VERSION` antes del diagnóstico esperado `SCOPE_LINEAGE_MISMATCH`. La salida está en `%TEMP%\pfl-tasks-20261028\T002_node_stdout.txt`, SHA-256 `a1c167810cb07daed0d75f88de067823af54dd83d338325418cf0eaccef156df`; stderr vacío. El recolector auxiliar que mostró la cola en Windows encontró además un error de codificación de consola, posterior al guardado y separado del exit 1 real de Node. `node --check src/politics_fantasy/web/app.js`: exit 0.

## Reejecución tras las reparaciones y pruebas añadidas

`python -m pytest -q -rs`: **exit 1; 57 failed, 558 passed, 28 skipped, 24 subtests passed**; salida `%TEMP%\pfl-tasks-20261028\T002_final_pytest_stdout.txt`, SHA-256 `9958b5347ffc2db6d31e5de5f71b836dc7fb076132a8f3be5d39fe218f92f7a5`, stderr vacío. Se corrigieron los tres fixtures de T006, sin habilitar alias; los controles POSIX y symlink permanecen sin resolver en esta máquina. No se ha inventado un almacenamiento alternativo menos seguro.

`node --test` sobre los **15** archivos `tests/test_*.mjs` presentes tras los cambios: **exit 0; 125 passed, 0 failed, 0 skipped**; salida `%TEMP%\pfl-tasks-20261028\T002_final_node_stdout.txt`, SHA-256 `0621bf27bb3b46dd4f3472bfeda91048c463f59b53d4a4c17b5c0412251ccc53`, stderr vacío. La corrección de precedencia del diagnóstico y la prueba de paridad están en [T003](T003_RESULTADO.md). El flujo de navegador Chromium de compra, alineación, simulación, puntuación y siguiente jornada también pasó, usando la instalación local de Playwright; no es E2E de ingesta privada.

WSL no está instalado y no se encontró Docker ni Podman. Git Bash disponible es MINGW y no proporciona un Python POSIX. Python 3.13 y 3.14 están instalados, pero no tienen pytest; no se instalaron herramientas globales. Queda pendiente ejecutar las suites de almacenamiento, señales y concurrencia en un entorno POSIX real y repetir la suite completa allí. No se ha elevado madurez, CT2 ni gates.
