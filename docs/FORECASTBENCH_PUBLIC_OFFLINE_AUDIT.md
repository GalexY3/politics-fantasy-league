# PFL — auditoría sin red de preguntas públicas de ForecastBench

Herramienta de desarrollo: `scripts/offline_forecastbench_audit.mjs`. **No es un servidor, no recoge respuestas ni constituye un estudio humano.** Requiere Node.js 20+ y solo procesa el material público, no identificable, de preguntas y resoluciones de [ForecastBench](https://github.com/forecastingresearch/forecastbench-datasets), Forecasting Research Institute / Karger et al., ICLR 2025, CC BY-SA 4.0. La licencia del conjunto de datos **no** autoriza automáticamente otros tratamientos de datos personales o reutilizaciones de contenido de plataformas subyacentes.

## Preparación manual

A partir del commit original inmutable `027ba0b3017a60e0e64602d724284ac6b2d91134`, obtener los siguientes cuatro archivos públicos y guardarlos en una carpeta local `datos/`:

```text
datos/
  question_sets/
    2026-09-27-llm.json
    2026-10-11-llm.json
  resolution_sets/
    2026-09-27_resolution_set.json
    2026-10-11_resolution_set.json
```

**No descargar predicciones individuales**, datos de encuestas humanas ni conjuntos de `forecast_sets` para este flujo. No renombrar o reserializar los archivos: sus bytes han de coincidir con las cuatro identidades Git originales especificadas en `src/politics_fantasy/forecastbench_provenance.mjs`.

Desde la raíz `proyectos/politics-fantasy-league`:

```sh
node scripts/offline_forecastbench_audit.mjs --source-dir ./datos --as-of-date 2026-10-29
```

La salida estándar es **solo JSON agregado** por cohorte: número de preguntas, resoluciones, rechazos según motivo y Brier descriptivo de probabilidades de mercado congeladas que ya tenían desenlace conocido en la fecha indicada. No emite textos de preguntas, IDs, nombres de personas, probabilidades por pregunta ni muestras de participantes. Una fuente modificada o incompleta provoca código de salida **2**, sin resultados parciales. El parámetro `--as-of-date` es obligatorio y no admite un día anterior al vencimiento de la cohorte.

## Verificación y límites

Pruebas nativas sin Internet: `node tests/test_offline_forecastbench_audit.mjs`, **11/11 PASS** en el commit de la [PR #55](https://github.com/GalexY3/Metodologia-AB/pull/55). Contrasta hash y lectura real de ficheros sintéticos temporales, modificaciones, extras, símbolos y salida de errores sin detalles privados. No se debe usar `expected_blobs` autoconstruido como prueba de fuente: esa vía existe **exclusivamente para fixtures técnicos**, y el resultado marca `used_project_manifest:false`. El CLI no expone opción para reemplazar los cuatro hashes oficiales.

**Comprobación original independiente posterior al preregistro:** el conector GitHub permitió leer, re-encodificar y calcular SHA1 Git de los cuatro blobs originales completos; **4/4 coincidieron** con los SHA fijados. Se ejecutó también el guard de preguntas públicas sobre esas respuestas y devolvió 52 registros admisibles en la cohorte 27/09 y 8 en 11/10, a corte 29/10. Esto **NO** equivale a haber ejecutado el nuevo CLI nativo sobre las cuatro rutas locales originales: el contenedor local no pudo descargar esos archivos. El recibo [C04_POSTHOC_ORIGINAL_SOURCE_SHA_RECEIPT.json](../research/ABH30_NEW_20261029/C04_POSTHOC_ORIGINAL_SOURCE_SHA_RECEIPT.json) deja explícita la distinción.

Los SHA de Git verifican identidad de bytes respecto a un objeto declarado y versionado, **no** autenticidad editorial, autorización de uso, revisión ética, seguridad general de todo el sistema o preparación para lanzamiento. El directorio que se pasa al CLI es un directorio **local de confianza**; `O_NOFOLLOW` impide sustituir el componente final por un enlace simbólico en POSIX, pero no prueba inmunidad ante carreras de archivos o enlaces en componentes ancestrales. No se recomienda cargar directorios de usuarios desconocidos ni habilitar acceso remoto. Las resoluciones con fecha sin hora se excluyen hasta el día siguiente para no anticipar la información.

La métrica Brier observada está **condicionada a haberse resuelto el evento** y no caracteriza por sí sola el conjunto inicial; consultar el análisis de identificación parcial de C03. Los pronósticos congelados son agregados externos, nunca predicciones de PFL. Esta herramienta no autoriza puntuar políticos reales ni satisface ningún gate de lanzamiento.
