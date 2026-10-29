/**
 * Partial identification for four-cell FICTIONAL-only PFL pilot aggregates.
 * No source authentication, no people, no political events, no randomization claim.
 * Bounds require only each unobserved normalized outcome is in [0,1].
 */
const ARMS=Object.freeze(['control','transparency','leaderboard','both']);
const COEFF=Object.freeze({
 transparency:Object.freeze({control:-0.5,transparency:0.5,leaderboard:-0.5,both:0.5}),
 leaderboard:Object.freeze({control:-0.5,transparency:-0.5,leaderboard:0.5,both:0.5}),
 interaction:Object.freeze({control:1,transparency:-1,leaderboard:-1,both:1})
});
function exact(o,keys){
 if(!o||typeof o!=='object'||Array.isArray(o))return false;
 const proto=Object.getPrototypeOf(o);
 if(proto!==Object.prototype&&proto!==null)return false;
 const own=Reflect.ownKeys(o);
 return own.length===keys.length&&keys.every(k=>Object.hasOwn(o,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(o,k),'value'));
}
function bad(code){throw Error(code)}
function oneCell(o){
 if(!exact(o,['assigned','observed','observed_score_sum']))bad('INVALID_CELL_SHAPE');
 const {assigned,observed,observed_score_sum:sum}=o;
 if(!Number.isSafeInteger(assigned)||assigned<1||assigned>1_000_000||
    !Number.isSafeInteger(observed)||observed<0||observed>assigned||
    typeof sum!=='number'||!Number.isFinite(sum)||sum<0||sum>observed||
    (observed===0&&sum!==0))bad('INVALID_BOUNDED_COUNTS');
 const missing=assigned-observed;
 return Object.freeze({assigned,observed,missing,complete_case_mean:observed?sum/observed:null,
  lower:sum/assigned,upper:(sum+missing)/assigned});
}
function contrast(cells,weights){
 let lo=0,hi=0,cc=0,allCC=true;
 for(const arm of ARMS){
  const w=weights[arm],s=cells[arm];
  lo+=w*(w>=0?s.lower:s.upper);
  hi+=w*(w>=0?s.upper:s.lower);
  if(s.complete_case_mean===null)allCC=false;
  else cc+=w*s.complete_case_mean;
 }
 return Object.freeze({lower:lo,upper:hi,complete_case_descriptive:allCC?cc:null,
  sign_identified:lo>0?'POSITIVE':hi<0?'NEGATIVE':'NOT_IDENTIFIED'});
}
export function boundFictionalPilot(payload){
 if(!exact(payload,['study_fixture','arms'])||payload.study_fixture!=='FICTIONAL_AGGREGATES_ONLY'||
    !exact(payload.arms,ARMS))bad('FICTIONAL_AGGREGATES_REQUIRED');
 const cells=Object.freeze(Object.fromEntries(ARMS.map(a=>[a,oneCell(payload.arms[a])])));
 const effects=Object.freeze(Object.fromEntries(Object.entries(COEFF).map(([k,v])=>[k,contrast(cells,v)])));
 const missing_total=ARMS.reduce((s,a)=>s+cells[a].missing,0);
 const assigned_total=ARMS.reduce((s,a)=>s+cells[a].assigned,0);
 return Object.freeze({schema:'pfl.fictional.missingness.manski.bounds.v1',
  source:'FICTIONAL_AGGREGATES_ONLY',assumption:'EACH_UNOBSERVED_NORMALIZED_OUTCOME_IN_CLOSED_INTERVAL_0_1',
  cells,effects,assigned_total,missing_total,
  sharp_given_only_armwise_bounded_outcomes:true,
  conditional_on_valid_allocation_and_no_interference:false,
  actual_randomization_authenticated:false,actual_exposure_authenticated:false,
  human_rows_processed:false,causal_effect_claim:false,research_originality_grade:'0/3',
  release_ready:false,
  warning:missing_total?'COMPLETE_CASE_MAY_MISLEAD;_BOUNDS_NOT_POINT_IDENTIFIED':'FULLY_OBSERVED_SYNTHETIC_ONLY'});
}
