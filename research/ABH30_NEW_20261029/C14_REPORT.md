# PFL · ABH30-C14 — Separación explícita de privacidad y granularidad del ranking

**Fecha 29/10/2026; AB-P contrato de producto de cinco brazos ficticios; DRIFT D2.** Rama `research/pfl-abh30-c14-rank-visibility-factorial-20261029`, apilada sobre el PR #65. **Un ciclo válido limitado, con un intento inicialmente INVALID registrado y posteriormente reparado, no dos ciclos.**

## Resultado principal

C12 identificó como antecedente externo de un experimento humano cuatro brazos con un **cuartil diario privado** de puntuaciones de peers; no demuestra el efecto de una **clasificación social pública**. Comparar directamente cuartil privado y clasificación pública completa mezclaría **dos dimensiones**: público/privado y cuartil/orden completo. C14 introduce `src/politics_fantasy/fictional_rank_visibility_contract.mjs` con **cinco condiciones exclusivamente ficticias**, cada una con el mismo motor de puntuación Brier virtual, oportunidades fijadas por SHA, calendario SHA y visualización del resultado individual:

| Brazo | Información adicional | Audiencia | Alias |
|---|---|---|---|
| `own_only` | Solo puntuación individual | Personal | No |
| `private_quartile` | Cuartil de posición | Personal | No |
| `public_quartile` | Cuartil de posición | Sala | Alias ficticio |
| `private_order` | Orden completo | Personal | No |
| `public_order` | Orden completo | Sala | Alias ficticio |

La disposición 2×2 identifica **contrastes planificables**, no efectos estimados: público vs privado a cuartil fijo; público vs privado a orden completo fijo; orden vs cuartil a audiencia fija; interacción de ambos componentes. El control `own_only` permite un contraste no comparativo. Las identidades/alias y posibles contagios entre miembros de una sala forman parte del mecanismo público: aun con paridad de configuración, el tratamiento `public_*` no está garantizado libre de interferencia. Las cinco condiciones son **un contrato para futuro diseño**, no alteran los cuatro brazos originales `control/transparency/leaderboard/both` ni son un ensayo con participantes.

## Secuencia A–J y reparación trazable

El primer código/test estaba congelado en el [preregistro inicial](C14_PREREG_AJ_SHA.json), commit **`cb6b06a69e813a54b610e062cbad2e6035ebfe7c`**. Los 18 casos de `node:test` pasaron 18/18, pero un intento adversarial **post hoc** identificó un fallo: `HEX.test(v.event_frame)` convierte implícitamente un **objeto JavaScript con método `toString()`** en cadena. El mismo objeto falsamente idéntico entre brazos pasaba la paridad y el sistema aceptaba la configuración no admisible. El fallo se reprodujo en **Node real**, y se conservó en [C14_INITIAL_INVALID_ATTEMPT.json](C14_INITIAL_INVALID_ATTEMPT.json). El estado de esa primera ejecución queda **INVALID_ATTEMPT**, aunque 18/18 inicialmente hubieran pasado; ningún ciclo se contó por esa ejecución.

Una **reparación explícita R1** fijó `typeof v.event_frame==='string'` y `typeof v.schedule==='string'` antes de regex, y añadió dos pruebas del ataque coercitivo. El [preregistro reparado](C14_REPAIR_R1_PREREG_AJ_SHA.json) se guardó en commit **`cb50ce4a84ebfdf98829b9d93fa3eafb945e331e`** con código blob **`cad226a589772de6c733929d32a527252d719ad6`**, SHA256 **`c007e0320e4ab5b4b2f1d3e7d37208828e70da253da47727547dff1f804f8c20`**; test blob **`cbbbfc6556502494c4d49ef6d3ee1d85abe87c55`**, SHA256 **`32651b31728146e9a422cab67c006fad5025f2a051c6bdccca3209c2a3b4f011`**, **antes de volver a ejecutar**. Tras comprobar hashes locales contra GitHub, **Node v22.16.0: 20/20 PASS, 0 FAIL, exit 0**, archivo TAP con SHA256 `b42c53b3719c3d041725c0fb486297bbcabc09cd103fa8f059eb7c668f34f092`. [Recibo completo](C14_RUN_RECEIPT.json).

## Contrato A–J

**A — Problema y estimando:** distinguir arquitectura experimental de audiencia pública/privada y granularidad del feedback, manteniendo constantes recompensas e instrumento de observación. El estimando humano sería un efecto de política de exposición sobre resultados, pero aquí no hay ningún resultado humano.

**B — Hipótesis rivales:** H1, un contrato de cinco brazos puede aislar cambios arbitrarios en configuración (rangos, recompensa, oportunidades, horario, identidad). H0, diferencias incontroladas pasan la validación. Rival fuerte: paridad de JSON estático no equivale a recepción efectiva del tratamiento, y los mecanismos de sala introducen interferencia.

**C — Diseño:** 18 casos originales, más dos adversariales de no-cadena tras el hallazgo del primer intento. Cumplimiento de esquema exacto, cinco brazos, cuatro factoriales, pseudónimos ficticios, paridad de hashes y recompensa Brier virtual.

**D — Freeze:** Git blobs y hashes de código/test congelados ANTES de cada suite nativa, con archivo de intento negativo e informe de reparación R1. No se modificó la fuente antigua de cuatro brazos.

**E — Ejecución:** primer run 18/18 fue invalidado por contraejemplo nuevo; repetición reparada **20/20 nativa** con paridad Git/SHA y salida TAP archivada. El primer fallo no se oculta.

**F — Adversarios y límites:** detecta cambios de público a privado, cambio de granularidad, identidades reales declaradas, desalineación de eventos y fechas, cambio de dinero virtual a real, campos de filas o supuestos recibos falsos. La herramienta **no autentica asignación, recepción, oportunidades observadas reales, consentimientos ni privacidad**. La seguridad de seudonimización y los efectos de redes requieren revisión aparte.

**G — Comparador:** el antiguo 2×2 de transparencia/leaderboard y el estudio AAAI de cuartil privado son fenómenos y diseños diferentes; contrastar `public_order-private_quartile` sería un **bundle**. Este protocolo permite discriminar hipótesis de resolución de rango y visibilidad que no podían separarse con el diseño simple.

**H — Priors:** actualizar PF-BR53 de diseño e invalidación de configuración no causal. No crear nueva fuente humana ni promover grado científico; conservar PF-BR50, 51 y 52.

**I — Dictamen:** **AB-P válido solo en su versión reparada**, ciencia PFL **0/3**, CT2 científica ordinal **20/100**, N1/N2/N3 nuevos **0/0/0**, lanzamiento **0/6**. Diseño no equivale a experimento ejecutado ni permite cuantificar efectos.

**J — Decisión:** contabilizar **C14 una sola vez**: 14/30 ciclos nuevos válidos limitados, **16 nuevos disponibles**, 2 históricos intactos STOP_R5. Aumentar intentos inválidos acumulados de 2→3 **sin aumentar ciclos inválidos** (primera ejecución reparada dentro del mismo ciclo). No main merge, CI costosa, ChatRelay, licencias/filas de participantes ni scoring de políticos reales.

