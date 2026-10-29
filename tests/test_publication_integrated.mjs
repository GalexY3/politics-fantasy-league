import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {gitBlobHash,PUBLIC_DATASET_PIN} from '../src/politics_fantasy/forecastbench_provenance.mjs';
import {PINNED_SOURCE_PUBLICATION,assertPublicDatasetPublished} from '../src/politics_fantasy/forecastbench_publication_gate.mjs';
import {auditBuffers,runOfflineAudit} from '../scripts/offline_forecastbench_audit.mjs';
const published='2026-10-29T07:30:17Z';
const after='2026-10-29T16:00:00Z';
const before='2026-10-29T07:30:16Z';
const pub=()=>({as_of_instant:after,source_commit:PUBLIC_DATASET_PIN.commit});
const enc=(x)=>Buffer.from(JSON.stringify(x),'utf8');
function fixture(){
 const files=Object.create(null);
 for(const date of ['2026-09-27','2026-10-11']){
  files['question_sets/'+date+'-llm.json']=enc({forecast_due_date:date,question_set:date+'-llm.json',questions:[{source:'metaculus',id:'fictional',freeze_datetime:'2026-09-01T00:00:00Z',freeze_datetime_value:'0.8'}]});
  files['resolution_sets/'+date+'_resolution_set.json']=enc({forecast_due_date:date,question_set:date+'-llm.json',resolutions:[{source:'metaculus',id:'fictional',resolved:true,resolved_to:1,resolution_date:'2026-10-20'}]});
 }
 const hashes=Object.fromEntries(Object.entries(files).map(([k,v])=>[k,gitBlobHash(v)]));
 return {files,hashes};
}
let n=0;
async function test(label,fn){await fn();n++;console.log('PASS '+n+' '+label)}
await test('source commit date is the published original GitHub snapshot',()=>{
 assert.equal(PINNED_SOURCE_PUBLICATION.committed_at,published);
 assert.equal(PINNED_SOURCE_PUBLICATION.commit,PUBLIC_DATASET_PIN.commit);
});
await test('Oct01 prior retrospective day always rejects the Oct29 source',()=>{
 assert.throws(()=>assertPublicDatasetPublished({as_of_instant:'2026-10-01T23:59:59Z',source_commit:PUBLIC_DATASET_PIN.commit}),/SOURCE_NOT_PUBLIC_AT_CUTOFF/);
});
await test('Oct08 prior snapshot still cannot use Oct29 source',()=>{
 assert.throws(()=>assertPublicDatasetPublished({as_of_instant:'2026-10-08T00:00:00Z',source_commit:PUBLIC_DATASET_PIN.commit}),/SOURCE_NOT_PUBLIC_AT_CUTOFF/);
});
await test('just before publish is not allowed',()=>{
 assert.throws(()=>assertPublicDatasetPublished({as_of_instant:before,source_commit:PUBLIC_DATASET_PIN.commit}),/SOURCE_NOT_PUBLIC_AT_CUTOFF/);
});
await test('exact published second is allowed with source-only caveats',()=>{
 const r=assertPublicDatasetPublished({as_of_instant:published,source_commit:PUBLIC_DATASET_PIN.commit});
 assert.equal(r.original_git_snapshot_available_at_cutoff,true);
 assert.equal(r.per_record_first_public_at_verified,false);
 assert.equal(r.rights_independently_attested,false);
});
await test('valid later as-of maintains explicit source timestamp',()=>{
 const r=assertPublicDatasetPublished(pub());
 assert.equal(r.git_commit_at,published);assert.equal(r.event_cutoff_date,'2026-10-29');
});
await test('non UTC, date-only, invalid calendar and fractional times denied',()=>{
 for(const s of ['2026-10-29','2026-10-29T09:30:17+02:00','2026-10-29T07:30:17.000Z','2026-10-40T12:00:00Z','2026-10-29T07:30Z']){
  assert.throws(()=>assertPublicDatasetPublished({as_of_instant:s,source_commit:PUBLIC_DATASET_PIN.commit}),/INVALID_AS_OF_INSTANT/);
 }
});
await test('unrecognized source commit denied, even if date later',()=>{
 assert.throws(()=>assertPublicDatasetPublished({as_of_instant:after,source_commit:'0'.repeat(40)}),/UNVERIFIED_SOURCE_COMMIT/);
});
await test('old date-only API cannot silently default to later instant',()=>{
 const {files,hashes}=fixture();
 assert.throws(()=>auditBuffers(files,{as_of_date:'2026-10-29',expected_blobs:hashes}),/INVALID_AS_OF_INSTANT/);
});
await test('integrated pure audit rejects future published original before parsing',()=>{
 const {files,hashes}=fixture();
 assert.throws(()=>auditBuffers(files,{as_of_instant:before,expected_blobs:hashes}),/SOURCE_NOT_PUBLIC_AT_CUTOFF/);
});
await test('test fixture can be counted only with explicit untrusted-manifest flag',()=>{
 const {files,hashes}=fixture(); const r=auditBuffers(files,{as_of_instant:after,expected_blobs:hashes});
 assert.deepEqual(r.datasets.map(x=>x.accepted),[1,1]);assert.equal(r.used_project_manifest,false);
 assert.equal(r.source_publication.per_record_first_public_at_verified,false);
 assert.equal(r.release_ready,false);assert.equal(r.rights_independently_attested,false);
 assert.equal(JSON.stringify(r).includes('fictional'),false);
});
await test('same fake bytes cannot impersonate the real four pinned source files',()=>{
 const {files}=fixture();assert.throws(()=>auditBuffers(files,{as_of_instant:after}),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
});
await test('missing file rejected for supported as-of',()=>{
 const {files,hashes}=fixture();delete files['question_sets/2026-09-27-llm.json'];
 assert.throws(()=>auditBuffers(files,{as_of_instant:after,expected_blobs:hashes}),/EXPECTED_FOUR_FILES/);
});
const folder=await mkdtemp(join(tmpdir(),'pfl-snapshot-gate-'));
try{
 const {files}=fixture();for(const [name,buf] of Object.entries(files)){
  const [dirname]=name.split('/');await mkdir(join(folder,dirname),{recursive:true});await writeFile(join(folder,name),buf);
 }
 await test('native disk reader refuses historical source before any disk read',async()=>{
  await assert.rejects(runOfflineAudit({source_dir:join(folder,'missing'),as_of_instant:before}),/SOURCE_NOT_PUBLIC_AT_CUTOFF/);
 });
 await test('native CLI refuses Oct01 time without reading data and leaks no path',()=>{
  const run=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--source-dir',join(folder,'missing'),'--as-of-instant','2026-10-01T23:59:59Z'],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(run.status,2);assert.equal(run.stdout,'');assert.equal(run.stderr,'AUDIT_FAILED:SOURCE_NOT_PUBLIC_AT_CUTOFF\n');
  assert.equal(run.stderr.includes(folder),false);
 });
 await test('native CLI refuses legacy --as-of-date argument rather than silently leak',()=>{
  const run=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--source-dir',folder,'--as-of-date','2026-10-29'],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(run.status,2);assert.equal(run.stdout,'');assert.equal(run.stderr,'AUDIT_FAILED:USAGE_SOURCE_DIR_AND_AS_OF_INSTANT\n');
 });
 await test('native CLI with correct time and synthetic bytes fails original hashes',()=>{
  const run=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--source-dir',folder,'--as-of-instant',after],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(run.status,2);assert.equal(run.stdout,'');assert.equal(run.stderr,'AUDIT_FAILED:ORIGINAL_SOURCE_BYTES_MISMATCH\n');
 });
 await test('native CLI with malformed time rejects before source bytes',()=>{
  const run=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--source-dir',folder,'--as-of-instant','2026-10-29'],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(run.status,2);assert.equal(run.stderr,'AUDIT_FAILED:INVALID_AS_OF_INSTANT\n');
 });
}finally{await rm(folder,{recursive:true,force:true})}
console.log('PFL bitemporal publication CLI '+n+'/18 PASS');
