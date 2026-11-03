// Optional native Chrome headless click-through. Zero third-party dependencies.
// A Python pytest fixture supplies REAL localhost HTTP and actual Python->Node.
// All temporary Chrome profile/download bytes are isolated and deleted.
import assert from 'node:assert/strict';
import {spawn,spawnSync} from 'node:child_process';
import {existsSync,mkdtempSync,mkdirSync,readFileSync,readdirSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createHash} from 'node:crypto';

const base=process.argv[2];
const chrome=process.argv[3];
if(!/^http:\/\/127\.0\.0\.1:[0-9]+$/.test(base)||!chrome||!existsSync(chrome))
 throw new Error('LOCAL_BROWSER_ONLY');
const profile=mkdtempSync(join(tmpdir(),'pfl-s8-chrome-'));
const downloads=join(profile,'downloads');
mkdirSync(downloads);
let child=null;
let socket=null;
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const deadline=ms=>Date.now()+ms;
const downloadFiles=()=>readdirSync(downloads).sort();
async function completedDownload(name){
 const target=join(downloads,name);
 const until=deadline(12000);
 while(Date.now()<until){
  if(existsSync(target)&&!downloadFiles().some(x=>x.endsWith('.crdownload'))){
   try{
    const bytes=readFileSync(target);
    const parsed=JSON.parse(bytes.toString('utf8'));
    if(parsed?.schema==='pfl.synthetic_scientific_export_receipt.v1')
     return {bytes,parsed};
   }catch(_){/* Chrome may still be writing the file. */}
  }
  await sleep(110);
 }
 throw new Error('CHROME_S8_DOWNLOAD_NOT_COMPLETE');
}

async function chromePort(){
 const file=join(profile,'DevToolsActivePort');
 const until=deadline(11000);
 while(Date.now()<until){
  if(existsSync(file)){
   const n=Number(readFileSync(file,'utf8').split(/\r?\n/)[0]);
   if(Number.isInteger(n)&&n>0)return n;
  }
  if(child.exitCode!==null)throw new Error('CHROME_EXITED_PREMATURELY');
  await sleep(110);
 }
 throw new Error('CHROME_DEVTOOLS_PORT_NOT_READY');
}

async function openCdp(port){
 const until=deadline(8000);
 let target=null;
 while(Date.now()<until){
  try{
   const list=await (await fetch('http://127.0.0.1:'+port+'/json/list')).json();
   target=list.find(item=>item.type==='page'&&item.url.startsWith(base));
   if(target?.webSocketDebuggerUrl)break;
  }catch(_){ /* Chrome startup between ready file and HTTP service. */ }
  await sleep(110);
 }
 if(!target)throw new Error('CHROME_TARGET_NOT_FOUND');
 const ws=new WebSocket(target.webSocketDebuggerUrl);
 await new Promise((resolve,reject)=>{
  const timeout=setTimeout(()=>reject(Error('CDP_OPEN_TIMEOUT')),9000);
  ws.addEventListener('open',()=>{clearTimeout(timeout);resolve();},{once:true});
  ws.addEventListener('error',()=>{clearTimeout(timeout);reject(Error('CDP_OPEN_ERROR'));},{once:true});
 });
 socket=ws;
 let id=0;
 const pending=new Map();
 const downloadEvents=[];
 ws.addEventListener('message',event=>{
  const obj=JSON.parse(event.data);
  if(obj.method==='Browser.downloadWillBegin'||obj.method==='Browser.downloadProgress')
   downloadEvents.push({method:obj.method,guid:obj.params?.guid,state:obj.params?.state});
  if(!pending.has(obj.id))return;
  const promise=pending.get(obj.id);pending.delete(obj.id);
  if(obj.error)promise.reject(Error('CDP_'+obj.error.message));
  else promise.resolve(obj.result);
 });
 const send=(method,params={})=>new Promise((resolve,reject)=>{
  const seq=++id;
  const timeout=setTimeout(()=>{pending.delete(seq);reject(Error('CDP_TIMEOUT_'+method));},12000);
  pending.set(seq,{resolve:v=>{clearTimeout(timeout);resolve(v);},
                   reject:e=>{clearTimeout(timeout);reject(e);}});
  ws.send(JSON.stringify({id:seq,method,params}));
 });
 const evaluate=async expression=>{
  const r=await send('Runtime.evaluate',{expression,returnByValue:true,awaitPromise:true});
  if(r.exceptionDetails)throw Error('BROWSER_JS_'+r.exceptionDetails.text);
  return r.result?.value;
 };
 const wait=async(expression,label,ms=11000)=>{
  const until=deadline(ms);
  while(Date.now()<until){
   if(await evaluate(expression))return;
   await sleep(110);
  }
  const state=await evaluate('({ready:document.readyState,tab:typeof ui!=="undefined"?ui.tab:null,content:document.querySelector("#content")?.innerText?.slice(0,280)})');
  throw Error('BROWSER_TIMEOUT_'+label+' '+JSON.stringify(state));
 };
 return {send,evaluate,wait,downloadEvents};
}

