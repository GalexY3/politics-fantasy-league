import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,mkdtempSync,rmSync} from 'node:fs';
import {createHash, webcrypto} from 'node:crypto';
import {execFileSync,spawn} from 'node:child_process';
import {createContext, runInContext} from 'node:vm';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {createServer} from 'node:net';
import {setTimeout as delay} from 'node:timers/promises';

// Real application code, isolated in-memory DOM/fetch; no external URLs.
const source = readFileSync(new URL('../src/politics_fantasy/web/app.js', import.meta.url), 'utf8');

function syntheticReport() {
  return {
    schema: 'pfl.synthetic_scientific_integration_lab.v1',
    evidence_class: 'SYNTHETIC_LAB_ONLY',
    cut: 'late', scenario: 'baseline', R5: 'STOP_R5',
    scientific_AB_cycles: 0, release_gates_passed: 0,
    real_corpus_ingestion_allowed: false, scientific_estimator_admitted: false,
    independent_all_received_denominator: null,
    explorer: {
      schema: 'pfl.synthetic_scientific_explorer.v1',
      admission: {R5: 'STOP_R5', real_denominator: null, real_distribution_rights_admitted: false},
      catalog: {
        schema: 'pfl.synthetic_distribution_catalog.v1',
        witness_distributions_redacted: true,
        distributions: [{empirical_distribution_admitted: false, rights_for_requested_purpose_admitted: false}]
      },
      observatory: {schema: 'pfl.synthetic_bitemporal_observatory.v1', real_actor_identity_verified: false}
    },
    warehouse: {b0_b3_witness_sets: {
      schema: 'pfl.synthetic_b0_b3_witness_sets_oracle.v1',
      real_rights_admitted: false, real_denominator: null
    }}
  };
}

function harness() {
  const elements = {}, listeners = {}, requests = [], downloads = [], blobExports = [];
  const pendingExports = [];
  let reloadStatus = 503;
  let registryHandler = null;
  const doc = {
    getElementById(id) {
      return elements[id] ??= {textContent: '', innerHTML: '', addEventListener() {}};
    },
    querySelectorAll() {return [];},
    addEventListener(event, callback) {listeners[event] = callback;},
    createElement() {
      return {href: '', download: '', click() {downloads.push(this.download);}, remove() {}};
    },
    body: {appendChild() {}}
  };
  class LocalURL extends URL {}
  LocalURL.createObjectURL = blob => {blobExports.push(blob);return 'blob:synthetic';};
  LocalURL.revokeObjectURL = () => {};
  const fetch = route => {
    requests.push(route);
    if (route.startsWith('/api/scientific-lab-export?'))
      return new Promise(resolve => pendingExports.push(resolve));
    if (route.startsWith('/api/scientific-integration-lab?'))
      return Promise.resolve({ok: false, status: reloadStatus});
    if (route.startsWith('/api/scientific-registry?') && registryHandler)
      return registryHandler(route);
    throw Error('UNEXPECTED_LOCAL_ROUTE: ' + route);
  };
  const ctx = createContext({
    document: doc, URL: LocalURL, fetch, crypto: webcrypto, TextEncoder, Blob,
    Intl, Date, Number, String, Error, console, setTimeout() {}, clearTimeout() {}
  });
  runInContext(source.slice(0, source.lastIndexOf('bootstrap().catch')), ctx);
  const report = syntheticReport();
  ctx.syntheticFixture = report;
  runInContext("ui.state=null;ui.tab='scientific';ui.scientific=syntheticFixture;ui.scienceCut='late';ui.scienceScenario='baseline';ui.scienceFirstPublic='2026-09-19T12:00:00Z';", ctx);
  function resolveExport(filter = '2026-09-19T12:00:00Z') {
    const data = structuredClone(report);
    data.explorer.catalog.publication_filter_fixture = filter;
    const canonical_json = JSON.stringify(data);
    const bytes = Buffer.byteLength(canonical_json, 'utf8');
    const sha256 = createHash('sha256').update(canonical_json).digest('hex');
    const resolve = pendingExports.shift();
    assert.ok(resolve, 'An export response must be pending');
    resolve({ok: true, json: async () => ({
      schema: 'pfl.synthetic_scientific_export_receipt.v1',
      canonicalization: 'JSON_UTF8_SORTED_KEYS_COMPACT_V1',
      canonical_json, bytes, sha256, R5: 'STOP_R5', empirical_data_exported: false
    })});
  }
  return {ctx, elements, listeners, requests, downloads, blobExports, pendingExports,
    resolveExport, setReloadStatus(status) {reloadStatus=status;},
    setRegistryHandler(handler) {registryHandler=handler;}};
}

