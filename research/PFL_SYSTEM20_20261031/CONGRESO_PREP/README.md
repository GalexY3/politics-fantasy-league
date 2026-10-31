# Congreso: prototipo aislado de universo de iniciativas

**Estado:** adaptador preparado originalmente en un directorio scratch aislado y posteriormente incorporado a una rama de revisión de PFL, tras inspección y cotejo SHA-256. **Solo Python de biblioteca estándar. Este adaptador no hace solicitudes HTTP.** Su existencia en Git no representa admisión de un corpus original del Congreso.

`congreso_adapter.py` ingiere una secuencia **normalizada y sintética** de páginas JSON, validando estratos (legislatura, código de tipo de iniciativa), identidad completa, cursores de paginación, totales declarados, duplicados idénticos frente a contradictorios, fechas de presentación/calificación/BOCG, fuentes HTTPS oficiales y cortes temporales. `parse_offline_csv()` admite la misma estructura de columnas normalizadas para fixtures CSV sin inferir que coincide con el CSV real del Congreso. No existe endpoint API conocido/validado incorporado al código.

Pruebas sin red:

```powershell
python -m unittest -v test_congreso_adapter.py
```

Único smoke sintético:

```powershell
python congreso_adapter.py smoke
```

Produce en `runs/2026-10-31/` (directorio ignorado por Git) un marcador para no duplicar ejecuciones, `synthetic_originals/page_1.json` y `page_2.json` con SHA-256 confirmados por lectura posterior, `synthetic_index.json` como inventario normalizado SIN resultados, `coverage.json` y `receipt.json` con fecha UTC, número de GET cero, estado HTTP nulo y razón por la que no se obtuvo un corpus real. Los recibos de la primera ejecución permanecen en el directorio scratch original.

**Los expedientes ficticios `121/900001` a `121/900003` y los enlaces marcados `SYNTHETIC-DOES-NOT-EXIST` no representan iniciativas observadas.** No se deben publicar como microdatos oficiales ni usar como resultados sociológicos. Al no haber acceso real, `source_population_complete` y `first_public_at_attested` siempre son falsos. La fecha de primera publicación exacta permanece `null`, incluso en presencia de una fecha editorial de día.

La documentación primaria, derechos y límites están en [SOURCE_AUDIT.md](SOURCE_AUDIT.md). Se mantiene una distinción explícita entre documentación encontrada, pruebas de código realizadas y ciclos de investigación (cero). El contrato del formato offline es provisional: hay que mapearlo contra un export oficial legítimamente obtenido y comparar recuentos de todo el estrato antes de cualquier claim de cobertura.
