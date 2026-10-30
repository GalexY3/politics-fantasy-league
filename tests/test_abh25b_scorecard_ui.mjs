import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const source=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const match=source.match(/function roundBreakdown\(r,clubId\)\{[\s\S]*?\n\}/);
assert.ok(match,'scorecard renderer must be implemented');
const esc=s=>String(s??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const ui={state:{figures:[{id:'F01',display_name:'Figura <img src=x onerror=alert(1)>'}]}};
const render=runInNewContext(match[0]+'\nroundBreakdown',{ui,esc});
test('frozen components render only escaped fictional labels and points',()=>{
 const body=render({score_details:{demo:{status:'FROZEN_COMPONENTS',
    components:[{figure_id:'F01',points:3.0}],rule_version:'demo-0.1-SYNTHETIC'}}},'demo');
 assert.match(body,/3 puntos sintéticos/);
 assert.match(body,/&lt;img/);
 assert.doesNotMatch(body,/<img/);
 assert.doesNotMatch(body,/\bstyle\s*=/i);
});
test('legacy and pending scores do not invent zero contributions',()=>{
 assert.match(render({score_details:{demo:{status:'LEGACY_UNAVAILABLE',components:[]}}},'demo'),/sin desglose histórico/);
 assert.match(render({score_details:{demo:{status:'NOT_SETTLED',components:[]}}},'demo'),/antes del cierre/);
 assert.match(render({score_details:{demo:{status:'NO_VALID_LINEUP',components:[]}}},'demo'),/no equivale a cero/);
});
