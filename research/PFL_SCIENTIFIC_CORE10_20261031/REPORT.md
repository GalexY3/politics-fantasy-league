# PFL · Primer bloque científico-computacional independiente (31/10/2026)

**Estado:** IMPLEMENTED_AND_FOCAL_QA_PASS / **REVIEW_REQUIRED**. No integrado en `main` ni en la rama protegida SYSTEM20. Sin despliegue, descarga de fuentes, PII, puntuaciones políticas reales ni CI remota.

## Procedencia y sesión

- Base: `GalexY3/politics-fantasy-league`, rama `research/pfl-system20-process-corpus-gates-20261031`, HEAD `8df788007553c05890be08b962ffc24349ee1a6a`, worktree limpio y 3.254 archivos rastreados con SHA verificable por el preflight.
- Trabajo: checkout independiente `/cos-prueba/PFL-POLICY-TRACE-20261031`, rama `research/pfl-policy-trace-scientific-core-20261031`. La copia original `/cos-prueba/PFL-trabajo` permanece protegida y sin modificaciones de esta sesión.
- Autoridad científica: `docs/VISION_CIENTIFICA_Y_ALCANCE_PFL.md`, `docs/SISTEMA_POLITICO_ESPAÑOL_DELIMITACION_V0_20261031.md` y `docs/PROGRAMA_COMPARATIVO_SISTEMA_POLITICO_ABH_20261031.md`; autoridad AB: `METHOD_REFERENCE.json` fijado en Metodologia-AB `69ed402d...`. No se ha efectuado en este bloque un nuevo contraste empírico AB.
- Se consultaron semánticamente los contratos de sesión y gobernanza, documentación sistémica, inventario de candidatos R18, código de grafo registral e instrumentos previos de selección documental, y tests relacionados; no se ha leído semánticamente todo el árbol, ni los ocho textos íntegros del método AB remoto ni archivos originales privados.

## Resultado 1: trazabilidad documental de una política

`src/politics_fantasy/synthetic_policy_trace.py` representa siete tipos de documento/acto heterogéneos: compromiso, iniciativa, decisión, norma, partida presupuestaria, actuación de implementación e indicador asociado. No aplica cierre transitivo por nombre o fecha; exige seis tipos de aristas referenciadas explícitamente, correspondencia exacta de IDs y SHA-256 alegados, y cronología de conocimiento de cada elemento con huso jurídico declarado. El reporte no incluye identificadores ni importes.

El experimento formal de uso es un fixture sintético: con seis enlaces explícitos conocidos existe una ruta documental completa; cuando el séptimo nodo y último enlace no estaban capturados a `as_of`, no aparece. Una referencia nunca se convierte en identidad, responsabilidad o efecto causal, y un enlace sin extremo conocido es `UNKNOWN`, no un hecho negativo. No se concede autenticidad, derechos ni población censal por simular esa ruta.

## Resultado 2: C20, comparación de rivales sintéticos

`src/politics_fantasy/synthetic_mechanism_discrimination.py` fija cinco reglas probabilísticas ilustrativas: B0 calendario, B1 condición institucional, B2 memoria interna, B2 entorno y B2 conjunto. Las covariables poseen testigos de tiempo anteriores a la predicción; la etiqueta binaria se evalúa únicamente tras cerrar su día jurídico y conocer la observación. La pérdida de Brier se computa como racional exacto, sin seleccionar hiperparámetros sobre los labels. Su contrato descriptivo tiene SHA `77ecbed6586b9beaec871fee02c7b4af195ed9edb76f0e934cdad283f499e209`.

En el fixture de cuatro casos, los vectores de pronóstico de memoria y entorno son distintos; una perturbación que iguala ambas señales elimina la distinción. Los Brier **puramente artificiales** son B0 `61/200`, B1 `111/400`, B2 interno `133/400`, B2 entorno `27/80` y B2 conjunto `157/400`. No son medidas del comportamiento político real, no estiman feedback ni establecen cuál mecanismo explica España. El instrumento comprueba **discriminabilidad de especificaciones**, no identificación causal ni validez predictiva externa. M3, la selección editorial, sigue dependiendo del gate de censo independiente R5.

