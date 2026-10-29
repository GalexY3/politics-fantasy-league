/** Offline-only opportunity/response/exposure audit for synthetic PFL research fixtures.
 * No collection, enrolment, publication, user tracking or causal-estimate claims.
 * Never infer an individual display from a published question or submitted forecast.
 */
const ARMS = Object.freeze(['control','transparency','leaderboard','both']);
const PROVENANCE = 'INDEPENDENT_SYNTHETIC_DISPLAY_EVENT';
function fail(code){throw new Error(code)}
function objectExact(obj, names){
 if(obj===null || typeof obj!=='object' || Array.isArray(obj)) return false;
 const proto=Object.getPrototypeOf(obj);
 if(proto!==Object.prototype && proto!==null)return false;
 const actual=Reflect.ownKeys(obj);
 return actual.length===names.length && names.every(n=>Object.hasOwn(obj,n) && Object.hasOwn(Object.getOwnPropertyDescriptor(obj,n),'value'));
}
function id(s){return typeof s==='string' && /^[A-Za-z0-9_-]{1,24}$/.test(s)}
function stamp(s){
 if(typeof s!=='string'|| !/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$/.test(s))fail('INVALID_UTC_TIME');
 const ms=Date.parse(s);
 if(!Number.isFinite(ms)||new Date(ms).toISOString()!==s.replace('Z','.000Z'))fail('INVALID_UTC_TIME');
 return ms;
}
export function auditFictionalOpportunities(payload){
 if(!objectExact(payload,['study_fixture','roster_complete','roster','questions','first_answers','impressions'])
  ||payload.study_fixture!=='SYNTHETIC_OFFLINE_ONLY'
  ||payload.roster_complete!==true
  ||![payload.roster,payload.questions,payload.first_answers,payload.impressions].every(Array.isArray))fail('SYNTHETIC_FULL_ROSTER_REQUIRED');
 const people=new Map(), questions=new Map();
 for(const person of payload.roster){
  if(!objectExact(person,['participant_id','arm','registered_at'])|| !id(person.participant_id)||!ARMS.includes(person.arm))fail('INVALID_ROSTER');
  if(people.has(person.participant_id))fail('DUPLICATE_PARTICIPANT');
  people.set(person.participant_id,{...person,ts:stamp(person.registered_at)});
 }
 for(const q of payload.questions){
  if(!objectExact(q,['question_id','opened_at','closed_at'])||!id(q.question_id))fail('INVALID_QUESTION');
  if(questions.has(q.question_id))fail('DUPLICATE_QUESTION');
  const open=stamp(q.opened_at),close=stamp(q.closed_at);
  if(open>=close)fail('INVALID_WINDOW');
  questions.set(q.question_id,{open,close});
 }
 if(people.size===0||questions.size===0)fail('EMPTY_RISK_SET');
 const opportunity=(personId,questionId)=>{
  const person=people.get(personId),q=questions.get(questionId);
  if(!person||!q)fail('UNKNOWN_UNIT');
  const start=Math.max(person.ts,q.open);
  if(start>=q.close)fail('NOT_ELIGIBLE');
  return {start,close:q.close};
 };
 const answers=new Map();
 for(const a of payload.first_answers){
  if(!objectExact(a,['participant_id','question_id','submitted_at']))fail('INVALID_FIRST_ANSWER');
  const w=opportunity(a.participant_id,a.question_id),ts=stamp(a.submitted_at);
  if(ts<w.start||ts>=w.close)fail('FIRST_ANSWER_OUTSIDE_WINDOW');
  const k=a.participant_id+'|'+a.question_id;
  if(answers.has(k))fail('DUPLICATE_FIRST_ANSWER');
  answers.set(k,ts);
 }
 const observed=new Map();
 for(const e of payload.impressions){
  if(!objectExact(e,['participant_id','question_id','observed_at','provenance'])||e.provenance!==PROVENANCE)fail('UNVERIFIED_DISPLAY_SEMANTICS');
  const w=opportunity(e.participant_id,e.question_id),ts=stamp(e.observed_at);
  if(ts<w.start||ts>=w.close)fail('DISPLAY_OUTSIDE_WINDOW');
  const k=e.participant_id+'|'+e.question_id, previous=observed.get(k);
  if(previous===undefined||ts<previous)observed.set(k,ts);
 }
 const cells=Object.fromEntries(ARMS.map(a=>[a,{assigned:0,eligible_opportunities:0,first_responses:0,pre_response_displays:0,post_response_only_displays:0,unknown_display_opportunities:0,display_without_response:0}]));
 for(const person of people.values()){
  const s=cells[person.arm];s.assigned++;
  for(const [qid,q] of questions){
   const start=Math.max(person.ts,q.open);
   if(start>=q.close)continue;
   const k=person.participant_id+'|'+qid;
   s.eligible_opportunities++;
   const answer=answers.get(k),view=observed.get(k);
   if(answer!==undefined)s.first_responses++;
   if(view===undefined)s.unknown_display_opportunities++;
   else if(answer!==undefined && view>answer)s.post_response_only_displays++;
   else {s.pre_response_displays++;if(answer===undefined)s.display_without_response++}
  }
 }
 let n=0,y=0;
 for(const s of Object.values(cells)){
  n+=s.eligible_opportunities;y+=s.first_responses;
  s.uptake_per_eligible=s.eligible_opportunities?s.first_responses/s.eligible_opportunities:null;
  Object.freeze(s);
 }
 return Object.freeze({schema:'pfl.synthetic.opportunity.audit.v1',source:'FICTIONAL_ONLY_NOT_HUMAN_ITT',opportunities:n,first_responses:y,uptake_per_eligible:y/n,display_absence_meaning:'UNKNOWN_NOT_UNSEEN',cells:Object.freeze(cells)});
}
