# Informe integral de estado Politics Fantasy League — AB-H R05 · 27/10/2026

**Objeto:** evaluar la situación real del producto, sus fuentes, investigación, documentación, ingeniería y riesgos después de la primera tanda A01–A20 y de los cuatro contrastes de revisión R01–R04. Esta evaluación no es un resultado AB-R confirmatorio ni un certificado de lanzamiento.

## 1. Situación en una frase

Politics Fantasy League es hoy **una demo sintética local con mecánicas funcionales y un observatorio electoral/documental parcialmente verificado**, respaldada por fuentes originales acotadas, pero sin incorporación longitudinal suficiente de figuras reales, sin control fiable de publicación `as_of` para la mayoría de familias documentales y sin autenticación para operación multiusuario. La **madurez contractual V4 = 36,90 %** solo mide el avance ponderado de 36 hitos definidos, **no** una probabilidad de éxito o de completitud de la política española.

**AB Atlas:** historial vigente antes de R05 basado en 11 lotes heredados + delta A01–A20 `0012` (fuente original `seed.json` inalterada). Comprobación estricta JS de 11 lotes heredados positiva; el **ejecutable Python oficial no ha sido ejecutado**. Evitar publicar el visor HTML como si fuera grafo vivo.

## 2. Nueve subvías V4, pesos y principales huecos

| Área | Peso | V4 | Evidencia efectiva | Falta imprescindible |
| --- | ---: | ---: | --- | --- |
| Fuentes y datos | 18 % | 45,0 % | BOE firmado 2023, JEC/Interior 52 provincias, catálogos oficiales, 11 originales conservados | Registro RPP individual, permisos por dataset, actualización y cobertura continua |
| Identidad e historial | 12 % | **42,5 %** | 11 continuidades longitudinales positivas (seleccionadas), BOCG con nombre y fechas, DOB oficial contradictoria preservada | Homónimo exacto negativo, registro de evidencia fiable, identidad multifuente reproducible |
| Eventos | 10 % | **35,0 %** | Alta/baja de condición plena, credenciales, DSCD juramento, comisión y declaraciones diferenciadas | Universo de eventos nombrados con `first_public_at` y exclusión de faltantes, pipelines |
| Investigación | 14 % | 27,5 % | Protocolo TFM, criterios VSDS, código/simulaciones | Cohorte persona-semana y baselines equiparables, splits nunca reutilizados |
| Motor fantasy | 16 % | 45,0 % | Clubes, mercado, alineaciones y reglas ficticias en demo local | Puntuación real justificable, cobertura y no confundir puntos con mérito |
| Interfaz | 10 % | 32,5 % | Pantallas de mercado, atlas, barras progreso y smoke Chromium previo | Diseño accesible formal, pruebas de usuarios y confianza de datos actuales |
| Seguridad, privacidad, licencias | 8 % | 20,0 % | Bind loopback, filtros Host/Origin, avisos de fuentes y términos oficiales | Autenticación, CSRF, derechos por uso, evaluación de datos personales/daños |
| QA/reproducibilidad | 8 % | 45,0 % | CI antigua local y Chrome smoke; suite progresos V3, controles fuentes | Nuevos tests nativos A02/A19/R02 aún sin ejecutar, Atlas Python oficial, E2E original a vista |
| Operación/piloto/despliegue | 4 % | 17,5 % | Guías de demo | Infraestructura autenticada, backups/monitorización, piloto cerrado de usuarios |

**Revisión del porcentaje:** V3 36,350 → V4 **36,900 (+0,550 pp, scope_effect=0)**, con únicamente `id.real` y `ev.person` pasando nivel **0 a 1 (especificado)**. Las otras 34 fichas, nueve pesos y seis gates permanecen iguales. [Detalle de todos los hitos](R01_MILESTONES.json) y [explicación V4](../../docs/PROGRESO_Y_ALCANCE_v4.md). El endpoint local de progreso ha sido apuntado a V4, pero las pruebas nuevas de API/HTTP/Node **aún no corrieron** sobre un checkout completo.

## 3. Lo demostrado con originales, separado de inferencias

- **Integridad:** 11 archivos recuperados (XLSX Interior, XML Senado, JSON Congreso, PDF BOE) superaron SHA/longitud respecto del manifiesto del ZIP. Eso acredita transferencia, no sello original de publicación ni derechos.
- **Consistencia de fuentes:** BOE-JEC 2023 vs Interior: 52 provincias, 350 electos, 346 coincidencias nominales estrictas y cuatro discrepancias textuales revisadas contextualmente. El acuerdo puede compartir actas de origen y no constituye doble fuente de identidad.
- **Problemas de identidad:** 1.306 cadenas de nombre se repiten en elecciones distintas; solo 11 continuidades positivas históricas seleccionadas cuentan con biografías oficiales que relacionan legislaturas. Sin muestra adjudicada de dos personas distintas con nombre completo idéntico; ninguna tasa de falso enlace estimable. Un mismo cargo público tiene DOB contradictoria en Gobierno y Congreso/PSOE; no elegir fecha por mayoría.
- **Eventos temporales:** en BOCG 2023 se recogen ocho ceses y ocho altas con fecha efectiva distinta de la de edición; en BOCG 2025 tres credenciales preceden la plena condición por **39, 7 y 0 días**. En DSCD 2026 y ficha personal coincide otro acto de adquisición plena, distinto de altas de comisión o fechas de declaración. Nada de esto valida automáticamente `first_public_at` exacto.
- **Contras verificables:** un `asiento=-1` repetido no es ID; 2026 bajas parlamentarias posteriores al voto muestran sesgo de usar roster actual; en el BOCG 2025 unir por **posición de fila** produce **2 enlaces erróneos de 3**, aunque coinciden el conjunto de nombres; el PDF firmado del BOE 2023 puede ofrecer una cota editorial condicional día+1, pero no se puede trasladar a editor BOCG.

