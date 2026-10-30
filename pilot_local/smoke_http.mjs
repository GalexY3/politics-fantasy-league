/** Native Node smoke tests; tests only localhost dry-run. No test of real participants. */
import assert from 'node:assert/strict';
import {server} from './server.mjs';
await new Promise((resolve,reject)=>{
 if(server.listening)return resolve();
 server.once('listening',resolve);
 server.once('error',reject)
});
const base='http://127.0.0.1:8787';
const checks=[
 ['root','/', 'GET',200],['index','/index.html','GET',200],
 ['ui script','/app.mjs','GET',200],['stylesheet','/style.css','GET',200],
 ['fictional cases','/materials.mjs','GET',200],['head','/','HEAD',200],
 ['no answer key','/fictional_transfer_key.mjs','GET',404],
 ['no source traversal','/../src/politics_fantasy/fictional_transfer_key.mjs','GET',404],
 ['no encoded traversal','/%2e%2e/src/politics_fantasy/fictional_transfer_key.mjs','GET',404],
 ['no query data','/?q=case','GET',404],['no analytics','/analytics','GET',404],
 ['no post','/','POST',405],['no put','/','PUT',405],
 ['no delete','/','DELETE',405],['no query on JS','/app.mjs?q=1','GET',404]
];
let pass=0,fail=[];
try{
 for(const [name,path,method,expected] of checks){
  const res=await fetch(base+path,{method});
  const body=method==='HEAD'?'':await res.text();
  let ok=res.status===expected
   &&res.headers.get('content-security-policy')?.includes("connect-src 'none'")
   &&res.headers.get('x-content-type-options')==='nosniff'
   &&!res.headers.has('set-cookie')
   &&!res.headers.has('access-control-allow-origin');
  if(name==='ui script')ok&&=!body.includes('evaluateFictionalTransfer')&&!body.includes('localStorage')&&!body.includes('fetch(');
  if(name==='fictional cases')ok&&=body.includes('fictionalTransferItems')&&!body.includes('evaluateFictionalTransfer');
  if(ok)pass++;else fail.push({name,status:res.status,expected})
 }
}finally{await new Promise(done=>server.close(done))}
console.log(JSON.stringify({node:process.version,pass,total:checks.length,fail},null,2));
assert.equal(pass,checks.length);
