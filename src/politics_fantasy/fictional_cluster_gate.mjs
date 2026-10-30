/** Offline design diagnostic: cluster interference and estimand weighting.
 * Synthetic assignments ONLY; neither randomization nor actual exposure is attested.
 * Never accepts names, political entities, PII, network or human records.
 */
const ARMS = Object.freeze(['control','transparency','leaderboard','both']);
function exact(x, fields) {
  if (x===null || typeof x!=='object' || Array.isArray(x)) return false;
  const proto=Object.getPrototypeOf(x);
  if (proto!==Object.prototype && proto!==null) return false;
  const own=Reflect.ownKeys(x);
  return own.length===fields.length && fields.every(k=>Object.hasOwn(x,k) && Object.hasOwn(Object.getOwnPropertyDescriptor(x,k),'value'));
}
const safeId=v=>typeof v==='string'&&/^[A-Za-z0-9_-]{1,24}$/.test(v);
const fatal=k=>{throw Error(k)};
function factorial(means){
  return Object.freeze({
    transparency:(means.transparency-means.control+means.both-means.leaderboard)/2,
    leaderboard:(means.leaderboard-means.control+means.both-means.transparency)/2,
    interaction:means.both-means.transparency-means.leaderboard+means.control
  });
}
export function diagnoseFictionalClusterFrame(payload){
  if(!exact(payload,['study_fixture','rows'])||payload.study_fixture!=='SYNTHETIC_OFFLINE_ONLY'||!Array.isArray(payload.rows))fatal('SYNTHETIC_FRAME_REQUIRED');
  const people=new Set(),groups=new Map();
  for(const p of payload.rows){
    if(!exact(p,['participant_id','room_id','arm','completed'])||!safeId(p.participant_id)||!safeId(p.room_id)||!ARMS.includes(p.arm)||typeof p.completed!=='boolean')fatal('INVALID_ROW');
    if(people.has(p.participant_id))fatal('DUPLICATE_PERSON');people.add(p.participant_id);
    if(!groups.has(p.room_id))groups.set(p.room_id,{arm:p.arm,n:0,completed:0});
    const g=groups.get(p.room_id);
    if(g.arm!==p.arm)fatal('ROOM_ARM_CONTAMINATION');
    g.n++;if(p.completed)g.completed++;
  }
  if(people.size===0)fatal('EMPTY_FRAME');
  const cells={};
  for(const arm of ARMS){
    const roomRates=[...groups.values()].filter(g=>g.arm===arm).map(g=>g.completed/g.n);
    if(roomRates.length<2)fatal('TOO_FEW_ROOMS_PER_ARM');
    const all=[...groups.values()].filter(g=>g.arm===arm);
    const assigned=all.reduce((a,g)=>a+g.n,0),completed=all.reduce((a,g)=>a+g.completed,0);
    cells[arm]=Object.freeze({rooms:roomRates.length,assigned,completed,
      person_weighted:completed/assigned,
      cluster_equal:roomRates.reduce((a,r)=>a+r,0)/roomRates.length});
  }
  const person=factorial(Object.fromEntries(ARMS.map(a=>[a,cells[a].person_weighted])));
  const cluster=factorial(Object.fromEntries(ARMS.map(a=>[a,cells[a].cluster_equal])));
  return Object.freeze({schema:'pfl.synthetic.cluster.diagnostic.v1',mode:'SYNTHETIC_DESIGN_ONLY',
    n:people.size,rooms:groups.size,cells:Object.freeze(cells),
    factorial_person_weighted:person,factorial_cluster_equal:cluster,
    randomization_attested:false,individual_exposure_attested:false,causal_ready:false,
    interpretation:'Different weighting can change a contrast; no sampling errors or human causal inference.'});
}
