# Politics Fantasy League · AB-H ORIGINALS5 — Informe final (28/10/2026)

**CERRADA: 5/5 ciclos A–J válidos acotados (C01–C05), 0 inválidos, 0 de planificación, 0 pendientes.** Los cinco AB-R son documentales/retrospectivos y contienen fuentes oficiales y cálculo reproducible. Rama `research/pfl-abh5-originals-20261028` nacida del HEAD `4962376a8d84af9d0ca36a27bd80af12348c99e4` de `research/pfl-abh5-institutional-20261028`. No hay ejecución de ChatRelay, merge a `main`, CI costosa ni ranking de personas. Ciclos de campañas anteriores no se han vuelto a contabilizar.

## A. Marcadores

| Indicador | Inicio | Cierre | Observación |
|---|---:|---:|---|
| Plazas AB-H | 5 nuevas | **5/5 usadas** | C01–C05: 5 AB-R, 0 inválidos y 0 planificación |
| CT2, rama identidad | 29/100 | **29/100** | Ordinal, no probabilidad |
| VSDS | 1/3 | **1/3** | No hay comparador científico prospectivo validado |
| Progreso de producto V4 | 36,90 % | **36,90 %** | Ninguna de las 36 adjudicaciones V4 revisada |
| Medallas | 2/90 | **2/90** | No se han concedido otras |
| Gates de release | 0/6 | **0/6** | Ninguno verificado en nueva rama |
| Hallazgos científicos nuevos N1/N2/N3 | 0/0/0 | **0/0/0** | No confundir con falsaciones locales y resultados clásicos |

[Trayectoria CT2 JSON](CT2_TRAJECTORY.json) · [Gráfico de escala completa y ampliada](CT2_FULL_AND_ZOOM.svg). La ausencia de subida es deliberada: fuente primaria pública **HTML**, controles empíricos retrospectivos y una reejecución didáctica de un sistema electoral conocido no justifican atribuir originalidad científica 1/3 ni probabilidad prospectiva.

## B. Procedencia original y límites de captura

Dos resoluciones JEC en páginas originales oficiales del BOE:
- **28/04/2019**, BOE-A-2019-8070, publicada el **30/05/2019**: https://www.boe.es/buscar/doc.php?id=BOE-A-2019-8070
- **23/07/2023**, BOE-A-2023-18907, publicada el **01/09/2023**: https://www.boe.es/diario_boe/txt.php?id=BOE-A-2023-18907
- Corrigendum publicado el **16/09/2023**, BOE-A-2023-19537: https://www.boe.es/buscar/doc.php?id=BOE-A-2023-19537

Las **páginas HTML oficiales** se inspeccionaron con navegación web y se extrajeron manualmente los agregados literales de sus cuadros; **NO** se han obtenido XML/PDF originales como bytes, ni hashes oficiales, ni instante exacto `first_public_at`. El intento previo de acceder a XML devolvió `unsupported application/xml` en el lector y falló por DNS en el entorno de ejecución; se preserva como bloqueo ya conocido, no como otro ciclo. Los números de referencia del BOE acreditan publicaciones oficiales, no la identidad de individuos ni la licencia de un eventual producto de perfilado.

## C. Resultados con unidades, controles y alternativas

| Ciclo | Experimento A–J | Resultado comprobado y límite |
|---|---|---|
| [C01](C01_RESULT.json) ([prereg](C01_PREREG.json)) | Cadena bitemporal de corrección de fuente oficial | El BOE-A-2023-19537 rectifica un número de votos **de una candidatura no electa al Senado en Madrid**, publicado inicialmente el 01/09/2023: literal original ambiguo `1.007.32`; valor rectificado `1.007.322`. Es una publicación nueva el **16/09/2023**, **15 días** después. No imputar la corrección al día de elección y no modificar por ello votos agregados del **Congreso**. No se guardan nombres. |
| [C02](C02_RESULT.json) ([prereg](C02_PREREG.json)) | Panel 2019–2023 de tres escaños, Guadalajara | **2019**: PSOE 42.521 votos/1 escaño; PP 28.618/1; Ciudadanos 26.817/1; Vox 23.501/0. **2023**: PP 51.195/1; PSOE 46.479/1; Vox 27.126/1; Sumar 12.907/0. Cambia ganador por votos PSOE→PP y partido del tercer escaño Cs→Vox; no supone seguimiento de los mismos electores ni equipara Sumar a Podemos. |
| [C03](C03_RESULT.json) ([prereg](C03_PREREG.json)) | Panel 2019–2023 de cinco escaños, Cantabria | **2019**: PSOE 90.534/2, PP 77.902/1, Cs 54.361/1 y **PRC 52.266/1**; Vox 40.139/0. El PRC estaba en una continuación distinta del Cuadro II. **2023**: PP 147.326/2, PSOE 116.596/2, Vox 49.243/1. No se conocen porcentajes de todo el voto solo con cuatro o seis candidaturas; el total de escaños se mantiene, no el censo. |
| [C04](C04_RESULT.json) ([prereg](C04_PREREG.json)) | D’Hondt frente a restos mayores, tres circunscripciones de 2023 | Reproducción computacional de resultados oficiales en Guadalajara (3), Cantabria (5) y Alicante (12). **D’Hondt 20/20 escaños** en estas cuatro candidaturas principales; método alternativo de restos mayores adjudica en Alicante **PP 4 y Sumar 2**, frente al resultado **PP 5 y Sumar 1**: diferencia de un escaño. Es una simulación *in-sample* con distritos seleccionados porque las cuatro listas cubren todos los puestos, no un benchmark predictivo ni prueba de cobertura nacional. [Fixture íntegra](C04_DHONDT_VS_HAMILTON_2023.json). |
| [C05](C05_RESULT.json) ([prereg de pivote R5](C05_PIVOT_PREREG.json)) | Ablación adversarial exacta de seis listas en Cantabria 2019 | Con PRC, D’Hondt reproduce PSOE 2, PP 1, Cs 1, PRC 1. Si se **elimina PRC**, el modelo asigna erróneamente **un escaño a Vox**, a pesar de conservar los votos nacionales. Reproducción con `fractions.Fraction` de Python y **seis variantes de eliminar exactamente una candidatura**: cuatro cambian la asignación y dos no. **Advertencia metodológica:** el efecto PRC→Vox ya había sido observado exploratoriamente durante C04 **antes** del prerregistro de pivote C05. La batería completa de seis ablations sí se ejecutó después; por tanto no se presenta como nuevo experimento ciego. [Datos y seis variantes](C05_2019_CANTABRIA_LEAVE_ONE_OUT.json). |

