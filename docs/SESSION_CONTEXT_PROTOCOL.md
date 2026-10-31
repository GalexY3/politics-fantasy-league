# PFL · Contrato de contexto integral verificable entre chats y agentes

**Versión 1.0, 31/10/2026.** Contrato prospectivo de operaciones/lectura, no una nueva regla de AB, experimento científico, licencia de datos ni autorización de despliegue. Se aplica a ChatGPT, COS, revisores, agentes delegados y futuros chats que trabajen en Politics Fantasy League (PFL).

## Principio: contexto integral recuperable ≠ 3.000 archivos en una ventana de tokens

El usuario quiere que **ninguna parte del proyecto quede invisible por defecto**. Esto requiere **inventario completo, fuentes de autoridad y recuperación bajo demanda**, no simular una memoria infinita. Incluso si un programa abre y procesa todos los bytes para calcular SHA, un modelo no ha leído ni comprendido semánticamente esos archivos. Cada sesión debe distinguir cuatro operaciones:

1. **`INVENTARIADO`**: el archivo aparece en `git ls-files` / índice de rutas, pero no se ha abierto.
2. **`HASH_VERIFICADO`**: todos sus bytes fueron recorridos para calcular SHA-256 y detectar pérdida/deriva; no se ha inferido el contenido.
3. **`LEIDO_SEMANTICAMENTE`**: el agente o revisor ha recibido y examinado el contenido pertinente, completo o por rangos explícitos, identificando partes no inspeccionadas. No se acredita con un hash, un título o un resumen previo.
4. **`EJECUTADO_VERIFICADO`**: un contrato/función/test se ejecutó en el commit y entorno indicados, con salida observada. Tampoco equivale a comprobación empírica ni de licencias.

**Prohibido declarar «leído todo», «conozco cada rincón», «código probado» o «datos validados» si solo se dispone de índices, hashes, documentación o comprobaciones focales.** El protocolo permite *alcance sistemático* y *lectura exhaustiva del subconjunto necesario para actuar*, no omnisciencia. Lo que no esté accesible se declara explícitamente.

## Autoridades y repositorios

- **Objetivos expresos y alcance científico:** `docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md`, `docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md`; cualquier cambio estratégico exige decisión identificable del usuario. Núcleo: sistema político español real, reproducción/autorregulación y acoplamientos con derecho, economía, empresas, medios y sociedad; fantasy, aplicación, no fin exclusivo.
- **Reglas operativas:** `AGENTS.md`, este documento y `docs/WORKING_AGREEMENT.md`. Las instrucciones actuales del usuario y límites de seguridad/legales prevalecen; un documento de investigación no puede otorgar permisos ni ciclos.
- **Estado de hitos:** `PROJECT_STATE.json` con `scripts/project_status.py brief|check`; **autorizaciones:** ledgers originales por campaña, en particular `research/PFL_SYSTEM20_20261031/AUTHORIZATION.json`; **último trabajo:** `HANDOFF.md` e informe de ronda en su propio directorio. Los snapshot históricos no sustituyen a esas autoridades.
- **Método científico:** `METHOD_REFERENCE.json` apunta a `GalexY3/Metodologia-AB` en commit fijado; se deben recuperar y leer el método y O1–O7 antes de **nueva investigación AB**, no asumir su lectura porque exista URL o por la memoria de otro chat. El `docs/AB_O1_O7_RFC_PFL_20261031.md` no implica adopción.
- **Atlas de trabajo:** `ab_atlas/seed.json`, todos los `ab_atlas/updates/` y su reconstrucción con `tools/ab_atlas/atlas_delta.py`. **Atlas de logros:** `ab_atlas/ACHIEVEMENTS_REGISTRY.json` + política README + validador, separado de los nodos, progreso V4, CT2 y puertas de lanzamiento.
- **Ramas y PR:** GitHub es la autoridad de publicación. `main` puede quedar por detrás de PR apiladas. Comparar `git rev-parse HEAD`, estado de worktree, `git ls-remote` de la rama activa y `gh pr view` cuando estén disponibles, sin confundir `MERGEABLE` con revisión aprobada. No seleccionar una rama solo por fecha del directorio o porque un prompt enlaza `main`.
- **Navegación y archivo histórico:** `PROJECT_MAP.md`, `PROJECT_INDEX.json`, `research/INDEX.md`, `docs/migration/`, `tareas_codex/` y `research/`. El índice categoriza, no certifica actualidad o lectura. **No borrar, mover ni corregir retrospectivamente evidencias inmutables para simplificar el árbol.**

