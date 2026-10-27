# Politics Fantasy · BRANCHING20C · Investigación externa C13–C18

**Fecha de trabajo:** 27/10/2026. **Rama:** `research/pfl-sources-reconcile-20261027`. **Motivación:** buscar evidencia nueva más allá del ZIP original y no tratar el bloqueo de `first_public_at` como imposibilidad universal. Se exploraron fuentes primarias adicionales y se obtuvo evidencia discriminante de disponibilidad documental acotada y de enlaces biográficos entre legislaturas.

**Autorización:** nueva concesión de 20 ciclos. C01–C12 anteriores consumidos; C13–C18 son **6 ciclos nuevos**. **18/20 consumidos, 2 reservados**, sin autorización nueva necesaria. [Ledger](CAMPAIGN_RESUME_C13_C18.json). Prerregistro previo a la prueba focalizada, pero C13 y C17 declaran expresamente fuentes y hechos detectados antes del prerregistro: exploratorio, no ciego. [Priors acumulativos](PRIORS_DELTA_C13_C18.json).

## C13 · BOE 2023: original firmado, obligación de acceso y evidencia agregada de puntualidad

[Prerregistro](C13_PREREG.json) · [resultado](C13_RESULT.json).

El [Real Decreto 181/2008, artículo 11.2](https://www.boe.es/buscar/act.php?id=BOE-A-2008-2389) establece que la edición electrónica oficial será accesible en el día que figura en cabecera salvo imposibilidad por circunstancias extraordinarias técnicas; su art.12 dispone firma electrónica avanzada.

La Agencia Estatal BOE, en su [Informe General de Actividad 2023](https://www.boe.es/organismo/documentos/informe_actividad_aeboe_2023.pdf), también resumido en [BOE-A-2024-16378](https://www.boe.es/diario_boe/txt.php?id=BOE-A-2024-16378), declaró **312/312 números ordinarios de 2023 publicados antes de las 08:00** del día asignado, indicador 100 %. Hubo además un número extraordinario en diciembre no aplicable a los documentos seleccionados.

Los **dos PDF originales extraídos del ZIP privado** se examinaron con `pdfsig`, preservando su SHA-256:
- **BOE-A-2023-15066** (candidaturas): ejemplar 27/06/2023, SHA-256 `d1c179fcfab9889df272753ad3d44513f86cec703805219834b7d048ef0eda20`, firma criptográfica `Signature is Valid` por `DIARIOS OFICIALES` de Agencia Estatal BOE, firmada nominalmente 26/06/2023 a las 18:25:33 UTC.
- **BOE-A-2023-18907** (resultados/proclamación): ejemplar 01/09/2023, SHA-256 `f2146cfbf00d2b6eb6f8dd0dcdebc1e10298019589b2254e244e0ebc513d2f8a`, firma `Signature is Valid` por mismo emisor, firmada nominalmente 31/08/2023 a las 17:04:45 UTC.

**Alcance de la verificación:** firma con SHA-1 y certificado que actualmente aparece caducado; no se ha reconstruido íntegramente la cadena de confianza histórica ni existe sello de publicación CDN firmado de cada archivo. **Momento de firma ≠ momento de publicación pública.**

**Resultado temporal:** para **análisis históricos con cortes diarios**, bajo la declaración agregada del editor y el marco normativo (no como observación directa por fichero), cabe usar **disponible a partir de la medianoche siguiente al día del ejemplar**. Así, los dos cortes documentales condicionales son 28/06/2023 00:00 CEST y 02/09/2023 00:00 CEST. `first_public_at_exact=null`. Esta política solo se aplica a los **BOE ordinarios de 2023 concretos y autenticados en origen**, no a fuentes del Senado, Congreso ni Cortes autonómicas, ni implica que esos hechos fueran desconocidos antes en otros medios. No abre por sí sola backtests personales ni gates de lanzamiento.

## C14 · Regla de disponibilidad documental en código (AB-P)

[Prerregistro](C14_PREREG.json) · [resultado](C14_RESULT.json) · [módulo](../../src/politics_fantasy/boe_2023_publication_bound.py) · [tests](../../tests/test_boe_2023_publication_bound.py).

Control puro con lista inmutable de dos documentos firmados, fechas de edición y hash esperado. Rechaza cortes anteriores al día siguiente, timestamps sin zona horaria y IDs fuera del catálogo; informa `available_under_assumption`, **NO** `first_public_at` ni habilitación de personas reales. **10/10 pruebas Python locales** correctas, sin tests HTTP ni certificación de recibo de publicación web.

## C15 · Todos los nombres repetidos ≥35 años en Interior: tres controles positivos

[Prerregistro](C15_PREREG.json) · [resultado](C15_RESULT.json).

En el XLSX oficial de Interior (5.600 electos en 16 elecciones) se identificaron **exactamente tres** etiquetas completas normalizadas cuyo primer y último registro distaban al menos 35 años. Se verificaron todas contra biografías originales del Congreso y, en un caso, Moncloa: **Luis Planas Puchades** (1982–2023), **José Manuel García-Margallo Marfil** (1977–2016), **Ignacio Gil Lázaro** (1986–2023). Las biografías enlazan expresamente legislaturas y datos del cargo, aun con siglas, provincias y códigos parlamentarios diferentes. Resultado: **3 continuidades personales positivas acotadas**, no tres identificadores estatales inmutables, no evidencia de cómo comprobar pertenencia `as_of` y **0 homónimos exactos negativos**.

## C16 · Cambio de provincia y 20–34 años de separación: ocho controles positivos más

[Prerregistro](C16_PREREG.json) · [resultado](C16_RESULT.json).

Se fijó una muestra de los **primeros ocho** entre **17 nombres** del XLSX que se repiten a lo largo de 20–34 años y aparecen asociados a provincias distintas, ordenados por amplitud temporal. Los **8/8** se vinculan mediante biografías históricas del Congreso: José María Benegas Haddad, Mariano Rajoy Brey, José Bono Martínez, Josep Antoni Duran i Lleida, Gabriel Cisneros Laborda, Cristina Narbona Ruiz, Ramón Aguirre Rodríguez y Francisco Miguel Fernández Marugán. Constituyen evidencia de **identidad positiva documental**, no muestreo aleatorio ni una tasa de precisión poblacional. No se ha certificado ningún caso de **dos personas distintas con nombre completo idéntico**. La exploración encontró una discrepancia de biografía adicional, investigada en C17.

## C17 · Contraejemplo a equivalencia rígida por fecha de nacimiento

[Prerregistro](C17_PREREG.json) · [resultado](C17_RESULT.json).

**Cristina Narbona Ruiz:** la [Referencia del Consejo de Ministros, La Moncloa, 30/04/2008](https://www.lamoncloa.gob.es/consejodeministros/referencias/Paginas/2008/refc20080430.aspx) y una [referencia 28/12/2012](https://www.lamoncloa.gob.es/consejodeministros/referencias/paginas/2012/refc20121228.aspx) indican nacimiento **21/07/1951**. El [Congreso XV](https://www.congreso.es/es/busqueda-de-diputados?_diputadomodule_mostrarFicha=true&codParlamentario=271&idLegislatura=XV) y las [biografías publicadas por PSOE en 2017](https://www.psoe.es/media-content/2017/06/BIOGRAFIAS.-CEF-39-CONGRESO-OK.pdf) y [2024](https://www.psoe.es/media-content/2024/12/011224-BIOGRAF%C3%8DAS-41-CONGRESO-1.pdf) indican **29/07/1951**. Ambas trayectorias enumeran el mismo conjunto de cargos (diputada, ministerio de Medio Ambiente, embajada OCDE, etc.).

**Hallazgo lógico:** exigir igualdad exacta de fecha de nacimiento como condición necesaria de identidad **dividiría erróneamente una persona documentada como continua**. Conservar las dos afirmaciones y editor, no elegir silenciosamente una “fecha verdadera” por mayoría ni convertir la divergencia en prueba de homónimo. Las dos ediciones de cada mismo editor posiblemente comparten linaje; el conflicto es entre familias editoriales, no cuatro mediciones independientes. El registro civil u otra fuente primaria jurídica no se ha revisado; la fecha correcta sigue **sin adjudicar**. Los datos referidos son biográficos públicos y no se publican identificadores privados.

## C18 · Implementación multifuente del conflicto (AB-P)

[Prerregistro](C18_PREREG.json) · [resultado](C18_RESULT.json) · [módulo](../../src/politics_fantasy/identity_field_conflicts.py) · [pruebas](../../tests/test_identity_field_conflicts.py).

`audit_birth_assertions` conserva las cinco afirmaciones documentales en **3 linajes editoriales (Gobierno, Congreso, PSOE)** y 2 fechas incompatibles. Rechaza fechas imposibles, schema inválido y referencias duplicadas; es invariante al orden y nunca rellena `first_public_at` ni emite `SAME_PERSON`/`DIFFERENT_PERSON` automáticos o scoring político. **11/11 unittest locales PASS**, previo commit de fuente y tests; sin HTTP/E2E ni firma independiente de editor en tiempo real.

## Resultado transversal y decisión R5

**AB-R:** dos clases de aporte nuevo: (1) evidencia institucional adicional permite una **cota documental condicional de disponibilidad por día** para dos BOE ordinarios de 2023; (2) **once continuidades históricas positivas** y **una contradicción oficial real de atributo DOB** desacreditan reglas de enlace ingenuas. No se acredita un homónimo exacto negativo ni una tasa poblacional de error, ni `first_public_at` exacto.

**AB-P:** los prototipos nuevos de fuente disponible y conflicto biográfico han pasado 21 tests locales en total; no están integrados en el servicio HTTP ni validan como reales las afirmaciones del usuario. El mecanismo de identidad y los gates siguen bloqueados.

**Métricas heredadas:** PFL-V1 rev.3 36,35 % contractual, CT2 identidad 29/100 ordinal, VSDS 1/3; N1/N2/N3 científicos nuevos 0/0/0 (no convertir descubrimientos documentales en resultados teóricos confirmatorios); gates críticos aprobados 0/6. No se han lanzado GitHub Actions y los originales privados siguen fuera de Git.

**Concesión:** C01–C18 utilizados de BRANCHING20C, **18/20; 2 plazas conservadas**, no precisa permiso nuevo. R5 impide consumirlas solo para repetir nombres y fechas ya explorados. Próximos contrastes con potencial discriminante: archivos históricos versionados de Congreso/Senado con evidencia independiente `first_public_at`, un homónimo de nombre y apellidos completos **certificado como dos personas** por dos fuentes institucionales, y pruebas de integración de la registradora de evidencias en un checkout completo con el validador Atlas oficial.

Cualquier nuevo dato externo se incorporará conservando procedencia, incertidumbre y evidencia negativa en [`PRIORS_DELTA_C13_C18.json`](PRIORS_DELTA_C13_C18.json). Mantener la autorización para ejecutar ciclos sin solicitar otro bloque si la evidencia cambia.
