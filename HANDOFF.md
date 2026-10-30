# PFL · briefing derivado

Rama de trabajo: `research/pfl-abh25-evidence-and-product-20261030` (PR #3, draft); base de `main`: `653604358183b59e8c0446497f47ff4a3769134f` (verificar HEAD remoto de nuevo al continuar).
Estado rev. 13; publicación canónica: MAIN_PR2_MERGED_CODE_REVIEW_PASS; ABH25 aún no fusionado.
El código ABH25 vive SOLO en la rama de revisión; no está integrado a main. No confundir QA de la rama con liberación.

Atlas: 96 lotes; SHA `8072ccbd76ed7851f96757cf8567a17e869f66d59da7ef6637f122583ac93d3f`, 63 nodos, 81 aristas, 314 ejecuciones, 51 complaints; gates 0/6.
Autorización ABH10: 6/10 ejecutados; 4 disponibles, preservados bajo R5. Históricos separados: 2.

## Último trabajo de origen migrado (AB PR81)
P1 GitHub Actions #40995507812: 35 Python tests PASS y node --check, dos cuentas y clubes separados. R1 C38 GitHub Actions #40996183394: 8/8 tests Python y 4170 registros originales, diferencia documentacion −29,08 p.p. Atlas94 original Python #40996696957: 94 lotes, SHA ac64213f..., nodes63 edges81.
Pruebas históricas de AB; no sustituyen QA sobre el nuevo commit.

## Estado del corte de repositorios
MERGED_PR2_CODE_REVIEW_PASS; origen: PR #81 (d725a8dff37429a035b6e1ffb27c3568e51322ce); rama de revisión: migration/pfl-final-cutover-20261030. Consultar status del traslado y recibo de incorporación antes de continuar.

Concesión nueva INDEPENDIENTE PFL-GRANT-20261030-INTEGRATION10: 0/10 ejecutados; 10 disponibles. No reasignar saldo ABH10.

## Concesión de continuación: lectura y trabajo sustantivo
20 unidades totales: 5/5 revisiones documentales; 0 ciclos científicos válidos nuevos; 15 unidades sustantivas disponibles. Las revisiones y el mantenimiento no son experimentos; no sumar otra vez esta concesión.

## Nueva concesión ABH25 (independiente, 30/10/2026)
25 autorizados, 2 válidos de alcance limitado ejecutados: C01 AB-R original de código externo, C02 AB-P HTTP ficticio; 1 intento C03 solo planificación bloqueada sin consumir; quedan 23. Contratos, recibos, prior PF-BR81/82 y O7 están en `research/ABH25_20261030/`; Atlas lote 0096. Históricos READ5-CONTINUE15 (15), ABH10 (4), INTEGRATION10 (10) y STOP_R5 (2) intactos.

C01: fuente original [Suite à donner](https://github.com/Clemsrec/suiteadonner/blob/a627cc26f255231d67faebb14e265523e46c0a66/scripts/fetch-reunions.mjs), script inspeccionado sin `first_public_at` acreditado por evento; no equivale a ausencia universal ni prueba causal. C02: [Actions #41018524103](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41018524103), 2/2 pruebas HTTP de dos cuentas, rondas, controles negativos y persistencia. C03: [CSV oficial](research/ABH25_20261030/C03_STAGE0_CSV_RECEIPT.json) 29 filas, MD5 coincidente, sin meeting ID; [ZIP oficial](research/ABH25_20261030/C03_STAGE1_BLOCKED.json) con MD5 distinto al publicado y FAIL-CLOSED antes de abrir: PARK/R5, no repetir sin nueva versión autenticada.

## product
- P0-INTEGRATION [DONE]: Una base técnica y de evidencia reunida y revisable. Siguiente: Integración incorporada; el siguiente hito de producto es P1-ACCOUNTS con datos ficticios
- P1-ACCOUNTS [READY_REVIEW]: Cuentas y sesiones locales con clubes ficticios aislados por cuenta; sin despliegue público. Siguiente: 2/2 pruebas HTTP reales en Linux, pero revisión humana de dos perfiles en navegador pendiente antes de DONE
- P2-PLAYABLE-FLOW [QUEUED]: Flujo ficticio completo usable y persistente. Siguiente: test HTTP de acceso→club→alineación→jornada ficticia→resultado y reinicio PASS; faltan UX real y aceptación humana antes de DONE.
- P-CONTINUITY [DONE]: Continuidad verificable entre conversaciones sin copiar un resumen que caduque. Siguiente: Cada nueva sesión lee START_HERE y cada cierre guarda estado y handoff
- P-ORGANIZATION [DONE]: Mapa por tareas, catálogo buscable e índice de investigaciones mantenidos con Git. Siguiente: Regenerar catálogo al cambiar rutas versionadas; conservar la trazabilidad de los archivos históricos
- P-MIGRATION [DONE]: Proyecto independiente de AB con historia y herramientas reproducibles. Siguiente: Continuar P1-ACCOUNTS en este repositorio; adoptar cambios de AB solo explícitamente

## research
- R0-FEASIBLE-QUESTION [DONE]: Pregunta institucional delimitada frente a rutas de rank humano e incentivos, con datos públicos originales accesibles y licencia abierta. Siguiente: Pregunta/acceso validados; continuar R1 con medida auditada y antecedente competente, sin reivindicar novedad general.
- R1-DISCRIMINATING-RESULT [READY_REVIEW]: Negativo observacional C38 preregistrado: diferencia high−low −29,08 pp en documentación CSV, 3 de 4 años comparables con signo contrario. Siguiente: C38 negativo descriptivo sin corrección causal; C03 no habilita corpus nuevo por falta de enlace y desfase MD5 del ZIP. Reabrir solo con versión oficial verificada.
- R-AEA-C37 [PARKED]: Acceso al registro original e historial del ensayo AEARCTR-0000981. Siguiente: No repetir búsquedas equivalentes
- R-T005 [PARKED]: Originales y condiciones de uso suficientes para una pieza concreta de T005. Siguiente: Reabrir solo la pieza para la que haya evidencia nueva

## Última validación declarada
Histórico full Linux de PFL #2: 837 Python +32 subtests, 511 Node, 38 Atlas +105 subtests PASS en `7de66007`. Nueva rama ABH25: Actions #41018524103 HTTP real 2/2 PASS; #41018842403 Atlas96 96 lotes SHA `8072cc...` PASS; #41019269617 catálogo y project_status PASS en un commit anterior a C03. Run #41019397612 falló por índice desactualizado tras C03; catálogo/mapa/índice regenerados. **Validación final del candidato de PR #3**: Actions #41020562908 éxito, 2/2 tests HTTP, Atlas96 SHA exacto, índice de 2899 archivos PASS, project_status.errors=[], verificador de presupuesto nuevo e histórico PASS. C03 CSV original #41019397659 PASS; ZIP original #41019680394 FALLÓ MD5, conservado. NO se reejecutó toda la suite Python/Node en esta rama ni se acreditó aceptación humana.

Este briefing consulta el árbol local y el ledger; hacer fetch/resolver HEAD remoto antes de usarlo para continuar. Un resultado histórico no verifica otro commit.

Consistencia: PASS en PR #3, Actions #41020562908, candidato de merge `e06811c435296f03f28dce5a9b52a072671affe6` (checkout separado; no constituye fusión a main).
Huella código/tests en ese candidato: `7688664942efc7a1783e58c73f76cc1d695d5c679fffc516d636c623e6a7343f`.
No pedir ciclos por fórmula. Aparcar bloqueos sin observación nueva. Actualizar PROJECT_STATE y este handoff al cerrar.
