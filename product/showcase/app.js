/* Interactive editorial showcase. Only fictional cards are scored. */
(function () {
  'use strict';
  const E=window.PFLDemoEngine, PARTIES=window.PFL_PARTIES, W=window.PFLDemoWorld;
  const STORAGE='pfl-showcase-edition-zero-v1';
  const PAGES={inicio:'Inicio',mercado:'Mercado',plantilla:'Mi equipo',jornadas:'Jornadas',
    liga:'Clasificación',partidos:'Formaciones españolas',laboratorio:'Observatorio · Laboratorio',perfil:'Mi perfil'};
  const ui={page:PAGES[location.hash.slice(1)]?location.hash.slice(1):'inicio',
    marketQuery:'',marketRole:'Todas',marketSort:'orden',partyQuery:'',scope:'Todas',
    kind:'Todas',favouritesOnly:false,badge:null,labView:'panorama',
    region:'Castilla y León',indicator:'participacion',symbols:null,palette:null};
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
  const SYMBOLS=Object.freeze({tower:'♜',star:'✦',waves:'≋',scale:'⚖',sun:'☼',leaf:'❧',bridge:'⌒',spark:'✧'});
  function crest(symbols){
    const choices=symbols||state.heraldry||['tower','star','waves'];
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 160 174');svg.setAttribute('class','crest-art');
    svg.setAttribute('role','img');svg.setAttribute('aria-label','Escudo compuesto por '+choices.length+' símbolos del club');
    const ns='http://www.w3.org/2000/svg';
    const path=document.createElementNS(ns,'path');
    path.setAttribute('d','M80 8 L149 28 V92 Q143 142 80 165 Q17 142 11 92 V28 Z');
    path.setAttribute('class','crest-shield');svg.append(path);
    const divider=document.createElementNS(ns,'path');
    divider.setAttribute('d','M80 24 V154 M25 90 H135');divider.setAttribute('class','crest-lines');svg.append(divider);
    [[47,65],[113,65],[47,118],[113,118]].slice(0,choices.length).forEach(([x,y],i)=>{
      const t=document.createElementNS(ns,'text');
      t.setAttribute('x',x);t.setAttribute('y',y);
      t.setAttribute('class','crest-glyph');t.textContent=SYMBOLS[choices[i]];svg.append(t);
    });
    return svg;
  }
  function lineChart(values,title){
    const svg=document.createElementNS('http://www.w3.org/2000/svg','svg');
    svg.setAttribute('viewBox','0 0 640 245');svg.setAttribute('role','img');
    svg.setAttribute('aria-label',title+'; valores simulados: '+values.join(', '));
    svg.setAttribute('class','trend-chart');
    const ns='http://www.w3.org/2000/svg';
    const add=(tag,attrs,content)=>{
      const n=document.createElementNS(ns,tag);
      for(const [k,v]of Object.entries(attrs))n.setAttribute(k,String(v));
      if(content!==undefined)n.textContent=String(content);
      svg.append(n);return n;
    };
    for(const tick of [20,40,60,80]){const y=205-tick*1.75;
      add('line',{x1:34,y1:y,x2:616,y2:y,class:'chart-grid'});
      add('text',{x:7,y:y+4,class:'chart-label'},tick);
    }
    const pts=values.map((v,i)=>[48+i*79,205-v*1.75]);
    add('polygon',{points:[...pts,[601,205],[48,205]].map(p=>p.join(',')).join(' '),class:'chart-fill'});
    add('polyline',{points:pts.map(p=>p.join(',')).join(' '),class:'chart-stroke'});
    pts.forEach(([x,y],i)=>{add('circle',{cx:x,cy:y,r:5,class:'chart-dot'});
      add('text',{x,y:230,class:'chart-label center'},'J'+(i+1));});
    return svg;
  }
  function barChart(values,years,description){
    const ns='http://www.w3.org/2000/svg';
    const svg=document.createElementNS(ns,'svg');
    svg.setAttribute('viewBox','0 0 720 300');svg.setAttribute('class','trend-chart bar-chart');
    svg.setAttribute('role','img');
    svg.setAttribute('aria-label',description+'. '+years.map((y,i)=>y+': '+values[i]+' miles').join('; '));
    const add=(tag,props,content)=>{
      const node=document.createElementNS(ns,tag);
      Object.entries(props).forEach(([k,v])=>node.setAttribute(k,String(v)));
      if(content!==undefined)node.textContent=String(content);
      svg.append(node);return node;
    };
    for(const n of [0,200,400,600]){
      const y=251-n*.33;add('line',{x1:38,y1:y,x2:700,y2:y,class:'chart-grid'});
      add('text',{x:7,y:y+4,class:'chart-label'},n);
    }
    values.forEach((v,i)=>{
      const x=52+i*64, height=v*.33;
      const bar=add('rect',{x,y:251-height,width:34,height,class:'history-bar'+(i===values.length-1?' recent':'')});
      const title=document.createElementNS(ns,'title');title.textContent=years[i]+': '+v+' mil ocupados adicionales en T3';bar.append(title);
      add('text',{x:x+17,y:274,class:'chart-label center'},String(years[i]).slice(-2));
    });
    return svg;
  }
  function eventCard(event,compact=false){
    return e('article','event-card'+(compact?' compact':''),[
      div('event-art',e('img','',null,{src:'./artwork/'+event.id+'.svg',
        alt:'Ilustración vectorial original del escenario ficticio '+event.type,loading:'lazy'})),
      div('event-copy',span('eyebrow','ESCENARIO INVENTADO · J'+event.week+' · '+event.type),
        heading(3,'',event.title),para('',event.detail),
        div('event-meta',span('tag',event.territory),span('tag',event.stage),span('tag','Recepción ficticia '+event.reception+'/100'))),
    ]);
  }
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
    const upcoming=W.weekEvent(Math.min(8,state.week));
    const hero=section('hero-layout',
      section('hero-main',
        label('POLÍTICA FANTASY ESPAÑA · TEMPORADA DE EXHIBICIÓN'),
        e('h1','',['El país cambia.',e('em','',' Tu equipo también.')]),
        para('','La política no ocurre solo en los parlamentos. Explora actores, movilizaciones, acuerdos, políticas y territorios. Anticipa la próxima jornada en un mundo ficticio y descubre el laboratorio científico que queremos construir.'),
        div('hero-ctas',navigate('Preparar mi próxima jornada','plantilla',''),
          navigate('Explorar el Observatorio','laboratorio')),
        e('img','hero-illustration',null,{src:'./hemicycle.svg',alt:'Ilustración geométrica de un hemiciclo y sus conexiones territoriales'})),
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
    const steps=section('panel',sectionHeading('El bucle de la liga','ACTUALIDAD → ESTRATEGIA → CONSECUENCIAS'),
      div('quest-list',
        div('quest',span('quest-symbol','01'),div('quest-copy',e('strong','','Lee los acontecimientos'),para('','Observa el escenario ficticio y anticipa qué competencias importan.')),navigate('Ver','jornadas')),
        div('quest',span('quest-symbol','02'),div('quest-copy',e('strong','','Ficha y organiza'),para('','Elige hasta cinco titulares, un capitán y una táctica.')),navigate('Equipo','plantilla')),
        div('quest',span('quest-symbol','03'),div('quest-copy',e('strong','','Celebra, comprende y reacciona'),para('','Sigue cada evento, su repercusión y los puntos que genera.')),navigate('Jugar','jornadas'))));
    const diary=e('section','panel',[
      sectionHeading('Actividad reciente','BITÁCORA DE TU CLUB'),
      e('ol','activity-list',state.log.slice(0,5).map((item,i)=>
        e('li','',[span('activity-no',String(i+1).padStart(2,'0')),span('',item.message)]))),
      para('footer-caption','La partida se guarda solo en este navegador. Puedes exportarla desde tu perfil.')
    ]);
    return div('',hero,div('news-ticker',span('ticker-indicator','DOSSIER · FICCIÓN'),span('ticker-copy',upcoming.title),
      navigate('Examinar acontecimiento','jornadas','secondary')),
      stats(),sectionHeading('En el foco','ACONTECIMIENTO DE LA PRÓXIMA JORNADA'),eventCard(upcoming),
      div('two-columns',steps,diary),div('leadline'),
      div('two-columns',
        section('',para('page-kicker','EXPLORACIÓN INSTITUCIONAL'),
          heading(2,'serif','El país entero es el tablero.'),
          para('page-intro','El directorio reúne '+PARTIES.length+' denominaciones y candidaturas españolas. Unos nombres se anclan en elecciones documentadas; otros necesitan comprobación registral individual.'),
          navigate('Explorar formaciones','partidos')),
        section('panel',label('CIENCIA + PRODUCTO'),
          para('serif','Historia institucional, economía, opinión pública y datos territoriales. El laboratorio no depende del juego.'),
          para('footer-caption','El juego no puntúa políticos ni partidos reales.'),
          navigate('Abrir laboratorio','laboratorio'))),
      section('panel real-briefing',sectionHeading('En los datos oficiales','RECORTE VERIFICABLE · SIN ACTUALIZACIÓN AUTOMÁTICA'),
        div('real-metrics',...W.REAL_SNAPSHOT.metrics.slice(0,2).map(m=>div('real-metric',
          e('strong','',m.value),div('',label(m.name),para('footer-caption',m.period+' · publicación '+m.published)),
          link('INE · Nota oficial ↗',m.source)))),
        para('footer-caption','Datos reales de notas de prensa del INE. No se mezclan con los índices simulados del juego. Corte documental: '+W.REAL_SNAPSHOT.asOf+'.')));
  }
  function cardStats(c){
    return div('mini-stats',...[
      ['Datos',c.stats.datos],['Acuerdos',c.stats.alianzas],['Debate',c.stats.debate]
    ].map(([name,score])=>div('mini-stat',e('label','',name),e('strong','',score))));
  }
  function character(c){
    const owned=state.roster.includes(c.id);
    return e('article','character-card',[
      div('char-cover',e('img','',null,{src:'./artwork/'+c.id+'.svg',
        alt:'Retrato artístico del personaje inventado '+c.name,loading:'lazy'})),
      div('char-top',span('char-role',c.role+' · CARTA '+c.id.slice(1)),span('char-price',c.price+' CR')),
      heading(3,'',c.name),
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
    const current=W.weekEvent(Math.min(state.week,E.MAX_WEEKS));
    const feature=section('round-callout',
      div('',label(finished?'TEMPORADA FINALIZADA':'JORNADA '+String(state.week).padStart(2,'0')),
        heading(2,'',finished?'Una temporada completa.':E.WEEK_TITLES[state.week-1]),
        para('',finished?'Puedes revisar la clasificación y tus ocho actas.':
          'Titulares: '+state.starters.length+'. Táctica: '+E.TACTICS.find(t=>t.id===state.tactic).name+'. '+(state.starters.length<3?'Necesitas al menos tres titulares.':'La simulación está lista.')),
        action(finished?'Temporada completada':'Celebrar jornada '+state.week,'round','', '',
          finished||state.starters.length<3),
        para('footer-caption','Cada jornada otorga 14 CR y 30 XP. Los acontecimientos de esta edición son enteramente inventados.')),
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
          para('footer-caption','Jornada '+last.week+'. '+last.title+'. Evento '+last.eventId+'. Todos los datos son ficticios.'),
          dataTable([{name:'Carta'},{name:'Base',right:true},{name:'Táctica',right:true},
            {name:'Variación',right:true},{name:'Evento',right:true},{name:'Capitán',right:true},{name:'Puntos',right:true}],
            last.breakdown.map(x=>({values:[E.card(x.id).name,x.base,x.boosted,
              x.variance,x.event||0,x.captain,x.points]}))))):
      section('empty-state',heading(3,'','Todavía no hay actas.'),
        para('','Prepara tres titulares y celebra la primera sesión.'),
        navigate('Preparar alineación','plantilla'));
    return div('',pageHeader('CALENDARIO / OCHO SESIONES','Lo que ocurre importa.',
      'Cada jornada combina capacidades ficticias y un acontecimiento simulado. Participación, cooperación, implementación y recepción modifican el resultado de manera transparente.'),
      sectionHeading('Dossier de la jornada','HIPÓTESIS DE JUEGO · NO NOTICIA REAL'),eventCard(current),
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
  function labTerritoryToolbar(){
    return div('toolbar',
      selectControl('lab-region','Territorio del escenario',W.REGIONS.map(x=>[x,x]),ui.region),
      selectControl('lab-indicator','Dimensión sintética',W.INDICATORS.map(x=>[x.id,x.name]),ui.indicator));
  }
  function labSeries(){
    const metric=W.INDICATORS.find(x=>x.id===ui.indicator);
    const values=W.series(ui.indicator,ui.region);
    return section('panel chart-panel',sectionHeading(metric.name,ui.region+' · OCHO SESIONES SINTÉTICAS'),
      lineChart(values,metric.name+' en '+ui.region),
      para('footer-caption',metric.definition+' Escala abstracta 0–100. Datos fabricados por una función determinista; no son cifras económicas, territoriales ni encuestas reales.'));
  }
  function labTerritories(){
    return div('',labTerritoryToolbar(),
      labSeries(),
      sectionHeading('Cobertura territorial de la demo','19 UNIDADES · NO CARTOGRAFÍA ESTADÍSTICA'),
      div('territory-grid',...W.REGIONS.map(region=>{
        const v=W.value(ui.indicator,region,Math.min(state.week,8));
        return e('button','territory-tile'+(region===ui.region?' selected':''),[
          span('territory-mark',String(v)),span('territory-name',region),
          div('bar-track',e('div','bar-fill',null,{style:'width:'+v+'%'}))
        ],{type:'button',dataset:{action:'region',id:region},'aria-pressed':String(region===ui.region),
          'aria-label':region+', índice sintético '+v+', seleccionar'})})),
      para('source-note','Visualización territorial demostrativa: los 19 índices son calculados, no datos sobre población, economía, opinión o acción política en ninguna comunidad autónoma.'));
  }
  function labPolicies(){
    const stages=['Propuesta','Consulta','Comisión','Acuerdo o veto','Implementación','Evaluación y recepción'];
    return div('',section('panel',
      sectionHeading('De una propuesta a sus consecuencias','NO SOLO VOTACIONES'),
      div('policy-steps',...stages.map((step,i)=>div('policy-step',span('policy-number',String(i+1).padStart(2,'0')),e('strong','',step)))),
      para('footer-caption','Son fases analíticas orientativas, no una secuencia universal obligatoria. Propuestas rechazadas, censuradas, pendientes y no implementadas también deben observarse en un futuro conjunto de datos verificable.')),
      sectionHeading('Ocho expedientes de ejemplo','TODOS INVENTADOS'),
      div('events-grid',...W.EVENTS.map(event=>eventCard(event,true))),
      section('panel',sectionHeading('¿Cómo puntuar sin reducirlo al escaño?','DISEÑO DEL MODELO'),
        para('','Una acción documentada podría generar indicadores diferentes para iniciativa, colaboración, deliberación, capacidad de ejecución, participación social y respuesta ciudadana. Deben atribuirse a actores y fechas concretos con una fuente verificable; no bastaría una noticia aislada.'),
        para('footer-caption','Recepción social no equivale a éxito normativo: necesitaríamos encuesta comparable, población, incertidumbre, temporalidad, control de sesgos y trazabilidad de intervenciones. La protesta es una forma de participación, no una penalización automática. Ninguno de esos indicadores reales está activado aquí.')));
  }
  function labSources(){
    return div('',section('source-note',e('strong','','Sin canal en directo habilitado. '),
      'Las fuentes siguientes están enlazadas y documentadas; esta versión no extrae datos, no recopila noticias y no ha evaluado aún los permisos de reutilización de cada activo.'),
      div('source-grid',...W.SOURCES.map(source=>section('source-card',
        span('eyebrow','FUENTE PRIMARIA · CONEXIÓN PENDIENTE'),
        heading(3,'',source.name),para('',source.topic),
        para('footer-caption',source.status),link('Consultar portal oficial ↗',source.url)
      ))),
      section('panel',sectionHeading('Contrato científico antes de conectar','PFL · INFRAESTRUCTURA'),
        para('','Cada indicador requerirá: entidad y jurisdicción, fuente de procedencia, identidad de versión, fecha de primera publicidad, ventana de observación, universo y denominador, cobertura de resultados negativos/pendientes, método de medida, licencia y límites explícitos.'),
        para('footer-caption','Las APIs de INE y BOE y los catálogos parlamentarios ofrecen rutas de documentación, pero tener una API no demuestra cobertura íntegra, permisos homogéneos ni elegibilidad para análisis confirmatorio. R5 STOP permanece vigente.')));
  }
  function labEconomy(){
    const snap=W.REAL_SNAPSHOT;
    const hist=snap.epaQ3Change;
    return div('',section('source-note',e('strong','','Datos reales, no simulados. '),
      'Este panel contiene un pequeño recorte manual de estadísticas oficiales publicadas y fechadas. No existe conexión automática, revisión de nuevas versiones ni API activa en el navegador.'),
      div('real-metrics',...snap.metrics.map(m=>section('real-metric',
        label(m.name),e('strong','',m.value),para('',m.period),
        para('footer-caption',m.quality),
        para('footer-caption','INE · publicado '+m.published),
        link('Ver fuente oficial ↗',m.source)))),
      section('panel chart-panel',sectionHeading('Evolución de la ocupación en el tercer trimestre','EPA · SERIE HISTÓRICA, ESPAÑA'),
        barChart(hist.thousands,hist.years,hist.definition),
        para('footer-caption',hist.definition+'. No son tasas porcentuales, sino cambios trimestrales expresados en miles.'),
        para('footer-caption','Fuente: INE, EPA 3T 2026, publicado '+hist.published+'. Serie incluida en la propia nota de prensa.'),
        link('Examinar tabla y metodología del INE ↗',hist.source)),
      section('panel',sectionHeading('Para entender estos indicadores','CONTEXTUALIZACIÓN'),
        para('','La EPA utiliza una encuesta para estimar ocupación, desempleo y actividad. El IPC estima cambios en precios de consumo; el dato adelantado puede revisarse en la publicación definitiva. Ninguno de los dos permite inferir directamente aprobación ciudadana de políticas concretas.'),
        para('footer-caption','Corte documental del prototipo: '+snap.asOf+'. Indicadores reales separados de eventos y series sintéticos. No se ha practicado una auditoría completa del universo ni de los derechos por activo para investigación confirmatoria.')));
  }
  function labFantasy(){
    const allowed=state.week<=E.MAX_WEEKS&&state.starters.length>=3;
    const results=allowed?E.TACTICS.map(t=>{
      const next=E.change(E.change(state,'tactic',{id:t.id}),'round');
      return {tactic:t,points:next.rounds.at(-1).points};
    }):[];
    const max=Math.max(1,...results.map(x=>x.points));
    return div('',section('source-note','Comparación interna al juego: misma alineación, mismo evento y misma jornada. Las variaciones son reglas de ficción, no efectos causales ni evaluaciones de actores reales.'),
      sectionHeading('Ensayo de tácticas','CONTRAFACTUAL DEL MOTOR FICTICIO'),
      allowed?div('lab-grid',...results.map(x=>section('lab-result',
        label(x.tactic.name),e('strong','',formatPoints(x.points)),
        div('bar-track',e('div','bar-fill',null,{style:'width:'+Math.round(x.points/max*100)+'%'})),
        para('',x.tactic.id===state.tactic?'Táctica activa':'Alternativa sin aplicar'),
        action(x.tactic.id===state.tactic?'Seleccionada':'Elegir táctica','tactic',x.tactic.id,
          'secondary',x.tactic.id===state.tactic)))):
        section('empty-state',heading(3,'','Necesitas tres titulares.'),navigate('Preparar equipo','plantilla')),
      section('panel',sectionHeading('Cómo se forman los puntos','TRAZABILIDAD DEMO'),
        para('','Cada carta combina su base, la táctica escogida, una variación determinista y su participación en el evento ficticio semanal. La recepción sintética introduce una corrección acotada; la capitanía se aplica después. Cada acta conserva el identificador de evento y su desglose.'),
        para('footer-caption','Esta regla sirve para enseñar mecánicas; no equivale a una rúbrica validada para políticos, movimientos o administraciones reales.')));
  }
  function lab(){
    const views={
      panorama:()=>div('',div('lab-stat-strip',
        statTile('Cobertura de escenarios',W.REGIONS.length,'Territorios definidos, sin observación real'),
        statTile('Acontecimientos',W.EVENTS.length,'Casos narrativos ficticios'),
        statTile('Portales de referencia',W.SOURCES.length,'Documentados, no conectados'),
        statTile('Series observadas','0','Pendientes de derechos y QA')),
        div('lab-hero-grid',labSeries(),section('panel',sectionHeading('Del acontecimiento al análisis','EL MUNDO EN MOVIMIENTO'),
          eventCard(W.weekEvent(Math.min(state.week,8)),true),
          action('Ver políticas y procesos','labtab','politicas','secondary'))),
        sectionHeading('Una España que no termina en el Congreso','GEOGRAFÍA, ECONOMÍA Y SOCIEDAD'),
        div('lab-topic-grid',...[
          ['Población y territorio','Demografía, estructura local y desigualdades','territorios','◫'],
          ['Economía y empleo','Precios, trabajo, renta y ciclos económicos','economia','↗'],
          ['Políticas y recepción','Propuesta, veto, ejecución y opinión pública','politicas','⚖'],
          ['Parlamentos y tejido social','Votación, cooperación, incidencia y movilización','politicas','◎']
        ].map(x=>e('button','topic-card',[
          span('topic-glyph',x[3]),e('strong','',x[0]),para('',x[1]),span('topic-link','Explorar área →')
        ],{type:'button',dataset:{action:'labtab',id:x[2]}}))),
        para('footer-caption','La estructura de áreas es una propuesta de producto; los gráficos actuales son simulados y no hay aún un repositorio histórico nacional integrado.')),
      territorios:labTerritories,politicas:labPolicies,economia:labEconomy,fuentes:labSources,fantasy:labFantasy
    };
    return div('',pageHeader('OBSERVATORIO / CIENCIA DE DATOS','La política, de dentro a fuera.',
      'Instituciones, ciudadanía, territorios, políticas públicas, economía y sus conexiones. El Observatorio debe ser útil incluso sin participar en la liga.',
      span('tag warm','SHOWCASE · SIMULACIÓN + RECORTE OFICIAL FECHADO')),
      div('lab-tabs',...[
        ['panorama','Panorama'],['territorios','Territorios'],['economia','Economía real'],
        ['politicas','Políticas y sociedad'],['fuentes','Fuentes oficiales'],['fantasy','Motor fantasy']
      ].map(([id,name])=>e('button','lab-tab'+(ui.labView===id?' active':''),name,
        {type:'button',dataset:{action:'labtab',id},'aria-pressed':String(ui.labView===id)}))),
      views[ui.labView]());
  }
  function profile(){
    ui.badge=ui.badge||state.badge;
    ui.symbols=ui.symbols||[...(state.heraldry||['tower','star','waves'])];
    ui.palette=ui.palette||state.palette||'copper';
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
    const symbolsChooser=div('symbol-chooser',...Object.entries(SYMBOLS).map(([id,glyph])=>
      e('button','symbol-choice',glyph,{type:'button',dataset:{action:'symbol',id},
        'aria-label':'Seleccionar símbolo '+id,'aria-pressed':String(ui.symbols.includes(id))})));
    const colours=div('palette-chooser',...[
      ['copper','Cobre'],['blue','Azul tinta'],['violet','Violeta'],['silver','Plata']
    ].map(([id,name])=>e('button','palette-choice palette-'+id,[
      span('palette-dot',''),span('',name)
    ],{type:'button',dataset:{action:'palette',id},'aria-pressed':String(ui.palette===id)})));
    return div('',pageHeader('PERFIL / PROGRESIÓN','Construye tu identidad.',
      'Nombre, emblema, heráldica y tema visual. Toda tu personalización es local: no existe cuenta remota.'),
      section('level-strip',div('level-icon',crest(state.heraldry)),
        div('level-details',label('ESTRATEGIA · NIVEL '+E.level(state)),
          heading(2,'',state.club),
          para('',number(state.xp)+' XP · '+E.achievements(state).filter(x=>x.unlocked).length+' logros'),
          completion)),
      div('two-columns',
        section('panel',sectionHeading('Identidad del club','PERSONALIZACIÓN'),form,
          div('leadline'),sectionHeading('Taller de heráldica','DE 1 A 4 SÍMBOLOS, SIN IMÁGENES EXTERNAS'),
          div('heraldry-editor',div('heraldry-display',crest(ui.symbols)),
            div('heraldry-settings',para('footer-caption','Elige entre uno y cuatro signos para construir un escudo propio. No son símbolos institucionales reales.'),
              symbolsChooser,para('footer-caption','Paleta del perfil y de la interfaz:'),colours,
              action('Guardar diseño heráldico','save-heraldry',''))),
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
        section('panel',sectionHeading('Apariencia','TEMA DEL PERFIL'),
          div('appearance-control',e('strong','','Tema de lectura'),
            para('footer-caption','El modo oscuro de grafito es el predeterminado. Puedes cambiarlo y conservarlo con tu partida.'),
            div('tag-group',action('Oscuro','set-theme','dark','secondary'),
              action('Claro','set-theme','light','secondary'))),
          div('leadline'),sectionHeading('Colección de insignias','LOGROS POR ACCIONES'),
          achievementList(E.ACHIEVEMENTS.length))));
  }
  const views={inicio:home,mercado:market,plantilla:team,jornadas:rounds,
    liga:league,partidos:parties,laboratorio:lab,perfil:profile};
  function render(){
    if(!E.validState(state)){state=E.newGame();persist();}
    document.body.dataset.theme=state.theme;
    document.body.dataset.palette=state.palette||'copper';
    $('theme-toggle').setAttribute('aria-label',state.theme==='dark'?'Activar modo claro':'Activar modo oscuro');
    $('top-club').textContent=state.club;$('top-monogram').replaceChildren(crest(state.heraldry));
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
    ui.page=page;if(page!=='perfil'){ui.badge=null;ui.symbols=null;ui.palette=null;}
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
    }else if(op==='labtab'){
      if(['panorama','territorios','economia','politicas','fuentes','fantasy'].includes(id)){
        ui.labView=id;render();
      }
    }else if(op==='region'){
      if(W.REGIONS.includes(id)){ui.region=id;render();}
    }else if(op==='symbol'){
      ui.symbols=ui.symbols||[...(state.heraldry||['tower','star','waves'])];
      if(ui.symbols.includes(id)){
        if(ui.symbols.length>1)ui.symbols=ui.symbols.filter(x=>x!==id);
        else {notify('El escudo necesita al menos un símbolo.',true);return;}
      }else{
        if(ui.symbols.length>=4){notify('Máximo cuatro símbolos.',true);return;}
        ui.symbols=[...ui.symbols,id];
      }
      document.querySelectorAll('.symbol-choice').forEach(b=>
        b.setAttribute('aria-pressed',String(ui.symbols.includes(b.dataset.id))));
      document.querySelector('.heraldry-display')?.replaceChildren(crest(ui.symbols));
    }else if(op==='palette'){
      if(['copper','blue','violet','silver'].includes(id)){
        ui.palette=id;document.body.dataset.palette=id;
        document.querySelectorAll('.palette-choice').forEach(b=>
          b.setAttribute('aria-pressed',String(id===b.dataset.id)));
      }
    }else if(op==='save-heraldry'){
      if(commit('customize',{palette:ui.palette||state.palette||'copper',
        heraldry:ui.symbols||state.heraldry||['tower','star','waves']}))notify('Escudo y paleta guardados.');
    }else if(op==='set-theme'){
      if(commit('theme',{id}))notify('Apariencia actualizada.');
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
    if(id==='lab-region'){ui.region=ev.target.value;render();}
    if(id==='lab-indicator'){ui.indicator=ev.target.value;render();}
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
