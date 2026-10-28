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
test('C03 reject impossible and non-Gregorian calendar days',()=>{
 for (const day of ['2026-02-31','2025-02-29','2026-13-10','2024-04-31','1900-02-29','0000-01-01'])
   assert.throws(()=>canonicalVoteKey(row({session_date:day})),/INVALID_SESSION_DATE|DATE_NOT_ISO/);
});
test('C03 allow real leap day without timezone reinterpretation',()=>{
 assert.equal(canonicalVoteKey(row({session_date:'2024-02-29'})),'C|XV|193|2024-02-29|1');
 assert.equal(canonicalVoteKey(row({session_date:'2000-02-29'})),'C|XV|193|2000-02-29|1');
});
test('C04 reject object-to-string alias and numeric legislature',()=>{
 assert.throws(()=>canonicalVoteKey(row({institution:{toString(){return 'C'}}})),/INVALID_COMPONENT_TYPE/);
 assert.throws(()=>canonicalVoteKey(row({legislature:15})),/INVALID_COMPONENT_TYPE/);
});
test('C04 reject untyped expediente and padded text',()=>{
 assert.throws(()=>indexVotes([row({expediente:130})]),/INVALID_COMPONENT_TYPE/);
 assert.throws(()=>indexVotes([row({expediente:'130/000049 '})]),/INVALID_COMPONENT_WHITESPACE/);
});
test('C04 reject null/array input in controlled form',()=>{
 assert.throws(()=>canonicalVoteKey(null),/INVALID_ROW/);
 assert.throws(()=>canonicalVoteKey([]),/INVALID_ROW/);
});
