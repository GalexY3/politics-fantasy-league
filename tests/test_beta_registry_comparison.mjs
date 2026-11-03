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
const ENROLLED_PYCODE=[
 'import json,tempfile,sys',
 'from pathlib import Path',
 'from politics_fantasy.scientific_registry import enroll_synthetic_fixture,query_registry',
 'with tempfile.TemporaryDirectory(prefix="pfl-registry-guest-filter-") as folder:',
 '    db=Path(folder)/"fixture.sqlite3"',
 '    enroll_synthetic_fixture(db,"sandbox_alpha_v1")',
 '    result=query_registry(db,cut=sys.argv[1],valid_at=sys.argv[2],family=sys.argv[3],published_until=sys.argv[4])',
 '    print(json.dumps(result,ensure_ascii=False))'
].join('\n');
const enrolledCache=new Map();
function enrolledPythonRegistry(cut,validAt,family,published){
 const key=[cut,validAt,family,published].join('|');
 if(!enrolledCache.has(key)){
  enrolledCache.set(key,JSON.parse(execFileSync('python',
   ['-B','-c',ENROLLED_PYCODE,cut,validAt,family,published],
   {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:3*1024*1024,timeout:12000})));
 }
 return structuredClone(enrolledCache.get(key));
}
const lab=Object.fromEntries(['early','late'].map(cut=>[
 cut,JSON.parse(execFileSync('python',['-B','scripts/run_scientific_integration_lab.py','--cut',cut],
  {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:3*1024*1024,timeout:12000}))
]));

