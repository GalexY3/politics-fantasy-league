import test from 'node:test';
import assert from 'node:assert/strict';
import {compareElectionComposition} from '../src/politics_fantasy/parity_comparator_research.mjs';
const row=(type,category,count,more={})=>({series:type,election_id:'E1',district_id:'D1',category,count,...more});
const base=[row('candidates','F',60),row('candidates','M',40),row('elected','F',30),row('elected','M',20)];
test('paired complete strata return shares and representation gap, not election probability',()=>{
 const x=compareElectionComposition(base);
 assert.equal(x.length,1);assert.equal(x[0].denominators.candidates,100);assert.equal(x[0].denominators.elected,50);
 assert.equal(x[0].categories.find(y=>y.category==='F').composition_gap_pp,0);
 assert.equal(x[0].per_person_success_probability_computable,false);
});
test('different distribution represented without inferring identity',()=>{
 const x=compareElectionComposition([row('candidates','F',60),row('candidates','M',40),row('elected','F',20),row('elected','M',30)]);
 assert.equal(x[0].categories.find(y=>y.category==='F').composition_gap_pp,-20);
});
test('mismatched election or territory rejected',()=>{
 assert.throws(()=>compareElectionComposition([...base.slice(0,3),row('elected','M',20,{election_id:'E2'})]),/UNMATCHED_STRATUM|CATEGORY_MISMATCH/);
 assert.throws(()=>compareElectionComposition([...base.slice(0,3),row('elected','M',20,{district_id:'D2'})]),/UNMATCHED_STRATUM|CATEGORY_MISMATCH/);
});
test('missing category, unknown category asymmetry rejected, never silently discarded',()=>{
 assert.throws(()=>compareElectionComposition(base.slice(0,3)),/CATEGORY_MISMATCH/);
 assert.throws(()=>compareElectionComposition([...base,row('elected','UNKNOWN',1)]),/CATEGORY_MISMATCH/);
});
test('zero denominators and duplicate category rejected',()=>{
 assert.throws(()=>compareElectionComposition(base.map(x=>({...x,count:0}))),/ZERO_DENOMINATOR/);
 assert.throws(()=>compareElectionComposition([...base,row('candidates','F',10)]),/DUPLICATE_CATEGORY/);
});
test('bad types and impossible elected count within a stratum rejected',()=>{
 assert.throws(()=>compareElectionComposition([...base.slice(0,3),row('elected','M',-1)]),/INVALID_COUNT/);
 assert.throws(()=>compareElectionComposition([...base.slice(0,3),row('elected','M',100)]),/ELECTED_GT_CANDIDATES/);
});
test('empty/array malformed input rejected',()=>{
 assert.throws(()=>compareElectionComposition(null),/ROWS_NOT_ARRAY/);
 assert.throws(()=>compareElectionComposition([]),/NO_ROWS/);
});
