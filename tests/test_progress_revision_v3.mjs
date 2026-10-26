import {test} from "node:test";
import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {compare,evaluate} from "../src/politics_fantasy/progress_model.mjs";
const read=p=>JSON.parse(readFileSync(new URL("../product/"+p,import.meta.url),"utf8"));
const old=read("progress_scope_v2_20261026.json"),current=read("progress_scope_v3_20261026.json");
test("V3 is 36.35%: +0.90 pp verified browser activity, unchanged scope",()=>{
 const d=compare(old,current);
 assert.ok(Math.abs(d.old_pct-35.45)<1e-9);
 assert.ok(Math.abs(d.new_pct-36.35)<1e-9);
 assert.ok(Math.abs(d.work_effect_pp-0.9)<1e-9);
 assert.equal(d.scope_effect_pp,0);
});
test("only frontend and E2E QA milestones are upgraded",()=>{
 let modified=[];
 const m=new Map(old.tracks.flatMap(x=>x.milestones).map(x=>[x.id,x.level]));
 for(const x of current.tracks.flatMap(y=>y.milestones))
  if(m.get(x.id)!==x.level)modified.push([x.id,m.get(x.id),x.level]);
 assert.deepEqual(modified,[["ui.pages",2,3],["qa.endtoend",2,3]]);
});
test("36 tasks, nine lines and all six production safeguards remain",()=>{
 const s=evaluate(current);
 assert.equal(s.milestone_count,36);assert.equal(s.track_count,9);
 assert.equal(s.release_blockers.length,6);
 assert.equal(s.real_people_scoring_ready,false);
 assert.equal(s.global_status,"NOT_PUBLIC_RELEASE_READY");
});