function harness({href='http://localhost/',scienceOnly=false,registrySource=pythonRegistry}={}){
 const elements={},listeners={},requests=[],downloads=[],blobs=[];
 const location={href};
 const historyWrites=[];
 const history={replaceState(state,title,path){
  historyWrites.push({state,title,path,requestCount:requests.length});
  location.href=new URL(path,location.href).href;
 }};
 const tabs=['overview','club','market','rounds','observatory','scientific','atlas','progress']
  .map(tab=>({dataset:{tab},hidden:false,classList:{toggle(){}},
   setAttribute(){},removeAttribute(){}}));
 let compareFail=null,rightsSpoof=false,badSha=false,holdNext=false,pending=null;
 let pauseDigest=false,pendingDigest=null,labFail=null,digestCalls=0;
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
   json:async()=>scienceOnly
    ?({authenticated:false,science_only:true,error:'LOCAL_SCIENCE_ONLY'})
    :({authenticated:false,error:'AUTH_REQUIRED'})};
  if(url.pathname==='/api/scientific-integration-lab'){
   if(labFail!==null)return{ok:false,status:labFail};
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
   const data=registrySource(cut,valid,family,publication);
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
 const crypto={subtle:{digest:(...args)=>{
  digestCalls++;
  if(!pauseDigest)return webcrypto.subtle.digest(...args);
  pauseDigest=false;
  return new Promise((resolve,reject)=>{
   pendingDigest=()=>webcrypto.subtle.digest(...args).then(resolve,reject);
  });
 }}};
 const context=createContext({document,fetch,URL:LocalURL,location,history,TextEncoder,Blob,crypto,
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
  elements,requests,downloads,blobs,evalJs,click,change,historyWrites,
  getHref:()=>location.href,
  digestCalls:()=>digestCalls,
  guest:async()=>{await evalJs('bootstrap()');if(!evalJs('ui.guest'))await click('guest-enter');},
  setFail(cut,status){compareFail={cut,status};},
  setLabFail(status){labFail=status;},
  setRightsSpoof(enabled){rightsSpoof=enabled;},
  setBadSha(enabled){badSha=enabled;},
  pauseNextDigest(){pauseDigest=true;},
  hasPendingDigest(){return Boolean(pendingDigest);},
  releaseDigest(){assert.ok(pendingDigest);const f=pendingDigest;pendingDigest=null;f();},
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
 await t.click('science-registry-pair-export');
 assert.equal(t.downloads.length,1);
 const output=JSON.parse(await t.blobs[0].text());
 assert.equal(output.exports.early.query.published_until,'2026-10-15T12:00:00Z');
 assert.equal(output.exports.late.query.published_until,'2026-10-30T12:00:00Z');
 onlyGet(t.requests);
});

test('paired export retains common nondefault valid_at and family without new source or account calls',async()=>{
 const t=harness();await t.guest();
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-family','CHAIN');
 await t.click('science-registry-tab','compare');
 await t.click('science-registry-pair-export');
 assert.equal(t.downloads.length,1);
 const pair=JSON.parse(await t.blobs[0].text());
 assert.equal(pair.exports.early.query.valid_at,'2026-10-10');
 assert.equal(pair.exports.late.query.valid_at,'2026-10-10');
 assert.equal(pair.exports.early.query.family,'CHAIN');
 assert.equal(pair.exports.late.query.family,'CHAIN');
 assert.equal(pair.exports.early.query.published_until,'2026-10-15T12:00:00Z');
 assert.equal(pair.exports.late.query.published_until,'2026-11-01T12:00:00Z');
 assert.equal(pair.exports.early.snapshot_receipt.sha256,
  createHash('sha256').update(pair.exports.early.snapshot_receipt.canonical_json,'utf8').digest('hex'));
 assert.equal(pair.pair_receipt.sha256,
  createHash('sha256').update(pair.pair_receipt.canonical_json,'utf8').digest('hex'));
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

test('PREPATCH RED S9 admission direct family filter distinguishes exclusion from zero global assessments',async()=>{
 const t=harness();await t.guest();
 await t.click('science-registry-tab','admission');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.admission_assessments.assessment_count'),8);
 assert.match(t.elements.content.innerHTML,/8 evaluaciones ficticias visibles/);
 await t.change('science-registry-family','CHAIN');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.admission_assessments.assessment_count'),0,
  'The author-closed family projection excludes all eight otherwise valid S9 assessments');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'admission');
 assert.match(t.elements.content.innerHTML,/Fuera del filtro de familia/,
  'Direct admission tab must disclose exclusion instead of reporting an empty global ledger');
 assert.doesNotMatch(t.elements.content.innerHTML,/\b0 evaluaciones ficticias visibles\b/);
 await t.change('science-registry-family','all');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.admission_assessments.assessment_count'),8);
 assert.match(t.elements.content.innerHTML,/8 evaluaciones ficticias visibles/);
 assert.equal(t.evalJs('ui.scienceRegistryError'),null);
 onlyGet(t.requests);
});

test('PREPATCH RED S9 intake direct family filter distinguishes excluded authored enrollment from zero registered globally',async()=>{
 const t=harness({registrySource:enrolledPythonRegistry});await t.guest();
 await t.click('science-registry-tab','intake');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.synthetic_intake.intake_count'),1);
 assert.match(t.elements.content.innerHTML,/1 incorporaciones ficticias registradas/);
 assert.match(t.elements.content.innerHTML,/S9:INTAKE_01/);
 await t.change('science-registry-family','CHAIN');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.synthetic_intake.intake_count'),0,
  'The actual SHA-verified CHAIN projection cannot include the authored overlay');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'intake');
 assert.match(t.elements.content.innerHTML,/Fuera del filtro de familia/,
  'Direct intake tab must not say zero global registrations or rejections');
 assert.doesNotMatch(t.elements.content.innerHTML,/\b0 incorporaciones ficticias registradas\b/);
 assert.doesNotMatch(t.elements.content.innerHTML,/\b0 rechazadas por controles internos\b/);
 await t.change('science-registry-family','all');
 assert.equal(t.evalJs('ui.scienceRegistry.snapshot.synthetic_intake.intake_count'),1);
 assert.match(t.elements.content.innerHTML,/1 incorporaciones ficticias registradas/);
 assert.equal(t.evalJs('ui.scienceRegistryError'),null);
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

const guestLink=(values={})=>{
 const entries=[
  ['pfl_guest','v1'],['cut','late'],['valid_at','2026-09-15'],
  ['family','all'],['published_until','as_of'],
  ['scenario','baseline'],['view','sources']
 ];
 const query=new URLSearchParams(entries);
 for(const [name,value] of Object.entries(values))query.set(name,value);
 return 'http://localhost/?'+query.toString();
};

for(const [view,panelText] of [
 ['admission','Historial sintético'],
 ['intake','Control sandbox']
]){
 test('PREPATCH RED guest bookmarked S9 '+view+' panel survives reboot',async()=>{
  const original=harness();
  await original.guest();
  await original.click('science-registry-tab',view);
  assert.equal(original.evalJs('ui.scienceRegistryTab'),view);
  assert.match(original.elements.content.innerHTML,new RegExp(panelText));
  assert.equal(original.getHref(),guestLink({view}),
   'selected public S9 subview must be mirrored into the seven-field URL');
  const restored=harness({href:original.getHref(),scienceOnly:true});
  await restored.guest();
  assert.equal(restored.evalJs('ui.scienceRegistryTab'),view);
  assert.match(restored.elements.content.innerHTML,new RegExp(panelText));
  assert.equal(restored.digestCalls(),1,'reload verifies fresh S9, not URL evidence');
  onlyGet(restored.requests);
 });
}

for(const [view,panelText] of [
 ['chain','relaciones explícitas del mismo emisor'],
 ['chronicle','relaciones explícitas del mismo emisor'],
 ['episodes','Censura derecha independiente'],
 ['admission','Historial sintético'],
 ['intake','Control sandbox'],
 ['quality','Migración del esquema']
]){
 test('guest S9 '+view+' subview survives reload and independent science-only reboot',async()=>{
  const selected=harness();
  await selected.guest();
  const originalRegistryQueries=selected.registryQueries();
  await selected.click('science-registry-tab',view);
  assert.equal(selected.evalJs('ui.scienceRegistryTab'),view);
  assert.match(selected.elements.content.innerHTML,new RegExp(panelText));
  assert.equal(selected.getHref(),guestLink({view}));
  assert.equal(selected.registryQueries(),originalRegistryQueries,
   'Selecting a verified S9 subview needs no new GET');
  assert.equal(selected.evalJs('ui.scienceRegistryComparison'),null,
   'Only compare requires independently verified early and late projections');
  const shaCalls=selected.digestCalls();
  await selected.click('guest-reload');
  assert.equal(selected.evalJs('ui.scienceRegistryTab'),view);
  assert.match(selected.elements.content.innerHTML,new RegExp(panelText));
  assert.equal(selected.digestCalls(),shaCalls+1,
   'Guest retry verifies a fresh single S9 SHA receipt');
  assert.equal(selected.getHref(),guestLink({view}));
  const restored=harness({href:selected.getHref(),scienceOnly:true});
  await restored.guest();
  assert.equal(restored.evalJs('ui.scienceRegistryTab'),view);
  assert.match(restored.elements.content.innerHTML,new RegExp(panelText));
  assert.equal(restored.evalJs('ui.scienceRegistryError'),null);
  assert.equal(restored.evalJs('ui.scienceRegistryComparison'),null);
  assert.equal(restored.digestCalls(),1,'New browser reload never trusts URL as evidence');
  assert.equal(restored.registryQueries(),1,
   'Exactly one current S9 projection GET for a non-comparison subview');
  assert.equal(restored.getHref(),guestLink({view}));
  assert.equal(restored.historyWrites[0].requestCount,1,
   'The restored selection precedes every scientific GET');
  onlyGet(selected.requests);
  onlyGet(restored.requests);
 });
}

test('guest mirrors exact allowlisted selection as a reproducible, credential-free URL',async()=>{
 const t=harness();await t.guest();
 await t.change('science-cut','early');
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-family','CHAIN');
 await t.change('science-registry-publication','2026-09-19T12:00:00Z');
 await t.change('science-scenario','privacy_probe');
 await t.click('science-registry-tab','compare');
 const expected=guestLink({
  cut:'early',valid_at:'2026-10-10',family:'CHAIN',
  published_until:'2026-09-19T12:00:00Z',
  scenario:'privacy_probe',view:'compare'
 });
 assert.equal(t.getHref(),expected);
 assert.ok(t.historyWrites.length>=7);
 assert.ok(t.historyWrites.every(x=>x.state===null&&x.title===''));
 const params=[...new URL(t.getHref()).searchParams];
 assert.deepEqual(params.map(([k])=>k),
  ['pfl_guest','cut','valid_at','family','published_until','scenario','view']);
 assert.doesNotMatch(t.getHref(),/username|password|csrf|token|S9:PUBLIC|snapshot_receipt/);
 assert.equal(t.evalJs('ui.scienceRegistryComparison.early.cut'),'early');
 assert.equal(t.evalJs('ui.scienceRegistryComparison.late.cut'),'late');
 onlyGet(t.requests);
});

test('reloaded science-only URL restores filters BEFORE GET then verifies current and both comparison SHA afresh',async()=>{
 const url=guestLink({
  cut:'early',valid_at:'2026-10-10',family:'CHAIN',
  published_until:'2026-09-19T12:00:00Z',
  scenario:'privacy_probe',view:'compare'
 });
 const t=harness({href:url,scienceOnly:true});
 t.pauseNextDigest();
 const opening=t.evalJs('bootstrap()');
 for(let i=0;i<100&&!t.hasPendingDigest();i++)await new Promise(setImmediate);
 assert.equal(t.hasPendingDigest(),true,'A fresh WebCrypto verification must occur after network GET');
 assert.equal(t.evalJs('ui.scienceRegistry'),null,'No S9 result visible while SHA unresolved');
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null,'URL never supplies a trusted pair');
 t.releaseDigest();
 await opening;
 assert.equal(t.evalJs('ui.guest'),true);
 assert.equal(t.evalJs('ui.scienceCut'),'early');
 assert.equal(t.evalJs('ui.scienceScenario'),'privacy_probe');
 assert.equal(t.evalJs('ui.scienceRegistryValid'),'2026-10-10');
 assert.equal(t.evalJs('ui.scienceRegistryFamily'),'CHAIN');
 assert.equal(t.evalJs('ui.scienceRegistryPublished'),'2026-09-19T12:00:00Z');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'compare');
 assert.ok(t.evalJs('ui.scienceRegistryComparison'));
 assert.equal(t.digestCalls(),3,'Current S9 + independently verified early/late');
 assert.equal(t.historyWrites[0].requestCount,1,
  'Only anonymous /api/session occurs before URL has been normalized');
 const scienceRequests=t.requests.filter(x=>x.route.includes('/api/scientific-'));
 assert.equal(scienceRequests.length,4,'S8, current S9, both comparison S9 cuts');
 assert.ok(scienceRequests[0].route.includes('cut=early'));
 for(const req of scienceRequests.filter(x=>x.route.startsWith('/api/scientific-registry'))){
  const query=new URL(req.route,'http://localhost').searchParams;
  assert.equal(query.get('valid_at'),'2026-10-10');
  assert.equal(query.get('family'),'CHAIN');
 }
 assert.equal(t.getHref(),url);
 assert.match(t.elements.content.innerHTML,/Comparar cortes/);
 onlyGet(t.requests);
});

