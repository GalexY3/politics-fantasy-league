/* PF-BR20H: 20 full-cycle acceptance endpoints. All actors here are FICTIONAL.
 * In Node: node --test tests/test_political_universe.mjs
 */
import {test} from "node:test";
import * as universe from "../src/politics_fantasy/political_universe.mjs";

export function buildTests(u){
 const eq=(a,b,msg="not equal")=>{if(a!==b)throw Error(msg+": "+a+" != "+b)};
 const ok=(x,msg="expected truthy")=>{if(!x)throw Error(msg)};
 const reject=(fn,regex)=>{let err=null;try{fn()}catch(e){err=e};if(!err || !regex.test(err.message))throw Error("Expected rejection "+regex+"; got "+err)};
 const date="2026-10-25T16:00:00Z",pub="2026-01-10T12:00:00Z",year="2026-01-01";
 const base=()=>{
  const reg=u.createRegistry();
  u.addSource(reg,{id:"S_DOC",kind:"OFFICIAL",state:"DOCUMENTED_ONLY",url:"https://fixture.example/metadata",observed_at:date,license:null});
  u.addSource(reg,{id:"S_OFF",kind:"OFFICIAL",state:"FIXTURE",url:"https://fixture.example/official",observed_at:date,license:"TEST ONLY"});
  u.addSource(reg,{id:"S_NEWS",kind:"FIXTURE",state:"FIXTURE",url:"https://fixture.example/story",observed_at:date,license:"TEST ONLY"});
  const put=(id,kind,name,source_id="S_OFF")=>u.addActor(reg,{id,kind,name,source_id,public_role_documented:true,jurisdiction:"ES"});
  put("TEST:p_a","PARTY","Partido Horizonte");put("TEST:p_b","PARTY","Partido Esfera");
  put("TEST:p_c","PARTY","Partido Bosque");put("TEST:coal","COALITION","Coalición Tres Vías");
  put("TEST:group","ELECTORS_GROUP","Agrupación Vecinal Ficticia");
  put("TEST:civic","CIVIC_PLATFORM","Asociación Plataforma Imaginaria");
  put("TEST:inst","PUBLIC_BODY","Asamblea Inventada");
  put("TEST:person1","PERSON","Nia Ficticia");
  put("TEST:person2","PERSON","Tomás Ejemplo");
  put("TEST:person3","PERSON","Nia Ficticia");
  return reg;
 };
 const add=(r,id,relation,subject_id,object_id=null,extras={})=>u.addClaim(r,{id,relation,subject_id,object_id,source_id:"S_OFF",valid_from:year,valid_to:null,observed_at:date,first_public_at:pub,...extras});
 return [
 {id:"C01",run:()=>{const r=base();eq(r.sources.length,3);eq(r.sources[0].state,"DOCUMENTED_ONLY");reject(()=>u.addSource(r,{id:"missinghash",kind:"OFFICIAL",state:"RAW_CAPTURED",url:"https://fixture.example/raw",observed_at:date,license:null}),/RAW_NEEDS_SHA256/);}},
 {id:"C02",run:()=>{const r=base();u.addActor(r,{id:"TEST:lobby",kind:"INTEREST_GROUP",name:"Mesa Documentada Ficticia",source_id:"S_OFF",jurisdiction:"ES"});eq(new Set(r.actors.map(a=>a.kind)).size,7);ok(r.actors.some(a=>a.kind==="INTEREST_GROUP"));ok(r.actors.some(a=>a.kind==="ELECTORS_GROUP"));ok(!r.actors.some(a=>a.kind==="GOVERNING_PARTY"));}},
 {id:"C03",run:()=>{const r=base();const p=r.actors.find(a=>a.id==="TEST:person2");ok(p.public_role_documented);eq(u.representation(r,"TEST:p_c"),"UNKNOWN");eq(u.minimalParliamentaryBaseline(r).represented_person_count,0);}},
 {id:"C04",run:()=>{const r=base();const q=u.resolveIdentity(r,{authority:"OTHER",external_id:"nia",name:"Nia Ficticia"});eq(q.status,"UNRESOLVED_HOMONYM");eq(q.candidate_count,2);eq(r.actors.length,10);}},
 {id:"C05",run:()=>{eq(u.stableId("RPP","abc-1"),"RPP:abc-1");reject(()=>u.stableId("RPP",""),/BAD_EXTERNAL_ID/);const r=base();eq(u.resolveIdentity(r,{authority:"TEST",external_id:"person1",name:"OTHER"}).status,"EXACT_ID_MATCH");}},
 {id:"C06",run:()=>{const r=base();reject(()=>u.addClaim(r,{id:"orphan",relation:"PUBLIC_SPOKESPERSON",subject_id:"TEST:person1",source_id:"UNKNOWN",valid_from:year,observed_at:date}),/MISSING_SOURCES/);}},
 {id:"C07",run:()=>{const r=base();const x=add(r,"c_date","PUBLIC_ADVOCACY","TEST:person1",null,{valid_from:"2025-01-01"});eq(x.valid_from,"2025-01-01");eq(x.observed_at,date);reject(()=>add(r,"late","PUBLIC_ADVOCACY","TEST:person1",null,{observed_at:"2027-01-01T00:00:00Z"}),/CLAIM_AFTER_SOURCE_CAPTURE/);}},
 {id:"C08",run:()=>{const r=base();add(r,"role_old","DOCUMENTED_LEADERSHIP","TEST:person2","TEST:p_a",{valid_from:"2024-01-01",valid_to:"2025-01-01"});add(r,"role_new","PUBLIC_SPOKESPERSON","TEST:person2","TEST:p_b",{valid_from:"2025-01-01",valid_to:null});eq(u.roleAt(r,"TEST:person2","2024-12-31").length,1);eq(u.roleAt(r,"TEST:person2","2025-01-01").length,1);eq(u.roleAt(r,"TEST:person2","2025-01-01")[0].object_id,"TEST:p_b");}},
 {id:"C09",run:()=>{const r=base();add(r,"candidate","CANDIDATE_FOR","TEST:person1","TEST:group");eq(r.claims.length,1);ok(!r.claims.some(x=>x.relation==="REGISTERED_PARTY"&&x.subject_id==="TEST:person1"));reject(()=>add(r,"private","REGISTERED_PARTY","TEST:person1","TEST:p_a"),/PRIVATE_MEMBERSHIP/);}},
 {id:"C10",run:()=>{const r=base();for(const [i,p] of ["TEST:p_a","TEST:p_b","TEST:p_c"].entries())add(r,"coal"+i,"COALITION_MEMBER",p,"TEST:coal");eq(r.claims.length,3);eq(new Set(r.claims.map(x=>x.subject_id)).size,3);}},
 {id:"C11",run:()=>{const r=base();add(r,"policy","DECLARED_POLICY_POSITION","TEST:p_a",null,{issue:"transporte",exact_statement:"Defendemos un nuevo servicio de autobuses."});eq(u.issueClaims(r,"transporte").length,1);ok(!("left_right" in r.claims[0]));reject(()=>add(r,"bad","DECLARED_POLICY_POSITION","TEST:p_b",null,{issue:"transporte",exact_statement:"A",ideology_score:90}),/BAD_CLAIM|NO_IDEOLOGICAL_COORDINATES/);}},
 {id:"C12",run:()=>{const r=base();u.addEvent(r,{id:"event1",kind:"PUBLIC_MEETING",source_id:"S_NEWS",occurred_on:"2026-01-10",observed_at:date,first_public_at:pub,participants:[{actor_id:"TEST:person2",role:"SPEAKER"},{actor_id:"TEST:civic",role:"ORGANIZER"}]});eq(r.events.length,1);eq(r.events[0].kind,"PUBLIC_MEETING");}},
 {id:"C13",run:()=>{const r=base();reject(()=>u.addEvent(r,{id:"ev",kind:"PUBLIC_DEBATE",source_id:"S_NEWS",occurred_on:"2026-01-10",observed_at:date,first_public_at:pub,participants:[{actor_id:"TEST:person1",role:"SPEAKER"}],influence_score:0.95}),/BAD_EVENT/);}},
 {id:"C14",run:()=>{const r=base();reject(()=>u.addActor(r,{id:"TEST:private",kind:"PERSON",name:"Ciudadano privado",source_id:"S_OFF",public_role_documented:false}),/PRIVATE_PERSON_EXCLUDED/);reject(()=>u.addActor(r,{id:"TEST:contact",kind:"PERSON",name:"Ficticio",source_id:"S_OFF",public_role_documented:true,private_email:"a@b.es"}),/BAD_ACTOR/);}},
 {id:"C15",run:()=>{const r=base();add(r,"seat_yes","SEAT_STATUS","TEST:p_a",null,{value:"PRESENT",election_id:"E2026"});add(r,"seat_no","SEAT_STATUS","TEST:p_a",null,{value:"ABSENT",election_id:"E2026"});eq(r.claims.length,2);eq(u.representation(r,"TEST:p_a"),"CONFLICT_REVIEW_REQUIRED");add(r,"old_seat","SEAT_STATUS","TEST:p_b",null,{value:"PRESENT",election_id:"E2025",valid_from:"2025-01-01",valid_to:"2026-01-01"});add(r,"new_no_seat","SEAT_STATUS","TEST:p_b",null,{value:"ABSENT",election_id:"E2026",valid_from:"2026-01-01"});eq(u.representation(r,"TEST:p_b"),"HISTORICAL_STATUS_DATE_REQUIRED");eq(u.representation(r,"TEST:p_b","2027-01-01T00:00:00Z"),"ABSENT");}},
 {id:"C16",run:()=>{const r=base();u.addSource(r,{id:"S_EARLY",kind:"FIXTURE",state:"FIXTURE",url:"https://fixture.example/early",observed_at:"2026-03-01T00:00:00Z",license:"TEST ONLY"});add(r,"old","DOCUMENTED_LEADERSHIP","TEST:person2","TEST:p_a",{source_id:"S_EARLY",observed_at:"2026-03-01T00:00:00Z",first_public_at:"2026-02-01T00:00:00Z"});add(r,"new","DOCUMENTED_LEADERSHIP","TEST:person1","TEST:p_b",{first_public_at:"2026-09-01T00:00:00Z"});eq(u.timeView(r,"2026-06-01T00:00:00Z").claims.length,1);eq(u.timeView(r,"2026-10-26T00:00:00Z").claims.length,2);}},
 {id:"C17",run:()=>{const r=base();add(r,"speaker","PUBLIC_SPOKESPERSON","TEST:person1","TEST:p_c");const filtered=u.filterActors(r,{kind:"PERSON",relation:"PUBLIC_SPOKESPERSON"});eq(filtered.length,1);eq(filtered[0].name,"Nia Ficticia");}},
 {id:"C18",run:()=>{const r=base();const a=u.coverageAudit(r);eq(a.seatStatus.UNKNOWN,6);eq(a.seatStatus.ABSENT,0);eq(a.actorTypes.PARTY,3);eq(a.actorTypes.PERSON,3);}},
 {id:"C19",run:()=>{const r=base();const g=u.realityScoringGate(r,"TEST:person1");eq(g.eligible,false);eq(g.reason,"INDIVIDUAL_POLITICAL_RATING_NOT_ENABLED");}},
 {id:"C20",run:()=>{const r=base();add(r,"nomination","CANDIDATE_FOR","TEST:person1","TEST:group");add(r,"spoke","PUBLIC_SPOKESPERSON","TEST:person2","TEST:p_a");add(r,"seat","SEAT_STATUS","TEST:p_a",null,{value:"PRESENT",election_id:"E2026"});u.addEvent(r,{id:"e",kind:"PUBLIC_STATEMENT",source_id:"S_OFF",occurred_on:"2026-01-10",observed_at:date,first_public_at:pub,participants:[{actor_id:"TEST:person2",role:"SPEAKER"}]});eq(u.validateRegistry(r).valid,true);eq(u.minimalParliamentaryBaseline(r).nonseat_public_person_count,3);eq(u.coverageAudit(r).seatStatus.UNKNOWN,5);eq(u.timeView(r,"2026-10-26T00:00:00Z").events.length,1);}}
 ];
}
for(const c of buildTests(universe))test("PF-BR20H-"+c.id,c.run);
