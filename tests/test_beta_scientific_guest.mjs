import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {webcrypto} from 'node:crypto';
import {createContext,runInContext} from 'node:vm';
import {fileURLToPath} from 'node:url';

const root=fileURLToPath(new URL('../',import.meta.url));
const script=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const pythonEnv={...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'};
function fixtures(){
 const lab={},registry={};
 for(const cut of ['early','late']){
  lab[cut]=JSON.parse(execFileSync('python',['-B','scripts/run_scientific_integration_lab.py','--cut',cut],
   {cwd:root,env:pythonEnv,encoding:'utf8',maxBuffer:2*1024*1024}));
  const code=[
   'import json,tempfile,sys',
   'from pathlib import Path',
   'from politics_fantasy.scientific_registry import query_registry',
   'with tempfile.TemporaryDirectory(prefix="pfl-guest-vm-") as folder:',
   '    print(json.dumps(query_registry(Path(folder)/"fixture.sqlite3",cut=sys.argv[1]),ensure_ascii=False))'
  ].join('\n');
  registry[cut]=JSON.parse(execFileSync('python',['-B','-c',code,cut],
   {cwd:root,env:pythonEnv,encoding:'utf8',maxBuffer:2*1024*1024}));
 }
 return {lab,registry};
}
const originals=fixtures();

function setup(){
 const elements={},listeners={},requests=[],downloads=[];
 const tabs=['overview','club','market','rounds','observatory','scientific','atlas','progress']
  .map(tab=>({dataset:{tab},hidden:false,classList:{toggle(){}},setAttribute(){},removeAttribute(){}}));
 let labStatus=200,registryStatus=200,corruptRegistry=false;
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
  if(u.pathname==='/api/session')return {ok:false,status:401};
  const cut=u.searchParams.get('cut')||'late';
  if(u.pathname==='/api/scientific-integration-lab'){
   if(labStatus!==200)return {ok:false,status:labStatus};
   const report=structuredClone(originals.lab[cut]);
   report.scenario=u.searchParams.get('scenario')||'baseline';
   return {ok:true,json:async()=>report};
  }
  if(u.pathname==='/api/scientific-registry'){
   if(registryStatus!==200)return {ok:false,status:registryStatus};
   const data=structuredClone(originals.registry[cut]);
   if(corruptRegistry)data.snapshot_receipt.sha256='0'.repeat(64);
   return {ok:true,json:async()=>data};
  }
  throw Error('Guest made a forbidden request: '+route);
 };
 const context=createContext({document:doc,fetch,URL,TextEncoder,Blob,crypto:webcrypto,
  Intl,Date,Number,String,Error,console,setTimeout(){},clearTimeout(){}});
 runInContext(script.slice(0,script.lastIndexOf('bootstrap().catch')),context);
 const click=(action,tab,exitGuest=false)=>listeners.click({target:{closest(selector){
  if(selector==='#guest-exit'&&exitGuest)return {};
  if(selector==='[data-nav],[data-tab]'&&tab)return {dataset:{tab}};
  if(selector==='[data-action]'&&action)return {dataset:{action}};
  return null;
 }}});
 const value=expression=>runInContext(expression,context);
 return {elements,listeners,tabs,requests,downloads,click,value,
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
 assert.doesNotMatch(t.elements.content.innerHTML,/science-registry-export/);
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
