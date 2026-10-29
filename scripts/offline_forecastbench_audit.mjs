/**
 * Offline read-only, non-personal public-question audit for PFL. This is NOT a
 * deployed feature, a participant study, or a source-rights attestation.
 * Dataset attribution: Forecasting Research Institute / Karger et al. (ICLR
 * 2025), forecastingresearch/forecastbench-datasets, CC BY-SA 4.0.
 */
import {open} from 'node:fs/promises';
import {constants} from 'node:fs';
import {resolve, join} from 'node:path';
import {pathToFileURL} from 'node:url';
import {verifyBlobAgainstExpected, PUBLIC_DATASET_PIN} from '../src/politics_fantasy/forecastbench_provenance.mjs';
import {auditPublicForecastQuestions} from '../src/politics_fantasy/forecastbench_source_guard.mjs';
import {assertPublicDatasetPublished} from '../src/politics_fantasy/forecastbench_publication_gate.mjs';

const names=Object.keys(PUBLIC_DATASET_PIN.blobs);
const MAX_BYTES=5_000_000;

/** Pure public-question audit; test maps have NO evidential standing. */
export function auditBuffers(buffers,{as_of_instant,expected_blobs=PUBLIC_DATASET_PIN.blobs}={}){
 if(!buffers||typeof buffers!=='object'||Array.isArray(buffers)||
    Reflect.ownKeys(buffers).length!==names.length||
    names.some(n=>!Object.hasOwn(buffers,n)))throw Error('EXPECTED_FOUR_FILES');
 if(!expected_blobs||typeof expected_blobs!=='object'||Array.isArray(expected_blobs)||
    Reflect.ownKeys(expected_blobs).length!==names.length||
    names.some(n=>!Object.hasOwn(expected_blobs,n)))throw Error('INVALID_EXPECTED_MANIFEST');
 // Fail before parsing any source rows, including test-only untrusted manifests.
 const source_publication=assertPublicDatasetPublished({as_of_instant,source_commit:PUBLIC_DATASET_PIN.commit});
 const as_of_date=source_publication.event_cutoff_date;
 const objects=Object.create(null);
 for(const name of names){
  verifyBlobAgainstExpected(buffers[name],expected_blobs[name]);
  try{objects[name]=JSON.parse(buffers[name].toString('utf8'))}
  catch{throw Error('INVALID_PUBLIC_DATASET_JSON')}
 }
 const results=[];
 for(const date of ['2026-09-27','2026-10-11']){
  const q=objects['question_sets/'+date+'-llm.json'];
  const r=objects['resolution_sets/'+date+'_resolution_set.json'];
  results.push(auditPublicForecastQuestions(q,r,{as_of_date}));
 }
 return Object.freeze({
  schema:'pfl.public.forecastbench.offline_audit.v1',
  upstream_repo:PUBLIC_DATASET_PIN.repo,
  declared_upstream_commit:PUBLIC_DATASET_PIN.commit,
  source_publication,
  declared_manifest_matches_bytes:true,
  used_project_manifest:expected_blobs===PUBLIC_DATASET_PIN.blobs,
  datasets:results,
  rights_independently_attested:false,
  personal_forecasts_processed:false,
  science_causal_grade:'0/3',
  release_ready:false,
  caveat:'Git byte identity and source cohort audits are not publisher authentication, participant-level evidence or a legal reuse decision'
 });
}

async function readPinnedFile(base,name){
 const path=resolve(base,...name.split('/'));
 // O_NOFOLLOW stops final-component symlink replacement on POSIX; bounded
 // handle.stat prevents reading a large file. No path comes from user JSON.
 const handle=await open(path,constants.O_RDONLY|(constants.O_NOFOLLOW||0));
 try{
  const s=await handle.stat();
  if(!s.isFile()||s.size<=0||s.size>MAX_BYTES)throw Error('INVALID_PUBLIC_FILE_SIZE');
  return await handle.readFile();
 }finally{await handle.close()}
}

export async function runOfflineAudit({source_dir,as_of_instant}){
 if(typeof source_dir!=='string'||!source_dir.trim())throw Error('SOURCE_DIR_REQUIRED');
 // Prevent disk IO and any inference from a source snapshot published after cutoff.
 assertPublicDatasetPublished({as_of_instant,source_commit:PUBLIC_DATASET_PIN.commit});
 const buffers=Object.create(null);
 for(const name of names)buffers[name]=await readPinnedFile(source_dir,name);
 return auditBuffers(buffers,{as_of_instant});
}

function parseArgs(args){
 if(args.length!==4||args[0]!=='--source-dir'||args[2]!=='--as-of-instant')
  throw Error('USAGE_SOURCE_DIR_AND_AS_OF_DATE');
 return {source_dir:args[1],as_of_instant:args[3]};
}
export async function main(args=process.argv.slice(2)){
 const report=await runOfflineAudit(parseArgs(args));
 process.stdout.write(JSON.stringify(report,null,2)+'\n');
 return report;
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 main().catch(e=>{
  // Only safe bounded category, never a private path or a question string.
  const known=['EXPECTED_FOUR_FILES','INVALID_EXPECTED_MANIFEST','INVALID_PUBLIC_DATASET_JSON',
   'INVALID_PUBLIC_FILE_SIZE','ORIGINAL_SOURCE_BYTES_MISMATCH','USAGE_SOURCE_DIR_AND_AS_OF_DATE',
   'SOURCE_DIR_REQUIRED','COHORT_MISMATCH','INVALID_CUTOFF','ROW_ACCOUNTING_FAIL',
   'INVALID_AS_OF_INSTANT','UNVERIFIED_SOURCE_COMMIT','SOURCE_NOT_PUBLIC_AT_CUTOFF'];
  const code=known.includes(e.message)?e.message:'SOURCE_INPUT_UNAVAILABLE_OR_INVALID';
  process.stderr.write('AUDIT_FAILED:'+code+'\n');
  process.exitCode=2;
 });
}
