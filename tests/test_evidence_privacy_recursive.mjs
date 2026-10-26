import {test} from "node:test";
import {strict as assert} from "node:assert";
import * as E from "../src/politics_fantasy/evidence_warehouse.mjs";
const time="2026-10-26T12:00:00Z",pub="2026-01-01T00:00:00Z";
function sample(){
 const r=E.empty();E.source(r,{id:"TEST:s",kind:"SYNTHETIC",state:"TEST_FIXTURE",
 url:"https://fixture.example/public",observed_at:time,first_public_at:pub,rights:"SYNTHETIC"});
 E.entity(r,{id:"TEST:party",name:"Partido ficticio",type:"PARTY",source_id:"TEST:s"});
 return r;
}
function act(r,opts={}){
 return E.event(r,{id:"TEST:event",type:"PUBLIC_DEBATE",occurred_on:"2026-02-01",
  source_id:"TEST:s",observed_at:time,first_public_at:pub,
  participants:[{actor_id:"TEST:party",role:"ISSUER"}],...opts});
}
test("nested event participant politically-sensitive guess is rejected",()=>{
 const r=sample();
 assert.throws(()=>act(r,{participants:[{actor_id:"TEST:party",role:"ISSUER",
  metadata:{party_member_guess:true}}]}),/UNSAFE_EVENT/);
 assert.equal(r.events.length,0);
});
test("nested role payload with private contact key rejected",()=>{
 const r=sample();
 assert.throws(()=>E.role(r,{id:"TEST:r",type:"CIVIC_ORGANIZER",subject_id:"TEST:party",
 source_id:"TEST:s",observed_at:time,first_public_at:pub,
 valid_from:"2026-01-01",valid_to:null,
 other:{contact:{private_email:"private@example.invalid"}}}),/UNSAFE_ROLE/);
 assert.equal(r.roles.length,0);
});
test("nested source with personal political profile rejected",()=>{
 const r=E.empty();
 assert.throws(()=>E.source(r,{id:"TEST:s",kind:"SYNTHETIC",state:"TEST_FIXTURE",
 url:"https://fixture.example/x",observed_at:time,first_public_at:pub,rights:"SYNTHETIC",
 metadata:{voter_profile:{political_views:"X"}}}),/UNSAFE_SOURCE/);
});
test("JSON prototype pollution key rejected even when nested",()=>{
 const r=sample();
 const bad=JSON.parse('{"actor_id":"TEST:party","role":"ISSUER","__proto__":{"polluted":true}}');
 assert.throws(()=>act(r,{participants:[bad]}),/UNSAFE_EVENT/);
});
test("cyclic untrusted payload rejected deterministically",()=>{
 const r=sample();let cyclic={};cyclic.self=cyclic;
 assert.throws(()=>act(r,{metadata:cyclic}),/UNSAFE_EVENT/);
});
test("legitimate public event still accepted with documented roles",()=>{
 const r=sample();act(r);
 assert.equal(r.events.length,1);
 assert.deepEqual(r.events[0].participants,[{actor_id:"TEST:party",role:"ISSUER"}]);
});
