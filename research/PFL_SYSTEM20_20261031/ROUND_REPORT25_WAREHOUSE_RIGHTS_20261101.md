# R25 · Derechos declarados frente a acreditación de warehouse

**1/11/2026. NONCYCLE de infraestructura, 0 AB-R y 0 AB-P.** Base independiente PR #7 HEAD 8df788007553c05890be08b962ffc24349ee1a6a. La PR #16 C17 trata derechos por distribución con un contrato Python separado y todavía DRAFT: no interpretarlo como integrado en el almacén JavaScript. Sin fuentes originales, expedientes personales, condiciones nuevas aceptadas, firmas o licencias adquiridas.

## Hipótesis adversarial

Hipótesis rival: el valor literal OPEN_LICENSE_VERIFIED aportado por un bundle al almacén tendría que corresponder a testigo independiente de derechos. Inspección de src/politics_fantasy/evidence_warehouse.mjs y scripts/ingest_political_evidence.mjs: el CLI recomputa SHA de **bytes locales**, pero ni ese digest ni las fechas y flags del bundle autentican editor, derechos por distribución/SHA/uso o primera publicidad histórica.

Falsador PREPATCH: fuente ficticia TEST:asset etiquetada OFFICIAL, RAW_CAPTURED y OPEN_LICENSE_VERIFIED, bytes sintéticos y SHA exacto, observación y primera publicación declaradas. El gate antiguo suprimía RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION y permitía read_only_aggregate_display_allowed=true. asOf() contaba la fuente sin prueba independiente de publicidad histórica, también cuando rights=UNKNOWN.

SHA256 del código antes de editar: **bfada6bfcd4cc43b816440e9286a2c8503cb94bef3842a2510387920294c7056**. SHA256 inicial del test: **8aa9fa128e5cfb357b8482e60904006f1f769b0ba138fb62cc6dc811814923dc**. Primera QA: **3 FAIL esperados, 1 PASS de control**, antes de tocar producción.

La prueba acredita una falsa señal de admisibilidad/visibilidad en **CLI offline**, no publicación web, autorización efectiva de ingesta o puntuación de personas reales. Los otros controles HTTP y source_eligibility siguen siendo conservadores.

## Reparación

El literal de derechos pasa a tratarse exclusivamente como afirmación no independiente, con flag rights_claim_is_independently_attested:false. evidenceGate() conserva el blocker de redistribución para cualquier original capturado, aunque reclame OPEN_LICENSE_VERIFIED. La visualización agregada se limita a simulaciones o índices documentales sin originales; asOf() permite cronologías de fixtures puramente ficticios, pero no de originales con first_public declarado unilateralmente. Cualquier vía a originales reales requeriría contrato de revisión independiente del lado servidor, sin autocertificación del bundle.

Se añadió un test de integración con el **CLI real** y fichero temporal de bytes enteramente ficticios. QA posterior: **39/39 Node PASS** (treinta casos anteriores de warehouse, cuatro de CLI previo, cinco R25), sintaxis JS PASS. SHA256 posterior del módulo: **4dd3f4b6902aeefdb7497c1b6b73a446f2ef4c0acf757e0b973b588f5f02a1ca**. SHA256 posterior del test: **13822317ff6b316ca6e3d6a2152498756313bbe64edc93080e95d105a0b24980**.

## Comprobación de nueva fuente para R5

Se revisó la propuesta documental sobre los conjuntos del Ayuntamiento de Madrid 300517 (solicitudes y reclamaciones) y 300594 (registro histórico). Ya estaban identificados y examinados como metadatos en **R11**, con advertencias sobre condiciones por mero uso, mismo editor y denominador no independiente. Por tanto, **REDUNDANT_R11_STOP_LOCAL_R5**, no un nuevo hallazgo. La licencia declarada CC BY 4.0 en el catálogo no resuelve por sí sola el alcance de cada distribución y las condiciones de acceso. No se descargaron CSV/XLSX, aceptaron términos ni consultaron casos.

**R5 sigue STOP**: población inicial completa, negativos, pendientes, censura, N independiente, first_public histórico y derechos por activo no acreditados. Ni QA ni datos artificiales consumen ciclo científico, desbloquean logros o superan los seis release gates. El incremento se prepara independiente de PR #16 y PR #18 para revisión y reconciliación antes de cualquier integración en main.

**Seguimiento documental R26 de la misma sesión, sin alterar los tests R25:** se identificó el conjunto distinto 300044 SYRG/SYRT de sugerencias y reclamaciones generales y tributarias, separando archivos «Recibidas» y «Terminadas», no encontrado en la búsqueda literal de la rama científica. Su metadata, tres rutas rivales, falsadores, riesgos de corte y restricciones preacceso se documentan en ROUND_REPORT26_MADRID_SYRG_SYRT_PREACCESS_20261101.md. **No se suma a los 300517/300594 R11, no se descargaron archivos y no levanta R5.**
