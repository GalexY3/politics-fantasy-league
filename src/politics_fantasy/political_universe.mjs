/* PF-BR20H — actor universe, documented relations, no inferred affiliation.
 * Public-record analytical instrumentation. Not a real-person reputation, influence
 * or fantasy-point scoring service. No network or external dependencies.
 */
export const KINDS = Object.freeze(["PERSON","PARTY","FEDERATION","COALITION",
 "ELECTORS_GROUP","CIVIC_PLATFORM","CIVIL_ORG","UNION","THINK_TANK",
 "MEDIA_ORG","PUBLIC_BODY","CANDIDACY","CAMPAIGN"]);
export const ROLES = Object.freeze(["REGISTERED_PARTY","CANDIDATE_FOR",
 "ELECTED_TO","DOCUMENTED_LEADERSHIP","PUBLIC_SPOKESPERSON",
 "COALITION_MEMBER","PUBLIC_ADVOCACY","DECLARED_POLICY_POSITION",
 "REGISTERED_INTEREST_GROUP","DOCUMENTED_PUBLIC_OFFICE","SEAT_STATUS"]);
export const EVENTS = Object.freeze(["OFFICIAL_VOTE","PUBLIC_STATEMENT",
 "PUBLIC_MEETING","REGISTERED_INITIATIVE","CANDIDACY_PROCLAMATION",
 "ORGANIZATION_ANNOUNCEMENT","PUBLIC_DEBATE","CIVIC_CAMPAIGN"]);
export const SOURCES = Object.freeze(["OFFICIAL","PUBLISHED_BY_ACTOR","SECONDARY",
 "JOURNALISM","FIXTURE"]);
export const SOURCE_STATE = Object.freeze(["DOCUMENTED_ONLY","RAW_CAPTURED","FIXTURE"]);
function assert(ok,code){if(!ok) throw new Error(code);}
function isoDate(s){return typeof s==="string" && /^\d{4}-\d\d-\d\d$/.test(s) &&
 !Number.isNaN(Date.parse(s+"T00:00:00Z")) &&
 new Date(s+"T00:00:00Z").toISOString().slice(0,10)===s;}