## Preflight obligatorio al abrir CADA sesión

**Paso A — acceder:** verificar si hay PC/COS/Git/archivos. Si no existen, leer vía GitHub accesible y describir exactamente qué no se pudo abrir o ejecutar. Nunca atribuir acceso al PC por ver una URL. No recurrir a suposiciones del chat previo.

**Paso B — reconciliar:** resolver rama/cabeza local, rama remota y PR apilada; comprobar `git status --porcelain`, `PROJECT_STATE`, último ledger y que la revisión reclamada sea la efectivamente disponible. No editar si cambió el HEAD o hay deriva concurrente sin aclarar autoría.

**Paso C — inventariar TODOS los archivos versionados (nivel máquina, sin datos privados):**

```powershell
python scripts/session_context.py audit
python scripts/session_context.py audit --inventory-out ../PFL-context-inventory.json
python scripts/project_index.py check
python scripts/project_status.py brief
python scripts/project_status.py check
python tools/ab_atlas/atlas_delta.py check --base ab_atlas/seed.json --updates ab_atlas/updates
python ab_atlas/validate_achievements.py
```

`session_context.py` lee **todos los bytes de todos los archivos versionados del árbol de trabajo** para SHA-256, confronta membresía contra el índice, identifica anclas ausentes y devuelve SHA del manifiesto. También informa el OID del árbol de `HEAD`, comparable entre equipos para el mismo contenido Git. **Los SHA-256 de los bytes del worktree pueden cambiar entre sistemas por diferencias de finales de línea**; no usarlos como identidad canónica de contenido entre plataformas sin normalización y comprobación de `.gitattributes`. Solo con `--inventory-out` escribe un recibo en la ruta explícita **FUERA del repositorio**; no recorre `data/raw`, `data/local_field`, otras carpetas privadas, objetos remotos, versiones no presentes ni ficheros sin seguimiento. Nunca lo presentes como lectura semántica. Si falta Python/Git/herramientas o falla el inventario, informar qué parte queda sin cobertura. El estado y el índice se verifican por separado; ningún comando acredita licitud de uso o bondad de un resultado científico.

**Paso D — leer contenido, no solo identificar rutas.** Lectura semántica obligatoria de:

| Nivel | Documentos / alcance | Cuándo |
| --- | --- | --- |
| **T0: mandatos** | `AGENTS.md`, este protocolo, `docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md`, `docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md`, `docs/WORKING_AGREEMENT.md`, instrucciones actuales del usuario | Toda sesión con decisiones |
| **T1: estado** | `START_HERE.md` (sección vigente, no toda la crónica), `PROJECT_STATE.json` (estado/autoridades/hitos), `HANDOFF.md` (última sección, no interpretar rótulos heredados), ledgers vigentes, `METHOD_REFERENCE.json`, `BRANCHES.json` con reconciliación real Git | Toda sesión |
| **T2: mapas** | `PROJECT_MAP.md`, `research/INDEX.md`, `PROJECT_INDEX.json` para localizar el árbol; política Atlas+logros y resultados de validadores | Toda sesión |
| **T3: investigación** | Documento AB fijado más O1–O7 relevantes, contratos A–J, antecedentes/rivales, fuentes, manifests, originales **solo si autorizados**, reportes negativos y positivos, versiones y falsadores | Antes de proponer o abrir investigación |
| **T4: ejecución** | Código completo del flujo a tocar, dependencias relevantes, tests, contratos API/esquema, callers, versiones, derechos y tests que podrían romperse | Antes de editar o ejecutar cambios |
| **T5: archivo transversal** | Todas las rutas históricas localizadas por `project_index.py find`, búsquedas de símbolo/linaje entre `src`, `tests`, `research`, `tareas_codex` y los registros de migración | Para evitar duplicar trabajos y afirmar novedad |

