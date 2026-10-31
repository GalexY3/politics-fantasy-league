# P02 · Integridad de la revisión doble documental

**Antes de resultados. AB-P sintético.** No certificación de personal, independencia humana ni enlaces normativos.

**A. Pregunta.** PP04C contrasta pseudónimos distintos pero no vincula identidad de sesión a una asignación o a una edición. Estimando de producto: cuántos de cinco ataques sintéticos se rechazan y cuántos de cuatro controles legítimos se preservan.

**B. Rivales.** B0 independent_review_gate de PP04C. B2 doble pseudónimo más formato estricto. B1 requiere asignación previa para cada par y dos ranuras con actor interno distinto, mismo SHA de edición y desacuerdos preservados, sin dar el enlace por autenticado. H1: B1 rechaza cinco de cinco ataques, preserva cuatro de cuatro controles, y B0 admite al menos un ataque. H0: B0 basta o B1 rompe controles.

**C. Falsadores.** Mismo actor bajo dos pseudónimos; par no asignado; SHA de otra edición; desacuerdo convertido en vínculo; votación duplicada de una ranura. Controles: acuerdo sin certificado jurídico; desacuerdo; UNKNOWN deliberado; dos pares N:1 que no se colapsan. Sin nombres ni PII y sin contraseñas reales.

**D. Instrumentación.** Python puro, rol/actor completamente sintético y manifiesto de asignación de edición. El estado SELLADO quiere decir no entregar dictamen agregado hasta dos respuestas válidas, NO criptografía ni verdadera prueba de persona independiente. Cero rutas de red, fuente, PDF o caso español.

**E. Ejecución.** Commit congelado de A-J, código y tests antes de observar ataques y controles, comparación baseline con mismos datos.

**F. Auditoría.** JSON con campos extra, SHA incorrecto, duplicidad de actor/slot, usuario no asignado, rights falsos, conflicto de decisiones. B0/B2 no deliberadamente desinformados de las asignaciones.

**G. Verificación adicional.** Permutaciones de ranuras y registros N:1, por pruebas distintas de los cinco casos primarios; no afirmar replicación externa.

**H. Revisión.** Distinción estricta entre integridad del expediente local, independencia humana efectiva y autenticidad jurídica de fuente.

**I. Alcance.** Un contrato funcional de producto, no firma electrónica, identidad del revisor ni cumplimiento de PAN; R5 STOP, sin niveles 2/3.

**J. Regla.** Un máximo de un ciclo AB-P si pasa ataques, controles, y comparación diferenciadora; en otro caso REPAIR o STOP preservando resultados fallidos. No DONE del producto sin aceptación.
