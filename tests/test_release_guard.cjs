"use strict";
// Runnable, offline, dependency-free tests on the *real* V4+achievement files.
// Run: node --test proyectos/politics-fantasy-league/tests/test_release_guard.cjs
// The research campaign tested exact guard code in V8; this native Node file is
// PREPARED but not claimed run in a clean checkout until Codex T025.
const test=require("node:test");
const assert=require("node:assert/strict");
const fs=require("node:fs");
const path=require("node:path");
const {assess,GATES}=require("../src/politics_fantasy/release_guard.cjs");
const ROOT=path.resolve(__dirname,"..");
const read=(p)=>JSON.parse(fs.readFileSync(path.join(ROOT,p),"utf8"));
const clone=(x)=>JSON.parse(JSON.stringify(x));
const input=()=>[
  read("product/release_gates_v1_20261028.json"),
  read("product/progress_scope_v4_20261027.json"),
  read("ab_atlas/ACHIEVEMENTS_REGISTRY.json")
];
function attemptedEvidence(manifest){
  for(const g of manifest.gates){
    g.status="PASS";
    const id=GATES.find(x=>x.id===g.id);
    g.attestation={verifier_role:id.role,commit_sha:"a".repeat(40),
      evidence_ref:"TEST_ONLY_NOT_ACTUAL_VERIFIED",reviewed_at:"2026-10-28"};
  }
}
test("V4 real baseline is 0/6 with five currently admitted achievements",()=>{
  const [m,s,a]=input(),x=assess(m,s,a);
  assert.equal(x.ready,false);assert.equal(x.six_gates_passed,0);
  assert.equal(x.achievements_unlocked,5);assert.equal(x.milestones,36);
});
test("invented 100% V4 and 90 badges cannot make release ready",()=>{
  const [m,s,a]=input();
  for(const t of s.tracks) for(const x of t.milestones)x.level=5;
  for(const x of a.achievements)x.status="unlocked";
  assert.equal(assess(m,s,a).ready,false);
});
test("forged PASS labels and attestation fields do not verify themselves",()=>{
  const [m,s,a]=input();
  for(const t of s.tracks)for(const x of t.milestones)x.level=5;
  attemptedEvidence(m);
  const x=assess(m,s,a);
  assert.equal(x.ready,false);assert.equal(x.six_gates_passed,0);
});
test("negative external review keeps release blocked",()=>{
  const [m,s,a]=input();
  for(const t of s.tracks)for(const x of t.milestones)x.level=5;
  attemptedEvidence(m);assert.equal(assess(m,s,a,()=>false).ready,false);
});
test("scope revision must remain current V4",()=>{
  const [m,s,a]=input();s.revision=9;assert.equal(assess(m,s,a).ready,false);
});
test("missing one of six gates fails shut",()=>{
  const [m,s,a]=input();m.gates.pop();
  assert.ok(assess(m,s,a).gates.some(x=>x.reasons.includes("MISSING_GATE")));
});
test("duplicate gate cannot silently override evidence",()=>{
  const [m,s,a]=input();m.gates.push(clone(m.gates[0]));
  assert.throws(()=>assess(m,s,a),/INVALID_OR_DUPLICATE_GATE/);
});
test("missing core registry milestone blocks the release",()=>{
  const [m,s,a]=input();s.tracks[0].milestones=s.tracks[0].milestones.filter(x=>x.id!=="src.registry");
  assert.equal(assess(m,s,a).ready,false);
});
test("positive trust-boundary injection proves control flow only, NOT authentication",()=>{
  const [m,s,a]=input();
  for(const t of s.tracks)for(const x of t.milestones)x.level=5;
  attemptedEvidence(m);
  const x=assess(m,s,a,()=>true); // artificial TEST-ONLY callback
  assert.equal(x.ready,true);
  assert.match(x.warning,/independently trusted/i);
});
