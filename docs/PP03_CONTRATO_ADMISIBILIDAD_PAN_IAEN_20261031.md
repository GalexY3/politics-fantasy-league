# PP-03 · Contrato de admisibilidad PAN/IAEN (políticas públicas españolas)

**Fecha:** 31-10-2026. **Estado:** validación documental de índices públicos y laboratorio totalmente sintético; **no adquisición de activos originales, no resultados individuales y no ciclo AB**. R5 sigue `STOP`. No modifica la autoridad de `main` ni permite puntuar personas reales, distribuir documentos o consultar outcomes reservados.

## 1. Corrección obligatoria de las tres fechas y del año nominal

El primer expediente PP-01/02 consignó por error `PAN2024 → IAEN2025`, interpretando que la frase «plan del año anterior» del artículo 4 del Real Decreto 286/2017 se refiere al año **del título** del informe. Esa lectura era incorrecta y debe marcarse como retractada, no conservarse sin aviso en handoffs, manifiestos o código.

La regla correcta y confirmada por dos **acuerdos públicos del Consejo de Ministros** es:

| PAN objetivo | IAEN nominal y ejercicio evaluado | Aprobación del informe | Testigo editorial oficial |
| --- | --- | --- | --- |
| **2024** | **IAEN 2024** | **15-04-2025** | [Consejo de Ministros, 15/04/2025](https://www.lamoncloa.gob.es/consejodeministros/referencias/paginas/2025/250415-referencia-del-consejo-de-ministros.aspx) |
| **2025** | **IAEN 2025** | **05-05-2026** | [Consejo de Ministros, 05/05/2026](https://www.lamoncloa.gob.es/consejodeministros/referencias/Paginas/2026/20260505-referencia-rueda-de-prensa-ministros.aspx) |

Los [índices de 2024](https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2024) y de [2025](https://transparencia.gob.es/publicidad-activa/por-materias/normativa-otras-disposiciones/plan-anual/plan-anual-2025) enlazan informes con **el mismo año nominal**. Los apartados 25 y 28 de la [Ley 50/1997](https://www.boe.es/buscar/act.php?id=BOE-A-1997-25336) y 2–4 del [RD 286/2017](https://boe.es/buscar/act.php?id=BOE-A-2017-3415) distinguen planificación, análisis anual y evaluación ex post. La fecha «información actualizada» de un índice no prueba aprobación o primera publicación de un activo. Por ejemplo, el índice PAN2024 muestra actualización 16/04/2025 mientras hay una noticia del portal anunciando la publicación del IAEN2024 el 29/04/2025: no se debe construir una cronología de ítems a partir de la fecha global de actualización.

**Regla formal para este par de ejemplos:** `plan_target_year = report_label_year = activity_evaluated_year`, `report_approval_year > activity_evaluated_year`. Para esas dos parejas editoriales observadas, el año de aprobación es exactamente el siguiente. No declarar que *cualquier* informe histórico en España necesariamente fue aprobado en `t+1`: las excepciones deben analizarse por versión y testigo.

## 2. Poblaciones distintas, sin resultados espurios

La unidad elegible del piloto es **una iniciativa prevista en una edición precisa del PAN**, no todas las políticas públicas ni todos los proyectos iniciados. El IAEN contiene por diseño **tres subuniversos no sustituibles**: revisión de ítems previstos, actividad normativa no prevista y evaluación ex post de disposiciones de otros ejercicios. Una coincidencia de texto, título, ministerio o norma consolidada no convierte una medida extraordinaria en la fase terminal de un ítem PAN. El incumplimiento requiere evidencia positiva sobre la medida; si una línea no figura en un informe visible, su estado es `UNKNOWN`, no rechazo, no retirada y no «cero».

Un vínculo futuro entre `PAN_ITEM` e `IAEN_PLANNED_ITEM` exige referencia documental exacta o crosswalk oficial bajo jurisdicción y edición; BOE/ELI, gastos y ejecución requieren vínculos adicionales con sus propias unidades, fecha de validez y visibilidad. Los nombres no son claves. Los cambios de instrumento y reformas `AMENDS`, `REPEALS`, `SUPERSEDES` no son equivalentes a una cita ni prueba de efectos causales.

## 3. Derechos, origen y detención

**PP-03 está detenido antes de abrir los PDF**. El [aviso general del Portal de Transparencia](https://transparencia.gob.es/utilidades/aviso-legal/reutilizacion) establece condiciones de reutilización que se aplican por el uso de documentos. La licencia específica, posibles condiciones por recurso, conservación local, tratamiento y redistribución del PAN e IAEN concreto **no han sido aprobados para esta ejecución**. No se presume que un permiso general sea consentimiento del usuario, ni que consultar un índice dé permiso para publicar filas individuales.

Alternativas preidentificadas, **no descargadas**:

- [Andalucía: recurso CSV PAN 2018](https://www.juntadeandalucia.es/datosabiertos/portal/dataset/plan-anual-normativo-2018/resource/a0b01500-ca68-4eea-8ebb-55cdfa36cf34), catálogo indica CC BY 4.0 para el recurso; aviso de condiciones del portal por mera utilización. No habilitar GET sin resolver el alcance de esos términos.
- [Aragón: conjunto PAN](https://opendata.aragon.es/datos/catalogo/dataset/plan-anual-normativo), categoría CC BY 4.0 a nivel dataset; permisos individuales de distribuciones y condiciones de acceso siguen sin evaluación suficiente. Posible discrepancia editorial de enlace 2018→2017, no corregir conjeturando filas.

Para pasar de **metadatos** a adquisición hace falta un acta humana de derechos **por URL exacta, edición, formato, finalidad, límites de conservación/distribución y términos vinculantes**, además de un manifiesto de HTTP/SHA y un depósito externo a Git. Para elevarlo a **estudio empírico** hace falta, por separado, un registro de todas las líneas del plan elegido, testigos temporales, estados y pendientes auditables, crosswalk explícito, evidencia de vintages y prerregistro A–J/código SHA remoto antes de outcomes. Una autorización de reutilización documental no levanta R5 automáticamente.

## 4. Exposición incidental y holdout

Al verificar las fechas editoriales mediante índices de búsqueda aparecieron fragmentos indexados de comunicados de La Moncloa que **incluían resultados agregados de los PAN 2024 y 2025**. No se abrió ni descargó el PDF de ningún PAN/IAEN, ni se leyeron filas individuales ni se ejecutaron estimadores. Pero ambos ejercicios **dejan de ser holdouts ciegos** para hipótesis planteadas después de esas consultas. No incorporar esos valores al entrenamiento o selección de umbrales fingiendo un preregistro previo; separar exploración de contraste futuro verdaderamente independiente.

## 5. Contrato ejecutable en pruebas (solo sintético)

`src/politics_fantasy/pan_iaen_preaccess_gate.py` proporciona `FictionalAnnualHeader`, `FictionalPlanItem`, `FictionalReportRow`, `audit_fictional_pan_iaen()` y `validate_preaccess_source_manifest()`. Prohíbe originales auténticos/PII/derechos afirmados, códigos fuente sin namespace, años nominales cruzados, filas ex post o no previstas presentadas como ítems de plan, disponibilidad futura `as_of`, enlaces sin documentos exactos, y promoción de R5 o de un holdout expuesto por manifest. **La referencia de un ítem previsto exige namespace de ministerio y referencia a la edición exacta del PAN (`issuer`, documento, SHA); el mismo ID de ítem de otra edición no basta.** Las filas derivadas capturadas después de `as_of` no pueden invalidar un diagnóstico histórico anterior. Se rechaza además un PAN supuestamente aprobado **después** de su IAEN y la inyección de campos no previstos en el manifiesto. Aceptar un fixture solo significa **consistencia estructural**, nunca legalidad, cobertura o exactitud española. `scripts/check_pan_iaen_source_gate.py` opera exclusivamente sobre el JSON de metadatos local, no tiene llamadas de red ni lee fuentes originales.

**Falsadores que obligarían a detener PP-04:** documento reportado como IAEN2025 para PAN2024 por la sola fecha de aprobación; IAEN reportando normas no previstas que se cuentan como plan cumplido; el mismo ID local de dos ministerios tratado como la misma iniciativa; fila publicada después del corte usada como observación anterior; licencia catalogal convertida en aprobación de activo; ausencia de reporte convertida en fallo; exposición agregada previa eliminada del registro para reclamar holdout ciego.

## 6. Siguiente avance que requiere evidencia distinta

La siguiente operación científicamente productiva es resolver la reutilización exacta de **una** pareja PAN/IAEN y adquirir ambos originales bajo permiso y conservación adecuados, sin consumir ciclos AB por descarga ni por QA. Si el permiso no se acredita, mantener STOP y preparar una fuente alternativa con derechos expresos y población de entrada identificable. Evitar abrir nuevas campañas de fixtures que no aporten propiedades diferentes a las ya verificadas.
