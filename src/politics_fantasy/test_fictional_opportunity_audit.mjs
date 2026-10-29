import assert from 'node:assert/strict';
import {auditFictionalOpportunities} from './fictional_opportunity_audit.mjs';
const t=(day)=>`2026-01-${String(day).padStart(2,'0')}T00:00:00Z`;
const arms=['control','transparency','leaderboard','both'];
const make=()=>({
 study_fixture:'SYNTHETIC_OFFLINE_ONLY',roster_complete:true,
 roster:arms.flatMap((arm,i)=>[{participant_id:`P${2*i}`,arm,registered_at:t(1)},{participant_id:`P${2*i+1}`,arm,registered_at:t(6)}]),
 questions:[{question_id:'Q1',opened_at:t(2),closed_at:t(5)},{question_id:'Q2',opened_at:t(5),closed_at:t(9)}],
 first_answers:[{participant_id:'P0',question_id:'Q1',submitted_at:t(3)},{participant_id:'P1',question_id:'Q2',submitted_at:t(7)},{participant_id:'P4',question_id:'Q1',submitted_at:t(3)},{participant_id:'P6',question_id:'Q2',submitted_at:t(6)}],
 impressions:[{participant_id:'P0',question_id:'Q1',observed_at:t(2),provenance:'INDEPENDENT_SYNTHETIC_DISPLAY_EVENT'},
 {participant_id:'P4',question_id:'Q1',observed_at:t(4),provenance:'INDEPENDENT_SYNTHETIC_DISPLAY_EVENT'},
 {participant_id:'P2',question_id:'Q2',observed_at:t(6),provenance:'INDEPENDENT_SYNTHETIC_DISPLAY_EVENT'}]
});
let pass=0;
const test=(name,fn)=>{fn();pass++;console.log('PASS',name)};
const rejects=(mutate,code)=>{const x=make();mutate(x);assert.throws(()=>auditFictionalOpportunities(x),new RegExp(code))};
test('full roster includes people with no response and late registrants',()=>{
 const s=auditFictionalOpportunities(make());
 assert.equal(s.opportunities,12);assert.equal(s.first_responses,4);assert.equal(s.uptake_per_eligible,1/3);
 assert.equal(s.cells.control.assigned,2);assert.equal(s.cells.control.eligible_opportunities,3);
 assert.equal(s.cells.control.first_responses,2);assert.equal(s.cells.transparency.first_responses,0);
});
test('pre-response vs post-response and unknown display are distinct',()=>{
 const s=auditFictionalOpportunities(make());
 assert.equal(s.cells.control.pre_response_displays,1);
 assert.equal(s.cells.leaderboard.post_response_only_displays,1);
 assert.equal(s.cells.transparency.display_without_response,1);
 assert.equal(s.cells.transparency.unknown_display_opportunities,2);
 assert.equal(s.display_absence_meaning,'UNKNOWN_NOT_UNSEEN');
});
test('order invariant and deterministic',()=>{
 const x=make(),a=auditFictionalOpportunities(x);
 x.roster.reverse();x.first_answers.reverse();x.impressions.reverse();x.questions.reverse();
 assert.deepEqual(auditFictionalOpportunities(x).cells,a.cells);
});
test('reject missing roster/guarded fixture',()=>{
 rejects(x=>{x.roster_complete=false},'SYNTHETIC_FULL_ROSTER_REQUIRED');
 rejects(x=>{x.study_fixture='REAL_USERS'},'SYNTHETIC_FULL_ROSTER_REQUIRED');
});
test('reject duplicates and invalid time',()=>{
 rejects(x=>{x.roster.push({...x.roster[0]})},'DUPLICATE_PARTICIPANT');
 rejects(x=>{x.questions[0].closed_at=x.questions[0].opened_at},'INVALID_WINDOW');
 rejects(x=>{x.questions[0].opened_at='2026-02-30T00:00:00Z'},'INVALID_UTC_TIME');
});
test('reject fabricated exposure from response or unknown provenance',()=>{
 rejects(x=>{x.impressions[0].provenance='FORECAST_EXISTS'},'UNVERIFIED_DISPLAY_SEMANTICS');
 rejects(x=>{x.impressions[0].observed_at=t(1)},'DISPLAY_OUTSIDE_WINDOW');
});
test('reject answer without eligibility and duplicate first forecast',()=>{
 rejects(x=>{x.first_answers[0].submitted_at=t(5)},'FIRST_ANSWER_OUTSIDE_WINDOW');
 rejects(x=>{x.first_answers.push({...x.first_answers[0]})},'DUPLICATE_FIRST_ANSWER');
 rejects(x=>{x.first_answers.push({participant_id:'P1',question_id:'Q1',submitted_at:t(3)})},'NOT_ELIGIBLE');
});
test('guard prototype getters and nested extra fields',()=>{
 rejects(x=>{x.roster[0].email='hidden'},'INVALID_ROSTER');
 rejects(x=>{Object.defineProperty(x.first_answers[0],'submitted_at',{get:()=>t(3),enumerable:true})},'INVALID_FIRST_ANSWER');
});
test('timestamp tie cannot attest pre-response display order',()=>{
 const x=make();x.impressions[0].observed_at=t(3);
 const s=auditFictionalOpportunities(x);
 assert.equal(s.cells.control.timestamp_tied_displays,1);
 assert.equal(s.cells.control.pre_response_displays,0);
});
console.log(JSON.stringify({schema:'pfl.synthetic.opportunity.tests.v2',pass,total:9,context:'SYNTHETIC_ONLY_NO_PEOPLE'}));
