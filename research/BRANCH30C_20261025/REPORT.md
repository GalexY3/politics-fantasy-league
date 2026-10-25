# Informe BR30C: 30 ciclos con branching y producto v0.6

**Fecha**: 25-10-2026. **Alcance:** 30 contratos de ingeniería A–J, no 30 estudios empíricos independientes. Diseño A, B, C, D, E congelado progresivamente antes de implementar cada lote: GitHub commits listados en `CYCLES_LEDGER.json`. El código completo no se congeló antes de cada cambio: exploración de ingeniería, no afirmación confirmatoria según O2/O3. Los saldos antiguos no fueron consumidos.

## Resultados

| Lote | Ciclos | Rama | Instrumento | Pruebas de suite acumuladas |
|---|---:|---|---|---:|
| A | 01–06 | CSV tercero por grupo, integración y conservación | `groupvotes.py` | 123 |
| B | 07–12 | descriptivos de cohesión y no-votos explícitos | `groupmetrics.py` | 129 |
| C | 13–18 | streaming acotado y revisiones de snapshots | `groupvotes.py` | 135 |
| D | 19–24 | tercera fuente opcional en CLI, informe y navegador | `field_cli.py`, `field_api.py`, `app.js` | 141 |
| E | 25–30 | puerta de identificabilidad, elegibilidad y temporalidad | `readiness.py` | 147 |

Cada contrato tiene A–J y falsador explícito en el ledger; 30/30 tests nuevos superados, sin repetir la misma prueba con semillas como ciclos independientes. **Incidencia QA real**: cuatro pruebas del lote E fallaron inicialmente por usar `tmp` en vez del fixture `tmp_path`. Reparadas antes de release, sin cambio en datos ni modelo, suite 147/147 tras la reparación. Esta corrección no añade ciclos ni soporte científico.

## Validez

- Fuente institucional disponible como *documentación pública*, no como bytes CSV/JSON descargados y certificados aquí; no se conocen esquemas reales contra los que validar parser. Puede cambiar el formato, y una fuente de terceros puede incluir filtros.
- `NO_VOTE` solo se admite cuando el archivo contiene expresamente «No vota»; la ausencia nunca implica abstención ni ausencia parlamentaria.
- Relacionar mayorías de grupos con disciplina individual sería falacia ecológica, no conclusión de este producto.
- Los hashes son hashes de datos descargados localmente, no firmas del Congreso ni un sello contra un adversario que pudiera reemplazar los archivos.
- `research_readiness` sigue en NOT_READY_FOR_EMPIRICAL_CLAIMS aun cuando coinciden los tres CSV: faltan censo en fecha, primera publicación, fuente oficial independiente y comparador temporal de campo.
- Usuario puede auditar sus archivos locales, bajo licencia y atribución correspondientes. Publicar solo resultados agregados, no perfiles ni rankings.

## CT2/VSDS y decisión

**VSDS:** 1/3 (instrumento funcional). Grados científicos AB N1=N2=N3=0. **CT2 predictivo:** 24/100 (juicio ordinal). No elevar el valor por pruebas unitarias. Se generan figuras de escala completa y ampliada, con trayectoria llana.

**AB-DECIDE:** CONTINUE_PRODUCT + REPAIR_SOURCE_ACCESS. Más simulaciones del mismo generador no resolverán el cuello de botella. Requiere obtención real de tres tablas, extracción inmutable, validación aleatoria contra JSON originales, historia de primera publicación y datos de censo históricos.

**Estado de despliegue:** app solo local; sin sesiones ni protección web pública completa. `GET /api/field` no expone personas. QA en navegador humano/automatizado todavía no completado en esta campaña.

**Migración:** el repositorio GitHub de AB es hospedaje temporal; migrar después al repositorio dedicado `GalexY3/polictics_fantasy_league`, conservando SHA/historial/metodología.

**Autorizaciones**: 30 nuevos BR30C realizados como ingeniería (0 pendientes este bloque); siguen sin consumir 12 PF-B50, 45 F45 y 19 AB20 de bloques anteriores.
