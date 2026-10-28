import test from 'node:test';
import assert from 'node:assert/strict';
import {auditBundle,empty} from '../src/politics_fantasy/evidence_warehouse.mjs';
test('Orphan claim source and subject are reported by warehouse audit',()=>{
 const x=empty();
 x.claims.push({id:'CLAIM:bad',type:'OFFICE_STATUS',source_id:'S:missing',subject_id:'E:missing'});
 const result=auditBundle(x);
 assert.equal(result.ok,false);
 assert.deepEqual(result.broken,['CLAIM:CLAIM:bad']);
 assert.equal(result.gate.can_score_real_people,false);
});
test('Empty warehouse audit is referentially valid but NOT source-ready',()=>{
 const result=auditBundle(empty());
 assert.equal(result.ok,true);
 assert.ok(result.gate.blockers.includes('NO_ORIGINAL_RAW_CAPTURED'));
 assert.equal(result.gate.can_publish_field_people,false);
});
