import {createHash} from 'node:crypto';
import {readFileSync,readdirSync} from 'node:fs';
import {join} from 'node:path';

// Shared native-CDP download readiness for both existing browser tests.
// Chrome can publish the final .json NAME before finishing its BYTES.
// Readiness is a complete parsed JSON with its exact canonical receipt,
// never a filename, fixed delay, successful HTTP status or stale UI state.
export async function completedJsonDownload(folder,pattern,poll){
 return poll(()=>{
  const name=readdirSync(folder).find(entry=>pattern.test(entry));
  if(!name)return null;
  const data=JSON.parse(readFileSync(join(folder,name),'utf8'));
  const receipt=data?.snapshot_receipt??data?.pair_receipt;
  if(typeof receipt?.canonical_json!=='string'
     ||receipt.sha256!==createHash('sha256').update(receipt.canonical_json,'utf8').digest('hex')
     ||receipt.bytes!==Buffer.byteLength(receipt.canonical_json,'utf8'))
   throw Error('INCOMPLETE_OR_UNVERIFIED_JSON_DOWNLOAD');
  return {name,data};
 },180);
}
