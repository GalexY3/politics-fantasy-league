import {test} from "node:test";
import {strict as assert} from "node:assert";
import {evaluate} from "../src/politics_fantasy/progress_model.mjs";

const scope = () => ({
 scope_id: "PFL-V1-20261026", revision: 4,
 tracks: [{id: "test", name: "Synthetic", weight: 100,
  milestones: [{id: "test.good", name: "Synthetic item",
   why: "For differential testing", level: 3, size: 1,
   evidence_ref: "synthetic/test", evidence_class: "TEST"}]}]
});
const reject = p => assert.throws(() => evaluate(p));

test("missing critical release milestones block all six gates", () => {
 const r = evaluate(scope());
 assert.equal(r.global_status, "NOT_PUBLIC_RELEASE_READY");
 assert.equal(r.release_blockers.length, 6);
 assert.equal(r.real_people_scoring_ready, false);
});
test("only V1 scope family is supported", () => {
 const p = scope(); p.scope_id = "PFL-V2-20261026"; reject(p);
});
test("missing track name is invalid", () => {
 const p = scope(); delete p.tracks[0].name; reject(p);
});
for(const [k,value] of [
 ["id", "INVALID"], ["name", 7], ["why", 7],
 ["evidence_ref", "x"], ["size", 10001], ["size", Number.NaN]
]){
 test("malformed milestone "+k+" is invalid", () => {
  const p = scope(); p.tracks[0].milestones[0][k] = value; reject(p);
 });
}
