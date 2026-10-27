# PFL · Campaña AB-H CONT40 · C31–C40 · 27/10/2026

**Permiso:** el usuario concedió diez nuevos ciclos AB-H y preguntó si la tarea de Codex podía esperar: **sí**. Se registraron **C31–C40, 10/10 expedientes A–J**, todos **AB-P** de ingeniería o validación del producto. Las tareas para Codex permanecen **pendientes**; no se ha invocado ni asumido ejecución alguna. Rama `research/pfl-codex-contributions-20261027`. [Ledger](CAMPAIGN_STATUS.json) · [Atlas 0026](../../ab_atlas/updates/0026-pfl-abh-cont40-c31-c40-20261027.json).

## Qué se ha ejecutado realmente

Sobre código Python/Node reconstruido localmente y contrastado mediante el SHA de blob Git del repositorio privado:

- **91/91 tests Python PASS** sobre módulos fuente que coinciden con **las versiones publicadas** en la rama, en 11,28 s. Incluyen los **58 tests verificados** del almacén privado de CONT30, más 33 pruebas focalizadas de progreso, simulación, normalización y grafo. **Algunos de los nuevos archivos de test permanecen sólo en el entorno local; el código probado sí coincide con los blobs publicados.**
- **9/9 tests Node PASS**, en ~0,06 s, contra `progress_model.mjs` y el test nuevo de validación compartida, **ambos archivos publicados** con SHA idéntico.
- **12/12 pruebas Python adicionales PASS** sobre una **modificación local de `forecast.py` que no se consiguió integrar en GitHub**. Las 12 se **excluyen** de los 91 tests de código publicado. Corrida conjunta de los 103 tests Python: **103 PASS / 0 FAIL (11,80 s)** en un árbol **mixto**, no checkout completo; 9 Node por separado.
- Logs, pruebas negativas iniciales, árbol sintético y parche pendiente están archivados en el contenedor de la conversación. No se ejecutaron todas las pruebas Python/JS del proyecto ni el verificador canónico del Atlas.

## Tabla de ciclos y estados de implementación

| Ciclo | Pregunta y contraste A–J | Antes / después (ejecución nativa) | Implementación |
|---|---|---|---|
| C31 AB-P | `progress_api.py` permitía `milestone.size=NaN`, generando `ok=True` y progreso no finito. | 5 PASS/1 FAIL → **6/6 PASS**, `math.isfinite`. | **Código y regresión en GitHub**. |
| C32 AB-P | JS marcaba `RELEASE_GATES_CLEARED_FOR_FURTHER_VALIDATION` con los seis hitos críticos **ausentes**. | 1 FAIL → PASS, más 9 tests compartidos en C34. | **Código en GitHub, integrado junto con C34**. Primer prerregistro local, GitHub anotado después por interrupción de escritura. |
| C33 AB-P | Auditoría diferencial de nueve entradas Python frente a Node: **7 discrepancias de aceptación** y una diferencia adicional de gates. | Matriz original 7 divergencias → **0** tras C34. | Investigación del contrato, no siete ciclos ni hallazgos independientes; prerregistro local y constancia posterior en GitHub. |
| C34 AB-P | Unificación de validadores de alcance: familia, ID, nombre, motivo, evidencia, tamaños, clase y gates omitidos. | **15 tests Python + 9 Node PASS**; recálculo independiente V4 **36,900000000000006%**, 9 líneas, 36 hitos. | **Ambos evaluadores y regresiones en GitHub**, hashes idénticos. |
| C35 AB-P | Volatilidad y Gini de la subasta sintética podían admitir parámetros no finitos o fuera de rango. | 3 PASS/6 FAIL → **9/9 PASS**. | **Código y test sintético publicados**; prerregistro local anterior a ejecución, registro Git posterior. |
| C36 AB-P | Auditor de eventos normalizados contaba como válidos un SHA no hexadecimal de 64 caracteres y personas duplicadas/no cadenas. | 1 PASS/1 FAIL → **2/2 PASS**. | **Código y test publicados**; contrato coherente con `PoliticalEvent`. No autentica originales oficiales. |
| C37 AB-P | Pérdida logarítmica Poisson admitía `NaN`, `Inf` y recuentos no enteros. | 1 PASS/4 FAIL → **5/5 PASS local**. | **Sólo parche local; GitHub NO actualizado** por bloqueo de escritura. |
| C38 AB-P | Tasa histórica sintética admitía exposiciones fraccionarias/bool y parámetros previos no finitos. | 1 PASS/6 FAIL → **7/7 PASS local**. | **Sólo parche local**, conjuntamente con C37; no atribuir corrección publicada. |
| C39 AB-P | Suavizado descriptivo de coincidencia de voto con `NaN/Inf` o `min_joint` no entero. | 2 PASS/5 FAIL → **7/7 PASS**. | **Código publicado**; regresión añadida localmente pero su subida a GitHub fue bloqueada. Sin inferencia causal/ideológica. |
| C40 AB-P | Contraste conjunto de módulos de almacén, progreso, subasta, normalización, previsión y grafo. | **91 Python + 9 Node** en código de la rama; **12 Python extra** en pronóstico parcheado local. | **Comprobación efectuada**; falta checkout completo. |

