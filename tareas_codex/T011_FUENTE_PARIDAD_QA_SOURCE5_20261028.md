# T011 · Captura oficial de paridad electoral + QA de la rama de investigación

**Estado: PREPARADO PARA CODEX, NO EJECUTADO.** El usuario ha autorizado **cinco** ciclos AB-H SOURCE5 por separado. Este encargo a Codex es **ejecución técnica de soporte**, no es por sí mismo un ciclo AB A–J, no gasta presupuesto científico ni autoriza hallazgos, medallas, cambios V4, uso de ChatRelay o despliegue.

## Contexto obligatorio

- Repo privado `GalexY3/Metodologia-AB`. Inspeccionar `AGENTS.md`, protocolo AB 3.2.1/O3–O7, proyecto `proyectos/politics-fantasy-league/README.md`, `ab_atlas/CURRENT.md` y los documentos de campaña `research/ABH_SOURCE5_20261028/AUTHORIZATION.json`, `C01_ACCESS_PROBE.json`, `C02_PREREG.json`, `C02_RESULT.json` y `CAMPAIGN_STATUS.json`.
- Rama de base **`research/pfl-abh5-source-validation-20261028`**. Comprobar `git fetch`, `git status --short` y `git rev-parse HEAD`; no asumir SHAs ni que `main` contenga T010. Crear rama de ejecución nueva `exec/pfl-t011-paridad-20261028` **a partir del HEAD verificado de SOURCE5**. No sobrescribir ficheros de campaña.
- La rama SOURCE5 ya parte de las dos reparaciones no fusionadas PR #18 T010 y PR #19 vote-key. No fusionar ninguna de ellas; no crear CI costosa.
- La última evidencia del repositorio es **C02**, un catálogo nuevo de paridad electoral del Ministerio del Interior, con **0 bytes originales capturados** desde ChatGPT. No afirmar que fecha de catálogo = `first_public_at`.

## Objetivo 1: descarga primaria autenticable (sin exposición de filas nominales)

Buscar dos distribuciones que el catálogo oficial anuncia:

1. `https://descargas.interior.gob.es/datasets/paridad_electoral/Paridad-cargos-electos.xlsx`
2. `https://descargas.interior.gob.es/datasets/paridad_electoral/Paridad-candidatos-y-candidatas.xlsx`

Procedencia: `https://sede.interior.gob.es/portal/sede/informacion-general/catalogo-de-datos`, conjunto «Paridad Electoral (Candidatos/as y Cargos electos)». Como comparador de estructuras de elección, considerar **solo si es necesario** el original `https://descargas.interior.gob.es/datasets/resultados_electorales/Elecciones-Congreso-cargos-electos.xlsx`. Evitar descargar todo el catálogo por inercia.

Para **cada** intento, guardar en registro la URL exacta, UTC de inicio/fin, HTTP code, redirecciones (sin credenciales), tipo MIME, Content-Length si existe, tamaño real, HTTPS/TLS verificado o error literal. No desactivar comprobación TLS ni seguir dominios no previstos silenciosamente. **Guardar los originales sin modificar en ubicación local excluida de Git**; calcular SHA-256 de los bytes originales. Validar que no es HTML/403 con extensión XLSX; probar firma ZIP/OOXML, `zipfile.testzip()`, presencia de partes mínimas XLSX y carga de solo lectura. Nunca declarar datos descargados a partir de una página de catálogo.

Si la descarga se bloquea, **STOP_R5** tras rutas mínimas justificadas; documentar fallos y, si es viable, ofrecer alternativa de descarga manual oficial con posterior hash. No inventar archivo, recuento, columnas ni fecha primera publicación.

## Objetivo 2: esquema, denominadores y comparación competente

Si existen bytes íntegros de ambos XLSX:
- Registrar nombres de hojas, encabezados y conteos de filas; comprobar duplicados según clave identificadora **solo después de verificar la clave real**, nulos, tipos, rangos y fechas/convocatoria.
- Diferenciar **candidaturas**, **personas candidatas**, **cargos electos**, **procesos electorales** y **elecciones distintas**; no calcular tasa de elección sin denominadores comparables, ni identificar una candidatura con un partido registrado. Confirmar las categorías literales de sexo/género del fichero, sin reconstruir identidad sensible ni inferir género de nombres.
- Para un piloto pequeño y controlado, calcular solo **agregados** con las unidades/convocatorias compatibles (fecha, ámbito y circunscripción si hay campos); un comparador razonable puede ser la distribución de candidaturas en idéntico estrato. Reportar conteos y desconocidos/sin categoría; si no hay unión exacta, NO construir tasas de éxito ni comparar años incompatibles.
- Nada de rankings personales, scoring de políticos reales, datos de afiliación inferidos ni subida de originales nominales a Git/GitHub. Mantener informes en el repositorio sin nombres de personas ni filas identificables. Verificar términos de reutilización por distribución, límites jurídicos y denominadores; no equiparar CC-BY a legitimación de perfilado.

## Objetivo 3: QA integrado antes de decidir logros QA-01/QA-02

En un **checkout limpio** y sin datos privados, ejecutar la suite real de la rama de trabajo (en Linux/POSIX si disponible):
1. Checker y replay `python ab_atlas/atlas_delta.py check/replay --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates`; comprobar número real de lotes, nodos, enlaces, operaciones, y SHA canónico.
2. `python -m pytest -q -rs -p no:cacheprovider ab_atlas/tests` desde raíz.
3. En `proyectos/politics-fantasy-league` con `PYTHONPATH=src`, `python -m pytest -q -rs -p no:cacheprovider` y `node --test tests/*.mjs`. No atribuir los 770 Python/144 Node de T010 al SHA nuevo.
4. Guardar cada stdout, stderr, exit, entorno/versiones, SHA-256 de logs y commit bajo prueba. Si falla por entorno, reparar solo si es legítimo y **registrar primer fallo**. No cambiar expectativas a PASS ni omitir nuevos regresores.
5. Un PASS técnico y el hash canónico son necesarios para candidaturas QA, pero **no modifican por sí solos** el registro de medallas; verificar prerequisitos, auditoría y `ab_atlas/ACHIEVEMENTS_README.md`.

## Entregables y aceptación

- Crear `tareas_codex/T011_RESULTADO.md`, manifiesto `tareas_codex/T011_EVIDENCIA/MANIFEST.json` y logs de comprobación en la rama de ejecución, con enlaces GitHub y SHAs exactos; **sin originales XLSX**, filas nominales, cookies, tokens ni datos personales.
- Si es posible, crear un archivo analítico de agregados sin individuos `research/ABH_SOURCE5_20261028/C02_ORIGINAL_SOURCE_AGGREGATES.json` con procedencia y controles de sesgo; no debe reescribir `C02_RESULT.json` retroactivamente. Un ciclo posterior autorizado evaluará el material como nueva evidencia; Codex no acredita automáticamente ningún ciclo.
- `SUCCESS` solo si se obtienen originales byte-verificados y QA integrado PASS, o `PARTIAL` si hay éxito documental de un lado y bloqueo del otro. `BLOCKED` con causa específica y reproducción cuando no hay acceso. Conservar rechazos y resultados negativos.
- Acompañar con resumen de archivos modificados, base y SHA probado; abrir **PR borrador** hacia la rama SOURCE5 si no hay instrucciones contrarias, **sin fusionar** a `main` ni a otras ramas. No usar ChatRelay.
