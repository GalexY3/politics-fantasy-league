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
  same_published_by_channel:true,different_synthetic_trajectories:true,
  hypothetical_change_by_mechanism:{
   CAPTURE_EXPANSION:'ZERO_CHANGE_UNDER_ASSUMPTIONS',
   STABLE_CAPTURE:'POSITIVE_CHANGE_UNDER_ASSUMPTIONS'},
  synthetic_published_totals:{before,after},
  synthetic_intake_under_assumptions:{CAPTURE_EXPANSION:captureExpansion,
   STABLE_CAPTURE:stableCapture},
  independent_registry_witness:false,first_public_at:null,
  source_identity_crosswalk_verified:false,rights_independently_verified:false,
  real_causal_effect_identified:false,empirical_estimand_admitted:false};
}

// Independent S3 arithmetic: BigInt rationals, no floating-point rounding and
// no reuse of Python fractions. Binary negatives are *not* administrative
// denials, and a zero censor witness is not a negative decision.
function s3Rat(n,d=1n){
 if(d===0n)fail('S3_ZERO_DENOMINATOR');
 if(d<0n){n=-n;d=-d;}
 let a=n<0n?-n:n,b=d;
 while(b!==0n){const t=a%b;a=b;b=t;}
 return {n:n/a,d:d/a};
}
const s3Plus=(a,b)=>s3Rat(a.n*b.d+b.n*a.d,a.d*b.d);
const s3Minus=(a,b)=>s3Rat(a.n*b.d-b.n*a.d,a.d*b.d);
const s3Times=(a,b)=>s3Rat(a.n*b.n,a.d*b.d);
const s3Divide=(a,b)=>s3Rat(a.n*b.d,a.d*b.n);
const s3String=(v)=>`${v.n}/${v.d}`;

function checkS3PartialIdentification(s3,cut){
 if(cut==='early'){
  if(s3!==null)fail('S3_FUTURE_PARTIAL_IDENTIFICATION_AT_EARLY_CUT');
  return null;
 }
 if(!exactKeys(s3,['schema','as_of','population','observations',
     'selection_ratio_positive_to_negative','independent_registry_total',
     'first_public_at_real','rights_independently_verified',
     'causal_effect_claimed','administrative_negative_claimed'])||
    s3.schema!=='pfl.synthetic_partial_identification_wire.v1'||
    s3.as_of!==cuts.late||s3.population!=='SYNTHETIC_OBSERVED_BINARY_ONLY'||
    s3.independent_registry_total!==null||s3.first_public_at_real!==null||
    s3.rights_independently_verified!==false||
    s3.causal_effect_claimed!==false||
    s3.administrative_negative_claimed!==false)
  fail('S3_UNTRUSTED_REAL_SOURCE_OR_KNOWLEDGE_CUT');
 const periods=['before','after'];
 const observed={before:{observed_positive:6,observed_negative:4,
    documented_censor_witnesses:0},
   after:{observed_positive:7,observed_negative:3,
    documented_censor_witnesses:0}};
 if(!exactKeys(s3.observations,periods))fail('S3_BINARY_FRAME_MISMATCH');
 for(const p of periods){
  const row=s3.observations[p];
  const keys=['observed_positive','observed_negative','documented_censor_witnesses'];
  if(!exactKeys(row,keys)||keys.some(k=>!Number.isSafeInteger(row[k])||
       row[k]!==observed[p][k]))fail('S3_BINARY_FRAME_MISMATCH');
 }
 const ratio=s3.selection_ratio_positive_to_negative;
 if(!exactKeys(ratio,['lower','upper'])||ratio.lower!=='1/2'||
    ratio.upper!=='2/1')fail('S3_RATIO_RANGE_SPOOF_OR_SWAP');
 const rMin=s3Rat(1n,2n),rMax=s3Rat(2n,1n),one=s3Rat(1n);
 const shares={},bounds={};
 for(const p of periods){
  const row=observed[p];
  const q=s3Rat(BigInt(row.observed_positive),
    BigInt(row.observed_positive+row.observed_negative));
  const truePrevalence=(r)=>s3Divide(q,
    s3Plus(q,s3Times(r,s3Minus(one,q))));
  shares[p]=s3String(q);
  bounds[p]={lower:truePrevalence(rMax),upper:truePrevalence(rMin)};
 }
 const deltaLow=s3Minus(bounds.after.lower,bounds.before.upper);
 const deltaHigh=s3Minus(bounds.after.upper,bounds.before.lower);
 return {schema:'pfl.synthetic_partial_identification_oracle.v1',
  status:'ASSUMPTION_CONDITIONAL_NONCAUSAL_BOUNDS',
  observed_positive_share:shares,
  selection_ratio_positive_to_negative:{lower:s3String(rMin),upper:s3String(rMax)},
  prevalence_bounds:Object.fromEntries(periods.map(p=>[p,{
    lower:s3String(bounds[p].lower),upper:s3String(bounds[p].upper)}])),
  change_bounds:{lower:s3String(deltaLow),upper:s3String(deltaHigh)},
  without_ratio_restriction:{nontrivial_bounds_available:false,
    trivial_change_closure:{lower:'-1/1',upper:'1/1'}},
  documented_censor_witnesses:{before:0,after:0},
  observed_negative_is_administrative_failure:false,
  independent_registry_total:null,first_public_at_real:null,
  rights_independently_verified:false,causal_effect_identified:false,
  empirical_estimand_admitted:false};
}

