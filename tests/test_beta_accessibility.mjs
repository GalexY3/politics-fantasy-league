import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {spawn,execFileSync} from 'node:child_process';
import {existsSync,mkdtempSync,mkdirSync,readFileSync,readdirSync,rmSync,unlinkSync} from 'node:fs';
import {createServer} from 'node:net';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {setTimeout as delay} from 'node:timers/promises';

// Narrow native-Chrome keyboard/accessibility acceptance against real Python
// loopback runtimes. Separate from the S9 mouse/fixture smoke. No user DBs.
const ROOT=new URL('../',import.meta.url).pathname.replace(/^\/(?=[A-Z]:)/i,'');
const CHROME='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PYENV={...process.env,PYTHONPATH:'src',PYTHONDONTWRITEBYTECODE:'1',
 PYTHONIOENCODING:'utf-8'};

async function freePort(){
 return new Promise((resolve,reject)=>{
  const s=createServer();s.once('error',reject);
  s.listen(0,'127.0.0.1',()=>{
   const port=s.address().port;s.close(()=>resolve(port));
  });
 });
}
async function poll(callback,tries=125){
 for(let i=0;i<tries;i++){
  try{const found=await callback();if(found)return found;}catch(_){}
  await delay(90);
 }
 throw Error('CDP_OR_LOCAL_SERVER_POLL_EXHAUSTED');
}
async function launchServer(directory,scienceOnly=false){
 const port=await freePort();
 const args=['-B','run_demo.py','--port',String(port),'--db',join(directory,'game.sqlite3')];
 if(scienceOnly)args.push('--science-only');
 const proc=spawn('python',args,{cwd:ROOT,env:PYENV,stdio:'ignore',windowsHide:true});
 try{
  const result=await poll(async()=>{
   if(proc.exitCode!==null)throw Error('Python launcher exited unexpectedly');
   const reply=await fetch('http://127.0.0.1:'+port+'/api/session');
   if(reply.status!==401)return null;
   const body=await reply.json();
   return Boolean(body.science_only)===scienceOnly?{port,proc}:null;
  });
  return result;
 }catch(e){proc.kill();throw e;}
}
function closeServer(server){if(server&&server.proc.exitCode===null)server.proc.kill();}

