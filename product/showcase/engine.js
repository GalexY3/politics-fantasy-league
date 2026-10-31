/* Politics Fantasy League: explicitly fictional, deterministic browser game.
   No real party / politician metrics, no external network and no hidden randomness. */
(function (root, factory) {
  'use strict';
  const engine = factory();
  if (typeof module === 'object' && module.exports) module.exports = engine;
  root.PFLDemoEngine = engine;
})(typeof window !== 'undefined' ? window : globalThis, function () {
  'use strict';
  const WORLD=typeof window!=='undefined'?window.PFLDemoWorld:require('./world.js');
  const VERSION = 1;
  const MAX_WEEKS = 8, MAX_ROSTER = 8, MAX_STARTERS = 5;
  const TACTICS = Object.freeze([
    {id:'datos',name:'Inteligencia de datos',role:'Información',detail:'Bonificación de +4 a cartas de información.'},
    {id:'alianzas',name:'Mesa de alianzas',role:'Acuerdos',detail:'Bonificación de +4 a cartas de acuerdos.'},
    {id:'debate',name:'Primera línea',role:'Debate',detail:'Bonificación de +4 a cartas de debate.'}
  ]);
  const fixtures = [
    ['c01','La Cronista','Información',22,88,66,64,'Observa patrones y encuentra pistas.', 'C'],
    ['c02','La Negociadora','Acuerdos',34,62,94,78,'Convierte posiciones distantes en acuerdos.', 'N'],
    ['c03','El Orador','Debate',31,72,65,95,'Una intervención puede cambiar la jornada.', 'O'],
    ['c04','La Tejedora','Acuerdos',18,61,79,63,'Construye conexiones en silencio.', 'T'],
    ['c05','El Archivista','Información',16,91,40,55,'Conserva todo lo que otros olvidan.', 'A'],
    ['c06','La Portavoz','Debate',28,67,69,88,'Defiende la posición de su equipo.', 'P'],
    ['c07','El Cartógrafo','Estrategia',24,82,75,67,'Ve oportunidades antes que los demás.', 'K'],
    ['c08','La Analista','Información',33,95,71,65,'Convierte hipótesis en movimientos.', 'I'],
    ['c09','El Enlace','Acuerdos',20,65,83,64,'Mantiene abiertas todas las puertas.', 'E'],
    ['c10','La Táctica','Estrategia',29,83,86,63,'Domina el ritmo de una negociación.', 'X'],
    ['c11','El Relator','Información',17,79,64,58,'Documenta cada decisión importante.', 'R'],
    ['c12','La Tribuna','Debate',25,71,64,84,'Tiene respuesta para cada pregunta.', 'B'],
    ['c13','El Mediador','Acuerdos',26,64,89,68,'Encuentra el punto en común.', 'M'],
    ['c14','La Estratega','Estrategia',38,89,88,83,'Orquesta movimientos complejos.', 'S'],
    ['c15','El Mensajero','Debate',15,59,55,75,'Aparece en el momento oportuno.', 'G'],
    ['c16','La Exploradora','Información',23,83,65,62,'Ve información donde otros ven ruido.', 'F'],
    ['c17','El Diplomático','Acuerdos',30,62,91,81,'Sabe cuándo hablar y cuándo escuchar.', 'D'],
    ['c18','La Ponente','Debate',27,73,72,82,'Hace que las ideas tengan voz.', 'L']
  ];
  const CARDS = Object.freeze(fixtures.map(x=>Object.freeze({
    id:x[0],name:x[1],role:x[2],price:x[3],
    stats:Object.freeze({datos:x[4],alianzas:x[5],debate:x[6]}),
    description:x[7],symbol:x[8]
  })));
  const WEEK_TITLES = Object.freeze([
    'Sesión de apertura','El debate de las mociones','Una semana de acuerdos',
    'La agenda cambiante','Comisiones en marcha','Punto de inflexión',
    'Los últimos movimientos','Gran sesión final'
  ]);
  const RIVALS = Object.freeze([
    {id:'r1',name:'Distrito Norte',initials:'DN'},
    {id:'r2',name:'Mesa Abierta',initials:'MA'},
    {id:'r3',name:'Los Archivistas',initials:'LA'},
    {id:'r4',name:'Voto de Calidad',initials:'VC'}
  ]);
  const ACHIEVEMENTS = Object.freeze([
    {id:'welcome',title:'Primera piedra',detail:'Entra en el laboratorio',check:s=>true},
    {id:'transfer',title:'Fichaje estrella',detail:'Realiza tu primer fichaje',check:s=>s.transfers>0},
    {id:'roster',title:'Equipo en marcha',detail:'Reúne cinco cartas',check:s=>s.roster.length>=5},
    {id:'captain',title:'Brazalete',detail:'Designa un capitán nuevo',check:s=>s.captainChanges>0},
    {id:'first_round',title:'Acta de la sesión',detail:'Completa tu primera jornada',check:s=>s.rounds.length>=1},
    {id:'three_rounds',title:'Constancia',detail:'Completa tres jornadas',check:s=>s.rounds.length>=3},
    {id:'scout',title:'Mirada territorial',detail:'Guarda cinco formaciones favoritas',check:s=>s.favorites.length>=5},
    {id:'century',title:'Cien puntos',detail:'Supera 100 puntos en la temporada',check:s=>s.points>=100},
    {id:'season',title:'Temporada completa',detail:'Termina las ocho jornadas',check:s=>s.rounds.length>=MAX_WEEKS}
  ]);

  function newGame() {
    return {
      version: VERSION, club:'Club Horizonte',badge:'H',theme:'dark',
      palette:'copper',heraldry:['tower','star','waves'],
      budget:94,roster:['c01','c04','c09'],starters:['c01','c04','c09'],
      captain:'c01',tactic:'datos',week:1,points:0,xp:0,
      rounds:[],transfers:0,captainChanges:0,favorites:[],
      log:[{message:'Tu club está listo para explorar el mercado.',week:1}]
    };
  }
  function isCard(id) { return CARDS.some(c=>c.id===id); }
  function card(id) { return CARDS.find(c=>c.id===id); }
  function assert(condition,reason) { if(!condition) throw new Error(reason); }
  function copy(s) { return JSON.parse(JSON.stringify(s)); }
  function unique(items) { return Array.isArray(items)&&new Set(items).size===items.length; }
  function validState(s) {
    if(!s||typeof s!=='object'||Array.isArray(s)||s.version!==VERSION) return false;
    if(typeof s.club!=='string'||!s.club.trim()||s.club.length>28) return false;
    if(typeof s.badge!=='string'||!['H','C','L','A','D','M','V','P'].includes(s.badge)) return false;
    if(s.palette!==undefined&&!['copper','blue','violet','silver'].includes(s.palette))return false;
    if(s.heraldry!==undefined&&(!Array.isArray(s.heraldry)||s.heraldry.length<1||s.heraldry.length>4||!unique(s.heraldry)||!s.heraldry.every(x=>['tower','star','waves','scale','sun','leaf','bridge','spark'].includes(x))))return false;
    if(!['light','dark'].includes(s.theme)||!TACTICS.some(t=>t.id===s.tactic)) return false;
    if(!Number.isSafeInteger(s.budget)||s.budget<0||s.budget>2000) return false;
    if(!Number.isSafeInteger(s.week)||s.week<1||s.week>MAX_WEEKS+1) return false;
    if(!Number.isSafeInteger(s.points)||s.points<0||!Number.isSafeInteger(s.xp)||s.xp<0) return false;
    if(!Number.isSafeInteger(s.transfers)||s.transfers<0||!Number.isSafeInteger(s.captainChanges)||s.captainChanges<0) return false;
    if(!unique(s.roster)||s.roster.length>MAX_ROSTER||!s.roster.every(isCard)) return false;
    if(!unique(s.starters)||s.starters.length>MAX_STARTERS||!s.starters.every(id=>s.roster.includes(id))) return false;
    if(s.captain!==null&&!s.starters.includes(s.captain)) return false;
    if(!unique(s.favorites)||s.favorites.length>300||!s.favorites.every(id=>typeof id==='string'&&/^f\d{3}$/.test(id))) return false;
    if(!Array.isArray(s.rounds)||s.rounds.length>MAX_WEEKS||s.week!==s.rounds.length+1) return false;
    if(!s.rounds.every((r,i)=>r&&r.week===i+1&&Number.isSafeInteger(r.points)&&r.points>=0&&Array.isArray(r.breakdown)&&r.breakdown.length<=MAX_STARTERS&&typeof r.tactic==='string')) return false;
    if(!Array.isArray(s.log)||s.log.length>15||!s.log.every(x=>x&&typeof x.message==='string'&&x.message.length<=170&&Number.isSafeInteger(x.week))) return false;
    return true;
  }
  function log(s,msg) {
    s.log.unshift({week:s.week,message:msg});
    s.log=s.log.slice(0,12);
  }
  function change(s,operation,params={}) {
    assert(validState(s),'El archivo del club no tiene un formato válido.');
    const next=copy(s);
    const id=params.id;
    if(operation==='buy'){
      const c=card(id);
      assert(c,'La carta no existe.');
      assert(!next.roster.includes(id),'Esta carta ya está en tu equipo.');
      assert(next.roster.length<MAX_ROSTER,'Plantilla completa: máximo ocho cartas.');
      assert(next.budget>=c.price,'No tienes créditos suficientes.');
      next.budget-=c.price;next.roster.push(id);next.transfers++;next.xp+=12;
      if(next.starters.length<3) next.starters.push(id);
      log(next,'Fichaje: '+c.name+' · -'+c.price+' CR.');
    } else if(operation==='sell'){
      const c=card(id);
      assert(c&&next.roster.includes(id),'No puedes vender una carta que no tienes.');
      const refund=Math.floor(c.price*.75);
      next.roster=next.roster.filter(x=>x!==id);
      next.starters=next.starters.filter(x=>x!==id);
      if(next.captain===id)next.captain=next.starters[0]||null;
      next.budget+=refund;next.xp+=3;
      log(next,'Venta: '+c.name+' · +'+refund+' CR (75 % del precio).');
    } else if(operation==='lineup'){
      assert(next.roster.includes(id),'La carta no pertenece al equipo.');
      if(next.starters.includes(id)){
        assert(next.starters.length>1,'Conserva al menos un titular.');
        next.starters=next.starters.filter(x=>x!==id);
        if(next.captain===id)next.captain=next.starters[0]||null;
      }else{
        assert(next.starters.length<MAX_STARTERS,'Solo caben cinco titulares.');
        next.starters.push(id);
        if(!next.captain)next.captain=id;
      }
      log(next,'Alineación actualizada.');
    } else if(operation==='captain'){
      assert(next.starters.includes(id),'El capitán debe ser titular.');
      if(id!==next.captain){next.captain=id;next.captainChanges++;next.xp+=5;log(next,'Nuevo capitán designado.');}
    } else if(operation==='tactic'){
      assert(TACTICS.some(t=>t.id===id),'Táctica desconocida.');
      next.tactic=id;log(next,'Cambio de planteamiento: '+TACTICS.find(t=>t.id===id).name+'.');
    } else if(operation==='favorite'){
      assert(typeof id==='string'&&/^f\d{3}$/.test(id),'Identificador de catálogo inválido.');
      next.favorites=next.favorites.includes(id)?next.favorites.filter(x=>x!==id):[...next.favorites,id];
      if(next.favorites.length>300)throw new Error('Máximo de favoritos alcanzado.');
      log(next,'Preferencias del catálogo actualizadas (sin efecto en puntuaciones).');
    } else if(operation==='profile'){
      const name=String(params.name||'').replace(/\s+/g,' ').trim();
      assert(name.length>=3&&name.length<=28,'El nombre debe tener entre 3 y 28 caracteres.');
      assert(['H','C','L','A','D','M','V','P'].includes(params.badge),'Insignia no disponible.');
      next.club=name;next.badge=params.badge;next.xp+=1;log(next,'Identidad del club actualizada.');
    } else if(operation==='theme'){
      assert(['dark','light'].includes(id),'Tema desconocido.');
      next.theme=id;
    } else if(operation==='customize'){
      const palette=String(params.palette||'');
      const heraldry=params.heraldry;
      assert(['copper','blue','violet','silver'].includes(palette),'Paleta no reconocida.');
      assert(Array.isArray(heraldry)&&heraldry.length>=1&&heraldry.length<=4&&unique(heraldry)&&heraldry.every(x=>['tower','star','waves','scale','sun','leaf','bridge','spark'].includes(x)),'La heráldica admite de uno a cuatro símbolos distintos.');
      next.palette=palette;next.heraldry=[...heraldry];log(next,'Heráldica del club rediseñada.');
    } else if(operation==='round'){
      assert(next.week<=MAX_WEEKS,'La temporada ha terminado.');
      assert(next.starters.length>=3,'Necesitas al menos tres titulares.');
      const breakdown=next.starters.map(cardId=>{
        const c=card(cardId);
        const base=Math.round((c.stats.datos+c.stats.alianzas+c.stats.debate)/27);
        const tactic=TACTICS.find(t=>t.id===next.tactic);
        const boosted=c.role===tactic.role?4:0;
        const variance=hash(c.id+'|'+next.week)%8;
        const event=WORLD.weekEvent(next.week);
        const eventPoints=WORLD.eventScore(c,event);
        const subtotal=base+boosted+variance+eventPoints;
        const captain=c.id===next.captain?Math.round(subtotal*.5):0;
        return {id:c.id,base,boosted,variance,event:eventPoints,eventId:event.id,captain,points:subtotal+captain};
      });
      const points=breakdown.reduce((sum,x)=>sum+x.points,0);
      next.rounds.push({week:next.week,title:WEEK_TITLES[next.week-1],points,
        eventId:WORLD.weekEvent(next.week).id,tactic:next.tactic,captain:next.captain,breakdown});
      next.points+=points;next.budget+=14;next.xp+=30;
      log(next,'Jornada '+next.week+' completada · +'+points+' puntos · +14 CR.');
      next.week++;
    } else {
      throw new Error('Operación no reconocida.');
    }
    assert(validState(next),'La operación ha producido un estado inválido.');
    return next;
  }
  function hash(str) {
    let h=2166136261;
    for(let i=0;i<str.length;i++){h^=str.charCodeAt(i);h=Math.imul(h,16777619);}
    return h>>>0;
  }
  function leaderboard(state) {
    assert(validState(state),'Estado inválido.');
    const others=RIVALS.map(r=>({
      id:r.id,name:r.name,initials:r.initials,isUser:false,
      points:state.rounds.reduce((n,week)=>n+43+(hash(r.id+'|'+week.week)%35),0)
    }));
    others.push({id:'myclub',name:state.club,initials:state.badge,
      points:state.points,isUser:true});
    return others.sort((a,b)=>b.points-a.points||a.name.localeCompare(b.name,'es'));
  }
  function scouting(state) {
    assert(validState(state),'Estado inválido.');
    if(state.week>MAX_WEEKS)return Object.freeze({finished:true,week:null,eventId:null,
      cards:[],tactics:[],eventBonus:0,chosenTactic:state.tactic});
    const event=WORLD.weekEvent(state.week);
    const cards=state.starters.map(id=>{
      const c=card(id);
      return Object.freeze({id,role:c.role,name:c.name,
        eventBonus:WORLD.eventScore(c,event),captain:state.captain===id});
    });
    const tactics=TACTICS.map(t=>Object.freeze({
      id:t.id,name:t.name,matched:cards.filter(c=>c.role===t.role).length,
      tacticBaseBonus:cards.filter(c=>c.role===t.role).length*4
    }));
    return Object.freeze({finished:false,week:state.week,eventId:event.id,
      cards:Object.freeze(cards),tactics:Object.freeze(tactics),
      eventBonus:cards.reduce((a,c)=>a+c.eventBonus,0),
      chosenTactic:state.tactic});
  }
  function achievements(s){return ACHIEVEMENTS.map(a=>({...a,unlocked:!!a.check(s)}));}
  function level(s){return Math.floor(s.xp/100)+1;}
  return Object.freeze({
    VERSION,MAX_WEEKS,MAX_ROSTER,MAX_STARTERS,
    CARDS,TACTICS,WEEK_TITLES,RIVALS,ACHIEVEMENTS,
    newGame,validState,card,change,hash,leaderboard,scouting,achievements,level
  });
});
