// Execute original frozen functions in a VM wrapper; no production source edits.
import test from 'node:test';
import assert from 'node:assert/strict';
import fs from 'node:fs';
import vm from 'node:vm';
import {fileURLToPath} from 'node:url';
const root=new URL('../research/ABH_INCENTIVE_MECHANISMS5_20261029/',import.meta.url);
function compare(a,b,path='root'){
 if(typeof b==='number'){assert.equal(typeof a,'number',path);assert.ok(Number.isFinite(a)&&Math.abs(a-b)<=1e-12*Math.max(1,Math.abs(b)),`${path}: ${a} vs ${b}`);return;}
 if(b===null||typeof b!=='object'){assert.equal(a,b,path);return;}
 assert.ok(a!==null&&typeof a==='object',path);assert.deepEqual(Object.keys(a).sort(),Object.keys(b).sort(),path);
 for(const k of Object.keys(b))compare(a[k],b[k],`${path}.${k}`);
}
for(const id of ['01','02','04'])test(`C${id} frozen engine reproduces all recorded seed outputs`,()=>{
 const source=fs.readFileSync(fileURLToPath(new URL(`C${id}_ENGINE.js`,root)),'utf8');
 const record=JSON.parse(fs.readFileSync(fileURLToPath(new URL(`C${id}_RESULT.json`,root)),'utf8'));
 const rows=id==='04'?record.E.seeds:record.E;
 assert.equal(rows.length,2);
 const seeds={ '01':[12001,13999], '02':[22001,23999], '04':[42001,43999] };
 assert.deepEqual(rows.map(r=>r.seed),seeds[id]); // Frozen AUTHORIZATION_AND_DESIGN.json.
 for(const row of rows){const output=vm.runInNewContext(`${source}\n;runC${id}(${row.seed})`,{}, {timeout:15000});compare(output,row,`C${id}/${row.seed}`);}
});