test('explicit visitor entry restores the canonical link without account/session APIs',async()=>{
 const url=guestLink({cut:'late',family:'CHRONICLE',
  published_until:'2026-10-30T12:00:00Z',view:'sources'});
 const t=harness({href:url});
 await t.evalJs('bootstrap()');
 assert.equal(t.evalJs('ui.guest'),false);
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.equal(t.historyWrites.length,0,'Account login view does not consume URL');
 assert.equal(t.getHref(),url);
 assert.equal(t.requests.length,1);
 await t.click('guest-enter');
 assert.equal(t.evalJs('ui.guest'),true);
 assert.equal(t.evalJs('ui.scienceCut'),'late');
 assert.equal(t.evalJs('ui.scienceRegistryFamily'),'CHRONICLE');
 assert.equal(t.evalJs('ui.scienceRegistryPublished'),'2026-10-30T12:00:00Z');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'sources');
 assert.equal(t.evalJs('ui.scienceRegistry.family'),'CHRONICLE');
 assert.equal(t.evalJs('ui.scienceRegistry.published_until'),'2026-10-30T12:00:00Z');
 assert.equal(t.digestCalls(),1,'Single fresh S9 receipt, not cached URL data');
 assert.equal(t.requests.filter(x=>x.route.startsWith('/api/scientific-registry')).length,1);
 assert.equal(t.getHref(),url);
 onlyGet(t.requests);
});