En C04 las tres asignaciones nacionales D’Hondt en 2023 se contrastaron con el total observado por circunscripción y categoría de partido. El algoritmo trabajó con los cuatro partidos cuyos escaños cubrían la totalidad de las circunscripciones seleccionadas; al limitarse a ese escenario **no** se valida que otras provincias, regionalismos, umbrales o votos a candidaturas minoritarias sean irrelevantes. Para C05 se usaron **seis** opciones documentadas por el BOE 2019, no se asumió que cinco partidos nacionales fueran todo el universo.

## D. Dictamen adversarial R1–R5

- **R1 / unidad real:** una papeleta no es un expediente, una candidatura no es una identidad individual y un escaño no equivale a una proporción individual de éxito; son agregados de opción política/circunscripción/elección.
- **R2 / comparadores fuertes:** D’Hondt (regla de asignación) contra Hamilton (método alternativo), comparación matched 2019/2023 por circunscripción y test crítico de **inclusión del PRC**; el predictor "partidos nacionales únicamente" es inadecuado.
- **R3 / selección y multiplicidad:** se eligieron distritos y documentos tras inspeccionar fuentes y resultados, por lo que el acierto 20/20 es **explicativo e in-sample**, no generalizable, no novedoso y no validado externamente como modelo.
- **R4 / ablaciones y fuente temporal:** corrigendum de septiembre con fecha posterior separada; seis exclusiones de listas en Cantabria con Python racional exacto; nulos/faltas de una lista no se convierten en voto cero certificado.
- **R5 / parada y pivote:** plan C05 original de otra tentativa XML se dejó **sin ejecutar como ciclo**, por bloqueo repetido. Se abrió [prereg de pivote](C05_PIVOT_PREREG.json) y se realizó la auditoría de seis condiciones. Conocimiento previo de la H1 explicitado; no se inventa una prueba ciega.

**No existe 2/3 ni 1/3 nuevo acreditado.** No hay captura nominal original, muestra poblacional para un estimando sociológico defendible, temporalidad `first_public_at` por registro, comparador de forecasting independiente y evaluación prospectiva. El efecto mostrado prueba un **riesgo de cobertura de fuentes** y una **necesidad de versionado**, no superioridad de una arquitectura.

## E. Tareas que sí necesitan Codex/PC — NO EJECUTADAS

- **T011 (pendiente):** https://github.com/GalexY3/Metodologia-AB/blob/research/pfl-abh5-source-validation-20261028/proyectos/politics-fantasy-league/tareas_codex/T011_FUENTE_PARIDAD_QA_SOURCE5_20261028.md — descarga oficial Interior XLSX y comprobación integral limpia Python/Node/Atlas del HEAD relevante; hashes y SHA probados.
- **T014 (propuesta, no ejecutada):** adquirir y preservar exactamente los XML originales del BOE 2019/2023 y corrección 2023 con validación TLS y SHA-256, registrando formato, campo, errata, fecha de publicación oficial y `first_public_at` únicamente si hay atestación horaria verificable; comparar artefactos contra las transcripciones manuales y documentar diferencias. No subir originales nominativos al repositorio público/privado si contienen más datos personales de los necesarios.
- **T015 (propuesta, no ejecutada):** esquema completo de candidaturas por distrito y originales JEC/Interior — recopilar todas las opciones regionales y minoritarias, denominadores y fechas de conocimiento; preinscribir selección de distritos y validación verdaderamente externa a los tres ejemplos vistos. No usar resultados para scores nominales sin base jurídica y auditoría de equidad.
- Revisar PR de forma ordenada sin fusionar automáticamente: #18 T010, #19 POSTT010, #20 SOURCE5, #21 INSTITUTIONAL5, además de esta rama.

## F. Cierre, hashes y siguiente bloque

[Ledger de campaña](CAMPAIGN_STATUS.json) con cinco pares de resultados/pre-registros. Las fuentes HTML oficiales se citan con URL y referencias de cuadro; **no** se atribuye SHA-256 de original descargado. Las dos ejecuciones aritméticas verificadas fueron V8 para D’Hondt y Hamilton en 2023 y `Fraction` de Python para 2019; no hay pruebas de Linux/Windows ni producción en esta campaña. El [gráfico CT2](CT2_FULL_AND_ZOOM.svg) muestra BASE y C01–C05 a 29/100, escala completa y zoom. La campaña se cierra con 5/5 válidos limitados, 0 inválidos, 0 planificación, N1/N2/N3 nuevos 0; el presupuesto se agotó, no hay autorización remanente.

**SOLICITO BRANCHING AB-H DE 5 CICLOS NUEVOS**, sujeto a autorización expresa, para contrastes externos preinscritos con universo electoral completo y fuente original verificable, evitando repetir los tres casos expuestos o nuevos intentos XML sin acceso; mantener la lista Codex para adquisiciones no realizables aquí.
