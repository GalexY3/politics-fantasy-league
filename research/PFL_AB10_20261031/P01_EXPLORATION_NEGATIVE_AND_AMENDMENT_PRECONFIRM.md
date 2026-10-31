# P01 · Negativo exploratorio, reparación prospectiva y umbral más exigente

**Estado:** revisión documentada DESPUÉS de la única semilla de desarrollo 4711 y ANTES de cualquier ejecución de las semillas confirmatorias 991, 992 y 993. El diseño original no se sobrescribe: P01_CANDIDATE_RANKING_AJ_PREREG.md y código del commit 1886e32308db07ad5b0dea48fc73b54bc296879b preservan la propuesta original. Archivo privado del resultado exploratorio SHA256 ab2b7e63ba88381e322f72ca838064555513bab23bc7205b8f37c4d6158538de.

## Evidencia exploratoria (únicamente títulos FICTICIOS)

| Comparador | Recall@1 | Recall@3 | Renglones distintos primera opción | Reordenados @3 | Abreviados @3 | Estables @3 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| B0 SequenceMatcher | 0.0000 | 0.0000 | 55 | 0.0 | 0.0 | 0.0 |
| B1 IDF+secuencia original | 0.3283 | 0.3333 | 113 | 0.0 | 0.0 | 1.0 |
| B2 Jaccard uniforme | 0.3283 | 0.3333 | 111 | 0.0 | 0.0 | 1.0 |
| Ablación sin IDF | 0.3283 | 0.3333 | 111 | 0.0 | 0.0 | 1.0 |

La mejora media de B1 respecto de B0 habría superado el umbral H1 original aunque **dos de tres estratos fracasan completamente**. B1 tampoco supera al Jaccard competente B2: la sola ponderación IDF original aporta escaso valor en esta prueba, aunque su primera elección se distribuya entre más destinos. Un score agregado no detecta que los cambios nominales se concentran en dos familias.

## PIVOT permitido solo antes del holdout

Se conserva el generador, la población, los 55 distractores y las semillas. El instrumento B1 se modifica para dar prioridad a tokens infrecuentes de títulos (IDF de candidatos, sin etiquetas verdaderas), con fallback definido cuando no existe token raro. Esto modifica una representación, no los datos. Se añade el **nuevo requisito primario obligatorio** de recall@3 de B1 >=0.55 en **cada uno** de los estratos reordenados, abreviados y estables en **cada** semilla confirmatoria, además de la ganancia macro >=0.05 sobre B0, no inferioridad <=0.02 respecto a B2 y no inferioridad por estrato original <=0.10. Esto fortalece los rechazos; no permite declarar éxito por concentrar aciertos en los títulos más fáciles.

Debe congelarse el código revisado y el test del nuevo umbral en un nuevo commit REMOTO antes de ejecutar cualquiera de 991/992/993. No habrá otra modificación tras observar confirmación. Si fracasa, P01 recibe REFUTED_WITHIN_MODEL/STOP; no se degrada el umbral otra vez. Se conserva como un solo intento de ciclo con historial de reparación. No es validación con la fuente española PAN/IAEN ni se promueve un crosswalk real.
