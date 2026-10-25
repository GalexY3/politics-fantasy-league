# Observatorio local v0.4 · guía de interpretación

Ejecutar `python run_demo.py`, abrir http://127.0.0.1:8787 (exclusivamente en el equipo local), seleccionar «Observatorio». `GET /api/lab` sirve un reporte inmutable derivado de once votos **inventados** de cuatro actores `SYN-P*`, tres oportunidades y dos grupos `SYN-G*`. Ningún campo describe diputados reales.

Los recuentos reales históricos siguen siendo **otro panel**: veinte totales agregados transcritos visualmente, no certificados nominalmente. La procedencia de cada panel y las limitaciones se muestran por separado. Nunca se asignan puntos fantasy usando `/api/lab`.

## Contratos semánticos esenciales

- `YES`, `NO`, `ABSTAIN` = tres elecciones expresadas. `NO_VOTE` requiere estar publicado explícitamente como tal, NO se deduce de la ausencia de registro.
- Ausencia de fila ante oportunidad documentada = `unknown`; tasa de participación = `null` hasta cerrar la cobertura del censo, nunca cero sin justificación.
- `group_at_vote` es la pertenencia en la fecha de votación, NO un grupo actual reasignado retrospectivamente.
- Revisiones se resuelven por la mayor versión **disponible en el corte temporal**. Se exigen ambos instantes `first_public_at` y `recorded_at`; uno no sustituye al otro.
- La mayoría de grupo se calcula por evento, abstenciones incluidas, no-voto excluido. Empates y «Mixto» se excluyen del denominador de discrepancia; discrepancia ≠ conflicto/independencia/ideología.
- Acuerdo entre dos actores se mide sobre oportunidades con voto expreso conjunto. Se muestra un comparador por frecuencias marginales; exceso descriptivo ≠ influencia o conexión social.
- Diversidad del voto = entropía de Shannon normalizada sobre respuestas expresas; no es un índice de calidad.
- Paradoja de Simpson es una señal de composición descriptiva, no prueba causal de confusión. Estandarización exige pesos comunes auditados.
- Pronóstico: MAE, logloss Poisson completo, baseline, calibración por bins, walk-forward purgado, bootstrap por sesión. Solo para corpus temporal suficientemente certificado.

## Escala de valor

`value_grade` usa VSDS 0–3 específico del proyecto y NO modifica el nivel de descubrimiento científico AB; en la demostración tiene valor `1`. Ver `docs/VSDS_PROYECTO.md`.

## Límites / seguridad

`server.py` solo escucha en 127.0.0.1. No hay cuentas, autenticación, cuotas ni autorización para exponer el proyecto a Internet. El source_url y SHA del fixture están explícitamente marcados sintéticos. Endpoint GET sin mutación. Pruebas Python no equivalen a QA visual en navegador ni garantizan inocuidad ante ataques reales.
