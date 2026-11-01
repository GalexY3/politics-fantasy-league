import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer as httpServer} from 'node:http';
import {createServer as portServer} from 'node:net';
import {readFileSync,existsSync,mkdtempSync,rmSync,mkdirSync,readdirSync} from 'node:fs';
import {spawn,execFileSync} from 'node:child_process';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {setTimeout as delay} from 'node:timers/promises';

// One native Chrome/CDP smoke: real DOM, fetch, CSS and WebCrypto. Only a
// loopback, synthetic-only HTTP facade is exposed; no official files or websites.
const ROOT=new URL('../',import.meta.url).pathname.replace(/^\/(?=[A-Z]:)/i,'');
const CHROME='C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe';
const PYENV={...process.env,PYTHONPATH:'src',
  PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'};
const REGISTRY_CODE=[
 'import json,sys',
 'from pathlib import Path',
 'from politics_fantasy.scientific_registry import query_registry',
 'result=query_registry(Path(sys.argv[1]),cut=sys.argv[2],valid_at=sys.argv[3],family=sys.argv[4],published_until=sys.argv[5])',
 'print(json.dumps(result,ensure_ascii=False))'
].join('\n');

function python(args){
 return execFileSync('python',['-B',...args],{
  cwd:ROOT,env:PYENV,encoding:'utf8',maxBuffer:2*1024*1024,timeout:12000});
}
function reply(res,status,payload,contentType='application/json; charset=utf-8'){
 res.writeHead(status,{'Content-Type':contentType,'Cache-Control':'no-store',
  'Content-Security-Policy':"default-src 'self'; script-src 'self'; style-src 'self'; connect-src 'self'; object-src 'none'; base-uri 'none'"});
 res.end(typeof payload==='string'?payload:JSON.stringify(payload));
}
async function freePort(){
 return new Promise((resolve,reject)=>{
  const server=portServer();server.once('error',reject);
  server.listen(0,'127.0.0.1',()=>{const port=server.address().port;
   server.close(()=>resolve(port));});
 });
}
async function poll(fn,attempts=100){
 for(let i=0;i<attempts;i++){
  try{const value=await fn();if(value)return value;}catch(_){}
  await delay(110);
 }
 throw Error('CHROME_LOCAL_SMOKE_POLL_EXHAUSTED');
}

test('S9 Chrome native CDP: live DOM observes registry late/early, source family, valid_at and 503', {
 timeout:45000
},async t=>{
 if(!existsSync(CHROME)||typeof WebSocket!=='function'){
  t.skip('Local Chrome or builtin WebSocket not available');return;
 }
 const scratch=mkdtempSync(join(tmpdir(),'pfl-s9-chrome-'));
 const registryDb=join(scratch,'synthetic.sqlite3');
 const downloadsDir=join(scratch,'downloads');
 mkdirSync(downloadsDir);
 const port=await freePort(),cdpPort=await freePort();
 const base='http://127.0.0.1:'+port;
 let failRegistry=false,chrome=null,socket=null;
 const server=httpServer((req,res)=>{
  const url=new URL(req.url,base);
  try{
   if(url.pathname==='/')return reply(res,200,
    readFileSync(join(ROOT,'src/politics_fantasy/web/index.html'),'utf8'),
    'text/html; charset=utf-8');
   if(url.pathname==='/app.js')return reply(res,200,
    readFileSync(join(ROOT,'src/politics_fantasy/web/app.js'),'utf8'),
    'text/javascript; charset=utf-8');
   if(url.pathname==='/style.css')return reply(res,200,
    readFileSync(join(ROOT,'src/politics_fantasy/web/style.css'),'utf8'),
    'text/css; charset=utf-8');
   if(url.pathname==='/api/session')return reply(res,401,
    {authenticated:false,error:'AUTH_REQUIRED'});
   if(url.pathname==='/api/scientific-integration-lab'){
    const cut=url.searchParams.get('cut')||'late';
    const scenario=url.searchParams.get('scenario')||'baseline';
    return reply(res,200,python(['scripts/run_scientific_integration_lab.py',
      '--cut',cut,'--scenario',scenario]));
   }
   if(url.pathname==='/api/scientific-registry'){
    if(failRegistry)return reply(res,503,{error:'SYNTHETIC_REGISTRY_UNAVAILABLE'});
    const q=url.searchParams;
    return reply(res,200,python(['-c',REGISTRY_CODE,registryDb,
      q.get('cut')||'late',q.get('valid_at')||'2026-09-15',
      q.get('family')||'all',q.get('published_until')||'as_of']));
   }
   return reply(res,404,{error:'NOT_FOUND'});
  }catch(e){return reply(res,503,{error:'SYNTHETIC_FIXTURE_UNAVAILABLE'});}
 });
 try{
  // A real persistent, explicitly triggered synthetic intake precedes the
  // browser session. The public HTTP endpoint cannot ingest originals.
  python(['-c',[
   'import sys',
   'from pathlib import Path',
   'from politics_fantasy.scientific_registry import enroll_synthetic_fixture',
   'for name in ("sandbox_alpha_v1","sandbox_beta_v1","sandbox_bad_issuer"):',
   '    enroll_synthetic_fixture(Path(sys.argv[1]),name)'
  ].join('\n'),registryDb]);
  await new Promise(resolve=>server.listen(port,'127.0.0.1',resolve));
  chrome=spawn(CHROME,[
   '--headless=new','--no-first-run','--no-default-browser-check',
   '--disable-gpu','--disable-background-networking','--disable-component-update',
   '--disable-sync','--disable-extensions','--no-pings',
   '--remote-debugging-address=127.0.0.1',
   '--remote-debugging-port='+cdpPort,'--remote-allow-origins=*',
   '--user-data-dir='+join(scratch,'chrome-profile'),base+'/'
  ],{stdio:'ignore'});
  const target=await poll(async()=>{
   const response=await fetch('http://127.0.0.1:'+cdpPort+'/json/list');
   const pages=await response.json();
   return pages.find(p=>p.type==='page'&&p.url.startsWith(base));
  });
  socket=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
   socket.addEventListener('open',resolve,{once:true});
   socket.addEventListener('error',reject,{once:true});
  });
  let nextId=0;
  const waiting=new Map();
  socket.addEventListener('message',event=>{
   const message=JSON.parse(event.data);
   if(!waiting.has(message.id))return;
   const task=waiting.get(message.id);waiting.delete(message.id);
   if(message.error)task.reject(Error(message.error.message));
   else task.resolve(message.result);
  });
  const cdp=(method,params={})=>new Promise((resolve,reject)=>{
   const id=++nextId;waiting.set(id,{resolve,reject});
   socket.send(JSON.stringify({id,method,params}));
  });
  const js=async expression=>{
   const result=await cdp('Runtime.evaluate',{
    expression,returnByValue:true,awaitPromise:true});
   if(result.exceptionDetails)throw Error('CHROME_JS_EXCEPTION');
   return result.result?.value;
  };
  await cdp('Runtime.enable');
  await cdp('Browser.setDownloadBehavior',{behavior:'allow',
    downloadPath:downloadsDir,eventsEnabled:true});
  await poll(()=>js("Boolean(document.querySelector('#auth-form'))"));
  await js("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.club='demo';document.querySelector('[data-tab=\"scientific\"]').click();true");
  await poll(()=>js("Boolean(ui.scientific&&ui.scientific.cut==='late'&&document.querySelector('[data-action=\"science-registry-load\"]'))"));
  await js("document.querySelector('[data-action=\"science-registry-load\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistry.registry.visible_distribution_count===6)"));
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),true);
  assert.equal(await js('ui.scienceRegistry.registry.schema_version'),4);
  await js("document.querySelector('[data-registry=\"intake\"]').click();true");
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:INTAKE_04')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('SANDBOX_REJECTED')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('SYN:LOCAL_SANDBOX')"),false);
  // S9.1: perform a genuine mouse click in native Chrome and verify that its
  // browser-downloaded JSON contains the exact WebCrypto-verified S9 receipt,
  // rather than accidentally exporting the S8 laboratory receipt.
  await js("document.querySelector('[data-action=\"science-registry-export\"]').scrollIntoView({block:'center'});true");
  const point=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-export\"]').getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
    x:point.x,y:point.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
    x:point.x,y:point.y,button:'left',clickCount:1});
  const saved=await poll(()=>readdirSync(downloadsDir).find(x=>
    /^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/.test(x)));
  const exported=JSON.parse(readFileSync(join(downloadsDir,saved),'utf8'));
  assert.equal(exported.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(exported.R5,'STOP_R5');
  const canonical=Buffer.from(exported.snapshot_receipt.canonical_json,'utf8');
  assert.equal(createHash('sha256').update(canonical).digest('hex'),
    exported.snapshot_receipt.sha256);
  assert.doesNotMatch(JSON.stringify(exported),/SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
  // The same current view must expose persistent synthetic assessment history.
  await js("document.querySelector('[data-registry=\"admission\"]').click();true");
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:ASSESS_08')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('SYN:CHAIN_V1')"),false);
  assert.equal(await js("getComputedStyle(document.querySelector('.science-registry')).display!=='none'"),true);
  await js("(()=>{const e=document.getElementById('science-registry-family');e.value='CHAIN';e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistry.family==='CHAIN'&&ui.scienceRegistry.registry.visible_distribution_count===2)"));
  await js("(()=>{const e=document.getElementById('science-registry-valid');e.value='2026-10-10';e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistry.valid_at==='2026-10-10')"));
  await js("(()=>{const e=document.getElementById('science-registry-family');e.value='all';e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistry.family==='all'&&ui.scienceRegistry.registry.visible_distribution_count===6)"));
  await js("(()=>{const e=document.getElementById('science-cut');e.value='early';e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scientific&&ui.scientific.cut==='early'&&ui.scienceRegistry===null)"));
  await js("document.querySelector('[data-action=\"science-registry-load\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistry.registry.visible_distribution_count===2)"));
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),false);
  failRegistry=true;
  await js("document.querySelector('[data-action=\"science-registry-load\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistryError&&ui.scienceRegistryError.includes('503'))"));
  assert.equal(await js("ui.scienceRegistry===null"),true);
 }finally{
  if(socket)socket.close();
  if(chrome&&chrome.exitCode===null)chrome.kill();
  await new Promise(resolve=>server.close(resolve));
  try{rmSync(scratch,{recursive:true,force:true,maxRetries:2,retryDelay:200});}catch(_){}
 }
});
