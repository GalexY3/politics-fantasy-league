# Priors AB30D — incorporación y procedencia

Estado científico: simulaciones y análisis posthoc de instrumentación; **no trasladar a datos españoles**.

- PFL-P0301 (refuerza prior de identificación): ponderar un cuadro por grupos no identifica el resultado si la ausencia depende del outcome dentro de grupo. Fuente: M03, código preregistrado, comparación sintética con generador MNAR. Evidencia a favor: error aumentó respecto a otro procedimiento en holdout sintético. En contra / incertidumbre: la tasa y el patrón MNAR son estipulados. Siguiente falsador: contrastar cobertura en fuentes oficiales independientes.
- PFL-P0302 (prior técnico contra regularizar a ciegas): reducir varianza de un estrato escaso mediante shrinkage puede empeorar error si hay cambio de mecanismo. Fuente: C09: mejora en régimen principal, revierte en estrés. No novedoso; la inversión depende de parámetros. Falsador: regularización evaluada en series de grupos con cambios observados temporalmente.
- PFL-P0303 (leakage): variables o revisiones publicadas después del corte vuelven invalida cualquier superioridad desplegable. Fuente: T13/T17 F-adversarial, comparación explícitamente no paritaria. No novedad; identidad de disponibilidad, no evidencia empírica.
- PFL-P0304 (falsa equivalencia de escalas): comparar un grado crudo con densidad, o acuerdo total con exceso de azar, mezcla estimandos. Fuente: R22, R19 auditoría posthoc. Contra: en un proyecto podrían ser ambas métricas útiles pero cada una tiene su pregunta y baseline propios.
- PFL-P0305 (Goodhart condicional): seleccionar un proxy optimizable cuya relación con el outcome se degrada por esfuerzo de optimización puede perder valor verdadero **por construcción**. Fuente: F27, generador controlado y ablación. No hay evidencia de un efecto equivalente sobre política española. Siguiente evidencia: score con etiquetas independientes y regla de no incentivos perversos.

Novedades científicas acreditadas 0, VSDS 1/3, CT2 24/100.