## 4. Estado de ingeniería verificable

**En esta nueva rama**, `GET /api/source-stages` fue integrado correctamente con verificación por lectura posterior y protección Host anterior a la ruta. El catálogo interno contiene tres documentos en cuarentena, ninguna publicación exacta acreditada y `real_person_scoring=false`. Se escribieron **cuatro tests HTTP**, todavía **no ejecutados** en una CI/servidor de checkout completo.

Hay prototipos puros de validación de fechas, afiliaciones documentales y conflictos de atributos (algunos ensayados en staging espejo); la unión por nombre se limita estrictamente a un único boletín y rechaza duplicados y ausencia. No hay ingesta de identidades reales certificada ni actividad política puntuable. Los códigos nuevos de procedimientos son una API de prueba, no un sistema real. GitHub Actions no se ejecutó deliberadamente para evitar gasto sin integración revisada; está configurado para main/PR.

El editor RPP del Interior cuenta con **consulta pública**, pero no se obtuvo una entrada jurídica individual original. Los XLSX estadísticos 2020/21 no son registro legal de entidades; la descarga 2021 devolvió **502**. La página de avisos del Congreso y la licencia BOE contienen condiciones de atribución y protección de datos; no está hecha la auditoría integral para puntuar representantes.

## 5. Calidad científica y riesgos

[Auditoría científica R03](R03_DISENO_VALIDACION.md): se mantienen **CT2 identidad 29/100**, **VSDS 1/3**, **N1/N2/N3 0/0/0**. La cantidad de tests, coincidencias y AB cycles no sustituye una tarea predictiva con evaluación fuera de muestra, denominadores de oportunidad, fuentes as-of, baseline rol×agenda y cohortes selladas. La aplicación no debe presentar puntos fantasy como medida de valor democrático ni sesgo causal.

[Auditoría de lanzamiento R04](R04_AUDITORIA_READINESS.md): **0/6 gates** acreditados. Faltan autenticación, corpus jurídico de actores y eventos, identificación robusta, prueba E2E completa y hosting seguro. No publicar el servidor de demo tras reverse proxy.

## 6. Próxima tanda B01–B20: orden adaptativo, no calendario de veinte condiciones prefijadas

**Primera decisión:** B01 intentará por fin una **validación nativa y reproducible de los módulos Python/JS nuevos con controles de blob SHA**, sin invocar un CI costoso sin necesidad. A partir del resultado se decidirá B02. Si no es posible ejecutar código fiel al repositorio, se registrará explícitamente y se dará prioridad a corrección/seguridad de lógica verificable estáticamente.

Rutas con ganancia plausible, sujetas a sus propios nuevos prerregistros:
- Cerrar **source-of-truth** del Atlas con Python real y prueba de hash, y hacer que cada ref de investigación se reproduzca en una rama limpia antes del PR.
- Integrar **fuentes de condición plena** con una capa de recibos controlados por el servidor y un pipeline de QA que nunca use firma/acto/edición como momento exacto de publicidad.
- Capturar **inscripción legal RPP** con la consulta oficial realmente utilizable, en lugar de rellenar nombres de listas electorales como partidos.
- Adjudicar **casos negativos de homonimia**, además de los once positivos; no evaluar precisión antes.
- Proteger derechos, política de minimización y scoring sintético; construir un prototipo usuario E2E sin recoger datos personales innecesarios.
- Diseñar **cohorte persona-semana y baseline temporal fuerte** antes del primer test científico confirmatorio.

**Criterio R5:** detener una línea que solo repite un mismo documento, un mismo conjunto de nombres o fixtures; mantener la cuota restante y no fabricar un resultado para alcanzar 20. Las próximas decisiones se basarán en resultado de B01, no en una agenda de veinte tests preseleccionados.

## 7. Contabilidad de permisos

El usuario autorizó **20 ciclos iniciales (A01–A20), cinco ciclos de evaluación (R01–R05), y hasta 20 adicionales (B01–B20)**. Al terminar este informe se consumen **20 + 5 + 0**, con **20 B aún autorizados**, sin necesidad de nueva solicitud entre ciclos. La suma de permisos no altera la cantidad de conocimiento validado.

**Fuentes de verdad:** archivos versionados de producto V4, AB Atlas semántico incremental, ledger [campaña ABH45](CAMPAIGN_AUTHORIZATION.json), catálogo de fuentes institucionales, pruebas y resultados de cada ciclo. No sobrescribir historia V3/previa.
