import test from 'node:test';
import assert from 'node:assert/strict';
import {eligibleAsOf} from '../src/politics_fantasy/publication_asof_research.mjs';
const date='2026-10-28T12:00:00Z';
const row=(p={})=>({captured_at:'2026-10-28T13:00:00Z', event_at:'2026-07-23T21:19:00Z', ...p});
const evidence={first_public_at:'2026-10-28T12:00:00Z', publication_evidence_url:'https://www.congreso.es/example', publication_evidence_type:'ISSUER_TIMESTAMP',verified_by:'human-reviewer'};
test('unknown first publication never inherits event or capture time',()=>{
 assert.equal(eligibleAsOf(row(), date).status,'UNKNOWN_FIRST_PUBLIC_AT');
 assert.equal(eligibleAsOf(row({first_public_at:'2026-10-28T12:00:00Z'}),date).status,'UNKNOWN_FIRST_PUBLIC_AT');
});
test('attested publication included only at or after cutoff',()=>{
 assert.equal(eligibleAsOf(row(evidence),'2026-10-28T11:59:59Z').status,'NOT_YET_PUBLIC');
 assert.equal(eligibleAsOf(row(evidence),date).status,'ELIGIBLE_ON_ATTESTED_RECORD');
});
test('incomplete attestation remains unknown',()=>{
 const {verified_by,...x}=evidence;
 assert.equal(eligibleAsOf(row(x),date).status,'UNKNOWN_FIRST_PUBLIC_AT');
});
test('reject impossible calendar and non-UTC timestamps',()=>{
 for(const t of ['2026-02-31T12:00:00Z','2026-10-28','2026-10-28T13:00:00+01:00','2026-00-01T12:00:00Z'])
  assert.throws(()=>eligibleAsOf(row(),t),/INVALID_INSTANT/);
});
test('reject contradictory capture before published time',()=>{
 assert.throws(()=>eligibleAsOf(row({...evidence,captured_at:'2026-10-28T11:00:00Z'}),date),/IMPOSSIBLE_PUBLICATION_ORDER/);
});
test('reject credential-bearing or non-https proof URL',()=>{
 for(const url of ['http://congreso.es/page','https://user:secret@www.congreso.es/page'])
  assert.throws(()=>eligibleAsOf(row({...evidence,publication_evidence_url:url}),date),/UNSAFE_EVIDENCE_URL/);
});
