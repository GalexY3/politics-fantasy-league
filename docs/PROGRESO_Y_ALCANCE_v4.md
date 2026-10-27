# Politics Fantasy League · Progreso V4 — revisión evidencial 27/10/2026

**Índice contractual nuevo: 36,900 % (36,9 % en pantalla).** Revisión anterior V3: **36,350 %**. Incremento **+0,550 puntos porcentuales por evidencia documental aceptada**, no por más ciclos ni cambios de alcance. Peso, definición y cardinalidad idénticos: **9 sublíneas, 36 hitos**. Documento computable: [V4 scope](../product/progress_scope_v4_20261027.json) · [V4 snapshot](../product/progress_snapshot_v4_20261027.json) · [auditoría de 36 hitos](../research/ABH_BRANCH45_20261027/R01_MILESTONES.json). V3 queda intacta.

| Subvía | Peso | V3 | V4 | Aportación ponderada V4 |
|---|---:|---:|---:|---:|
| Fuentes y datos | 18 % | 45,0 % | 45,0 % | 8,10 pp |
| Identidad, coaliciones e historial | 12 % | 40,0 % | **42,5 %** | 5,10 pp |
| Eventos políticos | 10 % | 32,5 % | **35,0 %** | 3,50 pp |
| Investigación y evaluación | 14 % | 27,5 % | 27,5 % | 3,85 pp |
| Mecánicas y motor fantasy | 16 % | 45,0 % | 45,0 % | 7,20 pp |
| Interfaz y experiencia | 10 % | 32,5 % | 32,5 % | 3,25 pp |
| Privacidad, seguridad y licencias | 8 % | 20,0 % | 20,0 % | 1,60 pp |
| QA y reproducibilidad | 8 % | 45,0 % | 45,0 % | 3,60 pp |
| Operación, piloto y despliegue | 4 % | 17,5 % | 17,5 % | 0,70 pp |
| **Global** | **100 %** | **36,350 %** | **36,900 %** | **36,90 pp** |

### Únicos hitos promovidos: nivel 0 → nivel 1

- `id.real` (peso efectivo 3 % del proyecto): **+0,300 pp**. Ahora existe **especificación contrastada** para enlaces persona-fuente: 11 continuidades públicas positivas entre legislaturas respaldadas por biografías del Congreso/La Moncloa, un caso de dato biográfico oficial contradictorio y reglas de custodia. **No** se certifica identidad multifuente poblacional, homónimo negativo ni incorporación segura al producto.
- `ev.person` (peso efectivo 2,5 % del proyecto): **+0,250 pp**. Se han documentado eventos individualizados y fechados de condición plena y credenciales en BOCG XV-D-51 (2023) y XV-D-390 (2025), y contraste DSCD/perfil oficial de 2026. **No** se ha demostrado un corpus sistemático reconciliado con disponibilidad `as_of` ni un pipeline E2E.

El nivel 1 tiene valor **0,10**, de acuerdo con la tabla V3. Los otros **34 hitos mantienen exactamente su nivel y denominador**. No se adjudica nivel 2/3/4/5 por documentación o archivos de tests que todavía no se ejecutaron.

### Riesgos y restricciones que no cambian

**0/6 gates críticos de lanzamiento superados:** falta registro RPP por partido con originales y cobertura, identidad real con adjudicación/ambigüedad controlada, eventos en producción con procedencia verificable, autenticación multiusuario, E2E completo del flujo real y despliegue seguro. `qa.endtoend` V3 permanece en nivel 3 por ejecución de demo anterior, no por los nuevos tests HTTP, que siguen pendientes.

El índice mide **madurez frente a un alcance contractual ponderado**, no probabilidad de éxito, avance cronológico, porcentaje de electos ya registrados ni calidad científica. **CT2 29/100, VSDS 1/3 y N1/N2/N3 nuevos = 0** permanecen fuera del cálculo. Los resultados de la investigación AB-R no deben reflejarse dos veces.

Esta V4 revisa evidencia anterior una sola vez, bajo una auditoría explícita de los 36 hitos. Conservar la V3 es obligatorio para comparaciones `work_effect=+0.55` y `scope_effect=0`.
