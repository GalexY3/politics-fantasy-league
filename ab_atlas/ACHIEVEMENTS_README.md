> **Estado actualizado · 29/10/2026:** Registro **v6** con **90 logros activos, 5 desbloqueados y 6 eventos de auditoría**. La copia incluida en el HTML se sincronizó con el JSON durante T025 para que la apertura local tenga el mismo estado inicial; se conservan las versiones anteriores en Git. [Adjudicación RELEASEPATH5](../research/ABH_RELEASEPATH5_20261028/C03_ACHIEVEMENT_ADJUDICATION.json). El registro no altera el 36,90 % V4 ni los gates. El contenido de creación siguiente conserva el contexto de V1 y ACH20.

# Los 90 logros del AB Atlas · Politics Fantasy League
**V1 · 28 de octubre de 2026** · [Registro canónico](ACHIEVEMENTS_REGISTRY.json) · [Salón visual](ACHIEVEMENTS_Atlas_Politics_Fantasy.html) · [Visor AB Atlas](AB_Atlas_Politics_Fantasy.html)

## Idea y relación con el 100 %
Hay **nueve vías** exactamente iguales a las de `product/progress_scope_v4_20261027.json` y **diez grandes logros iniciales por vía** (90). Cada premio significa una conquista que vale la pena recordar, no un commit, una prueba unitaria ni la redacción de un documento. La vista conserva la inspiración Steam: medallas de **bronce, plata, oro, platino y legendario**, bloqueadas, desbloqueadas y retiradas, con los criterios al hacer clic.

**Conseguir los 90 es una condición simbólica muy ambiciosa y supondría avances sustanciales hacia la versión definida del producto.** No es sinónimo automático de **100 % contractual**, de hallazgo científico, ni de levantar los **seis gates**. Se puede alcanzar 100 % en el marcador de logros sin que un release esté autorizado; en ese caso prevalecen los bloqueos verificables, y el catálogo debe revisarse en una nueva versión. Conservar un porcentaje independiente de logros (desbloqueados/activos) evita duplicar el 36,90 % de la V4.

## Las nueve ramas de logros
| ID | Rama V4 | Peso V4 | Progreso V4 inicial | Logros iniciales |
|---|---|---:|---:|---:|
| `sources` | Fuentes y datos | 18 % | 45,0 % | 10 |
| `identity` | Identidad, coaliciones e historial | 12 % | 42,5 % | 10 |
| `events` | Acontecimientos políticos | 10 % | 35,0 % | 10 |
| `science` | Investigación, predicción y evaluación | 14 % | 27,5 % | 10 |
| `game` | Mecánicas y motor fantasy | 16 % | 45,0 % | 10 |
| `ui` | Interfaz y experiencia de usuario | 10 % | 32,5 % | 10 |
| `security` | Privacidad, seguridad y licencias | 8 % | 20,0 % | 10 |
| `qa` | Pruebas y reproducibilidad | 8 % | 45,0 % | 10 |
| `launch` | Operación, pilotos y lanzamiento | 4 % | 17,5 % | 10 |
| **TOTAL** | | **100 %** | **36,90 % ponderado** | **90** |

**Referencia de estado inicial:** `0/90 desbloqueados`, **sin presunción de que los 90 logros estén realmente inacabados**: algunos antecedentes V4 pueden aportar evidencia para adjudicar premios, pero deben contrastarse específicamente. Los diez por vía son la base inicial, **no una obligación perpetua de mantener diez** si en el futuro se retiran o añaden otros.

