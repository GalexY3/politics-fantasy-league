import test from 'node:test';
import assert from 'node:assert/strict';
import {auditPublicRawRevision, auditPublicRawChain} from '../src/politics_fantasy/forecastbench_raw_revision_guard.mjs';
const A='a'.repeat(40), B='b'.repeat(40), C='c'.repeat(40);
const r=(id,y=1)=>({source:'metaculus',id,resolved:true,resolved_to:y});
const mk=(rows,opts={})=>({cohort:opts.cohort||'2026-09-27',
  git_blob:opts.blob||A,git_commit:opts.commit||A,
  committed_at:opts.time||'2026-10-07T07:19:29Z',
  data:{forecast_due_date:opts.cohort||'2026-09-27',
    question_set:(opts.cohort||'2026-09-27')+'-llm.json',resolutions:rows}});
const newer=(rows,opts={})=>mk(rows,{blob:B,commit:B,time:'2026-10-08T07:01:49Z',...opts});
const audit=(left,right)=>auditPublicRawRevision(mk(left),newer(right));
test('C09 genuine original-scope adversarial fixture: missing one raw row is visible',()=>{
 const x=audit([r('hidden'),r('kept')],[r('kept')]);
 assert.equal(x.removed,1);assert.equal(x.added,0);assert.equal(x.mutated,0);
 assert.equal(x.manual_review_required,true);assert.equal(x.raw_append_only_consistent,false);
});
test('raw removal is not concealed by addition of another row at constant count',()=>{
 const x=audit([r('drop')],[r('add')]);
 assert.equal(x.before_rows,x.after_rows);assert.equal(x.removed,1);assert.equal(x.added,1);
});
test('outcome flip for same composite key is a mutation, not a new event',()=>{
 const x=audit([r('x',0)],[r('x',1)]);assert.equal(x.mutated,1);assert.equal(x.added,0);
});
test('non-Y metadata correction also detected',()=>{
 const x=audit([{...r('x'),resolution_date:'2026-10-07'}],[{...r('x'),resolution_date:'2026-10-08'}]);assert.equal(x.mutated,1);
});
test('object property insertion order does not create false mutations',()=>{
 const x=audit([r('x')],[{resolved_to:1,id:'x',source:'metaculus',resolved:true}]);
 assert.equal(x.mutated,0);assert.equal(x.retained_unchanged,1);
});
test('safely isolates source plus id, rather than id alone',()=>{
 const x=audit([r('same')],[{...r('same'),source:'kalshi'}]);
 assert.equal(x.added,1);assert.equal(x.removed,1);
});
test('new event row is counted without pretending first-public-at is known',()=>{
 const x=audit([], [r('x')]);assert.equal(x.added,1);
 assert.equal(x.individual_event_first_public_at_verified,false);
 assert.equal(x.original_git_bytes_authenticated_here,false);
});
test('duplicate source id fails closed',()=>assert.throws(()=>audit([r('x'),r('x')],[r('x')]),/DUPLICATE_PUBLIC_SOURCE_KEY/));
test('bad key fails closed',()=>assert.throws(()=>audit([r('')],[r('x')]),/INVALID_PUBLIC_SOURCE_KEY/));
test('schema mismatch fails closed',()=>{const p=mk([r('x')]);p.data.question_set='wrong';assert.throws(()=>auditPublicRawRevision(p,newer([r('x')])),/PUBLIC_SOURCE_SCHEMA_MISMATCH/)});
test('cross cohort fails closed',()=>assert.throws(()=>auditPublicRawRevision(mk([]),newer([],{cohort:'2026-10-11'})),/CROSS_COHORT_COMPARISON/));
test('future-to-past / equal time prohibited',()=>assert.throws(()=>auditPublicRawRevision(mk([]),newer([],{time:'2026-10-07T07:19:29Z'})),/NONINCREASING/));
test('equal source blob prohibited even if commits differ',()=>assert.throws(()=>auditPublicRawRevision(mk([]),newer([],{blob:A})),/NO_DISTINCT_SOURCE_BLOB/));
test('invalid UTC or source hashes rejected',()=>{assert.throws(()=>auditPublicRawRevision(mk([]),newer([],{time:'2026-10-99T00:00:00Z'})),/INVALID_UTC/);assert.throws(()=>auditPublicRawRevision(mk([], {blob:'xyz'}),newer([])),/INVALID_ORIGINAL_GIT_MANIFEST/)});
test('no public question IDs or source text in output',()=>{const x=audit([r('SECRET_PUBLIC_ID_X9')],[r('SECRET_PUBLIC_ID_X9',0)]);const s=JSON.stringify(x);assert.equal(s.includes('SECRET_PUBLIC_ID_X9'),false);assert.equal(s.includes('metaculus'),false);assert.equal(x.public_row_identifiers_in_output,false)});
test('chain of three snapshots finds changes in each transition',()=>{const x=auditPublicRawChain([mk([r('a')]),newer([r('b')]),newer([r('b',0),r('c')],{blob:C,commit:C,time:'2026-10-09T07:01:29Z'})]);assert.equal(x.revisions.length,2);assert.equal(x.total_removed,1);assert.equal(x.total_mutated,1);assert.equal(x.no_raw_append_only_assumption,true)});
test('chain refuses fewer than two snapshots',()=>assert.throws(()=>auditPublicRawChain([mk([])]),/TWO_OR_MORE_PUBLIC_VERSIONS_REQUIRED/));
test('malicious special property in source record is not permitted',()=>{const x=JSON.parse('{"source":"metaculus","id":"a","__proto__":{"polluted":true}}');assert.throws(()=>audit([x],[r('a')]),/UNSAFE_PUBLIC_RECORD_FIELD/)});
test('no personal source semantics are claimed by results',()=>{const x=audit([],[r('a')]);assert.equal(x.source_personal_rows_processed,false);assert.equal(x.science_grade,'0/3');assert.equal(x.launch_ready,false)});
