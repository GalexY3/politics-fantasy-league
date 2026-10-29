/**
 * Source-pinned ORIGINAL PUBLIC (non-personal) ForecastBench vintage replay CLI.
 * Operator provides original raw bytes locally. No network; no source question
 * texts, IDs or individual forecast rows are printed or added to repository.
 */
import {open} from 'node:fs/promises';
import {constants} from 'node:fs';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {gitBlobHash} from '../src/politics_fantasy/forecastbench_provenance.mjs';
import {planVintagePair,replayOriginalPair} from '../src/politics_fantasy/forecastbench_vintage_replay.mjs';
const MAX=5_000_000;
async function readVerified(root,commit,cohort,kind,expected){
 const filename=kind==='questions'?cohort+'-llm.json':cohort+'_resolution_set.json';
 const dir=kind==='questions'?'question_sets':'resolution_sets';
 const path=resolve(root,commit,dir,filename);
 const h=await open(path,constants.O_RDONLY|(constants.O_NOFOLLOW||0));
 try{
  const s=await h.stat();
  if(!s.isFile()||s.size<1||s.size>MAX)throw Error('INVALID_SOURCE_FILE_SIZE');
  const bytes=await h.readFile();
  if(gitBlobHash(bytes)!==expected)throw Error('ORIGINAL_VINTAGE_BLOB_MISMATCH');
  try{return JSON.parse(bytes.toString('utf8'))}
  catch{throw Error('ORIGINAL_PUBLIC_JSON_INVALID')}
 }finally{await h.close()}
}
export async function replayVerifiedSource({snapshot_dir,from_instant,to_instant}={}){
 if(typeof snapshot_dir!=='string'||!snapshot_dir.trim())throw Error('SOURCE_DIR_REQUIRED');
 const plan=planVintagePair(from_instant,to_instant);
 const from={},to={};
 for(const [v,store] of [[plan.from,from],[plan.to,to]]){
  for(const [cohort,blob] of Object.entries(v.cohorts)){
   store[cohort]={
    questions:await readVerified(snapshot_dir,v.commit,cohort,'questions',blob.questions),
    resolutions:await readVerified(snapshot_dir,v.commit,cohort,'resolutions',blob.resolutions)
   };
  }
 }
 const report=replayOriginalPair({from,to,from_instant,to_instant});
 return Object.freeze({...report,original_public_git_blob_bytes_verified:true,
  native_offline_cli:true,real_human_data_processed:false,
  release_ready:false,notes:['Source versions byte-match frozen original Git manifests','No independent per-event first publication or human treatment exposure verified']});
}
function parse(args){
 if(args.length!==6||args[0]!=='--snapshots-dir'||args[2]!=='--from'||args[4]!=='--to')
  throw Error('USAGE_SNAPSHOTS_DIR_FROM_TO');
 return {snapshot_dir:args[1],from_instant:args[3],to_instant:args[5]};
}
export async function main(args=process.argv.slice(2)){
 const report=await replayVerifiedSource(parse(args));
 process.stdout.write(JSON.stringify(report,null,2)+'\n');
}
if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
 main().catch(e=>{
  const safe=['USAGE_SNAPSHOTS_DIR_FROM_TO','SOURCE_DIR_REQUIRED','INVALID_REPLAY_ORDER',
  'NO_VERIFIED_PUBLIC_VINTAGE','NONCANONICAL_INSTANT','INVALID_INSTANT',
  'NO_DISTINCT_VERIFIED_SOURCE_VERSION','INVALID_SOURCE_FILE_SIZE',
  'ORIGINAL_VINTAGE_BLOB_MISMATCH','ORIGINAL_PUBLIC_JSON_INVALID',
  'COHORT_MISMATCH','INVALID_QUESTION_ID','DUPLICATE_QUESTION_KEY',
  'MISSING_COHORT_FOR_REPLAY'];
  process.stderr.write('REPLAY_FAILED:'+(safe.includes(e.message)?e.message:'SOURCE_INPUT_UNAVAILABLE_OR_INVALID')+'\n');
  process.exitCode=2;
 });
}
