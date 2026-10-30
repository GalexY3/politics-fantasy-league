# PFL · STRIDE, abuso y reputación — revisión de alcance (28/10/2026)

**Tipo:** modelo de amenazas verificable, no mitigación terminada ni auditoría jurídica. **Estado:** SPECIFIED_ONLY, no afecta 0/6 gates ni V4. Revisa código de demo local y propuesta de producto público con separación deliberada. [Protocolo ético](VALIDACION_ETICA.md) · [derechos y finalidad](RIGHTS_AND_PERSON_SCORING_GATE_20261028.md) · [arquitectura](ARQUITECTURA.md).

## Límites de confianza

1. **B0: navegador de un usuario en su equipo ⇄ servidor local**: `src/politics_fantasy/server.py` usa `127.0.0.1`, filtro Host, filtro Origin, JSON máximo 16.384 bytes y CSP. El servidor **no tiene** cuentas, autenticación por usuario ni CSRF robusto; **no se puede desplegar tras reverse proxy**.
2. **B1: fuente oficial ⇄ capturas y caché**: `src/politics_fantasy/evidence_warehouse.mjs` comprueba esquemas y estados, no puede certificar veracidad por URL con título “OFFICIAL”. Capturas `raw`, SHA-256, `first_public_at`, licencia y revisiones son pruebas distintas. Los originales confidenciales no van a Git ni a cliente.
3. **B2: evento ⇄ identidad y valoración**: `src/politics_fantasy/events.py`, `scoring.py` y `docs/VALIDACION_ETICA.md` separan hecho documentado, interpretación, predicción y puntos convencionales. No deducir ideología, calidad moral, culpa o ausencia a partir de un voto o de registros faltantes.
4. **B3: usuario/club ⇄ mercado/jornada**: saldo, alineación y exclusividad deberían ser transacciones y aislar cuentas en un servicio público. La demo ficticia no certifica resistencia a carreras interusuario, bots, fraude o manipulación.
5. **B4: aplicación pública ⇄ sujetos de datos/reclamaciones**: perfiles y scores de personas identificables **bloqueados** hasta base jurídica, minimización, evaluación de impacto si procede, fuentes, notificación, ejercicio de derechos y evaluación experta; reglas públicas no equivalen a consentimiento.

## Registro de amenazas STRIDE y vías de abuso

