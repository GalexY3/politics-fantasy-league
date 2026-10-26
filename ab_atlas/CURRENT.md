# AB Atlas — Politics Fantasy · estado inicial (26-10-2026)

- **Modo:** AB-H; producto AB-P + investigación AB-R, no confundir sus validaciones.
- **Punto de partida:** `seed.json` (snapshot editorial, no sincronización automática).
- **Último lote aplicado:** ninguno (`parent_batch=""` para el próximo).
- **Vista HTML:** `AB_Atlas_Politics_Fantasy.html`, snapshot generado previo a nuevas actualizaciones.
- **Contrato del producto:** demo local con mercado y clubes sintéticos; producto público NO LISTO. Scope PFL-V1 revisión 3: índice convencional 36,350%, no probabilidad de éxito ni estimación temporal.
- **Seis gates críticos:** originales de registro/candidaturas, identidades reconciliadas, eventos individuales temporales, autenticación/autorización, pruebas E2E amplias y despliegue seguro. Todos pendientes o bloqueados.
- **Evidencia científica:** la creación del Atlas no modifica CT2 ni VSDS; no atribuir resultados de campo a fixtures.
- **Prioridad:** fuentes originales e identidades históricas; solo después eventos y modelos empíricos, sin confundir candidaturas con partidos ni personas.
- **Complaints:** no registradas en este snapshot; eso no certifica ausencia de errores.
- **Coste:** comprobar cuota GitHub Actions antes de activar CI costosa.

**Protocolo del agente:** leer este archivo primero; consultar la rama relevante del JSON y el ledger de la campaña; al terminar X ciclos añadir UN lote nuevo `updates/NNNN-IDENTIFICADOR.json`, validarlo con `ab_atlas/atlas_delta.py check`, actualizar este resumen. No sobrescribir el seed. Conservar IDs, estados negativos y justificaciones. El siguiente agente debe confirmar saldos de ciclos antes de ejecutar.
