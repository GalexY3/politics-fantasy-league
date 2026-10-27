# Politics Fantasy League · cierre AB-H CONT10 (27/10/2026)

**Autorización de usuario:** «Concedido» a solicitud de diez ciclos AB-H adicionales con branching; instrucción posterior de terminar todos los concedidos. **Cerrados C01–C10: 10/10 registrados A–J, 0 pendientes de este permiso.** Esto no significa 10 descubrimientos independientes ni 10 tests ejecutados de suite. AB-R investigación y AB-P producto se registran por separado. Los microtests ejecutados se distinguen expresamente de los pytest incorporados pero **no ejecutados**.

**Rama:** `research/pfl-codex-contributions-20261027`. Sin merge a `main`, sin activación de CI/Actions, sin originales privados en Git, sin puntuación de personas reales.

| Ciclo | Modo | Resultado verificable | Límite |
| --- | --- | --- | --- |
| C01 | AB-P | Replay JS independiente de GitHub Atlas seed+0001–0020, 63 nodos, 81 aristas, 119 runs y 44 complaints. | No check Python nativo ni hash estado canónico. |
| C02 | AB-R | Semántica conceptual institucional de presencia sin voto en Senado. | No equivalencia oficial exacta del literal XML `NO VOTAN`. |
| C03 | AB-R | Condiciones Senado open data CC BY 4.0 salvo excepciones; seis distribuciones de listas X–XV (tipoFich=9). | No licitud de scoring personal ni licencia de todo fichero fuera del ámbito. |
| C04 | AB-P | Actualización y read-back SHA Git de matriz documental de derechos; protección de privacidad preservada. | No análisis jurídico de producto ni gate levantado. |
| C05 | AB-R | Vías oficiales del RPP identificadas, sin un original registral por formación; STOP_R5 de consultas equivalentes. | No certificado firmado ni partido individual validado. |
| C06 | AB-P | Auditoría JS del parentesco 0021/0022 y sus cinco recibos nuevos: 63/81/124/44 derivado. | No replay canónico Python de los 22 lotes. |
| C07 | AB-P | Corrección de CLI: falta de tamaño declarado retorna código 2 en vez de 0; prueba aislada del mismo código SHA antes/después y prueba de regresión añadida. | Git prereg se asentó después del prototipo inicial por bloqueos de escritura; **no** atribuir descubrimiento preregistrado. Pytest del repo no ejecutado. |
| C08 | AB-P | `fcntl.flock(LOCK_EX)` durante escritura+fsync de JSONL. Contraste sintético local de 16 fragmentos: 0 JSON válidos sin lock, 16/16 con lock. | Lock asesor/cooperante POSIX; test del repo añadido, aún sin ejecución nativa. No power crash. |
| C09 | AB-R | `secure_store.py` hacía solo 2 `fsync(fd)`, ninguno en directorios, frente a documentación Linux `fsync(2)`. | Fuente y manual de API, no pérdida real demostrada. |
| C10 | AB-P | `os.fsync(parent)` tras crear directorio, `os.fsync(folder)` tras enlazar/limpiar objeto y tras apéndice ledger. Lectura Git Blob y prueba aislada POSIX de soporte de fsync(dirfd). Dos regresiones sintéticas nuevas. | Suite pytest no ejecutada; durabilidad completa/transacción objeto+manifest no demostradas. |

## Cambios de código y tests

1. `src/politics_fantasy/private_audit_cli.py` y `tests/test_private_audit_cli.py`: sin código 0 cuando `legacy_size_without_bytes > 0`. Cambio principal [8d228a9](https://github.com/GalexY3/Metodologia-AB/commit/8d228a90dbf5f476170220a3a12b2a5a366a9901), test [1640330](https://github.com/GalexY3/Metodologia-AB/commit/1640330db721930bed4b658932efe27dde6fcaa2).
2. `src/politics_fantasy/secure_store.py`: serialización cooperativa de cada línea JSONL frente a escrituras parciales. [301ee01](https://github.com/GalexY3/Metodologia-AB/commit/301ee015352809fe2cd7a091e5858cb5fb411e9), prueba [ca352fd](https://github.com/GalexY3/Metodologia-AB/commit/ca352fdf0fb1d907705bbb90039fe8ca79c82a9a).
3. Barreras de metadatos `fsync` en el mismo módulo ([1fd57dd](https://github.com/GalexY3/Metodologia-AB/commit/1fd57dd85a2441f0eeae8f5ed019bb12065d98e9), [9950b8d](https://github.com/GalexY3/Metodologia-AB/commit/9950b8d86a11d1d35554d814365bcb5a009cc3ae), [89597dc](https://github.com/GalexY3/Metodologia-AB/commit/89597dc14d325de32c4893be8e2e28d53b01c210)); pruebas agregadas [5f40e8b](https://github.com/GalexY3/Metodologia-AB/commit/5f40e8b160b19c40ef5f1411a8b9aef1eb7c7e96), corrección de literal de salto de línea [62aea43](https://github.com/GalexY3/Metodologia-AB/commit/62aea430aed7b13bc9d0e36508df92c4329c9807).

Documentación Linux de la necesidad de `fsync` sobre el descriptor del directorio: https://www.man7.org/linux/man-pages/man2/fsync.2.html. Se obtiene mayor cobertura de sincronización de metadatos, **no** se demuestra atomicidad transaccional ni protección frente a fallo eléctrico en condiciones reales.

## Atlas, métricas y límites

- Lotes append-only: `0001–0023`, con `0021` (C01–C04), `0022` (C05), `0023` (C06–C10), ver `ab_atlas/updates/`.
- Contadores deducidos del replay de 20 lotes y de las 10 adiciones `run.add` realizadas en `0021–0023`: **63 nodos, 81 aristas, 129 runs, 44 complaints**. No hay validación por `atlas_delta.py check` del estado completo de 23 lotes, ni SHA canónico.
- Sin promoción: madurez contractual **36,90%**, CT2 identidad **29/100** ordinal, VSDS **1/3**, N1/N2/N3 nuevos **0/0/0**, gates **0/6**. Los avances documentales y de seguridad no equivalen a preparación para publicar o puntuar políticos reales.
- **No constan** ejecución de la suite Python completa, suite Node nueva, pruebas del checkout exacto en Windows, pruebas hardware de crash, `first_public_at` institucional ni manual oficial que resuelva el literal XML `NO VOTAN` para casos reales.

## Siguiente intervención, si se autoriza una nueva campaña

Primero, **Codex en checkout completo de la rama**: ejecutar `python ab_atlas/atlas_delta.py check --base proyectos/politics-fantasy-league/ab_atlas/seed.json --updates proyectos/politics-fantasy-league/ab_atlas/updates`, guardar salida, hash canónico y estado de gates; después `pytest` completo y suite Node, focalizando las regresiones C07, C08 y C10. No activar Actions costosas ni fusionar `main` sin nueva aprobación específica. En segundo término, contrastar interrumpir procesos y verificación/integridad privada de objetos y ledger con datos exclusivamente sintéticos en un sistema POSIX desechable. Para AB-R, únicamente retomar RPP o semántica del Senado con un original primario comprobable y nuevo instrumento, no repitiendo enlaces de catálogo.

**Permiso CONT10 agotado: 10/10. Toda campaña siguiente necesita autorización nueva y plazo/cantidad explícitos.**
