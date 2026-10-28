import test from 'node:test';
import assert from 'node:assert/strict';
import {empty,source} from '../src/politics_fantasy/evidence_warehouse.mjs';
const form=url=>({id:'TEST:source',kind:'OFFICIAL',state:'TEST_FIXTURE',url,
 observed_at:'2026-10-28T00:00:00Z',first_public_at:null,rights:'UNKNOWN'});
test('source URL with embedded credentials is rejected even if HTTPS',()=>{
 assert.throws(()=>source(empty(),form('https://user:password@fixture.invalid/manifest')),/SOURCE_URL/);
});
test('plain HTTPS fixture remains syntactically permitted, not authenticated',()=>{
 const s=source(empty(),form('https://fixture.invalid/manifest'));
 assert.equal(s.kind,'OFFICIAL');
 assert.equal(s.state,'TEST_FIXTURE');
});
test('plain HTTP and escaped source authority rejected',()=>{
 assert.throws(()=>source(empty(),form('http://fixture.invalid/manifest')),/SOURCE_URL/);
 assert.throws(()=>source(empty(),form('https://fixture%2Einvalid/manifest')),/SOURCE_URL/);
});
