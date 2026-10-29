/**
 * PFL AB-H 30 · original public ForecastBench QUESTION-level source guard.
 * An importable local-only pure function; NOT an individual-forecaster, public-
 * politician, treatment-exposure or causal-effect evaluator.
 *
 * The input repository (Forecasting Research Institute, Karger et al. ICLR 2025)
 * is CC BY-SA 4.0; this module redistributes no text from that source.
 * The provenance of the two input files must be independently verified against
 * a pinned original Git commit. A caller-supplied "verified" boolean is never
 * accepted as evidence. Unknown or ambiguous records are rejected, not scored.
 */
const MARKET_SOURCES = new Set(['kalshi', 'manifold', 'metaculus', 'polymarket']);
const ISO_DATE = /^\d{4}-\d{2}-\d{2}$/;
const ISO_INSTANT = /^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/;
function day(v) {
 if (typeof v !== 'string' || !ISO_DATE.test(v)) return null;
 const ms=Date.parse(v+'T00:00:00Z');
 return Number.isFinite(ms) && new Date(ms).toISOString().slice(0,10)===v ? ms : null;
}
function instant(v) {
 if (typeof v!=='string'||!ISO_INSTANT.test(v)||day(v.slice(0,10))===null||Number(v.slice(11,13))>23||Number(v.slice(14,16))>59||Number(v.slice(17,19))>59)return null;
 const ms=Date.parse(v);
 return Number.isFinite(ms)?ms:null;
}
const key = obj => JSON.stringify([obj.source,obj.id]);
const bad = (name) => {throw new Error(name)};
export function auditPublicForecastQuestions(questionSet,resolutionSet,{as_of_date}={}) {
 if (!questionSet || !resolutionSet || !Array.isArray(questionSet.questions) ||
     !Array.isArray(resolutionSet.resolutions) ||
     typeof questionSet.question_set!=='string' ||
     questionSet.question_set!==resolutionSet.question_set ||
     questionSet.forecast_due_date!==resolutionSet.forecast_due_date) bad('COHORT_MISMATCH');
 const due=day(questionSet.forecast_due_date),asOf=day(as_of_date);
 if (due===null||asOf===null||asOf<=due)bad('INVALID_CUTOFF');
 const cutoff=asOf;
 const rejects=Object.create(null);
 let accepted=0,positive=0,sum=0, duplicateExtra=0;
 const sources=Object.create(null), qs=new Map(), duplicates=new Set(), rs=new Map();
 const reject=(k)=>{rejects[k]=(rejects[k]||0)+1};
 for(const q of questionSet.questions){
  if(!q||typeof q!=='object'||typeof q.source!=='string'||typeof q.id!=='string'||!q.source||!q.id){reject('invalid_question_key');continue}
  const k=key(q);
  if(qs.has(k)){duplicates.add(k);duplicateExtra++;reject('duplicate_question_extra');continue}
  qs.set(k,q);
 }
 for(const r of resolutionSet.resolutions){
  if(!r||typeof r!=='object'||typeof r.id!=='string'||typeof r.source!=='string'||!r.id||!r.source)continue;
  const k=key(r);
  let g=rs.get(k);if(!g){g=[];rs.set(k,g)}g.push(r);
 }
 for(const [k,q] of qs){
  if(duplicates.has(k)){reject('duplicate_question_first');continue}
  if(!MARKET_SOURCES.has(q.source)){reject('non_probability_quantity_source');continue}
  if(typeof q.freeze_datetime_value!=='string'||!q.freeze_datetime_value.trim()){reject('missing_probability');continue}
  const p=Number(q.freeze_datetime_value);
  if(!Number.isFinite(p)||p<0||p>1){reject('invalid_probability');continue}
  const freeze=instant(q.freeze_datetime);
  if(freeze===null||freeze>=due+86400000){reject('invalid_or_future_freeze');continue}
  const matching=rs.get(k)||[];
  if(matching.length===0){reject('no_resolution');continue}
  if(matching.length!==1){reject('ambiguous_resolution');continue}
  const observation=matching[0];
  if(observation.resolved!==true || !Number.isInteger(observation.resolved_to) ||
     (observation.resolved_to!==0&&observation.resolved_to!==1)){reject('not_resolved_binary');continue}
  const resolved=day(observation.resolution_date);
  if(resolved===null||resolved<=due){reject('resolution_not_after_due');continue}
  if(resolved>=cutoff){reject('resolution_not_known_by_cutoff');continue}
  accepted++;positive+=observation.resolved_to;
  sources[q.source]=(sources[q.source]||0)+1;
  sum+=(p-observation.resolved_to)**2;
 }
 const rejected=Object.values(rejects).reduce((a,b)=>a+b,0);
 if(accepted+rejected!==questionSet.questions.length)bad('ROW_ACCOUNTING_FAIL');
 return {
  schema:'pfl.public.forecastbench.source_guard.v1',
  cohort:questionSet.forecast_due_date,as_of_date,
  source_license:'Forecasting Research Institute CC BY-SA 4.0 (dataset; source verification required)',
  original_questions:questionSet.questions.length,
  resolution_records:resolutionSet.resolutions.length,
  accepted,rejected,positive,by_source:{...sources},reasons:{...rejects},
  brier_resolved_selection_only:accepted ? sum/accepted : null,
  interpret_as:'PUBLIC_QUESTION_RESOLUTION_SUBSET_NOT_PFL_FORECAST_OR_CAUSAL_STUDY',
  source_rights_attested:false,personal_forecasts_processed:false,release_ready:false
 };
}
