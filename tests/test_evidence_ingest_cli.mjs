import {test} from "node:test";
import {strict as assert} from "node:assert";
import {spawnSync} from "node:child_process";
import {mkdtempSync,writeFileSync,rmSync,readFileSync} from "node:fs";
import {tmpdir} from "node:os";
import {join} from "node:path";
import {createHash} from "node:crypto";
import {fileURLToPath} from "node:url";
const script=fileURLToPath(new URL("../scripts/ingest_political_evidence.mjs",import.meta.url));
const fixture=fileURLToPath(new URL("../examples/actor_evidence_fixture_30j.json",import.meta.url));
const node=(...args)=>spawnSync(process.execPath,[script,...args],{encoding:"utf8",timeout:10000});
test("real CLI processes fictional actor bundle without exposing personal names",()=>{
 const run=node(fixture,"--as-of","2026-05-01T00:00:00Z");
 assert.equal(run.status,0,run.stderr);
 const out=JSON.parse(run.stdout);
 assert.equal(out.audit.ok,true);
 assert.equal(out.audit.coverage.registered_entities,7);
 assert.equal(out.as_of.events_visible,1);
 assert.equal(out.original_publisher_authenticated,false);
 assert.equal(out.real_people_scoring_enabled,false);
 assert.ok(!run.stdout.includes("Alma Imaginaria"));
});
test("CLI fails closed on unsupported class or invalid first-public evidence",()=>{
 const dir=mkdtempSync(join(tmpdir(),"pf30j-"));
 try{
 const p=join(dir,"bad.json");writeFileSync(p,JSON.stringify({dataset_class:"REAL_VERIFIED",sources:[]}));
 const result=node(p);assert.notEqual(result.status,0);assert.match(result.stderr,/UNKNOWN_EVIDENCE_CLASS/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test("CLI recomputes SHA256 on local input bytes; rejects deliberately wrong hash",()=>{
 const dir=mkdtempSync(join(tmpdir(),"pf30j-"));
 try{
 const raw=join(dir,"original.dat"),payload=join(dir,"bundle.json"),bytes=Buffer.from("PUBLIC_SAMPLE_SOURCE_NOT_AN_OFFICIAL_CERTIFICATE","utf8");
 writeFileSync(raw,bytes);
 const h=createHash("sha256").update(bytes).digest("hex");
 const source={id:"TEST:raw",kind:"SECONDARY",state:"RAW_CAPTURED",url:"https://fixture.example/source",
 observed_at:"2026-10-26T00:00:00Z",first_public_at:null,rights:"UNKNOWN",raw_relpath:"original.dat",sha256_expected:h};
 writeFileSync(payload,JSON.stringify({dataset_class:"ORIGINAL_SNAPSHOT_UNCERTIFIED",sources:[source],entities:[],roles:[],events:[],claims:[]}));
 const good=node(payload);assert.equal(good.status,0,good.stderr);
 const out=JSON.parse(good.stdout);assert.equal(out.source_captures[0].sha256,h);
 assert.equal(out.original_publisher_authenticated,false);
 source.sha256_expected="a".repeat(64);
 writeFileSync(payload,JSON.stringify({dataset_class:"ORIGINAL_SNAPSHOT_UNCERTIFIED",sources:[source]}));
 const bad=node(payload);assert.notEqual(bad.status,0);assert.match(bad.stderr,/RAW_SHA256_DISAGREEMENT/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
test("CLI rejects raw attachment that escapes bundle directory",()=>{
 const dir=mkdtempSync(join(tmpdir(),"pf30j-"));
 try{
 const payload=join(dir,"bundle.json");
 writeFileSync(payload,JSON.stringify({dataset_class:"ORIGINAL_SNAPSHOT_UNCERTIFIED",
 sources:[{id:"TEST:raw",kind:"SECONDARY",state:"RAW_CAPTURED",url:"https://fixture.example/raw",
 observed_at:"2026-10-26T00:00:00Z",rights:"UNKNOWN",raw_relpath:"../../etc/hosts",sha256_expected:"a".repeat(64)}]}));
 const result=node(payload);assert.notEqual(result.status,0);
 assert.match(result.stderr,/RAW_FILE_ESCAPES_BUNDLE_DIRECTORY|ENOENT/);
 }finally{rmSync(dir,{recursive:true,force:true})}
});