try{
 child=spawn(chrome,[
  '--headless=new','--disable-gpu','--disable-background-networking',
  '--disable-component-update','--disable-extensions','--disable-sync',
  '--no-first-run','--no-default-browser-check','--no-proxy-server',
  '--remote-allow-origins=*','--remote-debugging-port=0',
  '--user-data-dir='+profile,'--window-size=1440,950',base,
 ],{stdio:'ignore',windowsHide:true});
 const port=await chromePort();
 const {send,evaluate,wait,downloadEvents}=await openCdp(port);
 await send('Runtime.enable');
 await send('Page.enable');
 // Ensure test downloads cannot land in a person's ordinary Downloads folder.
 let isolation=null;
 try{
  await send('Browser.setDownloadBehavior',{
   behavior:'allow',downloadPath:downloads,eventsEnabled:true});
  isolation='BROWSER_SET_DOWNLOAD_BEHAVIOR';
 }catch(_){
  await send('Page.setDownloadBehavior',{behavior:'allow',downloadPath:downloads});
  isolation='PAGE_SET_DOWNLOAD_BEHAVIOR';
 }
 // The initial HTML and menu are available before async bootstrap()/refresh()
 // has populated demo state. A premature click is ignored by the app's
 // account-navigation guard. Legacy demo HTTP may leave ui.session null.
 const demoReady='document.readyState==="complete"'
  +'&&typeof ui!=="undefined"&&!ui.guest&&ui.tab==="overview"'
  +'&&!!ui.state&&Array.isArray(ui.state.clubs)&&ui.state.clubs.length>0'
  +'&&ui.state.clubs.some(club=>club.id===ui.club)'
  +'&&!!document.querySelector("[data-tab=scientific]")'
  +'&&!document.querySelector("[data-tab=scientific]").hidden'
  +'&&document.querySelector("#club-select")?.options.length>0';
 await wait(demoReady,'INITIAL_DEMO_STATE_READY');
 const bootstrapReady=await evaluate('({stateReady:!!ui.state&&Array.isArray(ui.state.clubs)'
  +'&&ui.state.clubs.some(club=>club.id===ui.club),tab:ui.tab,guest:ui.guest,'
  +'navVisible:!document.querySelector("[data-tab=scientific]")?.hidden,'
  +'clubOptions:document.querySelector("#club-select")?.options.length})');
 assert.equal(bootstrapReady.stateReady,true,'Initial HTTP demo state must be loaded');
 assert.equal(bootstrapReady.tab,'overview','Click must occur before leaving account overview');
 assert.equal(bootstrapReady.guest,false,'Scientific navigation requires non-guest demo');
 assert.equal(bootstrapReady.navVisible,true,'Scientific account nav must be visible');
 assert.ok(bootstrapReady.clubOptions>0,'Demo club selector must be rendered');
 await evaluate('document.querySelector("[data-tab=scientific]").click()');
 await wait('document.querySelectorAll(".science-table tbody tr").length===20&&'+
            'document.querySelector("#content").innerText.includes("6 / 6")','S7_20_LATE');
 // textContent includes collapsed <details> whose SHA/coverage labels remain
 // accessible but are not part of innerText until the user expands them.
 let content=await evaluate('document.querySelector("#content").textContent');
 for(const required of ['B0 calendario','S3 · identificación parcial',
    'S7_NEITHER_APPROVED','S7_CONFLICT_SAME_TERMINAL_DAY',
    'S7_INADMISSIBLE_SHA','DISTRIBUTION_COVERAGE_UNATTESTED','R5 STOP'])
  assert.ok(content.includes(required),'browser missing '+required);
 assert.ok(!content.includes('SYN:CHRONICLE_V1'));
 assert.ok(!content.includes('SYN:CHAIN_COMM_V1'));
 assert.ok(!content.includes('SYN:S7_ASSET_'));

 const change=async(id,value)=>evaluate(`(()=>{const e=document.getElementById(${JSON.stringify(id)});e.value=${JSON.stringify(value)};e.dispatchEvent(new Event('change',{bubbles:true}));return true})()`);
 await change('science-cut','early');
 await wait('document.querySelector("#content")?.innerText.includes("2 / 2")','EARLY_CUT');
 assert.equal(await evaluate('document.querySelector(".science-table tbody").children.length'),20);
 content=await evaluate('document.querySelector("#content").innerText');
 assert.ok(content.includes('Aún no conocida en el corte temprano'));
 assert.ok(!content.includes('FIXTURE_EDITION_V2'));
 await change('science-cut','late');
 await wait('document.querySelector("#content")?.innerText.includes("6 / 6")','LATE_CUT');
 await change('science-first-public','2026-09-19T12:00:00Z');
 await wait('document.querySelector("#content")?.innerText.includes("2 / 6")','FIRST_PUBLIC_FIXTURE');
 assert.ok(!(await evaluate('document.querySelector("#content").innerText')).includes('FIXTURE_EDITION_V2'));
 await change('science-valid','2026-09-11');
 await wait('document.querySelector("#content")?.innerText.includes("vigencia de la cadena 2026-09-11")','VALID_DAY');
 await change('science-chronicle','2026-09-15');
 await wait('document.querySelector("#content")?.innerText.includes("Crónica 2026-09-15")','CHRONICLE_DAY');
 await change('science-candidate','sha_spoof');
 await evaluate('document.querySelector("[data-action=science-probe]").click()');
 await wait('document.querySelector("#content")?.innerText.includes("REJECTED_R5")','DRY_RUN');
 assert.ok((await evaluate('document.querySelector("#content").textContent')).includes('FIXTURE_SHA256_MATCHES_BYTES_FAILED'));

 const selectedCut='late',selectedScenario='baseline';
 const firstPublic='2026-09-19T12:00:00Z';
 const exportRoute='/api/scientific-lab-export?cut='+selectedCut
  +'&scenario='+selectedScenario+'&published_until='+encodeURIComponent(firstPublic);
 const apiResponse=await fetch(base+exportRoute);
 assert.equal(apiResponse.status,200);
 const receipt=await apiResponse.json();
 const digest=createHash('sha256').update(Buffer.from(receipt.canonical_json,'utf8')).digest('hex');
 assert.equal(receipt.sha256,digest);
 assert.equal(Buffer.byteLength(receipt.canonical_json,'utf8'),receipt.bytes);
 assert.equal(receipt.schema,'pfl.synthetic_scientific_export_receipt.v1');
 assert.equal(receipt.canonicalization,'JSON_UTF8_SORTED_KEYS_COMPACT_V1');
 assert.equal(receipt.R5,'STOP_R5');
 assert.equal(receipt.empirical_data_exported,false);
 const payload=JSON.parse(receipt.canonical_json);
 assert.equal(payload.cut,selectedCut);
 assert.equal(payload.scenario,selectedScenario);
 assert.equal(payload.R5,'STOP_R5');
 assert.equal(payload.release_gates_passed,0);
 assert.equal(payload.scientific_AB_cycles,0);
 assert.equal(payload.real_corpus_ingestion_allowed,false);
 assert.equal(payload.explorer.catalog.publication_filter_fixture,firstPublic);
 assert.equal(payload.explorer.catalog.visible_distribution_count,2);
 assert.deepEqual(downloadFiles(),[],'Only this test may create downloads in the isolated Chrome profile');
 await evaluate('document.querySelector("[data-action=science-export]").click()');
 await wait('document.querySelector("#science-export-status")?.innerText.includes("SHA-256 del contenido canónico")','EXPORT_CLICK');
 assert.ok((await evaluate('document.querySelector("#science-export-status").innerText')).includes(digest));
 const fileName='pfl-s8-'+selectedCut+'-'+selectedScenario+'-'+digest.slice(0,12)+'.json';
 const {bytes:diskBytes,parsed:diskReceipt}=await completedDownload(fileName);
 assert.deepEqual(downloadFiles(),[fileName],
  'Exactly one complete S8 JSON must be saved by actual native Chrome');
 assert.deepEqual(diskReceipt,receipt,
  'Physical Chrome download must match the independent localhost API receipt');
 assert.equal(diskBytes.toString('utf8'),JSON.stringify(receipt,null,2)+'\n',
  'Downloaded file bytes must equal the browser-authored JSON receipt');
 assert.equal(createHash('sha256').update(Buffer.from(diskReceipt.canonical_json,'utf8')).digest('hex'),digest);
 assert.equal(Buffer.byteLength(diskReceipt.canonical_json,'utf8'),diskReceipt.bytes);
 assert.equal(diskReceipt.R5,'STOP_R5');
 const downloadedPayload=JSON.parse(diskReceipt.canonical_json);
 assert.equal(downloadedPayload.cut,selectedCut);
 assert.equal(downloadedPayload.scenario,selectedScenario);
 assert.equal(downloadedPayload.explorer.catalog.publication_filter_fixture,firstPublic);
 assert.equal(downloadedPayload.release_gates_passed,0);
 assert.equal(downloadedPayload.scientific_AB_cycles,0);
 const eventsBeforeTamper=downloadEvents.filter(e=>e.method==='Browser.downloadWillBegin').length;
 const screenshot=await send('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
 const screenshotSha=createHash('sha256').update(Buffer.from(screenshot.data,'base64')).digest('hex');
 // Test-only malicious mutation AFTER real localhost HTTP response arrived.
 await evaluate(`(()=>{const original=window.fetch.bind(window);window.fetch=async (...args)=>{const response=await original(...args);if(String(args[0]).includes('/api/scientific-lab-export')){const payload=await response.json();payload.sha256='0'.repeat(64);return new Response(JSON.stringify(payload),{status:response.status,headers:{'content-type':'application/json'}})}return response};return true})()`);
 await evaluate('document.querySelector("[data-action=science-export]").click()');
 await wait('document.querySelector("#toast")?.textContent.includes("Exportación bloqueada")','TAMPER_BLOCK');
 // Browser downloads are asynchronous. Allow an extra event-loop/IO interval
 // after the rejected response before asserting no second artifact appeared.
 await sleep(750);
 assert.deepEqual(downloadFiles(),[fileName],
  'Tampered SHA must not create a second file (including a .crdownload)');
 assert.deepEqual(readFileSync(join(downloads,fileName)),diskBytes,
  'Tampered response must not overwrite the original verified download');
 assert.equal(downloadEvents.filter(e=>e.method==='Browser.downloadWillBegin').length,
  eventsBeforeTamper,'Tampered SHA must not start another browser download');
 const browserState=await evaluate('({cut:ui.scienceCut,publication:ui.scienceFirstPublic,valid:ui.scienceValid,chronicle:ui.scienceChronicleValid,R5:ui.scientific.R5})');
 assert.equal(browserState.cut,selectedCut);
 assert.equal(browserState.publication,firstPublic);
 assert.equal(browserState.R5,'STOP_R5');
 console.log(JSON.stringify({passed:true,evidence:'CHROME_HEADLESS_REAL_CDP',
  browser:chrome,download_isolation:isolation,bootstrap_ready:true,cuts:['early','late'],
  s7_sets:20,model_comparison:'B0_B3',source_catalog:{early:2,late:6,filtered:2},
  valid_at:browserState.valid,chronicle_valid_at:browserState.chronicle,
  sha256_export:digest,upload_real:false,dry_run:'REJECTED_R5',
  download_verified_from_disk:true,download_file_name:fileName,
  download_bytes:diskBytes.length,canonical_bytes:diskReceipt.bytes,
  download_sha256:diskReceipt.sha256,download_cut:downloadedPayload.cut,
  download_scenario:downloadedPayload.scenario,
  download_first_public:downloadedPayload.explorer.catalog.publication_filter_fixture,
  download_R5:diskReceipt.R5,download_gates:downloadedPayload.release_gates_passed,
  downloads_after_tamper:downloadFiles().length,
  sha_tamper_rejected:true,sha_tamper_no_second_download:true,
  ui_screenshot_sha256:screenshotSha}));
}finally{
 try{socket?.close();}catch(_){}
 if(child?.pid){
  child.kill();
  if(process.platform==='win32'){
   spawnSync('taskkill',['/PID',String(child.pid),'/T','/F'],
    {stdio:'ignore',windowsHide:true,timeout:5000});
  }
 }
 // Brief cleanup retry for Windows handles released after browser exit.
 for(let k=0;k<5;k++){
  try{rmSync(profile,{recursive:true,force:true,maxRetries:1,retryDelay:100});break;}
  catch(_){await sleep(180);}
 }
}
