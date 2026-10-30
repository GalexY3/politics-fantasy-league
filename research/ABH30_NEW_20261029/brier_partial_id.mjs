/**
 * Partial identification (no imputation) of mean Brier over a public question
 * cohort with unresolved binary outcomes, given frozen external market p.
 * Original ForecastBench public CC BY-SA event-question rows only.
 * NOT a user's PFL forecast, not human or ranking causal evidence.
 */
const MARKET=new Set(['kalshi','manifold','metaculus','polymarket']);
function day(s){if(typeof s!=='string'||!/^\d{4}-\d{2}-\d{2}$/.test(s))return null;const v=Date.parse(s+'T00:00:00Z');return Number.isFinite(v)&&new Date(v).toISOString().slice(0,10)===s?v:null;}
function stamp(s){return typeof s==='string'&&/^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(?:\.\d+)?(?:Z|[+-]\d{2}:\d{2})$/.test(s)?Date.parse(s):NaN;}
function key(r){return JSON.stringify([r.source,r.id])}
export function boundMarketBrier(qset,rset,{as_of_date}={}){
 if(!qset||!rset||!Array.isArray(qset.questions)||!Array.isArray(rset.resolutions)
    ||qset.forecast_due_date!==rset.forecast_due_date||qset.question_set!==rset.question_set)
   throw Error('COHORT_MISMATCH');
 const due=day(qset.forecast_due_date),cutoff=day(as_of_date);
 if(due===null||cutoff===null||cutoff<=due)throw Error('INVALID_AS_OF_DATE');
 const resolutions=new Map();
 for(const r of rset.resolutions){
  if(!r||typeof r.id!=='string'||typeof r.source!=='string')continue;
  const k=key(r);const a=resolutions.get(k)||[];a.push(r);resolutions.set(k,a);
 }
 const seen=new Set(),out={schema:'pfl.abh30.market.brier.partial_identification.v1',
  cohort:qset.forecast_due_date,as_of_date,all_questions:qset.questions.length,
  market_questions:0,eligible_probability_questions:0,invalid_probability_or_time:0,
  known_outcomes:0,unknown_outcomes:0,known_brier_sum:0,lower_bound_sum:0,upper_bound_sum:0,
  known_brier_mean:null,full_cohort_brier_lower:null,full_cohort_brier_upper:null,
  weak_0_5_brier_reference:0.25,notes:['Bounds are worst-case over missing y in {0,1} for each usable frozen-market probability','No assumption that missingness is random','Weak p=.5 arithmetic reference is not a competent forecasting comparator','Market-source not event-level authorization, no participant data']};
 for(const q of qset.questions){
  if(!q||typeof q.id!=='string'||typeof q.source!=='string')throw Error('MALFORMED_SOURCE_KEY');
  const k=key(q);if(seen.has(k))throw Error('DUPLICATE_QUESTION_KEY');seen.add(k);
  if(!MARKET.has(q.source))continue;
  out.market_questions++;
  if(typeof q.freeze_datetime_value!=='string'||!q.freeze_datetime_value.trim()){out.invalid_probability_or_time++;continue}
  const p=Number(q.freeze_datetime_value),frozen=stamp(q.freeze_datetime);
  if(!Number.isFinite(p)||p<0||p>1||!Number.isFinite(frozen)||frozen>=due+86400000){
    out.invalid_probability_or_time++;continue
  }
  out.eligible_probability_questions++;
  const matches=resolutions.get(k)||[];
  const y=matches.length===1?matches[0]:null;
  const rday=y?day(y.resolution_date):null;
  const known=y&&y.resolved===true&&Number.isInteger(y.resolved_to)
    &&[0,1].includes(y.resolved_to)&&rday!==null&&rday>due&&rday<cutoff;
  if(known){
   const loss=(p-y.resolved_to)**2;
   out.known_outcomes++;out.known_brier_sum+=loss;
   out.lower_bound_sum+=loss;out.upper_bound_sum+=loss;
  }else{
   out.unknown_outcomes++;
   const los0=p*p,los1=(1-p)*(1-p);
   out.lower_bound_sum+=Math.min(los0,los1);
   out.upper_bound_sum+=Math.max(los0,los1);
  }
 }
 const n=out.eligible_probability_questions;
 if(out.known_outcomes+out.unknown_outcomes!==n)throw Error('COUNT_MISMATCH');
 out.known_brier_mean=out.known_outcomes?out.known_brier_sum/out.known_outcomes:null;
 out.full_cohort_brier_lower=n?out.lower_bound_sum/n:null;
 out.full_cohort_brier_upper=n?out.upper_bound_sum/n:null;
 return out;
}
