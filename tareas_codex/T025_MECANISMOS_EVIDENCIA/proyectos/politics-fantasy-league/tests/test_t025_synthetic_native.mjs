import test from 'node:test';
import assert from 'node:assert/strict';
import {scoreSyntheticRound as score} from '../src/politics_fantasy/synthetic_round_score.mjs';
import {buildSyntheticManifest as manifest} from '../src/politics_fantasy/synthetic_round_manifest.mjs';

const fixture = () => ({round_id:'SYN-RND-1',rule_version:'synthetic-v1',verified_complete:true,evidence_id:'synthetic-fixture:test',slots:['SYN-EVT-1','SYN-EVT-2'],events:[{id:'SYN-EVT-1',attempted:true,success:true},{id:'SYN-EVT-2',attempted:true,success:false}]});
const clone = x => JSON.parse(JSON.stringify(x));
const change = (x, f) => { const r=clone(x); f(r); return r; };
const badScore = f => assert.throws(()=>score(change(fixture(),f)));
const snap = () => clone(score(fixture()));
const badManifest = f => assert.throws(()=>manifest(change(snap(),f)));

const c03 = [
 ['expected rate',()=>assert.equal(score(fixture()).scores.observed_rate,0.5)],
 ['scheduled denominator',()=>assert.equal(score(fixture()).scores.scheduled_rate,0.5)],
 ['beta prior',()=>assert.equal(score(fixture()).scores.beta22,0.5)],
 ['output frozen',()=>{let x=score(fixture()); assert.ok(Object.isFrozen(x)); assert.ok(Object.isFrozen(x.scores));}],
 ['zero successes documented',()=>assert.equal(score(change(fixture(),x=>x.events[0].success=false)).scores.raw_successes,0)],
 ['missing coverage null',()=>{let x=score(change(fixture(),x=>x.verified_complete=false));assert.equal(x.status,'COVERAGE_UNKNOWN');assert.equal(x.scores,null);} ],
 ['empty schedule null',()=>{let x=score(change(fixture(),x=>{x.slots=[];x.events=[];}));assert.equal(x.status,'VERIFIED_NO_OPPORTUNITIES');assert.equal(x.scores,null);} ],
 ['no attempts observed rate null',()=>assert.equal(score(change(fixture(),x=>x.events.forEach(e=>{e.attempted=false;e.success=null;}))).scores.observed_rate,null)],
 ['reject person key',()=>badScore(x=>x.person_id='SYN-PERSON')],
 ['reject party key',()=>badScore(x=>x.party_id='SYN-PARTY')],
 ['reject real ids',()=>badScore(x=>x.slots[0]='ordinary-id')],
 ['reject duplicate slots',()=>badScore(x=>x.slots[1]=x.slots[0])],
 ['reject duplicate observed id',()=>badScore(x=>x.events[1].id=x.events[0].id)],
 ['reject incomplete vector',()=>badScore(x=>x.events.pop())],
 ['reject missing evidence',()=>badScore(x=>delete x.evidence_id)],
 ['reject success on unattempted',()=>badScore(x=>x.events[0].attempted=false)],
 ['reject human round',()=>badScore(x=>x.round_id='person-round')],
 ['reject malformed event',()=>badScore(x=>x.events[0].id='not-synthetic')]
];
const c05 = [
 ['basic manifest',()=>assert.equal(manifest(snap()).schema,'pfl.synthetic.manifest.v1')],
 ['canonical deterministic',()=>assert.equal(manifest(snap()).canonical_payload,manifest(snap()).canonical_payload)],
 ['idempotent replay',()=>{let a=manifest(snap()); assert.equal(manifest(snap(),a).duplicate_safe,true)}],
 ['immutable',()=>assert.ok(Object.isFrozen(manifest(snap())))],
 ['unknown no score',()=>{let s=score(change(fixture(),x=>x.verified_complete=false));assert.equal(JSON.parse(manifest(s).canonical_payload).scores,null)}],
 ['empty verified',()=>{let s=score(change(fixture(),x=>{x.slots=[];x.events=[]}));assert.equal(manifest(s).status,'VERIFIED_NO_OPPORTUNITIES')}],
 ['reject person key',()=>badManifest(x=>x.person_id='SYN-PERSON')],
 ['reject political party',()=>badManifest(x=>x.party_id='SYN-PARTY')],
 ['reject real round',()=>badManifest(x=>x.round_id='ordinary-round')],
 ['reject missing evidence',()=>badManifest(x=>x.evidence_id=null)],
 ['reject fake zero when unknown',()=>badManifest(x=>{x.status='COVERAGE_UNKNOWN';x.evidence_id=null})],
 ['reject invalid denominator',()=>badManifest(x=>x.scheduled=0)],
 ['reject fake score',()=>badManifest(x=>x.scores.observed_rate=0.123)],
 ['reject silent changed rule version',()=>assert.throws(()=>manifest(change(snap(),x=>x.rule_version='synthetic-v2'),manifest(snap())))],
 ['reject silent changed evidence',()=>assert.throws(()=>manifest(change(snap(),x=>x.evidence_id='synthetic-fixture:other'),manifest(snap())))],
 ['reject cross round replay',()=>assert.throws(()=>manifest(change(snap(),x=>x.round_id='SYN-RND-other'),manifest(snap())))],
 ['reject unsupported status',()=>badManifest(x=>x.status='UNSUPPORTED')],
 ['reject bad previous',()=>assert.throws(()=>manifest(snap(),{}))]
];
for(const [name,fn] of c03) test(`C03 ${name}`,fn);
for(const [name,fn] of c05) test(`C05 ${name}`,fn);
