# R04 · Auditoría de readiness y seis puertas de lanzamiento — 27/10/2026

**Estado: NO APTO para lanzamiento con políticos reales.** El índice contractual V4 36,90% no constituye preparación regulatoria, seguridad o aceptación científica. Ninguno de los seis gates alcanza el nivel mínimo 4 definido en `progress_api.py`.

| Gate exacto | Nivel V4 | Evidencia existente | Aceptación pendiente |
|---|---:|---|---|
| `src.registry` Registro de partidos y candidaturas | 0/5 | Catálogo JEC/BOE, formulario RPP oficial, anuarios agregados | Fila original verificable de RPP por partido, identidad legal de coaliciones y derechos por dataset |
| `id.real` Identidad multifuente | 1/5 | Once positivos históricos, casos de homónimos/atributos conflictivos, nombres de BOCG | Muestra adjudicada independiente que contenga falsos enlaces y homónimos exactos, versionado de altas/bajas |
| `ev.person` Eventos individuales | 1/5 | Dos BOCG, DSCD 2026, fechas de condición plena/credenciales y controles de filas | Ingestión reproducible con identidad y `first_public_at` controlado, cobertura y temporización por evento |
| `sec.auth` Autenticación multiusuario | 0/5 | Demo local, protección Host/Origin y bind 127.0.0.1 | Diseño de cuentas/sesiones, CSRF/autorización, abuso, revisiones de seguridad y tests adversariales |
| `qa.endtoend` E2E | 3/5 | Smoke Chromium local anterior; tests HTTP de fuente escritos | Pipeline entero desde original hasta evidencia, decisiones, demo de usuario y seguridad con datos lícitos; nuevas pruebas HTTP en CI |
| `launch.hosted` Despliegue seguro | 0/5 | Ninguno, intencionalmente | Piloto cerrado, seguridad, observabilidad, backups, eliminación, licencias, y pruebas con usuarios |

El servidor `src/politics_fantasy/server.py` advierte explícitamente que **no** tiene autenticación de sesiones y se ata a `127.0.0.1`. El nuevo `GET /api/source-stages` muestra solo metadatos de **tres documentos en cuarentena** con `first_public_at=null` y `real_person_scoring=false`. Hay cuatro pruebas HTTP publicadas de dicha ruta pero aún no ejecutadas. No exponer por proxy ni activar scoring real.

**Cadena de dependencias útil para próximos ciclos:** primero fuentes originales, vocabulario jurídico y permisos; segundo identificación y vigencia temporal independiente; tercero trazabilidad de datos y pruebas E2E; cuarto evaluación científica y piloto de usuario; quinto autenticación/operación pública una vez que haya producto permitido. La seguridad de usuario debe diseñarse desde el inicio, pero no adelantar un deployment público para aumentar ficticiamente un porcentaje.

**Riesgos críticos:** (1) confundir documento firmado con fuente disponible en fecha del acto; (2) inferir méritos individuales mediante recuentos; (3) trasladar datos personales públicos a un uso nuevo sin base/cumplimiento; (4) unión por posición, sigla, asiento o fecha de nacimiento rígida; (5) métricas de QA basadas en tests **solo escritos** o sobre fixtures. La revisión de reutilización [A11](../../docs/DERECHOS_FUENTES_ABH45_20261027.md) no sustituye revisión de protección de datos.

**Decisión R04:** gates 0/6; no cambio de VSDS, CT2 ni N1–N3. PFL continúa como demo sintética local y observatorio en investigación.
