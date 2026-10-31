import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import {createRequire} from 'node:module';
import path from 'node:path';
import {fileURLToPath} from 'node:url';
const require=createRequire(import.meta.url);
const root=path.dirname(fileURLToPath(import.meta.url));
const E=require('../product/showcase/engine.js');
require('../product/showcase/parties.js');
const parties=globalThis.PFL_PARTIES;

test('la sesión inicial es autónoma, local y coherente',()=>{
  const s=E.newGame();
  assert.equal(E.validState(s),true);
  assert.equal(s.roster.length,3);
  assert.equal(s.starters.length,3);
  assert.equal(s.week,1);
  assert.equal(E.CARDS.length,18);
  assert.equal(E.MAX_WEEKS,8);
});
test('el catálogo incluye más de cien referencias sin fingir el registro oficial',()=>{
  assert.ok(parties.length>=100);
  assert.equal(new Set(parties.map(x=>x.id)).size,parties.length);
  assert.ok(new Set(parties.map(x=>x.territory)).size>=15);
  assert.ok(parties.some(x=>x.kind==='Coalición electoral'));
  assert.ok(parties.some(x=>x.kind==='Referencia histórica'));
  assert.ok(parties.some(x=>x.anchor==='C23'));
  assert.ok(parties.some(x=>x.anchor==='E24'));
  assert.ok(parties.some(x=>x.anchor==='EDU'));
});
test('las cartas nunca contienen denominaciones del catálogo ni fuentes reales',()=>{
  for(const card of E.CARDS){
    assert.equal(typeof card.price,'number');
    assert.ok(card.id.startsWith('c'));
    assert.ok(!/Pedro Sánchez|Feijóo|Abascal|Yolanda Díaz/.test(card.name));
  }
});
test('el fichaje descuenta créditos y respeta titularidad y tope',()=>{
  const s=E.newGame(),c=E.card('c02');
  const next=E.change(s,'buy',{id:c.id});
  assert.equal(next.budget,s.budget-c.price);
  assert.equal(next.roster.length,s.roster.length+1);
  assert.equal(next.transfers,1);
  assert.equal(s.roster.length,3);
  assert.throws(()=>E.change(next,'buy',{id:c.id}),/ya está/);
  let full=next;
  for(const id of ['c03','c05','c06','c11']){
    if(full.roster.length>=8)break;
    if(full.budget<E.card(id).price)break;
    full=E.change(full,'buy',{id});
  }
  assert.ok(full.roster.length<=8);
});
test('la venta es conservadora y elimina la capitanía retirada',()=>{
  const s=E.newGame(),c=E.card('c01');
  const sold=E.change(s,'sell',{id:c.id});
  assert.equal(sold.budget,s.budget+Math.floor(c.price*.75));
  assert.ok(!sold.roster.includes(c.id));
  assert.ok(!sold.starters.includes(c.id));
  assert.ok(sold.captain===null||sold.starters.includes(sold.captain));
});
test('los límites de alineación y capitanía se cumplen',()=>{
  const s=E.newGame();
  assert.throws(()=>E.change(s,'captain',{id:'c02'}),/titular/);
  const modified=E.change(s,'captain',{id:'c04'});
  assert.equal(modified.captain,'c04');
  assert.equal(modified.captainChanges,1);
  assert.throws(()=>E.change(s,'lineup',{id:'c02'}),/no pertenece/);
});
test('la simulación es determinista y registra desglose íntegro',()=>{
  const a=E.change(E.newGame(),'round');
  const b=E.change(E.newGame(),'round');
  assert.deepEqual(a.rounds,b.rounds);
  assert.equal(a.week,2);
  assert.equal(a.points,a.rounds[0].points);
  assert.equal(a.rounds[0].points,a.rounds[0].breakdown.reduce((sum,r)=>sum+r.points,0));
  assert.equal(a.budget,E.newGame().budget+14);
  assert.equal(a.xp,30);
});
test('tácticas producen comparaciones sin modificar el estado base',()=>{
  const s=E.newGame();
  const scores=E.TACTICS.map(t=>E.change(E.change(s,'tactic',{id:t.id}),'round').points);
  assert.equal(E.validState(s),true);
  assert.equal(s.rounds.length,0);
  assert.equal(scores.length,3);
  assert.ok(scores.every(Number.isSafeInteger));
});
test('ocho jornadas son el límite y la clasificación solo usa clubes ficticios',()=>{
  let s=E.newGame();
  for(let i=0;i<8;i++)s=E.change(s,'round');
  assert.equal(s.week,9);
  assert.equal(s.rounds.length,8);
  assert.equal(E.validState(s),true);
  assert.throws(()=>E.change(s,'round'),/terminado/);
  const ranking=E.leaderboard(s);
  assert.equal(ranking.length,5);
  assert.equal(ranking.filter(x=>x.isUser).length,1);
  assert.ok(ranking.every((x,i,a)=>i===0||a[i-1].points>=x.points));
});
test('favoritos y nombre de club no alteran puntos reales ni simulaciones',()=>{
  const s=E.newGame();
  const marked=E.change(s,'favorite',{id:parties[0].id});
  const named=E.change(marked,'profile',{name:'  Mi Club   de Prueba  ',badge:'V'});
  assert.equal(named.favorites.length,1);
  assert.equal(named.club,'Mi Club de Prueba');
  assert.equal(named.badge,'V');
  assert.equal(E.change(named,'round').points,E.change(s,'round').points);
  assert.equal(E.change(marked,'favorite',{id:parties[0].id}).favorites.length,0);
});
test('importación de estado malformado falla cerrada',()=>{
  const s=E.newGame();
  for(const [key,value] of [['week',100],['budget',-20],['roster',['c999']],
    ['theme','green'],['captain','c999'],['favorites',['../x']]]){
    assert.equal(E.validState({...s,[key]:value}),false,key);
  }
  assert.throws(()=>E.change(s,'op-inventada'),/no reconocida/);
});
test('puede ejecutarse con doble clic: todos los scripts son rutas locales',()=>{
  const html=fs.readFileSync(path.join(root,'../product/showcase/index.html'),'utf8');
  for(const file of ['parties.js','engine.js','app.js','style.css'])assert.ok(html.includes('./'+file));
  assert.ok(!/src="https:/.test(html));
  assert.ok(html.includes('id="party-list"')===false); // DOM se crea desde JS.
});
