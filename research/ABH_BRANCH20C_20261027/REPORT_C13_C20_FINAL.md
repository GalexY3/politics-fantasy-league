# Politics Fantasy · cierre BRANCHING20C · investigación externa C13–C20

**27/10/2026 · Rama:** `research/pfl-sources-reconcile-20261027`.

**Autorización:** 20 ciclos BRANCHING concedidos por el usuario en un bloque nuevo, distintos del bloque anterior reconciliado conservadoramente. Se realizaron **C01–C20, 20/20 consumidos, 0 disponibles**. C01–C04 incluyen una parada R5 y no deben contarse como veinte experimentos científicos independientes. Para cualquier **nuevo ciclo AB** hará falta otra autorización expresa; no prometer trabajo en segundo plano. [Cierre legible por máquinas](CAMPAIGN_FINAL_C01_C20.json).

La investigación externa C13–C18, sus fuentes originales, muestras de carreras, biografía DOB contradictoria y pruebas de código se describen exhaustivamente en [informe C13–C18](REPORT_C13_C18.md). Los ciclos C19–C20 completan este bloque **sin reutilizar los mismos testimonios**: el Congreso facilita otra fuente directa de la vigencia histórica individual de diputados y diputadas, antes inaccesible con simples listados en activo y de baja.

## C19 · BOCG XV-D-51, 15/12/2023: datos personales de *condición plena*

[Prerregistro C19](C19_PREREG.json) · [resultado C19](C19_RESULT.json). Fuente oficial: [BOCG XV-D-51, 15 de diciembre de 2023, composición del Pleno, exp. 051/000002, apartados A–C](https://www.congreso.es/es/busqueda-de-publicaciones?_publicaciones_id_texto=%28BOCG-15-D-51.CODI.%29&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal).

El Congreso comunica:
- **8 bajas** de diputados que habían adquirido condición plena, con fecha efectiva **06/12/2023**.
- **8 altas** con condición plena adquirida el **12/12/2023**.
- **8 presentaciones de credencial** en el registro, números **358–365**, con fecha **12/12/2023**.
- El documento se ordena firmar el **12/12/2023** y pertenece al ejemplar del **15/12/2023**.

Las tres fechas/granos **no son equivalentes**. La fuente acredita la clase de evento y día efectivo para los nombres listados, pero **no** dice que una de las ocho altas sustituya necesariamente a una baja determinada; 8/8 es igualdad de *recuentos*, no una relación causal o 1:1. El boletín del 15 tampoco demuestra por sí solo cuándo se conoció públicamente cada baja o alta. Ningún `first_public_at` original independiente fue recuperado para BOCG.

**Limitación técnica:** fuente primaria recuperada en texto HTML indexado por buscador, pero reabrir URL directa devolvió `Cache miss`. Se conservan ruta y datos documentales, **no bytes firmados ni SHA-256 del boletín PDF**; nivel de certificación inferior al de los dos PDF firmados del BOE de 2023.

## C20 · BOCG XV-D-390, 12/09/2025: credencial ≠ condición plena

[Prerregistro C20](C20_PREREG.json) · [resultado C20](C20_RESULT.json). Fuente oficial: [BOCG XV-D-390, 12 de septiembre de 2025, composición del Pleno, exp. 051/000002, apartados A–C](https://www.congreso.es/en/busqueda-de-publicaciones?_publicaciones_id_texto=BOCG-15-D-390.CODI.&_publicaciones_legislatura=XV&_publicaciones_mode=mostrarTextoIntegro&p_p_id=publicaciones&p_p_lifecycle=0&p_p_mode=view&p_p_state=normal).

La Cámara consigna **una baja de condición plena (02/09/2025)** y **tres altas (09/09/2025)**. Los tres nuevos miembros tienen credenciales oficiales **403–405**, pero **presentaron sus credenciales el 01/08, 02/09 y 09/09**, respectivamente. Diferencias hasta adquirir condición plena:

| Miembro | Credencial presentada | Condición plena | Diferencia |
|---|---|---|---:|
| Pablo Antuñano Colina | 01/08/2025 | 09/09/2025 | 39 días |
| María Elvira Rodríguez Herrer | 02/09/2025 | 09/09/2025 | 7 días |
| Irene Jódar Pérez | 09/09/2025 | 09/09/2025 | 0 días |

Los **tres valores 39/7/0** demuestran que una fecha de entrega de credencial no puede ser por definición la fecha de adquisición plena. La baja de la misma edición no puede tratarse como único predecesor individual de las tres altas. El texto se firma el **09/09/2025**, se publica en un ejemplar fechado **12/09/2025** y carece aquí de recibo de primera publicación independiente. La prueba reproduce, en otro año y otra muestra, el resultado de C19: existen fuentes originales con datos efectivos que los inventarios de electos actuales no contienen.

**Límite editorial:** la declaración de puntualidad **312/312 de BOE ordinario 2023** no se extrapola al **BOCG 2023/2025**, que tiene editor y periodicidad distintos. No se asigna disponibilidad certificada desde la fecha del acto o de la credencial.

## Resultado integrado AB-H y próximos requisitos

1. **AB-R, fuente de identidad:** los **once casos positivos** de continuidad entre 20 y 41 años se mantienen contrastados con biografías institucionales, y queda el problema del **control negativo de homónimo de nombre completo**. La discrepancia DOB de Cristina Narbona (Moncloa 21/07/1951, Congreso/PSOE 29/07/1951) demuestra que DOB no puede ser condición necesaria rígida de identidad.
2. **AB-R, temporalidad:** hay al menos dos **BOCG oficiales originales** que enumeran días de alta/baja efectiva y de presentación de credenciales. Separa `event_day`, `credential_submitted_day`, `full_condition_acquired_day`, `full_condition_ceased_day`, `bulletin_issue_day`, `first_public_at`. Para BOE ordinario 2023 hay evidencia de disponibilidad condicional día+1, que no transfiere automáticamente a BOCG.
3. **AB-P, software:** [`boe_2023_publication_bound.py`](../../src/politics_fantasy/boe_2023_publication_bound.py) (10 tests locales) e [`identity_field_conflicts.py`](../../src/politics_fantasy/identity_field_conflicts.py) (11 tests locales) representan condiciones **documentales**, no validación de personas ni gates de público. Sigue pendiente conectar `trusted_registry` al servidor de modo no falsificable y realizar pruebas HTTP.
4. **Atlas y catálogo:** [catálogo central](../../docs/CATALOGO_FUENTES.md) y [CURRENT](../../ab_atlas/CURRENT.md) deben identificar el último lote incremental [`0011`](../../ab_atlas/updates/0011-pfl-b20c-bocg-final-20261027.json) si su replay termina validado. No modificar seed, ni usar pruebas locales como pruebas de novedad N1–N3, ni promover CT2/VSDS o gate sin aceptación.

**Indicadores heredados sin cambios:** PFL-V1 rev.3 **36,35 %** (índice contractual), CT2 identidad **29/100**, VSDS **1/3**, N1/N2/N3 científicos nuevos **0/0/0**, gates críticos aprobados **0/6**. Sin puntuación de personas reales, sin despliegue público, sin ejecución GitHub Actions solicitada.

**Decisión:** la campaña queda cerrada por **techo autorizado 20/20**, no por haber demostrado imposible toda investigación posterior. La vía emergente más útil es una extracción sistemática y verificada de composición histórica `051/000002` del BOCG con gestión de fecha del evento vs disponibilidad del boletín; paralelamente, revisión independiente de un homónimo exacto negativo y recibos de archivo firmados. Esto requerirá nuevo permiso AB si el usuario solicita otra campaña.
