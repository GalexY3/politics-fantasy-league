# P1-ACCOUNTS · Acceso multiusuario local ficticio — listo para revisión

**Estado propuesto:** `READY_REVIEW`, NO `DONE` público. **Cero ciclos AB cargados**: implementación y QA de producto. Se parte del `integration/pfl` HEAD `69ed402dd4a3f25207d9e620ede568b5e92ad8af`. Rama técnica única del hito `feature/pfl-p1-accounts`, destino de PR `integration/pfl`, no main.

## Capacidad entregada

- **Cuentas locales** con usuario normalizado, contraseña 12–128 caracteres derivada por `hashlib.scrypt` y sal aleatoria (16 bytes), verificadas con comparación constante. Duplicados rechazados; sin correo ni datos políticos personales.
- **Sesiones de 8 horas** con token aleatorio opaco almacenado solo como SHA-256 en SQLite, cookie `HttpOnly; SameSite=Strict; Path=/`, revocada en logout. Tokens distintos tras iniciar nueva sesión.
- **CSRF**: acciones de juego requieren secreto obtenido en una sesión autenticada; formulario de acceso exige cabecera AJAX personalizada y origen compatible. El servidor acepta únicamente hosts locales y escucha exclusivamente en `127.0.0.1`.
- **Aislamiento físico de clubes**: cada cuenta recibe un fichero SQLite de juego distinto bajo `data/demo/accounts/<id>.sqlite3`, con figuras y eventos ficticios inicializados de manera independiente. Un ID de club ajeno no existe en la base del usuario y recibe 404; transacciones en una cuenta no cambian el inventario de otra.
- **Interfaz** `index.html` / `web/app.js`: formulario de alta/login, botón de salida, carga de sesión y protección de mutaciones; al cambiar cuenta se borra selección local previa. Las rutas de documentación y datos institucionales de solo lectura permanecen separadas del juego.

## Aceptación automática realmente ejecutada

[GitHub Actions #40995507812](https://github.com/GalexY3/Metodologia-AB/actions/runs/40995507812), HEAD `9f0fe6509b5f74a26241ac75cb39e0c10a912bc1`, ejecutó código con Git blobs congelados de `accounts.py`, `server.py`, `app.js` y `tests/test_accounts.py`. **35/35 tests Python PASS** (nuevos HTTP multiusuario y pruebas de producto heredadas), `compileall` Python y `node --check` del navegador PASS. No basta con que el archivo de test exista; el recibo incluye salida real del runner.

Casos adversariales observados: acceso a `/api/state` y mutaciones sin login devuelven 401; un usuario no lee ni modifica un club ajeno; CSRF omitido o tomado de otra sesión devuelve 403; Origin externo rechazado; inventarios de figuras independientes; contraseñas inválidas, nombres duplicados, logout, nueva sesión con persistencia SQLite y activos estáticos públicos. Las regresiones de `test_product.py` sobre el modo legado de pruebas siguen pasando.

## Límites y aceptación pendiente

El servicio real `serve()` activa siempre la capa de cuentas; `handler_factory(...,accounts_path=None)` conserva un modo interno legado para suites anteriores, **NO seguro para servir a terceros**. La aplicación utiliza **HTTP local sin TLS** y no implementa recuperación de cuentas, rate limiting distribuido, hardening del sistema de ficheros para alojamiento compartido, observabilidad ni revisión de seguridad de producción. No desplegar ni poner detrás de un proxy público.

**Pendiente de revisión humana de producto:** abrir la demo en navegador con dos perfiles locales, comprobar visualmente el alta/login, crear dos clubes, hacer un fichaje y volver a entrar; seguir con P2 (alineación → jornada → resultado) solo tras aceptar P1. El resultado 35/35 da soporte funcional, no aceptación humana ni autorización de despliegue público.

### Instrucción local

```bash
cd proyectos/politics-fantasy-league
PYTHONPATH=src python -m politics_fantasy.server --db data/demo/game.db --port 8787
```

Abrir `http://127.0.0.1:8787/`, crear usuario y contraseña de al menos 12 caracteres, iniciar sesión y crear un club. Nunca puntuar políticos reales ni publicar esta instancia en internet. Las cuentas antiguas no existían: ningún usuario se migra automáticamente desde el club único local; su base anterior no se sirve mediante sesiones nuevas.

**Siguiente hito:** `P2-PLAYABLE-FLOW` después de la aceptación del usuario: acceso → crear club → alineación → jornada ficticia → resultado, recarga y persistencia.

## Nota del repositorio independiente

Los comandos originales escritos para el monorrepositorio deben ejecutarse ahora desde
la **raÃ­z de politics-fantasy-league** (sin `cd proyectos/politics-fantasy-league`).
Los enlaces a Actions de AB describen pruebas histÃ³ricas, no validaciÃ³n del nuevo commit.
La versiÃ³n independiente conserva la restricciÃ³n de operaciÃ³n local y la revisiÃ³n humana pendiente.
