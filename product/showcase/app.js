/* Interactive editorial showcase. Only fictional cards are scored. */
(function () {
  'use strict';
  const E=window.PFLDemoEngine, PARTIES=window.PFL_PARTIES;
  const STORAGE='pfl-showcase-edition-zero-v1';
  const PAGES={inicio:'Inicio',mercado:'Mercado',plantilla:'Mi equipo',jornadas:'Jornadas',
    liga:'Clasificación',partidos:'Partidos españoles',laboratorio:'Laboratorio',perfil:'Mi perfil'};
  const ui={page:PAGES[location.hash.slice(1)]?location.hash.slice(1):'inicio',
    marketQuery:'',marketRole:'Todas',marketSort:'orden',partyQuery:'',scope:'Todas',
    kind:'Todas',favouritesOnly:false,badge:null};
  const $=id=>document.getElementById(id);
  const normal=s=>String(s||'').normalize('NFD').replace(/[\u0300-\u036f]/g,'').toLowerCase();
  const number=n=>new Intl.NumberFormat('es-ES').format(n);
  const e=(tag,cls,content,attributes)=>{
    const node=document.createElement(tag);
    if(cls)node.className=cls;
    if(content!==undefined&&content!==null)append(node,content);
    if(attributes)for(const [key,value] of Object.entries(attributes)){
      if(key==='dataset')for(const [k,v] of Object.entries(value))node.dataset[k]=String(v);
      else if(key==='checked'||key==='disabled'||key==='hidden'||key==='selected')node[key]=Boolean(value);
      else if(key==='value')node.value=String(value);
      else node.setAttribute(key,String(value));
    }
    return node;
  };
  function append(parent,children){
    for(const child of Array.isArray(children)?children:[children]){
      if(child===null||child===undefined||child===false)continue;
      parent.appendChild(child instanceof Node?child:document.createTextNode(String(child)));
    }
    return parent;
  }
  const div=(cls,...children)=>e('div',cls,children);
  const span=(cls,content)=>e('span',cls,content);
  const heading=(level,cls,text)=>e('h'+level,cls,text);
  const para=(cls,text)=>e('p',cls,text);
  const label=(content)=>span('overline',content);
  const section=(cls,...children)=>e('section',cls,children);
  const formatPoints=amount=>number(amount)+' pts';
  let state;
  try {const saved=JSON.parse(localStorage.getItem(STORAGE));state=E.validState(saved)?saved:E.newGame();}
  catch(_){state=E.newGame();}
  let toastTimer=0;
  function notify(message,isError=false){
    const node=$('toast');node.textContent=message;
    node.className='toast visible'+(isError?' error':'');
    clearTimeout(toastTimer);toastTimer=setTimeout(()=>node.className='toast',3300);
  }
  function persist(){
    try{localStorage.setItem(STORAGE,JSON.stringify(state));}
    catch(_){notify('No se ha podido guardar la partida en este navegador.',true);}
  }
  function commit(action,args){
    try{state=E.change(state,action,args||{});persist();render();return true;}
    catch(err){notify(err.message||'Acción no disponible',true);return false;}
  }
  function action(labelText,actionName,id,kind='secondary',disabled=false){
    return e('button','button small '+kind,labelText,
      {type:'button',dataset:{action:actionName,id:id||''},disabled:disabled});
  }
  function navigate(labelText,where,kind='secondary'){
    return e('button','button '+kind,[labelText,span('',' ↗')],
      {type:'button',dataset:{page:where}});
  }
  function sectionHeading(name,meta){
    return div('section-heading',heading(2,'',name),span('',meta||''));
  }
  function pageHeader(kicker,name,intro,extras){
    return e('header','page-header',[
      div('',para('page-kicker',kicker),heading(1,'page-heading',name),para('page-intro',intro)),
      extras?div('page-header-actions',extras):null
    ]);
  }
  function statTile(name,value,desc,accent){
    return e('article','stat-tile'+(accent?' accent':''),[
      span('stat-label',name),e('strong','',value),para('',desc)]);
  }
  function stats(){
    return div('dashboard-metrics',
      statTile('Créditos disponibles',number(state.budget)+' CR','Créditos virtuales',true),
      statTile('Puntos de temporada',number(state.points),'Juego ficticio'),
      statTile('Nivel de estrategia',String(E.level(state)).padStart(2,'0'),number(state.xp)+' XP'),
      statTile('Cartas en plantilla',state.roster.length+' / 8',state.starters.length+' titulares'));
  }
  function achievementList(limit){
    return div('quest-list',...E.achievements(state).slice(0,limit).map(a=>
      div('quest'+(a.unlocked?' complete':''),
        span('quest-symbol',a.unlocked?'✓':'○'),
        div('quest-copy',e('strong','',a.title),para('',a.detail)),
        span('quest-xp',a.unlocked?'LOGRADO':'PENDIENTE'))));
  }
  function home(){
    const hero=section('hero-layout',
      section('hero-main',
        label('EL LABORATORIO SE CONVIERTE EN JUEGO'),
        e('h1','',[ 'La política también ',e('em','',['se juega.'])]),
        para('','Construye un equipo de estrategas ficticios, explora las formaciones de España y prueba tácticas, jornadas y resultados. Una puerta de entrada a un proyecto mayor de ciencia de datos políticos.'),
        div('hero-ctas',navigate('Explorar mercado','mercado',''),
          navigate('Cómo funciona','jornadas'))),
      e('aside','hero-side',[
        div('',span('feature-label','TEMPORADA · EDICIÓN CERO'),
          div('feature-number',String(Math.min(state.week,8)).padStart(2,'0'),
            e('small','',' / 08')),
          para('feature-copy',state.week<=8?'Próxima sesión: '+E.WEEK_TITLES[state.week-1]+'. Forma tu alineación y decide cómo jugarla.':'Temporada completa: revisa tus resultados.')),
        div('',
          div('feature-row',span('','Puntos acumulados'),e('strong','',number(state.points))),
          div('feature-row',span('','Logros logrados'),e('strong','',E.achievements(state).filter(a=>a.unlocked).length+' / '+E.ACHIEVEMENTS.length)),
          div('feature-row',span('','Acceso'),e('strong','','Invitado, sin registro')))
      ]));
    const steps=section('panel',sectionHeading('Tu siguiente movimiento','TRES PASOS PARA JUGAR'),
      div('quest-list',
        div('quest',span('quest-symbol','01'),div('quest-copy',e('strong','','Explora y ficha'),para('','Elige cartas del mercado con créditos virtuales.')),navigate('Ir','mercado')),
        div('quest',span('quest-symbol','02'),div('quest-copy',e('strong','','Organiza tu equipo'),para('','Hasta cinco titulares, un capitán y una táctica.')),navigate('Ir','plantilla')),
        div('quest',span('quest-symbol','03'),div('quest-copy',e('strong','','Juega una jornada'),para('','Obtén resultados deterministas y revisa el desglose.')),navigate('Jugar','jornadas'))));
    const diary=e('section','panel',[
      sectionHeading('Actividad reciente','BITÁCORA DE TU CLUB'),
      e('ol','activity-list',state.log.slice(0,5).map((item,i)=>
        e('li','',[span('activity-no',String(i+1).padStart(2,'0')),span('',item.message)]))),
      para('footer-caption','La partida se guarda solo en este navegador. Puedes exportarla desde tu perfil.')
    ]);
    return div('',hero,stats(),div('two-columns',steps,diary),div('leadline'),
      div('two-columns',
        section('',para('page-kicker','EXPLORACIÓN INSTITUCIONAL'),
          heading(2,'serif','Un mapa político para seguir descubriendo.'),
          para('page-intro','El directorio reúne '+PARTIES.length+' denominaciones y candidaturas españolas. Unos nombres se anclan en elecciones documentadas; otros necesitan comprobación registral individual.'),
          navigate('Explorar formaciones','partidos')),
        section('panel',label('CIENCIA + PRODUCTO'),
          para('serif','La diversión es la superficie. Debajo existe un proyecto de trazabilidad, historia institucional y simulación.'),
          para('footer-caption','El juego no puntúa políticos ni partidos reales.'),
          navigate('Abrir laboratorio','laboratorio'))));
  }
  function cardStats(c){
    return div('mini-stats',...[
      ['Datos',c.stats.datos],['Acuerdos',c.stats.alianzas],['Debate',c.stats.debate]
    ].map(([name,score])=>div('mini-stat',e('label','',name),e('strong','',score))));
  }
  function character(c){
    const owned=state.roster.includes(c.id);
    return e('article','character-card',[
      div('char-top',span('char-portrait',c.symbol),span('char-price',c.price+' CR')),
      span('char-role',c.role+' · CARTA '+c.id.slice(1)),heading(3,'',c.name),
      para('char-desc',c.description),cardStats(c),
      div('char-footer',span(owned?'owned-note':'small-text text-muted',owned?'✓ EN TU EQUIPO':'Disponible'),
        action(owned?'En plantilla':'Fichar','buy',c.id,owned?'secondary':'',
          owned||state.roster.length>=E.MAX_ROSTER||state.budget<c.price))
    ]);
  }
  function selectControl(id,desc,options,current){
    return e('select','',options.map(([value,name])=>
      e('option','',name,{value,selected:current===value})),
      {id,'aria-label':desc});
  }
  function filterMarket(){
    let list=E.CARDS.filter(c=>ui.marketRole==='Todas'||c.role===ui.marketRole)
      .filter(c=>normal(c.name+' '+c.description).includes(normal(ui.marketQuery)));
    if(ui.marketSort==='baratos')list.sort((a,b)=>a.price-b.price);
    if(ui.marketSort==='caros')list.sort((a,b)=>b.price-a.price);
    if(ui.marketSort==='habilidad')list.sort((a,b)=>Math.max(...Object.values(b.stats))-Math.max(...Object.values(a.stats)));
    return list;
  }
  function market(){
    const search=e('input','',null,{id:'market-search',type:'search',placeholder:'Buscar cartas o habilidades…',
      'aria-label':'Buscar cartas',value:ui.marketQuery});
    return div('',pageHeader('MERCADO / CARTAS DE FICCIÓN','Cada decisión cuenta.',
      '18 personajes ficticios con habilidades inventadas. Construye tu equipo y prueba diferentes combinaciones.',
      span('tag active','SALDO '+number(state.budget)+' CR')),
      para('source-note','Las cartas no representan a políticos españoles. Sus nombres, perfiles, habilidades y precios son ficción, no valoraciones de personas reales.'),
      div('toolbar',search,
        selectControl('market-role','Filtrar especialidad',[['Todas','Todas las especialidades'],
          ...['Información','Acuerdos','Debate','Estrategia'].map(x=>[x,x])],ui.marketRole),
        selectControl('market-sort','Ordenar mercado',[['orden','Orden del catálogo'],['baratos','Menor precio'],['caros','Mayor precio'],['habilidad','Mejor habilidad']],ui.marketSort)),
      para('footer-caption',''),div('card-grid'));
  }
  function updateMarket(){
    const grid=document.querySelector('.card-grid'),note=grid?.previousElementSibling;if(!grid)return;
    const items=filterMarket();grid.replaceChildren(...items.map(character));
    note.textContent=items.length+' cartas visibles · '+state.roster.length+' fichadas · máximo ocho.';
    if(!items.length)grid.append(div('empty-state',heading(3,'','Sin resultados'),
      para('','Prueba otra palabra o especialidad.')));
  }
  function rosterRow(c){
    const playing=state.starters.includes(c.id),captain=state.captain===c.id;
    return div('roster-item',
      span('roster-icon',c.symbol),
      div('',e('strong','roster-name',c.name),span('roster-desc',c.role+' · '+c.price+' CR'),
        captain?span('tag warm','CAPITÁN'):null),
      div('roster-actions',
        action(playing?'Quitar titular':'Poner titular','lineup',c.id,'secondary',!playing&&state.starters.length===5),
        playing?action(captain?'Capitán ✓':'Capitán','captain',c.id,'secondary',captain):null,
        action('Vender +'+Math.floor(c.price*.75)+' CR','sell',c.id)));
  }
  function tactics(){
    return div('',...E.TACTICS.map(t=>
      e('button','tactic-option'+(t.id===state.tactic?' active':''),[
        span('tactic-radio',''),
        div('',e('strong','',t.name),e('small','',t.detail))
      ],{type:'button',dataset:{action:'tactic',id:t.id},'aria-pressed':String(t.id===state.tactic)})));
  }
  function team(){
    return div('',pageHeader('MI EQUIPO / ESTRATEGIA','La sala de decisiones.',
      'Selecciona hasta cinco titulares, un capitán y una táctica. El laboratorio te permite comparar las opciones antes de jugar.'),
      stats(),
      div('team-layout',
        section('panel',sectionHeading('Cartas de tu club','ALINEACIÓN'),
          div('roster-list',...state.roster.map(id=>rosterRow(E.card(id)))),
          para('footer-caption','Se necesitan al menos tres titulares para celebrar una jornada. La venta reintegra el 75 % del precio original.'),
          div('tag-group',navigate('Buscar fichajes','mercado'),navigate('Jugar jornada','jornadas',''))),
        section('panel',sectionHeading('Plan de juego','BONIFICACIONES'),tactics(),
          div('detail-block',label('REGLAS TRANSPARENTES'),
            para('footer-caption','Las habilidades aportan una base ficticia; la táctica suma 4 puntos a una especialidad y el capitán añade el 50 % de su subtotal.')),
          navigate('Comparar estrategias','laboratorio'))));
  }
  function dataTable(headers,rows){
    const table=e('table','',[
      e('thead','',e('tr','',headers.map(h=>e('th',h.right?'right':'',h.name)))),
      e('tbody','',rows.map(row=>e('tr',row.emphasis?'emph-row':'',
        row.values.map((v,i)=>e('td',headers[i].right?'right':'',String(v))))))
    ]);
    return div('table-scroll',table);
  }
  function rounds(){
    const finished=state.week>E.MAX_WEEKS;
    const last=state.rounds.at(-1);
    const feature=section('round-callout',
      div('',label(finished?'TEMPORADA FINALIZADA':'JORNADA '+String(state.week).padStart(2,'0')),
        heading(2,'',finished?'Una temporada completa.':E.WEEK_TITLES[state.week-1]),
        para('',finished?'Puedes revisar la clasificación y tus ocho actas.':
          'Titulares: '+state.starters.length+'. Táctica: '+E.TACTICS.find(t=>t.id===state.tactic).name+'. '+(state.starters.length<3?'Necesitas al menos tres titulares.':'La simulación está lista.')),
        action(finished?'Temporada completada':'Celebrar jornada '+state.week,'round','', '',
          finished||state.starters.length<3),
        para('footer-caption','Cada jornada otorga 14 CR y 30 XP.')),
      div('round-figure',String(state.rounds.length).padStart(2,'0'),
        e('small','','JORNADAS COMPLETADAS / 08')));
    const history=state.rounds.length?
      div('two-columns',
        section('',sectionHeading('Registro de jornadas','MARCADOR PERSONAL'),
          div('round-history',...[...state.rounds].reverse().map(r=>
            e('article','history-item',[
              div('',span('eyebrow','JORNADA '+r.week),e('strong','roster-name',r.title),
                para('',E.TACTICS.find(t=>t.id===r.tactic)?.name||r.tactic)),
              span('big-score',r.points+' pts')
            ])))),
        section('panel',sectionHeading('Última sesión','DESGLOSE'),
          para('footer-caption','Jornada '+last.week+'. '+last.title+'. Todo el cálculo es ficticio.'),
          dataTable([{name:'Carta'},{name:'Base',right:true},{name:'Táctica',right:true},
            {name:'Variación',right:true},{name:'Capitán',right:true},{name:'Puntos',right:true}],
            last.breakdown.map(x=>({values:[E.card(x.id).name,x.base,x.boosted,
              x.variance,x.captain,x.points]}))))):
      section('empty-state',heading(3,'','Todavía no hay actas.'),
        para('','Prepara tres titulares y celebra la primera sesión.'),
        navigate('Preparar alineación','plantilla'));
    return div('',pageHeader('CALENDARIO / OCHO SESIONES','El tiempo de jugar.',
      'Cada jornada transforma una alineación y una táctica en puntos explicables. No predice acontecimientos políticos reales.'),
      feature,history);
  }
  function league(){
    const standings=E.leaderboard(state);
    return div('',pageHeader('LIGA / FICCIÓN COMPETITIVA','La clasificación.',
      'Compite contra cuatro clubes inventados. Las puntuaciones no reflejan actividad o valor político real.'),
      stats(),section('panel',sectionHeading('Tabla general','TEMPORADA CERO'),
        dataTable([{name:'Pos.'},{name:'Club'},{name:'Jornadas',right:true},{name:'Puntos',right:true}],
          standings.map((r,i)=>({emphasis:r.isUser,values:[
            i+1,r.name+(r.isUser?' · TU EQUIPO':''),state.rounds.length,r.points]}))),
        para('footer-caption','Los rivales se calculan con 43 + hash(club, jornada) módulo 35. No hay otros jugadores conectados.')),
      navigate('Seguir jugando','jornadas',''));
  }
  function partyFiltered(){
    return PARTIES.filter(p=>
      (ui.scope==='Todas'||p.territory===ui.scope)&&
      (ui.kind==='Todas'||p.kind===ui.kind)&&
      (!ui.favouritesOnly||state.favorites.includes(p.id))&&
      normal(p.name+' '+p.short+' '+p.territory).includes(normal(ui.partyQuery)));
  }
  function anchorName(a){
    return a==='C23'?'Congreso 2023':a==='E24'?'Europeas 2024':'Referencia editorial';
  }
  function partyCard(p){
    const favorite=state.favorites.includes(p.id);
    return e('article','party-row',[
      span('party-mark',p.short.substring(0,11)),
      div('party-meta',e('strong','',p.name),e('small','',p.territory+' · '+p.kind),
        e('small','',anchorName(p.anchor))),
      e('button','heart',favorite?'★':'☆',
        {type:'button','aria-label':(favorite?'Quitar de favoritos: ':'Guardar favorita: ')+p.name,
          'aria-pressed':String(favorite),dataset:{action:'favorite',id:p.id}})
    ]);
  }
  function updatePartyList(){
    const holder=$('party-list');if(!holder)return;
    const items=partyFiltered();holder.replaceChildren(...items.map(partyCard));
    $('party-total').textContent=items.length+' referencias mostradas · '+state.favorites.length+' favoritas · registro jurídico no verificado.';
    if(!items.length)holder.append(section('empty-state',
      heading(3,'','Ninguna coincidencia'),para('','Prueba otra denominación o elimina algún filtro. La ausencia no demuestra que la formación no exista.')));
  }
  function link(text,url){
    return e('a','',text,{href:url,target:'_blank',rel:'noopener noreferrer'});
  }
  function parties(){
    const territories=[...new Set(PARTIES.map(p=>p.territory))].sort((a,b)=>a.localeCompare(b,'es'));
    const kinds=[...new Set(PARTIES.map(p=>p.kind))].sort((a,b)=>a.localeCompare(b,'es'));
    return div('',
      pageHeader('DIRECTORIO / UNIVERSO POLÍTICO','La pluralidad en un lugar.',
        'Explora referencias a partidos, coaliciones, candidaturas y formaciones históricas. No se acredita aquí que estén registradas ni vigentes.',
        span('tag active',PARTIES.length+' REFERENCIAS')),
      section('source-note',
        e('strong','','Nota metodológica. '),
        'Directorio orientativo y no exhaustivo. Los anclajes electorales remiten a candidaturas de 2023 y 2024, no a un padrón de partidos activos en 2026. Los favoritos son cosméticos y no afectan a puntos.',
        div('',link('Congreso 2023 ↗','https://www.congreso.es/backoffice_doc/prensa/notas_prensa/99427_1692877250184.pdf'),
          span('',' · '),link('Europeas 2024 ↗','https://results.elections.europa.eu/es/resultados-nacionales/espana/2024-2029/'),
          span('',' · '),link('Registro de Interior ↗','https://sede.interior.gob.es/portal/sede/tramites'))),
      div('toolbar',
        e('input','',null,{id:'party-search',type:'search',placeholder:'Buscar una formación…',
          'aria-label':'Buscar formaciones',value:ui.partyQuery}),
        selectControl('party-scope','Territorio',[['Todas','Toda España'],...territories.map(x=>[x,x])],ui.scope),
        selectControl('party-kind','Tipo de formación',[['Todas','Todas las categorías'],...kinds.map(x=>[x,x])],ui.kind),
        e('label','small-text',[
          e('input','',null,{id:'party-favorites',type:'checkbox',checked:ui.favouritesOnly}),
          span('','Solo favoritas')
        ])),
      e('p','footer-caption','',{id:'party-total'}),
      e('div','catalogue-grid',null,{id:'party-list'}));
  }
  function lab(){
    const allowed=state.week<=E.MAX_WEEKS&&state.starters.length>=3;
    const results=allowed?E.TACTICS.map(t=>{
      const next=E.change(E.change(state,'tactic',{id:t.id}),'round');
      return {tactic:t,points:next.rounds.at(-1).points};
    }):[];
    const max=Math.max(1,...results.map(x=>x.points));
    return div('',pageHeader('LABORATORIO / SIMULACIÓN','Abre la caja negra.',
      'Prueba una misma alineación bajo tres reglas. Los resultados son propiedades de nuestro juego ficticio, no efectos causales observados en España.'),
      section('source-note',e('strong','','Diferencia fundamental: '),
        'las simulaciones permiten analizar reglas declaradas, pero no estiman causalidad ni actividad real de formaciones políticas.'),
      sectionHeading('Ensayo contrafactual de tácticas','MISMA ALINEACIÓN · MISMA JORNADA'),
      allowed?div('lab-grid',...results.map(x=>section('lab-result',
        label(x.tactic.name),e('strong','',formatPoints(x.points)),
        div('bar-track',e('div','bar-fill',null,{style:'width:'+Math.round(x.points/max*100)+'%'})),
        para('',x.tactic.id===state.tactic?'Táctica activa':'Alternativa no aplicada'),
        action(x.tactic.id===state.tactic?'Seleccionada':'Elegir táctica','tactic',x.tactic.id,
          'secondary',x.tactic.id===state.tactic)))):
        section('empty-state',heading(3,'','Necesitas tres titulares.'),
          para('','Completa tu alineación para comparar estrategias.'),navigate('Preparar equipo','plantilla')),
      div('leadline'),
      div('two-columns',
        section('panel',sectionHeading('Lo que el juego calcula','REGLA EXPLÍCITA'),
          para('footer-caption','Base = media de las tres habilidades / 9, redondeada; +4 por la especialidad favorecida, +0–7 por hash fijo de carta y jornada, +50 % sobre subtotal del capitán. Repetible, pero no evidencia social.')),
        section('panel',sectionHeading('El proyecto que hay detrás','RIGOR CIENTÍFICO'),
          para('footer-caption','La infraestructura de investigación de PFL trabaja hacia fuentes primarias, derechos de reutilización, identificadores temporales, modelos validados y registro de incertidumbre. El producto fantasy es una de sus aplicaciones.'))));
  }
  function profile(){
    ui.badge=ui.badge||state.badge;
    const badgeOptions=div('badge-chooser',...['H','C','L','A','D','M','V','P'].map(ch=>
      e('button','badge-option',ch,{type:'button','aria-label':'Elegir insignia '+ch,
        'aria-pressed':String(ui.badge===ch),dataset:{action:'badge',id:ch}})));
    const form=e('form','form-stack',[
      e('label','',['Nombre del club',e('input','',null,{id:'profile-name',type:'text',
        value:state.club,required:true,minlength:3,maxlength:28,autocomplete:'off'})]),
      e('label','','Insignia del equipo'),badgeOptions,
      e('button','button','Guardar perfil',{type:'submit'})
    ],{id:'profile-form'});
    const completion=e('div','xp-track',e('span','',null,{style:'width:'+(state.xp%100)+'%'}));
    return div('',pageHeader('PERFIL / PROGRESIÓN','Tu propia historia.',
      'Personaliza tu club, consulta logros y exporta tu progreso sin crear una cuenta.'),
      section('level-strip',span('level-icon',state.badge),
        div('level-details',label('ESTRATEGIA · NIVEL '+E.level(state)),
          heading(2,'',state.club),
          para('',number(state.xp)+' XP · '+E.achievements(state).filter(x=>x.unlocked).length+' logros'),
          completion)),
      div('two-columns',
        section('panel',sectionHeading('Identidad del club','PERSONALIZACIÓN'),form,
          div('leadline'),sectionHeading('Mi temporada','PROGRESO DE JUEGO'),
          div('progress-columns',
            div('progress-panel',e('label','','Jornadas'),e('strong','',state.rounds.length)),
            div('progress-panel',e('label','','Fichajes'),e('strong','',state.transfers)),
            div('progress-panel',e('label','','Favoritas'),e('strong','',state.favorites.length))),
          div('leadline'),sectionHeading('Guardar partida','CONTROL LOCAL'),
          para('footer-caption','Exporta un JSON que podrás importar en otro navegador. La importación reemplaza el progreso local; no existe sincronización remota.'),
          div('tag-group',action('Exportar partida','export',''),action('Importar archivo','import',''),
            action('Restablecer demo','reset','','danger')),
          e('input','',null,{type:'file',id:'import-file',accept:'.json,application/json',hidden:true})),
        section('panel',sectionHeading('Colección de insignias','LOGROS POR ACCIONES'),
          achievementList(E.ACHIEVEMENTS.length))));
  }
  const views={inicio:home,mercado:market,plantilla:team,jornadas:rounds,
    liga:league,partidos:parties,laboratorio:lab,perfil:profile};
  function render(){
    if(!E.validState(state)){state=E.newGame();persist();}
    document.body.dataset.theme=state.theme;
    $('theme-toggle').setAttribute('aria-label',state.theme==='dark'?'Activar modo claro':'Activar modo oscuro');
    $('top-club').textContent=state.club;$('top-monogram').textContent=state.badge;
    $('top-week').textContent=String(Math.min(8,state.week)).padStart(2,'0');
    $('page-title').textContent=PAGES[ui.page];
    document.querySelectorAll('.nav-link').forEach(n=>{
      const active=n.dataset.page===ui.page;n.classList.toggle('active',active);
      if(active)n.setAttribute('aria-current','page');else n.removeAttribute('aria-current');
    });
    $('page-content').replaceChildren(views[ui.page]());
    if(ui.page==='mercado')updateMarket();
    if(ui.page==='partidos')updatePartyList();
  }
  function go(page){
    if(!PAGES[page])return;
    ui.page=page;if(page!=='perfil')ui.badge=null;
    history.replaceState(null,'','#'+page);render();
    window.scrollTo({top:0,behavior:'instant'});
  }
  function showDialog(children){
    $('dialog-body').replaceChildren(...children);$('dialog-backdrop').hidden=false;
    $('dialog-close').focus();
  }
  function closeDialog(){$('dialog-backdrop').hidden=true;$('dialog-body').replaceChildren();}
  function exportGame(){
    const url=URL.createObjectURL(new Blob([JSON.stringify(state,null,2)+'\n'],
      {type:'application/json'}));
    const a=e('a','',null,{href:url,download:'politics-fantasy-partida.json'});
    document.body.append(a);a.click();a.remove();
    setTimeout(()=>URL.revokeObjectURL(url),1000);
    notify('Partida exportada. No se envió información al servidor.');
  }
  document.addEventListener('click',ev=>{
    const p=ev.target.closest('[data-page]');
    if(p){go(p.dataset.page);return;}
    const n=ev.target.closest('[data-action]');if(!n)return;
    const op=n.dataset.action,id=n.dataset.id;
    if(['buy','sell','lineup','captain','tactic','favorite','round'].includes(op)){
      if(commit(op,{id}))notify(({buy:'Carta fichada',sell:'Carta vendida',
        lineup:'Alineación guardada',captain:'Capitanía actualizada',
        tactic:'Táctica seleccionada',favorite:'Favoritos actualizados',
        round:'Jornada completada'})[op]);
    }else if(op==='badge'){
      ui.badge=id;
      document.querySelectorAll('.badge-option').forEach(x=>
        x.setAttribute('aria-pressed',String(x.dataset.id===id)));
    }else if(op==='export')exportGame();
    else if(op==='import')$('import-file').click();
    else if(op==='reset')showDialog([
      label('RESTABLECER PARTIDA'),heading(2,'','¿Empezar de nuevo?'),
      para('','Se perderá el progreso local de esta demo: jornadas, fichajes, créditos, favoritos y experiencia.'),
      div('dialog-actions',action('Cancelar','cancel-reset',''),
        action('Restablecer partida','confirm-reset','','danger'))
    ]);
    else if(op==='cancel-reset')closeDialog();
    else if(op==='confirm-reset'){
      state=E.newGame();persist();closeDialog();go('inicio');notify('Partida restablecida.');
    }
  });
  $('theme-toggle').addEventListener('click',()=>commit('theme',{
    id:state.theme==='dark'?'light':'dark'}));
  document.addEventListener('input',ev=>{
    if(ev.target.id==='market-search'){ui.marketQuery=ev.target.value;updateMarket();}
    if(ev.target.id==='party-search'){ui.partyQuery=ev.target.value;updatePartyList();}
  });
  document.addEventListener('change',async ev=>{
    const id=ev.target.id;
    if(id==='market-role'){ui.marketRole=ev.target.value;updateMarket();}
    if(id==='market-sort'){ui.marketSort=ev.target.value;updateMarket();}
    if(id==='party-scope'){ui.scope=ev.target.value;updatePartyList();}
    if(id==='party-kind'){ui.kind=ev.target.value;updatePartyList();}
    if(id==='party-favorites'){ui.favouritesOnly=ev.target.checked;updatePartyList();}
    if(id==='import-file'){
      const file=ev.target.files?.[0];if(!file)return;
      try{
        if(file.size>100000)throw new Error('Archivo demasiado grande.');
        const imported=JSON.parse(await file.text());
        if(!E.validState(imported))throw new Error('Partida incompatible o inválida.');
        state=imported;persist();render();notify('Partida importada.');
      }catch(err){notify(err.message||'No se pudo importar.',true);}
      ev.target.value='';
    }
  });
  document.addEventListener('submit',ev=>{
    if(ev.target.id!=='profile-form')return;
    ev.preventDefault();
    if(commit('profile',{name:$('profile-name').value,badge:ui.badge||state.badge})){
      ui.badge=null;notify('Perfil actualizado.');
    }
  });
  $('dialog-close').addEventListener('click',closeDialog);
  $('dialog-backdrop').addEventListener('click',ev=>{
    if(ev.target.id==='dialog-backdrop')closeDialog();
  });
  document.addEventListener('keydown',ev=>{
    if(ev.key==='Escape'&&!$('dialog-backdrop').hidden)closeDialog();
  });
  window.addEventListener('hashchange',()=>{
    if(PAGES[location.hash.slice(1)])go(location.hash.slice(1));
  });
  render();
})();
