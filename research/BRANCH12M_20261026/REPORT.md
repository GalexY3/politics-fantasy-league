# Politics Fantasy League — BR12M, cierre de doce ciclos AB 3.2.1 BRANCHING

**Cierre:** 26/10/2026. Se concedieron 12 ciclos; se han realizado comprobaciones concretas y publicado 12 fichas A–J. **9 aceptaciones técnicas/documentales y 3 decisiones STOP_R5** (no cierre empírico positivo): las dos rutas de fuentes institucionales Congreso/Interior y la ausencia de identidad jurídica real consolidada.

## 1. Resultado principal

Se comprobó el [GitHub Actions 40258776701](https://github.com/GalexY3/Metodologia-AB/actions/runs/40258776701) sobre un checkout Git real, con **dos jobs concluidos SUCCESS**:
- `source-and-app-checks`: siete suites Node con **91 tests**, 91 PASS; Python pytest con **50 tests**, 50 PASS (incluye HTTP loopback y seguridad, progreso y CLI); cotejo del dataset secundario 2023 con BOE previamente transcrito y revisión Git pin.
- `original-source-download`: cuatro solicitudes HTTPS oficiales reales: **una captura original válida** y tres bloqueos. Conservó un artefacto privado interno temporal, comparó SHA-256 releyendo los bytes y extrajo/conciliò **52×6=312** cifras del PDF oficial.

**Las correcciones fueron empíricamente guiadas:** test de captura con una fixture inferior al mínimo de bytes, test con expectativa incorrecta del contenido, una expectativa Python errónea de 35,525% y ausencia inicial de `pdftotext` en el runner. Se observaron fallos nativos, se repararon y el checkout final pasó la batería. La fase posterior de pruebas se basa en un log REAL, no en inferencias de lectura del código.

## 2. Original oficial realmente capturado

| Campo | Hecho verificado |
|---|---|
| Publicador HTTPS | `www.boe.es`, hostname exacto |
| Fuente | [BOE-A-2023-18907](https://www.boe.es/boe/dias/2023/09/01/pdfs/BOE-A-2023-18907.pdf), JEC resultados 23/07/2023 |
| Bytes originales | 1.915.000 |
| SHA-256 | `f2146cfbf00d2b6eb6f8dd0dcdebc1e10298019589b2254e244e0ebc513d2f8a` |
| Formato | PDF válido con cabecera `%PDF-` y final `%%EOF` |
| Reproducibilidad numérica | Página 2 extraída con `pdftotext -layout` |
| Reconciliación con registro anterior | 52 circunscripciones × 6 magnitudes = **312 celdas**, sin discrepancias |
| Custodia | GitHub Actions privado, artefacto `12623134883`, expira **29/10/2026 02:22 UTC** |
| Límite | Solo cuadro I; no se validan aquí identidad/afiliación ni personas reales; derechos derivados aún sin adjudicar |

**No confundir** comprobación de 312 agregados con verificación de la totalidad del BOE o de la población política. Los originales del [Registro de Partidos](https://datos.gob.es/es/aplicaciones/consulta-del-registro-de-partidos-politicos) siguen sin capturarse.

**Intentos negativos preservados:** dos JSON históricos del Congreso `20260810` devolvieron HTTP 404; `Elecciones-Congreso.xlsx` del Ministerio devolvió fallo de cadena de certificados CA en ese runtime. **No se desactivó TLS**, ni se sustituyeron esas fuentes por un tercero haciéndolo pasar por original. Esos fallos están en [OFFICIAL_CAPTURE.json](OFFICIAL_CAPTURE.json).

Reproducción: [captura y verificador HTTPS](../../scripts/capture_official_sources.py), [auditor de tabla de PDF original](../../scripts/verify_boe_table_pdf.py), [tests de corrupción de fuente](../../tests/test_verify_boe_table_pdf.py). El checksum de la copia original que se obtenga posteriormente debe validarse contra el observado; si cambia se debe abrir investigación de revisión.

## 3. Actualización de la métrica de avance

Se incorpora **revisión 2 al mismo alcance PFL-V1-20261026**, sin añadir tareas ni modificar ponderaciones. Se mantienen las 9 sublíneas y 36 hitos. Sólo se modificaron los niveles respaldados por evidencia de esta campaña:
- `src.catalog`: 3→4, por obtención HTTPS del original BOE, SHA-256 y conciliación numérica automática.
- `qa.endtoend`: 1→2, por la ejecución nativa confirmada de tests Node/Python/HTTP, **sin subir más** porque no hay pruebas navegador E2E ni seguridad de hosting público.

| Sublínea | Antes V1 | Ahora revisión 2 | Peso |
|---|---:|---:|---:|
| Fuentes y datos | 38,75% | **45,00%** | 18% |
| Identidades y coaliciones | 40,00% | 40,00% | 12% |
| Acontecimientos | 32,50% | 32,50% | 10% |
| Investigación y predicción | 27,50% | 27,50% | 14% |
| Motor del juego | 45,00% | 45,00% | 16% |
| Interfaz | 27,50% | 27,50% | 10% |
| Seguridad | 20,00% | 20,00% | 8% |
| QA y reproducibilidad | 32,50% | **40,00%** | 8% |
| Operación y lanzamiento | 17,50% | 17,50% | 4% |
| **Ponderado global** | **33,725%** | **35,450%** | **100%** |

**Cambio global +1,725 pp, efecto trabajo +1,725 pp, efecto scope 0 pp**. Se conserva inmutable la [V1](../../product/progress_snapshot_v1_20261026.json); ahora la [V2](../../product/progress_snapshot_v2_20261026.json) es la vigente. La versión hipotética de cobertura municipal extensiva sigue siendo solo ejemplo no adoptado.

**Seis bloqueos de lanzamiento persisten:** originales de registro de partidos y candidaturas, reconciliación personal, atribución de eventos a personas con historia temporal, autenticación/autorización multiusuario, E2E con navegador y despliegue seguro. El juego sigue en prototipo local con personas ficticias; **no habilitar scoring real**. Los porcentajes expresan madurez relativa de requisitos, no probabilidad, tiempo ni porcentaje de España cubierta.

## 4. Contratos AB, A–J y prioridades

[PREREG](PREREG.json) conserva el contrato previo a las nuevas solicitudes originales, salvo C01 preexpuesto de historial. [RESULTS](RESULTS.json) contiene adjudicaciones individuales, [LEDGER](LEDGER.json) las doce fichas A–J completas y [PRIORS_DELTA](PRIORS_DELTA.md) incluye seis novedades con evidencia a favor/en contra y falsador.

| Ciclos | Alcance J |
|---|---|
| C01–C04 | GitHub Actions y tests nativos validados, fallos detectados y reparados |
| C05–C06 | STOP_R5: Congress JSON 404, Interior XLSX TLS |
| C07 | Descarga original BOE, checksum y 312 cifras contrastadas automáticamente |
| C08 | STOP_R5: identidad jurídica/personal original sigue sin consolidar |
| C09 | Controles adversariales de fuente/PDF, CI nativo |
| C10 | Progreso V2 35,45% sin expansión de scope |
| C11 | Workflow completo success, resultado auditable |
| C12 | Cierre AB y acumulación de priors, nuevos experimentos científicos = 0 |

**VSDS 1/3**, **CT2 multiactor 20/100** y **CT2 predictiva parlamentaria 24/100** se mantienen; **N1/N2/N3 nuevos=0**. Una verificación original de recuentos electorales no identifica influencia ni predice decisiones individuales. Haber ejecutado 141 tests no implica realizar 141 estudios.

## 5. Próximo contrato sugerido — no autorizado

La siguiente campaña solo sería valiosa si abordase una nueva fuente **original oficial de entidades con y sin escaños**, identidad jurídica, cambios temporales y mecanismos de carrera política; o probase con navegador los aspectos esenciales de producto y autenticación. Solicitar **8 ciclos con BRANCHING**, focalizados en (i) hallar y certificar registro RPP o descarga alternativa Interior con TLS confiable, (ii) normalizar una primera cohorte de candidaturas/cargos con originales y conflictos, (iii) ampliar el atlas más allá de generales 2023 y (iv) comprobar un piloto real de navegación y seguridad. Aplicar STOP_R5 si se agotan vías justificadas; evitar 8 pruebas más del mismo PDF.

**SOLICITO BRANCHING 8 CICLOS**
