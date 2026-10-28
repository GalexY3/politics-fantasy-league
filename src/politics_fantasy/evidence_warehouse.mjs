/* BR30J: source-first observational warehouse for Spanish public political entities.
 * Stores public-role/organization facts only. No personal ratings, no ideological
 * profiling, no inference of party membership from a candidacy or an event.
 * No network. Cryptographic content hashes MUST be recomputed by Node CLI.
 */
const TYPES=["PARTY","FEDERATION","COALITION","ELECTORS_GROUP","CANDIDACY",
 "CIVIL_ORG","INTEREST_GROUP","UNION","CIVIC_PLATFORM","PUBLIC_BODY","CAMPAIGN","PERSON_PUBLIC"];
const TYPES_EVENT=["DECLARATION","PUBLIC_APPEARANCE","ORGANISATION_EVENT","OFFICIAL_INITIATIVE","CANDIDACY_PROCLAMATION","DOCUMENTED_CAMPAIGN","PUBLIC_DEBATE","ELECTORAL_RESULT"];
const ROLES=["PUBLIC_SPOKESPERSON","DOCUMENTED_LEADER","PUBLIC_CANDIDATE","PUBLIC_OFFICE","COALITION_PARTICIPANT","ELECTORAL_LIST_PARTICIPANT","PUBLIC_EVENT_SPEAKER","CIVIC_ORGANIZER"];
const bad=(code)=>{throw Error(code)};
const check=(test,code)=>{if(!test)bad(code)};
const date=d=>typeof d==="string"&&/^\d{4}-\d\d-\d\d$/.test(d)&&!Number.isNaN(Date.parse(d+"T00:00:00Z"))&&new Date(d+"T00:00:00Z").toISOString().slice(0,10)===d;
const instant=x=>typeof x==="string"&&/^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(x)&&Number.isFinite(Date.parse(x));
const byId=(xs,id,code="MISSING_ID")=>{const found=xs.find(x=>x.id===id);check(found!==undefined,code);return found};
const unique=(xs,id,code="DUPLICATE_ID")=>check(!xs.some(x=>x.id===id),code);
const idValid=x=>typeof x==="string"&&/^[A-Z][A-Z0-9_]{1,31}:[a-zA-Z0-9._-]{1,80}$/.test(x);
const unsafeKey=k=>/__proto__|prototype|constructor|private|email|phone|birth|home.address|personal.address|party_member_guess|religion|ethnic|ideolog|influence.score|psychograph|political_profile|voter_profile/i.test(k);
const noPrivate=(obj,seen=new Set(),depth=0)=>{
 if(obj===null||typeof obj!=="object")return true;
 if(depth>12||seen.has(obj))return false;
 seen.add(obj);
 const entries=Object.entries(obj);
 const ok=entries.length<=1000&&entries.every(([key,val])=>!unsafeKey(key)&&noPrivate(val,seen,depth+1));
 seen.delete(obj);return ok;
};
const isHalfOpen=(d,from,to)=>d>=from&&(to===null||d<to);
export function empty(){return {sources:[],entities:[],roles:[],events:[],claims:[],collisions:[],revisions:[]}}
export function source(reg,v){
 check(v&&typeof v==="object"&&noPrivate(v),"UNSAFE_SOURCE");
 check(idValid(v.id),"SOURCE_ID");
 unique(reg.sources,v.id,"DUPLICATE_SOURCE");
 check(typeof v.url==="string"&&/^https:\/\/[^\s/]+\//.test(v.url),"SOURCE_URL");
 // Do not accept userinfo or escaped authorities masquerading as source origins.
 // This is syntax hygiene, NOT independent validation of the claim "OFFICIAL".
 const authority=v.url.slice(8).split('/')[0];
 check(authority.length>0&&!/[@\\%?#]/.test(authority),"SOURCE_URL");
 check(["OFFICIAL","PUBLISHED_BY_ACTOR","SECONDARY","JOURNALISTIC","SYNTHETIC"].includes(v.kind),"SOURCE_KIND");
 check(["DOCUMENTED_ONLY","RAW_CAPTURED","TEST_FIXTURE"].includes(v.state),"SOURCE_STATE");
 check(instant(v.observed_at),"SOURCE_OBSERVED_AT");
 check(v.first_public_at===null||v.first_public_at===undefined||instant(v.first_public_at),"SOURCE_PUBLIC_AT");
 if(v.first_public_at)check(Date.parse(v.first_public_at)<=Date.parse(v.observed_at),"PUBLIC_AFTER_CAPTURE");
 check(typeof v.rights==="string"&&["OPEN_LICENSE_VERIFIED","TERMS_RESTRICTED","UNKNOWN","SYNTHETIC"].includes(v.rights),"SOURCE_RIGHTS_REQUIRED");
 if(v.state==="RAW_CAPTURED"){
  check(/^[a-f0-9]{64}$/.test(v.sha256??""),"RAW_REQUIRES_SHA256");
  check(v.digest_recomputed===true,"RAW_REQUIRES_RECOMPUTED_DIGEST");
 }else check(v.sha256===null||v.sha256===undefined,"UNVERIFIED_SOURCE_CLAIMS_HASH");
 let o={id:v.id,kind:v.kind,state:v.state,url:v.url,observed_at:v.observed_at,first_public_at:v.first_public_at??null,
  sha256:v.sha256??null,rights:v.rights,scope:v.scope??"UNSPECIFIED",digest_recomputed:v.state==="RAW_CAPTURED"};
 reg.sources.push(o);return o;
}
export function entity(reg,v){
 check(v&&typeof v==="object"&&noPrivate(v),"UNSAFE_ENTITY");
 check(idValid(v.id),"ENTITY_ID");unique(reg.entities,v.id,"DUPLICATE_ENTITY");
 check(TYPES.includes(v.type),"ENTITY_TYPE");
 check(typeof v.name==="string"&&v.name.trim().length>=2&&v.name.length<=160,"ENTITY_NAME");
 let s=byId(reg.sources,v.source_id,"ENTITY_SOURCE_NOT_FOUND");
 check(s.state!=="DOCUMENTED_ONLY","ENTITY_NEEDS_CAPTURED_EVIDENCE");
 if(v.type==="PERSON_PUBLIC")check(v.public_role_documented===true,"NO_PRIVATE_PERSON");
 const x={id:v.id,type:v.type,name:v.name.trim(),source_id:v.source_id,
 public_role_documented:v.type==="PERSON_PUBLIC",jurisdiction:v.jurisdiction??"UNKNOWN",registered_party_id:null};
 reg.entities.push(x);return x;
}
export function resolve(reg,{id,name}){
 check(idValid(id),"BAD_RESOLVE_ID");
 const matched=reg.entities.find(x=>x.id===id);
 if(matched)return {status:"EXACT_NAMESPACE_ID",entity_id:id};
 const others=reg.entities.filter(x=>x.name.toLowerCase()===name?.toLowerCase());
 if(others.length){reg.collisions.push({unresolved_id:id,name,candidate_ids:others.map(x=>x.id)});
  return {status:"AMBIGUOUS_NAME",entity_id:null,candidates:others.length}}
 return {status:"NEW_ID",entity_id:id}
}
function checkProvenance(reg,source_id,observed_at,first_public_at){
 let s=byId(reg.sources,source_id,"UNKNOWN_EVIDENCE_SOURCE");
 check(s.state!=="DOCUMENTED_ONLY","EVIDENCE_ONLY_CATALOGUE");
 check(instant(observed_at),"EVIDENCE_CAPTURE_DATE");
 check(Date.parse(observed_at)<=Date.parse(s.observed_at),"EVIDENCE_AFTER_SOURCE_CAPTURE");
 check(first_public_at===null||first_public_at===undefined||instant(first_public_at),"EVIDENCE_PUBLIC_DATE");
 if(first_public_at)check(Date.parse(first_public_at)<=Date.parse(observed_at),"FUTURE_PUBLIC_DATE");
 return s;
}
export function role(reg,v){
 check(v&&typeof v==="object"&&noPrivate(v),"UNSAFE_ROLE");
 check(idValid(v.id),"ROLE_ID");unique(reg.roles,v.id,"DUPLICATE_ROLE");
 check(ROLES.includes(v.type),"ROLE_TYPE");
 byId(reg.entities,v.subject_id,"ROLE_SUBJECT_NOT_FOUND");
 if(v.object_id)byId(reg.entities,v.object_id,"ROLE_OBJECT_NOT_FOUND");
 check(date(v.valid_from),"ROLE_START");check(v.valid_to===null||v.valid_to===undefined||date(v.valid_to),"ROLE_END");
 check(!v.valid_to||v.valid_to>v.valid_from,"ROLE_INTERVAL");
 const proof=checkProvenance(reg,v.source_id,v.observed_at,v.first_public_at);
 if(v.type==="PUBLIC_OFFICE")check(["OFFICIAL","SYNTHETIC"].includes(proof.kind),"OFFICE_ROLE_NEEDS_OFFICIAL_SOURCE");
 if(v.type==="PUBLIC_CANDIDATE")check(v.object_id!==undefined&&v.object_id!==null&&byId(reg.entities,v.object_id).type==="CANDIDACY","CANDIDATE_NEEDS_LIST");
 if(v.type==="COALITION_PARTICIPANT"){
  check(v.object_id&&byId(reg.entities,v.object_id).type==="COALITION","COALITION_OBJECT");
  check(["PARTY","FEDERATION"].includes(byId(reg.entities,v.subject_id).type),"COALITION_SUBJECT");
 }
 const o={id:v.id,type:v.type,subject_id:v.subject_id,object_id:v.object_id??null,source_id:v.source_id,
 valid_from:v.valid_from,valid_to:v.valid_to??null,observed_at:v.observed_at,first_public_at:v.first_public_at??null};
 reg.roles.push(o);return o;
}
export function event(reg,v){
 check(v&&typeof v==="object"&&noPrivate(v),"UNSAFE_EVENT");
 check(idValid(v.id),"EVENT_ID");unique(reg.events,v.id,"DUPLICATE_EVENT_ID");
 check(TYPES_EVENT.includes(v.type),"EVENT_TYPE");
 check(date(v.occurred_on),"EVENT_DATE");checkProvenance(reg,v.source_id,v.observed_at,v.first_public_at);
 check(Array.isArray(v.participants)&&v.participants.length>=1,"EVENT_PARTICIPANTS");
 const p=v.participants.map(q=>{check(q&&typeof q==="object"&&idValid(q.actor_id),"EVENT_BAD_PARTICIPANT");byId(reg.entities,q.actor_id,"EVENT_UNKNOWN_ENTITY");check(["SPEAKER","ORGANIZER","PUBLIC_ATTENDEE","ISSUER","SIGNATORY","PUBLIC_INSTITUTION"].includes(q.role),"EVENT_PARTICIPATION_ROLE");return {actor_id:q.actor_id,role:q.role}});
 check(new Set(p.map(z=>z.actor_id+":"+z.role)).size===p.length,"EVENT_DUPLICATE_PARTICIPANT");
 const x={id:v.id,type:v.type,occurred_on:v.occurred_on,source_id:v.source_id,observed_at:v.observed_at,
 first_public_at:v.first_public_at??null,participants:p,external_event_id:v.external_event_id??null,amendment_of:v.amendment_of??null};
 if(x.amendment_of)byId(reg.events,x.amendment_of,"UNKNOWN_PREVIOUS_EVENT");
 reg.events.push(x);return x;
}
export function claim(reg,v){
 check(v&&typeof v==="object"&&noPrivate(v),"UNSAFE_CLAIM");
 check(idValid(v.id),"CLAIM_ID");unique(reg.claims,v.id,"DUPLICATE_CLAIM_ID");
 check(["PUBLIC_STATEMENT","CANDIDACY_STATUS","OFFICE_STATUS","OFFICIAL_ELECTORAL_RESULT"].includes(v.type),"CLAIM_TYPE");
 byId(reg.entities,v.subject_id,"CLAIM_SUBJECT");
 const proof=checkProvenance(reg,v.source_id,v.observed_at,v.first_public_at);
 if(v.valid_on!==null&&v.valid_on!==undefined)check(date(v.valid_on),"INVALID_CLAIM_VALID_ON");
 if(v.type==="OFFICE_STATUS")check(date(v.valid_on)&&["OFFICIAL","SYNTHETIC"].includes(proof.kind),"OFFICE_STATUS_NEEDS_OFFICIAL_DATED_EVIDENCE");
 if(v.type==="PUBLIC_STATEMENT")check(typeof v.exact_statement==="string"&&v.exact_statement.length>=2&&v.exact_statement.length<=1000&&typeof v.issue==="string"&&v.issue.length>=2,"CLAIM_QUOTE_AND_ISSUE");
 if(v.type==="OFFICE_STATUS")check(["PRESENT","ABSENT"].includes(v.value),"OFFICE_STATUS_NOT_CONFIRMED");
 const x={id:v.id,type:v.type,subject_id:v.subject_id,source_id:v.source_id,observed_at:v.observed_at,first_public_at:v.first_public_at??null,
 valid_on:v.valid_on??null,exact_statement:v.exact_statement??null,issue:v.issue??null,value:v.value??null};
 reg.claims.push(x);return x;
}
export function asOf(reg,cutoff){
 check(instant(cutoff),"ASOF_DATE");
 const t=Date.parse(cutoff);
 const permitted=new Set(reg.sources.filter(s=>s.state!=="DOCUMENTED_ONLY"&&Date.parse(s.observed_at)<=t&&s.first_public_at!==null&&Date.parse(s.first_public_at)<=t).map(s=>s.id));
 const visible=x=>permitted.has(x.source_id)&&x.first_public_at!==null&&Date.parse(x.first_public_at)<=t&&Date.parse(x.observed_at)<=t;
 return {as_of:cutoff,source_count:permitted.size,roles:reg.roles.filter(visible),events:reg.events.filter(visible),claims:reg.claims.filter(visible)}
}
export function rolesAt(reg,entity_id,day,cutoff=null){
 byId(reg.entities,entity_id,"UNKNOWN_ROLE_ENTITY");check(date(day),"ROLE_QUERY_DATE");
 const list=cutoff?asOf(reg,cutoff).roles:reg.roles;
 return list.filter(r=>r.subject_id===entity_id&&isHalfOpen(day,r.valid_from,r.valid_to))
}
export function officeStatus(reg,id,on,cutoff=null){
 byId(reg.entities,id,"UNKNOWN_OFFICE_ENTITY");check(date(on),"BAD_OFFICE_DATE");
 const list=(cutoff?asOf(reg,cutoff).claims:reg.claims).filter(c=>c.subject_id===id&&c.type==="OFFICE_STATUS"&&c.valid_on===on);
 if(!list.length)return "UNKNOWN";
 if(new Set(list.map(c=>c.value)).size!==1)return "CONFLICT_REVIEW_REQUIRED";
 return list[0].value;
}
export function eventDuplicates(reg){
 // A local external reference may be reused by different publishers/feeds.
 // Source-id scope avoids asserting that unrelated institutions describe one event.
 // It can miss a true collision between different files of the same publisher:
 // this is a *candidate* detector, not a universal deduplicator.
 const byKey=new Map();
 for(const e of reg.events){
  if(!e.external_event_id)continue;
  const key=JSON.stringify([e.source_id??null,e.external_event_id]);
  const rows=byKey.get(key)??[];
  rows.push(e.id);byKey.set(key,rows);
 }
 return [...byKey].filter(([,xs])=>xs.length>1).map(([key,ids])=>{
  const [source_id,external_event_id]=JSON.parse(key);
  return {source_id,external_event_id,event_ids:ids,needs_review:true};
 });
}
export function coverage(reg){
 const tally=(xs,key)=>Object.fromEntries([...new Set(xs.map(x=>x[key]))].sort().map(k=>[k,xs.filter(x=>x[key]===k).length]));
 return {registered_entities:reg.entities.length,by_type:tally(reg.entities,"type"),
 sources_by_kind:tally(reg.sources,"kind"),sources_by_state:tally(reg.sources,"state"),
 event_count:reg.events.length,roles_count:reg.roles.length,
 unknown_first_public_claims:reg.claims.filter(x=>x.first_public_at===null).length,
 unresolved_name_collisions:reg.collisions.length,
 known_population_denominator:null,coverage_rate:null,
 measurement_warning:"This is a source sample; denominator of all political persons/parties in Spain is NOT established."}
}
export function evidenceGate(reg){
 const captured=reg.sources.filter(s=>s.state==="RAW_CAPTURED");
 const blockers=[];
 if(!captured.length)blockers.push("NO_ORIGINAL_RAW_CAPTURED");
 if(captured.some(s=>s.rights!=="OPEN_LICENSE_VERIFIED"))blockers.push("RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION");
 if(!reg.entities.some(e=>e.type==="PERSON_PUBLIC"))blockers.push("NO_VERIFIED_PUBLIC_PERSON_COHORT");
 if(reg.sources.some(s=>s.first_public_at===null))blockers.push("SOURCE_PUBLICATION_DATE_UNKNOWN");
 return {can_publish_field_people:false,can_infer_influence:false,can_score_real_people:false,
 sources_raw:captureLength(captured),blockers,read_only_aggregate_display_allowed:true}
}
function captureLength(xs){return xs.length}
export function auditBundle(reg){
 const ids=new Set(reg.sources.map(x=>x.id));const eids=new Set(reg.entities.map(x=>x.id));
 const broken=[...reg.entities.filter(x=>!ids.has(x.source_id)).map(x=>"ENTITY:"+x.id),
 ...reg.roles.filter(x=>!ids.has(x.source_id)||!eids.has(x.subject_id)).map(x=>"ROLE:"+x.id),
 ...reg.events.filter(x=>!ids.has(x.source_id)||x.participants.some(p=>!eids.has(p.actor_id))).map(x=>"EVENT:"+x.id),
 ...reg.claims.filter(x=>!ids.has(x.source_id)||!eids.has(x.subject_id)).map(x=>"CLAIM:"+x.id)];
 return {ok:broken.length===0,broken,coverage:coverage(reg),gate:evidenceGate(reg),event_collisions:eventDuplicates(reg)}
}
export const CAPABILITIES={types:TYPES,eventTypes:TYPES_EVENT,roles:ROLES};
