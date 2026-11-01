// Node VM executes the actual shipped app.js, with REAL localhost HTTP fetch.
// Server and Python->Node bridge are started by test_s9_scientific_live_http.py.
// The VM owns only DOM/download stand-ins; scientific responses are never mocks.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createContext,runInContext} from 'node:vm';
import {createHash,webcrypto} from 'node:crypto';

const base=process.argv[2];
const mode=process.argv[3]||'baseline';
if(!/^http:\/\/127\.0\.0\.1:[0-9]+$/.test(base)||!['baseline','bridge_503'].includes(mode))
 throw new Error('LOCALHOST_TEST_CONTRACT_ONLY');

const script=readFileSync(new URL('../src/politics_fantasy/web/app.js',import.meta.url),'utf8');
const listeners={},elements={},routes=[],downloads=[];
let tamperExport=false;
const doc={
 getElementById(id){return elements[id]??={innerHTML:'',textContent:'',hidden:false,
  addEventListener(){}};},
 querySelectorAll(){return [];},
 addEventListener(name,listener){listeners[name]=listener;},
 createElement(){return {href:'',download:'',click(){downloads.push(this.download);},remove(){}};},
 body:{appendChild(){}},
};
class LocalURL extends URL {}
LocalURL.createObjectURL=()=> 'blob:local-only';
LocalURL.revokeObjectURL=()=>{};
const actualFetch=async (route,options)=>{
 const target=new URL(route,base);
 assert.equal(target.origin,base,'never leave the exact local HTTP server');
 routes.push(target.pathname+target.search);
 const response=await fetch(target,options);
 if(tamperExport&&target.pathname==='/api/scientific-lab-export'){
  // Adversarial CLIENT-side transit corruption of a response fetched from the
  // real Python->Node API. Do not alter production server or local fixture.
  const payload=await response.json();
  payload.sha256='0'.repeat(64);
  return new Response(JSON.stringify(payload),{status:response.status});
 }
 return response;
};
const context=createContext({document:doc,fetch:actualFetch,URL:LocalURL,
 crypto:webcrypto,Blob,TextEncoder,setTimeout(){return 1;},clearTimeout(){},
 Intl,Date,Number,String,Error,console,encodeURIComponent});
runInContext(script.slice(0,script.lastIndexOf('bootstrap().catch')),context);
runInContext("ui.state={clubs:[{id:'demo',name:'Demo'}]};ui.club='demo';ui.tab='scientific';",context);
const evaluate=expr=>runInContext(expr,context);
const change=(id,value)=>listeners.change({target:{id,value}});
const click=action=>listeners.click({target:{closest(selector){
 return selector==='[data-action]'?{dataset:{action}}:null;
}}});

