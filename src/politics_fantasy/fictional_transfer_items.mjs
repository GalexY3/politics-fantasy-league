/** Fictional civic transfer questions (no political persons). Do not bundle evaluator for human study client. */
export function fictionalTransferItems(){
  const items=[
    {id:"X1",scenario:"En un parlamento inventado, una semana indica cobertura incompleta. El fichero no registra actuaciones.",question:"¿Qué se puede concluir de las actuaciones no registradas?",options:["A: Se sabe que no existieron","B: No puede establecerse si existieron","C: Fueron todas incorrectas"],construct:"missingness"},
    {id:"X2",scenario:"La semana siguiente tiene cobertura completa y registra 0 votaciones. El calendario ficticio no anunciaba ninguna votación.",question:"¿Qué afirmación describe correctamente ese recuento?",options:["A: Cero votaciones observadas con cobertura completa","B: Hay votaciones omitidas demostradas","C: Cada personaje merece 0 puntos por productividad"],construct:"zero_vs_quality"},
    {id:"X3",scenario:"Una comisión ficticia celebra 5 votaciones sobre 2 expedientes: 3 enmiendas de uno y 2 decisiones del otro.",question:"¿Qué mide el número 5?",options:["A: Cinco expedientes distintos","B: Cinco votaciones, sin equivaler a cinco expedientes","C: Cinco personas competentes"],construct:"event_unit"},
    {id:"X4",scenario:"Un juego inventado anuncia 20 oportunidades y un avatar participa en 4, acertando 3. La puntuación por éxito se divide entre oportunidades anunciadas.",question:"¿Cuál es la tasa sobre oportunidades anunciadas?",options:["A: 3/4 = 0,75","B: 3/20 = 0,15","C: 4/20 = 0,20"],construct:"denominator"}
  ];return Object.freeze(items.map(x=>Object.freeze({...x,options:Object.freeze(x.options)})))
}
