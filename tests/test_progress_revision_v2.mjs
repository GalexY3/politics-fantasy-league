/* BR12M: actual completed work in an unchanged scope, not a hypothetical enlargement.
 * The frozen v1 and v2 remain distinct files; this is a real GitHub Actions test.
 */
import {test} from "node:test";
import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {evaluate,compare} from "../src/politics_fantasy/progress_model.mjs";
const read=p=>JSON.parse(readFileSync(new URL("../product/"+p,import.meta.url),"utf8"));
const v1=read("progress_scope_v1.json"),v2=read("progress_scope_v2_20261026.json");
test("V2 work improvement is +1.725 pp with unchanged V1 scope",()=>{
 const d=compare(v1,v2); assert.ok(Math.abs(d.old_pct-33.725)<1e-9);
 assert.ok(Math.abs(d.new_pct-35.45)<1e-9);
 assert.ok(Math.abs(d.work_effect_pp-1.725)<1e-9);
 assert.equal(d.scope_effect_pp,0);
});
test("9 tracks 36 milestones and six release blocks remain",()=>{
 const a=evaluate(v2);assert.equal(a.track_count,9);
 assert.equal(a.milestone_count,36); assert.equal(a.release_blockers.length,6);
 assert.equal(a.global_status,"NOT_PUBLIC_RELEASE_READY");
 assert.equal(a.real_people_scoring_ready,false);
});
test("Only evidence-backed source and QA maturities change",()=>{
 let changes=[];
 const old=new Map(v1.tracks.flatMap(t=>t.milestones).map(m=>[m.id,m.level]));
 for(const item of v2.tracks.flatMap(t=>t.milestones)){
   if(item.level!==old.get(item.id))changes.push([item.id,old.get(item.id),item.level]);
 }
 assert.deepEqual(changes,[["src.catalog",3,4],["qa.endtoend",1,2]]);
});
test("V1 snapshot never overwritten and hypothetical V2 isn't silently adopted",()=>{
 assert.equal(v1.revision,1);assert.equal(v2.revision,2);
 assert.equal(v2.tracks.find(x=>x.id==="sources").milestones.length,4);
 assert.equal(evaluate(v1).progress_pct,33.725);
});
