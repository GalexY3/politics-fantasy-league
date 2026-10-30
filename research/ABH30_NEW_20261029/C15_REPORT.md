# PFL · ABH30-C15 — correspondencia de oportunidades y recibos de visualización ficticios

**29/10/2026, AB-P acotado, DRIFT D1.** Rama `research/pfl-abh30-c15-five-arm-receipt-riskset-20261029`, padre PR #67 HEAD `b36dc5706fb1a192c2f5815431b2c8e43ce14f01`. Autorización antes: 14/30 ciclos nuevos válidos limitados, 16 sin consumir y 2 históricos separados STOP_R5. No confundir prueba del código con intervención humana.

## Resultado de producto e hipótesis

El contrato C14 separaba **granularidad cuartil/orden** y **audiencia privada/sala** en cinco brazos (`own_only, private_quartile, public_quartile, private_order, public_order`), pero solo verificaba la configuración. El módulo C15 `src/politics_fantasy/fictional_rank_delivery_audit.mjs` añade un flujo **estrictamente ficticio** de tres registros: asignación por miembro y sala, oportunidades con intervalos `[opens_at,closes_at)` y presuntos recibos de presentación emitidos como pruebas sintéticas. Importa y ejecuta **el contrato C14 exacto** antes de examinar los registros. Compara brazo, sala, miembro, oportunidad, plazo, *feedback* y audiencia; rechaza simultaneidad de brazos diferentes en una sala, replay de una oportunidad, duplicados de recibos, exposiciones fuera de riesgo y fuentes declaradas distintas del nombre de fixture.

**El detalle decisivo:** un brazo/oportunidad sin recibo se expresa como `unobserved_opportunities`, mientras `unobserved_opportunities: UNKNOWN_EXPOSURE_NOT_ZERO` impide asignar exposición nula a alguien cuya oportunidad no tiene constancia. El fichero de salida incluye **solo agregados por brazo**, no los identificadores ficticios. Un valor de texto `INDEPENDENT_SYNTHETIC_RENDER_LOG` es únicamente un indicador del fixture, **nunca evidencia criptográfica ni constatación de un renderizador real**.

## A–J ejecutados

**A. Problema:** evitar atribuir un tratamiento de ranking al participante por su configuración estática cuando la presentación concreta puede haber sido distinta, fuera de plazo o no registrada. Unidad = oportunidad sintética de exposición emparejada opcionalmente con recibo sintético.

**B. Hipótesis:** H1, cada recibo admitido coincide con brazo, sala, miembro, ventana y contenido del contrato; faltas de recibo quedan desconocidas. H0, duplicación, tratamiento erróneo o fechas inválidas pasan la auditoría. Rival: un simple campo `source` no da fe de independencia, y cinco fixtures ficticios no demuestran exposición humana ni causalidad.

**C. Prueba:** 20 casos congelados cubren positivo completo de cinco brazos, ausencia parcial y total de recibos, publicidad/granularidad errónea, reutilización del ID, doble registro por oportunidad, sala/brazo cruzado, tiempos, miembros desconocidos, contaminación de sala, falso origen, claves no previstas y contrato con pagos diferentes.

**D. Congelación:** código Git blob `db4df150fa73d26ee3ec40965586e4f3ca3c790f`, SHA256 `953459a239d69b0f77b6cd6293b4f4c8265b635deebcba2fd69986eb5d7b8d85`, test Git blob `ff04ef970dca3e5f68c98aa7f5818e6022287b1b`, SHA256 `94d916229a192dd2b3fd9a8423c447e55908126c517dd5e8081a5d5f7678e8fd`, dependencia C14 blob `cad226a589772de6c733929d32a527252d719ad6`. [Prerregistro A–J previo a ejecución](C15_PREREG_AJ_SHA.json) commit **`582035ac5d18ddb1ce2504cf0dba044225f61e9a`**.

**E. Ejecución:** se cotejaron los blobs Git y SHA256 del contenido ejecutado con los congelados; `Node v22.16.0`, `node --test tests/test_fictional_rank_delivery_audit.mjs`: **20/20 PASS, 0 fallos, exit 0** (primera ejecución, tras preregistro). SHA256 del TAP nativo `9614969cf829b77d8f90407d14622abfe3cdae2502de55fff558bc3d4472f0c4`. [Recibo](C15_RUN_RECEIPT.json).

**F. Auditoría de riesgos:** una oportunidad ficticia no es el universo real de oportunidades. Un recibo sintético no es un registro firmado; el *source string* no prueba origen independiente. No hay evidencia de renderizador en producción, asignación oculta, consentimiento, cobertura de missingness real ni interferencias entre personas. El comparador de sala impone homogeneidad de brazos pero no cuantifica spillovers.

**G. Control:** C14 auditaba JSON de configuración sin tiempos, recibos ni join con conjunto de riesgo; C15 comprueba una nueva propiedad (correspondencia de evento). `fictional_room_exposure.mjs` preexistente trataba cuatro brazos de otra familia; el experimento de cinco brazos sigue siendo una propuesta sintética.

**H. Priors:** PF-BR55 registra una inferencia negativa específica: no tratar ausencia de recibo como exposición 0 ni etiqueta de fuente sintética como autenticación real; no representa novedad empírica humana.

**I. Dictamen:** **un AB-P válido limitado**. CT2 científica 20/100 ordinal, nuevos N1/N2/N3 0/0/0, 0/6 gates; grado científico 0/3. C15 no acerca por sí mismo la verificación de entrega real o autorización para experimentos humanos.

**J. Decisión:** **15/30** nuevos ejecutados de alcance limitado, **15 nuevos pendientes**, **2 históricos STOP_R5** intactos. No consumir más ciclos en repeticiones de fixtures; siguiente criterio material: integrar realmente renderizador/servidor de un piloto ficticio con trazas no personales, medir desplazamiento de esfuerzo en tareas no clasificadas, o fuente humana independiente con permiso. Sin merge a main, ChatRelay, CI costosa, scoring de políticos ni datos personales.

