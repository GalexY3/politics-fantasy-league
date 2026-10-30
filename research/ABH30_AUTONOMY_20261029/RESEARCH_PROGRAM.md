# PFL AB-H 30 · programa BRANCHING con dos fases · 2026-10-29

## Estado real

Usuario autoriza **20 ciclos libres de desarrollo/investigación** y **10 posteriores de autonomía técnica**, ampliando scope de solicitudes de 5 a 30. **No se ha ejecutado ningún A–J en esta campaña al crear este archivo.** Las dos plazas anteriores siguen intactas. Rama creada desde PR39 HEAD `b514df48cfae88b0c9d802fa2e0f50746994c6db`. T028 permanece pendiente de ejecutor.

## Fase I: 20 plazas de investigación, no obligación de gasto

La pregunta rectora es si PFL aporta una experiencia y mecanismo medible que no se explique por juegos de pronóstico existentes, por sesgos de selección, diferencias de dificultad o simulaciones ad hoc.

Ejes candidatos, **sin preasignar ciclos válidos**: (a) identidad de producto y uso recreativo sin afirmaciones científicas; (b) equidad de scoring con oportunidades observables, contra difficulty-adjusted Brier de ForecastBench; (c) incentivos, gamificación y participación, con prior art y controles; (d) calidad de información, calibración y aprendizaje; (e) mecanismos de confianza y normas; (f) diseño de métricas sin datos personales; (g) robustez a eventos correlacionados; (h) seguridad, accesibilidad y anti-manipulación; (i) viabilidad operativa y ética; (j) pruebas científicas independientes legalmente reutilizables.

**Puerta A–J:** hipótesis y contraste falsable; prior/competidor; prereg antes de calcular; dataset/licencia/versiones/hashes; ejecución y control negativo; auditoría adversarial; resultado negativo registrado; actualización de fuentes/priors/CT2/Atlas solo con evidencia. Ninguna iteración de documentación, búsqueda sin contraste o planificación consume ciclo válido. R5 puede detener el trabajo antes de 20.

## Fase II: 10 plazas sobre independencia de Codex

Investigar **y, cuando sea posible, probar realmente** rutas para:
1. Recuperar archivos GitHub mediante conector sin checkout y verificar hashes Git SHA.
2. Materializar un checkout autorizado desde fuentes conectoras, manteniendo privacidad del repositorio y controles de integridad.
3. Ejecutar Python `ab_atlas/atlas_delta.py check` y `brief` de forma local si los bytes completos están disponibles.
4. Ejecutar Node y suites locales con fuentes íntegramente reconstruidas.
5. Usar Playwright/Chromium con servidor HTTP local en un entorno que permita loopback; si la política bloquea, declarar `BLOCKED_BY_ENVIRONMENT`.
6. Conservar evidencias y pruebas reproducibles en GitHub.
7. Comparar autonomía real vs Codex en esfuerzo, permisos, fidelidad y coste.
8. Verificar qué capacidades dependen inevitablemente de credenciales o aprobación humana.
9. Auditar seguridad de automatización, minimización y ausencia de secretos.
10. Integrar solo mecanismos que funcionen en tests nativos, sin prometer capacidades inexistentes.

No se asume que todos los ítems serán ciclos. Un ciclo debe contener ejecución real A–J y controles, no solo un catálogo de alternativas.

## Gobierno

Presupuestos independientes: antiguo `2 valid / 1 incomplete / 2 unused`; nuevo `phase I 0/20`, `phase II 0/10`. Sin personas, datos privados, scoring de políticos reales, ChatRelay, main merge ni CI costosa. Las PR sucesoras serán draft y apiladas. Los resultados no se fusionan ni elevan CT2 sin evidencia. El alcance de PRs hasta 30 es un techo, no una instrucción de generar 30 PRs artificialmente.
