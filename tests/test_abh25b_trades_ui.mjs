import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const src=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const m=src.match(/function tradeHistory\(s, clubId\)\{[\s\S]*?\n\}/);
assert.ok(m);
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const render=runInNewContext(m[0]+'\ntradeHistory',{esc,Number});
test('only active fictional club movements, signed credits and bounded statement',()=>{
 const s={figures:[{id:'F01',display_name:'Figura 01'}],trades:[
 {club_id:'A',figure_id:'F01',action:'buy',credits_delta:-23,occurred_at:'2026'},
 {club_id:'B',figure_id:'F01',action:'sell',credits_delta:23,occurred_at:'FOREIGN_MARKER'}
 ]};
 const v=render(s,'A');
 assert.match(v,/FICHAJE/);assert.match(v,/-23 CR/);
 assert.doesNotMatch(v,/FOREIGN_MARKER/);
 assert.match(v,/Últimos 40 movimientos/);
 assert.doesNotMatch(v,/\bstyle\s*=/i);
});
test('injected fictional labels are escaped and seeded assets not fabricated as transfers',()=>{
 const s={figures:[{id:'F01',display_name:'<img src=x onerror=alert(1)>'}],
 trades:[{club_id:'A',figure_id:'F01',action:'sell',credits_delta:23,occurred_at:'2026'}]};
 const v=render(s,'A');assert.match(v,/&lt;img/);assert.doesNotMatch(v,/<img/);
 assert.match(render({...s,trades:[]},'A'),/inventario inicial/);
});
