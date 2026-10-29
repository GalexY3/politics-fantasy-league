import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,symlink,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {gitBlobHash,PUBLIC_DATASET_PIN} from '../src/politics_fantasy/forecastbench_provenance.mjs';
import {auditBuffers,runOfflineAudit} from '../scripts/offline_forecastbench_audit.mjs';
let pass=0;
const check=async(name,fn)=>{await fn();pass++;process.stdout.write('PASS '+pass+' '+name+'\n')};
const names=Object.keys(PUBLIC_DATASET_PIN.blobs);
const enc=x=>Buffer.from(JSON.stringify(x),'utf8');
function fake(){
 const files=Object.create(null);
 for(const date of ['2026-09-27','2026-10-11']){
  files['question_sets/'+date+'-llm.json']=enc({forecast_due_date:date,question_set:date+'-llm.json',questions:[{source:'metaculus',id:'fictional',freeze_datetime:'2026-09-01T00:00:00Z',freeze_datetime_value:'0.8'}]});
  files['resolution_sets/'+date+'_resolution_set.json']=enc({forecast_due_date:date,question_set:date+'-llm.json',resolutions:[{source:'metaculus',id:'fictional',resolved:true,resolved_to:1,resolution_date:'2026-10-20'}]});
 }
 const hashes=Object.fromEntries(names.map(k=>[k,gitBlobHash(files[k])]));
 return {files,hashes};
}
await check('synthetic exact four-file hash produces aggregate only, never personal or authenticated',()=>{
 const {files,hashes}=fake();const r=auditBuffers(files,{as_of_date:'2026-10-29',expected_blobs:hashes});
 assert.equal(r.datasets.length,2);assert.deepEqual(r.datasets.map(x=>x.accepted),[1,1]);
 assert.equal(r.used_project_manifest,false);assert.equal(r.rights_independently_attested,false);
 assert.equal(r.personal_forecasts_processed,false);assert.equal(r.release_ready,false);
 assert.equal(JSON.stringify(r).includes('fictional'),false);
});
await check('earlier as-of excludes future outcome in both cohorts',()=>{
 const {files,hashes}=fake();const r=auditBuffers(files,{as_of_date:'2026-10-15',expected_blobs:hashes});
 assert.deepEqual(r.datasets.map(x=>x.accepted),[0,0]);
 assert.deepEqual(r.datasets.map(x=>x.reasons.resolution_not_known_by_cutoff),[1,1]);
});
await check('published pinned four original hashes cannot be defeated with fake fixture',()=>{
 const {files}=fake();assert.throws(()=>auditBuffers(files,{as_of_date:'2026-10-29'}),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
});
await check('mutating a value after computing the manifest rejects entire record',()=>{
 const {files,hashes}=fake();files[names[0]]=Buffer.from(files[names[0]].toString().replace('0.8','0.7'));
 assert.throws(()=>auditBuffers(files,{as_of_date:'2026-10-29',expected_blobs:hashes}),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
});
await check('partial file set or extra file rejected before audit',()=>{
 const {files,hashes}=fake();const partial={...files};delete partial[names[1]];
 assert.throws(()=>auditBuffers(partial,{as_of_date:'2026-10-29',expected_blobs:hashes}),/EXPECTED_FOUR_FILES/);
 assert.throws(()=>auditBuffers({...files,'private-forecasts.json':Buffer.from('{}')},{as_of_date:'2026-10-29',expected_blobs:hashes}),/EXPECTED_FOUR_FILES/);
});
await check('invalid JSON rejected after matching exact bytes without echoing source',()=>{
 const {files,hashes}=fake();files[names[0]]=Buffer.from('{private item');hashes[names[0]]=gitBlobHash(files[names[0]]);
 assert.throws(()=>auditBuffers(files,{as_of_date:'2026-10-29',expected_blobs:hashes}),/INVALID_PUBLIC_DATASET_JSON/);
});
await check('no supplied source path fails closed',async()=>{
 await assert.rejects(runOfflineAudit({source_dir:'',as_of_date:'2026-10-29'}),/SOURCE_DIR_REQUIRED/);
});
const root=await mkdtemp(join(tmpdir(),'pfl-offline-audit-'));
try{
 const {files}=fake();for(const name of names){
  const path=join(root,...name.split('/'));await mkdir(join(root,name.split('/')[0]),{recursive:true});await writeFile(path,files[name]);
 }
 await check('real Node file IO refuses four raw files with wrong original SHA, no silent fallback',async()=>{
  await assert.rejects(runOfflineAudit({source_dir:root,as_of_date:'2026-10-29'}),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
 });
 await check('CLI never emits question text or path on invalid source, nonzero exit',()=>{
  const result=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--source-dir',root,'--as-of-date','2026-10-29'],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(result.status,2);assert.equal(result.stdout,'');assert.match(result.stderr,/AUDIT_FAILED:ORIGINAL_SOURCE_BYTES_MISMATCH/);
  assert.equal(result.stderr.includes('fictional'),false);assert.equal(result.stderr.includes(root),false);
 });
 await check('CLI rejects argument shape before file IO',()=>{
  const result=spawnSync(process.execPath,['scripts/offline_forecastbench_audit.mjs','--wrong',root,'--as-of-date','2026-10-29'],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(result.status,2);assert.match(result.stderr,/AUDIT_FAILED:USAGE_SOURCE_DIR_AND_AS_OF_DATE/);
 });
 await check('symlink final component never accepted as authoritative source',async()=>{
  const victim=join(root,'question_sets','2026-09-27-llm.json');await rm(victim);
  await symlink(join(root,'resolution_sets','2026-10-11_resolution_set.json'),victim);
  await assert.rejects(runOfflineAudit({source_dir:root,as_of_date:'2026-10-29'}));
 });
}finally{await rm(root,{recursive:true,force:true});}
process.stdout.write('PFL offline public audit '+pass+'/11 PASS\n');