| ID | Categoría | Superficie y ataque plausible | Riesgo | Medida presente comprobable | Requisito para exposición pública |
|---|---|---|---|---|---|
| S01 | **S — Suplantación** | Host manipulado, DNS rebinding o origen falso inyecta acciones en la demo | Alto | Filtro de Host/Origin y escucha loopback en `server.py` | Test de encabezados adversariales real y autenticación multifactor o mecanismo de sesión según amenazas; no usar servidor demo públicamente |
| S02 | **S — Suplantación de identidad institucional** | Homónimo de cargo o partido con siglas repetidas produce atribución incorrecta | Crítico | IDs tipados, ambigüedad y colisiones en almacén de evidencias; **no hay corpus nominal conciliado** | Originales institucionales, falsos enlaces negativos, historial as-of y revisión humana, prohibir auto-match por nombre |
| T01 | **T — Manipulación de datos** | CSV “oficial” recreado en un espejo o fuente corregida ex post altera identidad/eventos | Alto | `source_version`, `raw_sha256` y estados de fuente del warehouse; originales de varias campañas externos aún no autenticados | SHA256 crudo del emisor, trazabilidad de transformaciones, reconciliación, control de versiones y cuarentena |
| T02 | **T — Alteración de juego** | Compra doble, puntos reescritos tras cierre o cambios de alineación posteriores | Alto | Demo local con mercado/jornada SQLite y scoring versionado | ACID multiusuario + pruebas de carreras, congelación de reglas, snapshot antes de jornada y auditoría inmutable |
| R01 | **R — Repudio** | Responsable no puede explicar modificación, revocación de logro o ajuste de puntos | Alto | Versionado de reglas/eventos y `ACHIEVEMENTS_REGISTRY.json` con log append-only de adjudicaciones | Registro firmado/append-only de acciones de privilegio, evidencia original, corrección reversible, revisión de reclamaciones |
| I01 | **I — Divulgación** | Exponer archivos nominales, opiniones o claves en logs, exportación CSV o API | Crítico | Prohibición explícita de perfiles de votantes y borradores de permisos en almacén; demo evita log de tokens | Inventario de datos, bases legítimas y minimización, pruebas DLP y exportación, cifrado/repositorios separados, privacidad y RGPD |
| I02 | **I — Inferencia reputacional** | Scores de figura pública se interpretan como calidad/ideología, acusaciones o “quién no participó” | Crítico | `scoring.py` declara puntos sintéticos, `RIGHTS_AND_PERSON_SCORING_GATE` mantiene **BLOCKED** | Rediseño propósito, derechos, revisión legal/DPO, procedimiento de corrección, nunca puntuación moral ni ausencia=0 |
| D01 | **D — Denegación de servicio** | POST masivos a rutas /api/buy, /api/simulate-round o descargas agotan CPU y SQLite | Alto | Límite de cuerpo 16.384 bytes, loopback exclusivamente | Cuotas por identidad, limitaciones de tasa, colas, límites operacionales y prueba de carga controlada |
| E01 | **E — Elevación de privilegios** | Rutas de demo sin auth permiten que cualquier navegador local manipule clubs ajenos | Crítico para hosting | **No existe auth multiusuario** y el propio comentario del servidor prohíbe reverse proxy | RBAC/ABAC sobre club/acción, protección CSRF, sesiones seguras, control de objeto, pruebas IDOR y rate limits |
| E02 | **E — Moderación y abuso comunitario** | Bots, nombres difamatorios de club, capturas con puntuaciones como “ranking real de dignidad” | Alto | Texto ético y aviso de demo sintética, **sin moderación real** | Términos de uso, reglas de nombres, limitación de abuso, impugnación y retirada del contenido, moderación y apelación |

## Matriz falsadora (tests concretos, NO declarados PASS)

- `NEG-HOST`: petición GET con Host `evil.example` debe devolver 403 y no modificar estado.
- `NEG-ORIGIN`: POST con Origin externo y Host local debe devolver 403.
- `NEG-IDOR`: cuenta A compra/vende figura de club B: 403, cero efectos; **no es implementable en demo sin auth**, es requisito bloqueador.
- `NEG-RACE`: dos transferencias paralelas sobre presupuesto final; exactamente una se confirma, la otra rechazada, sin saldo negativo.
- `NEG-RAW`: fuente declarada oficial sin bytes crudos SHA-256 verificados: no promover a `RAW_CAPTURED`/admisible.
- `NEG-ASOF`: evento publicado después de corte: ningún score o predicción anterior puede observarlo.
- `NEG-REPUTATION`: intento de alimentar score con acusación, noticia editorial o “voto ausente”: resultado QUARANTINE, no puntos ni ranking.
- `NEG-PRIVACY`: exportación con email, opiniones inferidas, datos de firmantes o secretos: bloquear exportación, log seguro.
- `NEG-RELEASE`: V4=100 o achievements=90 nunca sustituyen certificados de seis gates; release pública con cualquier gate abierto debe fallar.

## Umbrales GO / NO-GO

**Demo local sintética:** permitida de forma acotada cuando loopback y tests propios se ejecuten; no afirma readiness de hosting. **Observatorio público agregado y sin puntuación de personas:** requiere revisión separada de licencia, agregación, QA y seguridad de hosting; reducir alcance en nueva versión, no maquillar V4 actual. **Fantasy público de personas identificables:** NO-GO hasta evidencia original verificable, tratamiento legitimado, identidad y equidad, autentificación real, QA E2E, hosting y piloto con aceptación. Los seis gates permanecen abiertos. **No usar este documento como aprobación de GDPR ni certificado de pentest.**

Responsables de futuras comprobaciones: ingeniería (S01/T02/D01/E01), fuente/epistemología (S02/T01), DPO/experto externo (I01/I02), operaciones/moderación (R01/E02), evaluador de campo independiente (NEG-ASOF/NEG-RELEASE). Vincular tests a commits/versiones exactas.
