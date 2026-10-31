/* Browser E2E: Chrome DevTools Protocol on loopback only; no npm dependency.
 * Run manually, off-Git screenshot and isolated temporary browser profile.
 */
import assert from 'node:assert/strict';
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import {spawn} from 'node:child_process';
import {pathToFileURL,fileURLToPath} from 'node:url';
import process from 'node:process';
const here=path.dirname(fileURLToPath(import.meta.url));
const html=path.resolve(here,'../product/showcase/index.html');
const output=process.env.PFL_SHOWCASE_QA_OUTPUT||path.join(os.tmpdir(),'pfl-showcase-e2e');
const chrome=process.env.CHROME_PATH||(process.platform==='win32'
  ?'C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe'
  :'/usr/bin/google-chrome');
const profile=fs.mkdtempSync(path.join(os.tmpdir(),'pfl-showcase-cdp-'));
fs.mkdirSync(output,{recursive:true});
const proc=spawn(chrome,[
  '--headless=new','--disable-gpu','--disable-extensions',
  '--no-first-run','--no-default-browser-check','--disable-background-networking',
  '--remote-debugging-address=127.0.0.1','--remote-debugging-port=0',
  '--user-data-dir='+profile,'about:blank'
],{stdio:'ignore'});
let ws=null;
let counter=1;
const outstanding=new Map();
const sleep=ms=>new Promise(resolve=>setTimeout(resolve,ms));
const runWithDeadline=(promise,ms=10000)=>Promise.race([
  promise,new Promise((_,reject)=>setTimeout(()=>reject(new Error('CDP_TIMEOUT')),ms))
]);
async function waitFor(fn,ms=9500){
  const until=Date.now()+ms;
  while(Date.now()<until){
    const v=await fn();if(v)return v;
    await sleep(75);
  }
  throw new Error('CHROME_READY_TIMEOUT');
}
async function cdp(method,params={}){
  const id=counter++;
  const reply=runWithDeadline(new Promise((resolve,reject)=>{
    outstanding.set(id,{resolve,reject});
    ws.send(JSON.stringify({id,method,params}));
  }));
  return reply;
}
async function evaluate(expr){
  const result=await cdp('Runtime.evaluate',{
    expression:expr,returnByValue:true,awaitPromise:true});
  if(result.exceptionDetails)throw new Error('JS_EXCEPTION: '+JSON.stringify(result.exceptionDetails).slice(0,1600));
  return result.result?.value;
}
async function ready(){
  return waitFor(async()=>await evaluate("document.querySelector('#page-content')?.textContent?.trim().length > 20"));
}
function check(value,description){
  assert.ok(value,description);process.stdout.write('PASS '+description+'\n');
}
async function click(selector){
  const result=await evaluate("(function(){const e=document.querySelector("+JSON.stringify(selector)+");if(!e)return false;e.click();return true})()");
  check(result,'click '+selector);
}
async function snapshot(name){
  const data=await cdp('Page.captureScreenshot',{format:'png',captureBeyondViewport:false});
  if(!data.data)throw new Error('NO_SCREENSHOT_DATA');
  const file=path.join(output,name+'.png');
  fs.writeFileSync(file,Buffer.from(data.data,'base64'));
  process.stdout.write('SCREENSHOT '+file+' '+fs.statSync(file).size+' bytes\n');
}
try{
  const port=await waitFor(()=>{
    const f=path.join(profile,'DevToolsActivePort');
    if(!fs.existsSync(f))return null;
    const value=Number(fs.readFileSync(f,'utf8').split(/\r?\n/)[0]);
    return value>=1000&&value<=65535?value:null;
  });
  const targets=await fetch('http://127.0.0.1:'+port+'/json').then(r=>r.json());
  const first=targets.find(x=>x.type==='page');
  if(!first?.webSocketDebuggerUrl)throw new Error('NO_CDP_PAGE');
  ws=new WebSocket(first.webSocketDebuggerUrl);
  ws.addEventListener('message',event=>{
    const data=JSON.parse(String(event.data));
    if(data.id&&outstanding.has(data.id)){
      const {resolve,reject}=outstanding.get(data.id);
      outstanding.delete(data.id);
      if(data.error)reject(new Error(data.error.message));else resolve(data.result);
    }
  });
  await runWithDeadline(new Promise((resolve,reject)=>{
    ws.addEventListener('open',resolve,{once:true});
    ws.addEventListener('error',reject,{once:true});
  }));
  await cdp('Runtime.enable');await cdp('Page.enable');
  await cdp('Emulation.setDeviceMetricsOverride',{
    width:1440,height:950,deviceScaleFactor:1,mobile:false});
  await cdp('Page.navigate',{url:pathToFileURL(html).href});
  await ready();
  check((await evaluate("document.body.innerText")).includes('El país cambia.'),'showcase home renders with real JS');
  check((await evaluate("document.body.dataset.theme"))==='dark','graphite dark is the first-run theme');
  check((await evaluate("document.querySelectorAll('.event-card').length"))>=1,'fictional event dossier appears on home');
  check((await evaluate("document.querySelectorAll('.real-briefing .real-metric').length"))===2,'real INE snapshot on home distinctly labelled');
  check((await evaluate("document.querySelectorAll('.nav-link').length"))===8,'eight navigation routes');
  await snapshot('browser-desktop-home');

  await click('.nav-link[data-page="mercado"]');
  check((await evaluate("document.querySelectorAll('.character-card').length"))===18,'all eighteen cards render');
  check((await evaluate("document.querySelectorAll('.char-cover img').length"))===18,'all fictional characters have local illustration assets');
  const portraitLoaded=await waitFor(()=>evaluate("document.querySelector('.char-cover img')?.naturalWidth>0"),6500);
  check(portraitLoaded===true,'portrait SVG decodes in Chrome');
  await snapshot('browser-desktop-market');
  await click('button[data-action="buy"][data-id="c02"]');
  const afterBuy=await evaluate("JSON.parse(localStorage.getItem('pfl-showcase-edition-zero-v1'))");
  check(afterBuy.budget===60&&afterBuy.roster.includes('c02'),'purchase subtracts 34 CR and persists');

  await click('.nav-link[data-page="plantilla"]');
  await click('button[data-action="lineup"][data-id="c02"]');
  await click('button[data-action="captain"][data-id="c02"]');
  check((await evaluate("JSON.parse(localStorage.getItem('pfl-showcase-edition-zero-v1')).captain"))==='c02','captain change persists');
  await click('.nav-link[data-page="jornadas"]');
  await click('button[data-action="round"]');
  const afterRound=await evaluate("JSON.parse(localStorage.getItem('pfl-showcase-edition-zero-v1'))");
  check(afterRound.week===2&&afterRound.rounds.length===1&&afterRound.points>0,'round completed deterministically in browser');
  check(afterRound.rounds[0].eventId==='demo-01','round is attributable to explicit fictional event');
  check((await evaluate("document.body.innerText")).includes('Última sesión'),'round breakdown renders');
  await click('.nav-link[data-page="laboratorio"]');
  check((await evaluate("document.querySelectorAll('.lab-tab').length"))===6,'six observatory modes render');
  check((await evaluate("document.querySelectorAll('.trend-chart').length"))===1,'synthetic trend has real SVG nodes');
  await snapshot('browser-desktop-laboratory');
  await click('.lab-tab[data-id="economia"]');
  check((await evaluate("document.querySelectorAll('.real-metric').length"))===3,'official 2026 economy snapshot renders separately');
  check((await evaluate("document.querySelectorAll('.history-bar').length"))===10,'real EPA historic quarter changes chart renders');
  check((await evaluate("document.body.innerText")).includes('4,9 %'),'verified INE IPC advance is visible');
  await snapshot('browser-desktop-economy');
  await click('.lab-tab[data-id="territorios"]');
  check((await evaluate("document.querySelectorAll('.territory-tile').length"))===19,'nineteen territorial scenario cells render');
  await click('.territory-tile[data-id="Galicia"]');
  check((await evaluate("document.querySelector('.chart-panel')?.textContent.includes('Galicia')"))===true,'territory selection changes the chart');
  await click('.lab-tab[data-id="politicas"]');
  check((await evaluate("document.querySelectorAll('.event-card').length"))===8,'policy and participation event records render');
  await click('.lab-tab[data-id="fuentes"]');
  check((await evaluate("document.querySelectorAll('.source-card').length"))===6,'official source register renders with no ingestion');
  check((await evaluate("document.body.innerText")).includes('Sin canal en directo habilitado'),'no fake realtime claim');

  await click('.nav-link[data-page="partidos"]');
  check((await evaluate("document.querySelectorAll('.party-row').length"))>=100,'parties, coalitions and historical names render');
  await click('button[data-action="favorite"]');
  check((await evaluate("JSON.parse(localStorage.getItem('pfl-showcase-edition-zero-v1')).favorites.length"))===1,'favourite flag persists without affecting game');
  const searchCount=await evaluate("(function(){const n=document.getElementById('party-search');n.value='PSOE';n.dispatchEvent(new Event('input',{bubbles:true}));return document.querySelectorAll('.party-row').length})()");
  check(searchCount>=1&&searchCount<117,'directory search filters names without navigating externally');
  const allAgain=await evaluate("(function(){const n=document.getElementById('party-search');n.value='';n.dispatchEvent(new Event('input',{bubbles:true}));return document.querySelectorAll('.party-row').length})()");
  check(allAgain>=100,'clearing search restores full catalogue');
  const onlyFav=await evaluate("(function(){const c=document.getElementById('party-favorites');c.checked=true;c.dispatchEvent(new Event('change',{bubbles:true}));return document.querySelectorAll('.party-row').length})()");
  check(onlyFav===1,'favourites-only filter matches local saved state');
  await evaluate("(function(){const c=document.getElementById('party-favorites');c.checked=false;c.dispatchEvent(new Event('change',{bubbles:true}))})()");
  await snapshot('browser-desktop-parties');

  await click('#theme-toggle');
  check((await evaluate("document.body.dataset.theme"))==='light','theme toggle changes graphite to light');
  await click('.nav-link[data-page="perfil"]');
  await click('button[data-action="symbol"][data-id="scale"]');
  await click('button[data-action="palette"][data-id="blue"]');
  await click('button[data-action="save-heraldry"]');
  check((await evaluate("JSON.parse(localStorage.getItem('pfl-showcase-edition-zero-v1')).heraldry.length"))===4,'four symbols persist');
  check((await evaluate("document.body.dataset.palette"))==='blue','palette changes on save');
  await click('button[data-action="set-theme"][data-id="dark"]');
  await snapshot('browser-desktop-profile');
  const nameSet=await evaluate("(function(){let n=document.getElementById('profile-name');n.value='Club del Público';document.getElementById('profile-form').requestSubmit();return document.getElementById('top-club').textContent})()");
  check(nameSet==='Club del Público','profile form updates and persists');

  await cdp('Page.reload',{ignoreCache:true});await ready();
  check((await evaluate("document.body.dataset.theme"))==='dark','dark theme survives reload');
  check((await evaluate("document.body.dataset.palette"))==='blue','selected palette survives reload');
  check((await evaluate("document.getElementById('top-club').textContent"))==='Club del Público','club name survives reload');

  await cdp('Emulation.setDeviceMetricsOverride',{
    width:390,height:844,deviceScaleFactor:1,mobile:true,screenWidth:390,screenHeight:844});
  await cdp('Page.navigate',{url:pathToFileURL(html).href+'#inicio'});await ready();
  const measured=await evaluate("({inner:window.innerWidth,root:document.documentElement.scrollWidth,body:document.body.scrollWidth})");
  check(measured.inner===390,'genuine mobile viewport of 390 CSS pixels');
  check(measured.root<=390&&measured.body<=390,'mobile layout has no horizontal overflow');
  await snapshot('browser-mobile-home');
  await click('.nav-link[data-page="mercado"]');
  check((await evaluate("document.querySelectorAll('.character-card').length"))===18,'market also renders at mobile width');
  await click('.nav-link[data-page="laboratorio"]');
  await click('.lab-tab[data-id="territorios"]');
  const mobileLab=await evaluate("({root:document.documentElement.scrollWidth,body:document.body.scrollWidth})");
  check(mobileLab.root<=390&&mobileLab.body<=390,'lab territorial mode has no horizontal mobile overflow');
  await snapshot('browser-mobile-laboratory');
  process.stdout.write('SHOWCASE_BROWSER_E2E_PASS\n');
} catch(err) {
  process.stderr.write('SHOWCASE_BROWSER_E2E_FAIL '+(err?.stack||String(err))+'\n');
  process.exitCode=1;
} finally {
  for(const {reject} of outstanding.values())reject(new Error('BROWSER_CLOSED'));
  if(ws){try{ws.close();}catch(_){}}
  if(proc&&!proc.killed){try{proc.kill();}catch(_){}}
}