const canonicalGuestUrl=guestLink({view:'compare'});
const invalidGuestUrls=[
 ['duplicate cut',canonicalGuestUrl+'&cut=early'],
 ['unknown field',canonicalGuestUrl+'&username=IGNORED_CANARY'],
 ['malformed percent',canonicalGuestUrl.replace('cut=late','cut=%ZZ')],
 ['trailing separator',canonicalGuestUrl+'&'],
 ['empty separator',canonicalGuestUrl.replace('&family=all','&&family=all')],
 ['wrong marker',canonicalGuestUrl.replace('pfl_guest=v1','pfl_guest=v2')],
 ['unknown registry subview',guestLink({view:'private_account'})],
 ['subview with encoded control',guestLink({view:'admission\nsource_id'})],
 ['invalid scenario',canonicalGuestUrl.replace('scenario=baseline','scenario=rights_unknown')],
 ['missing field',canonicalGuestUrl.replace('&view=compare','')],
 ['unallowlisted date',canonicalGuestUrl.replace('valid_at=2026-09-15','valid_at=2026-12-20')],
 ['future early publication',guestLink({cut:'early',
  published_until:'2026-10-30T12:00:00Z',view:'compare'})],
 ['oversized query',canonicalGuestUrl+'&x='+'z'.repeat(700)],
 ['SHA masquerading as selector',canonicalGuestUrl+'&sha256='+'f'.repeat(64)]
];
for(const [label,href] of invalidGuestUrls){
 test('invalid guest URL '+label+' fails closed without any S8/S9 GET and offers explicit reset',async()=>{
  const t=harness({href,scienceOnly:true});
  await t.guest();
  assert.equal(t.evalJs('ui.guest'),true);
  assert.equal(t.evalJs('ui.scientific'),null);
  assert.equal(t.evalJs('ui.scienceRegistry'),null);
  assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
  assert.match(t.elements.content.innerHTML,/Selección científica de URL rechazada/);
  assert.match(t.elements.content.innerHTML,/Restablecer consulta/);
  assert.equal(t.requests.length,1,'Only /api/session, no scientific data leaked');
  assert.equal(t.historyWrites.length,0,'Reject URL without silently normalizing it');
  await t.click('guest-reload');
  assert.equal(t.requests.length,1,'Retry cannot bypass invalid URL gate');
  await t.click('guest-url-reset');
  assert.equal(t.evalJs('ui.guestUrlError'),null);
  assert.ok(t.evalJs('ui.scientific'));
  assert.ok(t.evalJs('ui.scienceRegistry'));
  assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
  assert.equal(t.getHref(),guestLink());
  assert.equal(t.evalJs('ui.scienceRegistryTab'),'sources');
  assert.ok(t.digestCalls()>=1);
  onlyGet(t.requests);
 });
}

