/**
 * PFL public, non-person, bi-temporal source replay. Exactly three independently
 * inspected original Git repository source versions; never construct a historical
 * risk set from the last observed version of an event.
 *
 * Original public source: Forecasting Research Institute / Karger et al.
 * ForecastBench ICLR 2025; official repository data CC BY-SA 4.0.
 * This code never reproduces question text or individual forecasts.
 */
export const SOURCE_VINTAGES=Object.freeze([
 {at:'2026-10-07T07:19:29Z',commit:'4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110',
  cohorts:Object.freeze({
   '2026-09-27':Object.freeze({questions:'d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0',resolutions:'0b67cfec67fad4b23899e8e48c6ca3a034344edc'})})},
 {at:'2026-10-23T06:53:25Z',commit:'f3d8a4f83754f6c26990c67c69185f91f214c30c',
  cohorts:Object.freeze({
   '2026-09-27':Object.freeze({questions:'d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0',resolutions:'9d17e5f8487ae2cad9c9d3130c3006cd1cc5d880'}),
   '2026-10-11':Object.freeze({questions:'fe9772f2275edcada671c4082cf9103185f1becf',resolutions:'1556a17106131cf8a7d7cb3b33122d18c3b9ef6a'})})},
 {at:'2026-10-29T07:30:17Z',commit:'027ba0b3017a60e0e64602d724284ac6b2d91134',
  cohorts:Object.freeze({
   '2026-09-27':Object.freeze({questions:'d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0',resolutions:'b2ee53f09407e2b555668f66e286073ace6d5fce'}),
   '2026-10-11':Object.freeze({questions:'fe9772f2275edcada671c4082cf9103185f1becf',resolutions:'d8416bccbfcd4736e9772748bb42fd4cc403db7e'})})}
]);
const MARKETS=new Set(['metaculus','manifold','kalshi','polymarket']);
const DATE=/^\d{4}-\d{2}-\d{2}$/;
const UTC=/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$/;
function instant(s){
 if(typeof s!=='string'||!UTC.test(s))throw Error('NONCANONICAL_INSTANT');
 const x=Date.parse(s);
 if(!Number.isFinite(x)||new Date(x).toISOString()!==s.replace('Z','.000Z'))throw Error('INVALID_INSTANT');
 return x;
}
function day(s){
 if(typeof s!=='string'||!DATE.test(s))return null;
 const n=Date.parse(s+'T00:00:00Z');
 return Number.isFinite(n)&&new Date(n).toISOString().slice(0,10)===s?n:null;
}
const key=x=>JSON.stringify([x.source,x.id]);
export function selectVintage(asOfInstant){
 const asOf=instant(asOfInstant);
 const candidates=SOURCE_VINTAGES.filter(v=>instant(v.at)<=asOf);
 if(!candidates.length)throw Error('NO_VERIFIED_PUBLIC_VINTAGE');
 const last=candidates[candidates.length-1];
 return Object.freeze({at:last.at,commit:last.commit,cohorts:last.cohorts,as_of_instant:asOfInstant});
}
export function planVintagePair(fromInstant,toInstant){
 if(instant(fromInstant)>=instant(toInstant))throw Error('INVALID_REPLAY_ORDER');
 const from=selectVintage(fromInstant),to=selectVintage(toInstant);
 if(from.commit===to.commit)throw Error('NO_DISTINCT_VERIFIED_SOURCE_VERSION');
 return Object.freeze({from,to,scope:'ORIGINAL_PUBLIC_GITHUB_FILE_AVAILABILITY_ONLY',
  not_per_row_first_public_at:true,personal_records:false,rights_verified_for_humans:false});
}
export function inspectPublicCohort(questionSet,resolutionSet,{cohort,as_of_instant}){
 const cut=instant(as_of_instant),due=day(cohort);
 if(due===null)throw Error('INVALID_COHORT');
 if(!questionSet||!resolutionSet||!Array.isArray(questionSet.questions)||
    !Array.isArray(resolutionSet.resolutions)||questionSet.forecast_due_date!==cohort||
    resolutionSet.forecast_due_date!==cohort||questionSet.question_set!==cohort+'-llm.json'||
    resolutionSet.question_set!==cohort+'-llm.json')throw Error('COHORT_MISMATCH');
 const outcomes=new Map(),questions=new Set();
 for(const r of resolutionSet.resolutions){
  if(!r||typeof r.source!=='string'||typeof r.id!=='string')continue;
  let k=key(r),a=outcomes.get(k);
  if(!a){a=[];outcomes.set(k,a)}a.push(r);
 }
 let invalid_source=0,invalid_freeze=0,unresolved=0,not_known_by_cutoff=0,eligible_market_questions=0,brier=0;
 const accepted=new Map(),by_source={};
 for(const q of questionSet.questions){
  if(!q||typeof q.source!=='string'||typeof q.id!=='string')throw Error('INVALID_QUESTION_ID');
  const k=key(q);
  if(questions.has(k))throw Error('DUPLICATE_QUESTION_KEY');
  questions.add(k);
  if(!MARKETS.has(q.source)){invalid_source++;continue}
  eligible_market_questions++;
  const f=Date.parse(q.freeze_datetime),p=Number(q.freeze_datetime_value);
  if(typeof q.freeze_datetime_value!=='string'||!q.freeze_datetime_value.trim()||
     !Number.isFinite(p)||p<0||p>1||!Number.isFinite(f)||f>=due+86400000){invalid_freeze++;continue}
  const rr=outcomes.get(k)||[];
  if(rr.length!==1||rr[0].resolved!==true||![0,1].includes(rr[0].resolved_to)||
     !Number.isInteger(rr[0].resolved_to)){unresolved++;continue}
  const rd=day(rr[0].resolution_date);
  if(rd===null||rd<=due){unresolved++;continue}
  if(rd>=cut){not_known_by_cutoff++;continue}
  const y=rr[0].resolved_to;
  brier+=(p-y)**2;
  accepted.set(k,y);
  by_source[q.source]=(by_source[q.source]||0)+1;
 }
 const n=accepted.size;
 return {report:Object.freeze({cohort,source_question_count:questionSet.questions.length,
  source_resolution_row_count:resolutionSet.resolutions.length,market_question_count:eligible_market_questions,
  accepted:n,invalid_source,invalid_freeze,unresolved,not_known_by_cutoff,
  brier_resolved_only:n?brier/n:null,by_source,not_full_population:true}),
  accepted};
}
export function replayOriginalPair({from,to,from_instant,to_instant}){
 const plan=planVintagePair(from_instant,to_instant);
 const common=Object.keys(plan.from.cohorts).filter(c=>Object.hasOwn(plan.to.cohorts,c));
 const results=[];
 for(const cohort of common){
  const a=from?.[cohort],z=to?.[cohort];
  if(!a||!z)throw Error('MISSING_COHORT_FOR_REPLAY');
  const x=inspectPublicCohort(a.questions,a.resolutions,{cohort,as_of_instant:from_instant});
  const y=inspectPublicCohort(z.questions,z.resolutions,{cohort,as_of_instant:to_instant});
  let retained=0,flipped=0;
  for(const [id,oldY] of x.accepted){
   if(y.accepted.has(id)){retained++;if(y.accepted.get(id)!==oldY)flipped++}
  }
  results.push({cohort,first:x.report,later:y.report,
    retained_known:retained,previously_known_no_longer_valid:x.accepted.size-retained,
    newly_known:y.accepted.size-retained,outcome_flips_among_retained:flipped,
    source_question_blob_unchanged:plan.from.cohorts[cohort].questions===plan.to.cohorts[cohort].questions});
 }
 const newCohorts=Object.keys(plan.to.cohorts).filter(c=>!Object.hasOwn(plan.from.cohorts,c));
 return {schema:'pfl.public.original.vintage.replay.v1',from_commit:plan.from.commit,to_commit:plan.to.commit,
  from_commit_at:plan.from.at,to_commit_at:plan.to.at,
  from_as_of:from_instant,to_as_of:to_instant,cohorts:results,
  newly_available_cohorts:newCohorts,unavailable_cohorts_are_not_zero_outcomes:true,
  per_record_first_public_at_verified:false,personal_rows_processed:0,
  science_causal_grade:'0/3',release_ready:false,
  provenance:'Git source commit time only; original publisher license does not permit individual data processing'};
}