test('S9 PREPATCH RED: an old export must not download after first-public filter changes', async () => {
  const h = harness();
  const operation = runInContext('exportScientific()', h.ctx);
  assert.match(h.requests[0], /published_until=2026-09-19/);
  await h.listeners.change({target: {id: 'science-first-public', value: '2026-10-30T12:00:00Z'}});
  assert.equal(runInContext('ui.scienceFirstPublic', h.ctx), '2026-10-30T12:00:00Z');
  h.resolveExport('2026-09-19T12:00:00Z');
  await operation;
  assert.equal(h.downloads.length, 0,
    'Exported bytes from the previous filter must not download under a different selection');
});

test('S9 PREPATCH RED: HTTP 503 reload invalidates a pending, formerly valid export', async () => {
  const h = harness();
  const operation = runInContext('exportScientific()', h.ctx);
  await runInContext('loadScientific()', h.ctx);
  assert.equal(runInContext('ui.scientific', h.ctx), null);
  assert.match(String(runInContext('ui.scientificError', h.ctx)), /503/);
  h.resolveExport();
  await operation;
  assert.equal(h.downloads.length, 0,
    'A failed current scientific report must prevent an earlier export from downloading');
});

test('S9 positive control: unchanged selection exports SHA-verified synthetic receipt', async () => {
  const h = harness();
  const operation = runInContext('exportScientific()', h.ctx);
  h.resolveExport();
  await operation;
  assert.equal(h.downloads.length, 1);
  assert.match(h.downloads[0], /^pfl-s8-late-baseline-[0-9a-f]{12}\.json$/);
});

test('S9 rejects a SHA-valid receipt whose publication filter differs from the requested filter', async () => {
  const h = harness();
  const operation = runInContext('exportScientific()', h.ctx);
  h.resolveExport('2026-10-30T12:00:00Z');
  await operation;
  assert.equal(h.downloads.length, 0,
    'A correct digest must not authenticate a receipt for the wrong publication cut');
});

test('S9 rejects a download even if the first-public selection changes A-to-B-to-A', async () => {
  const h = harness();
  const operation = runInContext('exportScientific()', h.ctx);
  await h.listeners.change({target: {id: 'science-first-public', value: '2026-10-30T12:00:00Z'}});
  await h.listeners.change({target: {id: 'science-first-public', value: '2026-09-19T12:00:00Z'}});
  h.resolveExport();
  await operation;
  assert.equal(h.downloads.length, 0, 'Selection-generation changes invalidate the old export');
});

