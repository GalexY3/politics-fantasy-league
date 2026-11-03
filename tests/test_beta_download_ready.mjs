import {test} from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,writeFileSync,rmSync} from 'node:fs';
import {join} from 'node:path';
import {tmpdir} from 'node:os';
import {completedJsonDownload} from './beta_chrome_download_ready.mjs';

function syntheticReceipt(canonical_json){
 return {canonical_json,sha256:createHash('sha256').update(canonical_json,'utf8').digest('hex'),
  bytes:Buffer.byteLength(canonical_json,'utf8')};
}
function boundedPoll(max,atAttempt=()=>{}){
 let calls=0;
 const poll=async callback=>{
  for(let i=0;i<max;i++){
   calls++;
   atAttempt(calls);
   try{const result=await callback();if(result)return result;}catch(_){}
  }
  throw Error('BOUNDED_CONDITION_NOT_MET');
 };
 return {poll,calls:()=>calls};
}

test('CDP download reader waits for canonical complete bytes after filename appears',async()=>{
 const folder=mkdtempSync(join(tmpdir(),'pfl-cdp-ready-synthetic-'));
 try{
  const path=join(folder,'synthetic-snapshot.json');
  const data={snapshot_receipt:syntheticReceipt('{"á":"valor"}')};
  const complete=JSON.stringify(data)+'\n';
  writeFileSync(path,complete.slice(0,11),'utf8');
  const runner=boundedPoll(5,n=>{
   // An explicitly controlled synthetic write completes after the first
   // rejected incomplete reads. No clock, arbitrary sleep or browser.
   if(n===3)writeFileSync(path,complete,'utf8');
  });
  const got=await completedJsonDownload(folder,/^synthetic-snapshot\.json$/,runner.poll);
  assert.equal(got.name,'synthetic-snapshot.json');
  assert.deepEqual(got.data,data);
  assert.equal(runner.calls(),3);
 }finally{rmSync(folder,{recursive:true,force:true});}
});

test('CDP download reader rejects fully parsed but incorrect snapshot/pair SHA',async()=>{
 const folder=mkdtempSync(join(tmpdir(),'pfl-cdp-ready-negative-'));
 try{
  const path=join(folder,'wrong.json');
  for(const field of ['snapshot_receipt','pair_receipt']){
   const receipt=syntheticReceipt('{"scope":"synthetic"}');
   receipt.sha256='0'.repeat(64);
   writeFileSync(path,JSON.stringify({[field]:receipt})+'\n','utf8');
   const runner=boundedPoll(3);
   await assert.rejects(
    completedJsonDownload(folder,/^wrong\.json$/,runner.poll),
    /BOUNDED_CONDITION_NOT_MET/,
   );
   assert.equal(runner.calls(),3);
  }
 }finally{rmSync(folder,{recursive:true,force:true});}
});
