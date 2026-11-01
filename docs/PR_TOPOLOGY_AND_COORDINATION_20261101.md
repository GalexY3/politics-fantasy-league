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

## Ampliación 1/11/2026 · prueba de árbol Git aislado y contratos R5 (NONCYCLE)

El informe inicial analizaba rutas comunes y **no** probaba conflictos reales.
Esta fase aporta un instrumento complementario con un falsador diferencial:
la PR #11 y la #12 coinciden en `pan_iaen_original_frame.py`, pero hay que
distinguir una coincidencia de rutas de un **add/add conflictivo** comprobado.
Se incorporó `scripts/pr_virtual_merge_probe.py` con entrada EXCLUSIVA de dos
SHA de commit completos existentes localmente. Usa
`git merge-tree --write-tree --name-only`, y devuelve solamente nombre de
fichero conflictivo y clasificación `coordination` / `substantive`.
**Advertencia importante:** `--write-tree` escribe objetos de árbol en la
base de objetos del CLON AISLADO; no actualiza ramas, refs o worktree, pero
NO es una operación Git estrictamente sin escritura de objetos. Por eso exige
opción explícita `--allow-isolated-object-writes` y rechaza por nombre el
checkout protegido `PFL-trabajo`. Este comando nunca se ejecutó en ese
checkout. No devuelve contenidos o conflictos de texto, ni lee originales
fuera de Git.

El test de módulo nuevo se congeló antes de implementarlo: la colección
prepatch falló por `ModuleNotFoundError` para la nueva capacidad, lo cual
**no constituye** defecto previo de Git ni fallo científico. Después,
`tests/test_pr_virtual_merge_probe.py` y los ocho tests de la topología
inicial alcanzaron **12/12 PASS** en Windows, con mocks/fixtures de salida
de Git 100 % sintéticos. La ejecución posterior contra commits reales ya
presentes en el clon independiente constató:

| Pareja de commits | Conflictos Git de árbol | Ciencia/código sustantivo | Conclusión limitada |
| --- | --- | --- | --- |
| #11 `ff3da7c` ↔ #12 `3fabecc` | 6 paths; 4 coordinación + 2 sustantivos (`pan_iaen_original_frame.py` y su test). | Sí, colisión `add/add`. | Reconciliación de API necesaria; PR #21 es candidata, no merge automático. |
| #16 `f20f2a3` ↔ #18 `1a7e1b1` | 4 paths de coordinación. | 0 paths sustantivos conflictivos. | Resolver handoff, índice, mapa y autorización; no inferir semántica compatible. |
| #16 `f20f2a3` ↔ #19 `f284c2d` | 5 paths de coordinación. | 0 paths sustantivos conflictivos. | Idéntica distinción. |
| #18 `1a7e1b1` ↔ #19 `f284c2d` | 5 paths de coordinación. | 0 paths sustantivos conflictivos. | Idéntica distinción. |

Los cuatro testigos producen `tree_merge_has_conflicts=true`, nunca
`integration_approved=true`. Los pares con #19 fueron revalidados DESPUÉS de
su avance documental R27 a `f284c2de9128dc5a70710359de8d53f90f693a1d`:
persisten 5 conflictos exclusivamente de coordinación, con árboles virtuales
`4e5a51cc2cedb7ec18b865d96ac37b32297a7181` (#16×#19) y
`dfe37211b56374414686273e4e0e01dec3a997b6` (#18×#19). El resultado de
los pares #16/#18/#19 fue calculado sobre commits **concretos**; si cualquiera avanza debe
repetirse el probe, sin sustituirlo por un número histórico de PR.

### Revisión de contratos científicos: alcance del negativo

Auditoría estática independiente de `r5_asset_rights_gate.py` PR #16,
`synthetic_regime_capture_sensitivity.py` PR #18,
`evidence_warehouse.mjs` PR #19 y consumidores del servidor de PR #7:

- Los tres módulos modificados son diferentes y ninguno integra las salidas
  de los otros como autorización. El gate Python de derechos mantiene
  `reuse_admitted=false`, `independent_attestation=false` y `R5` cerrado;
  únicamente se localizaron consumidores en tests. **No** es un fallo
  material nuevo: el informe R23 advertía esa falta de integración.
- El comparador sintético de exposición C14A obliga a comparar ventanas,
  canales y capturas y mantiene ausentes first_public y N auténticos. Su
  corrección ya se produjo en R24 y no se repitieron pruebas sin delta.
- El almacén JS/CLI offline R25 ya bloquea derechos autodeclarados y
  as_of de originales; el `audit.ok` CLI acredita solo integridad interna.
  No hay endpoint POST de ingesta científica real en el servidor examinado.
- Los consumidores HTTP de denominador/registro siguen informando derechos,
  N independiente y first_public reales no acreditados. Un módulo ya
  disponible en otro checkout (`BR-P08`) trata unión sintética entre
  TemporalLedger y DocumentaryGraph; crear el mismo oráculo en este hito
  sería redundante. Se conserva STOP a un supuesto bypass transversal
  sin consumidor alcanzable.

La contribución nueva de este bloque es por tanto **verificación de conflictos
de Git trees y clasificación de las obligaciones de integración**, no
una atestación de que los motores científicos estén interoperando en un
pipeline empírico. Cuando se cree un consumidor real que combine #16/#18/#19,
deberá exigir vínculo explícito de `source_id`, SHA, finalidad, fecha legal,
`first_public_at`, jurisdicción, población y negatives/censura, con test
prepatch que demuestre su comportamiento propio. **R5 STOP, 0 AB, 0
originales/PII, 0 gates y ninguna fusión a main.**
