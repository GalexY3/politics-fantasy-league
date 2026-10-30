# R0 · Selección prospectiva de una pregunta sociológica verificable

**Estado:** exploración y elección de fuente, no resultado causal ni ciclo por sí sola. Tres rutas materialmente diferentes, comparadas ANTES de analizar filas:

| Ruta | Mecanismo, población y original | Rival competente, falsador y viabilidad | Decisión |
|---|---|---|---|
| **RANK-HUMAN** | Feedback público/privado en trabajadores o plataformas de pronóstico; requiere exposición y datos de oportunidad por persona | R1 presión social y conformidad vs R0 incentivo informativo. El registro AEA 0000981 ya falló; sin original accesible/permiso no se puede validar subgrupos ni extraer estimandos | **PARKED** hasta registro o dataset nuevo con uso explícito |
| **INSTITUTIONAL-PETITIONS** | Peticiones ciudadanas de la Asamblea Nacional francesa, decisiones de comisión, estados y firmas | H1 apoyo se asocia a decisión pública documentada vs H0 diferencia por año/antigüedad, comisión o vacío del campo administrativo. Falsador: desaparece asociación dentro de strata o suficientes decisiones no consignadas; fuente oficial publicada bajo Licence Ouverte 2.0, pipeline público [datagouv/datagouvfr_data_pipelines](https://github.com/datagouv/datagouvfr_data_pipelines/tree/main/data_processing/assemblee_nationale/petitions) | **ELEGIDA** para contraste observacional descriptivo R0→R1 acotado |
| **INCENTIVE-FORECAST** | Modelos formales y simulaciones de incentivos/rank; sin nuevas observaciones humanas | Rival fuerte: comportamiento depende de supuestos, generalización sin identificar. Fixtures/runs de rankings ya exhaustos; no reabrir sin un original independiente o personas consentidas | **PARKED** hasta datos nuevos |

## Pregunta y comparadores

«Entre peticiones francesas cerradas y suficientemente antiguas, ¿la probabilidad de que el dataset publique una *decisión de comisión* difiere entre peticiones con al menos 10.000 firmas y peticiones con 100–9.999, y persiste al estratificar por año y comisión?»

**No es un experimento de umbral**: 10.000 firmas es un corte descriptivo predefinido para contar grupos, no una atribución de discontinuidad causal a las reglas francesas. La plataforma oficial identifica un umbral procedimental distinto de **100.000** y contempla **500.000** para debate pleno. La selección por publicación, duración, temática y acumulación de firmas es endógena. No existe fecha de cruce de umbral en este dataset.

**Instrumento:** analizar exclusivamente columnas `identifiant`, `date_publication`, `nb_votes`, `statut`, `commission`, `decision_commission` del CSV abierto. Su [código de ingesta](https://github.com/datagouv/datagouvfr_data_pipelines) lo obtiene por scraping de páginas de la plataforma; un campo vacío significa **NO DOCUMENTADO EN EL CSV**, no ausencia de decisión real. Se excluirán ids duplicados, firmas ausentes, estados abiertos o peticiones publicadas después de la fecha de corte de antigüedad. No almacenar ni mostrar nombres, títulos, descripciones, URL individuales o contenido personal.

**Valor de información:** una señal descriptiva estable por año/ comisión podría justificar auditoría independiente de actas de comisión; la desaparición de la diferencia, pocos casos de apoyo alto o una cobertura inconsistente serían resultados negativos que obligarían a aparcar. No se atribuirán causalidad, cumplimiento ni intencionalidad a una sola extracción. Antes de descargar observaciones: congelar A–J, código, fecha de referencia, filtro y reglas de falta de datos.
