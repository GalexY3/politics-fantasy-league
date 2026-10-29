/** Offline cryptographic synthetic receipt signing; NOT a deployed renderer trust root. */
import {createHmac, timingSafeEqual} from 'node:crypto';
const arms=['own_only','private_quartile','public_quartile','private_order','public_order'];
const id=/^[A-Za-z0-9_-]{1,24}$/;
const fields=['receipt_id','opportunity_id','room_id','arm','shown_at','feedback','audience'];
const exact=(x,ks)=>x&&typeof x==='object'&&!Array.isArray(x)&&(Object.getPrototypeOf(x)===Object.prototype||Object.getPrototypeOf(x)===null)&&Reflect.ownKeys(x).length===ks.length&&ks.every(k=>Object.hasOwn(x,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(x,k),'value'));
function valid(o){if(!exact(o,fields)||![o.receipt_id,o.opportunity_id,o.room_id].every(v=>typeof v==='string'&&id.test(v))||!arms.includes(o.arm)||typeof o.feedback!=='string'||typeof o.audience!=='string'||typeof o.shown_at!=='string'||!/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(o.shown_at)||!Number.isFinite(Date.parse(o.shown_at)))throw Error('INVALID_RECEIPT_SCHEMA')}
const signerKey=k=>{if(!Buffer.isBuffer(k)||k.length!==32)throw Error('KEY_MUST_BE_32_BYTES')};
function serial(r){return fields.map(k=>JSON.stringify(r[k])).join('|')}
export function signSyntheticReceipt(receipt,key){valid(receipt);signerKey(key);return Object.freeze({receipt:{...receipt},mac:createHmac('sha256',key).update(serial(receipt),'utf8').digest('hex')})}
export function verifySyntheticReceipt(envelope,key){signerKey(key);if(!exact(envelope,['receipt','mac'])||typeof envelope.mac!=='string'||!/^[a-f0-9]{64}$/.test(envelope.mac))throw Error('INVALID_ENVELOPE');valid(envelope.receipt);const expect=createHmac('sha256',key).update(serial(envelope.receipt),'utf8').digest();return timingSafeEqual(expect,Buffer.from(envelope.mac,'hex'))}
export function auditSyntheticReceiptChain(envelopes,key){signerKey(key);if(!Array.isArray(envelopes)||!envelopes.length)throw Error('EMPTY_SIGNED_RECEIPTS');const ids=new Set(),ops=new Set();for(const e of envelopes){if(!verifySyntheticReceipt(e,key))throw Error('BAD_SIGNATURE');if(ids.has(e.receipt.receipt_id)||ops.has(e.receipt.opportunity_id))throw Error('REPLAYED_RECEIPT');ids.add(e.receipt.receipt_id);ops.add(e.receipt.opportunity_id)}return Object.freeze({synthetic_verified:ids.size,cryptographic_integrity:true,deployed_renderer_key_attestation:false,actual_human_view:false,no_causal_effect:true})}
