# Política Fantasy España — Contrato de producto y datos v0.2

Fecha de corte: **31/10/2026**. Estado: SHOWCASE sintético con una pequeña instantánea real del INE. No autoriza investigación R5, integración a main, despliegue público ni puntuación de personas reales.

## Identidad y arquitectura

**Política Fantasy España** es el nombre gráfico provisional, no un cambio formal del repositorio Politics Fantasy League. Mantiene el logo geométrico. PFL se organiza conceptualmente en Observatorio (historia y fuentes), Laboratorio (análisis, incertidumbre, mecanismos, escenarios) y Fantasy (juego y decisiones); ninguno reemplaza a los demás.

El bucle es: **dossier → equipo → estrategia → acontecimiento → acta → progreso → nuevo dossier**. La demo implementa ocho eventos ficticios y guarda en cada jornada su identificador. Sus personajes, organizaciones, puntuaciones y situaciones no representan acontecimientos españoles reales.

## Benchmark competitivo

- [Fantasy Premier League](https://fantasy.premierleague.com/es/help): plantillas, fichajes, plazos, capitanía, rendimiento y clasificación. Adoptar claridad de jornada y expectativa.
- [Fantasy Congress](https://fantasycongress.com/): selección de congresistas reales y su actividad convertida en competición.
- [Politiparty](https://politiparty.com/scoring): rúbrica explícita para iniciativas, votaciones, enmiendas y otras actividades.
- [Fantasy Government](https://www.fantasygovernment.com/academy/how-to-play): liga por temporadas y utilidad cívica también para quien no juega.

**Diferencia propuesta:** una política española que incluya actores institucionales y extra-institucionales, candidaturas sin escaño, organizaciones, movimientos ciudadanos, cooperaciones, propuestas, ejecución y fiscalización. No asumir que todo evento es puntuable para cualquier persona o partido.

## Qué calcula la simulación

Ocho expedientes identificados demo-01 a demo-08 conservan semana, ámbito, tema, actor ficticio, fase, tipo, señal de especialidad, descripción y recepción sintética. La contribución de evento por carta usa cuatro partes: bonificación de especialidad, capacidad, recepción y fase procedimental. La recepción adversa reduce puntos del evento sin castigar por defecto el derecho a manifestarse; el evento de protesta es participación. Los resultados son reproducibles y aparecen en el acta. Esto es diseño lúdico, no evaluación de políticas reales ni inferencia causal.

Los 19 territorios (17 comunidades autónomas, Ceuta y Melilla) y cuatro indicadores de participación, cooperación, actividad y recepción se muestran como **series inventadas en escala abstracta 0–100**. No son datos de ninguna comunidad autónoma. Solo demuestran filtros, gráficos e interacción.

## Qué valores reales se presentan

Se incluyen únicamente pequeñas cifras públicas, fechadas y atribuidas a notas oficiales del INE; no microdatos ni originales descargados:

| Indicador | Valor | Periodo | Publicado | Fuente |
|---|---:|---|---|---|
| IPC anual adelantado | 4,9 % | Octubre 2026 | 30/10/2026 | [INE](https://ine.es/dyngs/Prensa/es/adIPC1026.htm) |
| Tasa de paro EPA | 10,18 % | 3T 2026 | 27/10/2026 | [INE](https://www.ine.es/dyngs/Prensa/es/EPA3T26.htm) |
| Ocupados EPA | 22.852.600 | 3T 2026 | 27/10/2026 | [INE](https://www.ine.es/dyngs/Prensa/es/EPA3T26.htm) |

El gráfico histórico muestra la variación **del segundo al tercer trimestre** de personas ocupadas (miles) para 2017–2026, según la misma nota EPA de 27/10/2026; no es crecimiento interanual. La serie conserva sus años, unidades, fecha y enlace. El IPC es un avance, pendiente de dato definitivo.

**La instantánea es manual, NO un canal automático ni en tiempo real.** No hay extracción de contenidos de los medios o APIs en esta demo. Los valores puntuales no equivalen a un dataset AB-R validado. Permisos y cobertura requieren estudio por activo antes de una ingesta estable.

## Contrato de datos futuros

Cada fuente candidata (INE, BOE, Congreso, Senado, CIS, Interior y otros organismos estatales, autonómicos y locales) requiere ficha de derecho de uso, activo y URL, entidad, territorio, identificadores institucionales, fecha de evento, fecha de primera publicidad, fecha de recuperación, versión, integridad/hash cuando proceda, unidad, universo, denominador y cobertura de casos negativos, pendientes, vetados y censurados. Las series no pueden confundirse con la fecha de descarga. El portal BOE advierte condiciones de reutilización; la disponibilidad pública no equivale automáticamente a licencia plena.

Para puntuación política real, separar **iniciativa, colaboración, tramitación, implementación, participación social y recepción**. Incluir actores no electos y normalizar oportunidades, volumen y desigual visibilidad institucional. Colaboración requiere un vínculo documentado entre actores y acción, no coincidencia de declaraciones. Una aprobación legal no prueba éxito social; una manifestación no es un resultado negativo intrínseco. La recepción requiere encuestas comparables, población, muestreo, incertidumbre y temporalidad, no contabilizar interacciones en redes como aprobación representativa. Cualquier atribución causal requiere diseño adecuado.

La futura infraestructura deberá almacenar hechos referenciados y mantener separados los modelos de puntuación calibrados, la visualización y la simulación de escenarios. Las normas de R5 STOP para investigación confirmatoria permanecen intactas.

## Diseño v0.2 y trabajos posteriores

Oscuro grafito por defecto, sin dominante verde; claro opcional. Paletas cobre, azul tinta, violeta y plata. Logo provisional conservado. Arte vectorial generado con Python: 18 retratos ficticios y ocho ilustraciones temáticas, sin fotos/logotipos oficiales ni recursos externos. Perfil con escudo de 1–4 símbolos, sin efecto en puntuaciones. La web sigue funcionando sin cuentas y de modo offline.

Pendiente de futuras autorizaciones, alcance y QA: verificar jurídicamente las 117 referencias; habilitar conectores oficiales con derechos por activo; construir historial territorial real interoperable; modelar políticas y actores como red temporal; verificar la recepción social; implementar ligas y perfiles sociales con autenticación; añadir noticias con licencias y versiones; validar accesibilidad, usuarios y navegadores. La demo v0.2 no certifica ninguna de esas capacidades.
