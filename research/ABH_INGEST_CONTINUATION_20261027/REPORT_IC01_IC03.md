# Politics Fantasy · continuidad integrada de ingesta · IC01–IC03

**27/10/2026 · rama existente** `research/pfl-codex-contributions-20261027`, sin crear otra ni tocar `main`. Tres ciclos nuevos **IC01, IC02, IC03**, posteriores y **separados** de ChatGPT AB-H45 (45/45) y Codex CDX01–09 (9 ciclos). Esta fase no añade pruebas científicas predictivas confirmatorias ni modifica CT2/VSDS o el alcance contractual.

## IC01 — Redirecciones y emparejamiento fuente/host

**Riesgo demostrado por lectura del código inicial:** `ingest.py` permitía seleccionar `source='senado'` con una URL del Congreso y utilizaba `urlopen`, que podía seguir un 302 antes de comprobar `response.geturl()`. No se ha demostrado exposición de esta llamada a clientes HTTP remotos ni explotación real.

**Corrección:** vinculación exacta `congreso↔www.congreso.es`, `senado↔www.senado.es`, `boe↔www.boe.es` en la URL inicial y en **cada `Location` antes del siguiente contacto** mediante `SourceScopedRedirects(HTTPRedirectHandler)`. Se rechazan HTTP, cambio de editor aunque el destino también sea oficial, suplantaciones por sufijo, credenciales en autoridad, puertos no estándar, loopback, rutas con fragmento, redirects opacos de un `opener` de test y más de cinco saltos. Redirecciones HTTPS dentro del mismo editor se mantienen y registran en `redirect_chain` como trazabilidad de red **sin certificar al editor**. Destino final se verifica antes de leer bytes. El importador preserva límite de 20 MiB, SHA y manifiesto privado, y añade `first_public_at:null` y `release_grade:false`.

**Pruebas:** nueve casos con transporte `HTTPSHandler` ficticio que ejercita el redirector real de `urllib`: **9/9 PASS nativo local** y cero solicitudes externas. Se conservaron pruebas iniciales fallidas al descubrir que el doble `Response` carecía de `read()` sin argumentos y de campos `code/msg/info` requeridos por `urllib`; no se confundió este defecto del fixture con una prueba de bypass. El módulo `ingest.py` local ejecutado sí reproduce el SHA de GitHub `d4e7d62bdcbec58312336e40dab539b0ed23c3eb`; la copia manual del **test** IC01 usada en el entorno local no alcanzó igualdad exacta de blob con la versión final del repositorio, por lo que su resultado se clasifica como ejecución de fixture equivalente, **no** como certificación byte a byte del archivo de test.

## IC02 — Captura, comprobación estructural y cuarentena

Nuevo módulo [`quarantine_ingest.py`](../../src/politics_fantasy/quarantine_ingest.py) (uso **solo local, no expuesto en HTTP**): valida que el tipo documental está autorizado para el editor **antes** de llamar a `import_url`; captura un objeto privado y su `manifest.jsonl`; relee el SHA del objeto; pasa JSON ficticio del Congreso por `audit_congress_vote` y XML ficticio del Senado por `audit_original_senate_session`; añade un `quarantine_reviews.jsonl` local con estados explícitos.

- Un original con formato y totales válidos queda en **`QUARANTINED_SCHEMA_PASSED`**, nunca publicable.
- Totales inválidos quedan **`QUARANTINED_SCHEMA_FAILED`**; bytes manipulados después del guardado, **`QUARANTINED_INTEGRITY_FAILED`**.
- Un tipo documental `senado_session` presentado como Congreso, o una pretendida inscripción `rpp_party`, se rechaza **antes de iniciar la captura**.
- `first_public_at=null`, firma editorial **no verificada**, licencia **no aprobada**, **ningún ID personal certificado**, `release_grade=false`, `real_person_scoring=false` y `http_ingest_endpoint_connected=false`.
- El parser de Senado reconoce operativamente la etiqueta `NO VOTAN`, pero **su correspondencia semántica institucional NO está documentada**; los totales coherentes del XML no la acreditan.

**Pruebas:** seis casos negativos/positivos de extremo a extremo **local y ficticio**, **6/6 PASS nativo**. La suite combinada IC01+IC02 alcanzó **15/15** en el entorno local sin red. La primera ejecución IC02 produjo un fallo de instrumentación al parchear `import_url.__globals__`; se corrigió y verificó la versión de los tests por SHA Git. El módulo IC02 y ambos validadores originales sí coinciden exactamente con sus blobs GitHub.

