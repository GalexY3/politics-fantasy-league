# Política Fantasy · Producto ejecutable 0.2.0 (24 octubre 2026)

## Contrato del producto

**Funciona como prototipo local**: herramienta Python estándar + SQLite y UI web responsive (sin framework JS). **NO** producción pública: faltan sesiones, identidades, autorización, backups, estrategia de secretos, hardening, observabilidad y validación nominal externa. Nunca abrir el servidor a una red pública. El código fuerza interfaz de escucha `127.0.0.1` para impedir exposición directa.

## Cómo abrirlo

1. Descargar y descomprimir el ZIP de proyecto.
2. Instalar Python **3.10+** si no se dispone de él.
3. Dentro de la carpeta, ejecutar `python run_demo.py` (en Windows: `py -3 run_demo.py` o doble clic en `start_windows.bat`; Linux/macOS: `./start_linux_mac.sh`).
4. En el mismo ordenador, abrir **http://127.0.0.1:8787**.
5. Los datos del juego permanecen en `data/demo/game.db` y sobreviven al reinicio. Para reiniciar *solo* la demo, detener servidor y eliminar ese archivo.

No hace falta `pip install` para jugar localmente; Python stdlib. Pruebas: instalar `pytest` y ejecutar `PYTHONPATH=src python -m pytest -q` en macOS/Linux (Windows PowerShell: `$env:PYTHONPATH='src'; python -m pytest -q`).

## Pantallas reales (HTML, CSS, JS)

- **Visión general**: créditos, figuras, jornada cerrada y balance del observatorio; aviso de naturaleza ficticia.
- **Mi club**: hasta 5 activos por club; selección de 3 titulares; bloqueo por hora UTC; modificar la propiedad no modifica alineaciones históricas.
- **Mercado**: 10 figuras sintéticas inequívocamente numeradas, precios fijos explícitos, crédito inicial 100, compra/venta registradas y propiedad exclusiva (invariante transaccional). Sin subastas, cesiones ni transferencias diferidas todavía.
- **Jornadas**: pasado con eventos inventados y scoring `DEMO_RULE`, futuro sin cobertura/puntos; tablas ordenadas de equipos. Sin atribución causal o meritocrática.
- **Observatorio**: 20 recuentos reales *transcritos manualmente de una página oficial* y advertencias de limitaciones; esos datos nunca llegan al fantasy.

**Reto científico vs mecánica:** la puntuación es convencional y sujeta a sesgos de oportunidad y cobertura. 0 puntos sintéticos en un expediente con cobertura ficticia completa no legitima atribuir 0 a un político real. No publicar rankings de personas reales antes de auditorías legales, de cobertura y equidad.

## Rutas API locales

| Método | Ruta | Entrada | Salida |
|---|---|---|---|
| GET | `/api/health` | — | salud + veto a scoring real |
| GET | `/api/state` | — | clubes, mercado, rondas, eventos de demo y agregados observatorio |
| POST | `/api/clubs` | `{"name":"Club Q"}` | club con 100 CR |
| POST | `/api/buy` | `{"club_id":"...","figure_id":"F04"}` | compra atómica |
| POST | `/api/sell` | ídem | venta atómica |
| POST | `/api/lineup` | `{"club_id":"...","round_id":"next","figures":["F01","F02","F03"]}` | alineación de 3 |

Requiere `Content-Type: application/json`, cuerpo hasta 16 KiB, mutaciones solo en POST, comprobación básica de Origin y `127.0.0.1` como bind. **No hay autenticación**, no usar como plataforma multiusuario expuesta. Los endpoints y el esquema SQLite son de demostración y pueden cambiar.

## Separación de datos

Una base local de fantasía aloja **solo figuras sintéticas**, eventos con URLs `synthetic://fixture` y resultados de la demo. Los recuentos manuales van por otro canal de solo lectura y no generan score. El almacén `warehouse.py` (también separado) admite únicamente eventos **previamente normalizados**, con SHA256 esperado, IDs y timestamps conscientes de zona; no certifica el significado institucional ni cobertura.

## Pruebas de aceptación

- Idempotencia al sembrar fixtures; coste de compra y crédito, venta y trazabilidad.
- Validación de nombres y entradas, rechazo de doble propiedad, crédito insuficiente, límite de plantilla y ventas ajenas.
- Competiciones por un mismo activo: un solo ganador vía `BEGIN IMMEDIATE`.
- Alineación de exactamente tres; solo activos poseídos, bloqueo inclusive en la hora exacta y conservación histórica tras vender.
- API local HTTP, políticas básicas contra cross-origin, tipos MIME requeridos, rutas no declaradas rechazan.
- Warehouse: hash antes de cargar, rollback total tras fila incorrecta, revisiones versionadas y filtrado temporal estricto (`first_public_at` **y** `recorded_at` antes de consulta).
- Fuente de recuentos separada del juego. Suite Python automatizada; `node --check` para sintaxis JS. No hay una prueba de navegador end-to-end certificada; el navegador headless de este entorno impide la navegación de localhost.

## Riesgos y bloqueadores explícitos

1. Los 10 fichajes son personajes **ficticios**, no miembros reales del Congreso. Datos solo para probar UX y transacciones.
2. Faltan fuentes nominales oficiales con hash y marcas de publicación cotejados, identidad de persona persistente, vigencia de mandato, correcciones y cobertura por institución.
3. Las estadísticas de la sesión 193/2026 son un piloto descriptivo manual; no conforman el universo longitudinal ni garantizan correspondencia 1 a 1 con los JSON descargables.
4. Motor competitivo aún simplificado: sin login, ligas privadas, subastas, mercado fluctuante, pronóstico ni escalado multiusuario. Las solicitudes de un cliente HTTP malicioso con acceso al localhost podrían modificar el juego; no se permite exposición en internet.
5. No se ha conseguido guardar este árbol en GitHub: conector HTTP 403 en repositorio nuevo.
6. Falta validación visual en navegador real; CSS responsive ha sido implementado y revisado estáticamente, no se certifica acceso móvil.

## Próximo corte producto

Autenticación de clubs y control de permisos; mercado con ofertas y adjudicación determinista; snapshots de plantilla e histórico de cambios; ficheros de migración; interfaz móvil ensayada; CI/GitHub al recuperar acceso; contrato formal para ingesta nominal (sin adivinar su schema). Investigación cuantitativa solo después de verificar microdatos y exposición temporal.
