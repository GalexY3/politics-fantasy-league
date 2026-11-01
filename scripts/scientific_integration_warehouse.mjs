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
const exactKeys=(obj,keys)=>obj!==null&&!Array.isArray(obj)&&
 typeof obj==='object'&&Object.keys(obj).sort().join(',')===keys.slice().sort().join(',');

function checkSyntheticRivals(experiment,cut){
 if(cut==='early'){
  if(experiment!==null)fail('FUTURE_RIVAL_PROJECTION_AT_EARLY_CUT');
  return null;
 }
 if(!exactKeys(experiment,['schema','as_of','hypotheses',
    'synthetic_fixture_ids_by_channel','capture_at_by_channel',
    'exposure_window_by_regime',
    'first_public_at','independent_registry_total',
    'source_identity_crosswalk_verified','reuse_rights_independently_verified'])||
    experiment.schema!=='pfl.synthetic_observational_equivalence_wire.v1'||
    experiment.as_of!==cuts.late||experiment.first_public_at!==null||
    experiment.independent_registry_total!==null||
    experiment.source_identity_crosswalk_verified!==false||
    experiment.reuse_rights_independently_verified!==false)
  fail('UNTRUSTED_OR_FUTURE_RIVAL_WITNESS');
 const labels=['CAPTURE_EXPANSION','STABLE_CAPTURE'];
 const regimes=['BEFORE_REFORM','AFTER_REFORM'];
 const channels=['ELECTRONIC','PAPER'];
 if(!exactKeys(experiment.hypotheses,labels)||
    !exactKeys(experiment.synthetic_fixture_ids_by_channel,regimes)||
    !exactKeys(experiment.capture_at_by_channel,regimes)||
    !exactKeys(experiment.exposure_window_by_regime,regimes))
  fail('RIVAL_IDENTITY_OR_PROJECTION_MISMATCH');
 const published={BEFORE_REFORM:{ELECTRONIC:2,PAPER:8},
   AFTER_REFORM:{ELECTRONIC:12,PAPER:8}};
 const expected={CAPTURE_EXPANSION:'EQUAL_UNDER_ASSUMPTIONS',
   STABLE_CAPTURE:'RISING_UNDER_ASSUMPTIONS'};
 const windows={BEFORE_REFORM:{first_day:'2026-09-01',last_day:'2026-09-30'},
  AFTER_REFORM:{first_day:'2026-10-01',last_day:'2026-10-30'}};
 for(const regime of regimes){
  const ids=experiment.synthetic_fixture_ids_by_channel[regime];
  const captures=experiment.capture_at_by_channel[regime];
  const window=experiment.exposure_window_by_regime[regime];
  if(!exactKeys(ids,channels)||!exactKeys(captures,channels))
   fail('RIVAL_IDENTITY_OR_PROJECTION_MISMATCH');
  if(!exactKeys(window,['first_day','last_day'])||
     window.first_day!==windows[regime].first_day||
     window.last_day!==windows[regime].last_day)
   fail('RIVAL_EXPOSURE_WINDOW_MISMATCH');
  for(const channel of channels){
   if(ids[channel]!==`SYNTHETIC:${regime}:${channel}`||
      captures[channel]!=='2026-10-31T12:00:00Z')
    fail('RIVAL_IDENTITY_OR_CAPTURE_ASOF_MISMATCH');
  }
 }
 const before=published.BEFORE_REFORM.ELECTRONIC+published.BEFORE_REFORM.PAPER;
 const after=published.AFTER_REFORM.ELECTRONIC+published.AFTER_REFORM.PAPER;
 const captureExpansion={before:2*before,after:after};
 const stableCapture={before:2*before,after:2*after};
 const assumedIntake={CAPTURE_EXPANSION:{
    BEFORE_REFORM:captureExpansion.before,AFTER_REFORM:captureExpansion.after},
   STABLE_CAPTURE:{BEFORE_REFORM:stableCapture.before,
    AFTER_REFORM:stableCapture.after}};
 for(const label of labels){
  const hypothesis=experiment.hypotheses[label];
  if(!exactKeys(hypothesis,['visible_by_channel','hypothetical_intake_by_regime',
        'hypothetical_trend_sign'])||
     !exactKeys(hypothesis.visible_by_channel,regimes)||
     hypothesis.hypothetical_trend_sign!==expected[label])
    fail('RIVAL_MECHANISM_OR_TREND_MISMATCH');
  if(!exactKeys(hypothesis.hypothetical_intake_by_regime,regimes)||
     regimes.some(r=>hypothesis.hypothetical_intake_by_regime[r]!==assumedIntake[label][r]))
   fail('RIVAL_LATENT_SCENARIO_NOT_MATCHING_ASSUMPTIONS');
  for(const regime of regimes){
   const cells=hypothesis.visible_by_channel[regime];
   if(!exactKeys(cells,channels))fail('RIVAL_PROJECTION_CHANNEL_MISMATCH');
   for(const channel of channels){
    if(!Number.isInteger(cells[channel])||
       cells[channel]!==published[regime][channel])
     fail('RIVAL_PROJECTION_CHANNEL_MISMATCH');
   }
  }
 }
 // Two DGPs, one publication vector. Only the counterfactual *assumption*
 // changes: capture expands from 1/2 to 1, or capture remains at 1/2.
 // These totals are invented latent states, never measured risk sets.
 if(captureExpansion.before!==captureExpansion.after||
    stableCapture.after<=stableCapture.before)
  fail('RIVAL_MECHANISMS_NOT_DISCRIMINATING');
 return {schema:'pfl.synthetic_observational_equivalence_oracle.v1',
  status:'OBSERVATIONALLY_EQUIVALENT_NOT_IDENTIFIED',
  same_published_by_channel:true,opposed_synthetic_trend_signs:true,
  synthetic_published_totals:{before,after},
  synthetic_intake_under_assumptions:{CAPTURE_EXPANSION:captureExpansion,
   STABLE_CAPTURE:stableCapture},
  independent_registry_witness:false,first_public_at:null,
  source_identity_crosswalk_verified:false,rights_independently_verified:false,
  real_causal_effect_identified:false,empirical_estimand_admitted:false};
}

function run(v){
 if(!v||Array.isArray(v)||typeof v!=='object'||
    !['assets,cut,experiment,scenario,sha256','assets,cut,scenario,sha256']
      .includes(Object.keys(v).sort().join(',')) ||
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
 if(!Object.hasOwn(v,'experiment'))fail('SYNTHETIC_RIVAL_WIRE_REQUIRED');
 const observationalEquivalence=checkSyntheticRivals(v.experiment??null,v.cut);
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
  observational_equivalence_experiment:observationalEquivalence,
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
