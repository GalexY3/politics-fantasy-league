/** T028 independent, preregistered QA holdout. Synthetic allocation ONLY. */
import assert from 'node:assert/strict';
import { readFileSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { assignSyntheticArms } from './pilot_assignment.mjs';
const names = ['control','transparency','leaderboard','both'];
const source = readFileSync(new URL('./pilot_assignment.mjs', import.meta.url));
const blob = createHash('sha1').update(`blob ${source.byteLength}\0`).update(source).digest('hex');
assert.equal(blob, '44e194c7d52826e4adcf8c966060734ade6956cb', 'Original verified remote source blob changed');
const windows=[
  ['adjacent_holdout',4096,4096],
  ['high_bit_holdout',2147483648,4096],
  ['maximum_seed_holdout',4294963200,4096]
];
let records=[];
for(const [label,start,count] of windows){
 const matrix=Array.from({length:4},()=>[0,0,0,0]);
 const perms=new Map();
 for(let seed=start;seed<start+count;seed++){
  const arm=assignSyntheticArms(4,seed);
  assert.equal(arm.length,4);
  assert.equal(new Set(arm).size,4);
  const order=arm.join('|');perms.set(order,1+(perms.get(order)||0));
  for(let i=0;i<4;i++)matrix[i][names.indexOf(arm[i])]++;
 }
 const maxDeviation=Math.max(...matrix.flat().map(c=>Math.abs(c-count/4)/(count/4)));
 assert.ok(maxDeviation<=0.12,`${label} exceeds frozen max deviation: ${maxDeviation}`);
 const chisquare=matrix.flat().reduce((sum,c)=>sum+(c-count/4)**2/(count/4),0);
 records.push({label,start,count,max_relative_cell_deviation:maxDeviation,position_arm_counts:matrix,permutations_seen:perms.size,permutation_min:Math.min(...perms.values()),permutation_max:Math.max(...perms.values()),chi_square_descriptive:chisquare});
}
for(const seed of [0,4096,2147483648,4294967295]){
 for(const n of [8,10000]){
  const s=assignSyntheticArms(n,seed);
  assert.equal(s.length,n);assert.ok(Object.isFrozen(s));
  assert.deepEqual(s,assignSyntheticArms(n,seed),'deterministic');
  for(let b=0;b<n;b+=4)assert.equal(new Set(s.slice(b,b+4)).size,4);
 }
}
for(const [n,seed] of [[0,0],[5,0],[10001,0],[4,-1],[4,4294967296],[4,NaN]]){
 assert.throws(()=>assignSyntheticArms(n,seed),/INVALID_(ALLOCATION_SIZE|SEED)/);
}
const report={status:'PASS',scope:'synthetic noncryptographic allocation QA; no human randomization',source_git_blob:blob,prereg:'a4fe5b87d5c3571155926702dc9c96f45f23ea16',holdouts:records,multiblock_seeds_checked:[0,4096,2147483648,4294967295],multiblock_sizes:[8,10000],invalid_case_count:6,CT2_unchanged:22};
console.log(JSON.stringify(report));
if(process.argv[2])writeFileSync(process.argv[2],JSON.stringify(report,null,2)+'\n');
