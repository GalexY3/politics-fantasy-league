import test from 'node:test';
import assert from 'node:assert/strict';
import { canonicalVoteKey, indexVotes } from '../src/politics_fantasy/vote_key_research.mjs';
const row=(delta={})=>({institution:'C',legislature:'XV',session_id:'193',session_date:'2026-07-23',observation_seq:1,expediente:'130/000049',yes:2,no:1,abstain:0,total:3,...delta});
test('C02 reject ambiguous separator in identity component',()=>{
 assert.throws(()=>canonicalVoteKey(row({institution:'C|XV',legislature:'S'})),/UNSAFE_COMPONENT_DELIMITER/);
 assert.throws(()=>canonicalVoteKey(row({legislature:'XV|S'})),/UNSAFE_COMPONENT_DELIMITER/);
 assert.throws(()=>canonicalVoteKey(row({session_id:'193|194'})),/UNSAFE_COMPONENT_DELIMITER/);
});
test('C02 reject separator in expediente scope',()=>{
 assert.throws(()=>indexVotes([row({expediente:'130|000049'})]),/UNSAFE_COMPONENT_DELIMITER/);
});
test('C02 unchanged key for canonical existing inputs',()=>{
 assert.equal(canonicalVoteKey(row()),'C|XV|193|2026-07-23|1');
});
test('C02 duplicates inside same vote remain fail-closed',()=>{
 assert.throws(()=>indexVotes([row(),row()]),/DUPLICATE_VOTE_KEY/);
});
test('C02 distinct observations in one expediente remain distinct',()=>{
 const x=indexVotes([row(),row({observation_seq:2})]);
 assert.equal(x.count,2); assert.equal(x.multiVoteExpedientes.length,1);
});
