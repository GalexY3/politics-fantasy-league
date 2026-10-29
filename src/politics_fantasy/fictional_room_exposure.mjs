/** Synthetic offline-only time-varying room exposure witness; NOT authentication. */
const ARMS = Object.freeze(['control','transparency','leaderboard','both']);
const FATAL = code => { throw new Error(code); };
function exact(v, fields) {
  if (v===null || typeof v!=='object' || Array.isArray(v)) return false;
  const p=Object.getPrototypeOf(v);
  if (p!==Object.prototype && p!==null) return false;
  const keys=Reflect.ownKeys(v);
  return keys.length===fields.length && fields.every(k=>Object.hasOwn(v,k) && Object.hasOwn(Object.getOwnPropertyDescriptor(v,k),'value'));
}
const id=s=>typeof s==='string' && /^[A-Za-z0-9_-]{1,24}$/.test(s);
function utc(s) {
  if (typeof s!=='string' || !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s)) FATAL('NONCANONICAL_TIME');
  const ms=Date.parse(s);
  if(!Number.isFinite(ms) || new Date(ms).toISOString()!==s.replace('Z','.000Z')) FATAL('NONCANONICAL_TIME');
  return ms;
}
export function auditFictionalRoomExposure(payload) {
  if (!exact(payload,['study_fixture','memberships','questions','impressions']) || payload.study_fixture!=='SYNTHETIC_OFFLINE_ONLY' || !Array.isArray(payload.memberships) || !Array.isArray(payload.questions) || !Array.isArray(payload.impressions)) FATAL('SYNTHETIC_FRAME_ONLY');
  const history=new Map(), questions=new Map(), impressions=new Set();
  for(const m of payload.memberships) {
    if(!exact(m,['member_id','room_id','arm','from_at','until_at']) || !id(m.member_id) || !id(m.room_id) || !ARMS.includes(m.arm)) FATAL('INVALID_MEMBERSHIP');
    const from=utc(m.from_at), until=utc(m.until_at);
    if(from>=until) FATAL('BAD_MEMBERSHIP_INTERVAL');
    if(!history.has(m.member_id))history.set(m.member_id,[]);
    history.get(m.member_id).push({...m,from,until});
  }
  if(history.size===0)FATAL('EMPTY_MEMBERSHIP');
  let switches=0;
  for(const events of history.values()){
    events.sort((a,b)=>a.from-b.from);
    for(let i=1;i<events.length;i++){
      if(events[i].from<events[i-1].until)FATAL('OVERLAPPING_MEMBERSHIPS');
      if(events[i].room_id!==events[i-1].room_id)switches++;
    }
  }
  for(const q of payload.questions) {
    if(!exact(q,['question_id','opens_at','closes_at']) || !id(q.question_id))FATAL('INVALID_QUESTION');
    if(questions.has(q.question_id))FATAL('DUPLICATE_QUESTION');
    const opens=utc(q.opens_at),closes=utc(q.closes_at);
    if(opens>=closes) FATAL('BAD_QUESTION_INTERVAL');
    questions.set(q.question_id,{opens,closes});
  }
  if(questions.size===0)FATAL('EMPTY_QUESTION_FRAME');
  const byArm=Object.fromEntries(ARMS.map(a=>[a,0]));
  for(const view of payload.impressions){
    if(!exact(view,['event_id','member_id','room_id','question_id','shown_at','source']) || !id(view.event_id) || !id(view.member_id) || !id(view.room_id) || !id(view.question_id) || view.source!=='INDEPENDENT_SYNTHETIC_DISPLAY_EVENT') FATAL('UNATTESTED_SYNTHETIC_DISPLAY');
    if(impressions.has(view.event_id))FATAL('DUPLICATE_IMPRESSION');
    impressions.add(view.event_id);
    const at=utc(view.shown_at), q=questions.get(view.question_id);
    if(!q || !(q.opens<=at && at<q.closes))FATAL('DISPLAY_OUTSIDE_QUESTION');
    const active=(history.get(view.member_id)||[]).filter(m=>m.from<=at && at<m.until);
    if(active.length!==1) FATAL('UNRESOLVED_MEMBERSHIP_ASOF');
    if(active[0].room_id!==view.room_id)FATAL('STALE_OR_WRONG_ROOM_VIEW');
    for(const [otherId,events] of history){
      if(otherId===view.member_id)continue;
      if(events.some(m=>m.room_id===view.room_id && m.from<=at && at<m.until && m.arm!==active[0].arm))FATAL('MIXED_ROOM_ARMS_ASOF');
    }
    byArm[active[0].arm]++;
  }
  return Object.freeze({schema:'pfl.synthetic.room.exposure.v1',mode:'SYNTHETIC_OFFLINE_ONLY',
    unique_members:history.size,room_switches:switches,observed_displays:impressions.size,
    by_arm:Object.freeze(byArm),unobserved_displays:'UNKNOWN_NOT_ZERO',
    independent_real_exposure_verified:false,actual_allocation_verified:false,
    causal_claim:false,privacy_clearance:false});
}
