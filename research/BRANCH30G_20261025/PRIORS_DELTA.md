# PF-BR30G — priors acumulativos (apéndice, no reemplaza anteriores)

**PF-MG-01**. El importador de Congreso Abierto excluye del catálogo nominal las filas sin coincidencia exacta con un mapa de 350 nombres/códigos, reteniendo totales. Procedencia: blobs `2a9d63c7...`, `fed1b07b...`. Tipo: VERIFICADO_EN_CÓDIGO, no inferencia empírica causal. Favor: lectura del importador y TSV. Contra/alternativas: reglas de archivo, actualización y nombres distintos. Falsador: comparación original/derivado que no pueda explicarse por el mapa. Incertidumbre: cuánto explica de 34.654 posiciones.

**PF-MG-02**. Un registro no enlazado no equivale a «No vota». Procedencia: C02, pruebas fabricadas. Tipo: PRINCIPIO_INSTRUMENTAL, apoyado solo por 12 pruebas de ingeniería en local. Favor: categorias conservadas, ausencia nominal explícitamente no identificable. Contra: esquemas reales no inspeccionados; falsador: herramienta confunde categorías al aplicarse a original. Próxima acción: QA de JSON de campo.

**PF-MG-03**. Existe una fuente externa con marco longitudinal declarado de 412 personas, frente a 350 actuales en TSV de otra fuente. Procedencia: https://www.quienvota.org/ y C01. Tipo: METADATOS_EXTERNOS_NO_RECONCILIADOS. Favor: declaración del portal. Contra: distintos universos (2.176 vs 2.175 votaciones) y sesiones (147 vs 144). Falsador: emparejamiento que demuestre falta de comparabilidad del roster o de las fechas. No deducir «62 personas causaron 34.654 faltantes».

Nuevos N1/N2/N3=0; VSDS=1/3; CT2_predictivo=24/100. Retener priors anteriores y negativos, sin sobrescritura.
