# PP-04C · Cola privada de adjudicación documental y ramas paralelas

**31/10/2026. NONCYCLE, R5 STOP, 0 AB científicos.** Este instrumento es de priorización de revisión humana, nunca un enlace PAN–IAEN autenticado. Reutiliza los derivados privados previamente extraídos del PAN2024 en PR #10 y del IAEN2024 en PR #11, sin descargar más originales y sin introducir texto o casos en Git. Se mantienen las autorizaciones para estudio local académico de los dos PDF exactos y no se concede redistribución.

## Procedencia y límites del ejercicio

La derivada PAN corregida tiene SHA-256 c5bb5feba316c77c827bf60e912074ebc2ab56fd2be0489122116c30a78d86bf; la derivada IAEN prevista de PR #11 SHA-256 0a46761441426183f08c86a1ba334640b8c402c059b777eb34cf2de8f571696b. Los PDF oficiales de los que proceden mantienen respectivamente SHA-256 49de70b656da1b9ed9c68f552eafe743bede253e5b7a725d5eb615db1b61b4c5 y 7c77a73480f3f039d8ba069e12301b7a4c7ad0eeec85934ec84721526cb88aa2.

El nuevo script de revisión privada, scripts/pp04_dual_review_queue.py, compara solo textos candidatos de títulos y páginas dentro de los 198 ítems planificados de cada fichero fuente-local. Comprueba la validez de los rótulos retrospectivos IAEN, pero **no utiliza la aprobación ni el estado pendiente para asignar puntuación o proponer pares**. Ordena como máximo tres posibles destinos por semejanza de cadenas normalizadas; esta semejanza **no representa una probabilidad calibrada**, un ID editorial, una correspondencia de iniciativa ni una fecha disponible en 2024.

Los resultados privados se conservan únicamente en PFL-raw-primary/pan_iaen_2024_20261031/_pp04c_dual_review_queue_v1/, fuera de cualquier checkout Git, con recibo de SHA del script/pruebas antes de la primera ejecución real. El JSON de la cola tiene SHA-256 **afe4f1372abed7d0c6cb0bea8ec59f81d17070b25f1b135bf4be430e6e06fa30**. No se publica el fichero de títulos o sugerencias.

## Falsador observado contra el emparejamiento ingenuo

Las **198 propuestas PAN** produjeron **594 sugerencias** (tres por propuesta), pero sus **198 destinos de primera preferencia** apuntan a solo **81 entradas distintas IAEN**: 117 repeticiones de destino. Treinta y ocho primeras opciones tienen semejanza textual normalizada mayor o igual a 0,90, y dos menor a 0,50. Estos son recuentos de decisiones del algoritmo, **no** una matriz de verdad ni prueba de 117 errores históricos. Son evidencia directa de que convertir automáticamente la mejor semejanza textual en una correspondencia uno a uno no está justificado. Relaciones N:1, títulos semejantes y truncamientos exigen cotejo documental adicional. **Los 198 casos conservan decision=UNKNOWN, cero enlaces autenticados.**

Una función de doble revisión exige dos pseudónimos diferenciados y referencias a documento, página y hash concordantes. Incluso si ambos registran mismo par con referencia explícita, la respuesta es solo lista para nueva comprobación del original y nunca enlace ya autenticado. Dos pseudónimos distintos **no acreditan por sí mismos** independencia humana; el control operativo de revisores y la lectura exacta de los originales siguen pendientes. Con solo títulos iguales, desacuerdos o evidencia no disponible, se conserva UNKNOWN. **11/11 tests sintéticos PASS** sobre contratos y negativos; no se ha certificado capacidad de identificar normas reales.

## Rivalidad de PR #11 y #12 antes de cualquier integración

La PR #11 (ff3da7c95718528f8f67b1bc0ba8060255566306) expone los constructores parse_plan_candidate_blocks, parse_report_ministry_listings y reconcile_counts_without_crosswalk. La PR #12 (3fabecc800acb300f84c7c4710239847db1c4520) expone otros: parse_pan_objective_ministry_pairs, parse_iaen_ministry_bullets y summarise_local_frame. Ambas tocan el mismo módulo y sus pruebas con **firmas públicas diferentes**. Copiar una sobre la otra sin una decisión explícita rompería contratos de llamada; una coincidencia de nombres de ficheros no permite inferir compatibilidad. Además, GitHub confirma PR #12 **diverged / behind_by=3** respecto al HEAD actual de PR #10. No se ejecutó merge ni aceptación humana.

## Tres rutas discriminantes para proseguir

**Identidad documental (PP04C):** revisión humana estratificada de propuestas con primera opción compartida; buscar testigo inequívoco en dos fuentes exactas, sin autorizar nuevas descargas tácitas. *Falsador:* mismo título con dos objetos jurídicos distintos, o correspondencia N:1 que invalida una unión bijectiva.

**Tiempo jurídico-institucional (PP05):** separar propuesta, decisión, aprobación, publicación, vigencia y captura, con intervalos cuando la fecha exacta falte. *Falsador:* norma de 2025 retroproyectada a cumplimiento al 31/12/2024 por un informe posterior.

**Producto científico (observatorio):** visualizar estado y cobertura UNKNOWN, atribución, versión y posibilidad de refutar el vínculo sin puntuar políticos reales. *Falsador:* interfaz que presenta 89/198 como éxito causal, 109 pendientes como fracaso o normas no previstas como iniciativas planificadas.

La igualdad de recuentos PAN198/IAEN198 no equivale a un crosswalk 1:1; la contradicción interna del PAN intro 199/tabla 198 sigue abierta, sin padrón independiente all-received, dos vintages, first_public_at ni holdout ciego. **R5 STOP**. Los **10 ciclos adicionales del usuario** quedan disponibles, sin cargo por el presente noncycle y sin modificar otros ledgers SYSTEM20/BRANCHING10, Atlas, CT2 o logros.
