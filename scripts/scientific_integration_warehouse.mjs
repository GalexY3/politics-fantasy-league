/* PFL: fixed, server-owned, synthetic-only Python↔Node warehouse consumer.
 * No network, file I/O, user supplied identities, URLs, people or cases.
 * A SHA of these fictitious bytes is a parity check, NOT publisher evidence.
 */
import {createHash} from 'node:crypto';
import {stdin,stdout,stderr} from 'node:process';
import * as W from '../src/politics_fantasy/evidence_warehouse.mjs';

const fakeBytes=Buffer.from('PFL_SYNTHETIC_SCIENTIFIC_INTEGRATION_V1\n','utf8');
const ownSha=createHash('sha256').update(fakeBytes).digest('hex');
const cuts=Object.freeze({early:'2026-10-15T12:00:00Z',late:'2026-11-01T12:00:00Z'});
// Immutable local fixture manifest: a caller's SYNTHETIC label plus a
// self-consistent digest alone must never enroll arbitrary document content.
const registeredFixtureSha=Object.freeze({
 'SYNTHETIC:PAN24':'d15928aaf5bbaceaf74c922662ae6771924d63c3f8457707d8cbc092f6268b86',
 'SYNTHETIC:IAEN24':'ee0abeff47a5ef623aecbfe5f5db26a925777a20e6588f9e700fac44406ff152',
});
const scenarios=new Set(['baseline','rights_spoof','privacy_probe']);
const fail=(message)=>{throw Error(message)};

