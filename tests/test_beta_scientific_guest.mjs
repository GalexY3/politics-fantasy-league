import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash,webcrypto} from 'node:crypto';
import {createContext,runInContext} from 'node:vm';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../',import.meta.url));
const script=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const pythonEnv={...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'};
function fixtures(){
 const lab={},registry={};
 const code=[
  'import json,tempfile,sys',
  'from pathlib import Path',
  'from politics_fantasy.scientific_registry import query_registry',
  'with tempfile.TemporaryDirectory(prefix="pfl-guest-vm-") as folder:',
  '    print(json.dumps(query_registry(Path(folder)/"fixture.sqlite3",cut=sys.argv[1],valid_at=sys.argv[2],family=sys.argv[3],published_until=sys.argv[4]),ensure_ascii=False))'
 ].join('\n');
 const query=(cut,valid='2026-09-15',family='all',published='as_of')=>
  JSON.parse(execFileSync('python',['-B','-c',code,cut,valid,family,published],
   {cwd:root,env:pythonEnv,encoding:'utf8',maxBuffer:2*1024*1024}));
 const key=(cut,valid='2026-09-15',family='all',published='as_of')=>
  [cut,valid,family,published].join('|');
 for(const cut of ['early','late']){
  lab[cut]=JSON.parse(execFileSync('python',['-B','scripts/run_scientific_integration_lab.py','--cut',cut],
   {cwd:root,env:pythonEnv,encoding:'utf8',maxBuffer:2*1024*1024}));
  registry[key(cut)]=query(cut);
 }
 registry[key('late','2026-10-10')]=query('late','2026-10-10');
 registry[key('late','2026-09-15','CHAIN')]=query('late','2026-09-15','CHAIN');
 registry[key('late','2026-09-15','all','2026-09-19T12:00:00Z')]=
  query('late','2026-09-15','all','2026-09-19T12:00:00Z');
 return {lab,registry,key};
}
const originals=fixtures();

function setup({scienceOnly=false}={}){
 const elements={},listeners={},requests=[],downloads=[],blobs=[];
 const tabs=['overview','club','market','rounds','observatory','scientific','atlas','progress']
  .map(tab=>({dataset:{tab},hidden:false,classList:{toggle(){}},setAttribute(){},removeAttribute(){}}));
 let labStatus=200,registryStatus=200,corruptRegistry=false;
 let delayNextDigest=false,pendingDigest=null;
 class LocalURL extends URL {}
 LocalURL.createObjectURL=blob=>{blobs.push(blob);return 'blob:verified-synthetic-s9';};
 LocalURL.revokeObjectURL=()=>{};
 const crypto={subtle:{digest:(...args)=>{
  if(!delayNextDigest)return webcrypto.subtle.digest(...args);
  delayNextDigest=false;
  return new Promise((resolve,reject)=>{
   pendingDigest=()=>webcrypto.subtle.digest(...args).then(resolve,reject);
  });
 }}};
 const doc={
  getElementById(id){return elements[id]??={innerHTML:'',textContent:'',hidden:false,addEventListener(){}};},
  querySelectorAll(selector){return selector==='[data-tab]'?tabs:[];},
  addEventListener(type,fn){listeners[type]=fn;},
  createElement(){return {click(){downloads.push(this.download);},remove(){}};},
  body:{appendChild(){}}
 };
 const fetch=async (route,options={})=>{
  requests.push({route,method:options.method||'GET'});
  const u=new URL(route,'http://localhost');
  if(u.pathname==='/api/session')return {ok:false,status:401,
   json:async()=>scienceOnly?{authenticated:false,science_only:true,error:'LOCAL_SCIENCE_ONLY'}
    :{authenticated:false,error:'AUTH_REQUIRED'}};
  const cut=u.searchParams.get('cut')||'late';
  if(u.pathname==='/api/scientific-integration-lab'){
   if(labStatus!==200)return {ok:false,status:labStatus};
   const report=structuredClone(originals.lab[cut]);
   report.scenario=u.searchParams.get('scenario')||'baseline';
   return {ok:true,json:async()=>report};
  }
  if(u.pathname==='/api/scientific-registry'){
   if(registryStatus!==200)return {ok:false,status:registryStatus};
   const key=originals.key(cut,u.searchParams.get('valid_at')||'2026-09-15',
    u.searchParams.get('family')||'all',u.searchParams.get('published_until')||'as_of');
   const fixture=originals.registry[key];
   if(!fixture)throw Error('Unprepared real SQLite synthetic query: '+key);
   const data=structuredClone(fixture);
   if(corruptRegistry)data.snapshot_receipt.sha256='0'.repeat(64);
   return {ok:true,json:async()=>data};
  }
  throw Error('Guest made a forbidden request: '+route);
 };
 const context=createContext({document:doc,fetch,URL:LocalURL,TextEncoder,Blob,crypto,
  Intl,Date,Number,String,Error,console,setTimeout(){},clearTimeout(){}});
 runInContext(script.slice(0,script.lastIndexOf('bootstrap().catch')),context);
 const click=(action,tab,exitGuest=false)=>listeners.click({target:{closest(selector){
  if(selector==='#guest-exit'&&exitGuest)return {};
  if(selector==='[data-nav],[data-tab]'&&tab)return {dataset:{tab}};
  if(selector==='[data-action]'&&action)return {dataset:{action}};
  return null;
 }}});
 const value=expression=>runInContext(expression,context);
 const change=(id,value)=>listeners.change({target:{id,value}});
 return {elements,listeners,tabs,requests,downloads,blobs,click,change,value,
  pauseNextDigest(){delayNextDigest=true;},
  hasPendingDigest(){return Boolean(pendingDigest);},
  releaseDigest(){assert.ok(pendingDigest,'Expected an in-flight WebCrypto digest');
   const release=pendingDigest;pendingDigest=null;release();},
  setLabStatus(n){labStatus=n;},setRegistryStatus(n){registryStatus=n;},
  setCorruptRegistry(n){corruptRegistry=n;}};
}

test('visitor enters from unauthorized session and sees S9 public registry with no game calls',async()=>{
 const t=setup();
 await t.value('bootstrap()');
 assert.match(t.elements.content.innerHTML,/Entrar al Observatorio y Laboratorio/);
 assert.equal(t.elements.navigation.hidden,true);
 assert.equal(t.elements['club-select'].hidden,true);
 await t.click('guest-enter');
 assert.equal(t.value('ui.guest'),true);
 assert.equal(t.value('ui.state'),null);
 assert.equal(t.value('ui.session'),null);
 assert.equal(t.value('ui.csrf'),null);
 assert.equal(t.elements.navigation.hidden,false);
 assert.equal(t.elements['guest-exit'].hidden,false);
 assert.equal(t.elements['account-logout'].hidden,true);
 assert.equal(t.elements['club-select'].hidden,true);
 assert.ok(t.tabs.filter(x=>!x.hidden).every(x=>['observatory','scientific'].includes(x.dataset.tab)));
 assert.match(t.elements.content.innerHTML,/Registro persistente de fuentes y relaciones/);
 assert.match(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 assert.match(t.elements.content.innerHTML,/science-registry-export/);
 assert.deepEqual(t.requests.map(x=>new URL(x.route,'http://localhost').pathname),[
  '/api/session','/api/scientific-integration-lab','/api/scientific-registry']);
 assert.ok(t.requests.every(x=>x.method==='GET'));
 await t.click(null,'scientific');
 assert.match(t.elements.content.innerHTML,/Testigos diferenciales sintéticos/);
 assert.match(t.elements.content.innerHTML,/B0 y B3/);
 assert.doesNotMatch(t.elements.content.innerHTML,/science-export|science-probe/);
 assert.equal(t.requests.length,3);
 await t.click(null,'club');
 assert.equal(t.value('ui.tab'),'scientific');
 assert.equal(t.requests.length,3);
 await t.click('science-export');
 await t.click('science-probe');
 await t.click('science-registry-export');
 assert.equal(t.requests.length,3);
 assert.equal(t.downloads.length,0);
 await t.click(null,null,true);
 assert.equal(t.value('ui.guest'),false);
 assert.equal(t.elements.navigation.hidden,true);
 assert.match(t.elements.content.innerHTML,/Iniciar sesión/);
 assert.equal(t.elements['guest-exit'].hidden,true);
});

test('science-only HTTP 401 starts verified anonymous guest automatically, normal 401 retains login',async()=>{
 const science=setup({scienceOnly:true});
 await science.value('bootstrap()');
 assert.equal(science.value('ui.guest'),true);
 assert.equal(science.value('ui.scienceOnly'),true);
 assert.equal(science.value('ui.state'),null);
 assert.equal(science.value('ui.session'),null);
 assert.match(science.elements.content.innerHTML,/S9:PUBLIC_01/);
 assert.doesNotMatch(science.elements.content.innerHTML,/auth-form/);
 assert.equal(science.elements['guest-exit'].hidden,true,
  'Science-only cannot offer login/register, so it must not expose a return-to-login button');
 assert.ok(science.requests.every(x=>x.method==='GET'&&
  ['/api/session','/api/scientific-integration-lab','/api/scientific-registry']
   .includes(new URL(x.route,'http://localhost').pathname)));
 await science.click('science-registry-export');
 assert.equal(science.downloads.length,1);
 await science.click(null,null,true);
 assert.equal(science.value('ui.guest'),true);
 assert.doesNotMatch(science.elements.content.innerHTML,/Iniciar sesión|Crear cuenta/);
 const normal=setup();await normal.value('bootstrap()');
 assert.equal(normal.value('ui.guest'),false);
 assert.equal(normal.value('ui.scienceOnly'),false);
 assert.match(normal.elements.content.innerHTML,/auth-form/);
 assert.equal(normal.requests.length,1);
});

test('503 from either science endpoint erases prior guest results and offers retry',async()=>{
 const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
 assert.match(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 t.setRegistryStatus(503);
 await t.click('guest-reload');
 assert.match(t.elements.content.innerHTML,/Registro persistente rechazado \(HTTP 503\)/);
 assert.doesNotMatch(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 assert.equal(t.value('ui.scienceRegistry'),null);
 t.setRegistryStatus(200);t.setLabStatus(503);
 await t.click('guest-reload');
 assert.match(t.elements.content.innerHTML,/Contrato HTTP 503/);
 assert.doesNotMatch(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 assert.equal(t.value('ui.scientific'),null);
 assert.ok(t.requests.every(x=>x.method==='GET'));
});

test('a changed public SHA receipt is rejected and no old registry is rendered',async()=>{
 const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
 assert.match(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 t.setCorruptRegistry(true);
 await t.click('guest-reload');
 assert.equal(t.value('ui.scienceRegistry'),null);
 assert.match(t.elements.content.innerHTML,/SHA de recibo incompatible/);
 assert.doesNotMatch(t.elements.content.innerHTML,/S9:PUBLIC_01/);
 await t.click(null,'scientific');
 assert.doesNotMatch(t.elements.content.innerHTML,/Testigos diferenciales sintéticos/);
});

test('guest exports the exact S9 canonical SHA receipt without state, POST or S8 export',async()=>{
 const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
 assert.match(t.elements.content.innerHTML,/data-action="science-registry-export"/);
 await t.click('science-registry-export');
 assert.equal(t.downloads.length,1);
 assert.equal(t.blobs.length,1);
 const snapshot=JSON.parse(await t.blobs[0].text());
 const receipt=snapshot.snapshot_receipt;
 assert.match(t.downloads[0],new RegExp('^pfl-s9-registry-late-2026-09-15-'+receipt.sha256.slice(0,12)+'\\.json$'));
 assert.equal(snapshot.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
 assert.equal(snapshot.source_contract,'pfl.synthetic_scientific_registry.v1');
 assert.equal(snapshot.evidence_class,'SYNTHETIC_LAB_ONLY');
 assert.equal(snapshot.R5,'STOP_R5');
 assert.equal(snapshot.release_gates_passed,0);
 assert.equal(snapshot.scientific_ab_cycles,0);
 assert.equal(snapshot.external_authenticity_certified,false);
 assert.equal(snapshot.rights_for_public_display_admitted,false);
 assert.equal(snapshot.query.cut,'late');
 assert.equal(snapshot.query.family,'all');
 assert.equal(snapshot.query.valid_at,'2026-09-15');
 assert.equal(createHash('sha256').update(receipt.canonical_json,'utf8').digest('hex'),receipt.sha256);
 assert.equal(Buffer.byteLength(receipt.canonical_json,'utf8'),receipt.bytes);
 assert.doesNotMatch(JSON.stringify(snapshot),/SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
 assert.equal(t.value('ui.state'),null);
 assert.equal(t.value('ui.session'),null);
 assert.equal(t.value('ui.csrf'),null);
 assert.ok(t.requests.every(x=>x.method==='GET'&&
  ['/api/session','/api/scientific-integration-lab','/api/scientific-registry']
   .includes(new URL(x.route,'http://localhost').pathname)));
 await t.click(null,'scientific');
 await t.click('science-registry-export');
 await t.click('science-export');
 await t.click('science-probe');
 assert.equal(t.downloads.length,1,'Guest has no S8, admission or hidden S9 export actions');
 await t.click(null,null,true);
 assert.equal(t.value('ui.scienceRegistry'),null);
 assert.equal(t.value('ui.guest'),false);
});

for(const {name,id,to,from} of [
 {name:'first_public',id:'science-registry-publication',to:'2026-09-19T12:00:00Z',from:'as_of'},
 {name:'as_of',id:'science-cut',to:'early',from:'late'},
 {name:'valid_at',id:'science-registry-valid',to:'2026-10-10',from:'2026-09-15'},
 {name:'family',id:'science-registry-family',to:'CHAIN',from:'all'}
]){
 test('guest S9 pending export fails closed after '+name+' filter A→B→A',async()=>{
  const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
  t.pauseNextDigest();
  const pending=t.click('science-registry-export');
  assert.equal(t.hasPendingDigest(),true);
  await t.change(id,to);
  await t.change(id,from);
  assert.equal(t.value('ui.scienceRegistry!==null && ui.scienceRegistryError===null'),true,
   'An independently SHA-verified A query is restored before the original digest finishes');
  t.releaseDigest();
  await pending;
  assert.equal(t.downloads.length,0,'Old export must stay invalid even after selection returns to A');
  assert.equal(t.blobs.length,0);
  assert.equal(t.elements.toast?.textContent||'','',
    'Old export response must not publish a stale error after filter invalidation');
  assert.ok(t.requests.every(r=>r.method==='GET'));
 });
}

test('guest export pending on WebCrypto is invalidated by registry HTTP 503',async()=>{
 const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
 t.pauseNextDigest();
 const pending=t.click('science-registry-export');
 assert.equal(t.hasPendingDigest(),true);
 t.setRegistryStatus(503);
 await t.click('science-registry-load');
 assert.equal(t.value('ui.scienceRegistry'),null);
 assert.match(t.elements.content.innerHTML,/HTTP 503/);
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.blobs.length,0);
 assert.equal(t.elements.toast?.textContent||'','',
   'Current HTTP 503 is reported by the registry error panel, not by an old export');
 assert.ok(t.requests.every(r=>r.method==='GET'));
});

test('returning from guest to login invalidates an in-flight S9 receipt export',async()=>{
 const t=setup();await t.value('bootstrap()');await t.click('guest-enter');
 t.pauseNextDigest();
 const pending=t.click('science-registry-export');
 assert.equal(t.hasPendingDigest(),true);
 await t.click(null,null,true);
 t.releaseDigest();await pending;
 assert.equal(t.downloads.length,0);
 assert.equal(t.value('ui.guest'),false);
 assert.match(t.elements.content.innerHTML,/Iniciar sesión/);
});