## IC03 — La frontera HTTP realmente existente

Verificación sobre el `server.py` actual y la whitelist real del router:

| Ruta o etapa | Conectada al servidor HTTP integrado | Verificación de esta fase |
|---|---|---|
| `GET /api/source-stages` | **Sí**, catálogo de documentos gestionado por servidor | Implementación verificada por lectura; la suite local Codex previa había probado HTTP, pero no se reejecutó esta ruta sobre checkout completo en IC03 |
| `GET /api/health` | **Sí**, modo `SYNTHETIC_DEMO` | Implementación verificada por lectura |
| `POST /api/ingest`, `/api/source-import`, `/api/capture` | **No**, router POST solo de juego sintético | Test nuevo de loopback `test_ingest_http_boundary.py` escrito para exigir 404, **pendiente de ejecución sobre checkout real** |
| `GET /api/quarantine` o `GET /api/ingest` | **No** | Test de rechazo 404 escrito, no ejecutado aquí |
| Captura→validación→cuarentena | **Solo Python local IC02** | Seis tests nativos ejecutados; ningún original privado ni cuenta real |
| Cuarentena→perfil/jugador/puntos | **No** | No hay fuente certificada, usuario autenticado ni score político real |

El código HTTP existente comprueba `Host` antes de servir `/api/source-stages`; no importa `quarantine_ingest` ni ejecuta `import_url`. La nueva prueba en [`test_ingest_http_boundary.py`](../../tests/test_ingest_http_boundary.py) arranca un servidor local y exige catálogo read-only, Host falso 403, intentos de importación 404 y ausencia de manifiesto. Se incorporó, junto con los tests nuevos de ingesta y `test_ingest.py`, al workflow opcional. **No se ha lanzado GitHub Actions ni la suite Python completa en este turno**. No hay E2E de original HTTPS real→servidor→validación→juego.

## Auditoría adversarial, R5 y próximos bloqueos

La corrección aborda el riesgo de solicitudes a destinos no autorizados **dentro de este cliente local**; no sustituye un sandbox de egress de red, permisos de reutilización, TLS/PKI institucional ni controles contra destinos inesperados por proxies. El manifiesto de captura acredita la transferencia local, no la firma ni primera publicación. La prueba con `opener` inyectado es un mecanismo **de test**, no control fiable para un proveedor inyectado de producción.

**R5:** se cierran tres ciclos con evidencias discriminantes; no se crea un endpoint HTTP de importación prematuramente ni se consumen ciclos adicionales para repetir fixtures. Para un siguiente paso útil hace falta (a) una ejecución íntegra de la nueva suite HTTP en checkout de la rama, (b) diseño autenticado/seguro del operador de ingesta real con rights check y egress gate independiente o (c) un documento institucional que permita resolver la semántica `NO VOTAN`. Esos hitos no se simulan para elevar puntuaciones.

**Marcadores invariantes:** V4 **36,90 %**, CT2 identidad **29/100**, VSDS **1/3**, N1/N2/N3 **0/0/0**, gates **0/6**. Historiales AB-H45 y CDX quedan intactos y se citan como precedentes, sin sumarlos a los tres IC.

## Mantenimiento posterior de reproducibilidad (no es IC04)

Se ha resuelto la discrepancia de SHA señalada en IC01: una copia del fixture local contenía **tres nombres de parámetro `**kw` frente a `**k`** en lambdas de prueba. Tras igualar exactamente el fichero de GitHub, `test_ingest_redirect_security.py` mide **6.654 bytes y blob SHA `9dec4b4cc92d70712ce144f0a73c25a70fce59c0`**. `ingest.py`, `quarantine_ingest.py`, los dos validadores oficiales del repositorio y los dos tests nuevos coinciden asimismo con sus blobs. La **suite nativa conjunta 15/15 volvió a pasar**, sin peticiones a Internet.

[Seguimiento íntegro y hashes](IC01_EXACT_REPLAY_FOLLOWUP.json). Atlas registra esta reparación sin reescribir el lote 0017, mediante el lote **0018** y `complaint.triage(status=repaired)`. El test HTTP que necesita cargar el servidor entero sigue sin ejecutarse en este turno; el resultado no modifica V4, CT2 ni gates.
