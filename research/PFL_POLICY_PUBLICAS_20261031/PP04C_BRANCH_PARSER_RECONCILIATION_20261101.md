# PP04C · Reconciliación de parsers PAN/IAEN 2024 sin promoción R5

**1 de noviembre de 2026 · ingeniería documental NONCYCLE · revisión DRAFT.**
No se ha abierto, extraído, comparado ni redistribuido ningún PDF original en
este incremento. Todos los falsadores y controles ejecutados usan textos
**inventados**. Los datos individuales derivados anteriormente continúan fuera
de Git. No se ha aceptado ninguna condición de acceso nueva ni se ha hecho
un emparejamiento PAN↔IAEN a nivel de iniciativa.

## Selección frente a otras rutas

- **R5, nuevas entradas administrativas Madrid 300044 (R26):** las condiciones
  por mero acceso, la exhaustividad `all-received`, los vínculos entrada/salida
  y la primera publicación siguen sin acreditarse. No se reintentó el 403 ni
  se descargaron distribuciones. Se conserva `STOP_LOCAL_R5`.
- **Puente de derechos Python PR #16 ↔ warehouse JS PR #19:** la revisión
  estática independiente no halló un consumidor operativo nuevo que promueva
  derechos/`first_public_at` tras la reparación R25. Un import futuro es riesgo
  potencial, no un falsador material actual. **STOP** a abrir un duplicado.
- **PP04, reconciliación PR #11 ↔ PR #12:** existe una colisión concreta:
  ambas ramas añadieron `src/politics_fantasy/pan_iaen_original_frame.py` y
  `tests/test_pan_iaen_original_frame.py` con **distintas API**. Es una
  dependencia de integración reproducible, no un nuevo corpus científico.

## Testigo Git y procedencia

- PR #11 `ff3da7c95718528f8f67b1bc0ba8060255566306`, parser de bloques,
  importado por `scripts/pp04_extract_authorized_local_originals.py`.
- PR #12 `3fabecc800acb300f84c7c4710239847db1c4520`, parser de líneas y
  subpoblación `UNPLANNED`, sobre la que se construyó el checkout de integración.
- Base común inspeccionada: `0ca37662242e8a24c505f61f29e29855c833b5b6`.
- `git merge-tree <base> <head11> <head12>` (forma histórica de solo lectura)
  informó `added in both` para los dos paths anteriores. Esta salida demuestra
  conflicto de incorporación de rutas, **no** una evaluación científica de
  los 198 ítems ni mergeabilidad completa de todas las PR.

## Falsadores congelados antes de las reparaciones

| Caso | Resultado previo observado | Cambio limitado |
| --- | --- | --- |
| Dos API públicas necesarias, puente ausente, etiqueta `III. Desistidas` arrastrada como aprobada en PR #12 | `4 FAIL / 8 PASS`, con SHA inicial del módulo #12 `1b1e748680bade8705e7e4cd24950e1c56f354083086b892e041b1945949fbf2` y test nuevo `5bb5ceb1972bc337d20b46c26e0032570375b0ba0fd1ea1dd8a02d385ba0433d` | Reexportar API #11 conservando la de #12; rechazar encabezados romanos desconocidos antes de viñetas |
| «NO INCLUIDAS» dentro del título, no del encabezado; resultado privado dentro de *otro* repositorio Git | `2 FAIL / 11 PASS` después del port exacto del parser #11 (SHA `8c3916551a4aa28a964fe6716430ccbf5171a569e5d63258f4fef80f054ca13ca`); test `c1aae4f545dcdc71e42d48bea5ed65f1a2ffd5c958fe09c4253cdb578e43b12` | Clasificar únicamente las líneas del encabezado; rechazar cualquier ancestro `.git`, sea directorio o fichero de worktree |
| Etapa romana `III. Rechazadas` omitida en parser #11, heredando «Aprobadas» | `1 FAIL / 3 PASS` tras las primeras correcciones; SHA previo `ece8aaa5e8484e835b19802ad51ff94ca7b5b522ef20eb025ee0c4cf0bb7408e` | Clasificación fail-closed de cualquier encabezado romano no soportado |
| Los dos parsers admitían los mismos recuentos aunque faltase la subsección singular `4.22.1` | Falsador adversarial independiente reproducido: `1 FAIL / 6 PASS`, SHA del puente previo `60e7bae36ea72c9fa549af32d1484633b3b1aae960bccbfe5bc34d3ff9c4ec34`, test `15761f42cd9e6871aa36fe555efbf04fd9024de32ad1a5b99dc40a1f46c21a34` | Exigir explícitamente `4.22.1`, la lista de ministerios esperada y un recuento declarado de no previstas; ausencia o discrepancia → `FrameParseError` |
| Ambos parsers clasificaban `II. Pendientes de aprobación y Aprobadas` como solo pendientes y el comparador concedía acuerdo | `3 FAIL / 0 PASS` sobre el falsador nuevo; test SHA `885a10e81988681a7c6a15d9fa475cb02c5bf07dcaea825a0fd2446ea036180`; módulos antes de reparación: `8c4ea169593d188ca6871af9597f137b9762123be77c67d172e6ddd9ce2634a4` y `8d6c028a8d97bae4a194b55507a372c0726e51de8973804cb4c38546d7264ec6` | Lectura completa del estado romano, normalización de acentos y coincidencia exacta; cualquier categoría mixta o no reconocida → error |
| Una nota editorial precedida por guion se contaba como segunda norma `NO INCLUIDA`; el segundo parser no clasificaba sus viñetas | `2 FAIL / 0 PASS`; test SHA `dc0d949cbc91dc8fafaad07bf14c624573244d26dcaea825a0fd2446ea036180` | Lista conservadora de prefijos de instrumentos; viñetas sin tipología léxica reconocida → cuarentena, no añadir entradas ni declarar completitud |

