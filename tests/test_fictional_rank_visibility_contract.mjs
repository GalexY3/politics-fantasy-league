import test from 'node:test';
import assert from 'node:assert/strict';
import {auditFictionalRankVisibilityContract} from '../src/politics_fantasy/fictional_rank_visibility_contract.mjs';
const frame='a'.repeat(64),schedule='b'.repeat(64);
const arm=(feedback,audience,alias_mode)=>({feedback,audience,alias_mode,reward:'VIRTUAL_SAME_BRIER',event_frame:frame,schedule,show_own_score:true});
const specimen=()=>({fixture:'SYNTHETIC_RANK_DESIGN_ONLY',arms:{
 own_only:arm('own_only','self','none'),
 private_quartile:arm('rank_quartile','self','none'),
 public_quartile:arm('rank_quartile','room','fictional_alias'),
 private_order:arm('rank_full_order','self','none'),
 public_order:arm('rank_full_order','room','fictional_alias')}});
const edit=(name,field,value)=>{const p=specimen();p.arms[name][field]=value;return p};
const err=(x,code)=>assert.throws(()=>auditFictionalRankVisibilityContract(x),new RegExp(code));

test('five valid synthetic arms and four factorial cells produce planned contrasts',()=>{const x=auditFictionalRankVisibilityContract(specimen());assert.equal(x.planned_arms,5);assert.equal(x.factorial_cells.length,4);assert.equal(x.planned_contrasts.publicness_at_quartile.negative,'private_quartile');assert.equal(x.planned_contrasts.interaction.positive.length,2)});
test('never treats contract parity as delivered exposure',()=>{const x=auditFictionalRankVisibilityContract(specimen());assert.equal(x.independent_display_receipts_verified,false);assert.equal(x.human_allocation_verified,false);assert.equal(x.outcome_effect_estimated,false);assert.equal(x.release_ready,false)});
test('public full-order vs private quartile is a bundled contrast, not main publicness effect',()=>{const x=auditFictionalRankVisibilityContract(specimen());assert.equal(x.planned_contrasts.publicness_at_full_order.negative,'private_order');assert.equal(x.planned_contrasts.detail_at_private.negative,'private_quartile')});
test('public quartile cannot silently become full ordered leaderboard',()=>err(edit('public_quartile','feedback','rank_full_order'),'TREATMENT_ISOLATION_BROKEN'));
test('private full order cannot silently become a room display',()=>err(edit('private_order','audience','room'),'TREATMENT_ISOLATION_BROKEN'));
test('public room feedback cannot remove fictional aliases',()=>err(edit('public_order','alias_mode','none'),'TREATMENT_ISOLATION_BROKEN'));
test('cannot send real participant identities',()=>err(edit('public_order','alias_mode','real_name'),'TREATMENT_ISOLATION_BROKEN'));
test('all arms retain own score',()=>err(edit('own_only','show_own_score',false),'TREATMENT_ISOLATION_BROKEN'));
test('virtual scoring rule cannot drift to real monetary incentives',()=>err(edit('public_quartile','reward','MONEY'),'NONCOMPARABLE_COMMON_PROTOCOL'));
test('same game events required across arms',()=>err(edit('private_order','event_frame','c'.repeat(64)),'PROTOCOL_PARITY_VIOLATION'));
test('common schedule must not vary by arm',()=>err(edit('public_order','schedule','d'.repeat(64)),'PROTOCOL_PARITY_VIOLATION'));
test('malformed event hash rejected',()=>err(edit('private_quartile','event_frame','a'),'NONCOMPARABLE_COMMON_PROTOCOL'));
test('extra participant rows never accepted',()=>err({...specimen(),rows:[]},'FICTIONAL_FIVE_CELL_CONTRACT_REQUIRED'));
test('missing control invalidates the entire contract',()=>{const p=specimen();delete p.arms.own_only;err(p,'FICTIONAL_FIVE_CELL_CONTRACT_REQUIRED')});
test('cannot add unsupported sixth treatment',()=>{const p=specimen();p.arms.extra=arm('own_only','self','none');err(p,'FICTIONAL_FIVE_CELL_CONTRACT_REQUIRED')});
test('rejects inherited prototype input',()=>err(Object.assign(Object.create({real:true}),specimen()),'FICTIONAL_FIVE_CELL_CONTRACT_REQUIRED'));
test('rejects unexpected per-arm exposure claims',()=>{const p=specimen();p.arms.public_order.real_display_verified=true;err(p,'INVALID_TREATMENT_SHAPE')});
test('rejects malicious symbol property',()=>{const p=specimen();p.arms.own_only[Symbol('secret')]=1;err(p,'INVALID_TREATMENT_SHAPE')});
