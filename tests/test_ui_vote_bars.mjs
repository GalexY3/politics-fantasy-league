import {test} from 'node:test';
import {strict as assert} from 'node:assert';
import {readFileSync} from 'node:fs';
import {createContext, runInContext} from 'node:vm';

const source=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const context=createContext({document:{
  addEventListener(){},
  getElementById(){return {addEventListener(){}};}
}});
// Load the actual renderer without making the page's startup HTTP requests.
runInContext(source.slice(0,source.lastIndexOf('refresh().catch')),context);
const render=runInContext('voteBar',context);
const segments=html=>[...html.matchAll(/<rect\b[^>]*>/g)].map(([tag])=>({
  x:Number(tag.match(/\bx="([^"]*)"/)[1]),
  width:Number(tag.match(/\bwidth="([^"]*)"/)[1])
}));

test('vote bars retain all vote proportions without inline styles under strict CSP',()=>{
  const html=render({yes:140,no:200,abstain:10,total:350},0);
  const parts=segments(html);
  assert.equal(parts.length,3);
  for(const [i,count] of [140,200,10].entries()){
    assert.ok(Math.abs(parts[i].width-100*count/350)<1e-10);
    if(i>0)assert.ok(Math.abs(parts[i].x-parts[i-1].x-parts[i-1].width)<1e-10);
  }
  assert.ok(Math.abs(parts.reduce((sum,part)=>sum+part.width,0)-100)<1e-10);
  assert.match(html,/role="img" aria-label="Votación 1: sí 140, no 200, abstención 10\. Total 350\."/);
  assert.doesNotMatch(html,/\bstyle\s*=/i);
});

test('zero votes do not create NaN geometry or lose the accessible total',()=>{
  const html=render({yes:0,no:0,abstain:0,total:0},2);
  assert.deepEqual(segments(html),[{x:0,width:0},{x:0,width:0},{x:0,width:0}]);
  assert.match(html,/Votación 3: sí 0, no 0, abstención 0\. Total 0\./);
  assert.doesNotMatch(html,/NaN|Infinity/);
});

test('all page renderers avoid style attributes blocked by the server CSP',()=>{
  assert.doesNotMatch(source,/\bstyle\s*=/i);
});
