"use strict";
const assert=require('node:assert/strict');
const fs=require('node:fs');
const {audit}=new Function(fs.readFileSync(__dirname+'/forecastbench_gate.js','utf8'))();
let pass=0;
function check(n,fn){fn();pass++;process.stdout.write('PASS '+pass+': '+n+'\n');}
function question(id,source='metaculus',p='0.7',freeze='2026-09-01T00:00:00Z'){
 return {source,id,freeze_datetime_value:p,freeze_datetime:freeze};
}
function resolution(id,source='metaculus',y=1,date='2026-09-20'){
 return {id,source,resolved:true,resolved_to:y,resolution_date:date};
}
function run(q,rs,date='2026-09-13'){
 return audit({forecast_due_date:date,question_set:date+'-llm.json',questions:q},
 {forecast_due_date:date,question_set:date+'-llm.json',resolutions:rs});
}
check('realized market forecast and 0.5 comparator',()=>{let r=run([question('a')],[resolution('a')]);assert.equal(r.accepted,1);assert.ok(Math.abs(r.brier_market_mean-.09)<1e-12);assert.equal(r.brier_uninformative_mean,.25);});
check('semantic non-market raw quantity even if 0.6',()=>{let r=run([question('a','fred','0.6'),question('b','acled','12.5')],[resolution('a','fred'),resolution('b','acled')]);assert.equal(r.accepted,0);assert.equal(r.rejected.nonprobability_source,2);});
check('no outcome, unresolved and nonbinary excluded',()=>{let r=run([question('a'),question('b'),question('c')],[{...resolution('a'),resolved:false},resolution('b','metaculus',null),resolution('c','metaculus',3)]);assert.equal(r.rejected.unresolved_or_nonbinary_outcome,3);});
check('duplicate per source+id has no arbitrary last-win resolution',()=>{let r=run([question('a')],[resolution('a'),resolution('a','metaculus',0,'2026-10-20')]);assert.equal(r.accepted,0);assert.equal(r.rejected.ambiguous_multiple_resolution_records,1);});
check('source and id together distinguish separate questions',()=>{let r=run([question('a','manifold'),question('a','metaculus')],[resolution('a','manifold'),resolution('a','metaculus')]);assert.equal(r.accepted,2);});
check('do not score resolution before due date',()=>{let r=run([question('a')],[resolution('a','metaculus',1,'2026-09-12')]);assert.equal(r.rejected.time_order_or_resolution_date_not_after_due,1);});
check('do not score a post-deadline market freeze',()=>{let r=run([question('a','metaculus','0.7','2026-09-14T00:00:00Z')],[resolution('a')]);assert.equal(r.rejected.time_order_or_resolution_date_not_after_due,1);});
check('fail-closed zero/NaN/non-probability values',()=>{let r=run([question('a','metaculus',''),question('b','manifold','NaN'),question('c','kalshi','1.3')],[resolution('a'),resolution('b','manifold'),resolution('c','kalshi')]);assert.equal(r.rejected.invalid_probability_value,3);});
check('duplicated question key fails closed',()=>{let r=run([question('a'),question('a')],[resolution('a')]);assert.equal(r.accepted,0);assert.equal(r.rejected.duplicate_question_key,1);});
check('cohort mismatch fails before scoring',()=>{assert.throws(()=>audit({forecast_due_date:'2026-09-13',question_set:'2026-09-13-llm.json',questions:[]},{forecast_due_date:'2026-09-27',question_set:'2026-09-27-llm.json',resolutions:[]}),/SOURCE_COHORT_INCONSISTENT/);});
check('time unresolved not invented and zero accepted has null score',()=>{let r=run([question('a')],[]);assert.equal(r.accepted,0);assert.equal(r.brier_market_mean,null);assert.equal(r.rejected.no_resolution_record,1);});
check('no claims on PFL or causal effects and accounting identity',()=>{let r=run([question('a'),question('b','fred')],[resolution('a'),resolution('b','fred')]);assert.equal(r.accepted+r.rejected_total,r.questions);assert.equal(r.inference,'DESCRIPTIVE_RESOLVED_SUBSET_ONLY');assert.ok(r.claims.some(c=>c.includes('NOT PFL')));});
process.stdout.write('ALL '+pass+'/12 PASS\n');
