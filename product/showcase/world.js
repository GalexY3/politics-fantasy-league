/* Explicitly synthetic world and a separately labelled directory of official sources.
   None of the fictional observations are estimates about Spanish institutions. */
(function(root,factory){
  const world=factory();
  if(typeof module==='object'&&module.exports)module.exports=world;
  root.PFLDemoWorld=world;
})(typeof window!=='undefined'?window:globalThis,function(){
  'use strict';
  const EVENTS=Object.freeze([
    {id:'demo-01',week:1,title:'La mesa vecinal abre el debate sobre movilidad',sector:'Movilidad',type:'Participación',stage:'Consulta',territory:'Castilla y León',actor:'Red Vecinal Horizonte',signal:'alianzas',role:'Acuerdos',reception:71,detail:'Una organización ficticia presenta propuestas, obtiene apoyos y consigue una audiencia pública.'},
    {id:'demo-02',week:2,title:'Una comisión revisa el plan de vivienda compartida',sector:'Vivienda',type:'Tramitación',stage:'Comisión',territory:'Comunidad de Madrid',actor:'Asamblea Cívica del Centro',signal:'datos',role:'Información',reception:42,detail:'La iniciativa avanza formalmente, pero la consulta simulada refleja críticas por los criterios de acceso.'},
    {id:'demo-03',week:3,title:'Acuerdo transversal para bibliotecas de proximidad',sector:'Cultura',type:'Cooperación',stage:'Acuerdo',territory:'Andalucía',actor:'Plataforma de Barrios Abiertos',signal:'alianzas',role:'Acuerdos',reception:77,detail:'Gobierno local, colectivos y asociaciones ficticios acuerdan un proyecto compartido.'},
    {id:'demo-04',week:4,title:'La protesta cambia el calendario de una reforma',sector:'Vivienda',type:'Movilización',stage:'Revisión',territory:'Cataluña',actor:'Coordinadora del Tejido Urbano',signal:'debate',role:'Debate',reception:29,detail:'Una movilización ficticia visibiliza costes sociales. La protesta es participación, no un fracaso por sí misma.'},
    {id:'demo-05',week:5,title:'Observatorio ciudadano detecta una brecha territorial',sector:'Salud',type:'Investigación',stage:'Diagnóstico',territory:'Galicia',actor:'Instituto Cívico del Atlántico',signal:'datos',role:'Información',reception:64,detail:'Un informe ficticio impulsa preguntas públicas y alternativas de seguimiento.'},
    {id:'demo-06',week:6,title:'Pacto comarcal de transporte entra en ejecución',sector:'Movilidad',type:'Implementación',stage:'Despliegue',territory:'Aragón',actor:'Alianza de Municipios del Valle',signal:'alianzas',role:'Acuerdos',reception:68,detail:'Se ejecuta una medida ficticia; la aprobación formal no se confunde con implementación efectiva.'},
    {id:'demo-07',week:7,title:'Auditoría pública examina los resultados del programa',sector:'Economía',type:'Fiscalización',stage:'Evaluación',territory:'Comunitat Valenciana',actor:'Foro de Cuentas Claras',signal:'datos',role:'Información',reception:38,detail:'La fiscalización identifica incumplimientos parciales y abre un proceso de corrección.'},
    {id:'demo-08',week:8,title:'Acuerdo final con participación de asociaciones',sector:'Medio ambiente',type:'Cooperación',stage:'Resolución',territory:'País Vasco',actor:'Mesa Cívica del Estuario',signal:'debate',role:'Debate',reception:74,detail:'Una propuesta ficticia llega a resolución con participación institucional y social.'}
  ].map(Object.freeze));
  const REGIONS=Object.freeze(['Andalucía','Aragón','Asturias','Illes Balears','Canarias',
    'Cantabria','Castilla-La Mancha','Castilla y León','Cataluña','Comunitat Valenciana',
    'Extremadura','Galicia','Comunidad de Madrid','Región de Murcia','Navarra',
    'País Vasco','La Rioja','Ceuta','Melilla']);
  const INDICATORS=Object.freeze([
    {id:'participacion',name:'Participación social',definition:'Intensidad sintética de acciones ciudadanas en el escenario.'},
    {id:'actividad',name:'Actividad institucional',definition:'Frecuencia sintética de hitos institucionales.'},
    {id:'cooperacion',name:'Cooperación entre actores',definition:'Señales sintéticas de colaboración multisectorial.'},
    {id:'recepcion',name:'Recepción de medidas',definition:'Aceptación sintética; NO es un sondeo ni porcentaje observado.'}
  ]);
  const SOURCES=Object.freeze([
    {name:'INE · INEbase',topic:'Economía, población, precios y territorio',url:'https://www.ine.es/dyngs/DAB/index.htm?cid=1099',status:'API documentada · sin ingestión en esta demo'},
    {name:'BOE · Datos abiertos',topic:'Normas, sumarios, versiones y cronología jurídica',url:'https://www.boe.es/datosabiertos/api/api.php',status:'Condiciones de reutilización pendientes de evaluación por activo'},
    {name:'Congreso · Actividad parlamentaria',topic:'Iniciativas, expedientes, votaciones y agenda',url:'https://www.congreso.es/es/cem/faqs',status:'Referencias oficiales · no se extraen resultados'},
    {name:'Senado · Catálogo abierto',topic:'Iniciativas, enmiendas, votaciones y comisiones',url:'https://www.senado.es/web/relacionesciudadanos/datosabiertos/catalogodatos/index.html?lang=es_ES',status:'Catálogo documentado · sin ingestión'},
    {name:'CIS · Catálogo de estudios',topic:'Opinión pública y diseño muestral',url:'https://www.cis.es/catalogo-estudios/resultados-definidos/barometros',status:'Datos no incorporados; requiere auditoría de universo y tiempos'},
    {name:'Ministerio del Interior',topic:'Partidos y registro jurídico',url:'https://sede.interior.gob.es/portal/sede/tramites',status:'Identidades y vigencias pendientes de comprobación'}
  ].map(Object.freeze));
  // Source-backed, manually transcribed small public aggregates from INE press
  // releases. Frozen historical snapshot, NOT live feed or research dataset.
  const REAL_SNAPSHOT=Object.freeze({
    asOf:'2026-10-31',refresh:'manual',jurisdiction:'España',
    metrics:Object.freeze([
      Object.freeze({id:'ipc',name:'IPC anual · avance',value:'4,9 %',period:'octubre 2026',
        published:'2026-10-30',quality:'Indicador adelantado; pendiente de dato definitivo',
        source:'https://ine.es/dyngs/Prensa/es/adIPC1026.htm'}),
      Object.freeze({id:'paro',name:'Tasa de paro · EPA',value:'10,18 %',period:'3.er trimestre 2026',
        published:'2026-10-27',quality:'Estimación de encuesta; no registro administrativo',
        source:'https://www.ine.es/dyngs/Prensa/es/EPA3T26.htm'}),
      Object.freeze({id:'ocupados',name:'Personas ocupadas · EPA',value:'22.852.600',period:'3.er trimestre 2026',
        published:'2026-10-27',quality:'Estimación de encuesta; no cuenta de afiliaciones',
        source:'https://www.ine.es/dyngs/Prensa/es/EPA3T26.htm'})
    ]),
    epaQ3Change:Object.freeze({
      years:Object.freeze([2017,2018,2019,2020,2021,2022,2023,2024,2025,2026]),
      thousands:Object.freeze([235.9,183.9,69.4,569.6,387.1,138.3,188.0,138.3,118.4,73.6]),
      source:'https://www.ine.es/dyngs/Prensa/es/EPA3T26.htm',
      definition:'Variación del número de ocupados durante el tercer trimestre respecto al segundo, miles de personas',
      published:'2026-10-27'
    })
  });
  function hash(s){let h=2166136261;for(const c of s){h^=c.charCodeAt(0);h=Math.imul(h,16777619);}return h>>>0;}
  function value(indicator,region,week){
    if(!INDICATORS.some(i=>i.id===indicator)||!REGIONS.includes(region)||!Number.isInteger(week)||week<1||week>8)throw Error('Serie sintética desconocida.');
    const seed=hash(indicator+'|'+region);
    return Math.max(7,Math.min(93,31+(seed%34)+Math.round(9*Math.sin((week+(seed%9))/2))+(hash(indicator+'|'+region+'|'+week)%13)-6));
  }
  function series(indicator,region){return Array.from({length:8},(_,i)=>value(indicator,region,i+1));}
  function weekEvent(week){return EVENTS[week-1]||null;}
  function eventScore(c,event){
    if(!event||!c)return 0;
    const signal=event.signal==='alianzas'?'alianzas':event.signal==='debate'?'debate':'datos';
    const specialist=c.role===event.role?5:0;
    const expertise=Math.floor(c.stats[signal]/24);
    // A poorly received measure tempers outcomes, but public protest itself remains
    // a scoreable civic event through its type and specialist contribution.
    const reception=event.reception<45?-2:event.reception>=70?2:0;
    const stage=({'Consulta':0,'Comisión':1,'Acuerdo':3,'Revisión':-1,
      'Diagnóstico':1,'Despliegue':4,'Evaluación':0,'Resolución':3})[event.stage]||0;
    return specialist+expertise+reception+stage;
  }
  return Object.freeze({EVENTS,REGIONS,INDICATORS,SOURCES,REAL_SNAPSHOT,hash,value,series,weekEvent,eventScore});
});
