# R23 · R18-C17: control de derechos de distribución por versión y uso

**31/10/2026.** Incremento **NONCYCLE** sobre HEAD 8df788007553c05890be08b962ffc24349ee1a6a de PR #7, exclusivamente en checkout independiente. Estado **STOP_R5**. Ningún original, expediente o resultado empírico se ha adquirido, abierto, modificado o publicado. El usuario autoriza ciclos sin límite, pero una prueba de ingeniería con casos sintéticos no se convierte por ello en experimento científico A–J.

## Tres rutas consideradas y falsadores

**A. R18-C17: derechos por distribución, versión y finalidad (ejecutada).** Una política de portal puede parecer suficiente cuando no existe evidencia vinculada al recurso exacto. Rival: el módulo source_eligibility.py ya podría cubrirlo, pero su marcador reuse_adjudicated es un booleano declarado y no vincula distribución, bytes, uso y fecha. Falsador: una licencia general, de otro recurso, de otro SHA, posterior al corte, o que obligue a aceptar condiciones por mero acceso, obtiene autorización del nuevo instrumento.

**B. R18-C18: integridad de SHA de originales (aparcada sin consumir).** source_capture_guard.py, diff_parcan_capture_vintages.py y las pruebas de temporalidad ya controlan hashes y versiones. Repetirlos sin un fallo nuevo alcanzable sería mantenimiento redundante.

**C. R18-C20: mecanismos rivales de reproducción política (aparcada).** No existe todavía el universo original admisible, independiente, versionado y con primeros tiempos de publicación para estimar efectos. Simular B0/B1/B2 sin observaciones nuevas no sustituye R5.

## Artefactos y comprobación

- Módulo src/politics_fantasy/r5_asset_rights_gate.py: función pura sin red, exclusivamente para registros documentales **no confiables**. Distingue identificador y URL HTTPS estructural, SHA de bytes, finalidad solicitada, primera publicidad, corte de conocimiento, tipo de aviso, vínculo a distribución y SHA, usos permitidos, fecha del aviso, modo de términos y declaración de revisión humana.
- Suite tests/test_r5_asset_rights_gate.py: 14 tests sintéticos adversariales sin originales, PII, personas, outcomes o términos aceptados.
- Hashes congelados **antes de primera ejecución**: código SHA256 293f3d5748b2d7638cb91e161b02051a86ff4ae07fadc01f21f47826ccc5d10d; fixture y tests SHA256 7b3a10280738fa80988e9d89939679efe0b41763234be0faa4187c48331237af.
- Primera ejecución: 14/14 PASS con PYTHONPATH=src python -m unittest -v tests.test_r5_asset_rights_gate. Hubo después un pequeño retoque de claridad sintáctica sin cambio intencional de contrato; el cierre debe acreditar su SHA y repetir la prueba.

**Validación posterior al ajuste:** SHA256 del código 003c50d08902dc65b0ae2fbf2c03e765d48f427ebba85e51ffcac23e91fb6bd9, SHA de pruebas sin cambio 7b3a10280738fa80988e9d89939679efe0b41763234be0faa4187c48331237af. Reejecutadas 26/26 pruebas PASS contando 14 de R5 y 12 del módulo preexistente de elegibilidad de fuentes. Compilación Python PASS y los dos JSON de cola y autorización parsean correctamente. Estos resultados son QA técnica, no una adquisición legal ni evidencia empírica.

## Resultado y delimitación

La licencia de un catálogo no es automáticamente el permiso de cada distribución. La lectura académica no equivale a redistribuir originales. Un aviso posterior al corte no autoriza retrospectivamente el uso, y los términos que vinculan por acceso exigen revisión humana antes de adquirir contenido. Los registros del cliente no certifican identidad del editor ni titularidad ni legalidad.

La función devuelve siempre reuse_admitted=false, empirical_r5_open=false e independent_attestation=false, incluso si un registro afirma que todo está revisado. El caso formal perfecto queda en BLOCKED_R5 por falta de testigo independiente; el malformado queda en QUARANTINED.

**No se ha levantado R5.** Faltan derechos por activo y finalidad jurídicamente revisados, población all-received/admitted-first, negativos/pendientes/censura, denominador independiente, IDs entre asiento y decisión, dos vintages originales históricos, primera publicidad y autorización humana. Tampoco se ha integrado este guard en todos los endpoints de ingesta: solo está verificada su función focal, no una protección global.

## Reapertura prospectiva

Contrastar un activo y uso concretos únicamente tras permisos de adquisición evaluados; no visitar dominios de aceptación vinculante por mero uso, no repetir 403/404, no descargar resultados privados, y no contar esta QA como AB. Mantener R18-C18/C20 en cola hasta existir falsadores diferenciados.
