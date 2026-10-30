# T019: originales XML Clerk EE.UU. 2025/2026 y QA

**NO EJECUTADA.** Encargo preparado para Codex/PC, no ciclo AB ni permiso de fusionar, hacer CI costosa o perfilar políticos. Repo GalexY3/Metodologia-AB, base research/pfl-abh5-us-house-20261028. Leer AGENTS.md, AB 3.2.1, Atlas CURRENT y research/ABH_USHOUSE5_20261028/FINAL_REPORT.md antes de actuar. Crear rama de ejecución separada; PR solo borrador contra rama USHOUSE5.

## Originales que faltan
Obtener XML auténticos desde el enlace XML View de las fichas oficiales de https://clerk.house.gov/Votes/2025178 a /2025183 y de /2026178 a /2026183: **12 divisiones**. URL orientativa (verificar por enlace oficial): https://clerk.house.gov/evs/2025/roll180.xml; documentación https://xml.house.gov/. Aquí web XML devolvió errores, la descarga de contenedor falló y el contenedor no tiene DNS externo: **no afirmar original descargado**. Para cada original registrar URL real, TLS, redirecciones, HTTP, UTC, MIME, tamaño, SHA256 de bytes, árbol XML y permisos de uso. Guardar XML nominativo fuera de Git, solo agregados e índices no personales.

Comparar originales contra C01_2025_OFFICIAL_AGGREGATES.json y C02_2026_OFFICIAL_AGGREGATES.json: totales Yea/Nay/Present/Not Voting, partidos Republicano/Demócrata/Independiente, votación, tipo, fecha y correcciones. 2026 registra voto Independiente, incluirlo en total. No convertir "Not Voting" en ausencia física. Mantener separados votación, publicación original, capture UTC y primera publicación conocida; no inventar first_public_at.

## QA
Ejecutar en checkout limpio el archivo fuente research_only_house_groups.py y test_research_only_house_groups.py dentro de research/ABH_USHOUSE5_20261028. Blobs Git originales de los ejecutados localmente: source a8ff1dae5b4449a728d7e535bc86ab1947295eec, tests 04071e17eec565b9e03ade141266c98e327967cc. En ChatGPT hubo 15/15 PASS de tests locales sobre los mismos blobs, **NO** se ejecutó suite integral. Ejecutar toda suite Python/Node/Atlas, registrar comandos, versión, primer fallo y SHA logs.

## Protocolo científico posterior, no ejecución AB
La diferencia bruta 2025 vs 2026 de mayorías compartidas (1/6 vs 5/6) desaparece por tipo suspensión/otro (1/1 vs 5/5 y 0/5 vs 0/1). No supone causalidad. El comparador retrospectivo 1/6 vs 6/6 se hizo tras observar los resultados; NO es validación prospectiva. Una nueva evaluación legítima requiere fijar y congelar **antes del resultado** fecha límite, variables permitidas y muestra de futuras votaciones, baseline convencional, pérdida, tratamiento por sesión y comité ético de puntuaciones; autorización AB adicional, sin scoring de individuos.

Entregables T019_RESULTADO.md y T019_EVIDENCIA/MANIFEST.json con fuentes, hashes y resultados en rama de ejecución, PR borrador, sin fusionar. SUCCESS exige 12/12 originales y suite completa PASS, PARTIAL/BLOCKED según hechos. No subir XML identificable ni activar ChatRelay.
