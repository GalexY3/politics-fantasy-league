# Entrega de ingeniería preparatoria, no ciclos PF-F gastados

Este trabajo es **producción real** en el turno de autorización, **no una prueba empírica** y no convierte 45 slots futuros en 45 ciclos consumados. Todos los módulos siguientes están ejecutados y respaldados por la suite local.

| ID de entrega | Resultado entregado | Comprobante |
|---|---|---|
| P01 | Base SQLite, datos ficticios idempotentes | `product.py`; `test_seed_idempotent` |
| P02 | Cuenta de club y presupuesto persistentes | `add_club`; `test_club_validation` |
| P03 | Mercado de compra/venta con precio fijo | `transfer`; `test_buy_sell_consistency` |
| P04 | Propiedad exclusiva y transacción atómica | `BEGIN IMMEDIATE`; `test_atomic_buy_concurrency` |
| P05 | Límites de plantilla y de fondos | `test_roster_cap`; `test_low_credits` |
| P06 | Alineación de 3 activos propios | `set_lineup`; `test_future_lineup_can_be_saved_and_replaced` |
| P07 | Cierre temporal inclusivo sin backdating | `test_lock_boundary_exact_instant`; `test_locked_round_never_change` |
| P08 | Conservación histórica de equipos tras ventas | `test_historical_lineups_are_frozen_when_sold` |
| P09 | Jornadas, puntos sintéticos versionados y clasificación | `state`, `scoring.DEMO_RULE`, `test_seed_idempotent` |
| P10 | API con limitación de cuerpos, Origin y loopback | `server.py`; tests HTTP |
| P11 | Interfaz multisección local | `web/index.html`, `web/app.js`, `web/style.css`; prueba HTTP de assets y `node --check`; sin captura visual verificada |
| P12 | Observatorio agregado desacoplado del fantasy | `test_real_aggregate_is_separated` |
| P13 | Almacén bitemporal inmutable para JSONL normalizados | `warehouse.py`; `test_import_and_asof_cutoff`, `test_revision_is_immutable_and_bitemporal` |
| P14 | Ingesta atómica SHA256/rollback / idempotencia | `test_hash_mismatch_fails`, `test_atomic_rejection_of_bad_row`, `test_idempotent_identical_file` |
| P15 | Lanzadores Windows/Linux/macOS sin dependencias de runtime | `run_demo.py`, `start_windows.bat`, `start_linux_mac.sh`; ejecución en servidor de pruebas HTTP (no QA en PC usuario) |
| P16 | CI preparada para Python 3.10/3.13, JS syntax | `.github/workflows/ci.yml`; NO ejecutada en GitHub por 403 |
| P17 | Documentación de operación y de riesgos | `docs/PRODUCTO_LOCAL_v0_2.md`, `docs/ALMACEN_BITEMPORAL.md` |

**QA ejecutada:** 49 tests Python superados, `node --check` superado. Cobertura Python integral en la ejecución con pytest-cov: **88 %** de instrucciones, con cobertura desigual por módulo; no equivale a cobertura de ramas o seguridad. Una advertencia de conexiones SQLite sin cierre explícito detectada al medir cobertura se ha corregido en `warehouse.py`; la suite se reejecutó satisfactoriamente.

**Límite:** NO prueba E2E de UI en navegador real certificada. Chromium del runtime queda bloqueado por administrador y la prueba visual no produce capturas; no se hace pasar HTML servido por validación visual. Tampoco se dispone de datos nominales oficiales certificados, ni autenticación multiusuario, ni despliegue público.
