/** An executable, strictly fictional view renderer. No DOM, human data or real signed receipts. */
import {auditFictionalRankDelivery} from './fictional_rank_delivery_audit.mjs';
const fail=x=>{throw Error(x)};
const exact=(o,ks)=>o&&typeof o==='object'&&!Array.isArray(o)&&(Object.getPrototypeOf(o)===Object.prototype||Object.getPrototypeOf(o)===null)&&Reflect.ownKeys(o).length===ks.length&&ks.every(k=>Object.hasOwn(o,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(o,k),'value'));
export function renderFictionalRankSession(input){
 if(!exact(input,['fixture','contract','assignments','opportunities','scores'])||input.fixture!=='SYNTHETIC_RENDER_SESSION_ONLY'||!Array.isArray(input.scores))fail('SYNTHETIC_RENDER_ONLY');
 const base={fixture:'SYNTHETIC_DELIVERY_ONLY',contract:input.contract,assignments:input.assignments,opportunities:input.opportunities,receipts:[]};
 auditFictionalRankDelivery(base);
 const members=new Map(input.assignments.map(a=>[a.member_id,a]));
 const scores=new Map();
 for(const s of input.scores){if(!exact(s,['member_id','score'])||typeof s.member_id!=='string'||!members.has(s.member_id)||scores.has(s.member_id)||typeof s.score!=='number'||!Number.isFinite(s.score)||s.score<0||s.score>1)fail('INVALID_SYNTHETIC_SCORE');scores.set(s.member_id,s.score)}
 if(scores.size!==members.size)fail('INCOMPLETE_SYNTHETIC_SCORE_FRAME');
 const ordered=new Map();for(const member of input.assignments){const room=member.room_id;if(!ordered.has(room))ordered.set(room,[]);ordered.get(room).push(member.member_id)}
 for(const [room,ids] of ordered){ids.sort((a,b)=>scores.get(b)-scores.get(a)||a.localeCompare(b));}
 const views=[],receipts=[];
 for(const [i,o] of input.opportunities.entries()){
  const m=members.get(o.member_id),ids=ordered.get(m.room_id),own=scores.get(o.member_id);
  const ahead=ids.filter(id=>scores.get(id)>own).length,rank=ahead+1,quartile=Math.min(4,Math.floor(4*ahead/ids.length)+1);
  let shown={own_score:own};
  if(m.arm.includes('quartile'))shown={...shown,own_quartile:quartile};
  if(m.arm.includes('order'))shown={...shown,own_rank:rank,room_size:ids.length};
  if(m.arm==='public_quartile')shown={...shown,room_quartiles:ids.map(id=>({alias:id,quartile:Math.min(4,Math.floor(4*ids.filter(t=>scores.get(t)>scores.get(id)).length/ids.length)+1)}))};
  if(m.arm==='public_order')shown={...shown,room_order:ids.map((id,i)=>({alias:id,rank:ids.filter(x=>scores.get(x)>scores.get(id)).length+1}))};
  views.push({opportunity_id:o.opportunity_id,arm:m.arm,shown});
  const policy=input.contract.arms[m.arm];
  receipts.push({receipt_id:'generated'+i,opportunity_id:o.opportunity_id,member_id:m.member_id,room_id:m.room_id,arm:m.arm,shown_at:o.opens_at,feedback:policy.feedback,audience:policy.audience,source:'INDEPENDENT_SYNTHETIC_RENDER_LOG'});
 }
 const audit=auditFictionalRankDelivery({...base,receipts});
 return Object.freeze({schema:'pfl.synthetic.rank_session_renderer.v1',views,receipt_audit:audit,generated_from_executed_function:true,real_browser_presentation:false,real_renderer_attested:false,causal_claim:false,privacy_cleared:false});
}
