import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createServer as httpServer} from 'node:http';
import {createServer as portServer} from 'node:net';
import {readFileSync,existsSync,mkdtempSync,rmSync,mkdirSync,readdirSync,unlinkSync} from 'node:fs';
import {spawn,spawnSync,execFileSync} from 'node:child_process';
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
 let lastError;
 for(let i=0;i<attempts;i++){
  try{const value=await fn();if(value)return value;}
  catch(error){lastError=error;}
  await delay(110);
 }
 const detail=lastError?String(lastError.message||lastError)
  .replace(/https?:\/\/\S+/g,'[URL]')
  .replace(/[A-Za-z]:\\\S+/g,'[PATH]').slice(0,160):'condition not yet met';
 throw Error('CHROME_LOCAL_SMOKE_POLL_EXHAUSTED ('+detail+')');
}

async function completedJsonDownload(folder,pattern){
 // Chrome may expose the final .json filename before the write is complete.
 // Observe a parseable, fully written receipt instead of merely the directory
 // entry; the content assertions below remain independent of this wait.
 return poll(()=>{
  const name=readdirSync(folder).find(entry=>pattern.test(entry));
  if(!name)return null;
  const data=JSON.parse(readFileSync(join(folder,name),'utf8'));
  const receipt=data?.snapshot_receipt??data?.pair_receipt;
  if(typeof receipt?.canonical_json!=='string'
     ||receipt.sha256!==createHash('sha256').update(receipt.canonical_json,'utf8').digest('hex')
     ||receipt.bytes!==Buffer.byteLength(receipt.canonical_json,'utf8'))
   throw Error('Downloaded S9 JSON has an incomplete or invalid SHA receipt');
  return {name,data};
 },180);
}

async function stopChild(child,timeoutMs=2500){
 if(!child||child.exitCode!==null||child.signalCode!==null)return;
 // On Windows kill() requests termination but does not wait for process exit.
 // Wait for close (stdio/process handles released) before deleting its profile.
 await new Promise(resolve=>{
  let finished=false;
  const finish=()=>{
   if(finished)return;
   finished=true;
   clearTimeout(timer);
   child.off('close',finish);
   child.off('error',finish);
   resolve();
  };
  const timer=setTimeout(finish,timeoutMs);
  child.once('close',finish);
  child.once('error',finish);
  try{child.kill();}catch(_){finish();}
 });
}

// The real OS, not a speculative free-port probe, selects --port 0.
// Only capture the two public banner lines; never print process output or
// diagnostic URLs from failed launchers (they may include untrusted inputs).
function launchScienceOnly(dbPath,resumeGuestQuery=null){
 const args=['-B','-u','run_demo.py','--science-only','--port','0','--db',dbPath];
 if(resumeGuestQuery!==null)args.push('--resume-guest-query',resumeGuestQuery);
 const child=spawn('python',args,{
  cwd:ROOT,env:PYENV,stdio:['ignore','pipe','ignore'],windowsHide:true
 });
 const lines=[];
 let buffer='';
 child.stdout.setEncoding('utf8');
 child.stdout.on('data',chunk=>{
  buffer=(buffer+chunk).slice(-4096);
  for(let n=buffer.indexOf('\n');n!==-1;n=buffer.indexOf('\n')){
   const line=buffer.slice(0,n).trim();
   buffer=buffer.slice(n+1);
   if(line.startsWith('Politics Fantasy League · ')
      ||line.startsWith('REANUDAR CONSULTA CIENTÍFICA · '))
    lines.push(line.slice(0,1024));
  }
 });
 child.on('error',()=>{/* A bounded poll reports a failed startup safely. */});
 return {child,lines};
}

async function advertisedScienceLink(launcher,{resume=false}={}){
 const banner=await poll(()=>{
  if(launcher.child.exitCode!==null||launcher.child.signalCode!==null)
   throw Error('SCIENCE_ONLY_LAUNCHER_EXITED');
  const line=launcher.lines.find(x=>x.startsWith('Politics Fantasy League · '));
  if(!line)return null;
  const match=line.match(/http:\/\/127\.0\.0\.1:(\d{1,5})(?:\s|$)/);
  return match?Number(match[1]):null;
 },150);
 assert.ok(Number.isInteger(banner)&&banner>0&&banner<65536);
 const base='http://127.0.0.1:'+banner;
 let link=null;
 if(resume){
  const announced=await poll(()=>{
   if(launcher.child.exitCode!==null||launcher.child.signalCode!==null)
    throw Error('SCIENCE_ONLY_RESUME_EXITED');
   const line=launcher.lines.find(x=>x.startsWith('REANUDAR CONSULTA CIENTÍFICA · '));
   return line||null;
  },150);
  link=announced.split(' · ').slice(1).join(' · ').trim();
  const parsed=new URL(link);
  assert.equal(parsed.origin,base,'Resume banner MUST use actual OS-bound port');
  assert.equal(parsed.pathname,'/');
  assert.equal(parsed.hash,'');
 }
 await poll(async()=>{
  const response=await fetch(base+'/api/session',{signal:AbortSignal.timeout(1200)});
  return response.status===401&&(await response.json()).science_only===true;
 },150);
 return {base,port:banner,link};
}

