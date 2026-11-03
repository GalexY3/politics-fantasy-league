/* R25: synthetically demonstrate false rights from self-asserted bundle fields. */
import {test} from "node:test";
import {strict as assert} from "node:assert";
import {spawnSync} from "node:child_process";
import {createHash} from "node:crypto";
import {mkdtempSync,writeFileSync,rmSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {fileURLToPath} from "node:url";
import * as W from "../src/politics_fantasy/evidence_warehouse.mjs";

function rawSyntheticClaim(){
 const reg=W.empty();
 W.source(reg,{id:"TEST:asset",kind:"OFFICIAL",state:"RAW_CAPTURED",
  url:"https://fixture.invalid/asset.dat",
  observed_at:"2026-10-31T12:00:00Z",
  first_public_at:"2026-10-30T12:00:00Z",
  rights:"OPEN_LICENSE_VERIFIED",sha256:"a".repeat(64),
  digest_recomputed:true});
 W.entity(reg,{id:"TEST:civic",type:"CIVIL_ORG",name:"Colectivo Ficticio",
  source_id:"TEST:asset"});
 W.event(reg,{id:"TEST:event",type:"PUBLIC_DEBATE",
  source_id:"TEST:asset",occurred_on:"2026-10-20",
  observed_at:"2026-10-31T12:00:00Z",
  first_public_at:"2026-10-30T12:00:00Z",
  participants:[{actor_id:"TEST:civic",role:"SPEAKER"}]});
 return reg;
}

test("a caller's OPEN_LICENSE_VERIFIED is not an authenticated rights witness",()=>{
 const reg=rawSyntheticClaim();
 const gate=W.evidenceGate(reg);
 assert.ok(gate.blockers.includes("RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION"));
 assert.equal(gate.read_only_aggregate_display_allowed,false);
 assert.equal(gate.can_score_real_people,false);
 assert.equal(gate.can_publish_field_people,false);
});

test("as-of evidence cannot treat raw, unverified timestamps as independently known",()=>{
 const reg=rawSyntheticClaim();
 const historical=W.asOf(reg,"2026-10-31T12:00:01Z");
 assert.equal(historical.source_count,0);
 assert.equal(historical.events.length,0);
});

test("fully fictional test fixture continues to work for synthetic comparisons",()=>{
 const reg=W.empty();
 W.source(reg,{id:"TEST:fixture",kind:"SYNTHETIC",state:"TEST_FIXTURE",
  url:"https://fixture.invalid/test",
  observed_at:"2026-10-31T12:00:00Z",
  first_public_at:"2026-10-30T12:00:00Z",rights:"SYNTHETIC"});
 assert.equal(W.asOf(reg,"2026-10-31T12:00:01Z").source_count,1);
 assert.equal(W.evidenceGate(reg).read_only_aggregate_display_allowed,true);
});

test("unknown rights stay blocked without release on another source",()=>{
 const reg=rawSyntheticClaim();
 reg.sources[0].rights="UNKNOWN";
 assert.ok(W.evidenceGate(reg).blockers.includes("RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION"));
 assert.equal(W.asOf(reg,"2026-10-31T12:00:01Z").source_count,0);
});

test("real CLI path checks SHA but does not certify rights or historic visibility",()=>{
 const temp=mkdtempSync(join(tmpdir(),"pfl-r25-"));
 try{
  const data=Buffer.from("ENTIRELY_SYNTHETIC_NOT_AN_ORIGINAL");
  const sha=createHash("sha256").update(data).digest("hex");
  writeFileSync(join(temp,"asset.dat"),data);
  const json={dataset_class:"ORIGINAL_SNAPSHOT_UNCERTIFIED",
    sources:[{id:"TEST:asset",kind:"OFFICIAL",state:"RAW_CAPTURED",
      url:"https://fixture.invalid/asset.dat",
      observed_at:"2026-10-31T12:00:00Z",
      first_public_at:"2026-10-30T12:00:00Z",
      rights:"OPEN_LICENSE_VERIFIED",raw_relpath:"asset.dat",
      sha256_expected:sha}],entities:[],roles:[],events:[],claims:[]};
  const input=join(temp,"bundle.json");writeFileSync(input,JSON.stringify(json));
  const script=fileURLToPath(new URL("../scripts/ingest_political_evidence.mjs",import.meta.url));
  const run=spawnSync(process.execPath,[script,input,"--as-of","2026-10-31T12:00:01Z"],
    {encoding:"utf8",timeout:10000});
  assert.equal(run.status,0,run.stderr);
  const result=JSON.parse(run.stdout);
  assert.equal(result.original_publisher_authenticated,false);
  assert.equal(result.as_of.sources_available,0);
  assert.equal(result.audit.gate.read_only_aggregate_display_allowed,false);
  assert.ok(result.audit.gate.blockers.includes("RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION"));
 }finally{rmSync(temp,{recursive:true,force:true})}
});
