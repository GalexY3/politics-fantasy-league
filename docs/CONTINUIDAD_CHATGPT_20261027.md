# Continuidad · Politics Fantasy · 27/10/2026 tras ZIP original entregado

**Nuevo estado:** el usuario entregó a ChatGPT el ZIP privado `Politics-Fantasy-fuentes-para-ChatGPT-20261027.zip` (SHA-256 `47bbe80b69d8fd3b153a3e7368ac5542b6b03dd42dd65be76b8a97f495575bf4`). Los **11 originales** pasaron SHA y CRC y se usaron en C05–C12 (ver [informe](../research/ABH_BRANCH20C_20261027/REPORT_ORIGINALS_C05_C12.md)). **No están en GitHub**; un agente en otra sesión necesitará acceso a este archivo adjunto de la conversación o una nueva entrega de los mismos bytes. No fingir acceso a `C:\Github\...`.

**Último balance de autorización:** BRANCHING20C está concedido y es independiente del bloque viejo. **C01–C12 consumidos (12/20), 8 ciclos restantes**, STOP_R5 hasta conseguir fuentes/receipts nuevas discriminantes. No solicitar otro bloque de 20 por inercia.

**AB Atlas:** [CURRENT](../ab_atlas/CURRENT.md), seed + deltas 0001–0009; reproducción estructural de nueve JSON PASS (39 nodos, 57 relaciones, 33 runs, 22 complaints). Incidencia de 0008 reparada y consignada en 0009. El validador Python oficial `atlas_delta.py check` permanece pendiente. El HTML es una fotografía antigua.

**Datos confirmados en origen:** Senado 259 cadenas, 10 votos con día 08/10/2025 aunque sesión rotulada 07/10; Congreso 1.400 filas, 213 bajas posteriores al voto, `asiento=-1` repetido 11/11/15/30; Interior 16×350 electos y 1.306 nombres que se repiten en elecciones distintas; BOE JEC 2023 vs XLSX Interior 52 provincias / 350 filas, 346 nombres exactos y 4 discrepancias textuales explicadas solo de forma contextual. No hay correspondencia longitudinal certificada ni `first_public_at` por observación.

**Importante:** la nueva guardia `source_original_qa.py` superó 8 pruebas locales, sin conectarse al servidor ni habilitar puntuaciones políticas. No publicar originales nominales, PDF completos ni nombres privados en los repositorios de análisis sin revisión de permisos.

---

## Guía histórica anterior al traspaso del ZIP

# Continuar Politics Fantasy desde ChatGPT

1. Abrir la rama `research/pfl-sources-reconcile-20261027`. Leer [CURRENT](../ab_atlas/CURRENT.md), el [informe AB-H](../research/ABH_RECON_20261027/REPORT.md) y el [catálogo de fuentes](CATALOGO_FUENTES.md). `main` y las cuatro ramas históricas no contienen todo el trabajo fusionado.
2. La autorización de 9 + 4 ciclos anteriores sigue sin conciliar. El investigador no recuerda si pertenecen al mismo permiso. Con los cuatro nuevos, si fuera un único bloque y no hubo otros consumos, quedan como máximo **tres**; no es un saldo definitivo. Continuar adaptativamente y aplicar R5 si faltan contrastes discriminantes.
3. Las capturas de Interior y Senado y los ZIP recuperados de Actions son **locales y están excluidos de Git**. Si ChatGPT no puede recuperar los bytes oficiales, adjuntar `C:\Github\Politics-Fantasy-fuentes-para-ChatGPT-20261027.zip`. Incluye 11 archivos originales, cuatro votaciones nominales del Congreso, dos PDF BOE y un manifiesto con URL y SHA-256. No incluye las declaraciones económicas personales contenidas en uno de los artefactos completos.
4. Los tres artefactos originales de Actions están en la copia local bajo `data/raw/github_actions_20261026/` y se mantienen privados. Sus manifiestos cotejan 8/8 archivos de cada sondeo del Congreso y 2/2 PDF BOE. Las descargas son previas, no nuevas ejecuciones; detalles y hashes en [recibo de rescate](../research/ABH_RECON_20261027/RESCATE_FUENTES_20261027.json).
5. El siguiente contraste útil es un conjunto reducido de identidades adjudicadas con controles de homónimos y falsos enlaces y prueba de vigencia/primera publicación. La coincidencia de 259 nombres del Senado es exploratoria, no un crosswalk verificado. Revaluar derechos y privacidad para cualquier uso o distribución de los datos.

El mapa se reconstruye desde `seed.json` y los lotes de `updates/`; el HTML es una fotografía antigua. No elevar CT2, VSDS o gates por recuperación de archivos o pruebas de software.
