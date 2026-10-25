# Auditoría operacional v0.3

El módulo `politics_fantasy.ops` inspecciona **en lectura solamente** SQLite. Comprueba integridad SQLite, claves foráneas, créditos y plantillas, propiedad antes del cierre, y datos sintéticos de demo; en warehouse audita recuentos por lote. No certifica procedencia ni exhaustividad de datos parlamentarios.

```bash
PYTHONPATH=src python -m politics_fantasy.ops --db data/demo/game.db --kind product
PYTHONPATH=src python -m politics_fantasy.ops --db data/warehouse/warehouse.db --kind warehouse
```

Código de salida 0 si PASS, 1 si FAIL; JSON parseable en stdout. **No subir bases SQLite de usuarios ni datos de sesión al Git público**. El servidor web continúa siendo una demo monousuario sin autenticación, sólo para `127.0.0.1`.

Cambios v0.3: no vender figuras incluidas en alineaciones abiertas, seleccionar una revisión de evento por identidad/corte antes de filtrar ventana, comprobar SHA exacto del archivo efectivamente importado, UTF-8 fail closed, allowlist de Host, auditoría de integridad. Todas las figuras demo son ficticias.