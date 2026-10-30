# T016 avance parcial independiente (29/10/2026)

Base de QA: commit `7a6876f71b6cbc286f86ff4bf1393889e4f22851` (archivado a TEMP; no se modificó el repositorio). Ejecución Python 3.12.14 Windows. Esta revisión técnica no consume ciclos AB ni acredita release o resultados causales.

## Originales

Los manifiestos `MANIFEST.json` y `LINKED_MANIFEST.json` registran URL oficial solicitada y efectiva, fecha de captura, SHA-256, tamaño, tipo y última modificación cuando se anuncia. Capturados con TLS verificado: DOG HTML/PDF; BOE HTML/XML; cuatro CSV provinciales por municipio y cuatro por mesa, enlazados en el catálogo datos.gob.es a datos de la Xunta. Las copias se conservan únicamente en `private_raw/`; DOG y BOE pueden contener datos nominales y no deben incorporarse a Git.

La única solicitud directa al ZIP de Euskadi falló con `ssl.SSLCertVerificationError: self-signed certificate in certificate chain`; no se reintentó ni desactivó la verificación. La noticia oficial de Euskadi falló con el mismo error. Euskadi sigue sin validar.

## Cotejo Galicia

`AGGREGATE.json` contiene sumas reproducibles de los CSV de la Xunta; municipio y mesa coinciden para las cuatro provincias, y cada archivo concuerda con su fila fuente `Total`. La suma de provincias da 1.515.944 votantes, 14.187 nulos, 1.501.757 válidos y 1.488.705 votos a candidaturas. La cabecera del DOG identifica 1.515.944 votantes y 14.187 nulos, pero 1.501.857 válidos y 1.488.805 votos a candidaturas: hay diferencia de 100 en ambos campos. No se ha determinado la causa ni localizado una rectificación oficial.

El primer intento de análisis sumó también la fila `Total`, duplicando todas las cifras; esa salida y su script se preservan en `AGGREGATE_INITIAL_DOUBLE_COUNT.json` y `analyze_initial_double_count.py`. El análisis final excluye exactamente una fila `Total` por archivo y verifica su concordancia antes de sumar. También se preserva en `first_run_error.log` un primer error de nombre de encoding, corregido sin modificar los originales.

## BOE y QA

En el XML oficial de elecciones europeas constan 17.652.007 votantes, 17.527.438 válidos y 124.569 nulos (`PUBLICATION_COUNTS.json`). Es una elección y población distintas del DOG gallego: sus números no se comparan entre sí. No se han contrastado todavía ganadores ni escaños europeos.

El replay exacto de REGIONAL5 en el commit indicado terminó exit 0 (`replay.log`), observando 75 escaños de cuatro circunscripciones; los nueve tests de `test_source_invariant_guard` pasaron (`unittest.log`). Son controles focalizados: **no** se han ejecutado aquí las suites integrales Python/Node/Atlas de este commit. Las fechas de primera publicación y las licencias de reutilización aún no están verificadas.

Estado: **PARTIAL**. Faltan Euskadi, comprobación completa europea, licencias, QA integral y revisión de la discrepancia. No subir `private_raw/`.
