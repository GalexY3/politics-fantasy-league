/** Offline synthetic 2x2 descriptive contrasts; NEVER label fixtures as human ITT. */
export function analyseFictionalPilot(payload){
 const exact=(obj,fields)=>{if(!obj||typeof obj!=="object"||Array.isArray(obj))return false;const proto=Object.getPrototypeOf(obj);if(proto!==Object.prototype&&proto!==null)return false;const keys=Reflect.ownKeys(obj);return keys.length===fields.length&&fields.every(k=>Object.hasOwn(obj,k)&&Object.hasOwn(Object.getOwnPropertyDescriptor(obj,k),"value"));};
 const arms=["control","transparency","leaderboard","both"];
 if(!exact(payload,["rows","study_fixture"])||payload.study_fixture!=="SYNTHETIC_DRY_RUN_ONLY"||!Array.isArray(payload.rows))throw Error("SYNTHETIC_ANALYSIS_ONLY");
 const sums=Object.fromEntries(arms.map(x=>[x,{assigned:0,observed:0,correct_total:0,values:[]}]));
 for(const r of payload.rows){
  if(!exact(r,["arm","completed","correct"])||!arms.includes(r.arm)||typeof r.completed!=="boolean")throw Error("INVALID_ROW");
  if(r.completed){if(!Number.isSafeInteger(r.correct)||r.correct<0||r.correct>4)throw Error("INVALID_SCORE")}else if(r.correct!==null)throw Error("MISSING_MUST_BE_NULL");
  const cell=sums[r.arm];cell.assigned++;
  if(r.completed){cell.observed++;cell.correct_total+=r.correct;cell.values.push(r.correct)}
 }
 if(arms.some(x=>sums[x].assigned===0))throw Error("EMPTY_ARM");
 const means={};for(let a of arms){const s=sums[a];means[a]=s.observed?s.correct_total/s.observed:null}
 const available=arms.every(a=>means[a]!==null);
 const effects=available?{transparency:((means.transparency-means.control)+(means.both-means.leaderboard))/2,leaderboard:((means.leaderboard-means.control)+(means.both-means.transparency))/2,interaction:means.both-means.transparency-means.leaderboard+means.control}:null;
 const missing=Object.values(sums).some(s=>s.assigned!==s.observed);
 const cells=Object.freeze(Object.fromEntries(arms.map(a=>[a,Object.freeze({assigned:sums[a].assigned,observed:sums[a].observed,missing:sums[a].assigned-sums[a].observed,mean:means[a]})])));
 return Object.freeze({schema:"pfl.pilot.analysis.dryrun.v1",source:"FICTIONAL_TEST_ONLY",estimand:missing?"COMPLETE_CASE_NOT_ITT":"FULLY_OBSERVED_FACTORIAL",effects:effects?Object.freeze(effects):null,cells,warning:missing?"MISSING_OUTCOMES_ITT_NOT_IDENTIFIED":"NO_PARTICIPANT_DATA"});
}
