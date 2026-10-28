"use strict";
/**
 * Release policy guard for PFL. No network and no external dependencies.
 * Fail CLOSED unless all six gates have verified evidence from an independent
 * verifier supplied by the host (not a flag in the user-writable manifest).
 * No actual verification of signatures is built into this module.
 * No person-level scoring is authorized by a READY result; DPO approval separate.
 */
const GATES = Object.freeze([
  {id:"G01_REGISTRY_RIGHTS", milestones:["src.registry","sec.rights"], min:4, role:"data-rights"},
  {id:"G02_REAL_IDENTITY", milestones:["id.real","id.temporal"], min:4, role:"identity-auditor"},
  {id:"G03_REAL_EVENTS", milestones:["ev.person","ev.extra"], min:4, role:"source-auditor"},
  {id:"G04_MULTIUSER_AUTH", milestones:["sec.auth","sec.ops"], min:4, role:"security-auditor"},
  {id:"G05_E2E_ACTUAL", milestones:["qa.endtoend","qa.independent","ui.flow"], min:4, role:"qa-independent"},
  {id:"G06_HOSTING_PILOT", milestones:["launch.hosted","launch.pilot"], min:4, role:"ops-independent"},
]);
const SHA=/^[a-f0-9]{40}$/;
function assess(manifest, scope, registry, verifyEvidence=()=>false) {
  if(!manifest || typeof manifest!=="object" || !scope || !registry) throw Error("INPUT_REQUIRED");
  const levels=new Map();
  for(const t of scope.tracks||[]) for(const m of t.milestones||[]) {
    if(levels.has(m.id)) throw Error("DUPLICATE_MILESTONE:"+m.id);
    if(!Number.isInteger(m.level)||m.level<0||m.level>5) throw Error("INVALID_MATURITY:"+m.id);
    levels.set(m.id,m.level);
  }
  const ach=(registry.achievements||[]).filter(a=>a.status!=="retired");
  const badges=ach.filter(a=>a.status==="unlocked").length;
  const manifestRows=manifest.gates||[];
  const byId=new Map();
  for(const x of manifestRows){
    if(!x || !GATES.some(g=>g.id===x.id) || byId.has(x.id)) throw Error("INVALID_OR_DUPLICATE_GATE");
    byId.set(x.id,x);
  }
  const results=GATES.map(spec=>{
    const row=byId.get(spec.id);
    const failed=[];
    if(!row) failed.push("MISSING_GATE");
    for(const key of spec.milestones) if((levels.get(key)??-1)<spec.min) failed.push("MILESTONE:"+key);
    if(!row || row.status!=="PASS") failed.push("NOT_PASS");
    const e=row?.attestation;
    if(!e || e.verifier_role!==spec.role || !SHA.test(String(e.commit_sha||"")) ||
       typeof e.evidence_ref!=="string" || !e.evidence_ref.trim() ||
       typeof e.reviewed_at!=="string" || !/^\\d{4}-\\d{2}-\\d{2}/.test(e.reviewed_at)){
      failed.push("MISSING_ATTESTATION_FIELDS");
    } else {
      // An in-repo claim alone is NOT sufficient. External verifier must
      // validate bytes, role, evidence and commit independently.
      let authenticated=false;
      try{authenticated=verifyEvidence(spec,e)===true;}catch(_){authenticated=false;}
      if(!authenticated)failed.push("INDEPENDENT_VERIFICATION_REQUIRED");
    }
    return {id:spec.id,passed:failed.length===0,reasons:failed};
  });
  const scopeOk=scope.revision===4 && scope.scope_id==="PFL-V1-20261026";
  const manifestOk=manifest.schema==="pfl.release_gates.v1" && manifest.mode==="PUBLIC_NAMED_PERSON";
  const ready=scopeOk && manifestOk && results.every(r=>r.passed);
  return {
    schema:"pfl.release_assessment.v1",mode:manifest.mode||null,ready,
    release_state:ready?"ELIGIBLE_FOR_FINAL_HUMAN_SIGNOFF":"BLOCKED",
    six_gates_passed:results.filter(r=>r.passed).length,gate_count:6,
    scope_consistent:scopeOk,manifest_consistent:manifestOk,
    achievements_unlocked:badges,achievements_active:ach.length,
    milestones:levels.size,gates:results,
    warning:"Structural check only. Verified evidence callback must be independently trusted. READY never substitutes legal/DPO release approval."
  };
}
module.exports={assess,GATES};
if (require.main===module) {
  const fs=require("node:fs");
  const [manifestFile,scopeFile,registryFile]=process.argv.slice(2);
  if(!manifestFile||!scopeFile||!registryFile) {
    process.stderr.write("Usage: node release_guard.cjs manifest.json progress_scope_v4.json ACHIEVEMENTS_REGISTRY.json\n");
    process.exitCode=2;
  } else {
    const load=p=>JSON.parse(fs.readFileSync(p,"utf8"));
    const result=assess(load(manifestFile),load(scopeFile),load(registryFile));
    process.stdout.write(JSON.stringify(result,null,2)+"\n");
    process.exitCode=result.ready?0:3; // fail-closed: no external verifier in CLI
  }
}
