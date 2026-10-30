/** Manual regression: consecutive mock seeds must not induce positional imbalance. */
import {strict as assert} from 'node:assert';
import {assignSyntheticArms} from './pilot_assignment.mjs';
const names=['control','transparency','leaderboard','both'];
const count=Array.from({length:4},()=>[0,0,0,0]);
for(let seed=0;seed<4096;seed++){
 const block=assignSyntheticArms(4,seed);
 assert.equal(new Set(block).size,4,'each block must have four distinct arms');
 for(let position=0;position<4;position++)count[position][names.indexOf(block[position])]++;
}
const expected=4096/4, deviation=Math.max(...count.flat().map(n=>Math.abs(n-expected)/expected));
assert.ok(deviation<=0.08,`serial seed position bias: ${deviation}`);
console.log(JSON.stringify({status:'PASS',n_seeds:4096,max_relative_deviation:deviation,count}));
