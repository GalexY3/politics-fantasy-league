import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const code=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const match=code.match(/function seasonTable\(s\)\{[\s\S]*?\n\}/);
assert.ok(match);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const render=runInNewContext(match[0]+'\nseasonTable',{esc,count:n=>String(n)});
test('cumulative standings do not invent ranking for incomplete data',()=>{
 const html=render({season_standings:[
  {rank:1,club_name:'Ficción 1',total_points:8,rounds_scored:2,rounds_settled:2,status:'RANKED'},
  {rank:null,club_name:'Ficción 2',total_points:null,rounds_scored:1,rounds_settled:2,status:'INCOMPLETE_COVERAGE'}]});
 assert.match(html,/Ficción 1/);
 assert.match(html,/NO DISPONIBLE/);
 assert.match(html,/Faltan jornadas puntuables/);
 assert.doesNotMatch(html,/\bstyle\s*=/i);
});
test('fictional standings escape club names from UI HTML',()=>{
 const html=render({season_standings:[{rank:1,
  club_name:'<svg/onload=alert(1)>',total_points:4,
  rounds_scored:1,rounds_settled:1,status:'RANKED'}]});
 assert.match(html,/&lt;svg/);
 assert.doesNotMatch(html,/<svg/);
});
