# Revisión y continuación de PFL · 30/10/2026

## Resultado y alcance real

Se revisó la continuidad publicada, la PR2, el método adoptado, el contraste C38 y sus antecedentes. Se corrigió una regresión real de interfaz y se ejecutó una auditoría de medición con originales. Estas son las cinco unidades de lectura de la concesión del usuario; no cinco experimentos científicos ni cinco unidades adicionales a las que ya describía el texto recibido. No se afirma lectura exhaustiva de los aproximadamente 2.800 archivos históricos.

El adjunto contiene una conversación y los nombres de dos entregables descargables. **No contiene el ZIP ni TAREA_CODEX_CONTINUAR_PFL.md**. Sus contenidos y hashes no se inventan. El contrato siguiente se reconstruye explícitamente a partir de la evidencia accesible y queda identificado como trabajo nuevo de esta revisión.

## R01 · Continuidad y autoridad

`main` estaba en `08f83444`; PR2, en `9d5603ea`, partía de `903c000c`. Se reconciliaron los dos trabajos mediante merge, conservando el recibo final de migración de main y P1/C38/Atlas94 de PR2. Los índices y el handoff se regeneraron. Ningún presupuesto histórico se reinició: ABH10 6/10, saldo 4; concesión independiente 0/10, saldo 10; dos históricos bajo R5.

## R02 · Método y contabilidad

Se consultaron el núcleo 3.2.1 y O1–O7 de la revisión fijada en METHOD_REFERENCE, además del acuerdo local. Prerregistro y freeze son anteriores a los outcomes cuando se reivindica prospectividad; la exposición previa se conserva. R5 permite parar sin llenar una cuota. Una réplica conocida, mantenimiento o revisión posthoc no se transforma en confirmación independiente.

La nueva concesión es **20 unidades totales, cinco de lectura y quince sustantivas condicionadas**. No se convierte en cinco lecturas más veinte experimentos. [Registro único](AUTHORIZATION.json), visible en el briefing y comprobado por una regresión contra esa inflación. Los quince no se declaran ejecutados.

## R03 · C38 y selección

Se inspeccionaron contrato, reparación de fixtures, recibo, instrumento, pruebas, prior PF-BR80 y grafo O7. Se conserva el negativo −29,08 pp del indicador CSV, no una diferencia causal en respuesta institucional. La sensibilidad comunicada en el adjunto es aritmética: siete textos adicionales entre catorce celdas vacías del grupo alto invertirían el signo manteniendo fijo el bajo; no prueba que existan esos siete casos.

