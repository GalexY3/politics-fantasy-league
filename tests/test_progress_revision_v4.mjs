import {test} from "node:test";
import {strict as assert} from "node:assert";
import {readFileSync} from "node:fs";
import {compare,evaluate} from "../src/politics_fantasy/progress_model.mjs";
const read=p=>JSON.parse(readFileSync(new URL("../product/"+p,import.meta.url),"utf8"));
const old=read("progress_scope_v3_20261026.json");
const current=read("progress_scope_v4_20261027.json");

test("V4 is 36.90% with +0.55 pp only work, unchanged scope",()=>{
 const a=compare(old,current);
 assert.ok(Math.abs(a.old_pct-36.35)<1e-9);
 assert.ok(Math.abs(a.new_pct-36.9)<1e-9);
 assert.ok(Math.abs(a.work_effect_pp-0.55)<1e-9);
 assert.equal(a.scope_effect_pp,0);
});
test("only id.real and ev.person specified at level 1",()=>{
 const prev=new Map(old.tracks.flatMap(t=>t.milestones).map(x=>[x.id,x.level]));
 const changed=current.tracks.flatMap(t=>t.milestones)
  .filter(x=>prev.get(x.id)!==x.level).map(x=>[x.id,prev.get(x.id),x.level]);
 assert.deepEqual(changed,[["id.real",0,1],["ev.person",0,1]]);
});
test("V4 preserves 9 tracks, 36 milestones, six gates and no scores",()=>{
 const p=evaluate(current);
 assert.equal(p.milestone_count,36);assert.equal(p.track_count,9);
 assert.equal(p.release_blockers.length,6);
 assert.equal(p.real_people_scoring_ready,false);
 assert.equal(p.global_status,"NOT_PUBLIC_RELEASE_READY");
 assert.deepEqual(p.level_histogram,{"0":8,"1":9,"2":2,"3":15,"4":2,"5":0});
});