// This input is obtained from the actual S9 SQLite source contract, not authored
// duplicate registry fixtures. It creates only a temporary, closed synthetic DB.
function actualRegistry(cut='late',validAt='2026-09-15',family='all',published='as_of') {
  const root=new URL('../',import.meta.url).pathname.replace(/^\/(?=[A-Z]:)/i,'');
  const code=[
    'import json,sys,tempfile',
    'from pathlib import Path',
    'from politics_fantasy.scientific_registry import query_registry',
    'with tempfile.TemporaryDirectory(prefix="pfl-s9-ui-test-") as folder:',
    '    result=query_registry(Path(folder)/"closed-synthetic.sqlite3",cut=sys.argv[1],valid_at=sys.argv[2],family=sys.argv[3],published_until=sys.argv[4])',
    '    print(json.dumps(result,ensure_ascii=False))'
  ].join('\n');
  return JSON.parse(execFileSync('python',['-B','-c',code,cut,validAt,family,published],
    {cwd:root,encoding:'utf8',env:{...process.env,PYTHONPATH:'src',
      PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'}}));
}

function registryEndpoint(h, override=null) {
  h.setRegistryHandler(async route=>{
    const url=new URL(route,'http://127.0.0.1');
    if(override)return override(url);
    const q=url.searchParams;
    const data=actualRegistry(q.get('cut'),q.get('valid_at'),
      q.get('family'),q.get('published_until'));
    return {ok:true,json:async()=>data};
  });
}

test('S9 actual SQLite registry is navigable by family/valid_at with public descriptor SHA only',async()=>{
  const h=harness();
  registryEndpoint(h);
  h.ctx.rawRegistryProbe=actualRegistry();
  assert.equal(runInContext("validRegistryPayload(rawRegistryProbe,'late','2026-09-15','all','as_of')",h.ctx),
    true,'closed registry schema must pass before SHA validation');
  assert.equal(await runInContext('verifyRegistryReceipt(rawRegistryProbe)',h.ctx),
    true,'canonical receipt digest and content must pass');
  await runInContext('loadScientificRegistry()',h.ctx);
  let state=runInContext('ui.scienceRegistry',h.ctx);
  assert.ok(state, String(runInContext('ui.scienceRegistryError',h.ctx)));
  assert.equal(state.schema,'pfl.synthetic_scientific_registry.v1');
  assert.equal(state.registry.visible_distribution_count,6);
  assert.equal(state.snapshot.episodes.explicit_negative_documented,1);
  assert.equal(state.snapshot.episodes.right_censor_independently_attested,false);
  assert.equal(state.snapshot.pp04.not_included_source_local_not_negative,2);
  let html=runInContext('scientificRegistryPanel()',h.ctx);
  assert.match(html,/S9:PUBLIC_06/);
  assert.match(html,/SHA de descriptor p/);
  assert.doesNotMatch(html,/SYN:CHAIN_V1|SYN:CHRONICLE_V1|SYN:S9_INTERNAL_STAGE|SYNTHETIC_STAGE_DOCUMENT/);
  await h.listeners.change({target:{id:'science-registry-family',value:'CHAIN'}});
  state=runInContext('ui.scienceRegistry',h.ctx);
  assert.equal(state.family,'CHAIN');
  assert.equal(state.registry.visible_distribution_count,2);
  await h.listeners.change({target:{id:'science-registry-valid',value:'2026-09-11'}});
  state=runInContext('ui.scienceRegistry',h.ctx);
  assert.equal(state.valid_at,'2026-09-11');
  await h.listeners.change({target:{id:'science-registry-family',value:'PP04'}});
  state=runInContext('ui.scienceRegistry',h.ctx);
  assert.equal(state.registry.visible_distribution_count,2);
  assert.equal(state.snapshot.episodes.source_local_all_received_denominator,null);
  assert.equal(state.snapshot.pp04.unplanned_is_a_terminal_negative,false);
  assert.ok(h.requests.some(url=>url.includes('valid_at=2026-09-11')));
  assert.ok(h.requests.some(url=>url.includes('family=PP04')));
});

test('S9 early as_of hides late synthetic sources and never creates negative outcomes',async()=>{
  const h=harness();
  registryEndpoint(h);
  runInContext("ui.scienceCut='early';ui.scientific.cut='early';",h.ctx);
  await runInContext('loadScientificRegistry()',h.ctx);
  const state=runInContext('ui.scienceRegistry',h.ctx);
  assert.ok(state, String(runInContext('ui.scienceRegistryError',h.ctx)));
  assert.equal(state.registry.visible_distribution_count,2);
  assert.equal(state.snapshot.episodes.explicit_negative_documented,0);
  assert.equal(state.snapshot.episodes.pending_documented_not_negative,1);
  assert.equal(state.snapshot.pp04.not_included_source_local_not_negative,0);
  const html=runInContext('scientificRegistryPanel()',h.ctx);
  assert.doesNotMatch(html,/S9:PUBLIC_0[3-6]/);
  assert.match(html,/R5 STOP/);
});

test('S9 registry HTTP 503 clears the prior view, without fallback or hidden source exposure',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  assert.ok(runInContext('ui.scienceRegistry',h.ctx),
    String(runInContext('ui.scienceRegistryError',h.ctx)));
  assert.equal(runInContext('ui.scienceRegistry.registry.visible_distribution_count',h.ctx),6);
  registryEndpoint(h,()=>({ok:false,status:503}));
  await runInContext('loadScientificRegistry()',h.ctx);
  assert.equal(runInContext('ui.scienceRegistry',h.ctx),null);
  assert.match(String(runInContext('ui.scienceRegistryError',h.ctx)),/503/);
  const html=runInContext('scientificRegistryPanel()',h.ctx);
  assert.match(html,/503/);
  assert.doesNotMatch(html,/S9:PUBLIC_0[1-6]/);
});

test('S9 registry forbids raw source IDs/bytes and cross-cut spoofing even with valid fixture SHA',async()=>{
  const h=harness();
  registryEndpoint(h, url=>{
    const q=url.searchParams;
    const data=actualRegistry(q.get('cut'),q.get('valid_at'),
      q.get('family'),q.get('published_until'));
    data.registry.distributions[0].source_id='SYN:CHAIN_V1';
    return {ok:true,json:async()=>data};
  });
  await runInContext('loadScientificRegistry()',h.ctx);
  assert.equal(runInContext('ui.scienceRegistry',h.ctx),null);
  assert.match(String(runInContext('ui.scienceRegistryError',h.ctx)),/Registro incongruente/);
});

test('S9 registry browser-side WebCrypto rejects receipt SHA drift and content mismatch',async()=>{
  for(const tamper of ['SHA_DRIFT','SCOPED_CONTENT_DRIFT']){
    const h=harness();
    registryEndpoint(h,url=>{
      const q=url.searchParams;
      const data=actualRegistry(q.get('cut'),q.get('valid_at'),
        q.get('family'),q.get('published_until'));
      if(tamper==='SHA_DRIFT')data.snapshot_receipt.sha256='0'.repeat(64);
      else data.registry.distributions[0].quality_gate='SYNTHETIC_MUTATION_NOT_IN_RECEIPT';
      return {ok:true,json:async()=>data};
    });
    await runInContext('loadScientificRegistry()',h.ctx);
    assert.equal(runInContext('ui.scienceRegistry',h.ctx),null,tamper);
    assert.match(String(runInContext('ui.scienceRegistryError',h.ctx)),/SHA de recibo incompatible/);
  }
});

test('S9.1 registry export downloads the exact SHA-verified public snapshot, not the S8 report',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  const panel=runInContext('scientificRegistryPanel()',h.ctx);
  assert.match(panel,/data-action="science-registry-export"/);
  await runInContext('exportScientificRegistry()',h.ctx);
  assert.equal(h.downloads.length,1);
  assert.match(h.downloads[0],/^pfl-s9-registry-late-2026-09-15-[0-9a-f]{12}\.json$/);
  const exported=JSON.parse(await h.blobExports[0].text());
  assert.equal(exported.schema,'pfl.synthetic_scientific_registry_browser_export.v1');
  assert.equal(exported.source_contract,'pfl.synthetic_scientific_registry.v1');
  assert.equal(exported.R5,'STOP_R5');
  assert.equal(exported.external_authenticity_certified,false);
  assert.equal(exported.query.valid_at,'2026-09-15');
  const bytes=Buffer.from(exported.snapshot_receipt.canonical_json,'utf8');
  assert.equal(bytes.length,exported.snapshot_receipt.bytes);
  assert.equal(createHash('sha256').update(bytes).digest('hex'),exported.snapshot_receipt.sha256);
  assert.doesNotMatch(await h.blobExports[0].text(),/SYN:CHAIN_V1|SYN:CHRONICLE_V2|SYN:S9_INTERNAL_STAGE/);
});

test('S9.1 registry export blocks a public receipt whose SHA changed after load',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  runInContext("ui.scienceRegistry.snapshot_receipt.sha256='0'.repeat(64)",h.ctx);
  await runInContext('exportScientificRegistry()',h.ctx);
  assert.equal(h.downloads.length,0);
});

test('S9.1 registry export rejects an in-flight A-to-B-to-A registry selection',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  let finishDigest=null;
  h.ctx.crypto={subtle:{digest(algorithm,bytes){
    return new Promise(resolve=>{finishDigest=()=>resolve(webcrypto.subtle.digest(algorithm,bytes));});
  }}};
  const pending=runInContext('exportScientificRegistry()',h.ctx);
  await delay(0);
  assert.equal(typeof finishDigest,'function');
  h.ctx.crypto=webcrypto;
  await h.listeners.change({target:{id:'science-registry-valid',value:'2026-09-11'}});
  await h.listeners.change({target:{id:'science-registry-valid',value:'2026-09-15'}});
  assert.ok(runInContext('ui.scienceRegistry',h.ctx));
  finishDigest();
  await pending;
  assert.equal(h.downloads.length,0,'A newly verified A cannot authorize the previous A receipt');
});

