// Reconstructed from named C02-C05 assertions; original 84-test script unavailable.
// This is an offline synthetic fixture test, never approval for a human study.
import test from 'node:test';
import assert from 'node:assert/strict';
import {assignSyntheticArms as assign} from '../src/politics_fantasy/pilot_assignment.mjs';
import {fictionalTransferItems as items} from '../src/politics_fantasy/fictional_transfer_items.mjs';
import {evaluateFictionalTransfer as evaluate} from '../src/politics_fantasy/fictional_transfer_key.mjs';
import {validatePilotIntake as intake} from '../src/politics_fantasy/pilot_dryrun_intake.mjs';
import {analyseFictionalPilot as analyse} from '../src/politics_fantasy/pilot_analysis_dryrun.mjs';

const arms=['control','transparency','leaderboard','both'];
const count=a=>Object.fromEntries(arms.map(x=>[x,a.filter(y=>y===x).length]));
const right=()=>({X1:'B',X2:'A',X3:'B',X4:'B'});
const clone=x=>JSON.parse(JSON.stringify(x));
const changed=(x,f)=>{x=clone(x);f(x);return x;};
const approval=()=>({status:'APPROVED_BY_HUMAN_REVIEW',review_ref:'MOCK-REVIEW-01'});
const payload=()=>({arm:'control',responses:right(),completed:true,consent:true,age_confirmed:true,study_fixture:'SYNTHETIC_DRY_RUN_ONLY'});
const synthetic=()=>({study_fixture:'SYNTHETIC_DRY_RUN_ONLY',rows:arms.flatMap((arm,i)=>[0,1].map(()=>({arm,completed:true,correct:[2,3,1,3][i]})))});
const badEvaluate=f=>assert.throws(()=>evaluate(changed(right(),f)));
const badIntake=f=>assert.throws(()=>intake(changed(payload(),f),approval()));
const badAnalysis=f=>assert.throws(()=>analyse(changed(synthetic(),f)));