function replayBitemporal(timeline,cut){
 if(!exactKeys(timeline,['schema','issuer','sources','actor_id','institution_id',
   'roles','events','first_public_at_real','source_crosswalk_certified',
   'independent_denominator','rights_independently_verified'])||
   timeline.schema!=='pfl.synthetic_bitemporal_actor_event_wire.v1'||
   timeline.issuer!=='SYN:CHRONICLE'||
   timeline.actor_id!=='SYN:CHRONICLE_ACTOR'||
   timeline.institution_id!=='SYN:CHRONICLE_OFFICE'||
   timeline.first_public_at_real!==null||
   timeline.source_crosswalk_certified!==false||
   timeline.independent_denominator!==null||
   timeline.rights_independently_verified!==false)
  fail('BITEMPORAL_UNATTESTED_IDENTITY_OR_GATE');
 const bodies=[
  'SYNTHETIC BITEMPORAL FIXTURE\nISSUER:SYN:CHRONICLE\nEDITION:V1\nACTOR:A\nEVENT:E1\n',
  'SYNTHETIC BITEMPORAL FIXTURE\nISSUER:SYN:CHRONICLE\nEDITION:V2\nACTOR:A\nEVENT:E1_REVISED\n'];
 const digests=[
  'd652283f6dd552283d6187d03b255d1cde281ae7375697953e886ffe3cbaa245',
  '40458358e15b6e354541cf88d238e95894bac8b2bd93bff33c91530c7c3d0836'];
 const captures=['2026-09-20T12:00:00Z','2026-10-31T12:00:00Z'];
 const publications=['2026-09-19T12:00:00Z','2026-10-30T12:00:00Z'];
 if(!Array.isArray(timeline.sources)||timeline.sources.length!==2||
    !Array.isArray(timeline.roles)||timeline.roles.length!==2||
    !Array.isArray(timeline.events)||timeline.events.length!==2)
  fail('BITEMPORAL_TWO_REVISIONS_REQUIRED');
 const tReg=W.empty();
 for(let i=0;i<2;i++){
  const s=timeline.sources[i];
  if(!exactKeys(s,['source_id','text','sha256','captured_at','first_public_at'])||
     s.source_id!==`SYN:CHRONICLE_V${i+1}`||
     s.text!==bodies[i]||
     s.sha256!==digests[i]||
     s.sha256!==createHash('sha256').update(Buffer.from(s.text,'utf8')).digest('hex')||
     s.captured_at!==captures[i]||s.first_public_at!==publications[i])
   fail('BITEMPORAL_SOURCE_BYTES_OR_SHA_MISMATCH');
  W.source(tReg,{id:s.source_id,kind:'SYNTHETIC',state:'TEST_FIXTURE',
   url:'https://example.invalid/synthetic-bitemporal-no-external-source',
   observed_at:s.captured_at,first_public_at:s.first_public_at,rights:'SYNTHETIC'});
 }
 W.entity(tReg,{id:timeline.actor_id,type:'PERSON_PUBLIC',
  name:'Invented Public Actor',public_role_documented:true,
  source_id:timeline.sources[0].source_id});
 W.entity(tReg,{id:timeline.institution_id,type:'PUBLIC_BODY',
  name:'Invented Public Institution',source_id:timeline.sources[0].source_id});
 const expRole=[
  {id:'SYN:CHRONICLE_ROLE_V1',source_id:'SYN:CHRONICLE_V1',
   revision:'v1',valid_from:'2026-09-01',valid_to:'2026-10-01',amendment_of:null},
  {id:'SYN:CHRONICLE_ROLE_V2',source_id:'SYN:CHRONICLE_V2',
   revision:'v2',valid_from:'2026-10-01',valid_to:null,
   amendment_of:'SYN:CHRONICLE_ROLE_V1'}];
 const expEvent=[
  {id:'SYN:CHRONICLE_EVENT_V1',source_id:'SYN:CHRONICLE_V1',
   revision:'v1',occurred_on:'2026-09-10',
   typed_key:['SYN:CHRONICLE','INITIATIVE','FILE_1'],amendment_of:null},
  {id:'SYN:CHRONICLE_EVENT_V2',source_id:'SYN:CHRONICLE_V2',
   revision:'v2',occurred_on:'2026-09-10',
   typed_key:['SYN:CHRONICLE','INITIATIVE','FILE_1'],
   amendment_of:'SYN:CHRONICLE_EVENT_V1'}];
 for(let i=0;i<2;i++){
  const role=timeline.roles[i],ev=timeline.events[i];
  if(!exactKeys(role,Object.keys(expRole[i]))||
     Object.keys(expRole[i]).some(k=>role[k]!==expRole[i][k])||
     !exactKeys(ev,Object.keys(expEvent[i]))||
     Object.keys(expEvent[i]).some(k=>k!=='typed_key'&&ev[k]!==expEvent[i][k])||
     JSON.stringify(ev.typed_key)!==JSON.stringify(expEvent[i].typed_key))
   fail('BITEMPORAL_TYPED_AMENDMENT_CROSSWALK_MISMATCH');
  const s=timeline.sources[i];
  W.role(tReg,{id:role.id,type:'PUBLIC_SPOKESPERSON',
   subject_id:timeline.actor_id,object_id:timeline.institution_id,
   source_id:role.source_id,valid_from:role.valid_from,valid_to:role.valid_to,
   observed_at:s.captured_at,first_public_at:s.first_public_at});
  W.event(tReg,{id:ev.id,type:'OFFICIAL_INITIATIVE',
   occurred_on:ev.occurred_on,source_id:ev.source_id,
   observed_at:s.captured_at,first_public_at:s.first_public_at,
   participants:[{actor_id:timeline.actor_id,role:'SPEAKER'}],
   amendment_of:ev.amendment_of});
 }
 if(!W.auditBundle(tReg).ok)fail('BITEMPORAL_REFERENTIAL_INTEGRITY_FAILED');
 const visible=W.asOf(tReg,cuts[cut]);
 const views={};
 for(const day of ['2026-09-15','2026-10-10']){
  const known=visible.events.filter(e=>e.occurred_on<=day);
  if(known.length<1||known.length>2||known[0].id!==expEvent[0].id||
     (known.length===2&&(known[1].id!==expEvent[1].id||
       known[1].amendment_of!==known[0].id)))
   fail('BITEMPORAL_AMENDMENT_CHAIN_DIVERGENCE');
  views[day]={
   actor_source_local_identity_count:visible.source_count>0?1:0,
   role_assertions_visible_at_valid_day:W.rolesAt(tReg,timeline.actor_id,day,cuts[cut]).length,
   role_observation_state:W.rolesAt(tReg,timeline.actor_id,day,cuts[cut]).length>0?
    'OBSERVED':'NOT_OBSERVED',
   event_documentary_revisions_known:known.length,
   logical_events_after_typed_amendment:1,
   selected_revision:known.length===2?'v2':'v1'};
 }
 return {schema:'pfl.synthetic_bitemporal_actor_event_oracle.v1',
  views_by_valid_day:views,visible_source_receipts:visible.source_count,
  fixture_source_sha_checked:true,typed_amendment_fixture_checked:true,
  first_public_at_real:null,rights_independently_verified:false,
  source_crosswalk_certified:false,independent_denominator:null,
  real_actor_identity_verified:false,empirical_event_count_admitted:false};
}