test('S9.1 registry export rejects an in-flight receipt after current HTTP 503',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  let finishDigest=null;
  h.ctx.crypto={subtle:{digest(algorithm,bytes){
    return new Promise(resolve=>{finishDigest=()=>resolve(webcrypto.subtle.digest(algorithm,bytes));});
  }}};
  const pending=runInContext('exportScientificRegistry()',h.ctx);
  await delay(0);
  assert.equal(typeof finishDigest,'function');
  h.ctx.crypto=webcrypto;
  registryEndpoint(h,()=>({ok:false,status:503}));
  await runInContext('loadScientificRegistry()',h.ctx);
  assert.match(String(runInContext('ui.scienceRegistryError',h.ctx)),/503/);
  finishDigest();
  await pending;
  assert.equal(h.downloads.length,0);
});

test('S9.1 durable assessment history is navigable, redacted, and never eight independent sources',async()=>{
  const h=harness();
  registryEndpoint(h);
  await runInContext('loadScientificRegistry()',h.ctx);
  const a=runInContext('ui.scienceRegistry.snapshot.admission_assessments',h.ctx);
  assert.ok(a,String(runInContext('ui.scienceRegistryError',h.ctx)));
  assert.equal(a.assessment_count,8);
  assert.equal(a.history_event_count,16);
  assert.equal(a.source_rows_ingested,0);
  assert.equal(a.real_admission_allowed,false);
  assert.equal(a.assessments.filter(x=>x.status==='ASSESSED_REJECTED_R5').length,8);
  runInContext("ui.scienceRegistryTab='admission'",h.ctx);
  const html=runInContext('scientificRegistryPanel()',h.ctx);
  assert.match(html,/S9:ASSESS_08/);
  assert.match(html,/NO son ocho fuentes/);
  assert.doesNotMatch(html,/SYN:S8_NEW_DISTRIBUTION|SYN:CHAIN_V1|SYN:S9_INTERNAL_STAGE/);
  const early=actualRegistry('early','2026-09-15','all','as_of');
  assert.equal(early.snapshot.admission_assessments.assessment_count,0);
  const censored=actualRegistry('late','2026-09-15','all','2026-10-30T12:00:00Z');
  assert.equal(censored.snapshot.admission_assessments.assessment_count,0);
});