Si el material de T3–T5 es demasiado grande, **dividir en pasadas con listado de rangos, archivos leídos y pendientes**, y completar las partes que afectan a la decisión antes de emitirla. No resumir partes ausentes como si estuvieran leídas. Para investigación documental, leer las fuentes aplicables y también el historial de intentos negativos de la misma población; no volver a abrir endpoints bloqueados por inercia.

## Ficha de cobertura obligatoria por sesión (la escribe el agente, no el preflight)

Antes de formular una recomendación o realizar cambios sustantivos, declarar en el informe o mensaje:

```text
REVISIÓN: <HEAD local, rama, remoto/PR observados o SIN ACCESO>
INVENTARIO: <N SHA verificados, digest, índice PASS/FAIL o NO EJECUTADO>
LEÍDOS SEMÁNTICAMENTE: <rutas y, si parciales, rangos o secciones>
NO LEÍDOS/NO ACCESIBLES: <rutas/material con consecuencias para la conclusión>
AUTORIDADES: <estado, ledger AB, metodología/versión, Atlas, logros>
ESTADO: <producto vs investigación, gates, pendientes, STOP, incertidumbre>
PROCEDENCIA: <hecho fuente, simulación sintética, QA, inferencia, propuesta>
NOVEDAD: <contra qué experimentos o defectos previos se comprobó>
ACCIÓN Y FALSADOR: <resultado que se exige, prueba que podría invalidarlo>
PUBLICACIÓN: <commit local/remoto/PR o cambio solo local, NO ASUMIDO>
```

**El informe de cobertura no convierte en leído nada no leído**. Un fallo en la consulta remota invalida afirmar sincronización, no invalida los contenidos locales observados. Un `git ls-files` íntegro no prueba la presencia de originales locales privados ni su condición jurídica.

## R5, privacidad, autorizaciones y límites innegociables

Hasta levantar R5 mediante evidencia y revisión humana del universo **all-received/admitted-first**, negativos/pendientes/censura, denominador independiente compatible, IDs asiento→caso→decisión, derechos por **recurso y uso** (incluidos términos vinculantes por mero acceso), dos vintages históricos auténticos y primera publicidad, **no ejecutar ni contar AB empírico confirmatorio**. No extrapolar un piloto de Canarias o SIAP, catálogo o simulación al conjunto de España. No predecir outcomes reservados antes de congelar A–J y código; no confundir primacía de una fuente con población exhaustiva. Proteger originales, JSONL derivados, personas identificables, credenciales y materiales de usuarios. No aceptar licencias/cookies/términos, contactar autores, desplegar, puntuar personas reales ni fusionar `main` por continuidad automática. Los ciclos no usados siguen disponibles; QA, guías e inventarios son **noncycle**.

## Mantenimiento del contexto y de los logros

Tras cada bloque, escribir **al principio** del handoff una síntesis vigente y fechada con enlaces a evidencia; no acumular un título histórico como si fuese la situación actual. Conservar el archivo profundo detrás, sin borrarlo. Actualizar `PROJECT_STATE` solo cuando cambia de verdad una autoridad/hito; actualizar la cola, pruebas y el índice si se añaden rutas. Aportar comandos/resultados y SHA cuando se publique.

El registro de logros es **dinámico pero no ornamental**: añadir cuando una capacidad futura tenga criterio falsable y no duplique otro premio; revisar obsolescencia por cambio de alcance, anotar reemplazos y retirar mediante `retired`/motivo y evento versionado, sin borrar ni reutilizar ID. Nunca subir un logro por el mero hecho de haber redactado este protocolo. Los logros solo se desbloquean con evidencia de su condición y prerrequisitos, verificador y evento; ni Atlas, ni contratos, ni CI cambian automáticamente los seis gates.

## Criterio de aceptación de este protocolo

Dos sesiones independientes deben poder: (a) resolver la rama realmente vigente sin leer solo `main`; (b) verificar cobertura íntegra de los archivos rastreados; (c) discriminar hash/inventario de lectura semántica; (d) recuperar el mismo estado científico, ledger y gates; (e) detectar un índice obsoleto, un archivo ancla ausente y/o una rama cambiada en adversariales; (f) señalar documentos no accesibles y no reclamar que el proyecto entero está en su ventana. Hasta observar ese relevo independiente, **el protocolo es instrumentación, no un logro completado**.
