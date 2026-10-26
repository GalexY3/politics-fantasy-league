import {test} from "node:test";
import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {validateScope,evaluate,revise,compare} from "../src/politics_fantasy/progress_model.mjs";
const scope=JSON.parse(readFileSync(new URL("../product/progress_scope_v1.json",import.meta.url),"utf8"));
const clone=x=>JSON.parse(JSON.stringify(x));
export function cases(m,baseline){
 const {validateScope,evaluate,revise,compare}=m;
 const ok=x=>{if(!x)throw Error("ASSERTION_FAILED")};
 const eq=(a,b)=>{if(Math.abs(a-b)>1e-8)throw Error("EXPECTED_"+b+"_GOT_"+a)};
 const reject=(fn,err)=>{let e="";try{fn()}catch(x){e=String(x.message)}ok(e.includes(err))};
 const expanded=()=>revise(baseline,{revision:2,reason:"Simulated expanded national municipal coverage",add_milestones:[{track_id:"sources",milestone:{id:"src.full_local",name:"Full national municipal coverage",level:0,size:1,why:"No original all-country local dataset yet",evidence_ref:"research/BRANCH30J_20261026/REPORT.md",evidence_class:"ABSENT"}}]});
 return [
 ["nine tracks 36 milestones",()=>{const x=validateScope(baseline);ok(x.tracks===9&&x.milestones===36)}],
 ["baseline completion 33.725 percent",()=>eq(evaluate(baseline).progress_pct,33.725)],
 ["report one decimal 33.7",()=>eq(evaluate(baseline).progress_display_pct,33.7)],
 ["per track contributions sum global",()=>{const x=evaluate(baseline);eq(x.tracks.reduce((s,t)=>s+t.contribution_pp,0),x.progress_pct)}],
 ["release blockers stop public launch",()=>{const x=evaluate(baseline);ok(x.global_status==="NOT_PUBLIC_RELEASE_READY"&&x.release_blockers.length===6&&!x.real_people_scoring_ready)}],
 ["maturity histogram covers 36",()=>{const x=evaluate(baseline);eq(Object.values(x.level_histogram).reduce((a,b)=>a+b,0),36);ok(x.level_histogram[5]===0)}],
 ["duplicate milestone rejected",()=>{const x=clone(baseline);x.tracks[1].milestones[0].id=x.tracks[0].milestones[0].id;reject(()=>validateScope(x),"DUPLICATE_OR_INVALID_MILESTONE")}],
 ["source without evidence rejected",()=>{const x=clone(baseline);x.tracks[0].milestones[0].evidence_ref="";reject(()=>validateScope(x),"MILESTONE_NEEDS_EVIDENCE")}],
 ["invalid weight sum rejected",()=>{const x=clone(baseline);x.tracks[1].weight=13;reject(()=>validateScope(x),"TRACK_WEIGHTS_MUST_TOTAL_100")}],
 ["invalid maturity rejected",()=>{const x=clone(baseline);x.tracks[0].milestones[0].level=6;reject(()=>validateScope(x),"BAD_MATURITY")}],
 ["version bump requires reason",()=>reject(()=>revise(baseline,{revision:2,reason:"short"}),"SCOPE_REVISION_REASON_REQUIRED")],
 ["scope expansion lowers progress by 1.395 points",()=>{const x=compare(baseline,expanded());eq(x.new_pct,32.33);eq(x.work_effect_pp,0);eq(x.scope_effect_pp,-1.395)}],
 ["new evidence raises score without scope effect",()=>{const x=compare(baseline,revise(baseline,{revision:2,reason:"Hypothetical confirmed original registry data",level_updates:{"src.registry":3}}));eq(x.work_effect_pp,2.7);eq(x.scope_effect_pp,0)}],
 ["scope plus work decompose exactly",()=>{const x=revise(baseline,{revision:2,reason:"Source improvement and widened municipalities",level_updates:{"src.registry":3},add_milestones:[{track_id:"sources",milestone:{id:"src.full_local",name:"All municipality coverage",level:0,size:1,why:"Still no original countywide corpus",evidence_ref:"research/BRANCH30J_20261026/REPORT.md",evidence_class:"ABSENT"}}]});const a=compare(baseline,x);eq(a.work_effect_pp+a.scope_effect_pp,a.net_change_pp)}],
 ["wrong scope identity cannot be compared",()=>{const x=expanded();x.scope_id="PFL-V2-20261026";reject(()=>compare(baseline,x),"SCOPE_LINEAGE_MISMATCH")}],
 ["wrong revision direction cannot compare",()=>reject(()=>compare(baseline,baseline),"SCOPE_LINEAGE_MISMATCH")],
 ["revised scope does not mutate baseline",()=>{const b=JSON.stringify(baseline);expanded();ok(JSON.stringify(baseline)===b)}],
 ["unknown milestone update rejected",()=>reject(()=>revise(baseline,{revision:2,reason:"Hypothetical invalid id test",level_updates:{"fake.unknown":4}}),"UNKNOWN_MILESTONE")],
 ["unknown track is rejected",()=>reject(()=>revise(baseline,{revision:2,reason:"Hypothetical invalid lane",add_milestones:[{track_id:"no_lanes",milestone:{id:"fake.unknown",name:"Dummy",level:0,size:1,why:"This lane does not exist",evidence_ref:"research/path"}}]}),"MISSING_TARGET_TRACK")],
 ["reintroducing same task rejected",()=>reject(()=>revise(baseline,{revision:2,reason:"Duplicate work should not count twice",add_milestones:[{track_id:"sources",milestone:clone(baseline.tracks[0].milestones[0])}]}),"DUPLICATE_OR_INVALID_MILESTONE")]
 ];
}
for(const [name,fn] of cases({validateScope,evaluate,revise,compare},scope))test(name,fn);