## Cómo visualizar y mantener
1. Abrir `AB_Atlas_Politics_Fantasy.html` en un navegador, pestaña **★ Logros (90)**. Es una vista integrada del Atlas de trabajo; los archivos deben conservar su **estructura de carpeta relativa**. También se puede abrir `ACHIEVEMENTS_Atlas_Politics_Fantasy.html` directamente.
2. Cada logro lleva **ID estable**, sección V4, título, descripción, rareza, criterios verificables, estado, evidencia, verificador, fecha, requisitos previos e historial. El catálogo vive en **`ACHIEVEMENTS_REGISTRY.json`**: no se ha insertado dentro del grafo/deltas del Atlas para evitar colisionar con T010, que aún debe reparar `ab_atlas/atlas_delta.py`. La vista HTML es una **proyección lateral**, no una afirmación de que el replay canónico funcionó.
3. La interfaz permite **crear, editar, desbloquear con referencia y verificador, revocar, retirar o restaurar** premios; la retirada es **tombstone**, no borrado que dificulta la auditoría. Se documentan los cambios en `change_log` con secuencia y versión. No se reutilizan IDs antiguos.
4. **Navegador:** las ediciones son **borradores locales**, persistidos opcionalmente en localStorage. **Exportar JSON**; revisar el diff y subir el JSON al repositorio para hacerlo canónico. Este HTML lleva un snapshot V1 embebido para funcionar sin servidor desde `file://`; cuando se sirve por HTTP intenta obtener el `ACHIEVEMENTS_REGISTRY.json` actualizado. Para uso `file://` con versión posterior, **Importar JSON** manualmente o regenerar el HTML con el JSON nuevo, sin fingir que GitHub se sincroniza automáticamente.
5. El desbloqueo no es automágico: debe existir **evidencia inspectable**, quién verifica, cómo cumple el criterio y todas las dependencias previas. La interfaz solo comprueba estructura y declara una **adjudicación humana**, no certifica que la evidencia sea auténtica. Una reclamación o error posterior puede **revocar** el logro con motivo.
6. Un cambio de criterio ya desbloqueado **revoca el desbloqueo**, pues la nueva definición exige una nueva adjudicación. No se permite revocar o retirar un requisito previo de un logro posterior desbloqueado sin resolver antes la dependencia. Nuevas entradas tienen ID `PFL-{RAMAL}-{N}`, nunca reciclado.
7. Antes de aceptar cambios, ejecutar `python proyectos/politics-fantasy-league/ab_atlas/validate_achievements.py [--file RUTA]`, y los tests `node --test proyectos/politics-fantasy-league/tests/test_achievements_atlas.mjs` para **el baseline**. El test inicial fija 9×10 y el HTML V1; en versiones nuevas deberá adaptarse al esquema evolutivo sin modificar la instantánea de referencia.
8. **No editar** `ab_atlas/seed.json`, los 75 deltas existentes o el código corrupto `ab_atlas/atlas_delta.py` por esta función. T010 es independiente: cuando se restaure el checker, valorar un puente de **read-only** entre la información de logros y el grafo, con pruebas, sin meter 90 falsos nodos de progreso ni dar por validado un gate.

## Regla de decisiones y nuevas sesiones
Ante «desbloquea el logro X», el asistente ha de leer **el registro vigente**, corroborar criterios y evidencia con fuentes o pruebas disponibles y registrar **desbloqueo/adjudicación** únicamente si se cumplen. Ante «añade/elimina/cambia el logro», preservar estados y auditoría, explicar qué cambia en el denominador, tratar la eliminación como retirada auditada y versionar la revisión. El usuario puede sustituir metas si cambia el alcance, sin pretender que por ello subió el progreso contractual. Cualquier avance del porcentaje V4 requiere una **adjudicación separada de los 36 hitos y sus fuentes**, no un conteo de medallas.

## Verificaciones de esta creación
En la sesión de diseño se realizó **auditoría estructural en memoria** del registro exacto y de su proyección HTML: nueve ramas, 10 por rama, 90 IDs únicos, pesos V4 que suman 100, ponderado inicial 36,90 %, 90 estados bloqueados, dependencias internas válidas, registro inicial consistente y enlace de la pestaña AB Atlas al Hall. **No** se ha ejecutado aún una prueba real de navegador, el script de Node, ni el validador Python en un checkout íntegro tras esta incorporación. La ejecución satisfactoria de esas comprobaciones continúa siendo requisito para declarar la UI plenamente validada, y **no** se presenta como T010 completada.
