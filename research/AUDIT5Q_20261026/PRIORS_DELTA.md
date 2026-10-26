# Priors delta AUDIT5Q

- **PF-Q01.** Un original oficial puede producir segmentaciones incompletas (52 secciones, 25 secuencias, 27 cuarentena). A favor: parser del documento original verificado. En contra: calidad desconocida de secciones descartadas. Falsador: doble lectura humana y extracción alternativa que confirme el total.
- **PF-Q02.** 25 secciones con numeración continua no equivalen a 25 sin objeciones: nueve contienen avisos de no proclamación. A favor: 9 issues fuente originales. En contra: significado exacto de cada aviso todavía no adjudicado. Falsador: relectura de esos nueve pasajes.
- **PF-Q03.** La privacidad debe validarse sobre estructura JSON completa, no solo claves raíz. A favor: contrapruebas de atributos anidados y prototipo, seis tests y reparación. En contra: filtros basados en claves no reemplazan revisión humana ni protección de operación pública. Falsador: nueva entrada sensible no reconocida o exfiltración.
- **PF-Q04.** Las pruebas de navegador necesitan diferenciar fallos de UI de defectos del oráculo de test. A favor: `text-transform: uppercase` cambió `inner_text` sin ausencia de información. En contra: un oráculo demasiado permisivo podría dejar escapar regresiones. Falsador: captura o DOM contradicen el contenido mostrado.
- **PF-Q05.** Cerrar un bloque de auditoría no añade progreso automáticamente. A favor: congelación V3 36.35% y seis gates, ausencia de fuente RPP original. En contra: próximas fuentes parciales podrían justificar un incremento en hito concreto `src.local`. Falsador: nueva evidencia material registrada y revisión versionada.

Priors PF-P/MG/H/I/J/K/M/N/P anteriores preservados. VSDS 1/3, CT2 multiactor 20/100, predictiva 24/100, nuevos N1/N2/N3 0.
