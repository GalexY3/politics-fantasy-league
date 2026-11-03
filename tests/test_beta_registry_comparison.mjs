import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {readFileSync} from 'node:fs';
import {webcrypto,createHash} from 'node:crypto';
import {createContext,runInContext} from 'node:vm';
import {fileURLToPath} from 'node:url';

// Real Python/SQLite source-generated fixtures, not hand-written responses.
// Only the browser's network/DOM is simulated; all SHA receipts come from S9.
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const SOURCE=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const PYENV={...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'};
const PYCODE=[
 'import json,tempfile,sys',
 'from pathlib import Path',
 'from politics_fantasy.scientific_registry import query_registry',
 'with tempfile.TemporaryDirectory(prefix="pfl-registry-compare-") as folder:',
 '    result=query_registry(Path(folder)/"fixture.sqlite3",cut=sys.argv[1],valid_at=sys.argv[2],family=sys.argv[3],published_until=sys.argv[4])',
 '    print(json.dumps(result,ensure_ascii=False))'
].join('\n');
const cache=new Map();
function pythonRegistry(cut,validAt,family,published){
 const key=[cut,validAt,family,published].join('|');
 if(!cache.has(key)){
  const result=execFileSync('python',['-B','-c',PYCODE,cut,validAt,family,published],
   {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:3*1024*1024,timeout:12000});
  cache.set(key,JSON.parse(result));
 }
 return structuredClone(cache.get(key));
}
const lab=Object.fromEntries(['early','late'].map(cut=>[
 cut,JSON.parse(execFileSync('python',['-B','scripts/run_scientific_integration_lab.py','--cut',cut],
  {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:3*1024*1024,timeout:12000}))
]));

function harness(){
 const elements={},listeners={},requests=[],downloads=[],blobs=[];
 const tabs=['overview','club','market','rounds','observatory','scientific','atlas','progress']
  .map(tab=>({dataset:{tab},hidden:false,classList:{toggle(){}},
   setAttribute(){},removeAttribute(){}}));
 let compareFail=null,rightsSpoof=false,badSha=false,holdNext=false,pending=null;
 let registryQueries=0;
 class LocalURL extends URL{}
 LocalURL.createObjectURL=blob=>{blobs.push(blob);return 'blob:synthetic-compare-test';};
 LocalURL.revokeObjectURL=()=>{};
 const document={
  getElementById(id){return elements[id]??={
   innerHTML:'',textContent:'',hidden:false,addEventListener(){}};},
  querySelectorAll(selector){return selector==='[data-tab]'?tabs:[];},
  createElement(){return{click(){downloads.push(this.download);},remove(){}};},
  body:{appendChild(){}},
  addEventListener(type,fn){listeners[type]=fn;}
 };
 const fetch=async (route,options={})=>{
  requests.push({route,method:options.method||'GET'});
  const url=new URL(route,'http://localhost');
  if(url.pathname==='/api/session')return{ok:false,status:401,
   json:async()=>({authenticated:false,error:'AUTH_REQUIRED'})};
  if(url.pathname==='/api/scientific-integration-lab'){
   const data=structuredClone(lab[url.searchParams.get('cut')||'late']);
   data.scenario=url.searchParams.get('scenario')||'baseline';
   return{ok:true,json:async()=>data};
  }
  if(url.pathname==='/api/scientific-registry'){
   const q=url.searchParams,cut=q.get('cut')||'late';
   const valid=q.get('valid_at')||'2026-09-15';
   const family=q.get('family')||'all';
   const publication=q.get('published_until')||'as_of';
   registryQueries++;
   if(compareFail&&cut===compareFail.cut)return{ok:false,status:compareFail.status};
   const data=pythonRegistry(cut,valid,family,publication);
   if(rightsSpoof&&cut==='early'){
    data.registry.distributions[0].rights_for_public_display=true;
   }
   if(badSha&&cut==='early')data.snapshot_receipt.sha256='0'.repeat(64);
   if(holdNext&&cut==='early'){
    holdNext=false;
    return new Promise(resolve=>{pending=()=>resolve({ok:true,json:async()=>data});});
   }
   return{ok:true,json:async()=>data};
  }
  throw Error('Forbidden account API route: '+route);
 };
 const context=createContext({document,fetch,URL:LocalURL,TextEncoder,Blob,crypto:webcrypto,
  Intl,Date,Number,String,Error,console,setTimeout(){},clearTimeout(){}});
 runInContext(SOURCE.slice(0,SOURCE.lastIndexOf('bootstrap().catch')),context);
 const evalJs=expression=>runInContext(expression,context);
 const click=(action,registry=null,exitGuest=false)=>listeners.click({target:{closest(selector){
  if(selector==='#guest-exit'&&exitGuest)return {};
  if(selector==='[data-action]'&&action)return{dataset:{action,registry}};
  return null;
 }}});
 const change=(id,value)=>listeners.change({target:{id,value}});
 return{
  elements,requests,downloads,blobs,evalJs,click,change,
  guest:async()=>{await evalJs('bootstrap()');await click('guest-enter');},
  setFail(cut,status){compareFail={cut,status};},
  setRightsSpoof(enabled){rightsSpoof=enabled;},
  setBadSha(enabled){badSha=enabled;},
  holdNextEarly(){holdNext=true;},
  pending(){return Boolean(pending);},
  release(){assert.ok(pending);const f=pending;pending=null;f();},
  registryQueries:()=>registryQueries
 };
}

const onlyGet=requests=>assert.ok(requests.every(r=>r.method==='GET'&&
 ['/api/session','/api/scientific-integration-lab','/api/scientific-registry']
  .includes(new URL(r.route,'http://localhost').pathname)));

test('guest compares real S9 early/late receipts, public descriptors and typed counts',async()=>{
 const t=harness();await t.guest();
 const original=t.evalJs('ui.scienceRegistry');
 assert.match(t.elements.content.innerHTML,/science-registry-tab/);
 await t.click('science-registry-tab','compare');
 const pair=t.evalJs('ui.scienceRegistryComparison');
 assert.ok(pair);
 assert.equal(pair.early.registry.visible_distribution_count,2);
 assert.equal(pair.late.registry.visible_distribution_count,6);
 const oldIds=new Set(pair.early.registry.distributions.map(d=>d.public_id));
 const newIds=new Set(pair.late.registry.distributions.map(d=>d.public_id));
 assert.equal([...newIds].filter(id=>!oldIds.has(id)).length,4);
 assert.equal([...oldIds].filter(id=>!newIds.has(id)).length,0);
 for(const cut of ['early','late']){
  const snapshot=pair[cut];
  assert.equal(createHash('sha256').update(snapshot.snapshot_receipt.canonical_json,'utf8').digest('hex'),
   snapshot.snapshot_receipt.sha256);
  assert.equal(snapshot.snapshot_receipt.external_authenticity_certified,false);
  assert.equal(snapshot.release_gates_passed,0);
  assert.equal(snapshot.scientific_ab_cycles,0);
  assert.equal(snapshot.registry.private_source_ids_exposed,false);
 }
 assert.match(t.elements.content.innerHTML,/Solo visible en late/);
 assert.match(t.elements.content.innerHTML,/Descriptores revisados/);
 assert.match(t.elements.content.innerHTML,/S9:PUBLIC_06/);
 assert.match(t.elements.content.innerHTML,/Evaluaciones sandbox S9 · eventos de registro\/rechazo/);
 assert.match(t.elements.content.innerHTML,/Cadena fuente-local · enlaces tipados/);
 assert.match(t.elements.content.innerHTML,/Crónica fuente-local · enlaces tipados/);
 assert.match(t.elements.content.innerHTML,/R5 STOP/);
 assert.match(t.elements.content.innerHTML,/ausencia ≠ negativa|Ausencia ≠ negativa/);
 assert.match(t.elements.content.innerHTML,/dos revisiones documentales no son dos decisiones/);
 assert.equal(t.evalJs('ui.scienceCut'),'late');
 assert.equal(t.evalJs('ui.scienceRegistry'),original,'Comparison cannot replace the currently selected snapshot');
 assert.equal(t.requests.filter(r=>new URL(r.route,'http://localhost').pathname==='/api/scientific-registry').length,3);
 await t.click('science-registry-export');
 assert.equal(t.downloads.length,1,'Existing S9 single-snapshot export remains operational');
 onlyGet(t.requests);
 assert.equal(t.evalJs('ui.state'),null);
 assert.equal(t.evalJs('ui.session'),null);
});

test('publication ceiling is independently capped at each author-stipulated cut',async()=>{
 const t=harness();await t.guest();
 await t.change('science-registry-publication','2026-10-30T12:00:00Z');
 await t.click('science-registry-tab','compare');
 const pair=t.evalJs('ui.scienceRegistryComparison');
 assert.equal(pair.queries[0].published,'as_of');
 assert.equal(pair.queries[1].published,'2026-10-30T12:00:00Z');
 assert.equal(pair.early.published_until,'2026-10-15T12:00:00Z');
 assert.equal(pair.late.published_until,'2026-10-30T12:00:00Z');
 assert.equal(t.evalJs('ui.scienceRegistryPublished'),'2026-10-30T12:00:00Z');
 assert.match(t.elements.content.innerHTML,/Si el límite de primera publicación seleccionado supera/);
 onlyGet(t.requests);
});

test('filtered family does not present an excluded intake overlay as zero negative events',async()=>{
 const t=harness();await t.guest();
 await t.change('science-registry-family','CHAIN');
 await t.click('science-registry-tab','compare');
 const pair=t.evalJs('ui.scienceRegistryComparison');
 assert.equal(pair.early.family,'CHAIN');
 assert.equal(pair.late.family,'CHAIN');
 assert.match(t.elements.content.innerHTML,/Fuera del filtro de familia/);
 assert.match(t.elements.content.innerHTML,/una familia filtrada no representa cero rechazos/);
 assert.equal(pair.late.registry.distributions.every(d=>d.family==='CHAIN'),true);
 onlyGet(t.requests);
});

test('comparison is independent in authenticated UI and makes no account API request',async()=>{
 const t=harness();
 t.evalJs("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.tab='scientific'");
 await t.evalJs('loadScientific()');
 await t.evalJs('loadScientificRegistry()');
 await t.click('science-registry-tab','compare');
 assert.equal(t.evalJs('ui.scienceRegistryComparison.early.cut'),'early');
 assert.equal(t.evalJs('ui.scienceRegistryComparison.late.cut'),'late');
 assert.equal(t.evalJs('ui.state.clubs[0].id'),'demo');
 onlyGet(t.requests);
});

test('authenticated first_public control invalidates the comparison without touching single S9',async()=>{
 const t=harness();
 t.evalJs("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.tab='scientific'");
 await t.evalJs('loadScientific()');
 await t.evalJs('loadScientificRegistry()');
 const original=t.evalJs('ui.scienceRegistry');
 await t.click('science-registry-tab','compare');
 assert.ok(t.evalJs('ui.scienceRegistryComparison'));
 await t.change('science-first-public','2026-09-19T12:00:00Z');
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.equal(t.evalJs('ui.scienceRegistry'),original);
 onlyGet(t.requests);
});

for(const status of [400,503]){
 test('an HTTP '+status+' comparison failure clears a formerly valid pair without fallback',async()=>{
  const t=harness();await t.guest();await t.click('science-registry-tab','compare');
  assert.ok(t.evalJs('ui.scienceRegistryComparison'));
  t.setFail('early',status);
  await t.click('science-registry-compare-load');
  assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
  assert.match(t.evalJs('ui.scienceRegistryCompareError'),new RegExp('HTTP '+status));
  assert.match(t.elements.content.innerHTML,/Comparación invalidada/);
  assert.doesNotMatch(t.elements.content.innerHTML,/S9:PUBLIC_06/);
  assert.ok(t.evalJs('ui.scienceRegistry'),'Single snapshot remains independently available');
  onlyGet(t.requests);
 });
}

for(const [name,change] of [
 ['valid_at',t=>t.change('science-registry-valid','2026-10-10')],
 ['family',t=>t.change('science-registry-family','CHAIN')],
 ['publication',t=>t.change('science-registry-publication','2026-09-19T12:00:00Z')],
 ['as_of',t=>t.change('science-cut','early')]
]){
 test(name+' change invalidates a completed comparison',async()=>{
  const t=harness();await t.guest();await t.click('science-registry-tab','compare');
  assert.ok(t.evalJs('ui.scienceRegistryComparison'));
  await change(t);
  assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
  assert.doesNotMatch(t.elements.content.innerHTML,/Descriptores revisados/);
  onlyGet(t.requests);
 });
}

test('rights spoof and SHA spoof each invalidate both projections',async()=>{
 const t=harness();await t.guest();await t.click('science-registry-tab','compare');
 t.setRightsSpoof(true);
 await t.click('science-registry-compare-load');
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.match(t.evalJs('ui.scienceRegistryCompareError'),/SHA no verificable|derechos fingidos/);
 t.setRightsSpoof(false);t.setBadSha(true);
 await t.click('science-registry-compare-load');
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.match(t.elements.content.innerHTML,/Comparación invalidada/);
 onlyGet(t.requests);
});

test('in-flight early A→B→A request never resurrects obsolete comparison',async()=>{
 const t=harness();await t.guest();
 t.holdNextEarly();
 const pending=t.click('science-registry-tab','compare');
 assert.equal(t.pending(),true,'Early projection is stalled at the network boundary');
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-valid','2026-09-15');
 assert.equal(t.evalJs('ui.scienceRegistryValid'),'2026-09-15');
 assert.ok(t.evalJs('ui.scienceRegistry'));
 t.release();
 await pending;
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.equal(t.evalJs('ui.scienceRegistryCompareLoading'),false);
 assert.doesNotMatch(t.elements.content.innerHTML,/Descriptores revisados/);
 onlyGet(t.requests);
});

test('in-flight comparison invalidates on 503 current registry',async()=>{
 const t=harness();await t.guest();
 t.holdNextEarly();
 const pending=t.click('science-registry-tab','compare');
 assert.equal(t.pending(),true);
 t.setFail('late',503);
 await t.click('science-registry-load');
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.match(t.evalJs('ui.scienceRegistryError'),/HTTP 503/);
 t.release();await pending;
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 onlyGet(t.requests);
});

test('in-flight pair cannot reappear after anonymous visitor returns to login',async()=>{
 const t=harness();await t.guest();
 t.holdNextEarly();
 const pending=t.click('science-registry-tab','compare');
 assert.equal(t.pending(),true);
 await t.click(null,null,true);
 assert.equal(t.evalJs('ui.guest'),false);
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.match(t.elements.content.innerHTML,/Iniciar sesión/);
 t.release();await pending;
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.doesNotMatch(t.elements.content.innerHTML,/Descriptores revisados/);
 onlyGet(t.requests);
});
