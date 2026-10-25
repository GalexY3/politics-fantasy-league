# PF-BR30F C22 — auditoría adversarial del cambio de signo de mayoría

**Estado:** `POST_HOC_AUDIT`, apéndice de precisión del ciclo C22; **NO** es un nuevo ciclo autorizado, ni una prueba confirmatoria independiente. Fecha: 25/10/2026.

**Fuente:** Congreso Abierto, `data/raw/votaciones/pleno.jsonl`, Git blob `71918bb689c7a62cfbbdafe0b9248eac6b5c4be1` (archivo secundario derivado de votos oficiales del Congreso). Las cifras de agregados y subconjunto nominal proceden **del mismo archivo**, por lo que la comparación no acredita validación cruzada ni cuestiona los resultados oficiales.

## A–J: contrato y resultado

**A (estimando).** Entre las votaciones con algún registro nominal identificado, comparar el signo de `Sí − No` calculado sobre todos los recuentos agregados con el signo del subconjunto indexado por código. Unidad: votación, no diputado. Abstenciones y «No vota» no entran en el signo, pero se usan para distinguir una votación nominal vacía.

**B (rivales).** H1: los huecos de identidad pueden cambiar el signo obtenido del subconjunto. H0: no cambia el signo. H_otra: el cambio aparente puede ser un empate, no inversión estricta.

**C (regla, retrospectiva).** Clasificar: `SAME_SIGN` (ambos signos iguales), `STRICT_REVERSAL` (uno positivo y otro negativo), `TIE_INVOLVED` (son distintos y alguno es 0), `NO_NOMINAL` (no hay filas nominales). Esta taxonomía se formuló al revisar el resultado exploratorio previo de 149 cambios, así que no es preregistro prospectivo.

**D (instrumento).** Implementación independiente en `src/politics_fantasy/majority_sign.py` con CLI `scripts/audit_majority_sign.py` y pruebas negativas para inversión, empate, ausencia de nominal, coincidencia y revisión de SHA del blob.

**E (resultado).** 2.175 votaciones en el archivo, **2.173** con nominal no vacío; entre estas: **2.024** mismo signo, **125** inversiones estrictas de dirección, **24** cambios con empate. Tasas sobre 2.173: 93,14 %, 5,75 % y 1,10 %. Por año (inversiones estrictas / cambios con empate): 2023 **15/0**, 2024 **107/17**, 2025 **3/1**, 2026 **0/6**. Las dos votaciones sin nominal se excluyen de la comparación de signos.

Ejemplo fuente secundaria: `s2-v001` (2023-09-19), agregados **Sí 176, No 169**, nominales indexados **Sí 134, No 153**. El algoritmo ingenuo invierte el signo sin que el resultado original se haya modificado.

**F (auditoría).** La cifra previa de 149 `signos diferentes` es correcta, pero la expresión «149 inversiones estrictas» sería falsa: **24 tienen empate**. No se interpreta el voto no indexado como «No vota» ni como ausencia, no se infiere conducta de una persona. La gran concentración en 2023–2024 es compatible con cambios de cobertura del catálogo, pero no identifica de forma única su causa.

**G (replicación).** El recuento se reprodujo mediante agregación propia del mismo blob y se ofrecen fixtures de Python. **No hay confirmación contra los JSON originales del Congreso** ni contra una segunda fuente nominal independiente.

**H (actualización).** Añadir un prior metodológico local: distinguir cambio de signo, empate y reversión estricta antes de afirmar inversión de una mayoría por sesgo de cobertura.

**I (límites).** Muestra exhaustiva de **una versión de un archivo secundario**, agrupación de votaciones en solo 144 sesiones, fuerte dependencia temporal, universo de posiciones frente a identidades sin coincidencia histórica completa. Ni valor causal ni generalizable a otros procesos electorales.

**J (decisión).** `REPAIR` cualquier presentación que llame estrictas a las 149; `CONTINUE` únicamente con cotejo del JSON original y archivo de diputados históricos. CT2 y VSDS **sin cambios**; AB hallazgo 2/3 = **0**.

**Reproducción externa:** obtener por medios legítimos `https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl`, comprobar Git blob SHA y ejecutar `python scripts/audit_majority_sign.py /ruta/pleno.jsonl`. `--no-verify` permite estudiar otra revisión, pero los resultados se deben etiquetar como nueva versión.