test('changing to early cut from late-publication selection normalizes URL before any new GET',async()=>{
 const t=harness();await t.guest();
 await t.change('science-registry-publication','2026-10-30T12:00:00Z');
 assert.equal(new URL(t.getHref()).searchParams.get('published_until'),'2026-10-30T12:00:00Z');
 await t.change('science-cut','early');
 assert.equal(t.evalJs('ui.scienceRegistryPublished'),'as_of');
 assert.equal(t.getHref(),guestLink({cut:'early'}));
 assert.equal(t.evalJs('ui.scienceRegistry.cut'),'early');
 onlyGet(t.requests);
});

test('an established Fantasy account never interprets or overwrites a hostile guest URL',async()=>{
 const url=canonicalGuestUrl+'&username=ACCOUNT_CANARY';
 const t=harness({href:url});
 t.evalJs("ui.state={clubs:[{id:'demo',name:'demo'}]};ui.session='existing-account'");
 await t.evalJs('enterGuest()');
 assert.equal(t.evalJs('ui.guest'),false);
 assert.equal(t.evalJs('ui.guestUrlError'),null);
 t.evalJs('mirrorGuestUrlSelection()');
 assert.equal(t.getHref(),url);
 assert.equal(t.historyWrites.length,0);
 assert.equal(t.requests.length,0);
 assert.equal(t.evalJs('ui.session'),'existing-account');
});

test('an authenticated Fantasy session cannot consume a valid public admission subview link',async()=>{
 const url=guestLink({view:'admission',family:'CHAIN'});
 const t=harness({href:url});
 await t.evalJs('bootstrap()');
 assert.equal(t.evalJs('ui.guest'),false);
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'sources');
 t.evalJs("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.session='account-existing'");
 await t.evalJs('enterGuest()');
 t.evalJs('mirrorGuestUrlSelection()');
 assert.equal(t.evalJs('ui.guest'),false);
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'sources');
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.equal(t.getHref(),url);
 assert.equal(t.historyWrites.length,0);
 assert.equal(t.requests.length,1,'Authenticated Fantasy never loads scientific URL in guest mode');
});