function instant(s){return typeof s==="string" && /^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\d(?:\.\d+)?(?:Z|[+-]\d\d:\d\d)$/.test(s)&&Number.isFinite(Date.parse(s));}
function within(day,from,to){return (!from||day>=from)&&(!to||day<to);}
function noSecretFields(v){return !Object.keys(v).some(k=>/email|phone|address|private|influence[_-]?score|ideology[_-]?score|voter[_-]?profile|belief[_-]?inference/i.test(k));}
export function stableId(namespace,externalId){
 assert(/^[A-Z][A-Z0-9_]{1,31}$/.test(namespace),"BAD_NAMESPACE");
 assert(typeof externalId==="string"&&/^[A-Za-z0-9._-]{1,80}$/.test(externalId),"BAD_EXTERNAL_ID");
 return namespace+":"+externalId;
}
export function createRegistry(){
 return {sources:[],actors:[],claims:[],events:[],ambiguities:[],decisions:[]};
}
function unique(reg,key,id){assert(!reg[key].some(x=>x.id===id),"DUPLICATE_"+key.toUpperCase());}
function lookup(reg,key,id){let x=reg[key].find(x=>x.id===id);assert(x!==undefined,"MISSING_"+key.toUpperCase());return x;}
export function addSource(reg,s){
 assert(s && typeof s==="object" && noSecretFields(s),"BAD_SOURCE");
 unique(reg,"sources",s.id);
 assert(typeof s.id==="string"&&s.id.length>0,"BAD_SOURCE_ID");
 assert(SOURCES.includes(s.kind)&&SOURCE_STATE.includes(s.state),"BAD_SOURCE_TYPE");
 assert(/^https:\/\/[^\s/]+\/\S*/.test(s.url),"SOURCE_NEEDS_HTTPS_URL");
 assert(instant(s.observed_at),"SOURCE_NEEDS_OBSERVED_AT");
 assert(s.license===null || (typeof s.license==="string"&&s.license.length>0),"BAD_LICENSE");
 assert(s.state!=="RAW_CAPTURED" || /^[a-f0-9]{64}$/.test(s.sha256||""),"RAW_NEEDS_SHA256");
 assert(s.state==="RAW_CAPTURED" || s.sha256===null || s.sha256===undefined,"UNVERIFIED_HASH");
 let o={id:s.id,kind:s.kind,state:s.state,url:s.url,observed_at:s.observed_at,
 license:s.license??null,sha256:s.sha256??null,
 limitation:s.limitation||null};
 reg.sources.push(o);return o;
}
export function addActor(reg,a){
 assert(a && typeof a==="object" && noSecretFields(a),"BAD_ACTOR");
 assert(KINDS.includes(a.kind),"UNKNOWN_ACTOR_TYPE");
 assert(typeof a.name==="string"&&a.name.trim().length>1&&a.name.length<=160,"BAD_ACTOR_NAME");
 assert(typeof a.id==="string"&&/^[A-Z][A-Z0-9_]{1,31}:[A-Za-z0-9._-]{1,80}$/.test(a.id),"BAD_ACTOR_ID");
 assert(typeof a.source_id==="string","ACTOR_REQUIRES_SOURCE");
 lookup(reg,"sources",a.source_id);
 unique(reg,"actors",a.id);
 if(a.kind==="PERSON")assert(a.public_role_documented===true,"PRIVATE_PERSON_EXCLUDED");
 let out={id:a.id,kind:a.kind,name:a.name.trim(),source_id:a.source_id,
 public_role_documented:a.kind==="PERSON"?true:null,
 jurisdiction:a.jurisdiction||"UNSPECIFIED"};
 reg.actors.push(out);return out;
}
export function resolveIdentity(reg,{authority,external_id,name}){
 const id=stableId(authority,external_id);
 const actor=reg.actors.find(a=>a.id===id);
 if(actor)return {status:"EXACT_ID_MATCH",actor_id:id};
 const same=reg.actors.filter(a=>a.name===name);
 if(same.length){reg.ambiguities.push({authority,external_id,name,candidate_ids:same.map(a=>a.id)});
 return {status:"UNRESOLVED_HOMONYM",actor_id:null,candidate_count:same.length};}
 return {status:"NEW_IDENTIFIABLE_ENTITY",actor_id:id};
}
export function addClaim(reg,c){
 assert(c&&typeof c==="object"&&noSecretFields(c),"BAD_CLAIM");
 assert(ROLES.includes(c.relation),"UNKNOWN_RELATION");
 assert(typeof c.id==="string"&&c.id.length>0,"BAD_CLAIM_ID");unique(reg,"claims",c.id);
 const subject=lookup(reg,"actors",c.subject_id),source=lookup(reg,"sources",c.source_id);
 assert(isoDate(c.valid_from),"BAD_VALID_FROM");
 assert(c.valid_to===null||c.valid_to===undefined||isoDate(c.valid_to),"BAD_VALID_TO");
 assert(!c.valid_to||c.valid_to>c.valid_from,"BAD_INTERVAL");
 assert(instant(c.observed_at)&&Date.parse(c.observed_at)<=Date.parse(source.observed_at),"CLAIM_AFTER_SOURCE_CAPTURE");
 assert(c.first_public_at===null||c.first_public_at===undefined||instant(c.first_public_at),"BAD_FIRST_PUBLIC");
 if(c.first_public_at)assert(Date.parse(c.first_public_at)<=Date.parse(c.observed_at),"PUBLIC_AFTER_OBSERVATION");
 if(c.object_id)lookup(reg,"actors",c.object_id);
 if(c.relation==="CANDIDATE_FOR"){
   assert(subject.kind==="PERSON","CANDIDATE_MUST_BE_PERSON");
   let obj=lookup(reg,"actors",c.object_id);
   assert(["PARTY","FEDERATION","COALITION","ELECTORS_GROUP","CANDIDACY"].includes(obj.kind),"BAD_CANDIDACY_ORGANIZATION");
 }
 if(c.relation==="COALITION_MEMBER"){
   assert(lookup(reg,"actors",c.object_id).kind==="COALITION","COALITION_MEMBERSHIP_OBJECT");
   assert(["PARTY","FEDERATION"].includes(subject.kind),"COALITION_MEMBER_TYPE");
 }
 if(c.relation==="DECLARED_POLICY_POSITION"){
   assert(typeof c.issue==="string"&&c.issue.length>=2&&c.issue.length<=120,"ISSUE_REQUIRED");
   assert(typeof c.exact_statement==="string"&&c.exact_statement.length>0&&c.exact_statement.length<=600,"VERBATIM_REQUIRED");
   assert(!("left_right" in c) && !("ideological_coordinate" in c),"NO_IDEOLOGICAL_COORDINATES");
 }
 if(c.relation==="SEAT_STATUS"){
   assert(["PRESENT","ABSENT"].includes(c.value),"SEAT_STATUS_MUST_BE_EXPLICIT");
   assert(typeof c.election_id==="string"&&c.election_id.length>0,"ELECTION_REF_REQUIRED");
   assert(source.kind==="OFFICIAL","SEAT_NEEDS_OFFICIAL_EVIDENCE");
 }
 if(subject.kind==="PERSON" && c.relation==="REGISTERED_PARTY")throw Error("PRIVATE_MEMBERSHIP_NOT_INFERABLE");
 const o={id:c.id,relation:c.relation,subject_id:c.subject_id,
 object_id:c.object_id||null,source_id:c.source_id,valid_from:c.valid_from,valid_to:c.valid_to??null,
 observed_at:c.observed_at,first_public_at:c.first_public_at??null,
 exact_statement:c.exact_statement||null,issue:c.issue||null,
 value:c.value||null,election_id:c.election_id||null};
 reg.claims.push(o);return o;
}
export function addEvent(reg,e){
 assert(e&&typeof e==="object"&&noSecretFields(e),"BAD_EVENT");
 assert(EVENTS.includes(e.kind),"UNKNOWN_EVENT");
 assert(typeof e.id==="string"&&e.id.length>0,"BAD_EVENT_ID");unique(reg,"events",e.id);
 const s=lookup(reg,"sources",e.source_id);
 assert(isoDate(e.occurred_on),"BAD_EVENT_DATE");
 assert(instant(e.observed_at)&&Date.parse(e.observed_at)<=Date.parse(s.observed_at),"BAD_EVENT_OBSERVATION");
 assert(e.first_public_at===null||e.first_public_at===undefined||instant(e.first_public_at),"BAD_EVENT_PUBLIC");
 assert(!e.first_public_at||Date.parse(e.first_public_at)<=Date.parse(e.observed_at),"BAD_EVENT_PUBLIC_ORDER");
 assert(Array.isArray(e.participants)&&e.participants.length>0,"EVENT_PARTICIPANTS_REQUIRED");
 const participants=e.participants.map(p=>{
  lookup(reg,"actors",p.actor_id);
  assert(["SPEAKER","SIGNATORY","ORGANIZER","ATTENDEE_PUBLIC","PUBLISHER","INSTITUTION"].includes(p.role),"BAD_EVENT_ROLE");
  return {actor_id:p.actor_id,role:p.role};
 });
 assert(new Set(participants.map(p=>p.actor_id+":"+p.role)).size===participants.length,"DUPLICATED_EVENT_PARTICIPANT");
 let out={id:e.id,kind:e.kind,source_id:e.source_id,occurred_on:e.occurred_on,
 observed_at:e.observed_at,first_public_at:e.first_public_at??null,participants,
 description:e.description||null};
 reg.events.push(out);return out;
}
export function timeView(reg,cutoff){
 assert(instant(cutoff),"BAD_CUTOFF");
 const now=Date.parse(cutoff),sources=new Set(reg.sources.filter(s=>Date.parse(s.observed_at)<=now && s.state!=="DOCUMENTED_ONLY").map(s=>s.id));
 const available=o=>sources.has(o.source_id)&&o.first_public_at!==null&&Date.parse(o.first_public_at)<=now&&Date.parse(o.observed_at)<=now;
 const claims=reg.claims.filter(available),events=reg.events.filter(available);
 return {cutoff,claims,events,eligible_source_ids:[...sources]};
}
export function roleAt(reg,actorId,day,{cutoff=null}={}){
 lookup(reg,"actors",actorId);assert(isoDate(day),"BAD_ROLE_QUERY_DATE");
 const visible=cutoff?timeView(reg,cutoff).claims:reg.claims;
 return visible.filter(c=>c.subject_id===actorId&&within(day,c.valid_from,c.valid_to));
}
export function actorProfile(reg,id,{cutoff=null}={}){
 const a=lookup(reg,"actors",id);
 const records=cutoff?timeView(reg,cutoff).claims:reg.claims;
 return {id:a.id,name:a.name,kind:a.kind,jurisdiction:a.jurisdiction,
 documented_relations:records.filter(c=>c.subject_id===id||c.object_id===id).map(c=>({type:c.relation,source_id:c.source_id,valid_from:c.valid_from,valid_to:c.valid_to,issue:c.issue,statement:c.exact_statement})),
 representation_status:representation(reg,id,cutoff)};
}
export function representation(reg,id,cutoff=null){
 const actor=lookup(reg,"actors",id);
 if(actor.kind==="PERSON"||actor.kind==="PUBLIC_BODY")return "NOT_AN_ORGANIZATION_STATUS";
 const claims=cutoff?timeView(reg,cutoff).claims:reg.claims;
 const statuses=claims.filter(c=>c.subject_id===id&&c.relation==="SEAT_STATUS");
 if(!statuses.length)return "UNKNOWN";
 if(new Set(statuses.map(c=>c.value)).size>1)return "CONFLICT_REVIEW_REQUIRED";
 return statuses.at(-1).value;
}
export function issueClaims(reg,issue){
 assert(typeof issue==="string"&&issue.length>0,"ISSUE_QUERY_REQUIRED");
 return reg.claims.filter(c=>c.relation==="DECLARED_POLICY_POSITION"&&c.issue===issue)
 .map(c=>({actor_id:c.subject_id,statement:c.exact_statement,source_id:c.source_id}));
}
export function filterActors(reg,{kind=null,jurisdiction=null,relation=null}={}){
 if(kind)assert(KINDS.includes(kind),"BAD_FILTER_KIND");
 return reg.actors.filter(a=>(!kind||a.kind===kind)&&(!jurisdiction||a.jurisdiction===jurisdiction)&&
 (!relation||reg.claims.some(c=>c.subject_id===a.id&&c.relation===relation)))
 .map(a=>({id:a.id,name:a.name,kind:a.kind,jurisdiction:a.jurisdiction}));
}
export function coverageAudit(reg){
 const actorTypes=Object.fromEntries(KINDS.map(k=>[k,reg.actors.filter(a=>a.kind===k).length]));
 const sourceTypes=Object.fromEntries(SOURCES.map(k=>[k,reg.sources.filter(s=>s.kind===k).length]));
 const organizations=reg.actors.filter(a=>a.kind!=="PERSON"&&a.kind!=="PUBLIC_BODY");
 const seatStatus=organizations.reduce((o,a)=>{const k=representation(reg,a.id);o[k]=(o[k]||0)+1;return o;},{PRESENT:0,ABSENT:0,UNKNOWN:0,CONFLICT_REVIEW_REQUIRED:0});
 return {actors:reg.actors.length,organizations:organizations.length,actorTypes,sourceTypes,seatStatus,
 undocumented_first_public:reg.claims.filter(c=>c.first_public_at===null).length,
 eventsWithoutFirstPublic:reg.events.filter(c=>c.first_public_at===null).length,
 unresolved_homonyms:reg.ambiguities.length};
}
export function realityScoringGate(reg,actorId){
 const actor=lookup(reg,"actors",actorId);
 return {actor_id:actorId,eligible:false,reason:actor.kind==="PERSON"?
  "INDIVIDUAL_POLITICAL_RATING_NOT_ENABLED":
  "NO_VERIFIED_NONPARTISAN_RULES_AND_EVENT_QUALITY",
  available_documented_events:reg.events.filter(e=>e.participants.some(p=>p.actor_id===actorId)).length};
}
export function validateRegistry(reg){
 const problems=[];
 for(const c of reg.claims){if(!reg.sources.some(s=>s.id===c.source_id))problems.push("ORPHAN_CLAIM_SOURCE:"+c.id);if(!reg.actors.some(a=>a.id===c.subject_id))problems.push("ORPHAN_CLAIM_ACTOR:"+c.id);}
 for(const e of reg.events){if(!reg.sources.some(s=>s.id===e.source_id))problems.push("ORPHAN_EVENT_SOURCE:"+e.id);for(const p of e.participants)if(!reg.actors.some(a=>a.id===p.actor_id))problems.push("ORPHAN_EVENT_ACTOR:"+e.id);}
 return {valid:problems.length===0,problems,counts:{sources:reg.sources.length,actors:reg.actors.length,claims:reg.claims.length,events:reg.events.length}};
}
export function minimalParliamentaryBaseline(reg){
 const persons=reg.actors.filter(a=>a.kind==="PERSON");
 const represented=new Set(reg.claims.filter(c=>c.relation==="ELECTED_TO").map(c=>c.subject_id));
 return {person_count:persons.length,represented_person_count:persons.filter(a=>represented.has(a.id)).length,
 nonseat_public_person_count:persons.filter(a=>!represented.has(a.id)).length,
 ignored_nonperson_actor_count:reg.actors.length-persons.length,
 limitation:"This counts recorded roles only; lack of ELECTED_TO is UNKNOWN, not proof of no seat."};
}
