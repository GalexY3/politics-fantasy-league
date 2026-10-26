# Avance del proyecto — revisión 3 · 26 de octubre de 2026

**Índice de madurez vigente: 36,350 % (36,4 % en la aplicación).** El proyecto mantiene el **mismo alcance original PFL-V1-20261026**: 9 sublíneas, 36 hitos y los pesos originales. La puntuación no equivale a probabilidad de éxito, fracción de horas restantes ni calidad científica.

[Snapshot de revisión 3](../product/progress_snapshot_v3_20261026.json) · [Alcance computable](../product/progress_scope_v3_20261026.json) · [Anterior revisión 2](../product/progress_snapshot_v2_20261026.json) · [Método y pesos](PROGRESO_Y_ALCANCE_v1.md).

| Subvía | Peso | V2 | V3 |
|---|---:|---:|---:|
| Fuentes y datos | 18 % | 45,0 % | 45,0 % |
| Identidad, coaliciones e historial | 12 % | 40,0 % | 40,0 % |
| Eventos políticos | 10 % | 32,5 % | 32,5 % |
| Investigación y evaluación | 14 % | 27,5 % | 27,5 % |
| Mecánicas y motor fantasy | 16 % | 45,0 % | 45,0 % |
| Interfaz y experiencia | 10 % | 27,5 % | **32,5 %** |
| Privacidad, seguridad y licencias | 8 % | 20,0 % | 20,0 % |
| QA y reproducibilidad | 8 % | 40,0 % | **45,0 %** |
| Operación, piloto y despliegue | 4 % | 17,5 % | 17,5 % |
| **Global** | **100 %** | **35,450 %** | **36,350 %** |

**Cambio neto +0,900 puntos:** exclusivamente trabajo validado, **0 puntos de ampliación de scope**. Cambios justificados:
- `ui.pages` de nivel 2 a 3 por navegación de interfaz real con Chromium headless, panel de ocho candidaturas originales, mercado y progreso.
- `qa.endtoend` de nivel 2 a 3 por ejecución **nativa** del navegador sobre aplicación local, además de las pruebas Node/Python/HTTP del repositorio. El [runner 40316425686](https://github.com/GalexY3/Metodologia-AB/actions/runs/40316425686) pasó **3/3 jobs**: 98 pruebas Node, 59 pruebas Python y Chromium que validó las diez barras semánticas del progreso bajo una CSP restrictiva, sin excepciones JS, con rechazo Host 403.

El nuevo [BOE original de candidaturas de Albacete 2023](../data/observatory/boe_2023_albacete_verified.json) verifica ocho **listas históricas de una circunscripción**, pero aún **NO** acredita `src.registry` (padrón jurídico nacional del RPP), `id.real` (personas públicas reconciliadas), ni `ev.person` (eventos individuales longitudinales). No se incrementa ninguna de esas sublíneas por analogía.

**Seis gates críticos persisten:** registro original de partidos y candidaturas de alcance suficiente; identidad multifuente de personas; eventos verificables por persona/tiempo; autenticación/autorización; E2E completo más allá del smoke local; y despliegue seguro. El juego permanece demo local, con puntuaciones y personajes ficticios.

El método conserva tanto la fotografía V1 33,725 % como V2 35,450 %; V3 es actual. Si aumentase el alcance futuro, se produciría V4 con nuevas tareas o pesos y separando efecto trabajo/efecto scope, sin sobreescribir versiones. El análisis científico sigue independiente: VSDS 1/3 y CT2 20/100 (multiactor) y 24/100 (predictiva); no procede subir por tests de ingeniería.