test('reentering guest with spoofed view fail-closes an earlier validated admission panel',async()=>{
 const t=harness({scienceOnly:true});
 await t.guest();
 await t.click('science-registry-tab','admission');
 assert.match(t.elements.content.innerHTML,/Historial sintético/);
 const priorRequests=t.requests.length;
 t.evalJs('location.href='+JSON.stringify(guestLink({view:'secret_actor_graph'})));
 await t.evalJs('enterGuest()');
 assert.equal(t.requests.length,priorRequests,
  'Invalid subview does not request S8/S9 nor reuse old SHA-verified data');
 assert.equal(t.evalJs('ui.guestUrlError')!==null,true);
 assert.equal(t.evalJs('ui.scientific'),null);
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.match(t.elements.content.innerHTML,/Restablecer consulta/);
 assert.doesNotMatch(t.elements.content.innerHTML,/Historial sintético/);
 await t.click('guest-url-reset');
 assert.equal(t.evalJs('ui.guestUrlError'),null);
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'sources');
 assert.equal(t.getHref(),guestLink());
 onlyGet(t.requests);
});

for(const endpoint of ['registry','lab']){
 test('restored comparison retains selected URL through '+endpoint+' HTTP503 and verifies fresh data on retry',async()=>{
  const url=guestLink({view:'compare',family:'CHAIN'});
  const t=harness({href:url,scienceOnly:true});
  if(endpoint==='registry')t.setFail('late',503);
  else t.setLabFail(503);
  await t.guest();
  assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
  assert.equal(t.evalJs('ui.scienceRegistry'),null);
  assert.match(t.elements.content.innerHTML,/Reintentar consulta/);
  assert.equal(t.getHref(),url);
  t.setFail(null,null);
  t.setLabFail(null);
  const before=t.digestCalls();
  await t.click('guest-reload');
  assert.equal(t.evalJs('ui.guestUrlError'),null);
  assert.equal(t.evalJs('ui.scienceRegistryTab'),'compare');
  assert.ok(t.evalJs('ui.scienceRegistryComparison'));
  assert.ok(t.digestCalls()>=before+3);
  assert.equal(t.getHref(),url);
  onlyGet(t.requests);
 });
}

test('restored in-flight comparison A→B→A cannot republish stale data despite identical final URL',async()=>{
 const url=guestLink({view:'compare'});
 const t=harness({href:url,scienceOnly:true});
 t.holdNextEarly();
 const opening=t.evalJs('bootstrap()');
 for(let i=0;i<100&&!t.pending();i++)await new Promise(setImmediate);
 assert.equal(t.pending(),true,'Early comparison GET must be pending');
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-valid','2026-09-15');
 assert.equal(t.getHref(),url);
 t.release();await opening;
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 assert.ok(t.evalJs('ui.scienceRegistry'));
 await t.click('science-registry-compare-load');
 assert.ok(t.evalJs('ui.scienceRegistryComparison'),'User-initiated fresh query can now succeed');
 assert.equal(t.getHref(),url);
 onlyGet(t.requests);
});

test('restored admission subview forbids a stale S9 download across valid_at A→B→A',async()=>{
 const url=guestLink({view:'admission'});
 const t=harness({href:url,scienceOnly:true});
 await t.guest();
 assert.match(t.elements.content.innerHTML,/Historial sintético/);
 t.pauseNextDigest();
 const pending=t.click('science-registry-export');
 assert.equal(t.hasPendingDigest(),true,'Single S9 export awaits WebCrypto');
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-valid','2026-09-15');
 assert.equal(t.getHref(),url,'A→B→A returns to identical public bookmark');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'admission');
 assert.match(t.elements.content.innerHTML,/Historial sintético/);
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.blobs.length,0);
 assert.ok(t.evalJs('ui.scienceRegistry'));
 assert.equal(t.evalJs('ui.scienceRegistryComparison'),null);
 onlyGet(t.requests);
});

test('restored episodes subview fails closed during HTTP503 with pending single-export SHA',async()=>{
 const url=guestLink({view:'episodes'});
 const t=harness({href:url,scienceOnly:true});
 await t.guest();
 assert.match(t.elements.content.innerHTML,/Censura derecha independiente/);
 t.pauseNextDigest();
 const pending=t.click('science-registry-export');
 assert.equal(t.hasPendingDigest(),true);
 t.setFail('late',503);
 await t.click('science-registry-load');
 assert.equal(t.evalJs('ui.scienceRegistry'),null);
 assert.match(t.evalJs('ui.scienceRegistryError'),/503/);
 assert.doesNotMatch(t.elements.content.innerHTML,/Censura derecha independiente/);
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.blobs.length,0);
 assert.equal(t.getHref(),url);
 t.setFail(null,null);
 const previousSha=t.digestCalls();
 await t.click('guest-reload');
 assert.equal(t.evalJs('ui.scienceRegistryTab'),'episodes');
 assert.match(t.elements.content.innerHTML,/Censura derecha independiente/);
 assert.equal(t.evalJs('ui.scienceRegistryError'),null);
 assert.ok(t.digestCalls()>previousSha,'Retry requires fresh SHA');
 assert.equal(t.getHref(),url);
 onlyGet(t.requests);
});

