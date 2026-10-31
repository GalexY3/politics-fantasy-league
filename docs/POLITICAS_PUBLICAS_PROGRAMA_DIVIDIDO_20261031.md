# PFL · Programa de políticas públicas españolas por entregables verificables

**Fecha de decisión operativa:** 31-10-2026. **Ámbito:** primer piloto sobre políticas públicas españolas reales; no sustituye el universo multinivel de PFL. **Estado:** planificación ejecutable y auditoría documental previa a datos, `NONCYCLE`, `STOP_R5`. **No** es prerregistro A–J confirmatorio, estudio de resultados, permiso de uso de fuentes ni TFM cerrado.

## Continuidad y no duplicación

Base local protegida `research/pfl-system20-process-corpus-gates-20261031` @ `8df788007553c05890be08b962ffc24349ee1a6a`, idéntica a remoto al preflight. Rama derivada ya existente `research/pfl-policy-trace-scientific-core-20261031` @ `1e14d9e986cba2296450af6955a0763b5650e994` contiene `synthetic_policy_trace.py`, `synthetic_mechanism_discrimination.py` y sus pruebas. **Reutilizar** esos instrumentos; no repetirlos ni contabilizarlos como hallazgos científicos. Esta propuesta se desarrolla en checkout independiente y no modifica la base protegida ni `main`.

R12 ya estudió *agenda normativa AGE* y sus falsos denominadores (`docs/R12_IDENTIFICACION_NORMAS_Y_CONTROL_ADMINISTRATIVO_20261031.md`); R11/R18 ya aparcaron PLACSP y BDNS. Aquí **no** se presenta PAN ni BOE como fuente nueva. La aportación focal de este bloque es especificar el par *edición de plan / informe anual posterior*, su año correcto, su composición mixta y una ruta de tareas y admisión auditable.

## Alcance teórico

Una **política pública** no equivale automáticamente a una ley, una convocatoria, una decisión, un pago o un indicador. La unidad analítica principal futura será una intervención pública identificable, con instrumentos, instituciones y fases **observadas** y enlaces documentales N:M. Para el piloto se permite escoger una unidad más estrecha —**iniciativa normativa prevista en una edición del Plan Anual Normativo (PAN) estatal**— sin presentarla como censo de políticas españolas, de actividad legislativa total o de procedimientos iniciados.

La cadena `agenda/compromiso → formulación → decisión → norma → recursos → implementación → resultados/evaluación` es una ontología de enlaces documentales opcionales, no una sucesión universal y mucho menos una cadena causal confirmada. Los objetos poseen identidad y reloj propios. La existencia de referencias entre documentos no acredita atribución de efectos.

## Paquetes y dependencias (orden de ejecución, no cuota AB)

| ID | Producto verificable | Criterio de aceptación | Dependencia | Estado 31/10 |
| --- | --- | --- | --- | --- |
| **PP-01** | Reconciliación de PFL, R12–R22 y rama `synthetic_policy_trace`; inventario de marcos españoles | SHA local/remoto, negativos previos citados y ninguna doble cuenta | — | **COMPLETADO como preflight** |
| **PP-02** | Matriz de fuentes y grano: PAN, IAEN, BOE; alternativas Congreso/PLACSP/BDNS | URL oficial, año correcto, etapa, población, derechos por distribución, negativos, fecha/vintage y falsador; sin abrir outcomes | PP-01 | **DOCUMENTADO; acceso bloqueado por condiciones** |
| **PP-03** | Decisión de derechos y adquisición de un par de documentos originales, conservados fuera de Git | Permisos específicos aprobados antes del acceso; HTTP/bytes/SHA/edición/fechas; no cookies/terms automatizados | PP-02 + decisión humana de derechos | **BLOQUEADO** |
| **PP-04** | Diccionario de iniciativas previstas y correspondencia `plan_item → informe_item` | Población de todas las líneas del plan delimitado, identificadores estables o vínculos explícitos, no emparejamiento por título, estado UNKNOWN si no hay enlace, auditoría de cobertura | PP-03 | **PENDIENTE** |
| **PP-05** | Grafo temporal normativo y enlaces de norma aprobada | Versiones exactas, `event_on`, `first_public_at` o intervalo demostrado, `captured_at`, referencias explícitas PAN/IAEN/BOE; casuística N:M | PP-04 + derechos BOE | **PENDIENTE** |
| **PP-06** | Diseño científico preregistrado de una población/estimando concreto | A–J, B0/B1/B2/M3 competentes, marco de negativos/pendientes/censura, holdout y código SHA remoto **antes** de consultar outcomes | PP-04, PP-05 y R5 | **STOP_R5** |
| **PP-07** | Contraste empírico español + auditoría adversarial | Ejecución original, incertidumbre, métricas calibradas, refutación registrada, réplica independiente y límites; no contar tests como sociología | PP-06 | **NO INICIADO** |
| **PP-08** | Observatorio documental y conexión con otras políticas/instrumentos | Consulta histórica sólo para datos con derechos/tiempo acreditados; distinguir hechos/inferencias/simulaciones; sin puntuación individual ni despliegue automático | PP-05 y revisión producto | **PENDIENTE** |

