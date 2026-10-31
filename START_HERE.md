# Politics Fantasy: empezar o continuar

**Repositorio canónico: [GalexY3/politics-fantasy-league](https://github.com/GalexY3/politics-fantasy-league).** PFL utiliza AB, pero su producto, investigación, pruebas, estado y decisiones viven aquí. No continuar escribiendo PFL dentro del repositorio del método.

## Recuperación breve

1. Leer este archivo, [AGENTS.md](AGENTS.md), [PROJECT_STATE.json](PROJECT_STATE.json) y [la versión de AB adoptada](METHOD_REFERENCE.json).
2. Resolver el HEAD remoto actual de `main`, comprobar cambios locales y hacer fetch antes de continuar. No reconstruir el estado desde el chat anterior ni desde títulos de PR.
3. Ejecutar cuando sea posible `python scripts/project_status.py brief` y `python scripts/project_status.py check`. Sin ejecución, declarar qué solo se leyó y qué no se verificó.
4. Resumir el hito activo de producto, el de investigación, saldo verificado y siguiente acción. Leer solo las fuentes pertinentes; el historial completo es archivo consultable.
5. Si la rama remota avanzó, reconciliar antes de escribir. Nunca sobrescribir trabajo concurrente ni afirmar que se incorporó sin comprobarlo.

## Dónde está todo

**Cuarta ronda científica/documental 31/10/2026:** [Informe de cotejo editorial Canarias + Congreso](research/PFL_SYSTEM20_20261031/ROUND_REPORT4_20261031.md), [manifiesto de recuentos del Árbol de iniciativas](data/source_manifests/parcan_editorial_crossview_20261031.json), [derivado agregado de meses fuente-local](data/source_manifests/parcan_source_local_months_20261031.json), [contrato ontológico temporal y tres tradiciones sistémicas](docs/CONTRATO_ONTOLOGICO_SISTEMICO_TEMPORAL_PFL_20261031.md). Tres estratos PE 2024–2026 suman 1.753 (más PPL 2023/X = 1.754); 34 combinaciones observadas mes/distribución, no un histórico de primera publicación. Dos fuentes editoriales potencialmente comparten base de datos: NO censo completo, ni outcomes ni estudio AB-H confirmatorio. Endpoint local as-of con sellos conservadores hasta el segundo siguiente. Memorias IX/X del Congreso solo recuentos retrospectivos, PDF originales sin adquirir por derechos específicos no resueltos. SYSTEM20 20 disponibles.

**Visión y preguntas aún abiertas:** [Banco de ideas científicas de PFL (31/10/2026)](docs/BANCO_DE_IDEAS_CIENTIFICAS_PFL_20261031.md). Recoge expresamente política española, grandes empresas, poder económico, transparencia, promesas, implementación, efectos de políticas y dos finalidades complementarias: explicar y evaluar. **No sustituye el scope adoptado ni constituye resultados científicos.** Leerlo antes de redefinir el proyecto.

**Mandato de alcance científico amplio:** [Visión española y TFM](docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md) — recuperada de PR #5 y preservada en esta rama, con integridad SHA-256 comprobada. PFL es una infraestructura real española multiactor y bitemporal, no un juego ficticio como objetivo final. El estudio parlamentario, la monitorización BOE y la contratación pública son pilotos candidatos, no sustitutos del universo. La delimitación de los límites del sistema y su entorno sigue en [propuesta V0](docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md).

**Nueva orientación operativa, sin cierre académico (31/10/2026):** [Objetivo CoS de 20 ciclos](docs/OBJETIVO_COS_PFL_SYSTEM20_20261031.md) y [delimitación V0 del sistema político español](docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md). La prioridad teórica declarada es reproducción/autorregulación del sistema político; sus acoplamientos económicos, jurídicos y sociales mantienen peso sustantivo. El objeto específico del TFM sigue abierto. Concesión independiente en `research/PFL_SYSTEM20_20261031/AUTHORIZATION.json`; no inferir ciclos ejecutados por existir el objetivo.

**Piloto español de procesos reales:** [fuentes PDDL Canarias, cobertura y negativos](research/PFL_SYSTEM20_20261031/PARCAN_COHORTS/EVIDENCE_REPORT.md), [manifiesto original de tres fuentes y hashes](data/source_manifests/parcan_20261031.json) y [programa teórico/AB-H comparativo](docs/PROGRAMA_COMPARATIVO_SISTEMA_POLITICO_ABH_20261031.md). La primera auditoría conservó tres distribuciones y 1.211 registros de metadatos fuente-local. **Incremento posterior:** [PE/2025/XI](data/source_manifests/parcan_pe2025_20261031.json) añade una cuarta distribución oficial y 543 registros, llegando a **1.754** repartidos en dos cortes de auditoría conservados, sin sobrescribir los anteriores; [informe de tercera ronda](research/PFL_SYSTEM20_20261031/ROUND_REPORT3_20261031.md). Todos los originales y registros de ID/fecha están fuera de Git. La API `/api/spanish-process-cohorts?as_of=` representa conocimiento de **captura local**, nunca una primera publicación histórica, un censo parlamentario completo ni supervivencia. Congreso nacional sigue sin universo completo; Senado mantiene el bloqueo de condiciones de aceptación por uso. **SYSTEM20: 20/20 ciclos disponibles, 0 estudios confirmatorios.**

[Mapa por tareas](PROJECT_MAP.md) · [Catálogo buscable](PROJECT_INDEX.json) · [Investigaciones](research/INDEX.md) · [Handoff](HANDOFF.md) · [Cola técnica](tareas_codex/README.md).

`src/` contiene código; `tests/` pruebas; `research/` contratos, análisis y evidencia; `ab_atlas/` los lotes del proyecto; `tools/ab_atlas/` el motor fijado. Las copias archivadas no son código activo y el catálogo no certifica resultados.

## Dos líneas y una autoridad técnica

- **Producto:** capacidades completas y utilizables del prototipo ficticio; próximos hitos en el estado vivo. T005 no bloquea funcionalidades que pueden hacerse con datos ficticios.
- **Investigación:** pregunta social/institucional, rival competente y observación accesible; distinguir simulación, exploración y confirmación. Un test de software no es una observación humana nueva.
- `main` es la autoridad. Usar una rama corta por cambio/hito y devolverla mediante revisión; una conversación o ciclo conceptual no necesita su propia rama Git.
- El [inventario de ramas](BRANCHES.json) distingue la historia fuente de AB de las decisiones actuales. [Procedencia de la migración](docs/migration/README.md).

## Progreso sin rellenar cuotas

La política local del investigador prioriza producto e investigación por separado. No pedir nuevos ciclos por fórmula; usar el saldo aplicable sin obligación de agotarlo. [Acuerdo de trabajo](docs/WORKING_AGREEMENT.md).

Antes de un cambio de dirección, comparar tres rutas materialmente distintas. Tras dos intentos equivalentes bloqueados sin nueva observación, aparcar con condición de reapertura. No sustituir evidencia externa ausente por más semillas del mismo generador.

## Cierre de sesión

Guardar avances observados, negativos, evidencias, saldo y siguiente acción en `PROJECT_STATE.json` y los ledgers originales. Preparar los archivos previstos en Git; si cambian rutas, regenerar con `python scripts/project_index.py build`. Ejecutar `python scripts/project_status.py check`, generar `handoff` y guardar juntos los cambios.

Sin acceso de escritura, entregar estado/parche propuesto como **NO GUARDADO**. El [prompt reutilizable](NEW_CHAT_PROMPT.md) permanece breve: la información que avanza está en Git, no en el texto que copia el usuario.