test('S9.1 browser rejects assessment-stage spoofing unless it matches canonical SHA receipt',async()=>{
  const h=harness();
  registryEndpoint(h,url=>{
    const q=url.searchParams;
    const data=actualRegistry(q.get('cut'),q.get('valid_at'),
      q.get('family'),q.get('published_until'));
    data.snapshot.admission_assessments.assessments[0].history[0].status='EMPIRICALLY_ADMITTED';
    return {ok:true,json:async()=>data};
  });
  await runInContext('loadScientificRegistry()',h.ctx);
  assert.equal(runInContext('ui.scienceRegistry',h.ctx),null);
  assert.match(String(runInContext('ui.scienceRegistryError',h.ctx)),/Registro incongruente|SHA de recibo incompatible/);
});

async function freeLocalPort(){
  return new Promise((resolve,reject)=>{
    const server=createServer();
    server.once('error',reject);
    server.listen(0,'127.0.0.1',()=>{
      const port=server.address().port;
      server.close(()=>resolve(port));
    });
  });
}

test('S9 actual localhost HTTP registry feeds real app.js DOM harness without leaking internal IDs',async()=>{
  const root=new URL('../',import.meta.url).pathname.replace(/^\/(?=[A-Z]:)/i,'');
  const scratch=mkdtempSync(join(tmpdir(),'pfl-s9-http-ui-'));
  const port=await freeLocalPort();
  const base='http://127.0.0.1:'+port;
  let server=null;
  try{
    server=spawn('python',['-B','-m','politics_fantasy.server',
      '--db',join(scratch,'game.sqlite3'),'--port',String(port)],{
      cwd:root,env:{...process.env,PYTHONPATH:'src',
        PYTHONDONTWRITEBYTECODE:'1',PYTHONIOENCODING:'utf-8'},
      stdio:'ignore'
    });
    let ready=false;
    for(let attempt=0;attempt<70;attempt++){
      if(server.exitCode!==null)break;
      try{
        const health=await fetch(base+'/api/health',{signal:AbortSignal.timeout(1000)});
        if(health.ok){ready=true;break;}
      }catch(_){}
      await delay(75);
    }
    assert.equal(ready,true,'Isolated localhost API did not start');
    const h=harness();
    h.setRegistryHandler(route=>fetch(base+route,{cache:'no-store'}));
    await runInContext('loadScientificRegistry()',h.ctx);
    const state=runInContext('ui.scienceRegistry',h.ctx);
    assert.ok(state,String(runInContext('ui.scienceRegistryError',h.ctx)));
    assert.equal(state.registry.visible_distribution_count,6);
    const html=runInContext('scientificRegistryPanel()',h.ctx);
    assert.match(html,/S9:PUBLIC_06/);
    assert.doesNotMatch(html,/SYN:CHAIN_V1|SYN:CHRONICLE_V2|SYN:S9_INTERNAL_STAGE/);
    const early=await fetch(base+'/api/scientific-registry?cut=early&valid_at=2026-09-15');
    assert.equal(early.status,200);
    assert.equal((await early.json()).registry.visible_distribution_count,2);
    const bad=await fetch(base+'/api/scientific-registry?cut=early&published_until=2026-10-30T12:00:00Z');
    assert.equal(bad.status,400);
  }finally{
    if(server&&server.exitCode===null){
      const done=new Promise(resolve=>server.once('close',resolve));
      server.kill();
      await Promise.race([done,delay(3000)]);
    }
    rmSync(scratch,{recursive:true,force:true,maxRetries:3,retryDelay:100});
  }
});
