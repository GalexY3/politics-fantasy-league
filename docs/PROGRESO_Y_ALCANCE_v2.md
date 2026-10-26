# Progreso del proyecto · Revisión 2 adoptada · 26/10/2026

**Porcentaje actual:** **35,450%** (35,5% en interfaz). [Alcance V2](../product/progress_scope_v2_20261026.json) y [fotografía computada](../product/progress_snapshot_v2_20261026.json). **El alcance de producto PFL-V1-20261026 sigue siendo el mismo**: nueve sublíneas y 36 hitos. La revisión incrementa solo dos niveles de madurez por evidencias observadas en [BR12M](../research/BRANCH12M_20261026/REPORT.md).

| Sublínea | Peso global | Madurez revisión 1 | Madurez actual |
|---|---:|---:|---:|
| Fuentes y datos | 18% | 38,75% | **45,00%** |
| Identidad, coaliciones e historial | 12% | 40,00% | 40,00% |
| Eventos políticos | 10% | 32,50% | 32,50% |
| Investigación y modelos | 14% | 27,50% | 27,50% |
| Juego y economía fantasy | 16% | 45,00% | 45,00% |
| UI y experiencia | 10% | 27,50% | 27,50% |
| Seguridad y derechos | 8% | 20,00% | 20,00% |
| QA y reproducibilidad | 8% | 32,50% | **40,00%** |
| Operación y lanzamiento | 4% | 17,50% | 17,50% |
| **Global** | **100%** | **33,725%** | **35,450%** |

Cambio = +1,725 puntos de trabajo, 0 de alcance, por la convención de descomposición «primero trabajo, luego scope». Se conservan los artefactos V1 sin modificación. El ejemplo `progress_scope_v2_EXAMPLE_NOT_ADOPTED.json` describe **otra revisión 2 ficticia creada antes** para explicar qué ocurriría al ampliar objetivos y **no debe confundirse con esta revisión 2 realmente adoptada**.

### Qué ha cambiado la evidencia

- `src.catalog` subió de madurez 3 a 4. Un documento BOE original se obtuvo por HTTPS institucional, su SHA-256 se calculó desde 1.915.000 bytes y se compararon automáticamente 312 cifras originales con el archivo secundario. Se trata de datos electorales agregados de 2023, **no del Registro completo de Partidos ni de personas actuales**.
- `qa.endtoend` subió de madurez 1 a 2. Las pruebas Node, Python y HTTP local pasaron de ejecutables documentados sin verificación a logs nativos comprobados: 91 Node + 50 Python sin fallos, workflows Actions completos. **No ha habido prueba visual/browser E2E ni piloto público multiusuario**, por eso el nivel se mantiene en 2.

### Restricciones que no han cambiado

El indicador NO mide valor sociológico ni calidad intrínseca de políticos. Sigue sin existir autenticación multiusuario o despliegue público. Quedan seis gates: registro original de partidos/candidaturas, identidades reales verificadas, eventos individuales admisibles, autenticación, E2E completo y despliegue. No subir nivel por haber creado tests sin ejecutarlos.

VSDS=1/3, CT2 multiactor 20/100 y predictiva parlamentaria 24/100 (ordinales), N1/N2/N3=0. En futuras campañas crear revisión 3, conservar V1/V2, registrar justificantes y descomponer variación en trabajo frente al nuevo denominador. Metodología matemática, niveles y ponderación original en [v1](PROGRESO_Y_ALCANCE_v1.md).
