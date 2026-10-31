# P03 · MemPalace frente a FTS5 con las mismas fuentes

31/10/2026. Tercer ciclo AB-P ejecutado, H1 refutada. No prueba general de LLMs, ni de política española, ni de memoria automática entre chats. Todos los materiales son inventados.

## A–D. Pregunta, comparadores y diseño

El estimando principal fue el número de consultas con documento relevante en primera posición. Se comparó MemPalace 3.11.0 y EmbeddingGemma local offline con SQLite FTS5 Unicode61/BM25. Ambos motores recibieron exactamente diez documentos vigentes de diez proyectos sintéticos, las mismas diez preguntas y máximo tres resultados. Otros diez archivos históricos sintéticos se excluyeron de ambos motores.

Prerregistro original SHA de Git 4ed083aa5848e1b21a98b604077fefdf6f871441; enmienda prospectiva de paridad de fuentes, código y ocho tests congelados en el remoto antes de ejecutar, commit ab3d2e54f8b6bbcc0028dd03aab249240003141a. H1 exigía al menos ocho de diez top1 de MemPalace y una diferencia >=2 frente a FTS5. No se utilizaron datos personales, títulos de políticas reales ni originales PAN/IAEN.

## E–G. Resultados y auditoría adversarial

| Indicador | MemPalace | FTS5/BM25 |
| --- | ---: | ---: |
| Aciertos top1 | 3/10 | 4/10 |
| Aciertos top3 | 7/10 | 4/10 |

H1 REFUTADA: no alcanza ocho aciertos top1 y queda uno por detrás del baseline. La diferencia positiva en top3 es secundaria y no sustituye el criterio principal preregistrado. El programa invocó el ejecutable MemPalace realmente instalado y recibió rutas Source de cada búsqueda; no se simuló el modelo. Ocho tests del instrumento superados después del freeze. Las diez fuentes CURRENT y diez HISTORICAL ficticias conservan veinte hashes de bytes en el recibo privado.

El resultado individual se conserva exclusivamente fuera de Git en PFL-AB10-PRIVATE-20261031/P03_EQUAL_SOURCE_CURRENT10_20261031, SHA256 del JSON 7c9a685259328a78734a10d525c28942577a3cb22892aebf27778faac46fc789. MemPalace acertó top1 en casos 1, 2 y 6; FTS5 acertó top1 en 1, 6, 8 y 10. Las diferencias top3 no implican representatividad estadística para documentos de usuarios.

El falsador muestra que un recuperador semántico puede colocar primero un documento temáticamente cercano pero distinto. Sin embargo, **no** prueba selección de versiones obsoletas, puesto que ambos buscadores recibieron solo versiones vigentes. La precedencia GitHub/HEAD, firmas de fuente y sucesiones documentales es un mecanismo de autoridad diferente que no puede sustituirse por similitud.

## H–J. Interpretación y decisión

El banco permite utilizar MemPalace como búsqueda complementaria top3 dentro de este corpus de juguete, pero no ha demostrado superioridad top1, precisión general en ciencias sociales, eficacia de agentes LLM ni continuidad automática entre chats. El baseline FTS sin expansión avanzada de sinónimos y el diseño deliberado de diez consultas son límites importantes; no hay réplica externa ni prueba estadística sobre una muestra aleatoria de preguntas.

AB-DECIDE: STOP / REFUTED_WITHIN_SYNTHETIC_BENCHMARK para H1. Es una intervención AB-P ejecutada y válidamente refutada (no un ciclo INVALID por bugs, ni un éxito). Conserva R5 STOP, cero inferencias de políticas reales, ninguna puntuación, derechos, CT2, Atlas o logro promocionado. No ajustar consultas después de observar el resultado.
