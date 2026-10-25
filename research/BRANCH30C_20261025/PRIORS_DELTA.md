# Registro acumulativo de priors BR30C (proyecto, no AB global)

- **PFL-P06 | datos de grupo**. Procedencia: web Congreso Abierto y fixtures v0.6. Supuesto: CSV por grupo captura categoría en la votación, no es certificado independiente de censo histórico. Evidencia: unidad y parser reproducibles; contraevidencia pendiente: cotejo del CSV real con el JSON oficial; incertidumbre alta; acción: no elevar VSDS por tres CSV coincidentes.
- **PFL-P07 | escala de disciplina**. Procedencia: lógica matemática de proporciones. La concentración modal es función de recuentos observados y no mide obediencia, motivación, coerción o conducta de parlamentarios no observados. Evidencia: casos empate/abstención. Falsador futuro: criterios sustantivos independientes de obediencia partidista.
- **PFL-P08 | instrumentación previa**. Procedencia: fallos del lote E durante QA: cuatro tests con variable equivocada `tmp`; reparación documentada y suite repetida, sin cambio de estimando científico. Registrar defectos instrumentales, no ocultarlos.
- **PFL-P09 | bitemporalidad**. Procedencia: principio de disponibilidad histórica. Fecha original de votación y fecha de descarga son dos tiempos diferentes; ningún snapshot actual prueba lo disponible antes de la descarga. Contraejemplo: backfill retroactivo.
- **PFL-P10 | ausencia/censo**. Si faltan entradas nominales no se conoce la conducta real; con censo externo conocido las cotas pueden computarse, pero no identifican motivaciones ni valores verdaderos de faltantes. Incertidumbre dependiente de cobertura.
- **PFL-P11 | integridad self-signed**. Un SHA256 de archivo detecta alteraciones accidentales, no identifica al editor ni certifica el origen; verificar firmas/autenticidad mediante terceros.

**AB actualización**: ningún prior empírico nuevo cuantificado, ninguna elevación N1–N3. CT2 predicción 24/100 y VSDS proyecto 1/3 sin cambios. Priors históricos se preservan; estas entradas no borran P01–P05 y no cambian AB 3.2.1.