test('S9 Chrome native CDP: live DOM observes registry late/early, source family, valid_at and 503', {
 timeout:70000
},async t=>{
 if(!existsSync(CHROME)||typeof WebSocket!=='function'){
  t.skip('Local Chrome or builtin WebSocket not available');return;
 }
 const scratch=mkdtempSync(join(tmpdir(),'pfl-s9-chrome-'));
 const registryDb=join(scratch,'synthetic.sqlite3');
 const downloadsDir=join(scratch,'downloads');
 mkdirSync(downloadsDir);
 let base='http://127.0.0.1';
 let failRegistry=false,chrome=null,socket=null,scienceServer=null;
 let bookmarkedGuestUrl=null;
 const observedRequests=[];
 const browserRequests=[];
 const server=httpServer((req,res)=>{
  const url=new URL(req.url,base);
  observedRequests.push({method:req.method,path:url.pathname,search:url.search});
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
  // Keep the HTTP port reserved while obtaining the CDP port: two successive
  // "find free port then close" calls could otherwise return the same port.
  await new Promise(resolve=>server.listen(0,'127.0.0.1',resolve));
  const port=server.address().port;
  base='http://127.0.0.1:'+port;
  let cdpPort=await freePort();
  while(cdpPort===port)cdpPort=await freePort();
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
  },180);
  socket=new WebSocket(target.webSocketDebuggerUrl);
  await new Promise((resolve,reject)=>{
   socket.addEventListener('open',resolve,{once:true});
   socket.addEventListener('error',reject,{once:true});
  });
  let nextId=0;
  const waiting=new Map();
  let pageLoadEvents=0;
  socket.addEventListener('message',event=>{
   const message=JSON.parse(event.data);
   if(message.method==='Page.loadEventFired')pageLoadEvents++;
   if(message.method==='Network.requestWillBeSent'){
    const req=message.params?.request;
    if(req)browserRequests.push({method:req.method,url:req.url});
   }
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
  await cdp('Network.enable');
  await cdp('Page.enable');
  await cdp('Browser.setDownloadBehavior',{behavior:'allow',
    downloadPath:downloadsDir,eventsEnabled:true});
  await poll(()=>js("Boolean(document.querySelector('#auth-form'))"));
  // Real Chrome anonymous entry: no JS state injection, no login, no account.
  // The local HTTP facade also records every request Chrome makes, including
  // unexpected POST/state calls that an ordinary successful fetch test misses.
  assert.equal(await js("document.querySelector('#auth-form')!==null && !ui.session && !ui.state"),true);
  assert.equal(await js("document.querySelector('[data-action=\"guest-enter\"]')!==null"),true);
  const guestStart=observedRequests.length;
  await js("document.querySelector('[data-action=\"guest-enter\"]').click();true");
  await poll(()=>js("Boolean(ui.guest && !ui.session && !ui.csrf && !ui.state && ui.scientific && ui.scienceRegistry && !ui.scienceRegistryError)"));
  assert.equal(await js("ui.scientific.R5==='STOP_R5' && ui.scienceRegistry.R5==='STOP_R5'"),true);
  assert.equal(await js("document.getElementById('account-name').innerText==='VISITANTE'"),true);
  assert.equal(await js("document.getElementById('club-select').hidden && document.getElementById('account-logout').hidden"),true);
  assert.equal(await js("document.getElementById('guest-exit').hidden"),false);
  assert.equal(await js("[...document.querySelectorAll('[data-tab]')].filter(n=>!n.hidden).map(n=>n.dataset.tab).join(',')"),'observatory,scientific');
  assert.equal(await js("getComputedStyle(document.querySelector('[data-tab=\"market\"]')).display==='none'"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('R5 STOP')"),true);
  assert.equal(await js("(()=>{const b=document.querySelector('[data-action=\"science-registry-export\"]');return Boolean(b&&!b.disabled);})()"),true);
  // A narrow mobile viewport still exposes the guest export without
  // accidentally revealing the hidden account/market navigation.
  await cdp('Emulation.setDeviceMetricsOverride',{width:390,height:844,
    deviceScaleFactor:1,mobile:true});
  assert.equal(await js("(()=>{const b=document.querySelector('[data-action=\"science-registry-export\"]');return Boolean(b&&!b.disabled&&b.getBoundingClientRect().width>0&&getComputedStyle(b).display!=='none');})()"),true);
  assert.equal(await js("getComputedStyle(document.querySelector('[data-tab=\"market\"]')).display==='none'"),true);
  await cdp('Emulation.clearDeviceMetricsOverride');
  // The browser itself checks the canonical SHA-256; this assertion separately
  // recalculates the hash on the visible snapshot in native WebCrypto.
  assert.equal(await js(`(async()=>{
    const x=ui.scienceRegistry,r=x.snapshot_receipt;
    const bytes=new TextEncoder().encode(r.canonical_json);
    const sha=Array.from(new Uint8Array(await crypto.subtle.digest('SHA-256',bytes)))
      .map(b=>b.toString(16).padStart(2,'0')).join('');
    return r.sha256===sha && x.snapshot_receipt_sha256===sha && bytes.length===r.bytes;
  })()`),true);
  // The anonymous Observatorio compares two independently verified S9
  // projections in the real DOM. This precedes the historical auth spoof
  // and preserves the original single-snapshot download journey below.
  assert.equal(await js("(()=>{const n=document.querySelector('[data-action=\"science-registry-tab\"][data-registry=\"compare\"]');return Boolean(n&&n.getAttribute('aria-pressed')==='false'&&n.textContent.includes('Comparar cortes'));})()"),true);
  const compareStart=observedRequests.length;
  await js("document.querySelector('[data-action=\"science-registry-tab\"][data-registry=\"compare\"]').click();true");
  await poll(()=>js("Boolean(!ui.scienceRegistryCompareLoading&&(ui.scienceRegistryComparison||ui.scienceRegistryCompareError))"));
  assert.equal(await js('ui.scienceRegistryCompareError'),null,'Both WebCrypto S9 comparisons must validate');
  await poll(()=>js("Boolean(ui.scienceRegistryComparison&&document.querySelector('[aria-label=\"Comparación bitemporal de registros S9\"]')?.textContent.includes('Solo visible en late'))"));
  const compareDom=await js("(()=>{const n=document.querySelector('[aria-label=\"Comparación bitemporal de registros S9\"]');return {tab:ui.scienceRegistryTab,exists:Boolean(n),hasLabel:Boolean(n?.textContent.includes('Solo visible en late')),hasHtml:Boolean(n?.innerHTML.includes('Solo visible en late')),hasSummary:Boolean(n?.textContent.includes('Descriptores revisados'))};})()");
  assert.equal(compareDom.tab,'compare');
  assert.equal(compareDom.exists,true);
  assert.equal(compareDom.hasLabel,true,'Chrome comparison DOM: '+JSON.stringify(compareDom));
  assert.equal(await js("document.querySelector('[data-registry=\"compare\"]').getAttribute('aria-pressed')"),'true');
  assert.equal(await js("document.querySelector('[aria-label=\"Comparación bitemporal de registros S9\"]').textContent.includes('Comparar cortes')"),true);
  const compared=await js("(()=>{const x=ui.scienceRegistryComparison;return {queries:x.queries,early:x.early,late:x.late};})()");
  assert.equal(compared.early.registry.visible_distribution_count,2);
  assert.equal(compared.late.registry.visible_distribution_count,6);
  assert.equal(compared.early.cut,'early');
  assert.equal(compared.late.cut,'late');
  for(const [cut,snapshot] of [['early',compared.early],['late',compared.late]]){
   const receipt=snapshot.snapshot_receipt;
   const canonical=Buffer.from(receipt.canonical_json,'utf8');
   assert.equal(createHash('sha256').update(canonical).digest('hex'),receipt.sha256,
    cut+' independent Node SHA-256');
   assert.equal(canonical.length,receipt.bytes);
   assert.equal(receipt.sha256,snapshot.snapshot_receipt_sha256);
   assert.equal(receipt.external_authenticity_certified,false);
   assert.equal(snapshot.R5,'STOP_R5');
   assert.equal(snapshot.release_gates_passed,0);
   assert.equal(snapshot.scientific_ab_cycles,0);
  }
  assert.equal(await js("document.querySelector('#content').textContent.includes('Solo visible en late')"),true);
  assert.equal(await js("document.querySelector('#content').textContent.includes('S9:PUBLIC_06')"),true);
  assert.equal(await js("ui.scienceRegistry.registry.visible_distribution_count===6&&ui.state===null&&ui.session===null"),true);
  assert.deepEqual(observedRequests.slice(compareStart).filter(r=>
   r.method!=='GET'||r.path!=='/api/scientific-registry'),[]);
  assert.equal(observedRequests.slice(compareStart).filter(r=>
   r.path==='/api/scientific-registry').length,2);
  // Real Chrome click -> ONE physical paired download -> independently
  // recomputed envelope/children digests -> offline Python --pair CLI PASS.
  assert.equal(await js("(()=>{const b=document.querySelector('[data-action=\"science-registry-pair-export\"]');return Boolean(b&&!b.disabled&&b.textContent.includes('Descargar pareja verificable'));})()"),true);
  await js("document.querySelector('[data-action=\"science-registry-pair-export\"]').scrollIntoView({block:'center'});true");
  const pairPoint=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-pair-export\"]').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
   x:pairPoint.x,y:pairPoint.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
   x:pairPoint.x,y:pairPoint.y,button:'left',clickCount:1});
  const {name:pairSaved,data:pairExport}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-pair-2026-09-15-[a-f0-9]{12}\.json$/);
  assert.equal(pairExport.schema,'pfl.synthetic_scientific_registry_browser_pair_export.v1');
  assert.equal(pairExport.comparison_kind,'AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE');
  assert.deepEqual(Object.keys(pairExport.exports).sort(),['early','late']);
  assert.equal(pairExport.R5,'STOP_R5');
  assert.equal(pairExport.release_gates_passed,0);
  assert.equal(pairExport.scientific_ab_cycles,0);
  assert.equal(pairExport.rights_for_public_display_admitted,false);
  assert.equal(pairExport.external_authenticity_certified,false);
  assert.equal(createHash('sha256').update(pairExport.pair_receipt.canonical_json,'utf8').digest('hex'),
   pairExport.pair_receipt.sha256);
  assert.equal(Buffer.byteLength(pairExport.pair_receipt.canonical_json,'utf8'),
   pairExport.pair_receipt.bytes);
  for(const cut of ['early','late']){
   const nested=pairExport.exports[cut];
   assert.equal(nested.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
   assert.equal(nested.query.cut,cut);
   assert.equal(nested.query.valid_at,'2026-09-15');
   assert.equal(nested.query.family,'all');
   assert.equal(nested.snapshot_receipt.sha256,compared[cut].snapshot_receipt.sha256);
   assert.equal(createHash('sha256').update(nested.snapshot_receipt.canonical_json,'utf8').digest('hex'),
    nested.snapshot_receipt.sha256);
  }
  const offlinePair=JSON.parse(python(['scripts/compare_scientific_exports.py',
   '--pair',join(downloadsDir,pairSaved)]));
  assert.equal(offlinePair.status,'PASS');
  assert.equal(offlinePair.pair_sha256,pairExport.pair_receipt.sha256);
  assert.equal(offlinePair.early.sha256,pairExport.exports.early.snapshot_receipt.sha256);
  assert.equal(offlinePair.late.sha256,pairExport.exports.late.snapshot_receipt.sha256);
  assert.equal(offlinePair.rights_for_public_display_admitted,false);
  assert.equal(offlinePair.scientific_ab_cycles,0);
  unlinkSync(join(downloadsDir,pairSaved));
  // A filter change must remove BOTH previous projections, not merely hide
  // their panel while retaining stale receipts in memory.
  await js("(()=>{const n=document.getElementById('science-registry-family');n.value='CHAIN';n.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scienceRegistry&&ui.scienceRegistryFamily==='CHAIN'&&!ui.scienceRegistryLoading&&ui.scienceRegistryComparison===null&&document.querySelector('#content').textContent.includes('Selecciona «Consultar ambos cortes verificados»'))"));
  assert.equal(await js("document.querySelector('#content').textContent.includes('Solo visible en late')"),false);
  assert.equal(await js("document.querySelector('#content').textContent.includes('Selecciona «Consultar ambos cortes verificados»')"),true);
  await js("document.querySelector('[data-action=\"science-registry-compare-load\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistryComparison&&!ui.scienceRegistryCompareLoading&&ui.scienceRegistryComparison.late.family==='CHAIN'&&document.querySelector('#content').textContent.includes('Descriptores revisados'))"));
  // Failure of either paired query must clear a previously valid pair and
  // display only the fail-closed alert, never its former descriptor rows.
  failRegistry=true;
  await js("document.querySelector('[data-action=\"science-registry-compare-load\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistryCompareError&&ui.scienceRegistryCompareError.includes('503')&&!ui.scienceRegistryCompareLoading&&document.querySelector('#content').textContent.includes('Comparación invalidada'))"));
  assert.equal(await js('ui.scienceRegistryComparison===null'),true);
  assert.equal(await js("document.querySelector('[aria-label=\"Comparación bitemporal de registros S9\"] [role=\"alert\"]')!==null"),true);
  assert.equal(await js("document.querySelector('#content').textContent.includes('Comparación invalidada')"),true);
  assert.equal(await js("document.querySelector('#content').textContent.includes('Descriptores revisados')"),false);
  failRegistry=false;
  await js("(()=>{const n=document.getElementById('science-registry-family');n.value='all';n.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
  await poll(()=>js("Boolean(ui.scienceRegistry&&!ui.scienceRegistryLoading&&ui.scienceRegistryFamily==='all'&&ui.scienceRegistry.registry.visible_distribution_count===6&&document.querySelector('[data-registry=\"sources\"]'))"));
  await js("document.querySelector('[data-action=\"science-registry-tab\"][data-registry=\"sources\"]').click();true");
  assert.equal(await js("document.querySelector('[data-registry=\"sources\"]').getAttribute('aria-pressed')"),'true');
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),true);
  assert.equal(await js("(()=>{const b=document.querySelector('[data-action=\"science-registry-export\"]');return Boolean(b&&!b.disabled);})()"),true);
  // The anonymous visitor uses the actual Chrome mouse and download manager.
  // The saved JSON is verified independently of app.js and removed before the
  // existing authenticated test downloads a file with the same basename.
  await js("document.querySelector('[data-action=\"science-registry-export\"]').scrollIntoView({block:'center'});true");
  const guestPoint=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-export\"]').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
    x:guestPoint.x,y:guestPoint.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
    x:guestPoint.x,y:guestPoint.y,button:'left',clickCount:1});
  const {name:guestSaved,data:guestExport}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/);
  const guestCanonical=Buffer.from(guestExport.snapshot_receipt.canonical_json,'utf8');
  assert.equal(guestExport.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(guestExport.source_contract,'pfl.synthetic_scientific_registry.v1');
  assert.equal(guestExport.evidence_class,'SYNTHETIC_LAB_ONLY');
  assert.equal(guestExport.R5,'STOP_R5');
  assert.equal(guestExport.release_gates_passed,0);
  assert.equal(guestExport.scientific_ab_cycles,0);
  assert.equal(guestExport.rights_for_public_display_admitted,false);
  assert.equal(guestExport.external_authenticity_certified,false);
  assert.equal(guestExport.query.cut,'late');
  assert.equal(guestExport.query.family,'all');
  assert.equal(guestExport.query.valid_at,'2026-09-15');
  assert.equal(createHash('sha256').update(guestCanonical).digest('hex'),
    guestExport.snapshot_receipt.sha256);
  assert.equal(guestCanonical.length,guestExport.snapshot_receipt.bytes);
  assert.match(guestSaved,new RegExp(guestExport.snapshot_receipt.sha256.slice(0,12)));
  assert.doesNotMatch(JSON.stringify(guestExport),/SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
  // Independent offline acceptance: the actual browser-downloaded bytes
  // must pass the stdlib-only S9 verifier, not just the in-app WebCrypto SHA.
  const offlineGuest=JSON.parse(python(['scripts/verify_scientific_snapshot.py',
   join(downloadsDir,guestSaved)]));
  assert.equal(offlineGuest.status,'PASS');
  assert.equal(offlineGuest.sha256,guestExport.snapshot_receipt.sha256);
  assert.equal(offlineGuest.cut,'late');
  assert.equal(offlineGuest.synthetic_only,true);
  unlinkSync(join(downloadsDir,guestSaved));
  await js("document.querySelector('[data-tab=\"scientific\"]').click();true");
  await poll(()=>js("Boolean(ui.guest && ui.tab==='scientific' && document.querySelector('#content').innerText.includes('Testigos diferenciales sintéticos'))"));
  assert.equal(await js("document.querySelector('#content').innerText.includes('B0 y B3')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('S7_NEITHER_APPROVED')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('S7_CONFLICT_SAME_TERMINAL_DAY')"),true);
  assert.equal(await js("document.querySelector('[data-action=\"science-export\"]')===null && document.querySelector('[data-action=\"science-probe\"]')===null"),true);
  await js("document.querySelector('[data-tab=\"observatory\"]').click();true");
  assert.equal(await js("ui.guest && ui.tab==='observatory' && document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),true);
  // User-driven, NONDEFAULT guest selection. These are ordinary DOM change
  // events, not injected UI state; the URL must encode the closed seven-key
  // selection in order, including the comparison view, without evidence bytes.
  const selectGuest=async (id,value,ready)=>{
   const changed=await js("(()=>{const e=document.getElementById("+JSON.stringify(id)+");"
    +"if(!e||![...e.options].some(o=>o.value==="+JSON.stringify(value)+"))return false;"
    +"e.value="+JSON.stringify(value)+";e.dispatchEvent(new Event('change',{bubbles:true}));return true;})()");
   assert.equal(changed,true,'Guest filter control must be present: '+id);
   await poll(()=>js(ready));
  };
  // 'science-cut' lives in the scientific Laboratory toolbar, while source
  // family/valid_at/publication live in the Observatory registry toolbar.
  await js("document.querySelector('[data-tab=\"scientific\"]').click();true");
  await poll(()=>js("Boolean(ui.guest&&ui.tab==='scientific'&&document.getElementById('science-cut'))"));
  await selectGuest('science-cut','early',
   "Boolean(ui.guest&&ui.scienceCut==='early'&&ui.scientific?.cut==='early'&&ui.scienceRegistry?.cut==='early'&&!ui.scienceRegistryLoading)");
  await js("document.querySelector('[data-tab=\"observatory\"]').click();true");
  await poll(()=>js("Boolean(ui.guest&&ui.tab==='observatory'&&document.getElementById('science-registry-valid'))"));
  await selectGuest('science-registry-valid','2026-10-10',
   "Boolean(ui.scienceRegistry?.valid_at==='2026-10-10'&&!ui.scienceRegistryLoading)");
  await selectGuest('science-registry-family','CHAIN',
   "Boolean(ui.scienceRegistry?.family==='CHAIN'&&!ui.scienceRegistryLoading)");
  await selectGuest('science-registry-publication','2026-09-19T12:00:00Z',
   "Boolean(ui.scienceRegistry?.published_until==='2026-09-19T12:00:00Z'&&!ui.scienceRegistryLoading)");
  await js("document.querySelector('[data-action=\"science-registry-tab\"][data-registry=\"compare\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistryTab==='compare'&&!ui.scienceRegistryCompareLoading&&ui.scienceRegistryComparison&&!ui.scienceRegistryCompareError)"));
  const chosenUrl=await js('location.href');
  const chosen=new URL(chosenUrl);
  const allowedKeys=['pfl_guest','cut','valid_at','family','published_until','scenario','view'];
  const expectedSelection=['v1','early','2026-10-10','CHAIN',
   '2026-09-19T12:00:00Z','baseline','compare'];
  assert.deepEqual([...chosen.searchParams.keys()],allowedKeys);
  assert.deepEqual([...chosen.searchParams.values()],expectedSelection);
  assert.equal(chosen.origin,base);
  assert.equal(chosen.pathname,'/');
  bookmarkedGuestUrl=chosenUrl;
  assert.doesNotMatch(chosenUrl,/SYN:|AUTHOR_|csrf|password|source_id|account/i);
  const forbidden=observedRequests.slice(guestStart).filter(r=>
    r.method!=='GET' || !['/api/scientific-integration-lab','/api/scientific-registry'].includes(r.path));
  assert.deepEqual(forbidden,[], 'Guest session has no /api/state, POST, login or registration calls');
  assert.equal(await js("ui.state===null && ui.csrf===null && ui.session===null"),true);
  await js("document.getElementById('guest-exit').click();true");
  await poll(()=>js("Boolean(!ui.guest && document.querySelector('#auth-form') && document.querySelector('[data-action=\"guest-enter\"]'))"));
  assert.equal(await js("document.getElementById('navigation').hidden"),true);
  assert.equal(await js("document.getElementById('guest-exit').hidden"),true);
  assert.equal(await js("ui.state===null && ui.scientific===null && ui.scienceRegistry===null"),true);
  assert.deepEqual(observedRequests.slice(guestStart).filter(r=>r.method!=='GET'||r.path==='/api/state'||r.path==='/api/register'||r.path==='/api/login'),[]);
  // Reload the ACTUAL bookmarked query in the SAME Chrome target, with no
  // synthetic JS state injection. Waiting on Page.loadEventFired and fully
  // verified DOM avoids treating an old execution context as a new visit.
  const navigateAndLoad=async (url=null)=>{
   const before=pageLoadEvents;
   if(url===null)await cdp('Page.reload',{ignoreCache:true});
   else await cdp('Page.navigate',{url});
   await poll(()=>pageLoadEvents>before);
  };
  const explicitAnonymousGuestEntry=async()=>{
   // The ordinary (accounts-enabled) 401 must still show LOGIN. A bookmark
   // cannot silently open a session or treat URL parameters as credentials.
   await poll(()=>js("Boolean(!ui.guest&&ui.state===null&&ui.session===null&&document.querySelector('#auth-form')&&document.querySelector('[data-action=\"guest-enter\"]'))"));
   await js("document.querySelector('[data-action=\"guest-enter\"]').click();true");
  };
  const restoredFromBrowser=async()=>{
   await poll(()=>js("Boolean(ui.guest&&!ui.guestUrlError&&ui.state===null&&ui.session===null&&ui.csrf===null&&ui.tab==='observatory'&&ui.scienceCut==='early'&&ui.scienceRegistryValid==='2026-10-10'&&ui.scienceRegistryFamily==='CHAIN'&&ui.scienceRegistryPublished==='2026-09-19T12:00:00Z'&&ui.scienceRegistryTab==='compare'&&ui.scientific?.cut==='early'&&ui.scienceRegistry?.cut==='early'&&!ui.scienceRegistryLoading&&ui.scienceRegistryComparison&&!ui.scienceRegistryCompareLoading&&!ui.scienceRegistryCompareError&&document.querySelector('[data-action=\"science-registry-pair-export\"]'))"));
   const receipts=await js("(()=>({current:ui.scienceRegistry,early:ui.scienceRegistryComparison.early,late:ui.scienceRegistryComparison.late}))()");
   for(const [name,body] of Object.entries(receipts)){
    const rec=body.snapshot_receipt;
    const bytes=Buffer.from(rec.canonical_json,'utf8');
    assert.equal(rec.bytes,bytes.length,name+' canonical UTF8 byte count');
    assert.equal(rec.sha256,createHash('sha256').update(bytes).digest('hex'),
     name+' independently recomputed Node SHA-256');
    assert.equal(body.snapshot_receipt_sha256,rec.sha256);
    assert.equal(body.R5,'STOP_R5');
    assert.equal(body.release_gates_passed,0);
    assert.equal(body.scientific_ab_cycles,0);
    assert.equal(body.family,'CHAIN');
    assert.equal(body.valid_at,'2026-10-10');
    assert.equal(body.published_until,'2026-09-19T12:00:00Z');
   }
   assert.equal(receipts.early.cut,'early');
   assert.equal(receipts.late.cut,'late');
   assert.equal(receipts.current.cut,'early');
   assert.equal(receipts.early.registry.visible_distribution_count,1);
   assert.equal(receipts.late.registry.visible_distribution_count,1);
   assert.deepEqual([...new URL(await js('location.href')).searchParams.values()],
    expectedSelection);
   return receipts;
  };
  const assertFreshBrowserGets=(begin)=>{
   const seen=observedRequests.slice(begin);
   const reg=seen.filter(x=>x.method==='GET'&&x.path==='/api/scientific-registry');
   assert.ok(reg.length>=3,'Guest restore must issue current+two fresh registry GETs');
   for(const cut of ['early','late']){
    const matches=reg.filter(x=>{
     const q=new URLSearchParams(x.search);
     return q.get('cut')===cut&&q.get('family')==='CHAIN'
      &&q.get('valid_at')==='2026-10-10'
      &&q.get('published_until')==='2026-09-19T12:00:00Z';
    });
    assert.ok(matches.length>0,'Missing new SHA-backed '+cut+' GET');
   }
   assert.ok(seen.some(x=>x.path==='/api/scientific-integration-lab'));
   assert.deepEqual(seen.filter(x=>x.method!=='GET'
    ||['/api/state','/api/register','/api/login'].includes(x.path)),[]);
   return reg.length;
  };
  const bookmarkStart=observedRequests.length;
  await navigateAndLoad(bookmarkedGuestUrl);
  assert.deepEqual(observedRequests.slice(bookmarkStart).filter(r=>
   ['/api/scientific-registry','/api/scientific-integration-lab'].includes(r.path)),[],
   'Ordinary anonymous URL must not query science before explicit guest entry');
  await explicitAnonymousGuestEntry();
  const firstRestore=await restoredFromBrowser();
  const firstReloadGets=assertFreshBrowserGets(bookmarkStart);
  const reloadStart=observedRequests.length;
  await navigateAndLoad();
  await explicitAnonymousGuestEntry();
  const secondRestore=await restoredFromBrowser();
  const secondReloadGets=assertFreshBrowserGets(reloadStart);
  for(const name of ['current','early','late']){
   assert.equal(firstRestore[name].snapshot_receipt.sha256,
    secondRestore[name].snapshot_receipt.sha256,
    'Page.reload must revalidate the same authored public projection');
  }
  // A real 503 *after* navigation must preserve the selected query yet erase
  // all old receipts and the export control. Browser retry obtains NEW GETs.
  failRegistry=true;
  await navigateAndLoad();
  await explicitAnonymousGuestEntry();
  await poll(()=>js("Boolean(ui.guest&&ui.scienceRegistry===null&&ui.scienceRegistryComparison===null&&ui.scienceRegistryError?.includes('503')&&document.querySelector('#content [role=\"alert\"]')&&document.querySelector('[data-action=\"guest-reload\"]')&&!document.querySelector('[data-action=\"science-registry-pair-export\"]'))"));
  assert.deepEqual([...new URL(await js('location.href')).searchParams.values()],
   expectedSelection);
  failRegistry=false;
  const retryStart=observedRequests.length;
  await js("document.querySelector('[data-action=\"guest-reload\"]').click();true");
  await poll(()=>js("Boolean(ui.guest&&ui.scienceRegistry&&!ui.scienceRegistryError&&!ui.scienceRegistryLoading&&document.querySelector('[data-action=\"science-registry-compare-load\"]'))"));
  await js("document.querySelector('[data-action=\"science-registry-compare-load\"]').click();true");
  await restoredFromBrowser();
  const recoveredGets=assertFreshBrowserGets(retryStart);
  // The recovered pair is downloaded by real Chrome, then independently
  // parsed and verified by the UNMODIFIED Python offline --pair CLI.
  await js("document.querySelector('[data-action=\"science-registry-pair-export\"]').scrollIntoView({block:'center'});true");
  const freshPoint=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-pair-export\"]').getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
   x:freshPoint.x,y:freshPoint.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
   x:freshPoint.x,y:freshPoint.y,button:'left',clickCount:1});
  const {name:restoredPairFile,data:restoredPair}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-pair-2026-10-10-[a-f0-9]{12}\.json$/);
  assert.equal(restoredPair.pair_receipt.sha256,
   createHash('sha256').update(restoredPair.pair_receipt.canonical_json,'utf8').digest('hex'));
  assert.equal(restoredPair.pair_receipt.bytes,
   Buffer.byteLength(restoredPair.pair_receipt.canonical_json,'utf8'));
  assert.equal(restoredPair.exports.early.query.family,'CHAIN');
  assert.equal(restoredPair.exports.late.query.valid_at,'2026-10-10');
  const offlineRestored=JSON.parse(python(['scripts/compare_scientific_exports.py',
   '--pair',join(downloadsDir,restoredPairFile)]));
  assert.equal(offlineRestored.status,'PASS');
  assert.equal(offlineRestored.pair_sha256,restoredPair.pair_receipt.sha256);
  assert.equal(offlineRestored.early.sha256,restoredPair.exports.early.snapshot_receipt.sha256);
  assert.equal(offlineRestored.late.sha256,restoredPair.exports.late.snapshot_receipt.sha256);
  assert.equal(offlineRestored.publisher_identity_verified,false);
  assert.equal(offlineRestored.rights_for_public_display_admitted,false);
  unlinkSync(join(downloadsDir,restoredPairFile));
  // Malformed URL intent is rejected BEFORE any scientific GET or cached
  // results. An explicit reset produces only safe default guest parameters.
  const unknown=new URL(bookmarkedGuestUrl);unknown.searchParams.set('unknown','x');
  const future=new URL(bookmarkedGuestUrl);
  future.searchParams.set('published_until','2026-10-30T12:00:00Z');
  const wrongFamily=new URL(bookmarkedGuestUrl);
  wrongFamily.searchParams.set('family','REAL_ACTORS');
  const invalidUrls=[
   bookmarkedGuestUrl+'&cut=late',
   unknown.href,
   future.href,
   wrongFamily.href,
  ];
  for(const invalidUrl of invalidUrls){
   const invalidBegin=observedRequests.length;
   await navigateAndLoad(invalidUrl);
   await explicitAnonymousGuestEntry();
   await poll(()=>js("Boolean(ui.guest&&ui.guestUrlError&&ui.scientific===null&&ui.scienceRegistry===null&&ui.scienceRegistryComparison===null&&document.querySelector('#content [role=\"alert\"]')&&document.querySelector('[data-action=\"guest-url-reset\"]'))"));
   assert.deepEqual(observedRequests.slice(invalidBegin).filter(x=>
    ['/api/scientific-registry','/api/scientific-integration-lab'].includes(x.path)),[],
    'Malformed guest URL must not trigger scientific GETs');
   await js("document.querySelector('[data-action=\"guest-url-reset\"]').click();true");
   await poll(()=>js("Boolean(ui.guest&&!ui.guestUrlError&&ui.scienceRegistry?.cut==='late'&&ui.scienceRegistryFamily==='all'&&ui.scienceRegistryValid==='2026-09-15'&&ui.scienceRegistryPublished==='as_of'&&ui.scientific?.cut==='late'&&!ui.scienceRegistryLoading)"));
   assert.deepEqual([...new URL(await js('location.href')).searchParams.values()],
    ['v1','late','2026-09-15','all','as_of','baseline','sources']);
  }
  assert.deepEqual(observedRequests.slice(bookmarkStart).filter(x=>
   x.method!=='GET'||['/api/state','/api/login','/api/register'].includes(x.path)),[]);
  // Restore original smoke precondition: a plain login screen, not a
  // deep-linked guest, before the established authenticated S9 probe.
  await navigateAndLoad(base+'/');
  await poll(()=>js("Boolean(!ui.guest&&ui.state===null&&document.querySelector('#auth-form')&&document.querySelector('[data-action=\"guest-enter\"]'))"));
  // Keep the pre-existing S9 native Chrome flow and export assertions unchanged.
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
  const {name:saved,data:exported}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/);
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
  // Test the real Python --science-only server in the same Chrome instance.
  // Its HTTP 401 opt-in must auto-enter guest mode with no fake authenticated
  // ui.state, and WebCrypto must permit a real browser download.
  unlinkSync(join(downloadsDir,saved));
  const scienceDir=join(scratch,'science-only');
  mkdirSync(scienceDir);
  const scienceDb=join(scienceDir,'science.db');
  const firstScienceLauncher=launchScienceOnly(scienceDb);
  scienceServer=firstScienceLauncher.child;
  const firstScienceLink=await advertisedScienceLink(firstScienceLauncher);
  let scienceBase=firstScienceLink.base;
  const firstSciencePort=firstScienceLink.port;
  const scienceStart=browserRequests.length;
  await cdp('Page.navigate',{url:scienceBase+'/'});
  await poll(()=>js("Boolean(ui.guest && ui.state===null && ui.session===null && ui.csrf===null && ui.scientific && ui.scienceRegistry && document.querySelector('[data-action=\"science-registry-export\"]'))"));
  assert.equal(await js("ui.scienceOnly===true && document.getElementById('guest-exit').hidden"),true);
  assert.equal(await js("document.querySelector('#auth-form')===null && document.getElementById('account-name').innerText==='VISITANTE'"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('S9:PUBLIC_06')"),true);
  assert.equal(await js("document.querySelector('[data-action=\"science-registry-export\"]').disabled"),false);
  await js("document.querySelector('[data-action=\"science-registry-export\"]').scrollIntoView({block:'center'});true");
  const sciencePoint=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-export\"]').getBoundingClientRect();return{x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
    x:sciencePoint.x,y:sciencePoint.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
    x:sciencePoint.x,y:sciencePoint.y,button:'left',clickCount:1});
  const {name:scienceSaved,data:scienceExport}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-registry-late-2026-09-15-[a-f0-9]{12}\.json$/);
  assert.equal(scienceExport.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(scienceExport.R5,'STOP_R5');
  assert.equal(scienceExport.release_gates_passed,0);
  assert.equal(scienceExport.external_authenticity_certified,false);
  assert.equal(createHash('sha256').update(scienceExport.snapshot_receipt.canonical_json,'utf8').digest('hex'),
    scienceExport.snapshot_receipt.sha256);
  assert.doesNotMatch(JSON.stringify(scienceExport),/SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
  assert.equal(existsSync(join(scienceDir,'accounts.sqlite3')),false,
    'Real --science-only runtime must not create an accounts database');
  const scienceRequests=browserRequests.slice(scienceStart)
   .filter(r=>r.url.startsWith(scienceBase)).map(r=>({
    method:r.method,path:new URL(r.url).pathname}));
  assert.ok(scienceRequests.some(r=>r.path==='/api/session'));
  assert.ok(scienceRequests.some(r=>r.path==='/api/scientific-integration-lab'));
  assert.ok(scienceRequests.some(r=>r.path==='/api/scientific-registry'));
  assert.deepEqual(scienceRequests.filter(r=>r.method!=='GET'||
    ['/api/state','/api/register','/api/login','/api/scientific-lab-export'].includes(r.path)),[]);
  await js("document.querySelector('[data-tab=\"scientific\"]').click();true");
  assert.equal(await js("document.querySelector('#content').innerText.includes('B0 y B3')"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('S7_NEITHER_APPROVED')"),true);
  await js("document.getElementById('guest-exit').click();true");
  assert.equal(await js("ui.guest && ui.scienceOnly && document.querySelector('#auth-form')===null && ui.scienceRegistry!==null"),true);
  assert.equal(await js("document.querySelector('#content').innerText.includes('Crear cuenta')"),false);
  // An actual science-only visitor CHOOSES its own nondefault filters in the
  // real DOM, then bookmarks the canonical URL. This first Python subprocess
  // has port=0 assigned by its bound listening socket, NOT by freePort().
  const scienceBefore=browserRequests.length;
  await selectGuest('science-cut','early',
   "Boolean(ui.guest&&ui.scienceOnly&&ui.scienceCut==='early'&&ui.scientific?.cut==='early'&&ui.scienceRegistry?.cut==='early'&&!ui.scienceRegistryLoading)");
  await js("document.querySelector('[data-tab=\"observatory\"]').click();true");
  await poll(()=>js("Boolean(ui.tab==='observatory'&&document.getElementById('science-registry-valid'))"));
  await selectGuest('science-registry-valid','2026-10-10',
   "Boolean(ui.scienceRegistry?.valid_at==='2026-10-10'&&!ui.scienceRegistryLoading)");
  await selectGuest('science-registry-family','CHAIN',
   "Boolean(ui.scienceRegistry?.family==='CHAIN'&&!ui.scienceRegistryLoading)");
  await selectGuest('science-registry-publication','2026-09-19T12:00:00Z',
   "Boolean(ui.scienceRegistry?.published_until==='2026-09-19T12:00:00Z'&&!ui.scienceRegistryLoading)");
  await js("document.querySelector('[data-action=\"science-registry-tab\"][data-registry=\"compare\"]').click();true");
  await poll(()=>js("Boolean(ui.scienceRegistryTab==='compare'&&!ui.scienceRegistryCompareLoading&&ui.scienceRegistryComparison&&!ui.scienceRegistryCompareError)"));
  const scienceBookmark=await js('location.href');
  assert.equal(new URL(scienceBookmark).origin,scienceBase);
  assert.deepEqual([...new URL(scienceBookmark).searchParams.values()],
   expectedSelection);
  // The executable never receives a private/receipt-bearing URL.
  assert.doesNotMatch(scienceBookmark,/SYN:|AUTHOR_|password|cookie|csrf|account/i);
  // Neither the browser nor this test synthesizes a registry result.
  const freshScienceGets=(begin)=>{
   const seen=browserRequests.slice(begin).filter(r=>r.url.startsWith(scienceBase));
   const registry=seen.filter(r=>r.method==='GET'
    &&new URL(r.url).pathname==='/api/scientific-registry');
   assert.ok(registry.length>=3,'Science-only must re-fetch current and two compare receipts');
   for(const cut of ['early','late']){
    assert.ok(registry.some(request=>{
     const q=new URL(request.url).searchParams;
     return q.get('cut')===cut&&q.get('valid_at')==='2026-10-10'
      &&q.get('family')==='CHAIN'
      &&q.get('published_until')==='2026-09-19T12:00:00Z';
    }),'Missing restored '+cut+' cut in real Python HTTP');
   }
   assert.ok(seen.some(r=>new URL(r.url).pathname==='/api/scientific-integration-lab'));
   assert.deepEqual(seen.filter(r=>r.method!=='GET'
    ||['/api/state','/api/register','/api/login'].includes(new URL(r.url).pathname)),[]);
   return registry.length;
  };
  const scienceOriginal=await restoredFromBrowser();
  assert.equal(await js("ui.scienceOnly===true&&document.getElementById('guest-exit').hidden"),true);
  const originalScienceGets=freshScienceGets(scienceBefore);
  const originalScienceDigest=scienceOriginal.current.snapshot_receipt.sha256;
  const originalPairDigests=['early','late'].map(k=>
   scienceOriginal[k].snapshot_receipt.sha256);
  const previousServerPid=scienceServer.pid;
  await stopChild(scienceServer);
  scienceServer=null;
  const durableRegistry=join(scienceDir,'scientific_registry_synthetic.sqlite3');
  assert.equal(existsSync(durableRegistry),true);
  const originalDbDigest=createHash('sha256').update(readFileSync(durableRegistry)).digest('hex');
  // Invalid resume instructions fail BEFORE binding any listener. A rejected
  // input must not print a startup banner, create SQLite or fetch science.
  const malformedResume=[
   scienceBookmark+'&rights_for_public_display_admitted=true',
   scienceBookmark+'&unknown_selection=1',
   'http://example.invalid:49321/'+new URL(scienceBookmark).search,
  ];
  const beforeBadLauncherRequests=browserRequests.length;
  for(const [index,badUrl] of malformedResume.entries()){
   const unusableDb=join(scienceDir,'invalid-'+index,'science.db');
   const rejected=spawnSync('python',['-B','run_demo.py','--science-only',
    '--port','0','--db',unusableDb,'--resume-guest-query',badUrl],{
    cwd:ROOT,env:PYENV,encoding:'utf8',timeout:6000,windowsHide:true
   });
   assert.equal(rejected.error,undefined,'Rejected launcher must terminate cleanly');
   assert.equal(rejected.status,2,'Invalid query rejected before socket binding');
   assert.doesNotMatch(rejected.stdout||'',/Politics Fantasy League ·|REANUDAR CONSULTA CIENTÍFICA ·/);
   assert.doesNotMatch(rejected.stderr||'',/rights_for_public_display_admitted|unknown_selection|example\.invalid|SYN:|AUTHOR_/);
   assert.equal(existsSync(unusableDb),false);
   assert.equal(existsSync(join(scienceDir,'invalid-'+index)),false);
  }
  assert.equal(browserRequests.length,beforeBadLauncherRequests,
   'Rejected launcher must not contact the existing browser or issue science GETs');
  // A *second independent* port 0 is now bound by the OS: reuse the same
  // SQLite directory, not the old socket number or the old browser origin.
  const secondScienceLauncher=launchScienceOnly(scienceDb,scienceBookmark);
  scienceServer=secondScienceLauncher.child;
  const newScienceLink=await advertisedScienceLink(secondScienceLauncher,{resume:true});
  assert.notEqual(scienceServer.pid,previousServerPid);
  scienceBase=newScienceLink.base;
  const resumedUrl=new URL(newScienceLink.link);
  assert.equal(resumedUrl.origin,scienceBase);
  assert.equal(Number(resumedUrl.port),newScienceLink.port);
  assert.deepEqual([...resumedUrl.searchParams.keys()],allowedKeys);
  assert.deepEqual([...resumedUrl.searchParams.values()],expectedSelection);
  if(newScienceLink.port!==firstSciencePort){
   assert.notEqual(resumedUrl.port,String(firstSciencePort),
    'The launcher must not advertise the stopped old OS port');
  }
  assert.equal(resumedUrl.pathname,'/');
  assert.equal(resumedUrl.hash,'');
  assert.doesNotMatch(newScienceLink.link,/SYN:|AUTHOR_|source_id|password|csrf|account/i);
  const restartedScienceStart=browserRequests.length;
  await navigateAndLoad(newScienceLink.link);
  const scienceRestarted=await restoredFromBrowser();
  const restartedScienceGets=freshScienceGets(restartedScienceStart);
  assert.equal(scienceRestarted.current.snapshot_receipt.sha256,originalScienceDigest);
  assert.deepEqual(['early','late'].map(k=>scienceRestarted[k].snapshot_receipt.sha256),
   originalPairDigests,'Independent S9 receipts persist byte-identically after OS restart');
  assert.equal(createHash('sha256').update(readFileSync(durableRegistry)).digest('hex'),
   originalDbDigest,'The scientific SQLite was not reseeded or mutated on restart/read');
  assert.equal(existsSync(join(scienceDir,'accounts.sqlite3')),false);
  assert.equal(existsSync(join(scienceDir,'accounts')),false);
  assert.equal(existsSync(join(scienceDir,'science.db')),false);
  // Real Chrome downloads a *second* pair after the actual process restart;
  // the independent CLI must accept the exact re-created synthetic receipts.
  await js("document.querySelector('[data-action=\"science-registry-pair-export\"]').scrollIntoView({block:'center'});true");
  const durablePairPoint=await js("(()=>{const r=document.querySelector('[data-action=\"science-registry-pair-export\"]').getBoundingClientRect();return {x:r.left+r.width/2,y:r.top+r.height/2};})()");
  await cdp('Input.dispatchMouseEvent',{type:'mousePressed',
   x:durablePairPoint.x,y:durablePairPoint.y,button:'left',clickCount:1});
  await cdp('Input.dispatchMouseEvent',{type:'mouseReleased',
   x:durablePairPoint.x,y:durablePairPoint.y,button:'left',clickCount:1});
  const {name:durablePairFile,data:durablePair}=await completedJsonDownload(
   downloadsDir,/^pfl-s9-pair-2026-10-10-[a-f0-9]{12}\.json$/);
  const durableOffline=JSON.parse(python([
   'scripts/compare_scientific_exports.py','--pair',
   join(downloadsDir,durablePairFile)]));
  assert.equal(durableOffline.status,'PASS');
  assert.equal(durableOffline.pair_sha256,durablePair.pair_receipt.sha256);
  assert.equal(durableOffline.early.sha256,originalPairDigests[0]);
  assert.equal(durableOffline.late.sha256,originalPairDigests[1]);
  assert.equal(durableOffline.R5,'STOP_R5');
  assert.equal(durableOffline.real_sources_admitted,0);
  assert.equal(durableOffline.publisher_identity_verified,false);
  assert.equal(durableOffline.rights_for_public_display_admitted,false);
  unlinkSync(join(downloadsDir,durablePairFile));
  console.log('S9_GUEST_URL_CDP '+JSON.stringify({
   one_chrome:true,facade_initial_registry_gets:firstReloadGets,
   facade_reload_registry_gets:secondReloadGets,
   facade_503_recovery_registry_gets:recoveredGets,
   science_only_before_restart_registry_gets:originalScienceGets,
   science_only_after_restart_registry_gets:restartedScienceGets,
   science_only_restart_processes:2,
   port_assigned_by_os:true,
   original_port:firstSciencePort,
   resumed_port:newScienceLink.port,
   port_changed:newScienceLink.port!==firstSciencePort,
   launcher_invalid_links_rejected:malformedResume.length,
   registry_receipt_sha256:originalScienceDigest,
   persisted_sqlite_sha256:originalDbDigest,
   offline_pair_pass:true,guest_only:true,R5:'STOP_R5',
   public_release_gates:0,scientific_ab_cycles:0
  }));
 }finally{
  if(socket)socket.close();
  await Promise.all([stopChild(chrome),stopChild(scienceServer)]);
  await new Promise(resolve=>server.close(resolve));
  try{rmSync(scratch,{recursive:true,force:true,maxRetries:2,retryDelay:200});}catch(_){}
 }
});
