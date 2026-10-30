import assert from 'node:assert/strict';
import {diagnoseFictionalClusterFrame} from './fictional_cluster_gate.mjs';
const arms=['control','transparency','leaderboard','both'];
const make=()=>{
 const rows=[];
 for(const [i,arm] of arms.entries()){
  const small=['transparency','both'].includes(arm);
  const large=['control','both'].includes(arm);
  rows.push({participant_id:`P${i}A`,room_id:`R${i}A`,arm,completed:small});
  for(let j=0;j<3;j++)rows.push({participant_id:`P${i}B${j}`,room_id:`R${i}B`,arm,completed:large});
 }
 return {study_fixture:'SYNTHETIC_OFFLINE_ONLY',rows};
};
let pass=0;
function test(label,f){f();pass++;console.log('PASS',label)}
function reject(edit,pattern){const v=make();edit(v);assert.throws(()=>diagnoseFictionalClusterFrame(v),new RegExp(pattern))}
test('16 participants, 8 groups, 4 arms including non-completion',()=>{
 const r=diagnoseFictionalClusterFrame(make());
 assert.equal(r.n,16);assert.equal(r.rooms,8);assert.equal(r.cells.control.completed,3);
 assert.equal(r.cells.transparency.completed,1);assert.equal(r.cells.leaderboard.completed,0);
 assert.equal(r.cells.both.completed,4);assert.equal(r.causal_ready,false);
});
test('cluster-equal vs person-weighted change transparency contrast',()=>{
 const r=diagnoseFictionalClusterFrame(make());
 assert.equal(r.cells.control.person_weighted,0.75);
 assert.equal(r.cells.control.cluster_equal,0.5);
 assert.equal(r.factorial_person_weighted.transparency,0.25);
 assert.equal(r.factorial_cluster_equal.transparency,0.5);
 assert.equal(r.factorial_person_weighted.interaction,1.5);
 assert.equal(r.factorial_cluster_equal.interaction,1);
});
test('stable across row order and fresh clones',()=>{
 const x=make(),a=diagnoseFictionalClusterFrame(x);
 x.rows.reverse();assert.deepEqual(diagnoseFictionalClusterFrame(x),a);
});
test('refuse contamination within a ranking room',()=>{
 reject(x=>{x.rows[1].arm='both'},'ROOM_ARM_CONTAMINATION');
});
test('refuse duplicated participant and fabricated arm',()=>{
 reject(x=>{x.rows[1].participant_id=x.rows[0].participant_id},'DUPLICATE_PERSON');
 reject(x=>{x.rows[0].arm='politician'},'INVALID_ROW');
});
test('refuse fake study type and empty or incomplete frame',()=>{
 reject(x=>{x.study_fixture='LIVE_STUDY'},'SYNTHETIC_FRAME_REQUIRED');
 reject(x=>{x.rows=[]},'EMPTY_FRAME');
 reject(x=>{x.rows=x.rows.filter(p=>p.arm!=='control')},'TOO_FEW_ROOMS_PER_ARM');
});
test('refuse extra personal fields and getters',()=>{
 reject(x=>{x.rows[0].email='x@y.test'},'INVALID_ROW');
 reject(x=>{Object.defineProperty(x.rows[0],'completed',{get:()=>true,enumerable:true})},'INVALID_ROW');
});
test('no causal claims even with a well-formed synthetic cluster partition',()=>{
 const a=diagnoseFictionalClusterFrame(make());
 assert.equal(a.randomization_attested,false);assert.equal(a.individual_exposure_attested,false);
 assert.equal(a.mode,'SYNTHETIC_DESIGN_ONLY');
});
console.log(JSON.stringify({passed:pass,total:8,real_people:0,context:'PFL_ABH5_C03_OFFLINE_CLUSTER_GATE'}));
