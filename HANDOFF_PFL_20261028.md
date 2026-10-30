# HANDOFF PFL — 28/10/2026 · LEER ANTES DE RETOMAR

> **ESTE DOCUMENTO NO ES UNA AUTORIZACIÓN.** La última campaña `AECCHOICE5` está cerrada **5/5**, **0 ciclos disponibles**. El botón del último informe era una invitación; no inicia nada hasta que el usuario lo pulse o autorice explícitamente otro bloque. Este fichero es parte de la PR #31, no una nueva campaña.

## 1. Estado verificado al corte

- Repo privado: `GalexY3/Metodologia-AB`, rama `research/pfl-abh5-aec-choice-20261028`, PR [#31](https://github.com/GalexY3/Metodologia-AB/pull/31) **draft/open**, apilada sobre `research/pfl-abh5-petition-cohort-20261028`/PR #30. Al preparar el traspaso el HEAD anterior a este commit documental era `c98b93587e97dab34a93dfec7bba1df3be8b6b45`; después del handoff la rama tendrá un SHA distinto. **Verificar HEAD real antes de crear ramas.**
- `main` al corte: `968f2b1723bd7961a6fe08d003b165d6a9e93c81`; no se fusionó.
- Proyecto: `proyectos/politics-fantasy-league/`. Resumen acumulativo: `ab_atlas/CURRENT.md`.
- Último informe: [ABH_AECCHOICE5_20261028/FINAL_REPORT.md](research/ABH_AECCHOICE5_20261028/FINAL_REPORT.md), [ledger A–J](research/ABH_AECCHOICE5_20261028/CAMPAIGN_STATUS.json), [fuentes y priors](research/ABH_AECCHOICE5_20261028/SOURCES_AND_PRIORS.json), [CT2](research/ABH_AECCHOICE5_20261028/CT2_FULL_AND_ZOOM.svg).
- Indicadores **sin cambios**: `CT2=29/100` ordinal; `V4=36,90%`; `VSDS=1/3`; `logros=2/90`; `gates=0/6`; `N1/N2/N3 nuevos=0/0/0`. No asumir auditoría histórica exhaustiva de N1 del portafolio.

## 2. Normativa y métodos — fuente canónica

Leer EN ESTE ORDEN: `AGENTS.md`, `README.md`, `docs/METODO_AB_3_2_1.md`, `docs/AB_3_2_1_O3_BUCLES_DRIFT.md`, `docs/AB_3_2_1_O4_CONFIANZA_Y_NIVELES.md`, `docs/AB_3_2_1_O5_DISTANCIA_DRIFT.md`, `docs/AB_3_2_1_O6_CAMPANAS_INFORMES_CT2_Y_CICLOS.md`, `ab_atlas/CURRENT.md`, informe y ledger del último bloque.

**AB 3.2.1 R1–R5:** R1 estimando/unidad/outcome antes de prueba; R2 baseline competente con la misma información; R3 distinguir búsqueda/adaptación/holdout/multiplicidad; R4 falsadores, ablation, leakage y alternativas; R5 parar/pivotar cuando no exista evidencia nueva discriminante, aunque sobre cuota. El protocolo es una metodología de investigación **no validada como superior**.

**AB A–J:** A pregunta/contrato; B rivales/nula; C prueba y condiciones; D instrumento/QA; E ejecución **real**; F auditoría adversarial; G confirmación, separando interna de externa; H priors/hipótesis nuevas; I dictamen científico multidimensional; J AB-DECIDE. `C0x_PREREG.json` debe estar **committed ANTES de leer nuevos outcomes**; luego `C0x_RESULT.json`, métricas, QA y ledger con commits. Enmienda adaptativa explícita ANTES de nuevos datos. No contar intentos de descarga como ciclo extra ni plan como ejecución; distinguir `VALID_BOUNDED`, `INVALID`, `NOT_EXECUTED`, `PLANNING_AB_ONLY`, `POST_HOC_AUDIT`, `AB-R` y `AB-P`.

**Niveles:** 0/3 sin hallazgo adjudicable, 1/3 exploratorio replicable, 2/3 novedoso y discriminante + control fuerte + **validación externa independiente**, 3/3 más exigente. CT2 1–100 es **confianza ordinal en llegar a 2/3 por línea**, no probabilidad; no incrementarla por más ciclos o regresiones conocidas. DRIFT D0–D5 mide diferencia temática, no mérito. Dibujar SIEMPRE trayectoria CT2 0–100 + vista ampliada y fuente JSON.

## 3. Forma de trabajo del investigador

- Normalmente autoriza **5 ciclos AB-H adicionales**, sin consulta **entre** ciclos; nuevas campañas futuras deben tener autorización independiente (norma de solicitudes 5–15 por bloque). Si ya hay autorización explícita, ejecutarla dentro del presupuesto, sin pedirla de nuevo.
- Priorizar sociología, fuentes institucionales auténticas, datos que distingan hipótesis, variables conocidas antes de eventos, comparadores estadísticos competentes, pruebas fuera de muestra y explicaciones alternativas. **No** rellenar cuota con triviales ni perseguir la puntuación CT2.
- Prohibido **ChatRelay** (en pausa), **merge a main**, CI costosa, inventar source/ejecución/commit/resultado/causalidad o atribuir ejecución a Codex/PC no usado; no divulgar datos privados ni valorar políticamente personas reales.
- GitHub se ha manejado con conector conectado y acciones `mcp__GitHub__fetch_file`, `fetch_pr`, `create_branch`, `create_file`, `update_file`, `create_pull_request`, `compare_commits` desde `functions.exec`. **No asumir que otra instancia tiene las mismas herramientas ni que el repo privado está montado localmente**.
- Patrón: verificar base y HEAD → rama nueva desde SHA real → buscar nueva clase de datos → prerregistros A–J **committed** → recuperar y autenticar originales si posible → invariantes/conteos/denominadores → cálculos realmente ejecutados → auditoría adversarial → `SOURCES_AND_PRIORS.json` + ledger + CT2 JSON/SVG + informe → actualizar `ab_atlas/CURRENT.md` → PR draft apilada → verificar todo. No dar por ejecutado un script solo por haberlo escrito.
- Al finalizar, entregar links verificables e indicadores y un **botón accionable** de autorización, p.ej. `<button onClick={()=>GenUI.issueNewTurn('Autorizo 5 ciclos AB-H ...')}>Autorizar 5 ciclos...</button>` donde la interfaz lo admita. El botón **no** otorga permiso hasta pulsarse.

## 4. Línea y campañas recientes; qué NO repetir

La secuencia contiene SOURCE5, INSTITUTIONAL5 (#21), ORIGINALS5, REGIONAL5 (#23), HOLDOUT5 (#24), DIVISIONS5 (#25), USHOUSE5 (#26), EU27 (#27), UK650 (#28), PETITIONS5 (#29), PETITIONCOHORT5 (#30) y AECCHOICE5 (#31). Confirmar PR antiguas al citarlas.

- **EU27**: 27 países, mujeres eurodiputadas/turnout 2019/2024; corr casi nula, baseline representación 2019 superior a turnout, no preevento ni archivos originales firmados.
- **UK650**: 650 distritos/4515 candidaturas UK2024; margen final vs participación Spearman −0,276, fragmentación no ayuda materialmente, variables posteriores a votos y espejos con conflicto de versiones.
- **PETITIONS5**: 12 peticiones con más firmas UK; 10k→respuesta mediana 16,46 días, 100k→debate 86,58; muestra deliberadamente sesgada por éxito, 5/5 Hansard fechas verificadas.
- **PETITIONCOHORT5**: 40 IDs fijados, 9 copias; ampliación adaptativa a 180 IDs (prerregistrada antes de outcomes nuevos), 66 copias/114 sin copia; 13/13 >=10k con respuesta y 0/53 bajo10k; regla conocida mejor que logit, 100k n2 insuficiente: C04 **no contado**, C06 nueva prueba documental; no inferir causas ni población general.
- **AECCHOICE5 (última)**: Australia 2025, 150 divisiones y cuatro CSV con nombres de AEC hallados como **copia pública de tercero**, 0 bytes oficiales auténticos descargados. Correlación nº candidaturas vs % papeletas informales Spearman **+0,69068**, Pearson **+0,57639**; excluir Riverina/Calwell rho **+0,67984**; pendiente OLS ajustada estado/clase/censo **+0,8383 pp/candidatura** (HC3 SE 0,1115); `R2` 0,4685→0,6329; 7+ frente <=6 candidaturas diferencia **+2,566 pp**; leave-one-state-out MAE clase+censo **2,3958 pp** frente a +candidaturas **1,9801 pp** (ganancia 0,4157 pp). **NO causalidad ni predicción prospectiva**: archivos de junio 2025 tras elección mayo 2025, estudios previos McGinn–Maruyama 2025 y revisión AEC 2026 ya documentaban mecanismo. Por ello nuevos hallazgos N1/N2/N3 = **0** y CT2 **29**.
- **Fuentes:** SHA Git del espejo ≠ SHA-256 bytes originales del emisor; fecha `Generated` ≠ `first_public_at`. Las fuentes oficiales pueden tener revisiones, cachés y denominadores distintos. Siempre guardar priors y anotaciones de exposición previa.

## 5. Pendientes de Codex/PC — NO EJECUTADOS

Conservar **T011 y T016–T024** (todas tareas preparadas/pendientes salvo que GitHub demuestre un cambio posterior). Leer cada archivo antes de trabajar:
- T011 XLSX electoral/paridad y tests.
- T016–T019 antiguos; consultar texto original, no adivinar.
- T020 originales CSV/JSON firmados Parlamento Europeo.
- T021 originales UK 2024 por distrito y candidaturas, changelog y QA.
- T022 JSON UK Petitions y cohorte menos sesgada.
- T023 180 IDs originales de Petitions, estados/censura y verificación de las 114 ausencias.
- [T024](tareas_codex/T024_AEC2025_ORIGINALES_QA_20261028.md): originales CSV AEC, hashes de fuente, ventanas temporales, recomputación 150 divisiones y suite limpia.
Si se necesita un PC, generar tarea concreta con criterios de aceptación, dejar `NOT_EXECUTED` y seguir investigando con datos distintos; no prometer trabajo de fondo asíncrono.

## 6. Cómo reanudar en otro chat

**Si solo se comparte este traspaso:** verificar repositorio si se solicita, **no** empezar ciclos; última autorización AECCHOICE5 terminada. Si el usuario autoriza otros cinco, comenzar verificando HEAD/PR/ledger y ejecutar A–J sin consultas entre ellos, evitando repetir las tablas ya agotadas salvo evidencia **realmente** nueva.

**Cuello de botella real:** datos primarios originales y un protocolo fechado **antes** del outcome para una hipótesis genuinamente nueva y específica de PFL, con baseline competente. El éxito descriptivo o replicación de una asociación previamente publicada no es 2/3.

**Formato final exigido:** informe, marcadores inicial/final, resultados y negativos por ciclo, registros de fuentes y priors, niveles, CT2 completo/ampliado, commits/PR verificados, pendencias Codex claras, petición de 5–15 ciclos (siempre nueva autorización) y botón real.

**Nota de procedencia:** este documento es un resumen vivo, no prueba de que todo el portafolio histórico esté auditado. Dar prioridad a AGENTS, O3–O6, CURRENT y ledgers verificables. **Crear o actualizar este archivo de traspaso NO consume ciclo ni autoriza otro bloque.**