Todos los expedientes individuales `C31_RESULT.json` … `C40_RESULT.json` contienen **A–J**, con antecedentes, falsadores, pruebas, resultados, autocrítica, contrafactual y próximo paso. Los archivos originales de tres casos se registraron primero con prerregistro local anterior a la prueba y se trasladaron a GitHub posteriormente, sin fingir congelación previa en Git.

### Estados y límites

**V4 contractual 36,90%; CT2 identidad 29/100 ordinal; VSDS 1/3; N1/N2/N3 nuevos 0/0/0; lanzamiento 0/6 gates.** No se ha impulsado el porcentaje por aumentar tests, ni se han aprobado licencias individuales, firmas institucionales, identidades reales, puntuaciones de políticos o despliegue. Todo lo probado se alimentó de entradas sintéticas.

**Atlas append-only 0026:** `0026-PFL-ABH-CONT40-C31-C40-20261027` añade **10 operaciones `run.add`** a `0025`. Conteos **derivados**, no certificado Python canónico: **26 lotes, 63 nodos, 81 edges, 159 runs, 44 complaints, 328 operaciones**. El estado Python final, sus invariantes exactos y su SHA siguen sin validarse mediante `python ab_atlas/atlas_delta.py check`.

**R1–R5 / crítica:** las comparaciones fueron controles de software y contratos de datos, no inferencia sobre conducta parlamentaria. La secuencia es adaptativa y hay solapamiento entre pruebas: 91 no son 91 evidencias científicas independientes. Se conservaron todos los fallos iniciales de los ensayos red-green y las restricciones locales. El primer bloque de C31–C34 analizó una única familia de validación (se evitó inflar siete divergencias a siete ciclos); después se cambió instrumento a simulación, datos normalizados, predicción y red descriptiva. Un error de entrada no permite elevar el score político ni levantar gates. La mejora estadística real requerirá fuentes institucionales independientes.

**Próximo trabajo verificable sin Codex:** aplicar y repetir sobre GitHub el parche de `forecast.py` de C37–C38; subir la regresión numérica del grafo de C39; ejecutar pruebas de V4 con los ficheros históricos y comparaciones Python/JS completos. **Con Codex, cuando el usuario pueda:** checkout integral, test global y Atlas canónico 26 lotes; [incidencia #17](https://github.com/GalexY3/Metodologia-AB/issues/17) sigue abierta y es una solicitud, no ejecución.

**Permiso CONT40 agotado: 10/10.** Nueva campaña AB-H requerirá autorización expresa.
