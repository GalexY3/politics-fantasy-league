# PF-BR20H — actualización acumulativa de priors (25-10-2026)

Conservar los priors PF-P01–P12 y PF-MG-01–10 de las campañas anteriores sin modificarlos silenciosamente. Esta campaña expande el universo poblacional, no incrementa por sí misma el conocimiento causal sobre España.

## PF-H01 — Inscripción ≠ candidatura ≠ representación
Procedencia: LOREG art. 44 y LO 6/2002 (consulta documental) + test C02/C09. Naturaleza: distinción jurídico-conceptual (documental) y regla de diseño implementada. Favor: fuentes primarias normativas, tipos diferenciados. Contra/limitaciones: las categorías no demuestran el éxito de integrar los registros reales; no se ha descargado padrón exhaustivo. Falsador instrumental: un ejemplo legal válido no puede representarse sin fusionar dos de las unidades. Decisión: RETAIN, alcance limitado.

## PF-H02 — El ecosistema observable excede los órganos legislativos
[Inferencia] Una población de actores públicos que incluya portavoces, candidaturas, plataformas y organizaciones de interés puede producir un observatorio más inclusivo que el basado únicamente en votos del Congreso. Evidencia favorable: la ontología con 9 ENTIDADES TOTALMENTE INVENTADAS admite 2 personas sin mandato observado y 7 organizaciones (C03/C12/C20). Evidencia contraria: es una consecuencia del modelo construido, NO comprobación de cobertura, representatividad ni de actividad política real. Falsador: un corpus real de interés no añade eventos verificables fuera de parlamentos o resulta imposible documentarlos con igualdad razonable. Estado: HIPÓTESIS_NO_VALIDADA.

## PF-H03 — Ausencia de información no prueba ausencia de escaño ni influencia
Procedencia C18; estado: NORMATIVO/MATEMÁTICO_DE_DATOS. A favor: modelo con UNKNOWN distinto de ABSENT; en fixture 7 organizaciones tienen UNKNOWN, no cero escaños inferidos. Contra: sin censo electoral se desconocen estados institucionales reales. Falsador: contraejemplo donde algoritmo infiere ABSENT solo por ausencia de relación. RETAIN.

## PF-H04 — Candidatura no identifica afiliación a partido
Procedencia LOREG art. 46 sobre independientes y miembros en coaliciones, test C09. A favor: relación CANDIDATE_FOR separada de membresía; fixture controlada. Contra: identidad partidaria real depende de registros y fuentes específicas; falta parser de proclamas. Falsador: software genera afiliación sin fuente explícita. RETAIN como precaución de medición.

## PF-H05 — Varias dimensiones temáticas sin una sola escala de ideología
Procedencia posición del investigador, C11, diseño documental. Estado: HIPÓTESIS_METODOLÓGICA, no afirmación empírica universal. A favor: claims topic+statement+source; no puntuación izquierda-derecha. Contra: se desconoce coste de extracción/validación de posturas a gran escala y selección de temas. Falsador: extracción temática no permite acuerdo entre anotadores o resulta más sesgada que una alternativa explicitada. CONTINUE con desacuerdo y fuentes adversariales.

## PF-H06 — Participación pública no basta para identificar influencia
Procedencia C12/C13 y sociología de comunicación política. Estado: DISTINCIÓN_CAUSAL. Favor: eventos con roles documentados y sin influence_score. Contra: no hay estimador empírico de influencia; posible endogeneidad visibilidad/agenda. Falsador: diseño causal que identifique efecto específico y supere rival de atención mediática. CONTINUE condicional.

## PF-H07 — Fuente conocida no es evidencia capturada
Procedencia C01/C06 y corrección posterior del código para rechazar actor/claim/event basados únicamente en DOCUMENTED_ONLY. A favor: gates implementados, tests y lectura documental. Contra: el hash aceptado como cadena no autentica el archivo original por sí solo; se precisa ingestión en bytes y checksum recomputado. Falsador: CLI permite crear afirmaciones procedentes solo de referencias sin materializar. RETAIN como control técnico, no validación institucional.

## PF-H08 — Identidad y roles bitemporales
Procedencia C04/C05/C07/C08/C15/C16. Resultado: modelización viable para personas ficticias, con conflictos explícitos e histórica de roles. Contraevidencia: dos errores iniciales de pruebas C02 y C16 exigieron reparar fixtures, especialmente la captura posterior; no se han contrastado colisiones reales, registros de cambios de grupo ni primera publicación. Falsador: datos oficiales de cambios de afiliación y cargo se interpretan con historia falsa. REPAIR_WITH_FIELD_DATA.

## PF-H09 — Diversidad de fuentes y tipos no acredita representación nacional
Procedencia C17/C18/C20. Resultado: auditor de cobertura por tipo de entidad y tipo de fuente, sin ranking de individuos. Límite: muestra artificial de 9 entidades; no existe denominador nacional ni inferencia aleatoria. Falsador: fuente seleccionada genera inequidad documental que las métricas actuales no detectan. CONTINUE, no elevar VSDS.

## Contabilidad
N1/N2/N3 nuevos = 0. VSDS proyecto = 1/3 sin cambio. CT2 predictiva histórica = 24/100 en su rama. CT2 nueva rama multiactor = 20/100 antes/después, **JUICIO ORDINAL DE PLANIFICACIÓN, NO PROBABILIDAD**. Ninguna confirmación externa, ni entrenamiento con datos españoles originales, ni ranking de actores.
