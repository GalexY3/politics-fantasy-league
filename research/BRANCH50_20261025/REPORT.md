# Campaña PF-B50 con BRANCHING — informe del primer bloque de ejecución

**Fecha 25-10-2026.** Autoriza el usuario 50 bucles flexibles de producción e investigación. Los 45 anteriores siguen autorizados (sin consumir) y PF-AB20 tiene 19 ciclos no ejecutados. Aquí no se altera esa contabilidad. Esta campaña contiene **8 incrementos de ingeniería realmente instrumentados** (sin precongelación GitHub) y **42 ciclos autorizados no ejecutados**. La etiqueta "PRODUCTION_VERIFIED_LOCAL" no es equivalente a "EXPERIMENTAL_AB": se trata de pruebas de aceptación locales sobre código y fixtures ficticias. No hay novedad científica acreditada, ni contrafactual empírico político ni replicación independiente.

## Branching efectivamente realizado

Los ocho trabajos recorren cuatro ramas (mercado, warehouse, seguridad local, operaciones). Se documentan A–J para que no se confundan comprobaciones de QA con experimentos sociales. La bifurcación se motivó por fallos de invariantes al auditar el software anterior; no fue una búsqueda de estadísticas favorables. La distancia DRIFT es ≤D1 (sin cambio de población científica).

### PF-B50-01 · mercado · D0.4

**A.** question: La venta de una figura guardada para una jornada aún editable rompe coherencia de plantilla · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Bloquear venta mientras la figura esté en una alineación aún abierta · competent_rival: Permitir la venta y limpiar automáticamente las alineaciones (alternativa de producto) · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: El intento de venta se rechaza sin modificar fondos, posesión ni alineación · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: product.py,tests/test_product.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_cannot_sell_an_active_future_lineup · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Permitir la venta y limpiar automáticamente las alineaciones (alternativa de producto).

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No aplica; invariant test; no causalidad externa.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-02 · warehouse · D0.5

**A.** question: Versiones de un mismo evento en una consulta as-of se cuentan como eventos distintos · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Seleccionar última revisión conocida antes del corte · competent_rival: Mantener todas las revisiones y deduplicar después (alto riesgo de olvido) · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Al día siguiente de cargar r2, solo r2 aparece; al corte anterior, r1 · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: warehouse.py,tests/test_warehouse.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_revision_is_immutable_and_bitemporal · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Mantener todas las revisiones y deduplicar después (alto riesgo de olvido).

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No prueba que el identificador oficial de evento sea estable.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-03 · warehouse · D0.6

**A.** question: Filtrar la ventana temporal antes de deduplicar podría resucitar la revisión obsoleta · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Deduplicar por identidad antes de filtrar fecha efectiva · competent_rival: Filtrar primero (método previo vulnerable) · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Si r2 reubica evento fuera de ventana, no devolver r1 · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: warehouse.py,tests/test_warehouse.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_revision_replaced_before_time_window_filter · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Filtrar primero (método previo vulnerable).

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: Sin semántica de retractación formal para datos oficiales.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-04 · integridad · D0.5

**A.** question: Un archivo alterado tras el hash inicial podría escribirse con hash antiguo · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Recalcular SHA durante stream y comparar al final · competent_rival: Confiar solo en hash inicial sin bloqueo de archivo · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Si cambian bytes antes de lectura, rollback sin filas · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: warehouse.py,tests/test_warehouse.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_import_detects_intervening_file_change · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Confiar solo en hash inicial sin bloqueo de archivo.

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No defiende ataques con cambio coordinado antes y después sin medidas OS.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-05 · integridad · D0.2

**A.** question: Fallos de decodificación podrían comprometer atomismo/error comprensible · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Rechazar UTF-8 inválido y revertir transacción completa · competent_rival: Interpretación con reemplazo implícito y pérdida de información · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Entrada corrupta: 0 ingestions y excepción identificable · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: warehouse.py,tests/test_warehouse.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_import_rejects_invalid_utf8_atomically · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Interpretación con reemplazo implícito y pérdida de información.

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No es validación semántica del JSON institucional.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-06 · seguridad_local · D0.7

