# AB-P 0.2 — Modo de proyectos; complemento operativo de AB 3.2.1-O7

**Estado:** propuesta implementada parcialmente en AB Atlas v0.2, pruebas de ingeniería exploratorias. No reivindica superioridad metodológica. Fecha de corte: 2026-10-26.

## 1. Ontología: proyecto ≠ investigación

AB-P gestiona la entrega de un resultado útil, deseable y verificable bajo restricciones y cambios de alcance. No requiere que la entrega sea una aportación científica nueva. AB-R investiga hipótesis y produce afirmaciones con alcance epistemológico declarado; AB-H permite que tareas de producto dependan de subproyectos de investigación, y viceversa, sin intercambiar sus validaciones. AB-META evalúa y eventualmente revoca el propio método.

La pregunta rectora de AB-P no es «¿qué hemos descubierto?», sino **«¿qué valor concreto entregamos, a quién, con qué evidencia de que funciona, qué está bloqueado y cuáles son sus costes y riesgos?»**.

## 2. Contrato mínimo obligatorio al inicio

1. **Outcome**: comportamiento/resultados observables, no actividades ni número de commits.
2. **Audience**: usuario, operador, destinatarios; declaración de necesidades no equivale a evidencia con usuarios reales.
3. **Scope**: requisitos dentro/fuera, versión explícita; cambios nunca reetiquetan objetivos históricos sin registro.
4. **Acceptances**: criterios binarios o medibles para entregables, fuente de evidencia y revisor.
5. **Gates**: condiciones críticas independientes del porcentaje de progreso (privacidad, seguridad, legal, calidad, datos, operación). Ausencia de gates ≠ listo; una exención documentada de un gate crítico ≠ gate superado.
6. **Dependency graph**: relaciones con semántica clara: `A depends_on B` significa «para terminar A se necesita B»; ramas e influencias tienen otro tipo de relación.
7. **Verification plan**: baselines y pruebas adecuadas (unitarias, contrato, integración, E2E, campo, aceptación, accesibilidad, amenazas), diferenciando *ejecutado* de *escrito*.
8. **Cost/risk**: estimaciones, recursos, impactos, prioridades. Desconocido se deja desconocido.
9. **Release strategy**: demo, alpha local, piloto controlado, producción; cada uno exige criterios diferentes.
10. **Operations**: mantenimiento, rollback, incidentes, documentación y traspaso.

Este contrato evoluciona. No hay necesidad de describir diez apartados completos en cada pensamiento o cada microtarea.

## 3. Ciclo nativo AB-P, compatible con A–J

| Código | Investigación AB-R (lógica original) | Proyecto AB-P (operación equivalente, no extrapolación de evidencia científica) |
| --- | --- | --- |
| A | Formular problema | Resultado esperado y usuario con necesidad concreta |
| B | Antecedentes y priors | Estado actual y restricciones, precedentes y alternativas |
| C | Hipótesis y rivales | Supuestos de entrega, riesgos, opciones de diseño |
| D | Falsadores | Criterios de aceptación y condiciones de fallo |
| E | Experimento/protocolo | Unidad de trabajo y plan de verificación |
| F | Ejecución | Construcción/integración/ensayo con evidencias |
| G | Resultados | Comportamiento demostrado y límites de ejecución |
| H | Auditoría | Defectos, complaints, riesgos, fallos de información y costes |
| I | Dictamen | Aceptado/rechazado/parcial/bloqueado, con gate de liberación separado |
| J | Actualización | Grafo, backlog y alcance versionados; siguiente acción, parada o pivot |

**Un ciclo puede cerrar una incidencia sin desarrollar una teoría.** Si una tarea es trivial, se admiten microciclos AB-P con recibo ligero y enlaces a evidencia, sin forzar prosa ceremonial. Para cambios científicos profundos, sí corresponde A–J completo de AB-R.

## 4. Navegación mediante fases (son vistas, no flujo rígido)

- Descubrir (`discover`): destinatarios y necesidades; alternativas de solución.
- Definir (`specify`): límites y criterios observables.
- Construir (`build`): implementación, decisiones, prototipos y documentación.
- Verificar (`verify`): pruebas y evidencia de aceptación.
- Entregar (`release`): gates, entorno, permisos y puesta en uso.
- Operar (`operate`): cambios, fallos, costes, soporte y aprendizaje.

Un descubrimiento tardío puede reabrir definir; fallar la prueba puede devolver una funcionalidad a construir; un rechazo de usuario puede reabrir descubrir. No se finge avance lineal.

## 5. Medición con disyunciones explícitas

- **Madurez contra alcance** (opcional): aplicar esquema de pesos/snapshot si se dispone de uno, como el modelo PFL-V1. No confundir con % de trabajo restante, valor, calidad o probabilidad de éxito.
- **Aceptación**: contar entregables con criterios, evidencia y verificador; no significa aceptación real por usuarios externos si no se han involucrado.
- **Readiness**: gates críticos, con bloqueo por defecto cuando no se han definido o no están acreditados.
- **Eficiencia**: coste total por unidad de valor entregado, incluyendo QA, reparación, mantenimiento y overhead de AB. No premiar líneas de código, volumen de experimentos ni tickets cerrados sin resultado.
- **Investigación**: CT2 (ordinal y no calibrado), VSDS y novedad 0/3–3/3 mantienen su semántica y no se recalculan por avance de producto.

## 6. Politics Fantasy como prueba adversarial

Snapshot repositorio 26/10/2026, PFL-V1 revisión 3: madurez declarada 36,350%, producto local con personajes ficticios, pruebas del navegador Chromium en CI. Seis gates críticos pendientes: registro de partidos, identidad individual, eventos atribuibles por persona/tiempo, autenticación/autorización, E2E más allá de un smoke, despliegue seguro. No inferir puntuaciones reales ni perfiles de personas. El grafo v0.2 lleva estas seis condiciones de forma explícita. Los resultados de BOE sobre candidaturas no se imputan indebidamente a un padrón jurídico de partidos ni a identidad personal.

**Recomendación:** integrar este esquema junto al progreso ponderado ya desarrollado en Politics Fantasy, no sustituir los datos y pesos propios de PFL por un simple recuento de nodos.

## 7. Automejora y complaints

Una ejecución AB-P genera recibo inmutable de actividad, estado, versión metodológica, alcance y evidencias. Una complaint puede surgir de humano, test, auditor o agente. Distinguir señal de defecto confirmado; conservar raíz causal hipotética y verificada por separado; deduplicar cuando corresponde; reparar sin reescribir históricos. Una queja recurrente contra una norma de AB abre AB-META (hipótesis de menor coste/mayor utilidad frente a alternativa competente), **no un cambio automático de la metodología**. Si AB perjudica, retirar la norma o sustituir AB es un resultado aceptable.

## 8. Estado implementado y pendiente

**Implementado/ensayado:** scaffolds universales, grafo JSON, CLI atómica, aceptación documentada, gates con evidencia, scope versionado, navegación de dependencias, heurística de siguiente acción, recibos y complaints, visor oscuro profesional y móvil, importación/exportación autónoma, smoke Chromium.

**Pendiente:** validación automática de la autenticidad de referencias, sincronización GitHub/Drive, edición concurrente y control de conflictos, acceso privado multiusuario, comparación controlada AB-P vs gestor profesional, rendimiento para miles de nodos, mapeo semántico exhaustivo de repositorios, backups/snapshots automáticos, E2E completo del ciclo de importación/exportación y despliegue web seguro. **No etiquetar la propuesta como producto terminado de producción.**
