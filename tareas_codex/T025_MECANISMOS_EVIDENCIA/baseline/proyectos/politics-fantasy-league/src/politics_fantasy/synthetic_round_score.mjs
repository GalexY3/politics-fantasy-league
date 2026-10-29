/** Synthetic fixtures only; no real persons, parties or political actor scoring. */
export function scoreSyntheticRound(input){
const isObject=x=>x!==null&&typeof x==="object"&&!Array.isArray(x);
const keys=(x,allowed)=>Object.keys(x).every(k=>allowed.includes(k));
if(!isObject(input)||!keys(input,["round_id","rule_version","verified_complete","evidence_id","slots","events"]))throw Error("SCHEMA_DENIED");
const {round_id,rule_version,verified_complete,evidence_id,slots,events}=input;
if(typeof round_id!=="string"||!/^SYN-RND-[A-Za-z0-9_-]+$/.test(round_id))throw Error("SYNTHETIC_ROUND_ONLY");
if(typeof rule_version!=="string"||!/^synthetic-v[1-9]\d*$/.test(rule_version))throw Error("SYNTHETIC_RULE_ONLY");
if(typeof verified_complete!=="boolean"||!Array.isArray(slots)||!Array.isArray(events))throw Error("INVALID_COVERAGE");
if(verified_complete&&!(typeof evidence_id==="string"&&/^synthetic-fixture:[a-z0-9_-]+$/.test(evidence_id)))throw Error("EVIDENCE_REQUIRED");
const ids=new Set();for(const id of slots){if(typeof id!=="string"||!/^SYN-EVT-[A-Za-z0-9_-]+$/.test(id))throw Error("SYNTHETIC_EVENT_ONLY");if(ids.has(id))throw Error("DUPLICATE_SLOT");ids.add(id)}
if(events.length!==slots.length)throw Error("INCOMPLETE_EVENT_VECTOR");
const seen=new Set();let attempted=0,success=0;
for(const ev of events){if(!isObject(ev)||!keys(ev,["id","attempted","success"])||!ids.has(ev.id))throw Error("BAD_EVENT");if(seen.has(ev.id))throw Error("DUPLICATE_EVENT");seen.add(ev.id);if(typeof ev.attempted!=="boolean")throw Error("BAD_ATTEMPTED");
if(ev.attempted){if(typeof ev.success!=="boolean")throw Error("BAD_SUCCESS");attempted++;if(ev.success)success++}else if(ev.success!==null)throw Error("UNATTEMPTED_NEEDS_NULL")}
let status=verified_complete?(slots.length?"VERIFIED_SYNTHETIC_ROUND":"VERIFIED_NO_OPPORTUNITIES"):"COVERAGE_UNKNOWN";
const scores=status==="VERIFIED_SYNTHETIC_ROUND"?Object.freeze({raw_successes:success,observed_rate:attempted?success/attempted:null,beta22:(success+2)/(attempted+4),scheduled_rate:success/slots.length}):null;
return Object.freeze({schema:"pfl.synthetic.round.v1",round_id,rule_version,status,evidence_id:verified_complete?evidence_id:null,scheduled:slots.length,attempted,successes:success,scores});
}
