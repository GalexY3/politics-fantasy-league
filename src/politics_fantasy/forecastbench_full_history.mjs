/**
 * Complete observed repository path histories, capped at Git history checked
 * 2026-10-29 16:00Z. Public event-question/resolution data only; no personal
 * forecasts. Read-only source: forecastingresearch/forecastbench-datasets.
 * The version lists are original GitHub commits changing EACH resolution file.
 * No interpolation across unknown version histories or future updates.
 */
import {inspectPublicCohort} from './forecastbench_vintage_replay.mjs';
export const VERIFIED_AT='2026-10-29T16:00:00Z';
export const ORIGINAL_QUESTIONS=Object.freeze({
 '2026-09-27':Object.freeze({at:'2026-09-27T00:08:59Z',git:'d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0'}),
 '2026-10-11':Object.freeze({at:'2026-10-11T00:06:25Z',git:'fe9772f2275edcada671c4082cf9103185f1becf'})
});
const R27=[
 ['2026-10-07T07:19:29Z','4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110','0b67cfec67fad4b23899e8e48c6ca3a034344edc'],
 ['2026-10-08T07:01:49Z','d354d26d6f3feb03bacc363f6b346232645e8550','2efa48b677c7c4e8a4827585d49c4f59393e233e'],
 ['2026-10-09T07:01:29Z','8cae09d792922fa2580a7c7c5482c76b9710e3c3','59397edd6428a248e74d56ccd7af69d758aee604'],
 ['2026-10-10T06:51:43Z','b977388e168b338d47d53f567ab023d19ae2719e','02efeb0cb0c74d65415551e7cc18beded2ace212'],
 ['2026-10-11T06:35:43Z','3928408907498c991bc367c2d3493241aa19e516','424965825aae022f5861b69d17880665cd3026bb'],
 ['2026-10-12T07:03:09Z','d6dac818ec036aa8fa41dfc1fcb369d24ca81ce4','ea2f96ee0b30f248f3b9d1b61bd63fa03e938ec3'],
 ['2026-10-13T06:46:08Z','4629a73c505a0d619ef0ee59e697d57d21015131','0bd4533837ccfe2b14f6f23459daccf29a906ef4'],
 ['2026-10-14T06:55:40Z','ab1df37b3ccda9765d4879ddd52c2a9b4e6cad7b','55d87d015ab7cbd06cf1065f3c094d4918357846'],
 ['2026-10-15T07:34:05Z','dc59cac62b32dde8fb942f87af1f063af942cc79','97166cd083574ffb7462e2ff281113bff9608c16'],
 ['2026-10-16T06:49:58Z','dc4a1511374cb641dd31aa688bc1bcd93f0fb1f2','2dbd04d35e5197d12e634e6217262ba42aa2174e'],
 ['2026-10-17T07:31:51Z','c870c1124aa51cd16b4bc0276a8b89bd1ab941c7','60380b27cc293441ec02e4b05d95df29625252e7'],
 ['2026-10-18T07:26:33Z','f1698426edba99423344f6abb7619f3c4c9ee4f8','2a1821161d5a963137393bce94de8de415bc8cf3'],
 ['2026-10-19T07:03:18Z','11a93354f70453c45f6080482c45b4caf3db9a44','07b75c45860f556ad00e9f9863b094b29a052938'],
 ['2026-10-23T06:53:25Z','f3d8a4f83754f6c26990c67c69185f91f214c30c','9d17e5f8487ae2cad9c9d3130c3006cd1cc5d880'],
 ['2026-10-24T07:39:55Z','420dc4f3a1e23774347da7b199c58592dce45448','5fd032d0df1eea0dc47880bb3c640e6f75ab7fcd'],
 ['2026-10-29T07:30:17Z','027ba0b3017a60e0e64602d724284ac6b2d91134','b2ee53f09407e2b555668f66e286073ace6d5fce']
];
const R11=[
 ['2026-10-23T06:53:25Z','f3d8a4f83754f6c26990c67c69185f91f214c30c','1556a17106131cf8a7d7cb3b33122d18c3b9ef6a'],
 ['2026-10-24T07:39:55Z','420dc4f3a1e23774347da7b199c58592dce45448','0c535475a4037a47ecf009c933d635fd49f67e29'],
 ['2026-10-29T07:30:17Z','027ba0b3017a60e0e64602d724284ac6b2d91134','d8416bccbfcd4736e9772748bb42fd4cc403db7e']
];
export const RESOLUTION_VERSIONS=Object.freeze({
 '2026-09-27':Object.freeze(R27.map(r=>Object.freeze({at:r[0],commit:r[1],git:r[2]}))),
 '2026-10-11':Object.freeze(R11.map(r=>Object.freeze({at:r[0],commit:r[1],git:r[2]})))
});
const utc=s=>{
 if(typeof s!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s))throw Error('UTC_SECONDS_REQUIRED');
 const n=Date.parse(s);
 if(!Number.isFinite(n)||new Date(n).toISOString()!==s.replace('Z','.000Z'))throw Error('UTC_SECONDS_REQUIRED');
 return n;
};
const key=x=>JSON.stringify([x.source,x.id]);
export function versionAt(cohort,asOfInstant){
 const now=utc(asOfInstant);
 if(now>utc(VERIFIED_AT))throw Error('SOURCE_HISTORY_NOT_VERIFIED_AFTER_CUTOFF');
 const question=ORIGINAL_QUESTIONS[cohort],records=RESOLUTION_VERSIONS[cohort];
 if(!question||!records)throw Error('UNSUPPORTED_COHORT');
 if(now<utc(question.at))return Object.freeze({status:'QUESTION_COHORT_NOT_YET_PUBLISHED',cohort,as_of_instant:asOfInstant});
 const available=records.filter(v=>utc(v.at)<=now);
 if(!available.length)return Object.freeze({status:'RESOLUTION_DATASET_NOT_YET_PUBLISHED',cohort,as_of_instant:asOfInstant});
 const source=available[available.length-1];
 return Object.freeze({status:'VERIFIED_PATH_SOURCE_VERSION',cohort,as_of_instant:asOfInstant,
  question_git:question.git,resolution_git:source.git,commit:source.commit,committed_at:source.at,
  source_git_history_complete_in_checked_window:true,not_individual_event_publication:true});
}
export function timelineFromOriginals(cohort,questionObject,resolutionsByGit){
 if(!ORIGINAL_QUESTIONS[cohort]||!resolutionsByGit||typeof resolutionsByGit!=='object')
  throw Error('MISSING_OR_UNSUPPORTED_PUBLIC_COHORT');
 const versions=RESOLUTION_VERSIONS[cohort],q=ORIGINAL_QUESTIONS[cohort];
 const records=[],seen=new Map();let prior=null,oldHash=null;
 for(const [index,v] of versions.entries()){
  if(!Object.hasOwn(resolutionsByGit,v.git))throw Error('MISSING_ORIGINAL_GIT_BLOB');
  const source=resolutionsByGit[v.git];
  const next=versions[index+1];
  const d=new Date(utc(v.at)+12*60*60*1000);
  const target=new Date(Math.min(utc(VERIFIED_AT),next&&d.getTime()>=utc(next.at)?utc(v.at)+60*1000:d.getTime()));
  const cutoff=target.toISOString().replace('.000Z','Z');
  const check=versionAt(cohort,cutoff);
  if(check.commit!==v.commit)throw Error('INCOMPLETE_OR_MISORDERED_VERSION_HISTORY');
  const out=inspectPublicCohort(questionObject,source,{cohort,as_of_instant:cutoff});
  let retained=0,flips=0;
  if(prior)for(const [id,y] of prior){if(out.accepted.has(id)){retained++;if(out.accepted.get(id)!==y)flips++}}
  const lost=prior?prior.size-retained:0;
  const added=prior?out.accepted.size-retained:out.accepted.size;
  records.push({ordinal:index+1,commit:v.commit,committed_at:v.at,resolution_git:v.git,
    evaluation_instant:cutoff,source_rows:out.report.source_resolution_row_count,accepted:out.report.accepted,
    newly_known:added,lost_known:lost,flipped_known:flips,retained_known:retained,
    brier_resolved_only:out.report.brier_resolved_only,
    market_question_count:out.report.market_question_count});
  prior=out.accepted;oldHash=v.git;
 }
 return {schema:'pfl.public.original.full_history.v1',cohort,question_git:q.git,
  path_versions:versions.length,question_count:questionObject.questions?.length??null,
  records,total_new:records.reduce((s,r)=>s+r.newly_known,0),
  total_lost:records.reduce((s,r)=>s+r.lost_known,0),
  total_flipped:records.reduce((s,r)=>s+r.flipped_known,0),
  original_git_history_checked_at:VERIFIED_AT,original_human_rows:0,
  science_causal_grade:'0/3',original_question_text_redistributed:false,
  per_item_first_public_at_verified:false,market_forecast_accuracy_generalization:false,launch_ready:false};
}
