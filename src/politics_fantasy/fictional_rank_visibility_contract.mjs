/** PFL ABH30-C14: fictional factorial rank-feedback protocol, design validity only. */
const ARMS=Object.freeze(['own_only','private_quartile','public_quartile','private_order','public_order']);
const SPEC=Object.freeze({
 own_only:['own_only','self','none'],
 private_quartile:['rank_quartile','self','none'],
 public_quartile:['rank_quartile','room','fictional_alias'],
 private_order:['rank_full_order','self','none'],
 public_order:['rank_full_order','room','fictional_alias']
});
const KEYS=['feedback','audience','alias_mode','reward','event_frame','schedule','show_own_score'];
const HEX=/^[a-f0-9]{64}$/;
function exact(x,keys){
 if(!x||typeof x!=='object'||Array.isArray(x))return false;
 const proto=Object.getPrototypeOf(x);
 if(proto!==Object.prototype&&proto!==null)return false;
 const own=Reflect.ownKeys(x);
 return own.length===keys.length&&keys.every(k=>Object.hasOwn(x,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(x,k),'value'));
}
function fail(code){throw Error(code)}
export function auditFictionalRankVisibilityContract(payload){
 if(!exact(payload,['fixture','arms'])||payload.fixture!=='SYNTHETIC_RANK_DESIGN_ONLY'||!exact(payload.arms,ARMS))fail('FICTIONAL_FIVE_CELL_CONTRACT_REQUIRED');
 const ref=payload.arms.own_only;
 for(const name of ARMS){
  const v=payload.arms[name],spec=SPEC[name];
  if(!exact(v,KEYS))fail('INVALID_TREATMENT_SHAPE');
  if(v.feedback!==spec[0]||v.audience!==spec[1]||v.alias_mode!==spec[2]||v.show_own_score!==true)fail('TREATMENT_ISOLATION_BROKEN');
  if(v.reward!=='VIRTUAL_SAME_BRIER' || !HEX.test(v.event_frame)||!HEX.test(v.schedule))fail('NONCOMPARABLE_COMMON_PROTOCOL');
  if(v.reward!==ref.reward||v.event_frame!==ref.event_frame||v.schedule!==ref.schedule)fail('PROTOCOL_PARITY_VIOLATION');
 }
 return Object.freeze({
  schema:'pfl.synthetic.rank_visibility_factorial_contract.v1',
  fixture:'SYNTHETIC_RANK_DESIGN_ONLY',
  arms:Object.freeze([...ARMS]),
  planned_arms:5,
  factorial_cells:Object.freeze(['private_quartile','public_quartile','private_order','public_order']),
  baseline:'own_only',
  planned_contrasts:Object.freeze({
   publicness_at_quartile:Object.freeze({positive:'public_quartile',negative:'private_quartile'}),
   publicness_at_full_order:Object.freeze({positive:'public_order',negative:'private_order'}),
   detail_at_private:Object.freeze({positive:'private_order',negative:'private_quartile'}),
   detail_at_public:Object.freeze({positive:'public_order',negative:'public_quartile'}),
   interaction:Object.freeze({positive:['public_order','private_quartile'],negative:['private_order','public_quartile']})
  }),
  common_opportunities_and_virtual_reward_config_verified:true,
  mutually_visible_aliases_are_treatment_components:true,
  peer_network_interference_possible:true,
  outcome_effect_estimated:false,
  human_allocation_verified:false,
  independent_display_receipts_verified:false,
  population_coverage_verified:false,
  human_records_processed:false,
  politician_scoring_enabled:false,
  release_ready:false,
  science_grade:'0/3',
  limitation:'Static five-arm design parity, not delivery, randomization, privacy approval or causal identification.'
 });
}