function run(v){
 if(!v||Array.isArray(v)||typeof v!=='object'||
    Object.keys(v).sort().join(',')!=='assets,cut,scenario,sha256' ||
    !Object.hasOwn(cuts,v.cut)||!scenarios.has(v.scenario))fail('SYNTHETIC_INPUT_ONLY');
 if(v.sha256!==ownSha)fail('SYNTHETIC_SHA_MISMATCH');
 if(!Array.isArray(v.assets)||v.assets.length!==2)fail('TWO_SYNTHETIC_ASSETS_REQUIRED');
 const allowedIds=['SYNTHETIC:IAEN24','SYNTHETIC:PAN24'];
 const verifiedAssets=v.assets.map((asset)=>{
  if(!asset||typeof asset!=='object'||
     Object.keys(asset).sort().join(',')!=='id,sha256,text' ||
     !allowedIds.includes(asset.id)||typeof asset.text!=='string'||
     !asset.text.startsWith('SYNTHETIC DOCUMENT FIXTURE\n')||
     Buffer.byteLength(asset.text,'utf8')>2048)fail('UNBOUNDED_OR_NON_SYNTHETIC_ASSET');
  const computed=createHash('sha256').update(Buffer.from(asset.text,'utf8')).digest('hex');
  if(asset.sha256!==computed)fail('ASSET_SHA_MISMATCH');
  if(registeredFixtureSha[asset.id]!==computed)fail('UNREGISTERED_SYNTHETIC_FIXTURE');
  return {id:asset.id,sha256:computed};
 });
 if(verifiedAssets.map(x=>x.id).sort().join(',')!==allowedIds.join(','))
  fail('DUPLICATE_OR_MISSING_ASSET_ROLE');
 const reg=W.empty();
 const base={kind:'SYNTHETIC',state:'TEST_FIXTURE',rights:'SYNTHETIC',
  url:'https://example.invalid/pfl-synthetic-no-external-source'};
 W.source(reg,{...base,id:'SYN:EARLY',observed_at:'2026-09-20T12:00:00Z',
  first_public_at:'2026-09-19T12:00:00Z'});
 W.source(reg,{...base,id:'SYN:LATE',observed_at:'2026-10-31T12:00:00Z',
  first_public_at:'2026-10-30T12:00:00Z'});
 W.entity(reg,{id:'SYN:ACTOR',type:'PERSON_PUBLIC',name:'Fictional Public Actor',
  public_role_documented:true,source_id:'SYN:EARLY',jurisdiction:'SYNTHETIC_ES'});
 W.entity(reg,{id:'SYN:ORG',type:'PUBLIC_BODY',name:'Fictional Public Body',
  source_id:'SYN:EARLY',jurisdiction:'SYNTHETIC_ES'});
 W.role(reg,{id:'SYN:ROLE_V1',type:'PUBLIC_SPOKESPERSON',subject_id:'SYN:ACTOR',
  object_id:'SYN:ORG',source_id:'SYN:EARLY',valid_from:'2026-09-01',
  valid_to:null,observed_at:'2026-09-20T12:00:00Z',
  first_public_at:'2026-09-19T12:00:00Z'});
 W.role(reg,{id:'SYN:ROLE_V2',type:'PUBLIC_SPOKESPERSON',subject_id:'SYN:ACTOR',
  object_id:'SYN:ORG',source_id:'SYN:LATE',valid_from:'2026-09-01',
  valid_to:null,observed_at:'2026-10-31T12:00:00Z',
  first_public_at:'2026-10-30T12:00:00Z'});
 W.event(reg,{id:'SYN:DECISION_V1',type:'OFFICIAL_INITIATIVE',
  occurred_on:'2026-09-10',source_id:'SYN:EARLY',
  observed_at:'2026-09-20T12:00:00Z',first_public_at:'2026-09-19T12:00:00Z',
  participants:[{actor_id:'SYN:ORG',role:'ISSUER'}]});
 W.event(reg,{id:'SYN:DECISION_V2',type:'OFFICIAL_INITIATIVE',
  occurred_on:'2026-10-10',source_id:'SYN:LATE',
  observed_at:'2026-10-31T12:00:00Z',first_public_at:'2026-10-30T12:00:00Z',
  participants:[{actor_id:'SYN:ORG',role:'ISSUER'}],amendment_of:'SYN:DECISION_V1'});

 let spoofedRawSourceVisible=false;
 let rawId=null;
 if(v.scenario==='rights_spoof'){
  rawId='SYN:UNTRUSTED_RAW';
  W.source(reg,{id:rawId,kind:'OFFICIAL',state:'RAW_CAPTURED',
   rights:'OPEN_LICENSE_VERIFIED',url:base.url,
   observed_at:'2026-10-31T12:00:00Z',
   first_public_at:'2026-09-19T12:00:00Z',
   sha256:ownSha,digest_recomputed:true});
 }
 let recursivePrivateKeyRejected=false;
 if(v.scenario==='privacy_probe'){
  try{W.source(reg,{...base,id:'SYN:PRIVATE_PROBE',
   observed_at:'2026-10-31T12:00:00Z',first_public_at:null,
   personal_email:'synthetic@invalid.example'});}catch(e){
    recursivePrivateKeyRejected=String(e.message)==='UNSAFE_SOURCE';
  }
  if(!recursivePrivateKeyRejected)fail('PRIVACY_PROBE_NOT_REJECTED');
 }
 const cutoff=cuts[v.cut];
 const visible=W.asOf(reg,cutoff);
 // REQUIRE a knowledge cutoff: rolesAt's optional cutoff is unsafe for
 // historical consumers. Never call the cutoff-free branch in this adapter.
 const actorRoles=W.rolesAt(reg,'SYN:ACTOR','2026-10-10',cutoff);
 const audit=W.auditBundle(reg);
 if(!audit.ok)fail('SYNTHETIC_WAREHOUSE_REFERENTIAL_FAILURE');
 if(v.scenario==='rights_spoof'){
  // A raw fixture's visibility must not be inferred from the *total*
  // source count: as_of=early correctly sees one earlier synthetic source.
  spoofedRawSourceVisible=visible.source_count !==
      W.asOf({...reg,sources:reg.sources.filter(s=>s.id!==rawId)},cutoff).source_count;
  if(spoofedRawSourceVisible)fail('SPOOFED_ORIGINAL_ENTERED_HISTORICAL_CUT');
 }
 return {schema:'pfl.synthetic_warehouse_bridge.v1',
  synthetic_sha256_parity:ownSha===v.sha256,
  assets_verified_by_bytes:verifiedAssets,
  roles_visible_as_of:visible.roles.length,
  roles_at_valid_day_and_cut:actorRoles.length,
  decisions_visible_as_of:visible.events.length,
  source_count_visible_as_of:visible.source_count,
  spoofed_raw_source_visible_as_of:spoofedRawSourceVisible,
  recursive_private_key_rejected:recursivePrivateKeyRejected,
  rights_independent_attestation_available:audit.gate.rights_independent_attestation_available,
  real_people_scoring_enabled:audit.gate.can_score_real_people,
  raw_rights_blocker:v.scenario==='rights_spoof'&&
   audit.gate.blockers.includes('RIGHTS_NOT_VERIFIED_FOR_REDISTRIBUTION'),
  real_denominator:null,first_public_at_real:null,
  publisher_authenticated:false,source_identity_crosswalk_certified:false};
}

let data='';
try{
 for await(const part of stdin){data+=part;if(data.length>4096)fail('SYNTHETIC_INPUT_TOO_LARGE');}
 const payload=JSON.parse(data);
 stdout.write(JSON.stringify(run(payload))+'\n');
}catch(e){
 stderr.write(String(e?.message||'SYNTHETIC_BRIDGE_ERROR')+'\n');
 process.exitCode=2;
}
