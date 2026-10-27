# Politics Fantasy League · AB-H: cierre de la campaña 20 + 5 + 20

**27-10-2026 · Rama:** `research/pfl-abh-45-20261027` (sin fusionar a `main`). **Autorización completada: A01–A20, R01–R05, B01–B20 = 45/45 ciclos registrados y 0 disponibles.** Se ha aplicado R5 a líneas que no aportaban evidencia nueva. Esto no significa 45 experimentos científicos confirmatorios ni una app lista para publicación. [Ledger de 45 ciclos](CAMPAIGN_FINAL_A20_R5_B20.json).

## Estado cuantitativo vigente

V4 **36,90 %** de madurez contractual, +0,55 puntos sobre V3 36,35, con 36 hitos y 9 subvías ponderadas: fuentes **45 %**, identidad **42,5 %**, eventos **35 %**, investigación **27,5 %**, motor fantasy **45 %**, interfaz **32,5 %**, privacidad/seguridad **20 %**, QA **45 %**, operación **17,5 %**. Solo `id.real` y `ev.person` pasaron nivel 0→1 *especificado*: el resto se mantuvo. El porcentaje no mide probabilidad de lanzamiento ni precisión predictiva.

**Gates de lanzamiento: 0/6. CT2: 29/100 ordinal. VSDS: 1/3. N1/N2/N3 nuevos: 0/0/0.** La demo permanece local y sintética. Los cambios de parser y fuente no validan puntuaciones de políticos reales.

## Revisión profunda R01–R05

[Recap integral de producto](RECAP_INTEGRAL_R05.md), [36 hitos auditados](R01_MILESTONES.json), [auditoría científica](R03_DISENO_VALIDACION.md), [auditoría de seis gates](R04_AUDITORIA_READINESS.md) y [V4](../../docs/PROGRESO_Y_ALCANCE_v4.md). La investigación histórica encontró once continuidades positivas verificadas con biografías oficiales, ningún homónimo exacto diferente-persona adjudicado, ejemplos de disociación de fechas de credencial/condición plena, y discrepancia de DOB institucional. No hay corpus persona-semana sellado ni experimento prospectivo con baselines y publicación `as_of` original certificada.

## Segunda tanda B: controles realmente ejecutados sobre originales

Los **11 archivos originales** del ZIP privado conservan hashes, longitud y CRC íntegros respecto del manifiesto. Los ficheros personales permanecen privados, fuera de Git.

- **Congreso:** con el parser GitHub verificado byte a byte se validaron **4 JSON originales**, **1.400 filas nominales**, **67 sentinelas `asiento=-1`**, totales de categoría reconciliados. Se encontraron dos defectos reales: `totales=null` producía `AttributeError` en lugar de rechazo controlado; asiento `001` podía pasar. Se corrigieron con tests nuevos.
- **Senado:** se validó `sesion60.xml` original con **10 votaciones, 2.589 filas de voto y 51 ausencias**. La sesión se rotula 07/10/2025, los diez eventos son del 08/10/2025, **sin deducir `first_public_at`**. Se corrigieron etiquetas `NO VOTAN` frente a singular no oficial y meses españoles `ABR/AGO/DIC`, y se impidieron duplicados de escaño *dentro del mismo voto* y de `num_vot`/`CodVotacion` *dentro de la misma sesión*. Ninguna de estas claves identifica a una persona longitudinalmente.
- **Pruebas actuales conjuntas:** **23 casos nativos** de `unittest` con código y tests cuyos hashes Git coincidían con los de la rama; **23/23 PASS**. Se reconciliaron además los **14 eventos de voto originales** (4 Congreso + 10 Senado). Una primera selección de tests por glob solo cubría 13 del Senado; la ejecución correcta usó `test_source_original*.py`, se registró y pasó.
- **GitHub CI opcional:** `.github/workflows/politics-fantasy-evidence.yml` incorpora ese glob sin publicar los originales. **No se disparó workflow, no se consumieron minutos de Actions en esta campaña**, y aún no se puede afirmar E2E limpio de repositorio/servidor.

El cómputo V4 se verificó nuevamente a partir del JSON real, las 36 rutas `evidence_ref` existen en la rama, pero la API Python completa no se ejecutó nativamente. **Existencia de archivo no acredita verdad documental**.

## Pendientes que impiden promoción artificial

- Identidad jurídica individual de partidos: el buscador público RPP está identificado, pero no se obtuvo una inscripción original firmada; anuarios 2020–2021 son agregados y descarga XLSX 2021 devolvió 502.
- Historias de condición plena: algunos BOCG y DSCD contienen fechas efectivas y origen institucional, pero no se conserva recibo independiente de `first_public_at` de cada documento ni corpus completo histórico.
- Servidor: `GET /api/source-stages` de solo lectura se integró en rama y sus cuatro tests HTTP fueron escritos, **no corridos en un checkout E2E completo**. Auth multiusuario ausente.
- Atlas: se reprodujeron **13 lotes** reales sobre seed vía un comprobador JS independiente, total **52 nodos, 72 relaciones, 66 runs, 29 complaints, 197 operaciones**, con gates coherentes; **no se ejecutó el validador oficial Python**. El lote siguiente `0014` incorpora los 20 ciclos B al grafo y necesitará comprobación estructural propia.
- Privacidad y derechos: accesibilidad pública de los boletines no equivale a permiso sin condiciones para reutilizar perfiles personales y valorarlos políticamente. No hay criterio científico causal de “mérito”.

## Recomendación tras el cierre

**No repetir series de veinte tests sobre el mismo XML para aumentar el porcentaje.** Los bugs hallados eran reales y están corregidos; la prioridad ahora es integrar y verificar esos controles en una ingesta autoritativa, obtener originales de RPP y fuentes temporales verificables, establecer una muestra adversarial de identidad con negativos, cerrar seguridad y derechos de uso y construir un primer test externo fuerte persona-semana si la evidencia lo permite.

No se ha autorizado otro bloque más allá de B20. El final de los 45 ciclos es un **cierre de cuota y trazabilidad**, no una afirmación de que el proyecto haya alcanzado madurez científica o de despliegue.
