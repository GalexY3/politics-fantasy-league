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

## Comparación offline de dos cortes S9

El comparador acepta **dos modalidades**, ambas exclusivamente locales y
sintéticas. El modo anterior conserva sus dos argumentos posicionales:

    python -B scripts/compare_scientific_exports.py early.json late.json

El modo nuevo admite un único archivo de par descargado como conjunto desde
la interfaz científica, sin abrir cuentas, SQLite ni conexión HTTP:

    python -B scripts/compare_scientific_exports.py --pair downloaded-pair.json

El formato del archivo es
*pfl.synthetic_scientific_registry_browser_pair_export.v1* y contiene
**exactamente**: schema, evidence_class, comparison_kind, exports, R5,
release_gates_passed, scientific_ab_cycles, rights_for_public_display_admitted,
external_authenticity_certified y pair_receipt. El objeto exports tiene
únicamente early y late; **cada uno es el objeto completo** de once campos de
la exportación S9 individual, con su propio recibo SHA-256 íntegro. No son
resúmenes, enlaces ni referencias a documentos originales.

El recibo de par tiene **exactamente** los campos schema, canonicalization,
canonical_json, bytes y sha256. Su schema es
*pfl.synthetic_scientific_registry_browser_pair_receipt.v1* y utiliza la
canonicalización JSON_UTF8_SORTED_KEYS_COMPACT_V1. El JSON canónico contiene
todo el envelope superior **excepto** pair_receipt: UTF-8, claves ordenadas,
separadores compactos y SHA-256 calculado sobre los bytes exactos. La
interfaz, cuando proporciona esta descarga conjunta, es responsable de
calcular el SHA mediante WebCrypto y de iniciar **una sola descarga**.
El consumidor offline no fabrica el recibo, no solicita nuevas consultas
al backend y no afirma haber comprobado cómo se inició la descarga.

Al ejecutar --pair, el comparador limita el archivo a **1 MiB**, rechaza
claves JSON duplicadas y números no finitos, comprueba los campos y
marcadores de bloqueo exactos, vuelve a calcular longitud, SHA-256 y bytes
canónicos del sobre excluyendo pair_receipt, y verifica por **separado** ambos
objetos S9 mediante verify_scientific_snapshot.verify. Solo entonces compara
los descriptores públicos. Ambos cortes deben compartir familia y valid_at;
el reloj early ha de preceder al late, y la fecha máxima de publicación de
early es el mínimo entre la fecha de late y el as_of de early. Así, un par
con dos recibos individualmente válidos pero filtros incompatibles también
queda bloqueado.

El nombre recomendado de la única descarga es
*pfl-s9-pair-VÁLIDO-HASTA-PRIMEROS12SHA.json*, concretado por el contrato
como pfl-s9-pair-<valid_at>-<12 primeros caracteres del SHA del par>.json;
el nombre del fichero no constituye una prueba criptográfica y el CLI
no exige que el archivo conserve su nombre original. Con --pair, la línea
JSON de salida mantiene todos los campos de la comparación anterior y añade
**pair_sha256** cuando el resultado es PASS; FAIL conserva solo campos
seguros y un error_code, sin rutas, trazas ni contenido descargado.

Los descriptores públicos S9 no son IDs internos de fuente, identidades
personales ni unidades de decisión. Las diferencias son **visibilidad de
fixtures estipulados**, no estimaciones de cambios políticos reales.
La consistencia de una descarga conjunta no prueba un origen externo,
independencia documental, simultaneidad observacional o derechos.

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

Pruebas de comparación S9 individual y conjunta:

    PYTHONPATH=src python -m pytest -q tests/test_beta_offline_cut_comparison.py

En PowerShell, establecer previamente PYTHONPATH=src con
$env:PYTHONPATH='src'.
