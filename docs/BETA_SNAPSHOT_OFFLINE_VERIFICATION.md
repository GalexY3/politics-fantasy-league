# Verificación offline de una descarga S9 de la beta científica

**Ámbito:** S9 v4, datos documentales exclusivamente sintéticos de la consulta
local del Observatorio. Este control comprueba la coherencia del archivo
descargado sin conectarse a un servidor, abrir SQLite ni importar datos reales.
No constituye admisión científica, certificación externa ni autorización
para publicar la beta.

## Comando

Desde la raíz del repositorio, con Python:

    python scripts/verify_scientific_snapshot.py "ruta/al/snapshot-S9.json"

El argumento debe ser el JSON descargado desde «Exportar snapshot S9 + SHA»
en el Observatorio, no un cuerpo de respuesta del API ni un archivo de un
proveedor externo. Puede ejecutarse desde otro directorio pasando la ruta
completa del script. La herramienta usa solo bibliotecas estándar de Python;
no solicita cuentas, tokens, originales ni conexión a la red.

Un **PASS** devuelve una línea JSON con schema, status, sha256, cut, as_of,
valid_at, family, published_until, recuentos de descriptores, intake sintético
y rechazos de evaluación. También indica synthetic_only=true, R5=STOP_R5,
release_gates_passed=0, scientific_ab_cycles=0, public_release_eligible=false,
publisher_identity_verified=false y rights_for_public_display_admitted=false.
El código de salida es **0**.

Un archivo inválido devuelve una línea JSON con status=FAIL y un error_code
estable, sin imprimir contenido descargado, ruta local, credenciales, trazas
ni identificadores internos. El código de salida es **1**. El tamaño del
archivo se limita a 1 MiB y el del JSON canónico a 512 KiB.

## Contrato contrastado

Se exige exactamente el sobre
*pfl.synthetic_scientific_registry_browser_export.v1* producido por app.js,
con sus once campos y el contrato de recibo
*pfl.synthetic_registry_snapshot_receipt.v1*. Se rechazan claves JSON
duplicadas, números no finitos, campos adicionales, versiones distintas,
permisos o admisiones reales y la presencia conocida de IDs fuente-locales.
El JSON embebido se analiza de nuevo, se serializa conforme a la función
_json de S9 (UTF-8, claves ordenadas, separadores compactos,
ensure_ascii=False, sin NaN), y se compara **byte a byte**. Se verifican
también longitud, SHA-256, alcance del snapshot y coincidencia con la
consulta pública declarada.

Solo se admiten los cortes early/late, las tres fechas valid_at, las
familias S9 cerradas y los límites de primera publicación que no superen
as_of. El verificador contrasta los seis descriptores públicos de la versión
autor-cerrada, sus huellas y relojes estipulados; las ocho posibles
evaluaciones R5 y los cuatro posibles intake de ficción, con versiones,
eventos, estados, recuentos y grafos. Un SHA recalculado después de falsificar
un descriptor, un reloj temporal o un permiso no basta para pasar.

## Límite probatorio

El SHA acredita **integridad y consistencia local** del conjunto de bytes,
no identidad de un publicador. La herramienta no puede demostrar quién creó
el archivo, autenticidad externa, primera publicación real, permisos
de reutilización, población/denominador independiente, admisión científica
ni validez causal. La fijación de fixtures sintéticos tampoco constituye
certificación externa: un adversario que controle simultáneamente el código
del verificador y el archivo puede sustituir ambos.

**R5 continúa STOP: cero puertas de lanzamiento acreditadas y cero ciclos
AB científicos nuevos.** El resultado no autoriza publicar la beta,
abrirla a internet ni puntuar actores reales.

Prueba focal:

    PYTHONPATH=src python -m pytest -q tests/test_beta_snapshot_verifier.py

En PowerShell, establecer previamente PYTHONPATH=src con
$env:PYTHONPATH='src'.
