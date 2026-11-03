import {test} from 'node:test';
import assert from 'node:assert/strict';
import {execFileSync} from 'node:child_process';
import {createHash,webcrypto} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {createContext,runInContext} from 'node:vm';
import {fileURLToPath} from 'node:url';

// S8 browser flows use real closed Python integration reports and S9 SQLite
// receipts. The VM replaces only the browser/network boundary, never science.
const ROOT=fileURLToPath(new URL('../',import.meta.url));
const SOURCE=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const PYENV={...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'};
const PYQUERY=[
 'import json,sys,tempfile',
 'from pathlib import Path',
 'from politics_fantasy.scientific_registry import query_registry',
 'with tempfile.TemporaryDirectory(prefix="pfl-guest-lab-s9-") as p:',
 '    print(json.dumps(query_registry(Path(p)/"fixture.sqlite3",cut=sys.argv[1],valid_at=sys.argv[2],family=sys.argv[3],published_until=sys.argv[4]),ensure_ascii=False))'
].join('\n');
const lab=Object.fromEntries(['early','late'].map(cut=>[
 cut,JSON.parse(execFileSync('python',['-B','scripts/run_scientific_integration_lab.py','--cut',cut],
  {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:4*1024*1024,timeout:15000}))
]));
const registryCache=new Map();
function registry(cut,validAt,family,published){
 const key=[cut,validAt,family,published].join('|');
 if(!registryCache.has(key)){
  registryCache.set(key,JSON.parse(execFileSync('python',
   ['-B','-c',PYQUERY,cut,validAt,family,published],
   {cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:4*1024*1024,timeout:15000})));
 }
 return structuredClone(registryCache.get(key));
}

function harness({href='http://localhost/',scienceOnly=false}={}){
 const elements={},listeners={},requests=[],downloads=[],historyWrites=[];
 const location={href};
 const history={replaceState(state,title,path){
  historyWrites.push({path,requestCount:requests.length});
  location.href=new URL(path,location.href).href;
 }};
 const tabs=['overview','club','market','rounds','observatory','scientific','atlas','progress']
  .map(tab=>({dataset:{tab},hidden:false,classList:{toggle(){}},
   setAttribute(){},removeAttribute(){}}));
 let labStatus=200,registryStatus=200,corruptReceipt=false;
 const document={
  getElementById(id){return elements[id]??={innerHTML:'',textContent:'',hidden:false,addEventListener(){}};},
  querySelectorAll(selector){return selector==='[data-tab]'?tabs:[];},
  createElement(){return{click(){downloads.push(this.download);},remove(){}};},
  body:{appendChild(){}},
  addEventListener(event,callback){listeners[event]=callback;}
 };
 class LocalURL extends URL {}
 LocalURL.createObjectURL=()=> 'blob:guest-lab-test';
 LocalURL.revokeObjectURL=()=>{};
 const fetch=async (route,options={})=>{
  requests.push({route,method:options.method||'GET'});
  const u=new URL(route,'http://localhost');
  if(u.pathname==='/api/session')return {ok:false,status:401,json:async()=>scienceOnly
   ?{authenticated:false,science_only:true,error:'LOCAL_SCIENCE_ONLY'}
   :{authenticated:false,error:'AUTH_REQUIRED'}};
  if(u.pathname==='/api/scientific-integration-lab'){
   if(labStatus!==200)return {ok:false,status:labStatus};
   const result=structuredClone(lab[u.searchParams.get('cut')||'late']);
   result.scenario=u.searchParams.get('scenario')||'baseline';
   return {ok:true,json:async()=>result};
  }
  if(u.pathname==='/api/scientific-registry'){
   if(registryStatus!==200)return {ok:false,status:registryStatus};
   const data=registry(u.searchParams.get('cut')||'late',
    u.searchParams.get('valid_at')||'2026-09-15',
    u.searchParams.get('family')||'all',
    u.searchParams.get('published_until')||'as_of');
   if(corruptReceipt)data.snapshot_receipt.sha256='0'.repeat(64);
   return {ok:true,json:async()=>data};
  }
  throw Error('Forbidden guest request: '+route);
 };
 const context=createContext({document,location,history,fetch,URL:LocalURL,
  TextEncoder,Blob,crypto:webcrypto,Intl,Date,Number,String,Error,console,
  setTimeout(){},clearTimeout(){}});
 runInContext(SOURCE.slice(0,SOURCE.lastIndexOf('bootstrap().catch')),context);
 const value=expr=>runInContext(expr,context);
 const click=(action=null,extra={})=>listeners.click({target:{closest(selector){
  if(selector==='[data-nav],[data-tab]'&&extra.tab)return{dataset:{tab:extra.tab}};
  if(selector==='[data-action]'&&action)return{dataset:{action,...extra}};
  return null;
 }}});
 const change=(id,value)=>listeners.change({target:{id,value}});
 return {elements,tabs,requests,downloads,historyWrites,location,value,click,change,
  html:()=>elements.content.innerHTML,
  async guest(){await value('bootstrap()');if(!value('ui.guest'))await click('guest-enter');},
  setRegistryStatus:n=>{registryStatus=n;},
  setLabStatus:n=>{labStatus=n;},
  corruptReceipt:enabled=>{corruptReceipt=enabled;}
 };
}
function getOnly(t){
 assert.deepEqual(t.requests.filter(r=>r.method!=='GET'),[]);
 assert.deepEqual(t.requests.map(r=>new URL(r.route,'http://localhost').pathname)
  .filter(path=>!['/api/session','/api/scientific-integration-lab','/api/scientific-registry'].includes(path)),[]);
 assert.equal(t.value('ui.state'),null);
 assert.equal(t.value('ui.session'),null);
 assert.equal(t.value('ui.csrf'),null);
 assert.equal(t.downloads.length,0,'A visitor must never trigger an S8 export');
}
const S7=lab.late.warehouse.b0_b3_witness_sets.sets_by_knowledge_cut.late.sets;
assert.equal(S7.length,20,'The fixture must retain twenty differentiated S7 cases');
const conflict=S7.find(c=>c.status==='CONFLICT');
assert.ok(conflict?.contradiction,'The fixture must supply a genuine S7 contradiction');

test('S8 guest explorer offers four selectable read-only panels and detailed twenty-set S7',async()=>{
 const t=harness();await t.guest();
 await t.click(null,{tab:'scientific'});
 assert.equal(t.value('ui.tab'),'scientific');
 for(const panel of ['mechanisms','s3','witnesses','distributions']){
  assert.match(t.html(),new RegExp("data-action=[\"']science-guest-panel[\"'][^>]*data-panel=[\"']"+panel+"[\"']"));
  await t.click('science-guest-panel',{panel});
  assert.match(t.html(),/VISITA CIENTÍFICA|CONSULTA ABIERTA/);
  assert.equal(t.value('ui.tab'),'scientific');
 }
 await t.click('science-guest-panel',{panel:'mechanisms'});
 assert.match(t.html(),/B0/);
 assert.match(t.html(),/B3/);
 await t.click('science-guest-panel',{panel:'s3'});
 assert.match(t.html(),/S3/);
 assert.match(t.html(),new RegExp(lab.late.warehouse.partial_identification_oracle.change_bounds.lower.replace('/','\\/')));
 await t.click('science-guest-panel',{panel:'witnesses'});
 for(const item of S7)assert.ok(t.html().includes(item.case),'Missing S7 set '+item.case);
 assert.match(t.html(),/CONFLICT/);
 assert.ok(t.html().includes(conflict.case));
 assert.ok(t.html().includes(conflict.contradiction.kind),'S7 conflict evidence must remain reviewable');
 const detailed=S7.find(c=>c.witness_admissibility?.length>0);
 assert.ok(detailed,'Real S7 oracle must contain per-case witness admissibility');
 for(const witness of detailed.witness_admissibility){
  assert.ok(t.html().includes(witness.case),'Missing per-case witness '+witness.case);
  assert.ok(t.html().includes(witness.reason),'Missing witness exclusion/admission rationale');
 }
 assert.match(t.html(),/Conflicto|CONFLICT/);
 assert.doesNotMatch(t.html(),/SYN:S7_ASSET_|SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
 await t.click('science-export');
 await t.click('science-probe');
 getOnly(t);
});

test('S8 guest publication filter follows exact seven-key URL and independently verified S9 GET',async()=>{
 const t=harness({scienceOnly:true});await t.guest();
 await t.click(null,{tab:'scientific'});
 assert.match(t.html(),/id=["']science-registry-publication["']/);
 await t.click('science-guest-panel',{panel:'distributions'});
 assert.match(t.html(),/S8:PUBLIC_DESCRIPTOR_0[1-6]/);
 const origin=t.requests.length;
 await t.change('science-registry-publication','2026-09-19T12:00:00Z');
 const q=new URL(t.location.href).searchParams;
 assert.deepEqual([...q.keys()],['pfl_guest','cut','valid_at','family','published_until','scenario','view']);
 assert.equal(q.get('published_until'),'2026-09-19T12:00:00Z');
 assert.equal(t.value('ui.scienceRegistry.published_until'),'2026-09-19T12:00:00Z');
 assert.ok(t.requests.slice(origin).some(r=>{
  const u=new URL(r.route,'http://localhost');
  return u.pathname==='/api/scientific-registry'&&u.searchParams.get('published_until')==='2026-09-19T12:00:00Z';
 }));
 const report=lab.late.explorer.catalog.distributions;
 const included=report.filter(d=>d.first_public_at_fixture<='2026-09-19T12:00:00Z');
 const excluded=report.filter(d=>d.first_public_at_fixture>'2026-09-19T12:00:00Z');
 assert.equal(included.length,2);
 for(const d of included){
  const bytes=Buffer.from('S8 PUBLIC SYNTHETIC CATALOG\n'
   +'DISTRIBUTION:'+d.distribution_id+'\n'
   +'FAMILY:'+d.family+'\n'
   +'CAPTURE:'+d.captured_at_fixture+'\n'
   +'PUBLICATION:'+d.first_public_at_fixture+'\n','utf8');
  assert.equal(bytes.length,d.byte_length,'Public descriptor byte count');
  assert.equal(createHash('sha256').update(bytes).digest('hex'),d.sha256,
   'Public descriptor SHA must be independently reproducible in Node');
  assert.ok(t.html().includes(d.distribution_id),d.distribution_id);
  assert.ok(t.html().includes(d.sha256),'Missing public descriptor SHA '+d.distribution_id);
 }
 for(const d of excluded)assert.ok(!t.html().includes(d.distribution_id),'Future distribution leaked '+d.distribution_id);
 assert.match(t.html(),/DISTRIBUTION_COVERAGE_UNATTESTED/);
 assert.doesNotMatch(t.html(),/rights_for_requested_purpose_admitted.{0,10}true/);
 getOnly(t);
});

test('early S8 cut hides S3 lookahead, future descriptions and invalid publication choice',async()=>{
 const t=harness();await t.guest();await t.click(null,{tab:'scientific'});
 await t.change('science-registry-publication','2026-10-30T12:00:00Z');
 assert.equal(new URL(t.location.href).searchParams.get('published_until'),'2026-10-30T12:00:00Z');
 await t.change('science-cut','early');
 assert.equal(t.value('ui.scientific.cut'),'early');
 assert.equal(t.value('ui.scienceRegistry.cut'),'early');
 assert.notEqual(new URL(t.location.href).searchParams.get('published_until'),'2026-10-30T12:00:00Z');
 await t.click('science-guest-panel',{panel:'s3'});
 assert.match(t.html(),/S3/);
 assert.doesNotMatch(t.html(),/-11\/52/);
 assert.match(t.html(),/temprano|Aún no conocida|no conocida|no disponible/i);
 await t.click('science-guest-panel',{panel:'distributions'});
 const earlyDigests=new Set(lab.early.explorer.catalog.distributions.map(d=>d.sha256));
 for(const d of lab.late.explorer.catalog.distributions){
  // Public IDs are numbered *within each cut*; a late PUBLIC_01 can alias
  // an unrelated early PUBLIC_01. Compare descriptor SHA, not surrogate ID.
  if(d.first_public_at_fixture>'2026-10-15T12:00:00Z'&&!earlyDigests.has(d.sha256))
   assert.ok(!t.html().includes(d.sha256),'Early leaked future descriptor SHA '+d.sha256);
 }
 await t.change('science-registry-publication','2026-10-30T12:00:00Z');
 assert.notEqual(new URL(t.location.href).searchParams.get('published_until'),'2026-10-30T12:00:00Z');
 getOnly(t);
});

test('guest S8/S9 navigation and reload keeps verified panels without account effects',async()=>{
 const t=harness();await t.guest();
 await t.click(null,{tab:'scientific'});
 await t.click('science-guest-panel',{panel:'witnesses'});
 assert.ok(t.html().includes(conflict.case));
 const before=t.requests.length;
 await t.click(null,{tab:'observatory'});
 assert.match(t.html(),/S9:PUBLIC_01/);
 await t.click(null,{tab:'scientific'});
 assert.match(t.html(),/science-guest-panel/);
 assert.equal(t.requests.length,before);
 await t.click('guest-reload');
 assert.ok(t.requests.length>=before+2);
 assert.match(t.html(),/science-guest-panel/);
 getOnly(t);
});

test('S8 publication and knowledge changes invalidate an earlier S9 pair until explicit fresh GET',async()=>{
 const t=harness();await t.guest();
 await t.click('science-registry-tab',{registry:'compare'});
 assert.equal(t.value('ui.scienceRegistryComparison!==null && ui.scienceRegistryCompareError===null'),true);
 const compareRequests=t.requests.length;
 await t.click(null,{tab:'scientific'});
 await t.change('science-registry-publication','2026-09-19T12:00:00Z');
 assert.equal(t.value('ui.scienceRegistryComparison'),null);
 assert.equal(t.value('ui.scienceRegistryPairExportGeneration>=0'),true);
 assert.ok(t.requests.length>compareRequests);
 await t.click(null,{tab:'observatory'});
 await t.click('science-registry-tab',{registry:'compare'});
 assert.equal(t.value('ui.scienceRegistryComparison!==null && ui.scienceRegistryComparison.early.published_until==="2026-09-19T12:00:00Z"'),true);
 const newPair=t.requests.length;
 await t.click(null,{tab:'scientific'});
 await t.change('science-cut','early');
 assert.equal(t.value('ui.scienceRegistryComparison'),null);
 assert.equal(t.value('ui.scienceRegistry.cut'),'early');
 assert.ok(t.requests.length>newPair);
 getOnly(t);
});

for(const failed of ['lab','registry','sha']){
 test('HTTP/integrity failure '+failed+' clears all old guest S8 explorer and S9 data',async()=>{
  const t=harness();await t.guest();await t.click(null,{tab:'scientific'});
  await t.click('science-guest-panel',{panel:'witnesses'});
  assert.ok(t.html().includes(conflict.case));
  if(failed==='lab')t.setLabStatus(503);
  if(failed==='registry')t.setRegistryStatus(503);
  if(failed==='sha')t.corruptReceipt(true);
  await t.click('guest-reload');
  assert.equal(t.value('ui.scientific===null || ui.scienceRegistry===null'),true);
  assert.doesNotMatch(t.html(),new RegExp(conflict.case));
  assert.doesNotMatch(t.html(),/S8:PUBLIC_DESCRIPTOR_01/);
  assert.match(t.html(),/bloquead|rechazad|incompatible|no disponibles|SHA/i);
  getOnly(t);
 });
}