## QA y registro de fallos

- Contrato de trazas + tests escritos antes de su primera ejecución: **16/16 PASS**. Se reforzó después la verificación de SHA de origen/destino declarativos, con test adversarial adicional.
- Contrato C20, código y tests congelados en SHA antes del primer test. **27 PASS, 4 FAIL iniciales**, explicados por la localización errónea de `pytest.raises`: el constructor de dataclass correctamente rechazaba la característica futura antes de llegar a la función de evaluación. No fue fallo de filtración. Se corrigió solo la posición del contexto del test, dejando el rechazo temprano y registrando el negativo.
- Batería integrada posterior: **83/83 PASS** Windows, con los nuevos tests y regresiones existentes de grafo registral, identidad R21 y calendario R22. Compilación Python de ambos módulos PASS. No se ejecutó la suite completa Linux, CI ni replay de originales.

### Recibo SHA-256 del código/contratos tras los cambios

| Archivo | SHA-256 |
| --- | --- |
| `src/politics_fantasy/synthetic_policy_trace.py` | `cbe5252f761d3a433c0ca641a79dd14b5f863202dc35f339572b92ace57663d1` |
| `tests/test_synthetic_policy_trace.py` | `2533bfb45866623072112d40290e81ec290b83fbb1c2a62b1f12a769cd0146b2` |
| `src/politics_fantasy/synthetic_mechanism_discrimination.py` | `50db9b15be758eb5e703b0318a35065ba0fc9fcb80c4963a9d96cfc0d562098b` |
| `tests/test_synthetic_mechanism_discrimination.py` | `b1e4ec8e889f38ab3e1c4db2d8364eccaaaab3162bf010ea909a85c761757cb7` |
| `docs/POLICY_TRACE_CONTRACT_V0_20261031.md` | `729957ee88ba1711b09e083db0887616352cd78776b542bdf4e98070539d0724` |
| `docs/C20_MECHANISM_RIVALS_SYNTHETIC_PROTOCOL_20261031.md` | `7720c5679fa5c9a0dfb605b9c15e6ef9b159f00a2c3aeca860107bc890f40ac8` |

Los hashes son de archivos locales del trabajo independiente. Para auditar el resultado publicado se exige comprobar después los mismos blobs y commit/árbol Git. Los SHA de fixtures son demostrativos, no autenticación de fuentes institucionales.

## Estado AB, decisiones y falsadores

La concesión nueva de hasta diez ciclos AB consta en `AUTHORIZATION_AND_SCOPE.json` de forma **separada** de ABH10, INTEGRATION10 y SYSTEM20. **Ejecutados 0/10; disponibles 10/10; R5 STOP.** Tampoco se ha incrementado la madurez, CT2, Atlas, los seis gates de lanzamiento ni el estado de los hitos. Ambos resultados son NONCYCLE. El candidato C20 solo progresa como instrumentación sintética; un contraste científico C20 sobre población española continúa condicionado.

Antes de promover este diseño a una infraestructura empírica, falsar: enlaces que usan documentos no disponibles en el momento; equivalencias retroactivas entre compromisos y actuaciones; falta de universo de iniciativas; publicación selectiva de desenlaces; indicadores económicos revisados o publicados después del corte; atribución de responsabilidad o efecto causal por compartir referencia; cambios en la semántica de partidas presupuestarias o competencias institucionales; cobertura documental dependiente del régimen. La existencia de un camino N:M **no** demuestra que una propuesta se haya cumplido, financiado o causado un resultado.

**Siguiente integración propuesta:** revisión independiente de las dos interfaces puras; preservar importaciones de `procedural_index_contract` y `synthetic_registration_graph`; si se aprueba, integrar en rama de producto/investigación mediante PR tras reconciliar HEAD remoto, actualizar `PROJECT_STATE` y ledger solo en el sitio canónico y valorar una API exclusivamente de fixtures antes de admitir fuentes reales. No modificar `main`, `server.py`, pipelines de datos reales ni las ramas de otros agentes por arrastre.
