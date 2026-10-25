# PF-BR30G — informe INTERMEDIO, 25 de octubre de 2026

**Contrato:** 30 nuevos ciclos AB con BRANCHING empírico-productivo. **A–J completados: 2**, uno documental C01 y uno de ingeniería C02 con datos sintéticos. **No ejecutados: 28.** Cero validaciones nominales oficiales independientes. Los bloques históricos pendientes (12 B50, 45 libres, 19 AB20) se conservan aparte.

**Indicadores:** VSDS 1/3; CT2 predictiva 24/100 antes y después (juicio ordinal interno, NO probabilidad); N1/N2/N3 nuevos = 0. No sumar 12 tests de software como 12 experimentos.

## Evidencia contrastada

1. El archivo `data/raw/diputados_base.tsv` de MarcoAnarmo/CongresoAbierto (Git blob `fed1b07bbc8c592bc367be45ae21ece9a8c63e02`) tiene **350 nombres y 350 códigos únicos**. El importador `scripts/importar-votaciones.ts` (blob `2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e`) busca por nombre exacto; conserva los votos en totales/grupos aunque no resuelva su identificador.
2. La fuente externa https://www.quienvota.org/ declara **412 diputados históricos (350 activos), 2.176 votaciones, 761.568 registros nominales, 147 sesiones**. Es metadato publicado por otro proveedor, no un archivo fila a fila cotejado con el corpus antiguo (que contiene 2.175 votaciones y 144 sesiones); los universos y revisiones pueden diferir.
3. El JSON original de https://www.congreso.es/es/opendata/votaciones de sesión 193 (23/07/2026) está enlazado, pero la descarga de sus bytes ha fallado aquí. **No se cotejó ningún nombre original ni se identificó a los responsables de las 34.654 posiciones sin código.**

## C01 — A–J documental: contraste del mecanismo

**A** Estimando de diferencia entre censo actual e histórico, NO atribución de huecos. **B** H1 pérdida por catálogo de diputados actuales; H0 fallos de ingestión; H_otra diferencias temporales/metodológicas. **C** Comparación de código importador, TSV y metadatos externos. **D** Recuento de 350/350 únicos y referencias exactas a Git blobs. **E** Mecanismo técnico comprobado en fuente, cardinalidad histórica externa declarada 412. **F** La diferencia de 62 personas NO identifica a las personas ni la fracción causal de 34.654 posiciones; las dos fuentes no están emparejadas. **G** Contraste oficial por voto PENDIENTE. **H** Elevar prioridad de hipótesis de pérdida por resolución, no elevar confianza causal. **I** Evidencia técnica documental, no validación empírica nominal. **J** REPAIR_SOURCE.

## C02 — A–J de producción

**A** Instrumento para separar nombres nominales originales no resueltos, por cuatro categorías, y cotejar conjuntos de códigos de origen y derivado. **B** H1 nombres sin enlace; H0 enlaces completos; H_otra errores y colisiones. **C** Parear un JSON oficial, registro secundario y roster exacto; comprobar totales, conjuntos y fallos, emitir solo agregados y SHA-256. **D** `src/politics_fantasy/identity_reconcile.py`, `scripts/identity_reconcile_offline.py`, pruebas `tests/test_identity_reconcile.py`. **E** 12/12 pruebas locales sobre implementación análoga más CLI end-to-end ficticia; no se ejecutó la suite sobre checkout remoto ni microdatos oficiales. **F** Casos adversariales: campos desconocidos, códigos duplicados, identidades repetidas, conteos negativos y booleanos, ausencia de lista nominal. **G** Cero réplicas de campo. **H** Prior instrumental: ausencia de enlace ≠ «No vota». **I** Robustez parcial de software, no valor predictivo ni inferencia sobre personas reales. **J** CONTINUE_CONDITIONAL hacia cotejo oficial.

## Sociología y decisiones

La observabilidad del voto individual depende de la cadena **nombre oficial → diccionario de correspondencias → código indexado**. Si se confunde el último eslabón con la conducta de voto se introduce sesgo de medición potencialmente dependiente del tiempo y de la rotación legislativa. Sin identificación bitemporal y denominador de elegibilidad, no se sostienen tasas individuales de participación o disidencia basadas en filas ausentes.

**Prohibición operacional:** no asignar valor fantasy a políticos reales desde esa tabla retrospectiva ni entrenar pronósticos «as-of» sin fecha original de disponibilidad. Los **28 ciclos** C03–C30 siguen NOT_EXECUTED por R5; no se crean hallazgos por rellenar cuota.

**AB-DECIDE:** continuar el bloque autorizado cuando se obtengan originales nominales y roster histórico, o hacer producción focalizada en esa adquisición. **Informe intermedio: no corresponde solicitar más ciclos mientras queden 28 autorizados.**
