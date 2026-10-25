# VSDS · Escala de valor sociológico y de ciencia de datos — SOLO Politics Fantasy League

Decisión del investigador (2026-10-25): reemplazar **para este proyecto** la etiqueta de nivel visible 0/3–3/3, antes centrada en novedad científica, por una medida ordinal de **valor sociológico + valor computacional verificable**. Conservamos los niveles de descubrimiento AB 3.2.1 **en otro campo de metadata**, sin reescribir sus definiciones ni vender una utilidad como hallazgo original. VSDS **no es una probabilidad ni un promedio de calidad**.

| Nivel | Ancla | Evidencia mínima para otorgarlo | No basta |
|---|---|---|---|
| VSDS-0/3 | Sin utilidad reproducible | Fallo, diseño sin ensayo, o resultado inválido | Ejecutar código sin auditabilidad |
| VSDS-1/3 | Instrumento verificable | Código/diccionario/indicador con contratos, tests adversariales y procedencia de entradas; utilidad técnica local | Datos sintéticos o docencia aislada no prueban realidad política |
| VSDS-2/3 | Valor sociológico/data science demostrado en un corpus | Corpus de campo con identidad/denominadores/procedencia certificados, comparador competente, estimando sustantivo, casos negativos y evaluación temporal; informe explotable por sociólogos | Scores vistosos, correlaciones sin controls, conveniencia local |
| VSDS-3/3 | Utilidad social o analítica transferible y validada | Reproducción o auditoría independiente sobre fuentes nuevas, robustez por agenda/grupo/periodo, daño/fairness documentado, uso práctico demostrado por tercero o evidencia de aportación para políticas/conocimiento | Aparente novedad, una sola muestra adaptada o mera publicación del código |

**Situación 2026-10-25:** VSDS-1/3 del instrumento de observatorio. La prueba local contiene filas SIN POLÍTICOS REALES. Nivel de descubrimiento científico AB = 0; CT2 predicción parlamentaria = 24/100, ordinal y sin cambio. No conceder VSDS-2/3 sin fuente institucional auditada y aplicación sustantiva. VSDS-3/3 no exige originalidad científica per se; sí utilidad práctica/analítica replicada.

## Dimensiones no agregables

- **Ciencia sociológica:** estimando con dimensión relacional, longitudinal o institucional; explicación teóricamente inteligible; denominadores, contextualización y comparadores.
- **Ingeniería de datos:** fidelidad temporal, procedencia, esquema, pruebas, robustez a formatos, coste, reproducibilidad.
- **Producto:** validez semántica, seguridad, accesibilidad, juego con límites transparentes, evitar incentivos perversos (Goodhart).
- **Ética:** privacidad, reputación, no atribución causal indebida, derechos, inclusión, no confundir rendimiento y valor de personas.

Todas estas dimensiones se documentan separadamente; VSDS no sustituye la auditoría I del ciclo AB ni CT2. Ninguna interfaz debe mostrar VSDS como ranking de personas.

## Falsadores específicos

Un CSV que omite miembros convierte inasistencias en ceros espurios; la pertenencia a grupo tomada al final de legislatura contamina votaciones anteriores; múltiples votaciones de una sesión comparten factores y no son independientes; comparar proporciones de distintos temas sin estandarizar puede invertir resultados; co-votar no significa influirse; tendencia de observación no es calidad democrática.

## Fuente de antecedentes y límites

- https://www.congreso.es/es/opendata/votaciones (original institucional).
- https://congresoabierto.org/metodologia/ (terceros, afiliación en fecha, no voto y límites de nominales; no es validación de este proyecto).

El material de este proyecto no se licencia automáticamente por esa fuente. La licencia del código propio está pendiente de decisión explícita.