El primer fallo de colección sin `PYTHONPATH=src` se debió exclusivamente a
configuración del entorno Windows, **no** se contabiliza como falsador.
Los resultados arriba sí fueron ejecutados con `PYTHONPATH` apuntando al
`src` del checkout de integración.

## Arquitectura reconciliada y límites

Se preserva el parser de líneas de PR #12 en
`pan_iaen_original_frame.py` con `FrameParseError`, las tres funciones
originales y sus claves source-local. El código de PR #11 se incorpora,
con las reparaciones descritas, en `pan_iaen_source_block_parser.py`;
las funciones y los SHA declarados se reexportan desde el módulo tradicional
para conservar `scripts/pp04_extract_authorized_local_originals.py` y
las pruebas originales de #11. El script sigue siendo **local/offGit**;
su `--help` se ejecutó, pero no `--private-dir`, ni `--out-dir` real.

El nuevo `audit_pp04_dual_parsers` compara dos interpretaciones del **mismo
texto acotado**, exigiendo coincidencia de recuentos PAN, entradas IAEN
planificadas, aprobadas y pendientes, más categorías por ministerio y estados.
El llamador debe declarar expresamente `expected_planned_sections` y
`expected_unplanned_count`; estos valores se contrastan de manera interna,
pero **no** constituyen un denominador independiente del documento.
La anomalía `4.22.1` debe estar presente, se evalúa por encabezado y permanece fuera de las
`PLANNED`. Si cualquiera rechaza las páginas o discrepan categorías,
se lanza `FrameParseError` sin imprimir fragmentos. El informe de acuerdo
solo devuelve métricas agregadas y flags negativos.

**Limitación adversarial:** dos parsers que usan el mismo texto pueden
coincidir en un mismo error. La doble clasificación de un encabezado
contradictorio y la confusión entre nota editorial y norma demostraron
que una coincidencia no acredita precisión documental. La lista de
prefijos jurídicos se utiliza como **rechazo conservador**, no como
clasificación completa de actos oficiales; nuevas grafías, códigos,
instrumentos u OCR ambiguos requieren inspección manual y adaptación
documentada antes de utilizar el corpus. Los conteos esperados introducidos
por el llamador tampoco son testigos externos independientes.

**La concordancia entre dos parsers del mismo documento no es independencia
de fuente ni crosswalk de iniciativas.** Los hashes de originales históricos
indicados por los parsers no acreditan por sí mismos derechos, primera
publicación, revisión del índice editorial o denominador externo.
No se ha vuelto a inspeccionar la población oficial de 198 entradas PAN,
198 IAEN planificadas (89 aprobadas/109 pendientes) y 259 no planificadas
en esta sesión; son cifras de las PR históricas, no nuevos resultados.
Los estados del informe de 2025 no se convierten en predictores de 2024.
Los 109 pendientes no se redistribuyen en categorías finas sin fuente.

## Validación del incremento

Ejecutado localmente en Windows con `PYTHONPATH=src`:

```powershell
python -m pytest -q tests/test_pp04_ambiguous_status_falsifiers.py tests/test_pp04_unplanned_editorial_bullet_falsifiers.py tests/test_pp04_dual_parser_compatibility.py tests/test_pp04_block_parser_edge_falsifiers.py tests/test_pp04_source_block_parser_original_tests.py tests/test_pan_iaen_original_frame.py tests/test_pan2024_source_local_cohort.py tests/test_pan_iaen_manifest_gate.py tests/test_pan_iaen_originals_local_cli.py tests/test_pan_iaen_preaccess_gate.py tests/test_source_gate_boundaries.py tests/test_synthetic_policy_trace.py
```

**104/104 PASS** en la regresión amplia final, sin originales, tras las nuevas
pruebas negativas de encabezados contradictorios y notas editoriales.
`compileall` de los módulos y el CLI: PASS; `git diff --check`: PASS.
SHA-256 POSTPATCH de `pan_iaen_original_frame.py`:
`0e493f0d87c815315ce8b511cdefeb4ae45c62e7b748dd45aea027306a3ad7ed`;
`pan_iaen_source_block_parser.py`:
`952050883a91b9faa6ddba2b8dd0b6c02a8e70a0f4f1a9c9bfbbc72f931b6fe1`;
`pan_iaen_cross_parser_audit.py`:
`7439974ba9889b9861e0433ae44a42fbfdea26a390b8866c4a1ebaa90669acf0`.
No hay prueba de integración sobre PDFs originales, validación académica,
QA Linux ni prueba de una publicación R5-admisible.

## Integración recomendada, no ejecutada

Revisar esta rama **encima de PR #12**, que depende de PR #10, preservando
el parser de líneas y su subpoblación `UNPLANNED`. La funcionalidad de
PR #11 está portada con pruebas independientes; evitar fusionar después
PR #11 sin reconciliar su `add/add` (o duplicaría/machacaría módulos).
Mantener ambas PR históricas DRAFT hasta que la revisión humana decida
integrarlas o sustituirlas. No se ha fusionado ninguna rama en `main`.

**R5 = `STOP` · 0 AB científicos nuevos · 0 originales/casos/PII consultados
· 0 permisos nuevos · 0 gates de release superados.**
