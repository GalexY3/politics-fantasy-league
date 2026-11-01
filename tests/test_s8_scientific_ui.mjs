import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {execFileSync} from 'node:child_process';
import {createHash,webcrypto} from 'node:crypto';
import {runInNewContext,createContext,runInContext} from 'node:vm';

const script=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const root=new URL('../scripts/run_scientific_integration_lab.py',import.meta.url);
const reports=Object.fromEntries(['early','late'].map(cut=>[
 cut,JSON.parse(execFileSync('python',[root.pathname.replace(/^\/(?=[A-Z]:)/i,''),'--cut',cut],{encoding:'utf8',maxBuffer:1024*1024}))
]));

function setup(){
 const listeners={},elements={},routes=[],downloads=[];
 let badDigest=false;
 const doc={
  getElementById(id){return elements[id]??=( {innerHTML:'',textContent:'',hidden:false,addEventListener(){}} );},
  querySelectorAll(){return [];},
  addEventListener(name,callback){listeners[name]=callback;},
  createElement(){return {href:'',download:'',click(){downloads.push(this.download);},remove(){}};},
  body:{appendChild(){}},
 };
 class LocalURL extends URL {}
 LocalURL.createObjectURL=()=> 'blob:fake';
 LocalURL.revokeObjectURL=()=>{};
 const fetch=async route=>{
  routes.push(route);
  const url=new URL(route,'http://127.0.0.1');
  const cut=url.searchParams.get('cut')||'late';
  const scenario=url.searchParams.get('scenario')||'baseline';
  if(url.pathname==='/api/scientific-integration-lab'){
   const result=structuredClone(reports[cut]);
   result.scenario=scenario;
   return {ok:true,json:async()=>result};
  }
  if(url.pathname==='/api/scientific-lab-export'){
   const result=structuredClone(reports[cut]);
   result.scenario=scenario;
   const json=JSON.stringify(result);
   const sha=createHash('sha256').update(json).digest('hex');
   return {ok:true,json:async()=>({schema:'pfl.synthetic_scientific_export_receipt.v1',
    canonicalization:'JSON_UTF8_SORTED_KEYS_COMPACT_V1',
    canonical_json:json,bytes:Buffer.byteLength(json),sha256:badDigest?'0'.repeat(64):sha,
    R5:'STOP_R5',empirical_data_exported:false})};
  }
  if(url.pathname==='/api/scientific-lab-admission'){
   return {ok:true,json:async()=>({schema:'pfl.synthetic_distribution_admission_dry_run.v1',
     evidence_class:'SYNTHETIC_LAB_ONLY',candidate:url.searchParams.get('candidate'),
     status:'REJECTED_R5',R5:'STOP_R5',real_original_admitted:false,
     source_rows_imported:0,real_person_scoring:false,blockers:['REAL_RIGHTS_MISSING'],
     checks:{fixture_sha256_matches_bytes:true}})};
  }
  throw Error('Unexpected route '+route);
 };
 const globals={document:doc,URL:LocalURL,fetch,TextEncoder,Blob,crypto:webcrypto,
  setTimeout(){return 1;},clearTimeout(){},Intl,Date,Number,String,Error,
  console};
 const context=createContext(globals);
 runInContext(script.slice(0,script.lastIndexOf('bootstrap().catch')),context);
 runInContext("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.club='demo';ui.tab='scientific';",context);
 return {listeners,elements,routes,downloads,context,setBadDigest(value){badDigest=value;}};
}

test('S8 actual UI loads late 20-set S7, S3, B0/B3 and six source distributions',async()=>{
 const t=setup();
 await runInContext('loadScientific()',t.context);
 const html=t.elements.content.innerHTML;
 assert.match(html,/Laboratorio científico · S8/);
 assert.match(html,/S3 · identificación parcial/);
 assert.match(html,/S7 · conjuntos de testigos/);
 assert.match(html,/S7_NEITHER_APPROVED/);
 assert.match(html,/S7_CONFLICT_SAME_TERMINAL_DAY/);
 assert.match(html,/S7_INADMISSIBLE_SHA/);
 assert.match(html,/B0 calendario frente a B3 selección/);
 assert.match(html,/6 \/ 6/);
 assert.match(html,/R5 STOP · 0\/6/);
 assert.match(html,/Actor A ficticio/);
 assert.match(html,/DISTRIBUTION_COVERAGE_UNATTESTED/);
 assert.doesNotMatch(html,/SYN:S7_ASSET_/);
});

test('S8 change controls requery knowledge cut and filter fake first-public without lookahead',async()=>{
 const t=setup();
 await runInContext('loadScientific()',t.context);
 await t.listeners.change({target:{id:'science-cut',value:'early'}});
 assert.match(t.elements.content.innerHTML,/2 \/ 2/);
 assert.match(t.elements.content.innerHTML,/Aún no conocida en el corte temprano/);
 assert.doesNotMatch(t.elements.content.innerHTML,/FIXTURE_EDITION_V2/);
 assert.ok(t.routes.some(r=>r.includes('cut=early')));
 await t.listeners.change({target:{id:'science-cut',value:'late'}});
 await t.listeners.change({target:{id:'science-first-public',value:'2026-09-19T12:00:00Z'}});
 assert.match(t.elements.content.innerHTML,/2 \/ 6/);
 assert.doesNotMatch(t.elements.content.innerHTML,/FIXTURE_EDITION_V2/);
 await t.listeners.change({target:{id:'science-valid',value:'2026-09-11'}});
 assert.match(t.elements.content.innerHTML,/2026-09-11/);
 await t.listeners.change({target:{id:'science-chronicle',value:'2026-10-10'}});
 assert.match(t.elements.content.innerHTML,/Crónica 2026-10-10/);
});

test('S8 dry-run button stays fail closed, real export interaction checks SHA before download',async()=>{
 const t=setup();
 await runInContext('loadScientific()',t.context);
 await t.listeners.change({target:{id:'science-candidate',value:'sha_spoof'}});
 const act=action=>({target:{closest(selector){return selector==='[data-action]'?
   {dataset:{action}}:null;}}});
 await t.listeners.click(act('science-probe'));
 assert.match(t.elements.content.innerHTML,/REJECTED_R5/);
 assert.match(t.elements.content.innerHTML,/REAL_RIGHTS_MISSING/);
 await t.listeners.click(act('science-export'));
 assert.equal(t.downloads.length,1);
 assert.match(t.downloads[0],/^pfl-s8-late-baseline-/);
 assert.match(t.elements['science-export-status'].textContent,/SHA-256/);
 t.setBadDigest(true);
 await t.listeners.click(act('science-export'));
 assert.equal(t.downloads.length,1,'bad SHA must never trigger download');
});