No convertir PP-01/02 ni la escritura de documentos, QA sintética o informes de bloqueo en ciclos AB-R. Mantener producto AB-P en hito propio; no consumir saldo SYSTEM20 o las autorizaciones independientes por planificación.

## Tres rutas materiales y qué falsaría cada una

**R-A · Agenda normativa AGE (candidata prioritaria solo para piloto).** Unidad `edición PAN × ítem previsto × ejercicio`. Riesgo: el PAN lista previsiones, no toda iniciativa presentada. El informe anual posterior contiene también actuaciones **no previstas** y evaluaciones plurianuales. Ninguna entrada del informe debe presumirse pareja del PAN ni interpretarse su ausencia como fracaso. Falsador: falta de identificación por ítem, revisión no archivada, denominador de plan no reconstruible o indisponibilidad de negativos/pendientes.

**R-B · Procedimiento de elaboración/tramitación (alternativa aparcada R12/R18).** Unidad `expediente × familia homogénea × régimen`. La existencia de BOE final no enumera todos los intentos; proyectos, proposiciones y consultas no son equivalentes. Falsador: casos admitidos o presentados omitidos, sin registro preselección/estado terminal o sin primera publicación demostrada. Reabrir solo con un testigo original **nuevo** de cobertura o derecho, no repetir HTTP403/404.

**R-C · Instrumentos de implementación y gasto (alternativa aparcada R11/R18).** Unidad definida por **convocatoria**, **solicitud**, **concesión**, **licitación** o **contrato**, jamás intercambiables. PLACSP y BDNS no dan por sí solos el universo de necesidades públicas ni el impacto de una política. Falsador: extractos selectivos, duplicación de revisiones, convocatorias sin registro de solicitantes, condiciones legales no autorizadas, vintages no comparables. Reabrir con padrón independiente del grano elegido y derechos propios.

## Regla de los años: atención a un emparejamiento engañoso

**La Ley 50/1997, art. 28, y el RD 286/2017, art. 4, establecen que el Informe Anual de Evaluación Normativa del año `t+1` analiza el cumplimiento del PAN del año `t`**, además de iniciativas no incluidas en el plan y evaluaciones con objetivos plurianuales. Por tanto, **no** unir por defecto `PAN-2025` a `IAEN-2025` como plan e informe del mismo ejercicio. El candidato jurídico de contraste es `PAN-2024 ↔ IAEN-2025`; antes de utilizarlo debe verificarse que la **edición exacta de ambos originales** satisface esa relación y qué secciones corresponden a cada universo. Las páginas oficiales 2024 y 2025 enlazan informes de su año nominal, no identificadores de iniciativas individuales verificadas. No se ha abierto ni analizado ningún PDF original en esta sesión.

**Cortes temporales:** año en título de PAN, aprobación del plan, periodo planificado, año del informe, fecha del acto, publicación pública, adquisición y versión son variables separadas. Una fecha de actualización web o encabezamiento no acredita disponibilidad de cada ítem desde la fecha del acto. No utilizar el IAEN o las consolidaciones BOE para generar características retrospectivas de un pronóstico anterior.

## Gate previo a cualquier outcome

Registrar en `research/PFL_POLICY_PUBLICAS_20261031/SOURCE_DECISION_GATE.json` sólo metadatos de páginas y normas oficiales, **sin importar ni leer PDFs, textos completos de normas como outcomes, filas o identificadores personales**. Antes de adquirir originales o ejecutar una comparación empírica deben constar derechos por activo/uso, aprobación humana cuando las condiciones vinculen por uso, formato y versión, unidad exacta y cobertura/denominador, incidencias y versiones históricas, positivos/negativos/pendientes, ID y enlaces verificables, preregistro A–J y código remoto congelado. Si cualquiera falla, salida `BLOCKED` o `PARKED` con condición explícita de reapertura; no rellenar resultados con estimaciones inventadas.

## Fuentes documentales (metadatos públicos, no outcome)

- Planes AGE: <https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual>; páginas [2024](https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2024) y [2025](https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2025).
- Régimen: [Ley 50/1997, artículos 25 y 28](https://www.boe.es/buscar/act.php?id=BOE-A-1997-25336); [RD 286/2017, artículo 4](https://boe.es/buscar/act.php?id=BOE-A-2017-3415).
- Aviso de reutilización del Portal de Transparencia: <https://transparencia.gob.es/utilidades/aviso-legal/reutilizacion>, indica condiciones generales por el mero uso; aquí **no** se aceptan en nombre del usuario.
- BOE ELI y documentación de su API de legislación consolidada: <https://boe.es/legislacion/eli.php> y <https://www.boe.es/datosabiertos/faq/consolidada.php>. El propio acceso de reutilización requiere revisar condiciones y el texto consolidado es informativo, no sustituye acto publicado.

**Publicación:** este archivo no acredita que su rama se haya subido ni que una revisión de terceros lo haya aceptado; registrar SHA y estado Git tras validación. **Siguiente acción informativamente útil:** evaluar la autorización de reutilización y la correspondencia exacta PAN-2024/IAEN-2025, con una nueva pieza documental legítima y sin reanalizar resultados ya expuestos; si no hay camino legal/temporal, pivotar a una unidad delimitada sin fabricar otra campaña.
