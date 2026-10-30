/**
 * ABH30-C11: read-only local CLI for three pre-audited public ForecastBench
 * resolution-set revision pairs. Git object identity is NOT publisher truth,
 * event-level first_public_at, personal-data rights or causal validation.
 * Files are never uploaded; output is aggregate only.
 */
import {readFileSync, lstatSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {fileURLToPath} from 'node:url';
import {createHash} from 'node:crypto';
import {auditPublicRawRevision} from '../src/politics_fantasy/forecastbench_raw_revision_guard.mjs';

const HEX = /^[a-f0-9]{40}$/;
const MAX_BYTES = 5_000_000;
export const PINNED_PAIRS = Object.freeze({
  sep07to08: Object.freeze({cohort:'2026-09-27',
    before:Object.freeze({git_commit:'4eafa5cdda4d9fbf3542ea9f5f71050b9dd89110',git_blob:'0b67cfec67fad4b23899e8e48c6ca3a034344edc',committed_at:'2026-10-07T07:19:29Z'}),
    after:Object.freeze({git_commit:'d354d26d6f3feb03bacc363f6b346232645e8550',git_blob:'2efa48b677c7c4e8a4827585d49c4f59393e233e',committed_at:'2026-10-08T07:01:49Z'})}),
  sep11to12: Object.freeze({cohort:'2026-09-27',
    before:Object.freeze({git_commit:'3928408907498c991bc367c2d3493241aa19e516',git_blob:'424965825aae022f5861b69d17880665cd3026bb',committed_at:'2026-10-11T06:35:43Z'}),
    after:Object.freeze({git_commit:'d6dac818ec036aa8fa41dfc1fcb369d24ca81ce4',git_blob:'ea2f96ee0b30f248f3b9d1b61bd63fa03e938ec3',committed_at:'2026-10-12T07:03:09Z'})}),
  oct23to24: Object.freeze({cohort:'2026-10-11',
    before:Object.freeze({git_commit:'f3d8a4f83754f6c26990c67c69185f91f214c30c',git_blob:'1556a17106131cf8a7d7cb3b33122d18c3b9ef6a',committed_at:'2026-10-23T06:53:25Z'}),
    after:Object.freeze({git_commit:'420dc4f3a1e23774347da7b199c58592dce45448',git_blob:'0c535475a4037a47ecf009c933d635fd49f67e29',committed_at:'2026-10-24T07:39:55Z'})})
});
export function gitBlobSha1(bytes) {
  if (!Buffer.isBuffer(bytes) || bytes.length===0 || bytes.length>MAX_BYTES)
    throw Error('BOUNDED_PUBLIC_SOURCE_BYTES_REQUIRED');
  return createHash('sha1').update(Buffer.from(`blob ${bytes.length}\0`,'ascii')).update(bytes).digest('hex');
}
function parseOne(bytes, expected, cohort) {
  if (!expected || !HEX.test(expected.git_blob) || gitBlobSha1(bytes)!==expected.git_blob)
    throw Error('PINNED_PUBLIC_GIT_BLOB_MISMATCH');
  let data;
  try { data=JSON.parse(bytes.toString('utf8')); }
  catch { throw Error('INVALID_PUBLIC_SOURCE_JSON'); }
  return {cohort,data,git_commit:expected.git_commit,git_blob:expected.git_blob,committed_at:expected.committed_at};
}
export function auditRawPairBuffers(beforeBytes,afterBytes,pins) {
  if(!pins || !pins.cohort || !pins.before || !pins.after)
    throw Error('INVALID_PINNED_PAIR');
  const before=parseOne(beforeBytes,pins.before,pins.cohort);
  const after=parseOne(afterBytes,pins.after,pins.cohort);
  const audit=auditPublicRawRevision(before,after);
  return Object.freeze({...audit,validated_against_supplied_git_pins:true,
    pins_are_upstream_authenticated_here:false,
    local_bytes_git_sha1_verified:true,source_first_public_at_per_event_verified:false,
    no_person_data_permission_claim:true});
}
function readStrictFile(path) {
  const st=lstatSync(path);
  if(!st.isFile() || st.isSymbolicLink() || st.size===0 || st.size>MAX_BYTES)
    throw Error('UNSAFE_PUBLIC_FILE');
  return readFileSync(path);
}
export function auditPinnedPairFromDir(key,directory) {
  if(!Object.hasOwn(PINNED_PAIRS,key))throw Error('UNKNOWN_PUBLIC_REVISION_PAIR');
  if(typeof directory!=='string'||!directory.trim())throw Error('MISSING_SOURCE_DIR');
  const pins=PINNED_PAIRS[key],folder=resolve(directory);
  const before=readStrictFile(join(folder,`${key}.before.json`));
  const after=readStrictFile(join(folder,`${key}.after.json`));
  const audit=auditRawPairBuffers(before,after,pins);
  return Object.freeze({pair:key,...audit,official_git_pins_in_source_code:true,
    original_repository:'forecastingresearch/forecastbench-datasets',
    original_data_scope:'PUBLIC_NON_PERSON_RESOLUTION_ROWS',
    publisher_licensing_for_individual_forecasts_verified:false,
    release_ready:false});
}
function main(argv) {
  if(argv.length!==4 || argv[0]!=='--pair' || argv[2]!=='--source-dir')
    throw Error('USAGE_--pair_KEY_--source-dir_DIRECTORY');
  const result=auditPinnedPairFromDir(argv[1],argv[3]);
  process.stdout.write(JSON.stringify(result)+'\n');
}
if(process.argv[1] && resolve(process.argv[1])===fileURLToPath(import.meta.url)){
  try { main(process.argv.slice(2)); }
  catch(e) { const known=e instanceof Error && /^[A-Z0-9_-]+$/.test(e.message) ? e.message : 'LOCAL_PUBLIC_SOURCE_IO_OR_SCHEMA_FAILED';
    process.stderr.write('PUBLIC_REVISION_AUDIT_FAILED:'+known+'\n');
    process.exitCode=1; }
}
