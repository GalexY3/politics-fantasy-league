# PF-BR30G — contrato de continuidad (25/10/2026)

**Autorización:** 30 ciclos adicionales de BRANCHING empírico-productivo, conforme a la concesión del usuario en el chat actual. Se parte de BRANCH30F sin repetir sus 30 auditorías retrospectivas. No confundir autorización con ejecución ni inflar resultados con pruebas unitarias.

**Estado y evidencia ya conocida (expone selección adaptativa):** Congreso Abierto `pleno.jsonl` blob Git `71918bb689c7a62cfbbdafe0b9248eac6b5c4be1`, 2.175 votaciones, 34.654 posiciones no enlazadas; BR30F 125 inversiones estrictas y 24 discrepancias que implican empate. Importador `importar-votaciones.ts` blob `2a9d63c7b247cf6ad2a74b03e9c4afd2a6bfa47e`: mapa nombre-código desde `diputados_base.tsv`; los nombres no resueltos no se incorporan al diccionario nominal, aunque los recuentos generales los incluyen.

**Evidencia independiente limitada disponible antes del análisis:** https://www.quienvota.org/ declara 2.176 votaciones, 761.568 registros individuales, 412 diputados históricos (350 activos) y 147 sesiones. Son declaraciones publicadas por otra fuente; no se ha descargado y conciliado su archivo fila a fila. La URL JSON nominal oficial de la sesión 193 está enlazada desde https://www.congreso.es/es/opendata/votaciones, pero descargar bytes falló en este entorno.

## Ciclo C01 — metadatos y mecanismo histórico (retrospectivo/documental)
A. Pregunta: ¿es plausible que un diccionario limitado a la fotografía actual cause pérdida de cobertura retrospectiva?
B. Rivales: restricción de identidades históricas; fallos de ingestión; desajustes de universo, calendarios y criterios.
C. Contraste: metadatos de dos proveedores y revisión del importador; no atribuir las diferencias a individuos ni asumir equivalencia de las dos colecciones.
D. Instrumentos: URLs, blobs y fechas de consulta.
E. Resultado: lectura documental; se consignará después, sin considerarla experimento independiente.
F. Auditoría: números totales de dos sitios no prueban igualdad de voto a voto.
G. Confirmación: necesita originales oficiales y join histórico, ausente.
H. Priors: revisar condicionalmente mecanismo de exclusión.
I. Validez: documental; no prueba causal.
J. REPAIR_SOURCE antes de inferencias de comportamiento.

## Ciclo C02 — auditor original versus roster actual (producción; diseño previo a la implementación)
A. Unidad: voto; estimando: distribución por opción oficial de las filas nominales con y sin correspondencia exacta en roster, y comparación con códigos de la fuente secundaria.
B. H1: nombres originales no resueltos; H0: resolución completa; H_otra: duplicados, colisiones o errores.
C. Validar nominal original y agregados oficiales, resolver nombres por igualdad estricta con `apellidos, nombre` del TSV, comparar códigos por opción; preservar 4 categorías, sin imputación. En casos de colisiones, invalidar.
D. Código Python estándar; fixtures independientes con errores adversariales; salida exclusivamente agregada y SHA256.
E. Solo etiquetar como evidencia empírica cuando se ejecute sobre JSON original verificado; fixtures se etiquetan SOFTWARE_TEST_SYNTHETIC.
F. Rechazar categorías desconocidas, códigos duplicados, conteos inválidos, ambigüedades y discordancias en set; no publicar nombres.
G. Pruebas sintéticas no son replicación externa.
H. Registrar favor y contra del prior específico; no transferir al parlamento sin campo.
I. Validez funcional versus externa separadas; VSDS 1/3 y CT2 predictivo 24/100 de partida.
J. CONTINUE hacia voto oficial emparejado solo tras tener bytes.

## C03–C30
C03–C08: pares originales Congreso vs fuente secundaria, fechas y hashes; C09–C14: roster y pertenencia temporal; C15–C20: sensibilidad de errores de cobertura por año, margen y grupo; C21–C25: predicción longitudinal con paridad as-of y baseline fuerte; C26–C30: integración en observatorio/fantasy, UX y protocolos de puntuación. **Todos NOT_EXECUTED** hasta disponer de resultados instrumentados y fichas A–J separadas. El branching requiere registrar distancia DRIFT y congelación cuando cambie estimando, fuente o mecanismo.

**Governance:** AB 3.2.1 O1–O6; selección explícita, fuente y licencia, trazas por commit, hallazgos negativos y actualización de priors. El exceso de pruebas sobre una misma fuente no equivale a replicación independiente; no puntuar personas reales ni afirmar validez causal.