El nuevo diagnóstico usa **exactamente el CSV de C38**, SHA `a5757255…`, y el [acta del 8/4/2026](https://www.assemblee-nationale.fr/dyn/opendata/CRCANR5L17S2026PO419865N038.html). Sus cuatro decisiones están identificadas por número. Las cuatro celdas CSV están vacías: dos decisiones de examen y dos de clasificación. Las dos primeras siguen abiertas en el CSV, por lo que quedan fuera del conjunto cerrado de C38. No se estimó la falta de cobertura entre sus mil elegibles ni se corrigió su diferencia. Tampoco se comprobó concordancia textual de campos no vacíos. [Contrato con exposición previa](C39_AUDIT_CONTRACT.json), [código](../R0_INSTITUTIONAL_PETITIONS_20261030/committee_measurement_audit.py), [recibo](C39_RUN_RECEIPT.json).

Es **POST_HOC_AUDIT**, cero ciclos científicos nuevos y ningún 1/3–2/3. El identificador de este expediente no consume ni certifica un futuro ciclo formal ABH10-C39. Conservar esa distinción al continuar.

## R04 · Producto y regresión

La última [CI remota de PR2](https://github.com/GalexY3/politics-fantasy-league/actions/runs/41004587727) había pasado Python y Atlas, pero fallaba Node: un atributo `style` del formulario de acceso violaba la CSP y una prueba ya existente. Se trasladó el diseño a `style.css`, preservando CSP y test. Se corrigieron también enlaces activos del panel de progreso que todavía apuntaban al árbol retirado de AB y texto corrompido durante el traslado.

QA completo Linux/QEMU sobre `7de66007`: **837 Python +32 subtests, 511 Node y 38 Atlas +105 subtests PASS**, cero fallos/skips. Instalación, catálogo, continuidad, logros y replay PASS. [Logs y hashes](linux/MANIFEST.json), [comandos](check.sh), [entorno](linux/environment.txt). Los cambios posteriores en el verificador de presupuesto tienen comprobación focal separada; no se atribuyen retrospectivamente al mismo SHA.

En Chrome se comprobó alta y entrada real de una cuenta ficticia al tablero. La automatización perdió la conexión de foco al crear un club mediante diálogo; no se presenta el resto del recorrido como observado. Las pruebas HTTP sí cubren dos cuentas, aislamiento, inventarios, CSRF, logout y persistencia. **P1 sigue READY_REVIEW para aceptación humana de uso**, sin despliegue. Revisión de código para incorporar y aceptación de producto son decisiones diferentes.

## R05 · Fuentes y antecedente competente

La [Comisión de Leyes, 5/4/2023](https://www.assemblee-nationale.fr/dyn/opendata/CRCANR5L16S2023PO59051N049.html), describe un criterio de 5.000 apoyos en seis meses adoptado en julio de 2022. La [Comisión de Asuntos Económicos, 1/7/2026](https://www.assemblee-nationale.fr/dyn/opendata/CRCANR5L17S2026PO419610N111.html), describe su criterio de 10.000 en seis meses, 212 clasificaciones en esa sesión y recuerda 39 el 14 de enero. Son reglas/documentos fechados, no una reconstrucción de todas las comisiones o periodos. No se deduce qué peticiones integraban el grupo de 39 ni que esos criterios expliquen C38.

El antecedente próximo es [Suite à donner, metodología](https://suiteadonner.nucom.fr/methodologie), [repositorio público](https://github.com/Clemsrec/suiteadonner) y [artículo de Clément Tournier de 15/9/2026](https://fr.linkedin.com/pulse/une-p%C3%A9tition-deux-lectures-%C3%A0-jours-d%C3%A9cart-quatre-champs-tournier-l5ate). Ya estudia discordancias CSV/actas, reglas de comisión y enlaces por identificadores. Por tanto, la idea general no se considera nueva ni confirmación independiente de PFL. Su pipeline es un comparador competente que debe revisarse antes de programar otro equivalente. No se ejecutó ni copió su código.

## Siguiente investigación: una decisión concreta antes de quince bloques

Se comparan tres rutas:

| Ruta | Qué aportaría | Qué hace falta y cuándo parar |
| --- | --- | --- |
| Auditoría de cobertura en un corpus nuevo finito | Validez del indicador y errores de enlace frente al baseline publicado | Fijar actas/fechas aún no inspeccionadas, reglas de inclusión y extracción por número; congelar antes de leer outcomes; adjudicar ambiguos sin imputarlos. La réplica es útil aunque no novedosa. |
| Secuencia temporal apoyo → tratamiento | Orden y desfases de tramitación | Versiones originales con fechas de apoyo y decisión; una foto acumulada no identifica precedencia. Aparcar si no hay versiones. |
| Reglas heterogéneas por comisión y periodo | Comparación institucional con mecanismo definido | Norma vigente en cada fecha, apoyos al plazo relevante y criterios de asignación; no hacer RD con apoyo final ni aplicar un umbral universal. |

Se elige primero **validar la medición en un corpus nuevo**, con Suite à donner como baseline. El objetivo es una tabla auditable de cobertura y errores, no otro signo tras cambiar umbrales. [Contrato siguiente](NEXT_RESEARCH_CONTRACT.md) pendiente de completar corpus y congelar instrumentos; no se marca como ejecutado. Las rutas temporales/causales esperan sus datos. C37 y T005 continúan aparcados.

AB-DECIDE: REPAIR de integración y medición; CONTINUE condicionado a un corpus nuevo y comparador competente. No pedir presupuesto adicional: hay saldo. CT2 ordinal conservada en 20, sin punto nuevo de trayectoria ni gráfica inventada; grados 0/0/0 y gates 0/6.
