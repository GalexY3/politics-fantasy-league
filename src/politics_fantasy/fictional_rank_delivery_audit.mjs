/** ABH30-C15: an offline synthetic receipt consistency checker, NOT receipt attestation. */
import {auditFictionalRankVisibilityContract} from './fictional_rank_visibility_contract.mjs';
const ARMS=['own_only','private_quartile','public_quartile','private_order','public_order'];
const ID=/^[A-Za-z0-9_-]{1,24}$/;
const FEEDBACK={own_only:'own_only',private_quartile:'rank_quartile',public_quartile:'rank_quartile',private_order:'rank_full_order',public_order:'rank_full_order'};
const AUDIENCE={own_only:'self',private_quartile:'self',public_quartile:'room',private_order:'self',public_order:'room'};
const fail=x=>{throw Error(x)};
function exact(x,keys){
 if(!x||typeof x!=='object'||Array.isArray(x))return false;
 const p=Object.getPrototypeOf(x);
 if(p!==Object.prototype&&p!==null)return false;
 const k=Reflect.ownKeys(x);
 return k.length===keys.length&&keys.every(n=>Object.hasOwn(x,n)&&Object.hasOwn(Object.getOwnPropertyDescriptor(x,n),'value'));
}
function id(s){return typeof s==='string'&&ID.test(s)}
function utc(s){
 if(typeof s!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s))fail('NONCANONICAL_UTC');
 const t=Date.parse(s);
 if(!Number.isFinite(t)||new Date(t).toISOString()!==s.replace('Z','.000Z'))fail('NONCANONICAL_UTC');
 return t;
}
export function auditFictionalRankDelivery(input){
 if(!exact(input,['fixture','contract','assignments','opportunities','receipts'])||
    input.fixture!=='SYNTHETIC_DELIVERY_ONLY'||!Array.isArray(input.assignments)||
    !Array.isArray(input.opportunities)||!Array.isArray(input.receipts))fail('SYNTHETIC_DELIVERY_FRAME_ONLY');
 auditFictionalRankVisibilityContract(input.contract);
 const assigned=new Map(),rooms=new Map(),opp=new Map(),receiptIds=new Set(),seenOpp=new Set();
 const counts=Object.fromEntries(ARMS.map(a=>[a,{assigned:0,opportunities:0,observed_receipts:0}]));
 for(const a of input.assignments){
  if(!exact(a,['member_id','room_id','arm'])||!id(a.member_id)||!id(a.room_id)||!ARMS.includes(a.arm))fail('INVALID_SYNTHETIC_ASSIGNMENT');
  if(assigned.has(a.member_id))fail('DUPLICATE_SYNTHETIC_MEMBER');
  if(rooms.has(a.room_id)&&rooms.get(a.room_id)!==a.arm)fail('ROOM_ARM_CONTAMINATION');
  rooms.set(a.room_id,a.arm);assigned.set(a.member_id,a);counts[a.arm].assigned++;
 }
 if(!assigned.size)fail('EMPTY_SYNTHETIC_ASSIGNMENTS');
 for(const o of input.opportunities){
  if(!exact(o,['opportunity_id','member_id','room_id','opens_at','closes_at'])||
     !id(o.opportunity_id)||!id(o.member_id)||!id(o.room_id))fail('INVALID_SYNTHETIC_OPPORTUNITY');
  if(opp.has(o.opportunity_id))fail('DUPLICATE_OPPORTUNITY');
  const a=assigned.get(o.member_id);
  if(!a||a.room_id!==o.room_id)fail('OPPORTUNITY_NOT_IN_ASSIGNED_ROOM');
  const opens=utc(o.opens_at),closes=utc(o.closes_at);
  if(opens>=closes)fail('INVALID_OPPORTUNITY_WINDOW');
  opp.set(o.opportunity_id,{...o,opens,closes,arm:a.arm});counts[a.arm].opportunities++;
 }
 if(!opp.size)fail('EMPTY_OPPORTUNITY_FRAME');
 for(const r of input.receipts){
  if(!exact(r,['receipt_id','opportunity_id','member_id','room_id','arm','shown_at','feedback','audience','source'])||
     !id(r.receipt_id)||!id(r.opportunity_id)||!id(r.member_id)||!id(r.room_id)||
     r.source!=='INDEPENDENT_SYNTHETIC_RENDER_LOG')fail('UNATTESTED_OR_INVALID_SYNTHETIC_RECEIPT');
  if(receiptIds.has(r.receipt_id))fail('DUPLICATE_RECEIPT');receiptIds.add(r.receipt_id);
  if(seenOpp.has(r.opportunity_id))fail('MULTIPLE_RENDER_FOR_SAME_OPPORTUNITY');
  const o=opp.get(r.opportunity_id);
  if(!o||o.member_id!==r.member_id||o.room_id!==r.room_id||o.arm!==r.arm)fail('RECEIPT_ASSIGNMENT_OR_RISK_SET_MISMATCH');
  const t=utc(r.shown_at);
  if(!(o.opens<=t&&t<o.closes))fail('RECEIPT_OUTSIDE_OPPORTUNITY_WINDOW');
  if(r.feedback!==FEEDBACK[r.arm]||r.audience!==AUDIENCE[r.arm])fail('ACTUAL_RENDER_DIVERGES_FROM_ARM');
  counts[r.arm].observed_receipts++;seenOpp.add(r.opportunity_id);
 }
 const aggregate=Object.fromEntries(ARMS.map(a=>[a,Object.freeze({...counts[a],unobserved_opportunities:counts[a].opportunities-counts[a].observed_receipts})]));
 return Object.freeze({schema:'pfl.synthetic.rank_delivery_audit.v1',scope:'SYNTHETIC_OFFLINE_ONLY',by_arm:Object.freeze(aggregate),
  observed_receipts:receiptIds.size,registered_opportunities:opp.size,
  unobserved_opportunities:'UNKNOWN_EXPOSURE_NOT_ZERO',
  single_render_per_opportunity_enforced:true,configured_treatment_matches_synthetic_receipts:true,
  real_receipt_authentication:false,human_allocation_authenticated:false,real_renderer_integrated:false,
  room_interference_excluded:false,causal_effect_estimated:false,personal_rows_processed:false,release_ready:false,
  scientific_grade:'0/3'});
}
