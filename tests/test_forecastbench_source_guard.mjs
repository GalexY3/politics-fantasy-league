import {auditPublicForecastQuestions} from '../src/politics_fantasy/forecastbench_source_guard.mjs';
// Offline, deterministic, no human records, no network or fixtures downloaded.
let pass=0;
const eq=(a,b)=>{if(a!==b)throw Error('EXPECTED '+JSON.stringify(b)+' GOT '+JSON.stringify(a))};
const ok=(a)=>{if(!a)throw Error('ASSERTION_FAILED')};
const throws=(f,match)=>{let msg='';try{f()}catch(e){msg=String(e.message)}if(!msg.includes(match))throw Error('EXPECTED_THROW '+match+' GOT '+msg)};
const q=(id,source='metaculus',p='0.7',freeze='2026-09-01T12:00:00+00:00')=>({id,source,freeze_datetime_value:p,freeze_datetime:freeze});
const res=(id,source='metaculus',y=1,date='2026-09-20')=>({id,source,resolved:true,resolved_to:y,resolution_date:date});
function audit(qs,rs,as_of_date='2026-10-29'){
 return auditPublicForecastQuestions(
  {forecast_due_date:'2026-09-13',question_set:'2026-09-13-llm.json',questions:qs},
  {forecast_due_date:'2026-09-13',question_set:'2026-09-13-llm.json',resolutions:rs},
  {as_of_date});
}
function test(n,f){f();pass++}
test('baseline one real-scope market scenario',()=>{const x=audit([q('a')],[res('a')]);eq(x.accepted,1);eq(x.positive,1);ok(Math.abs(x.brier_resolved_selection_only-.09)<1e-12);eq(x.release_ready,false)});
test('source units override numeric range',()=>{const x=audit([q('x','fred','0.2'),q('y','acled','0.4')],[res('x','fred'),res('y','acled')]);eq(x.accepted,0);eq(x.reasons.non_probability_quantity_source,2)});
test('temporal as-of fail closed',()=>{const x=audit([q('a')],[res('a','metaculus',0,'2026-10-11')],'2026-10-01');eq(x.reasons.resolution_not_known_by_cutoff,1)});
test('same outcome known later is retained for later cutoff',()=>{const x=audit([q('a')],[res('a','metaculus',0,'2026-10-11')],'2026-10-29');eq(x.accepted,1)});
test('no same-day outcome allowed without timestamp evidence',()=>{const x=audit([q('a')],[res('a','metaculus',1,'2026-10-29')],'2026-10-29');eq(x.reasons.resolution_not_known_by_cutoff,1)});
test('duplicate resolution fails rather than taking convenient value',()=>{const x=audit([q('a')],[res('a'),res('a','metaculus',0)]);eq(x.reasons.ambiguous_resolution,1)});
test('duplicate question row each accounted',()=>{const x=audit([q('a'),q('a')],[res('a')]);eq(x.reasons.duplicate_question_extra,1);eq(x.reasons.duplicate_question_first,1);eq(x.rejected,2)});
test('composite key protects coincident IDs across markets',()=>{const x=audit([q('a','metaculus'),q('a','manifold')],[res('a','metaculus'),res('a','manifold')]);eq(x.accepted,2)});
test('outcome unresolved cannot be assumed negative',()=>{const x=audit([q('a')],[{...res('a'),resolved:false}]);eq(x.accepted,0);eq(x.reasons.not_resolved_binary,1)});
test('no resolution means null, not zero forecast quality',()=>{const x=audit([q('a')],[]);eq(x.accepted,0);eq(x.brier_resolved_selection_only,null);eq(x.reasons.no_resolution,1)});
test('zero, empty, NaN and out of range handled without coercion',()=>{const x=audit([q('a','kalshi',''),q('b','manifold','NaN'),q('c','metaculus','-0.1'),q('d','polymarket','0')],[res('a','kalshi'),res('b','manifold'),res('c'),res('d','polymarket')]);eq(x.accepted,1);eq(x.reasons.missing_probability,1);eq(x.reasons.invalid_probability,2)});
test('no early resolution before frozen question due',()=>{const x=audit([q('a')],[res('a','metaculus',1,'2026-09-12')]);eq(x.reasons.resolution_not_after_due,1)});
test('future freeze prevented',()=>{const x=audit([q('a','metaculus','0.7','2026-09-14T00:00:00Z')],[res('a')]);eq(x.reasons.invalid_or_future_freeze,1)});
test('bad cohort/date rejected',()=>{throws(()=>audit([q('a')],[res('a')],'2026-09-13'),'INVALID_CUTOFF');throws(()=>audit([q('a')],[res('a')],'2026-09-35'),'INVALID_CUTOFF')});
test('outcomes cannot masquerade as participant effects',()=>{const x=audit([q('a')],[res('a')]);eq(x.personal_forecasts_processed,false);eq(x.source_rights_attested,false);eq(x.interpret_as,'PUBLIC_QUESTION_RESOLUTION_SUBSET_NOT_PFL_FORECAST_OR_CAUSAL_STUDY')});

test("calendar rollover freeze rejected",()=>{const x=audit([q("bad","metaculus","0.7","2026-02-30T12:00:00Z")],[res("bad")]);eq(x.accepted,0);eq(x.reasons.invalid_or_future_freeze,1)});

export const testsPassed=pass;
if(typeof process!=='undefined')process.stdout.write('PFL source as-of safety '+pass+'/'+pass+' PASS\n');