function cdpClient(socket){
 let next=0;
 const pending=new Map();
 socket.addEventListener('message',event=>{
  const reply=JSON.parse(event.data);
  if(!pending.has(reply.id))return;
  const task=pending.get(reply.id);pending.delete(reply.id);
  if(reply.error)task.reject(Error(reply.error.message));
  else task.resolve(reply.result);
 });
 const cdp=(method,params={})=>new Promise((resolve,reject)=>{
  const id=++next;pending.set(id,{resolve,reject});
  socket.send(JSON.stringify({id,method,params}));
 });
 const js=async expression=>{
  const data=await cdp('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(data.exceptionDetails)throw Error('CDP_JS_EXCEPTION: '+expression.slice(0,70));
  return data.result?.value;
 };
 const key=async(name,shift=false)=>{
  const code=name==='Tab'?9:13;
  const modifiers=shift?8:0;
  const attrs={key:name,code:name,windowsVirtualKeyCode:code,
   nativeVirtualKeyCode:code,modifiers};
  await cdp('Input.dispatchKeyEvent',name==='Enter'?
   {type:'keyDown',...attrs,text:'\r',unmodifiedText:'\r'}:
   {type:'rawKeyDown',...attrs});
  await cdp('Input.dispatchKeyEvent',{type:'keyUp',...attrs});
 };
 const tabTo=async(selector,limit=85)=>{
  const trace=[];
  for(let i=0;i<limit;i++){
   await key('Tab');
   const state=await js(`(()=>{
    const n=document.activeElement;
    return {match:!!n?.matches(${JSON.stringify(selector)}),
     hidden:!!n?.closest('[hidden]'),
     fantasy:!!n?.matches('[data-tab="club"],[data-tab="market"],[data-tab="rounds"],[data-tab="overview"],[data-tab="atlas"],[data-tab="progress"]'),
     label:n?.getAttribute('aria-label')||n?.innerText?.slice(0,55)||n?.getAttribute('name')||n?.id||n?.tagName};
   })()`);
   trace.push(state.label);
   assert.equal(state.hidden,false,'Tab focused a hidden descendant: '+state.label);
   assert.equal(state.fantasy,false,'Tab focused a hidden Fantasy menu: '+state.label);
   if(state.match)return trace;
  }
  throw Error('KEYBOARD_UNREACHABLE '+selector+' sequence='+trace.join(' > '));
 };
 return {cdp,js,key,tabTo};
}

function namedControls(script){
 return script(`(()=>{
  const visible=n=>n.getClientRects().length>0&&getComputedStyle(n).visibility!=='hidden'
    &&!n.closest('[hidden]')&&!n.disabled;
  const list=[...document.querySelectorAll('main button,main input,main select,nav button,#guest-exit')].filter(visible);
  return list.map(n=>({
    kind:n.tagName.toLowerCase(),id:n.id||n.getAttribute('data-action')||n.getAttribute('data-tab'),
    name:n.getAttribute('aria-label')||n.labels?.[0]?.innerText?.trim()||n.textContent?.trim()||'',
  }));
 })()`);
}

test('Chrome CDP: visitor keyboard Tab/Enter/Shift-Tab, narrow viewport, aria/alerts, S9 SHA', {
 timeout:90000
},async t=>{
 if(!existsSync(CHROME)||typeof WebSocket!=='function'){
  t.skip('Native Chrome and builtin WebSocket are required for this real CDP test');
  return;
 }
 const scratch=mkdtempSync(join(tmpdir(),'pfl-beta-keyboard-'));
 const downloadDir=join(scratch,'downloads');mkdirSync(downloadDir);
 const demoDir=join(scratch,'demo');mkdirSync(demoDir);
 const scienceDir=join(scratch,'science');mkdirSync(scienceDir);
 let demo=null,science=null,chrome=null,socket=null;
 const requests=[];
 try{
  demo=await launchServer(demoDir,false);
  const cdpPort=await freePort();
  chrome=spawn(CHROME,[
   '--headless=new','--no-first-run','--no-default-browser-check',
   '--disable-gpu','--disable-background-networking','--disable-component-update',
   '--disable-sync','--disable-extensions','--no-pings',
   '--remote-debugging-address=127.0.0.1','--remote-debugging-port='+cdpPort,
   '--remote-allow-origins=*','--user-data-dir='+join(scratch,'chrome-profile'),
   'http://127.0.0.1:'+demo.port+'/'
  ],{stdio:'ignore',windowsHide:true});
  const page=await poll(async()=>{
   const data=await (await fetch('http://127.0.0.1:'+cdpPort+'/json/list')).json();
   return data.find(x=>x.type==='page'&&x.url.includes(':'+demo.port+'/'));
  });
  socket=new WebSocket(page.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
   socket.addEventListener('open',resolve,{once:true});
   socket.addEventListener('error',reject,{once:true});
  });
  const {cdp,js,key,tabTo}=cdpClient(socket);
  socket.addEventListener('message',event=>{
   const p=JSON.parse(event.data);
   if(p.method==='Network.requestWillBeSent'){
    const r=p.params?.request;
    if(r)requests.push({method:r.method,url:r.url});
   }
  });
  await cdp('Runtime.enable');
  await cdp('Network.enable');
  await cdp('Page.enable');
  await cdp('Browser.setDownloadBehavior',{behavior:'allow',
   downloadPath:downloadDir,eventsEnabled:true});
  await poll(()=>js("Boolean(document.querySelector('[data-action=\"guest-enter\"]')&&!ui.guest)"));
  const loginControls=await namedControls(js);
  assert.ok(loginControls.some(x=>x.name.includes('Usuario')));
  assert.ok(loginControls.some(x=>x.name.includes('Contraseña')));
  assert.ok(loginControls.some(x=>x.name.includes('Entrar al Observatorio')));
  const initial=await tabTo('[data-action="guest-enter"]',15);
  assert.ok(initial.length>=1);
  await key('Enter');
  await poll(()=>js("Boolean(ui.guest&&ui.scienceRegistry&&ui.scientific&&ui.state===null&&ui.session===null)"));
  assert.equal(await js("Boolean(document.querySelector('#content[aria-live=polite]')&&document.querySelector('#content').innerText.includes('R5 STOP'))"),true);
  assert.equal(await js("document.querySelectorAll('[data-tab]:not([hidden])').length"),2);
  const navNames=await js("[...document.querySelectorAll('[data-tab]:not([hidden])')].map(x=>x.innerText.trim())");
  assert.ok(navNames.some(x=>x.includes('Observatorio')));
  assert.ok(navNames.some(x=>x.includes('Laboratorio')));
  const ax=await cdp('Accessibility.getFullAXTree');
  assert.ok(ax.nodes.some(x=>x.role?.value==='button'&&/Observatorio/.test(x.name?.value||'')),
   'Chrome accessibility tree must name the scientific navigation');
  assert.ok(ax.nodes.some(x=>/R5 STOP/.test(x.name?.value||'')),
   'R5 warning must appear in the real Chrome accessibility tree');
  const controls=await namedControls(js);
  assert.deepEqual(controls.filter(x=>!x.name).map(x=>x.id),[],
   'Every visible input, select and button needs a meaningful accessible name');
  await tabTo('[data-tab="scientific"]');
  await key('Enter');
  await poll(()=>js("Boolean(ui.tab==='scientific'&&document.querySelector('#content').innerText.includes('B0 y B3')&&document.querySelector('#content').innerText.includes('Testigos diferenciales sintéticos'))"));
  assert.equal(await js("document.querySelector('[data-tab=\"scientific\"]').getAttribute('aria-current')"),'page');
  await tabTo('[data-tab="observatory"]');
  await key('Enter');
  await poll(()=>js("Boolean(ui.tab==='observatory'&&document.querySelector('[data-action=\"science-registry-export\"]'))"));
  assert.equal(await js("document.querySelector('[data-tab=\"observatory\"]').getAttribute('aria-current')"),'page');
  await cdp('Emulation.setDeviceMetricsOverride',{width:360,height:740,
   deviceScaleFactor:1,mobile:false});
  assert.equal(await js("document.documentElement.clientWidth<=400"),true);
  assert.equal(await js("getComputedStyle(document.querySelector('[data-tab=\"market\"]')).display==='none'"),true);
  const untilExport=await tabTo('[data-action="science-registry-export"]',100);
  assert.ok(untilExport.length>0);
  assert.equal(await js("(()=>{const b=document.activeElement,r=b.getBoundingClientRect();return b.matches('[data-action=\"science-registry-export\"]')&&r.width>0&&r.height>0&&!b.disabled&&r.top<innerHeight&&r.bottom>0;})()"),true);
  await key('Tab',true);
  assert.equal(await js("document.activeElement.matches('[data-action=\"science-registry-export\"]')"),false,
   'Shift+Tab must leave the export action');
  await key('Tab');
  assert.equal(await js("document.activeElement.matches('[data-action=\"science-registry-export\"]')"),true,
   'Tab must return to the export action');
  await key('Enter');
  const saved=await poll(()=>readdirSync(downloadDir)
    .find(x=>/^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/.test(x)));
  const exported=JSON.parse(readFileSync(join(downloadDir,saved),'utf8'));
  const sha=createHash('sha256').update(exported.snapshot_receipt.canonical_json,'utf8').digest('hex');
  assert.equal(sha,exported.snapshot_receipt.sha256);
  assert.equal(exported.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(exported.R5,'STOP_R5');
  assert.equal(exported.release_gates_passed,0);
  assert.equal(exported.external_authenticity_certified,false);
  assert.match(saved,new RegExp(sha.slice(0,12)));
  unlinkSync(join(downloadDir,saved));

  // A real temporary S9 integrity fault should replace results with a
  // keyboard-reachable alert, never retain a stale exportable snapshot.
  const registryDb=join(demoDir,'scientific_registry_synthetic.sqlite3');
  execFileSync('python',['-B','-c',
   'import sqlite3,sys;db=sqlite3.connect(sys.argv[1]);db.execute("DROP TRIGGER registry_distribution_immutable_update");db.commit();db.close()',
   registryDb],{cwd:ROOT,env:PYENV,timeout:8000});
  await tabTo('[data-action="science-registry-load"]',100);
  await key('Enter');
  await poll(()=>js("Boolean(ui.scienceRegistryError&&document.querySelector('#content [role=\"alert\"]'))"));
  assert.equal(await js("ui.scienceRegistry===null"),true);
  assert.equal(await js("document.querySelector('[data-action=\"science-registry-export\"]')===null"),true);
  assert.equal(await js("document.querySelector('#content [role=\"alert\"]').innerText.includes('503')"),true);
  const errorAX=await cdp('Accessibility.getFullAXTree');
  assert.ok(errorAX.nodes.some(x=>x.role?.value==='alert'),
   'The real 503 must expose an alert in the Chrome accessibility tree');
  await tabTo('[data-action="guest-reload"]',100);
  assert.equal(await js("document.activeElement.innerText.includes('Reintentar')"),true);
  assert.ok(requests.filter(x=>x.url.includes(':'+demo.port+'/'))
    .every(x=>x.method==='GET'&&!/\/api\/(state|register|login)/.test(x.url)));
  closeServer(demo);demo=null;

  // Reuse the SAME Chrome/CDP instance for the real accounts-free science mode.
  science=await launchServer(scienceDir,true);
  await cdp('Page.navigate',{url:'http://127.0.0.1:'+science.port+'/'});
  await poll(()=>js("Boolean(ui.guest&&ui.scienceRegistry&&document.querySelector('[data-action=\"science-registry-export\"]'))"));
  assert.equal(await js("document.querySelector('#auth-form')===null"),true);
  assert.equal(await js("document.querySelectorAll('[data-tab]:not([hidden])').length"),2);
  assert.equal(await js("document.querySelector('#content').innerText.includes('R5 STOP')"),true);
  await tabTo('[data-action="science-registry-export"]',100);
  await key('Enter');
  const second=await poll(()=>readdirSync(downloadDir)
    .find(x=>/^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/.test(x)));
  const scienceExport=JSON.parse(readFileSync(join(downloadDir,second),'utf8'));
  assert.equal(createHash('sha256').update(scienceExport.snapshot_receipt.canonical_json,'utf8').digest('hex'),
   scienceExport.snapshot_receipt.sha256);
  assert.equal(scienceExport.R5,'STOP_R5');
  assert.equal(existsSync(join(scienceDir,'accounts.sqlite3')),false);
  const requestsScience=requests.filter(x=>x.url.includes(':'+science.port+'/'));
  assert.ok(requestsScience.some(x=>x.url.includes('/api/scientific-registry')));
  assert.deepEqual(requestsScience.filter(x=>x.method!=='GET'||/\/api\/(state|register|login)/.test(x.url)),[]);
  console.log(JSON.stringify({
   status:'PASS',nativeChrome:true,viewport:360,tab_to_guest:initial.length,
   tab_to_export:untilExport.length,keyboard_export_sha256:sha,
   science_only_sha256:scienceExport.snapshot_receipt.sha256,
   r5_accessible:true,http503_role_alert:true,
   fantasy_menu_keyboard_focus:false,
  }));
 }finally{
  if(socket)socket.close();
  if(chrome&&chrome.exitCode===null)chrome.kill();
  closeServer(demo);closeServer(science);
  try{rmSync(scratch,{recursive:true,force:true,maxRetries:3,retryDelay:200});}catch(_){}
 }
});
