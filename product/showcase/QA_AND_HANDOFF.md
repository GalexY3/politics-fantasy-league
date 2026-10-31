# Politics Fantasy League · Edición de muestra — verificación y relevo

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

La versión es SHOWCASE v0.1 en rama/PR de borrador, sin integración en main. Primera acción: revisión presencial de usabilidad con una persona que desconozca PFL. Después, catálogo jurídicamente verificado y versionado por fuente oficial, y propuesta de integración con P1/P2 real cuando se acepten sus contratos. No copiar puntuaciones ficticias a políticos, no presentar eventos sintéticos como reales, ni levantar R5, derechos, investigación o Atlas a causa de esta demostración. No se modificó PFL-trabajo.
