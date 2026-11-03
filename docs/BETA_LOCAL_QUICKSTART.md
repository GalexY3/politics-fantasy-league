# PFL · recorrido de evaluación local de la beta científica

**Alcance:** prototipo en un único ordenador, con datos sintéticos y HTTP
exclusivamente en 127.0.0.1. No autoriza publicar un servicio, incorporar
originales españoles ni puntuar personas políticas reales. La centralidad
corresponde al Observatorio y al Laboratorio; Fantasy es subordinado.

## Comprobar el núcleo científico

Desde la raíz del repositorio, con Python 3.10+ y Node.js instalados:

    python scripts/beta_scientific_smoke.py

El comando no reutiliza cuentas, originales ni bases persistentes del usuario.
Crea un servidor HTTP local y bases SQLite temporales, consulta realmente
/api/health, /api/beta-readiness, /api/scientific-integration-lab y
/api/scientific-registry, verifica SHA-256 del snapshot y los 20 testigos S7
del corte tardío.
Incorpora mediante procesos CLI independientes sandbox_alpha_v1,
sandbox_beta_v1 y sandbox_bad_issuer: dos fuentes lógicas ficticias y un
rechazo. Comprueba cortes early/late, errores HTTP 400/403/503 e integridad
fail-closed al adulterar solamente su propia base temporal. Al finalizar
cierra el servicio y elimina el entorno de prueba.

Un resultado de status PASS y nueve controles acredita **solo** este
recorrido local; no sustituye un ensayo de seguridad de una instalación real,
una revisión de accesibilidad o evidencia externa. Si status es FAIL, el
campo error_code informa del paso sin imprimir datos privados; el proceso
devuelve código no cero. Su regresión reproducible es:

    python -m pytest -q tests/test_beta_scientific_smoke.py

## Arrancar el prototipo interactivo

    python run_demo.py

Abrir http://127.0.0.1:8787. A diferencia del smoke, este lanzador
**sí conserva** datos locales en data/demo/game.db y cuentas de prueba en
data/demo/accounts.sqlite3. Estas cuentas locales no equivalen a identidad
para internet, TLS ni despliegue multiusuario seguro. No exponer el puerto
mediante NAT, túneles, proxies públicos o interfaces distintas de loopback.

Si el puerto está ocupado, se puede seleccionar otro. Para una base aislada
de prueba, se puede elegir una ruta distinta:

    python run_demo.py --port 8788 --db data/demo/beta_separada.sqlite3

El parámetro --port 0 pide al sistema un puerto libre y muestra la URL real.
No existe una opción --host para habilitar interfaces públicas.

**Primera visita, sin cuenta:** desde la pantalla de acceso, pulsa
«Entrar al Observatorio y Laboratorio». El visitante dispone únicamente
de esas dos pestañas; puede examinar los cortes del laboratorio y el
registro sintético S9 con su SHA verificado, sin crear una cuenta ni
acceder al mercado, los clubes o las operaciones POST. El botón de retorno
devuelve al formulario de acceso. Un HTTP 503 o un recibo SHA incompatible
bloquean la vista en vez de conservar datos obsoletos. La exportación y
las acciones de preadmisión quedan fuera del modo visitante.

El Laboratorio muestra modelos rivales B0/B3, sensibilidad condicional S3,
testigos S7 y el registro histórico-relacional sintético S9. Una validación
de sandbox no es admisión científica, licencia, evidencia histórica
española ni estimación causal. El contrato técnico está en
docs/S9_DURABLE_SYNTHETIC_SCIENTIFIC_REGISTRY_20261101.md.

## Bloqueos de la beta pública

STOP_R5 permanece, con **0/6 puertas** y cero ciclos AB-R nuevos.
Faltan universo independiente ALL_RECEIVED, denominador externo, episodios
con negativos/pendientes/censura verificables, dos vintages auténticas,
first_public acreditado, derechos por distribución/revisión/finalidad,
garantías de seguridad y revisión humana del producto. Esta fase es
**local, sintética, no pública**; superar un test HTTP no levanta R5.
