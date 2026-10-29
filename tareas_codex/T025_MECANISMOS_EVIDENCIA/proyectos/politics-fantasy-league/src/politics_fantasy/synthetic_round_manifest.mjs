/** Canonical synthetic manifest, not a signature or source authentication. */
export function buildSyntheticManifest(snapshot,previous=null){
const isObject=x=>!!x&&typeof x==="object"&&!Array.isArray(x)&&(Object.getPrototypeOf(x)===Object.prototype||Object.getPrototypeOf(x)===null),valid=x=>Number.isFinite(x)&&x>=0&&x<=1;
const hasExactFields=(x,expected)=>{const names=Reflect.ownKeys(x);return names.length===expected.length&&names.every(k=>typeof k==="string"&&expected.includes(k)&&Object.getOwnPropertyDescriptor(x,k)?.enumerable===true&&Object.hasOwn(Object.getOwnPropertyDescriptor(x,k),"value"));};
if(!isObject(snapshot)||!hasExactFields(snapshot,["attempted","evidence_id","round_id","rule_version","scheduled","schema","scores","status","successes"]))throw Error("BAD_SNAPSHOT_SCHEMA");
const {round_id,rule_version,status,evidence_id,scheduled,attempted,successes,scores,schema}=snapshot;
if(schema!=="pfl.synthetic.round.v1"||typeof round_id!=="string"||!/^SYN-RND-[A-Za-z0-9_-]+$/.test(round_id)||!/^synthetic-v[1-9]\d*$/.test(rule_version))throw Error("SYNTHETIC_ONLY");
if(!Number.isSafeInteger(scheduled)||scheduled<0||!Number.isSafeInteger(attempted)||attempted<0||attempted>scheduled||!Number.isSafeInteger(successes)||successes<0||successes>attempted)throw Error("COUNTS_INVALID");
if(!["COVERAGE_UNKNOWN","VERIFIED_NO_OPPORTUNITIES","VERIFIED_SYNTHETIC_ROUND"].includes(status))throw Error("STATUS_INVALID");
if(status==="COVERAGE_UNKNOWN"){if(scores!==null||evidence_id!==null)throw Error("UNKNOWN_CANNOT_SCORE")}
else {if(typeof evidence_id!=="string"||!/^synthetic-fixture:[a-z0-9_-]+$/.test(evidence_id))throw Error("EVIDENCE_REQUIRED");if(status==="VERIFIED_NO_OPPORTUNITIES"&&(scheduled!==0||scores!==null))throw Error("EMPTY_STATUS_CONFLICT");if(status==="VERIFIED_SYNTHETIC_ROUND"){if(scheduled===0||!isObject(scores)||!hasExactFields(scores,["raw_successes","observed_rate","beta22","scheduled_rate"]))throw Error("INVALID_SCORES");if(scores.raw_successes!==successes||scores.observed_rate!==(attempted?successes/attempted:null)||scores.beta22!==(successes+2)/(attempted+4)||scores.scheduled_rate!==successes/scheduled||!valid(scores.beta22)||!valid(scores.scheduled_rate))throw Error("SCORES_INCONSISTENT")}}
const payload={schema,round_id,rule_version,status,evidence_id,scheduled,attempted,successes,scores:scores?{raw_successes:scores.raw_successes,observed_rate:scores.observed_rate,beta22:scores.beta22,scheduled_rate:scores.scheduled_rate}:null};
const canonical_payload=JSON.stringify(payload);
if(previous!==null){if(!isObject(previous)||previous.schema!=="pfl.synthetic.manifest.v1"||typeof previous.canonical_payload!=="string"||typeof previous.round_id!=="string")throw Error("INVALID_PREVIOUS");if(previous.round_id!==round_id)throw Error("ROUND_CONFLICT");if(previous.canonical_payload!==canonical_payload)throw Error("REVISION_CONFLICT")}
return Object.freeze({schema:"pfl.synthetic.manifest.v1",round_id,rule_version,status,canonical_payload,duplicate_safe:previous!==null});
}
