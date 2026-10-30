import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {runInNewContext} from 'node:vm';
const code=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const match=code.match(/function insightsPanel\(\)\{[\s\S]*?\n\}/);
assert.ok(match,'Insights panel must exist');
const x={
 c17:{portfolio_book_value:100},c18:{affordable_unowned_count:2},
 c19:{entropy_normalized:1},c20:{hhi:0.55},
 c21:{status:'SAVED_VALID_LINEUP',starter_value:68},
 c22:{cash_delta_bounded:-12},c23:{figures_traded_multiple_times:1},
 c24:{status:'READY'},c25:{mean_scored:null},c26:{hhi:0.4}
};
const ui={club:'demo',state:{insights:{demo:x}}};
const context={ui,
 stat:(title,value,info)=>'<article>'+title+':'+value+':'+info+'</article>',
 money:n=>String(n)+' CR',count:n=>String(n),esc:s=>String(s)};
const panel=runInNewContext(match[0]+'\ninsightsPanel',{...context});
test('ten independent metrics visible with non-causal disclaimer',()=>{
 const s=panel();
 for(let i=17;i<=26;i++)assert.match(s,new RegExp('C'+i+' ·'));
 assert.match(s,/no es una medición/i);
 assert.match(s,/—/);
});
test('other account missing club insight cannot leak',()=>{
 ui.club='foreign';
 const s=panel();
 assert.match(s,/Sin indicadores para el club/);
 assert.doesNotMatch(s,/100 CR/);
});