const c02=[
 ['four arms 4',()=>assert.deepEqual(count(assign(4,11)),Object.fromEntries(arms.map(a=>[a,1])))],
 ['balanced 8',()=>assert.deepEqual(count(assign(8,11)),Object.fromEntries(arms.map(a=>[a,2])))],
 ['balanced 120',()=>assert.deepEqual(count(assign(120,11)),Object.fromEntries(arms.map(a=>[a,30])))],
 ['blockwise balance',()=>{const r=assign(120,11);for(let i=0;i<r.length;i+=4)assert.equal(new Set(r.slice(i,i+4)).size,4)}],
 ['reproducible',()=>assert.deepEqual(assign(120,11),assign(120,11))],
 ['different seed different order',()=>assert.notDeepEqual(assign(120,11),assign(120,12))],
 ['valid extremes n=10000',()=>assert.equal(assign(10000,4294967295).length,10000)],
 ['no extra metadata',()=>assert.ok(assign(120,11).every(x=>arms.includes(x)))],
 ['frozen output',()=>assert.ok(Object.isFrozen(assign(4,11)))],
 ['reject small',()=>assert.throws(()=>assign(0,1))],
 ['reject odd',()=>assert.throws(()=>assign(5,1))],
 ['reject n fractional',()=>assert.throws(()=>assign(4.5,1))],
 ['reject n too high',()=>assert.throws(()=>assign(10004,1))],
 ['reject seed decimal',()=>assert.throws(()=>assign(4,1.5))],
 ['reject seed negative',()=>assert.throws(()=>assign(4,-1))],
 ['reject seed >u32',()=>assert.throws(()=>assign(4,4294967296))],
 ['zero-seed determinism',()=>assert.deepEqual(assign(120,0),assign(120,0))]
];
const c03=[
 ['four items',()=>assert.equal(items().length,4)],
 ['four constructs',()=>assert.equal(new Set(items().map(x=>x.construct)).size,4)],
 ['unique IDs',()=>assert.deepEqual(items().map(x=>x.id),['X1','X2','X3','X4'])],
 ['three options each',()=>assert.ok(items().every(x=>x.options.length===3))],
 ['fiction no parties',()=>assert.ok(!/partido|party/i.test(JSON.stringify(items())))],
 ['immutable top',()=>assert.ok(Object.isFrozen(items()))],
 ['immutable item',()=>assert.ok(items().every(Object.isFrozen))],
 ['immutable options',()=>assert.ok(items().every(x=>Object.isFrozen(x.options)))],
 ['perfect score',()=>assert.equal(evaluate(right()).correct,4)],
 ['zero score',()=>assert.equal(evaluate({X1:'A',X2:'B',X3:'A',X4:'A'}).correct,0)],
 ['partial score',()=>assert.equal(evaluate({X1:'B',X2:'A',X3:'A',X4:'A'}).correct,2)],
 ['score frozen',()=>assert.ok(Object.isFrozen(evaluate(right())))],
 ['reject absent',()=>badEvaluate(x=>delete x.X1)],
 ['reject extra metadata',()=>badEvaluate(x=>x.person='SYN')],
 ['reject invalid option',()=>badEvaluate(x=>x.X1='D')],
 ['reject lowercase',()=>badEvaluate(x=>x.X1='b')],
 ['reject array',()=>assert.throws(()=>evaluate(['B','A','B','B']))],
 ['reject null',()=>assert.throws(()=>evaluate(null))],
 ['round denominator factual',()=>assert.match(items().find(x=>x.id==='X4').options[1],/3\/20/)],
 ['coverage unknown case',()=>assert.match(items().find(x=>x.id==='X1').options[1],/No puede establecerse/)]
];
const c04=[
 ['valid mock',()=>assert.equal(intake(payload(),approval()).schema,'pfl.dryrun.intake.v1')],
 ['both artifacts frozen',()=>{const x=intake(payload(),approval());assert.ok(Object.isFrozen(x.safe)&&Object.isFrozen(x.consentReceipt))}],
 ['response snapshot frozen',()=>assert.ok(Object.isFrozen(intake(payload(),approval()).safe.responses))],
 ['receipt separate',()=>{const x=intake(payload(),approval());assert.notEqual(x.safe,x.consentReceipt);assert.ok(!('responses' in x.consentReceipt))}],
 ['fixture-only output',()=>assert.equal(intake(payload(),approval()).safe.fixture,'SYNTHETIC_ONLY')],
 ['accept partial',()=>assert.equal(intake(changed(payload(),x=>{x.completed=false;x.responses.X1=null}),approval()).safe.completed,false)],
 ['requires review',()=>assert.throws(()=>intake(payload(),{...approval(),status:'PENDING'}))],
 ['requires long ref',()=>assert.throws(()=>intake(payload(),{...approval(),review_ref:'short'}))],
 ['reject missing consent',()=>badIntake(x=>x.consent=false)],
 ['reject missing adult',()=>badIntake(x=>x.age_confirmed=false)],
 ['reject real fixture',()=>badIntake(x=>x.study_fixture='REAL')],
 ['reject name',()=>badIntake(x=>x.name='SYN')],
 ['reject email',()=>badIntake(x=>x.email='SYN')],
 ['reject political opinion',()=>badIntake(x=>x.political_opinion='SYN')],
 ['reject IP',()=>badIntake(x=>x.ip='SYN')],
 ['reject extra timestamp',()=>badIntake(x=>x.timestamp='SYN')],
 ['reject unknown arm',()=>badIntake(x=>x.arm='other')],
 ['reject incomplete disguised',()=>badIntake(x=>x.responses.X1=null)],
 ['reject unknown answer',()=>badIntake(x=>x.responses.X1='D')],
 ['reject missing response field',()=>badIntake(x=>delete x.responses.X1)],
 ['reject missing required',()=>badIntake(x=>delete x.consent)],
 ['review mock no data persistence',()=>{const oldFetch=globalThis.fetch,oldStorage=Object.getOwnPropertyDescriptor(globalThis,'localStorage');let calls=0;try{globalThis.fetch=()=>{calls++;throw Error('NETWORK_DENIED')};Object.defineProperty(globalThis,'localStorage',{configurable:true,value:{setItem(){calls++;throw Error('STORAGE_DENIED')}}});const x=intake(payload(),approval());assert.equal(x.consentReceipt.fixture,'SYNTHETIC_ONLY');assert.equal(x.consentReceipt.review_ref,approval().review_ref);assert.equal(calls,0)}finally{globalThis.fetch=oldFetch;if(oldStorage)Object.defineProperty(globalThis,'localStorage',oldStorage);else delete globalThis.localStorage}}]
];
const c05=[
 ['all four cells',()=>assert.deepEqual(Object.keys(analyse(synthetic()).cells),arms)],
 ['means ctrl',()=>assert.equal(analyse(synthetic()).cells.control.mean,2)],
 ['means transp',()=>assert.equal(analyse(synthetic()).cells.transparency.mean,3)],
 ['means leaderboard',()=>assert.equal(analyse(synthetic()).cells.leaderboard.mean,1)],
 ['means both',()=>assert.equal(analyse(synthetic()).cells.both.mean,3)],
 ['main transparency',()=>assert.equal(analyse(synthetic()).effects.transparency,1.5)],
 ['main leaderboard',()=>assert.equal(analyse(synthetic()).effects.leaderboard,-0.5)],
 ['interaction',()=>assert.equal(analyse(synthetic()).effects.interaction,1)],
 ['full observed tag',()=>assert.equal(analyse(synthetic()).estimand,'FULLY_OBSERVED_FACTORIAL')],
 ['source synthetic',()=>assert.equal(analyse(synthetic()).source,'FICTIONAL_TEST_ONLY')],
 ['immutable cells',()=>assert.ok(Object.isFrozen(analyse(synthetic()).cells))],
 ['immutable effects',()=>assert.ok(Object.isFrozen(analyse(synthetic()).effects))],
 ['partial missing correctly marked',()=>assert.equal(analyse(changed(synthetic(),x=>{x.rows[0].completed=false;x.rows[0].correct=null})).estimand,'COMPLETE_CASE_NOT_ITT')],
 ['empty observed arm effects null',()=>assert.equal(analyse(changed(synthetic(),x=>x.rows.filter(r=>r.arm==='control').forEach(r=>{r.completed=false;r.correct=null}))).effects,null)],
 ['reject real source',()=>badAnalysis(x=>x.study_fixture='REAL')],
 ['reject extra identity',()=>badAnalysis(x=>x.rows[0].name='SYN')],
 ['reject party',()=>badAnalysis(x=>x.rows[0].party='SYN')],
 ['reject ID metadata',()=>badAnalysis(x=>x.rows[0].id='SYN')],
 ['reject score 5',()=>badAnalysis(x=>x.rows[0].correct=5)],
 ['reject fraction',()=>badAnalysis(x=>x.rows[0].correct=2.5)],
 ['reject falsified missing',()=>badAnalysis(x=>{x.rows[0].completed=false;x.rows[0].correct=0})],
 ['reject missing arm',()=>badAnalysis(x=>x.rows=x.rows.filter(r=>r.arm!=='control'))],
 ['reject invalid arm',()=>badAnalysis(x=>x.rows[0].arm='other')],
 ['reject absent rows',()=>badAnalysis(x=>delete x.rows)],
 ['reject nonarray',()=>badAnalysis(x=>x.rows={})]
];
for(const [cycle,cases] of [['C02',c02],['C03',c03],['C04',c04],['C05',c05]])for(const [name,fn] of cases)test(`${cycle} ${name}`,fn);