test('view compare→admission→compare rejects stale in-flight pair download despite identical link',async()=>{
 const url=guestLink({view:'compare'});
 const t=harness({href:url,scienceOnly:true});
 await t.guest();
 assert.ok(t.evalJs('ui.scienceRegistryComparison'));
 t.pauseNextDigest();
 const pending=t.click('science-registry-pair-export');
 assert.equal(t.hasPendingDigest(),true);
 await t.click('science-registry-tab','admission');
 assert.equal(t.getHref(),guestLink({view:'admission'}));
 assert.match(t.elements.content.innerHTML,/Historial sintético/);
 await t.click('science-registry-tab','compare');
 assert.equal(t.getHref(),url);
 assert.ok(t.evalJs('ui.scienceRegistryComparison'),
  'Current compare view must fetch a new independently verified pair');
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.blobs.length,0);
 onlyGet(t.requests);
});

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

test('guest downloads exactly one canonical SHA-256 paired S9 receipt with both original single-export schemas',async()=>{
 const t=harness();await t.guest();await t.click('science-registry-tab','compare');
 assert.match(t.elements.content.innerHTML,/data-action="science-registry-pair-export"/);
 await t.click('science-registry-pair-export');
 assert.equal(t.downloads.length,1);
 assert.equal(t.blobs.length,1);
 const pair=JSON.parse(await t.blobs[0].text());
 assert.deepEqual(Object.keys(pair).sort(),[
  'R5','comparison_kind','evidence_class','exports','external_authenticity_certified',
  'pair_receipt','release_gates_passed','rights_for_public_display_admitted',
  'schema','scientific_ab_cycles'].sort());
 assert.equal(pair.schema,'pfl.synthetic_scientific_registry_browser_pair_export.v1');
 assert.equal(pair.evidence_class,'SYNTHETIC_LAB_ONLY');
 assert.equal(pair.comparison_kind,'AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE');
 assert.equal(pair.R5,'STOP_R5');
 assert.equal(pair.scientific_ab_cycles,0);
 assert.equal(pair.release_gates_passed,0);
 assert.equal(pair.rights_for_public_display_admitted,false);
 assert.equal(pair.external_authenticity_certified,false);
 assert.deepEqual(Object.keys(pair.exports).sort(),['early','late']);
 for(const cut of ['early','late']){
  const nested=pair.exports[cut];
  assert.deepEqual(Object.keys(nested).sort(),[
   'R5','evidence_class','external_authenticity_certified','query',
   'receipt_schema','release_gates_passed','rights_for_public_display_admitted',
   'schema','scientific_ab_cycles','snapshot_receipt','source_contract'
  ].sort());
  assert.equal(nested.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(nested.query.cut,cut);
  assert.equal(nested.query.valid_at,'2026-09-15');
  assert.equal(nested.query.family,'all');
  assert.equal(nested.query.as_of,cut==='early'?'2026-10-15T12:00:00Z':'2026-11-01T12:00:00Z');
  assert.equal(nested.rights_for_public_display_admitted,false);
  const receipt=nested.snapshot_receipt;
  assert.equal(receipt.sha256,createHash('sha256').update(receipt.canonical_json,'utf8').digest('hex'));
  assert.equal(Buffer.byteLength(receipt.canonical_json,'utf8'),receipt.bytes);
 }
 assert.equal(pair.pair_receipt.schema,'pfl.synthetic_scientific_registry_browser_pair_receipt.v1');
 assert.equal(pair.pair_receipt.canonicalization,'JSON_UTF8_SORTED_KEYS_COMPACT_V1');
 assert.equal(pair.pair_receipt.sha256,
  createHash('sha256').update(pair.pair_receipt.canonical_json,'utf8').digest('hex'));
 assert.equal(pair.pair_receipt.bytes,Buffer.byteLength(pair.pair_receipt.canonical_json,'utf8'));
 const canonical=JSON.stringify(Object.fromEntries(Object.entries(pair)
  .filter(([k])=>k!=='pair_receipt').sort(([a],[b])=>a.localeCompare(b))),
  (_k,v)=>v&&!Array.isArray(v)&&typeof v==='object'
   ?Object.fromEntries(Object.keys(v).sort().map(k=>[k,v[k]])):v);
 assert.equal(pair.pair_receipt.canonical_json,canonical);
 assert.match(t.downloads[0],new RegExp('^pfl-s9-pair-2026-09-15-'+pair.pair_receipt.sha256.slice(0,12)+'\\.json$'));
 onlyGet(t.requests);
 assert.equal(t.evalJs('ui.state'),null);
 assert.equal(t.evalJs('ui.session'),null);
});

test('authenticated comparison also downloads pair without any account API request',async()=>{
 const t=harness();
 t.evalJs("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.tab='scientific'");
 await t.evalJs('loadScientific()');
 await t.evalJs('loadScientificRegistry()');
 await t.click('science-registry-tab','compare');
 await t.click('science-registry-pair-export');
 assert.equal(t.downloads.length,1);
 assert.equal(JSON.parse(await t.blobs[0].text()).exports.late.query.cut,'late');
 onlyGet(t.requests);
});

for(const mode of ['rights','receipt']){
 test('pair export refuses '+mode+' spoofed previously loaded projection',async()=>{
  const t=harness();await t.guest();await t.click('science-registry-tab','compare');
  t.evalJs(mode==='rights'
   ?'ui.scienceRegistryComparison.early.registry.distributions[0].rights_for_public_display=true'
   :'ui.scienceRegistryComparison.early.snapshot_receipt.sha256="0".repeat(64)');
  await t.click('science-registry-pair-export');
  assert.equal(t.downloads.length,0);
  assert.equal(t.blobs.length,0);
  assert.match(t.elements.toast.textContent,/bloqueada/);
  onlyGet(t.requests);
 });
}

for(const [name,modify] of [
 ['cut',t=>t.change('science-cut','early')],
 ['valid_at',t=>t.change('science-registry-valid','2026-10-10')],
 ['family',t=>t.change('science-registry-family','CHAIN')],
 ['publication',t=>t.change('science-registry-publication','2026-09-19T12:00:00Z')],
 ['first_public',t=>t.change('science-first-public','2026-09-19T12:00:00Z')]
]){
 test('pair export in-flight is invalidated by '+name+' change',async()=>{
  const t=harness();
  if(name==='first_public'){
   t.evalJs("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.tab='scientific'");
   await t.evalJs('loadScientific()');
   await t.evalJs('loadScientificRegistry()');
  }else await t.guest();
  await t.click('science-registry-tab','compare');
  t.pauseNextDigest();
  const pending=t.click('science-registry-pair-export');
  assert.equal(t.hasPendingDigest(),true);
  await modify(t);
  t.releaseDigest();await pending;
  assert.equal(t.downloads.length,0);
  assert.equal(t.blobs.length,0);
  onlyGet(t.requests);
 });
}

test('pair export pending SHA is rejected after filter A→B→A even when rebuilt current snapshot is valid',async()=>{
 const t=harness();await t.guest();await t.click('science-registry-tab','compare');
 t.pauseNextDigest();
 const pending=t.click('science-registry-pair-export');
 assert.equal(t.hasPendingDigest(),true);
 await t.change('science-registry-valid','2026-10-10');
 await t.change('science-registry-valid','2026-09-15');
 await t.click('science-registry-compare-load');
 assert.ok(t.evalJs('ui.scienceRegistryComparison'));
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.blobs.length,0);
 onlyGet(t.requests);
});

for(const kind of ['registry503','lab503','logout']){
 test('in-flight verified pair is invalidated by '+kind,async()=>{
  const t=harness();await t.guest();await t.click('science-registry-tab','compare');
  t.pauseNextDigest();
  const pending=t.click('science-registry-pair-export');
  assert.equal(t.hasPendingDigest(),true);
  if(kind==='registry503'){
   t.setFail('late',503);
   await t.click('science-registry-load');
   assert.match(t.evalJs('ui.scienceRegistryError'),/503/);
  }else if(kind==='lab503'){
   t.setLabFail(503);
   await t.click('guest-reload');
   assert.match(t.evalJs('ui.scientificError'),/503/);
  }else{
   await t.click(null,null,true);
   assert.equal(t.evalJs('ui.guest'),false);
  }
  t.releaseDigest();await pending;
  assert.equal(t.downloads.length,0);
  assert.equal(t.blobs.length,0);
  onlyGet(t.requests);
 });
}
