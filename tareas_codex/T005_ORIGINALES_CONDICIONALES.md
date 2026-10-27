# T005 · Verificación de originales institucionales (bloqueada hasta disponer de documentos)

**Estado BLOQUEADA · No ejecutable hoy solo con Codex · Requiere nueva evidencia y autorización concreta.** [Volver al índice](README.md).

## Dependencias que Codex no puede suplir inventando datos

**A. Senado — literal de voto «NO VOTAN».** C51 verificó una explicación institucional general de las asistencias, pero **no consiguió el XML nominal original ni su XSD/leyenda de opciones**. Para resolver: archivo XML auténtico de una sesión concreta, referencia oficial de su estructura o aclaración publicada que vincule el literal exacto con una categoría, hashes/URL y fecha de versión. **No** deducir el significado del campo de una página genérica de asistencia ni imputar intención a una persona.

**B. Registro de Partidos Políticos (RPP).** C52 identificó en Interior el trámite oficial **SIA 992324 (certificados)**, distinto de la información/consulta SIA 992323. No se obtuvo un **certificado de inscripción de un partido específico**, firma/CSV ni validez temporal. Si el usuario aporta legítimamente un documento original y concede permiso de verificación, comprobarlo con la fuente oficial, registrar código de verificación, alcance y fecha, sin conservar ni subir datos nominativos innecesarios. **No** realizar solicitudes autenticadas ni introducir credenciales por cuenta del usuario.

**C. Datos electorales del Interior.** C55 comprobó licencia específica **CC BY 4.0** en el catálogo datos.gob.es para las distribuciones «Resultados Electorales» que incluyen XLSX de cargos electos del Congreso y Senado. Faltan bytes+SHA de versiones históricas y `first_public_at` de cada fichero/observación; una fecha de actualización de catálogo no los sustituye. La licencia tampoco da automáticamente base jurídica para **perfilar personas**.

**D. Privacidad y finalidad.** C53 identificó el marco RGPD art. 6/9 y AEPD de riesgo/EIPD. Codex puede preparar una matriz técnico-jurídica de tratamientos y preguntas para revisión profesional; **no** emitir un dictamen jurídico concluyente ni levantar el gate por un test automatizado.

## Cuándo desbloquear la ficha

Solo si existe **al menos un original nuevo** cuyo origen pueda verificarse y se especifiquen la fuente, el fichero/documento y el contraste discriminante. Si no hay original, clasificar **BLOQUEADA_R5** y no ejecutar búsquedas genéricas de forma repetitiva.

## Aceptación condicionada

- Cadena de custodia del original, URL institucional precisa, SHA, vigencia/versiones, derechos por recurso; separar dato probado, inferencia y lagunas.
- Comparador e hipótesis rival explícitos, prueba negativa cuando proceda y método A–J si se abre un ciclo autorizado.
- No incluir certificados personales ni originales nominativos en GitHub; solo metadatos mínimos y un hash cuando sea legítimo.
- No concluir `release_ready=true`, identidad de personas ni derechos de perfilado a partir del mero documento.

**Entregable futuro:** `T005_RESULTADO.md`, únicamente después de obtener original verificable y autorización pertinente. Hasta entonces, no pedir que Codex “fabrique” un resultado.