async function baseline(){
 // HTTP corroboration is from production server, not fabricated VM JSON.
 const upstream=await (await actualFetch('/api/scientific-integration-lab?cut=late')).json();
 assert.equal(upstream.R5,'STOP_R5');
 assert.equal(upstream.explorer.catalog.visible_distribution_count,6);
 assert.equal(upstream.warehouse.b0_b3_witness_sets.sets_by_knowledge_cut.late.sets.length,20);
 assert.equal(upstream.warehouse.partial_identification_oracle.change_bounds.lower,'-11/52');
 assert.equal(upstream.warehouse.b0_b3_observational_equivalence.hypothetical_all_received_by_mechanism.B0_CALENDAR,4);
 assert.equal(upstream.explorer.observatory.real_actor_identity_verified,false);
 const raw=JSON.stringify(upstream);
 assert.doesNotMatch(raw,/SYN:CHRONICLE_V1|SYN:CHAIN_COMM_V1|SYN:S7_ASSET_|SYN:WITNESS_S7_/);
 assert.doesNotMatch(raw,/SYNTHETIC S7 WITNESS\\n|SYNTHETIC BITEMPORAL FIXTURE/);
 assert.ok(upstream.explorer.catalog.distributions.every(x=>
  x.real_publisher_authenticated===false&&x.rights_for_requested_purpose_admitted===false));

 await evaluate('loadScientific()');
 let html=elements.content.innerHTML;
 for(const marker of ['Laboratorio científico · S8','B0 calendario frente a B3 selección',
  'S3 · identificación parcial','S7 · conjuntos de testigos','S7_NEITHER_APPROVED',
  'S7_CONFLICT_SAME_TERMINAL_DAY','S7_INADMISSIBLE_SHA','6 / 6',
  'DISTRIBUTION_COVERAGE_UNATTESTED','Actor A ficticio','R5 STOP · 0/6'])
  assert.ok(html.includes(marker),`Browser UI missing ${marker}`);
 assert.ok(!html.includes('SYN:CHRONICLE_V1'));
 assert.ok(!html.includes('SYN:WITNESS_'));

 await change('science-cut','early');
 html=elements.content.innerHTML;
 assert.match(html,/2 \/ 2/);
 assert.match(html,/Aún no conocida en el corte temprano/);
 assert.doesNotMatch(html,/FIXTURE_EDITION_V2/);
 assert.ok(routes.some(url=>url.includes('cut=early')));
 await change('science-cut','late');
 assert.match(elements.content.innerHTML,/6 \/ 6/);
 await change('science-first-public','2026-09-19T12:00:00Z');
 assert.match(elements.content.innerHTML,/2 \/ 6/);
 assert.doesNotMatch(elements.content.innerHTML,/FIXTURE_EDITION_V2/);
 await change('science-valid','2026-09-11');
 assert.match(elements.content.innerHTML,/vigencia de la cadena 2026-09-11/i);
 await change('science-chronicle','2026-09-15');
 assert.match(elements.content.innerHTML,/Crónica 2026-09-15/);

 await change('science-scenario','rights_spoof');
 assert.match(elements.content.innerHTML,/R5 STOP/);
 assert.match(elements.content.innerHTML,/S7_CONFLICT_SAME_TERMINAL_DAY/);
 await change('science-scenario','privacy_probe');
 assert.match(elements.content.innerHTML,/R5 STOP/);
 await change('science-scenario','baseline');

 await change('science-candidate','sha_spoof');
 await click('science-probe');
 html=elements.content.innerHTML;
 assert.match(html,/REJECTED_R5/);
 assert.match(html,/FIXTURE_SHA256_MATCHES_BYTES_FAILED/);
 assert.ok(routes.some(url=>url.includes('scientific-lab-admission?candidate=sha_spoof')));

 const receipt=await (await actualFetch('/api/scientific-lab-export?cut=late&scenario=baseline&published_until=2026-09-19T12%3A00%3A00Z')).json();
 assert.equal(receipt.sha256,createHash('sha256').update(receipt.canonical_json).digest('hex'));
 assert.equal(Buffer.byteLength(receipt.canonical_json),receipt.bytes);
 assert.equal(JSON.parse(receipt.canonical_json).explorer.catalog.visible_distribution_count,2);
 await click('science-export');
 assert.equal(downloads.length,1);
 assert.match(downloads[0],/^pfl-s8-late-baseline-/);
 assert.match(elements['science-export-status'].textContent,/SHA-256/);
 assert.ok(elements['science-export-status'].textContent.includes(receipt.sha256));
 tamperExport=true;
 await click('science-export');
 assert.equal(downloads.length,1,'corrupted actual HTTP receipt must not download');
 assert.match(elements.toast.textContent,/Exportación bloqueada/);
 assert.ok(routes.filter(x=>x.startsWith('/api/scientific-lab-export?')).length>=3);
 console.log(JSON.stringify({mode,passed:true,evidence:'REAL_HTTP_NODE_VM',
  cuts:['early','late'],s7:20,source_catalog:{early:2,late:6,filtered:2},
  sha256_export:receipt.sha256,tamper_rejected:true,
  dry_run:'REJECTED_R5',node_cross_language:true,routes:routes.length}));
}

async function bridge503(){
 const response=await actualFetch('/api/scientific-integration-lab?cut=late');
 assert.equal(response.status,503);
 assert.equal(response.headers.get('cache-control'),'no-store');
 assert.deepEqual(await response.json(),{error:'SYNTHETIC_BRIDGE_UNAVAILABLE'});
 await evaluate('loadScientific()');
 assert.match(elements.content.innerHTML,/Servicio científico rechazado/);
 assert.match(elements.content.innerHTML,/Contrato HTTP 503/);
 assert.doesNotMatch(elements.content.innerHTML,/S7_NEITHER_APPROVED/);
 assert.match(elements.content.innerHTML,/R5 STOP/);
 assert.equal(evaluate('ui.scientific'),null);
 console.log(JSON.stringify({mode,passed:true,evidence:'REAL_HTTP_503_NODE_VM',
  error:'SYNTHETIC_BRIDGE_UNAVAILABLE',ui_fail_closed:true}));
}

await (mode==='baseline'?baseline():bridge503());
