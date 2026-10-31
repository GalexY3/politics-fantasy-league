# Política Fantasy España · Edición de muestra v0.2 — verificación y relevo

**31 de octubre de 2026.** Tipo: frontend autónomo para enseñar el producto, no despliegue público ni validación científica.

## Alcance efectivamente construido

La carpeta product/showcase es una experiencia aislada del servidor científico, en checkout independiente. Ocho áreas: Inicio, Mercado, Mi equipo, Jornadas, Clasificación, Partidos españoles, Laboratorio y Mi perfil. El juego usa 18 cartas ficticias, 8 jornadas, 4 clubes rivales inventados, créditos, fichajes, ventas, hasta 8 cartas / 5 titulares, capitanía, tres tácticas, XP y 9 insignias, mercado con filtros, simulaciones contrafactuales y clasificación. La partida se guarda en localStorage, puede exportarse/importarse en JSON y se puede reiniciar. Acceso invitado sin contraseña, registro, red ni dependencias.

El catálogo exploratorio incluye **117 referencias españolas en 18 ámbitos territoriales**: 86 de tipo partido, 12 coaliciones electorales, 3 agrupaciones, 3 candidaturas y 13 referencias históricas. Los anclajes son **contextuales, no certificados por entrada**: 12 referencias Congreso 2023, 23 Europeas 2024 y 82 editoriales sin verificación individual. NO es Registro de Partidos Políticos, no demuestra identidad jurídica, vigencia, representatividad, inscripción ni exhaustividad. Los favoritos son cosméticos y nunca puntúan partidos reales.

## Diseño

La preferencia expresada por el usuario en el chat aportado: LessWrong e institucional/editorial, ambos temas cromáticos, dinamismo sin efectos recargados. CSS con papel cálido/carbón, serif para titulares, sans-serif de lectura, líneas finas, densidad informativa controlada y foco visible. Sin CDN, tipografías descargadas, Tailwind, React ni imágenes externas. Abrir con doble clic en index.html o ABRIR_DEMO.cmd.

## QA verificada

- JavaScript Node v24.16: comprobación sintáctica de app.js, engine.js, parties.js, PASS.
- **12/12 pruebas de motor PASS** mediante Node test. Cobertura de estado, mercado, presupuesto, límites, capitanía, táctica, ocho jornadas, ranking, favoritos y carga local.
- **8/8 vistas renderizadas en Chrome Headless** desde una URL de archivo, con JS ejecutado, DOM visible y sin stderr: Inicio, Mercado, Equipo, Jornadas, Liga, Partidos, Laboratorio y Perfil.
- **Prueba de interacción real Chrome/CDP PASS**: abrir inicio, ir al mercado, fichar c02 (saldo 94→60), ponerla de titular, designarla capitán, simular jornada, ver desglose, visitar catálogo, búsqueda y filtro de favoritos, activar oscuro, guardar perfil y comprobar persistencia al recargar.
- **Móvil emulado con CDP a 390 píxeles CSS:** window.innerWidth=390 y documentElement/body scrollWidth no superan 390; mercado responsive funciona. Se capturaron pantallas de escritorio y móvil **FUERA de Git**, en PFL-showcase-browser-qa-20261031.
- La inspección visual reveló un checkbox de favoritos sobredimensionado. Se corrigió su CSS y se repitió el ensayo CDP completo con los filtros PASS.

Límites: no hay auditoría integral de accesibilidad, todos los navegadores, teléfonos físicos, flujo completo de importación/exportación de archivos ni aceptación humana con visitantes. No hay backend o login; no equivalen a P1/P2 del producto científico ya aceptados.

## Continuidad y próximos pasos

La versión de origen fue SHOWCASE v0.1 en rama/PR de borrador, sin integración en main. La ampliación v0.2 conserva estas restricciones y requiere revisión presencial de usabilidad con una persona que desconozca PFL. Después, catálogo jurídicamente verificado y versionado por fuente oficial, y propuesta de integración con P1/P2 real cuando se acepten sus contratos. No copiar puntuaciones ficticias a políticos, no presentar eventos sintéticos como reales, ni levantar R5, derechos, investigación o Atlas a causa de esta demostración. No se modificó PFL-trabajo.

## Adenda v0.2 — revisión de producto del usuario (31/10/2026)

La reacción a v0.1 solicitó una atmósfera más visual, loop de fantasy que permita anticipar y entender resultados, laboratorio central con fuentes oficiales, economía, historia y geografías, puntuación más allá de los cargos con escaño, nombre español, tema oscuro más negro-gris que verde y heráldica propia. La respuesta implementada se concreta en:

- Marca visual provisional **Política Fantasy España**, logo geométrico original preservado.
- Tema oscuro grafito como predeterminado, claro alternativo y acentos cobre, azul, violeta y plata. Los guardados v0.1 que elijan tema claro lo conservarán hasta que el usuario cambie el tema.
- Arte íntegramente local: 18 retratos de cartas, ocho escenas de expedientes ficticios, hemiciclo original; SVG generado desde scripts/generate_showcase_art.py, sin fotos de personas reales ni imágenes de terceros.
- Ocho acontecimientos inventados y versionables por id, incluyendo protesta/participación, colaboración, aprobación o revisión, fiscalización y ejecución. Cada jornada preserva eventId y desglose de puntos por carta. El valor ficticio de «recepción» no representa una encuesta, popularidad ni una atribución causal.
- Perfil con paleta y heráldica de 1–4 símbolos, y Laboratorio con seis áreas: Panorama, Territorios, Economía real, Políticas y sociedad, Fuentes oficiales y Motor fantasy.
- La vista territorial presenta **19 nombres reales de territorios pero cifras completamente sintéticas**. Esta distinción es explícita.
- La vista de Economía real presenta **únicamente una instantánea manual del INE**: 4,9 % de IPC adelantado de octubre 2026 (30/10), 10,18 % de paro EPA 3T 2026 (27/10), 22.852.600 ocupados EPA 3T 2026 (27/10) y variaciones de ocupados del segundo al tercer trimestre de 2017–2026 extraídas de la tabla resumen de la misma nota. Se incluyen fecha, URL, periodo, unidad y advertencia de revisión. No es un feed en vivo.
- Un directorio de seis portales oficiales enlazados y etiquetados **sin ingestión**; requiere ficha de licencia, cobertura, identificadores, jurisdicción, casos negativos y fechas de publicidad antes de la integración.

**Validación nueva:** Node **16/16 PASS**; Chrome/CDP E2E completo **SHOWCASE_BROWSER_E2E_PASS**, incluyendo decodificación de retratos SVG locales, portada, fichajes, alineación y capitanía, acta con evento, seis secciones de laboratorio, tres cifras INE y gráfico EPA, filtros y favoritos, heráldica de cuatro símbolos, paleta persistente, exportación de estado no cubierta por diálogo nativo, 390 CSS px sin overflow en portada y laboratorio territorial. Capturas offGit bajo PFL-showcase-browser-qa-20261031/v02. La edición v0.2 no está validada por usuarios externos, y sus capacidades reales de datos son deliberadamente limitadas.

Contrato científico y límites detallados: docs/SHOWCASE_V02_PRODUCT_AND_DATA_CONTRACT_20261031.md. Este apartado sustituye las cifras v0.1 indicadas más arriba solo en lo relativo al showcase; no modifica hitos científicos, permisos, Atlas ni investigación de fondo.
