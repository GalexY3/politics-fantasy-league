# T011 · Avance de captura y perfil de fuentes

**Estado: avance parcial; T011 sigue pendiente de cierre.** Para evitar duplicar ramas ya resueltas se inspeccionó la ficha SOURCE5 heredada en RELEASEPATH5 y se realizó una captura acotada desde PC, sin cambios en código ni campañas científicas. La QA de T025 sobre una rama descendiente no se atribuye a la antigua base SOURCE5 ni sustituye sus criterios de aceptación específicos.

Se obtuvieron los dos XLSX de las URL oficiales exactas fijadas en la ficha: cargos electos y candidatos/as. Ambas respuestas fueron HTTP 200, sin redirecciones, con TLS verificado. MIME, longitud, firma ZIP, CRC y partes mínimas OOXML son coherentes; ambos libros se cargaron con `openpyxl 3.1.5` de solo lectura. [Manifiesto de captura](T011_EVIDENCIA/MANIFEST.json) y [perfil agregado](T011_EVIDENCIA/PROFILE_REPORT.md).

Los originales quedan exclusivamente fuera de Git, en la carpeta temporal indicada por el manifiesto. SHA-256: electos `8432b436a59f769c011f1f6b47429dd5e47d3b17cc3b1970526435d400499b60`; candidatos/as `670770cd65f6d1821db943f74dd10fb5dc44d95b9668ed004981dad7ab808d80`. `Last-Modified` y el momento de descarga no acreditan primera publicación histórica.

El perfil conserva encabezados, recuentos y agregados sin filas personales. Detectó que la clave de metadatos propuesta no es única y documentó los duplicados sin deduplicarlos ni corregir fechas por suposición. Se contrastó la aritmética de recuentos y redondeos; no se calcularon tasas individuales de elección ni se enlazaron personas entre libros. El piloto descrito usa denominadores de fuente distintos y no se interpreta como probabilidad de elección.

Para cerrar T011 faltan resolver semántica de unidades y versiones, derechos por recurso y la QA bajo su contrato y base específicos. Esta captura no permite elevar CT2, progreso, logros ni gates. Se preserva el resultado para que el siguiente trabajo pueda partir de bytes reales, en lugar de repetir intentos de acceso fallidos.

Se conservó además una copia verificada fuera de Git en `C:\Github\Metodologia-AB\proyectos\politics-fantasy-league\data\raw\t011_20261029`. El manifiesto de captura señala la carga aún no realizada en la fase inicial; la carga posterior se documenta en `PROFILE_MANIFEST.json`.