**A.** question: Comparación Origin con Host entrante permitiría aprobar valor atacante si ambos coinciden · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Allowlist estricta localhost y 127.0.0.1 en GET y POST · competent_rival: Confiar solo en Origin o en Host suministrado · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Host remoto rechazado aunque Origin coincida · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: server.py,tests/test_product.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_http_rejects_untrusted_host_even_if_origin_matches · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Confiar solo en Origin o en Host suministrado.

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No autenticación; no publicar en Internet; riesgo residual DNS/proxy.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-07 · operaciones · D1.0

**A.** question: Un cambio manual SQL puede dejar una alineación futura con una figura no poseída · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Auditoría read-only del estado en disco, con salida FAIL para incoherencias · competent_rival: Confiar únicamente en los endpoints (ignora escritura manual/corrupción) · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Validar buen estado, inyectar incoherencia y detectar OPEN_LINEUP_CONTAINS_UNOWNED_FIGURE · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: ops.py,tests/test_ops.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_audit_catches_future_lineup_corruption;test_audit_demo_only_synthetic · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Confiar únicamente en los endpoints (ignora escritura manual/corrupción).

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: No reemplaza auditoría de integridad de negocio multiusuario.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

### PF-B50-08 · operaciones · D1.0

**A.** question: Un cambio manual en row_count puede ocultar pérdida de filas · estimand: Cumplimiento de invariante computacional local (binario) · population: fixture sintética y ejecución local; NO población política.

**B.** hypothesis: Auditoría de recuentos por ingestión y SQLite quick_check / FKs · competent_rival: Sólo comprobar que el archivo sqlite abre · H_other: Defectos indirectos no cubiertos por la prueba.

**C.** design: Prueba determinista reproducible con caso adversarial · primary_endpoint: Tras alteración maliciosa del recuento, auditoría falla · negative_controls: suite completa y estado sin manipulación.

**D.** instrumentation: ops.py,tests/test_ops.py · prereg_before_execution: NO_GITHUB_PREREG; diseño de pruebas escrito localmente.

**E.** observed: PASS · tests: test_audit_warehouse_counts · global_tests_passed: 57.

**F.** adversarial: El test pasa, pero cobertura limitada al caso especificado · baseline: Sólo comprobar que el archivo sqlite abre.

**G.** independent_confirmation: NONE; misma suite local, no laboratorio externo.

**H.** prior_change: Confianza de ingeniería incremental para ese invariante; NO actualización de priors científicos políticos.

**I.** engineering_validity: LOCAL_ACCEPTED · scientific_novelty: NONE · external_validity: NOT_TESTED · limitation: Recuentos correctos no certifican completitud de fuente externa.

**J.** decision: CONTINUE_PRODUCTION_BRANCH · next_evidence: Pruebas E2E navegables y corpus oficial con contratos verificables.

## Política de descubrimientos, contabilidad y límites

- N1=0, N2=0, N3=0; CT2 para predicción parlamentaria 24/100 sin cambio. Los tests son sintéticos y no respaldan una predicción individual en España.
- O2/O3: falta *freeze before run* en GitHub para estos ocho casos, de modo que NO son experimentos científicos confirmatorios. El código/dictamen se suben retrospectivamente, explicitándolo.
- Una sola suite no constituye confirmación independiente ni comparación con un rival científicamente competente.
- Seguimiento: exposición de riesgos al convertir el servidor local en online (autenticación, antifraude, pagos, RGPD, moderación, permisos, auditoría). No desplegar servidor actual públicamente.
- Los 42 ciclos restantes deben decidirse tras evidencia nueva, no se rellenan a priori con falsos resultados. Está permitido derivar hacia nuevas ramas (fuente oficial, agentes, series temporales, interfaz, auditoría).

## Criterios de migración del repositorio

Actualmente se aloja de forma provisional en `GalexY3/Metodologia-AB/proyectos/politics-fantasy-league/`, porque `GalexY3/polictics_fantasy_league` devolvía HTTP 403. El repositorio de metodología AB sigue siendo dueño del protocolo y **no de los resultados substantivos**. Migrar los archivos y conservar esta ruta como puntero cuando el acceso al nuevo GitHub sea posible. Ver `MIGRATION.md`.