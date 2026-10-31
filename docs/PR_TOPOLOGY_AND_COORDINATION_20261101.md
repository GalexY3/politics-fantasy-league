# PFL · Auditoría de topología de PR y riesgos de coordinación

**1 de noviembre de 2026. SOLO METADATOS GITHUB, NONCYCLE.** Este es un instrumento de lectura para planificar la integración, no un veredicto de merge, compatibilidad, acceso a originales, calidad científica ni aprobación de ninguna PR. Base del checkout independiente: rama de investigación PR #7, HEAD 8df788007553c05890be08b962ffc24349ee1a6a. No se ha editado el checkout protegido PFL-trabajo.

## Resultado vivo congelado fuera de Git

El comando read-only gh pr list sobre GalexY3/politics-fantasy-league devolvió **16 PR abiertas**, con nombre de rama de cabeza, base, commit de cabeza y rutas modificadas. Su snapshot bruto permanece solo en el scratch local PFL-global-pr-qa-20261101/open_prs_snapshot.json (SHA-256 **576b796d094e11d0e329895ab048d775206f2787cf84f711273b5664986a37a6**). Informe derivado offline pr_dependency_audit.json (SHA-256 **5c0791d87855ee2ec47d83b7fb9454e8a7344a3dfcd822e58cc43eaef60abc21**). No se han leído bytes de archivos de origen ni descargado datos privados; los nombres de rutas y SHA de commits provienen de GitHub.

La auditoría reconoce **12 aristas explícitas de dependencia** entre ramas de PR abiertas y **81 pares con alguna ruta cambiada compartida** que no son antecesor/descendiente directo. Solo tres de esos pares comparten rutas clasificadas como sustantivas: (PR #5, #6), (#5, #7) y (#11, #12). La mayoría de los 81 pares comparten exclusivamente HANDOFF, índices regenerados, tablas de estado o autorizaciones. Estos cruces **no demuestran conflictos de fusión**; ni se ejecutó merge-tree, ni merge, ni rebase, ni checks de compatibilidad semántica.

Dos comparaciones de coordinación:

- **PR #11 y #12:** bases distintas, sin relación ancestral entre los HEAD de PR abierta que conoce el snapshot, y ambas cambian src/politics_fantasy/pan_iaen_original_frame.py y tests/test_pan_iaen_original_frame.py. Requiere reconciliación semántica del parser PAN/IAEN antes de integrar ambas; no asumir que una incorpora a la otra por título o fecha.
- **PR #16 y #18:** hermanas basadas en PR #7. Comparten HANDOFF, PROJECT_INDEX, PROJECT_MAP, research/INDEX y AUTHORIZATION, pero no archivos clasificados como código científico sustantivo. Conviene regenerar índices al integrar, pero no afirmar que hay un conflicto funcional.

Existe una base de PR declarada que no corresponde a ninguna rama HEAD de las 16 PR abiertas: research/pfl-policy-trace-scientific-core-20261031. El instrumento la denomina **base externa o no resuelta**, sin afirmar que no exista remotamente. Puede ser rama conservada que no tiene PR abierta propia o referencia desactualizada; necesita comprobación con Git remota independiente.

## Contrato operativo del nuevo script

scripts/pr_topology_audit.py permite:

1. Leer un snapshot JSON explícito mediante --snapshot, compatible con UTF-8 y BOM generado por Windows PowerShell 5.1.
2. Consultar solo metadata de PR abiertas con --live y gh CLI, con límite 250 y timeout 30 segundos. No usa Git escritura, no acepta originales ni lee cuerpos de código.
3. Validar esquema cerrado, SHAs de 40 caracteres, rutas relativas saneadas, claves únicas y ausencia de ciclos de dependencia; reconstruir aristas, orden topológico y solapamientos por rutas, sin etiquetar ningún solapamiento como conflicto probado.

Los tests/test_pr_topology_audit.py tienen ocho casos sintéticos de ramas apiladas, hermanas, rutas compartidas solo de documentación, bases no conocidas, ciclos, duplicados, rutas inseguras y no promoción científica. **8/8 PASS**. El primer ensayo de lectura del snapshot falló por BOM de PowerShell 5.1 y fue corregido en el lector; el informe derivado final y su SHA corresponden a la ejecución posterior satisfactoria.

## Próximos pasos antes de integrar código

Revisar primero los cambios semánticos de #11/#12 y la base no resuelta, después construir plan de integración y repetir el reporte con HEADs frescos. Si la base de cualquier PR avanza, reejecutar el análisis y no reutilizar cifras históricas como estado vivo. Los cruces entre PR #16 y #18 son documentales; regenerar índices y resolver HANDOFF/AUTHORIZATION con control de derechos y A–J intactos. La realización de un merge-test futuro necesitaría comparar Git trees concretos y resolver cambios por responsables, pero este instrumento deliberadamente **no lo hace**.

**R5 STOP, 0 AB consumidos, 0 permisos nuevos, 0 originales, 0 CI costosa, 0 merge main, 0 despliegue.** No se asigna logro por resolver topología ni se afirma que las PR sean aptas para publicar o fusionar.
