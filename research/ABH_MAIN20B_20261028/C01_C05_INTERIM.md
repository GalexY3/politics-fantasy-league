> **Nota de actualización del expediente (28/10/2026):** llegó evidencia original de Codex T008, que efectivamente pasó **651 tests + 28 subtests** bajo Alpine/QEMU en `b0344d1`. También hubo checker nativo de **35 lotes** en `9d0ef84`. Ambas pruebas son históricas y se preservan como tales; **el full pytest y Atlas de 60 lotes de `main` siguen sin ejecutar**, ahora agrupados en [T009](../../tareas_codex/T009_MAIN_LINUX_ATLAS60.md). La conciliación no es otro ciclo AB; el balance MAIN20B sigue en 5 válidos y 15 autorizaciones disponibles. [Informe de procedencia](../../tareas_codex/T008_RECONCILIACION_MAIN_20261028.md).

# Campaña AB-H MAIN20B · avance C01–C05 · 28/10/2026

**Autorización del usuario:** 20 ciclos branching, sin obligación de gastar cuota; campaña independiente de BRANCH20 (cerrada 19 válidos, 1 inválido). **Ejecutados en esta etapa: 5 válidos, 0 inválidos, 0 planificación, 15 pendientes de utilización.** Se usa `main`, sin crear ramas. La prioridad R5 prevalece sobre repetir pruebas sintéticas o búsquedas sin nuevos instrumentos.

## A–J y decisiones por ciclo

| Ciclo | Contraste y decisión | Ejecución comprobada y límite |
|---|---|---|
| **C01 AB-META** | Endurecer sintaxis de `at` en el Atlas, sin reescribir los 55 lotes heredados. **REPAIR acotado.** | 55/55 timestamps históricos parseados como ISO-aware; 4 controles inválidos rechazados y 2 positivos admitidos mediante Python 3.13.5. `ab_atlas/atlas_delta.py` y `ab_atlas/tests/test_delta_timestamps.py` modificados. Detectado retroceso temporal **1534 segundos** entre lotes 0015 y 0016; cadena padre no equivale a reloj estrictamente creciente. *Suite completa y replay nativo aún NOT_RUN.* |
| **C02 AB-R** | Concordancia XML/JSON en una votación del Congreso XV, sesión 202 (30/09/2026). **INCONCLUSIVE por acceso.** | Dos páginas HTML institucionales coinciden en **137 sí, 175 no y 34 abstenciones** para el expediente 162/000814; XML y JSON originales no recuperados. No existen SHA de bytes ni certificado de equivalencia entre formatos. No inferir no-voto a partir de 346. |
| **C03 AB-R** | Diferenciar derechos generales de reutilización de un fundamento lícito específico para puntuar personas. **CONTINUE con gate bloqueado.** | Fuentes del aviso legal del Congreso, Ley 37/2007 y AEPD inspeccionadas; [matriz documental](../../docs/RIGHTS_AND_PERSON_SCORING_GATE_20261028.md). Términos generales detectados, no autorización suficiente para perfiles individuales. Sin datos nominales recopilados. |
| **C04 AB-R** | La moda/pluralidad 4/9 se presentaba como mayoría en un indicador individual de discrepancia. **REPAIR acotado.** | Viejo cálculo: 5 votos «disidentes» ante un ganador modal 4/9; función nueva exige >50 % de expresados y devuelve elegibilidad 0 cuando no existe. API previa preservada. 11 controles aislados Python superados; pruebas nuevas en `tests/test_strict_group_dissent.py` requieren suite integral. |
| **C05 AB-R** | Diferenciar media por sesión y media por observación en bootstrap por conglomerados. **BRANCH a estimando explícito.** | En 100 ceros de sesión A y un diez de B: media sesiones = **5**, media registros = **10/101 ≈ 0,0990**. Nuevo `record_weighted_cluster_bootstrap_ci` remuestrea sesiones completas; 9 controles aislados Python superados. Se conserva `session_bootstrap_ci` para su estimando original. Ninguna validación empírica. |

## Referencias por ciclo

- `C01_PREREG.json` · `C01_RESULT.json` · Atlas `0056`
- `C02_PREREG.json` · `C02_RESULT.json` · Atlas `0057`
- `C03_PREREG.json` · `C03_RESULT.json` · Atlas `0058`
- `C04_PREREG.json` · `C04_RESULT.json` · Atlas `0059`
- `C05_PREREG.json` · `C05_RESULT.json` · Atlas `0060`

## Fuentes primarias consultadas

- Catálogo institucional: https://www.congreso.es/es/opendata/votaciones?targetDate=30%2F09%2F2026&targetLegislatura=XV
- Ficha institucional: https://www.congreso.es/es/proposiciones-no-de-ley?_iniciativas_id=162%2F000814&_iniciativas_legislatura=XV&_iniciativas_mode=mostrarDetalle&p_p_id=iniciativas&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal
- Aviso legal del Congreso: https://www.congreso.es/eu/cem/aviso-legal
- Ley 37/2007, texto consolidado BOE: https://www.boe.es/buscar/act.php?id=BOE-A-2007-19814
- AEPD, bases jurídicas del tratamiento: https://www.aepd.es/preguntas-frecuentes/2-tus-obligaciones-como-responsable-del-tratamiento/5-bases-legitimadoras-del-tratamiento/FAQ-0214-cuales-son-las-bases-de-legitimacion-para-el-tratamiento-de-datos

## Estado de infraestructura y CT2

**Atlas documental actual:** 60 lotes, 63 nodos, 81 relaciones, 226 runs, 48 incidencias y 401 operaciones. Estos son recuentos derivados (55 previos + cinco `run.add`); **checker canónico Python 60 y SHA del estado reconstruido: NOT_RUN/UNKNOWN**. El hallazgo de la revisión C19 sobre timestamps está mitigado a nivel de preflight, pero no puede cerrarse la incidencia de sistema sin T008.

**T008 sigue aplazada:** checkout completo `main` en Linux/POSIX, ejecución de todas las pruebas (incluidas las nuevas) y checker canónico **60 lotes**. No se ha lanzado GitHub Actions costosa ni desplegado sistema multiusuario.

**Indicadores sin promoción artificial:** CT2 identidad 29/100 **ordinal** (no probabilidad), VSDS 1/3, V4 36,90 % contractual, descubrimientos nuevos N1/N2/N3 = 0/0/0, gates críticos superados = **0/6**. En ningún momento se ha puntuado una persona política real.

## AB-DECIDE / siguiente evidencia

**STOP_R5** para continuar reconsultando HTML sin XML/JSON original, reiterar la misma consulta jurídica sin derechos específicos, o buscar otra semilla sintética para la pluralidad y el bootstrap. **Conservar 15 autorizaciones activas y sin consumir**. La siguiente observación discriminante requiere uno de estos instrumentos realmente nuevos: acceso comprobable a bytes originales oficiales; revisión jurídica concreta para la finalidad de datos personales; denominador histórico de pertenencia acreditado; o un checkout completo para pruebas integrales. No hay solicitud de nuevas autorizaciones porque quedan 15 concedidas.

Esta es una **entrega intermedia** de campaña, no un informe de cierre con 20 resultados.