function run(v){
 if(!v||Array.isArray(v)||typeof v!=='object'||
    !['assets,cut,experiment,partial_identification,scenario,sha256,timeline',
      'assets,cut,experiment,scenario,sha256,timeline',
      'assets,cut,experiment,scenario,sha256',
      'assets,cut,scenario,sha256']
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
 if(!Object.hasOwn(v,'timeline'))fail('BITEMPORAL_WIRE_REQUIRED');
 const bitemporal=replayBitemporal(v.timeline,v.cut);
 if(!Object.hasOwn(v,'partial_identification'))fail('S3_PARTIAL_IDENTIFICATION_WIRE_REQUIRED');
 const partialIdentification=checkS3PartialIdentification(v.partial_identification,v.cut);
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
  bitemporal_actor_event_equivalence:bitemporal,
  partial_identification_oracle:partialIdentification,
  real_denominator:null,first_public_at_real:null,
  publisher_authenticated:false,source_identity_crosswalk_certified:false};
}

let data='';
try{
 for await(const part of stdin){data+=part;if(data.length>8192)fail('SYNTHETIC_INPUT_TOO_LARGE');}
 const payload=JSON.parse(data);
 stdout.write(JSON.stringify(run(payload))+'\n');
}catch(e){
 stderr.write(String(e?.message||'SYNTHETIC_BRIDGE_ERROR')+'\n');
 process.exitCode=2;
}
