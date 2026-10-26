/* PF-BR30J — engineering and data-source feasibility AB acceptance suite.
 * node --test tests/test_evidence_warehouse.mjs
 * This suite is NOT 30 independent tests of influence or political behavior.
 */
import {test} from "node:test";
import {readFileSync} from "node:fs";
import * as W from "../src/politics_fantasy/evidence_warehouse.mjs";
export function suite(W,fixture,catalogue,serverSource){
 const yes=(x,m="FAILED_ASSERTION")=>{if(!x)throw Error(m)};
 const eq=(a,b)=>yes(JSON.stringify(a)===JSON.stringify(b),"EXPECTED_"+JSON.stringify(b)+"_GOT_"+JSON.stringify(a));
 const rejects=(f,regex)=>{let error=null;try{f()}catch(e){error=e.message}yes(error!==null,"EXPECTED_REJECTION");if(regex)yes(regex.test(error),"BAD_REJECTION_"+error)};
 const early="2026-04-01T00:00:00Z",late="2026-10-26T00:00:00Z";
 const populated=()=>{const r=W.empty();for(const z of fixture.sources)W.source(r,z);for(const z of fixture.entities)W.entity(r,z);for(const z of fixture.roles)W.role(r,z);for(const z of fixture.events)W.event(r,z);for(const z of fixture.claims)W.claim(r,z);return r};
 const raw=()=>{const r=W.empty();W.source(r,{id:"TEST:source",kind:"OFFICIAL",state:"DOCUMENTED_ONLY",url:"https://fixture.invalid/example",observed_at:late,rights:"UNKNOWN",first_public_at:null});return r};
 const src=(r,id="TEST:case",observed_at=late,first_public_at="2026-10-20T00:00:00Z")=>W.source(r,{id,kind:"SYNTHETIC",state:"TEST_FIXTURE",url:"https://fixture.invalid/"+id,observed_at,first_public_at,rights:"SYNTHETIC"});
 const add=(r,id,type="PARTY",name="Ficticia")=>W.entity(r,{id,type,name,source_id:"TEST:case",public_role_documented:true});
 const role=(r,id,type,subject_id,object_id=null,ext={})=>W.role(r,{id,type,subject_id,object_id,valid_from:"2026-01-01",valid_to:null,source_id:"TEST:case",observed_at:late,first_public_at:"2026-10-20T00:00:00Z",...ext});
 const ev=(r,id,type,actor_id,ext={})=>W.event(r,{id,type,occurred_on:"2026-09-01",source_id:"TEST:case",observed_at:late,first_public_at:"2026-10-20T00:00:00Z",participants:[{actor_id,role:"SPEAKER"}],...ext});
 const t=[
 ["S01","Registry metadata has no actual captured raw parties",()=>{const x=catalogue.source_registry.find(x=>x.id==="RPP");yes(x.metadata_only&&x.download_verified===false&&x.first_public_at_for_rows===null)}],
 ["S02","Interior elected officials catalogue is not an ingested roster",()=>{const x=catalogue.source_registry.find(x=>x.id==="INTERIOR_NATIONAL");yes(x.metadata_only&&x.delivery==="XLSX links")}],
 ["S03","JEC candidates are separate from juridical party registration",()=>{const x=catalogue.source_registry.find(x=>x.id==="JEC_CANDIDACIES");yes(x.scope.includes("distinct from registered parties"))}],
 ["S04","At least one official municipal source other than national Congress",()=>{const x=catalogue.source_registry.filter(x=>/BIZKAIA_MUNICIPAL|JEC_MUNICIPAL_BOE/.test(x.id));eq(x.length,2);yes(x.every(v=>v.metadata_only===true))}],
 ["S05","RAW source fails without recomputed SHA256",()=>{const r=W.empty();rejects(()=>W.source(r,{id:"TEST:raw",kind:"OFFICIAL",state:"RAW_CAPTURED",url:"https://fixture.invalid/raw",observed_at:late,rights:"UNKNOWN",sha256:"b".repeat(64)}),/RAW_REQUIRES_RECOMPUTED_DIGEST/)}],
 ["S06","Catalog-only source cannot back a political actor",()=>{const r=raw();rejects(()=>W.entity(r,{id:"TEST:org",type:"PARTY",name:"Ficticia",source_id:"TEST:source"}),/ENTITY_NEEDS_CAPTURED_EVIDENCE/)}],
 ["S07","Unknown rights do not pass reuse gate",()=>{const r=W.empty();W.source(r,{id:"TEST:source",kind:"OFFICIAL",state:"RAW_CAPTURED",url:"https://fixture.invalid/raw",observed_at:late,rights:"UNKNOWN",sha256:"a".repeat(64),digest_recomputed:true});const z=W.evidenceGate(r);yes(z.blockers.includes("RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION")&&!z.can_publish_field_people)}],
 ["S08","Source revisions retained under distinct IDs, duplicates rejected",()=>{const r=W.empty();src(r);src(r,"TEST:case_v2");eq(r.sources.length,2);rejects(()=>src(r),/DUPLICATE_SOURCE/)}],
 ["I09","Stable name-independent exact namespace ID resolution",()=>{const r=W.empty();src(r);add(r,"TEST:abc");eq(W.resolve(r,{id:"TEST:abc",name:"Otro"}).status,"EXACT_NAMESPACE_ID")}],
 ["I10","Homonym names remain unresolved without external ID",()=>{const r=W.empty();src(r);add(r,"TEST:a","PARTY","Duplicado");add(r,"TEST:b","PARTY","Duplicado");const q=W.resolve(r,{id:"TEST:c",name:"Duplicado"});eq(q.status,"AMBIGUOUS_NAME");eq(q.candidates,2);eq(r.collisions.length,1)}],
 ["I11","Coalition only has members when an explicit role is sourced",()=>{const r=W.empty();src(r);add(r,"TEST:p");add(r,"TEST:coal","COALITION");eq(r.roles.length,0);role(r,"TEST:relation","COALITION_PARTICIPANT","TEST:p","TEST:coal");eq(r.roles.length,1)}],
 ["I12","Candidacy does not silently create party membership",()=>{const r=populated();yes(r.roles.some(x=>x.type==="PUBLIC_CANDIDATE"));yes(!r.roles.some(x=>x.type==="PRIVATE_PARTY_MEMBERSHIP"));eq(r.entities.filter(x=>x.type==="PERSON_PUBLIC").length,1)}],
 ["I13","Effective intervals exclude expired spokesperson role",()=>{const r=populated();eq(W.rolesAt(r,"TEST:actor","2026-03-01").length,2);eq(W.rolesAt(r,"TEST:actor","2026-09-01").length,1)}],
 ["I14","Seat status is unknown without official dated claim",()=>{const r=populated();eq(W.officeStatus(r,"TEST:party_a","2026-07-01"),"UNKNOWN")}],
 ["E15","Non-parliament public debate with documented participants",()=>{const r=populated();const v=r.events[0];eq(v.type,"PUBLIC_DEBATE");eq(v.participants.length,2);yes(v.source_id==="TEST:early")}],
 ["E16","As-of excludes even published fact if source observed later",()=>{const r=populated();eq(W.asOf(r,"2026-03-15T00:00:00Z").events.length,0);eq(W.asOf(r,"2026-05-01T00:00:00Z").events.length,1);eq(W.asOf(r,"2026-10-27T00:00:00Z").events.length,2)}],
 ["E17","No numeric influence scoring accepted",()=>{const r=W.empty();src(r);add(r,"TEST:person","PERSON_PUBLIC","Nombre Inventado");rejects(()=>ev(r,"TEST:bad","PUBLIC_APPEARANCE","TEST:person",{influence_score:0.95}),/UNSAFE_EVENT/)}],
 ["E18","Civic platform may organize events without parliamentary seat",()=>{const r=populated();yes(r.events[0].participants.some(p=>p.actor_id==="TEST:civic"));eq(W.officeStatus(r,"TEST:civic","2026-02-01"),"UNKNOWN")}],
 ["E19","Public event corrections retain both versions",()=>{const r=populated();eq(r.events.length,2);eq(r.events[1].amendment_of,"TEST:debate");yes(r.events[0].id!==r.events[1].id)}],
 ["E20","Duplicate external event IDs trigger review, not double-count assumption",()=>{const r=populated();const d=W.eventDuplicates(r);eq(d.length,1);eq(d[0].event_ids.length,2);yes(d[0].needs_review)}],
 ["E21","Ordinary private person records rejected",()=>{const r=W.empty();src(r);rejects(()=>W.entity(r,{id:"TEST:private",type:"PERSON_PUBLIC",name:"Private",source_id:"TEST:case",public_role_documented:false}),/NO_PRIVATE_PERSON/)}],
 ["M22","Coverage denominator remains unknown",()=>{const r=populated();const c=W.coverage(r);eq(c.known_population_denominator,null);eq(c.coverage_rate,null)}],
 ["M23","Coverage stratified by actor and source type, without ranking",()=>{const r=populated();const c=W.coverage(r);eq(c.registered_entities,7);eq(c.by_type.PARTY,2);eq(c.sources_by_kind.SYNTHETIC,2);yes(!Object.hasOwn(c,"influence_score"))}],
 ["M24","Absent office claims not inferred from public events",()=>{const r=populated();yes(r.events.length>0);eq(W.officeStatus(r,"TEST:actor","2026-03-01"),"UNKNOWN")}],
 ["M25","No longitudinal forecasting without timestamped primary field data",()=>{const r=populated();const g=W.evidenceGate(r);yes(g.blockers.includes("NO_ORIGINAL_RAW_CAPTURED")&&!g.can_infer_influence&&!g.can_score_real_people)}],
 ["M26","Conflicting dated office claims produce review status",()=>{const r=W.empty();src(r);add(r,"TEST:person","PERSON_PUBLIC","Nombre Inventado");const base={type:"OFFICE_STATUS",subject_id:"TEST:person",source_id:"TEST:case",valid_on:"2026-01-01",observed_at:late,first_public_at:"2026-10-20T00:00:00Z"};W.claim(r,{id:"TEST:yes",value:"PRESENT",...base});W.claim(r,{id:"TEST:no",value:"ABSENT",...base});eq(W.officeStatus(r,"TEST:person","2026-01-01"),"CONFLICT_REVIEW_REQUIRED")}],
 ["P27","End-to-end fictional bundle integrity validates all references",()=>{const r=populated();yes(W.auditBundle(r).ok);eq(W.auditBundle(r).event_collisions.length,1);eq(r.events.length,2)}],
 ["P28","Demo exposes aggregate readiness but not personal labels",()=>{yes(serverSource.includes("route == '/api/evidence-readiness'"));yes(serverSource.includes("return self.reply(200,evidence_status())"))}],
 ["P29","30 test cases are registered for standalone Node, with errors reported",()=>{yes(t.length===30);yes(t.every(x=>typeof x[2]==="function"));yes(fixture.dataset_class==="FULLY_FICTIONAL_ENGINEERING_FIXTURE")}],
 ["P30","Conservative readiness reports no real people verified",()=>{const r=populated();const g=W.evidenceGate(r);eq(g.can_publish_field_people,false);eq(g.can_score_real_people,false);eq(W.auditBundle(r).coverage.registered_entities,7)}]
 ];
 return t.map(([id,name,fn])=>({id:"PF-BR30J-"+id,name,run:fn}));
}
const dir=new URL("../",import.meta.url);
const read=p=>readFileSync(new URL(p,dir),"utf8");
const fx=JSON.parse(read("examples/actor_evidence_fixture_30j.json"));
const catalog=JSON.parse(read("research/BRANCH30J_20261026/SOURCE_CATALOGUE.json"));
const server=read("src/politics_fantasy/server.py");
for(const c of suite(W,fx,catalog,server))test(c.id+": "+c.name,c.run);
