# BOE: prototipo aislado de procedencia, 2026-10-30

**Estado:** prototipo sintético incorporado en una rama de revisión de PFL; origen de desarrollo y primera ejecución en `/cos-prueba/PFL-scratch-boe` (equivalente Windows: `C:\Users\Nitropc\CoS-Prueba\PFL-scratch-boe`). El código y los fixtures han sido copiados y cotejados por SHA-256. No es una ingesta de originales ni una prueba empírica de política española.

El adaptador de Python estándar prepara **una sola solicitud HTTP GET** al sumario público previamente identificado: `https://www.boe.es/boe/dias/2026/10/30/`. Tiene URL fija, límite de 8 MiB, timeout de 20 s, sin redirecciones y sin reintentos automáticos. Preservaría los bytes HTML originales, su SHA-256, la fecha UTC de captura, el estado HTTP y la cabecera HTTP `Date`, el identificador documental y las URL encontradas. No descarga los documentos individuales.

**Bloqueo legal activo.** La descarga real está deshabilitada mediante `LIVE_FETCH_AUTHORIZED = False`: descargar/reutilizar puede quedar sujeto a condiciones vinculantes publicadas en [aviso legal del BOE](https://www.boe.es/informacion/aviso_legal/index.php). No se han aceptado condiciones en nombre del usuario y esta ejecución no hace ninguna solicitud HTTP a la fuente. Antes de habilitarla debe resolverse la autorización del titular y las condiciones aplicables; accesibilidad técnica y derecho de reutilización son cuestiones distintas.

Para ejecutar solo pruebas sintéticas sin red:

```powershell
python -m unittest -v test_boe_capture.py
```

Para ejecutar exactamente un smoke sintético y obtener recibos locales:

```powershell
python boe_capture.py smoke
```

El comando `smoke` se bloquea si ya existe `runs/2026-10-30/attempt.json`, evitando repetirlo accidentalmente. Produce `runs/2026-10-30/receipt.json` (bloqueo legal, HTTP nulo, fecha HTTP nula, número cero de GET), `coverage.json` (cobertura real nula y métricas sintéticas), `synthetic/original.html` (copia exacta de fixture), `synthetic/ids.json` (únicamente identificadores ficticios y sus enlaces) y hashes SHA-256 verificables. La prueba sintética usa `fixtures/synthetic_day.html`, que **no** es contenido del BOE.

Dentro del repositorio, `runs/` permanece ignorado por Git y las pruebas no efectúan llamadas de red. El recibo original del primer smoke se conserva en la carpeta local de origen y no se confunde con una captura BOE.

## Alcance y límites

El parser obtiene `BOE-A-AAAA-N` en rutas o en el parámetro `id` de enlaces HTML `<a href=...>`, restringe el host a `www.boe.es` y HTTPS, agrupa cada identificador con sus direcciones y contabiliza repetición exacta del par identificador-URL. Registra también documentos con más de un enlace (HTML/PDF), referencias de otro año y enlaces ambiguos. No extrae títulos, texto normativo, resultados políticos, adjudicaciones ni ninguna variable dependiente.

La eventual disponibilidad del sumario no demostraría por sí sola ni la exhaustividad del conjunto, ni que cada enlace sea una primera publicación, ni que corresponda a la sección I. El recuento de enlaces nunca será utilizado como medida de éxito legislativo sin construir la población de oportunidades pertinente y su prerregistro. Las fechas de disposición, publicación, consulta, actualización y entrada en vigor deben mantenerse separadas.
