import assert from 'node:assert/strict';
import {PUBLIC_DATASET_PIN,gitBlobHash,verifyBlobAgainstExpected,verifyPinnedForecastBenchBuffers}
 from '../src/politics_fantasy/forecastbench_provenance.mjs';
let n=0;
const test=(name,fn)=>{fn();n++};
test('known Git object SHA1 independent of implementation',()=>{
 assert.equal(gitBlobHash(Buffer.from('abc')),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f');
});
test('different raw bytes never match digest',()=>{
 assert.notEqual(gitBlobHash(Buffer.from('abC')),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f');
});
test('successful synthetic byte identity says NO authorization',()=>{
 const r=verifyBlobAgainstExpected(Buffer.from('abc'),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f');
 assert.equal(r.byte_identity_matches_expected_blob,true);
 assert.equal(r.independently_authenticated,false);
 assert.equal(r.licensed_for_personal_processing,false);
});
test('mismatched source content is fatal',()=>{
 assert.throws(()=>verifyBlobAgainstExpected(Buffer.from('abC'),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f'),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
});
test('missing hash and false human flag are rejected',()=>{
 for(const h of ['','X'.repeat(40),'f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f\n']){
  assert.throws(()=>verifyBlobAgainstExpected(Buffer.from('abc'),h),/INVALID_EXPECTED_GIT_BLOB_SHA/);
 }
});
test('string vs Buffer is rejected to preserve original bytes',()=>{
 assert.throws(()=>gitBlobHash('abc'),/RAW_BUFFER_REQUIRED/);
 assert.throws(()=>gitBlobHash(new Uint8Array([97,98,99])),/RAW_BUFFER_REQUIRED/);
});
test('empty bytes rejected',()=>assert.throws(()=>gitBlobHash(Buffer.alloc(0)),/SOURCE_BYTES_OUT_OF_BOUNDS/));
test('oversized source rejected before crypto or parsed JSON',()=>assert.throws(()=>gitBlobHash(Buffer.alloc(5_000_001)),/SOURCE_BYTES_OUT_OF_BOUNDS/));
test('four exact upstream blob hashes frozen',()=>{
 assert.equal(PUBLIC_DATASET_PIN.commit,'027ba0b3017a60e0e64602d724284ac6b2d91134');
 assert.equal(Object.keys(PUBLIC_DATASET_PIN.blobs).length,4);
 assert.equal(PUBLIC_DATASET_PIN.blobs['question_sets/2026-10-11-llm.json'],'fe9772f2275edcada671c4082cf9103185f1becf');
});
test('cannot pass synthetic bytes off as pinned original files',()=>{
 const fake=Object.fromEntries(Object.keys(PUBLIC_DATASET_PIN.blobs).map(x=>[x,Buffer.from('abc')]));
 assert.throws(()=>verifyPinnedForecastBenchBuffers(fake),/ORIGINAL_SOURCE_BYTES_MISMATCH/);
});
test('missing and extra dataset file fail before verification',()=>{
 const one={'question_sets/2026-09-27-llm.json':Buffer.from('abc')};
 assert.throws(()=>verifyPinnedForecastBenchBuffers(one),/MISSING_OR_EXTRA_SOURCE_FILE/);
 assert.throws(()=>verifyPinnedForecastBenchBuffers({...one,'evil':Buffer.from('abc')}),/MISSING_OR_EXTRA_SOURCE_FILE/);
});
test('prototype/array arguments cannot smuggle filenames',()=>{
 assert.throws(()=>verifyPinnedForecastBenchBuffers(null),/INVALID_PINNED_FILES/);
 assert.throws(()=>verifyPinnedForecastBenchBuffers([]),/INVALID_PINNED_FILES/);
});
test('unknown content rights remain unasserted',()=>{
 assert.equal(PUBLIC_DATASET_PIN.license,'CC-BY-SA-4.0');
 assert.equal(Object.isFrozen(PUBLIC_DATASET_PIN.blobs),true);
 assert.equal(Object.isFrozen(PUBLIC_DATASET_PIN),true);
});
process.stdout.write('PFL original source byte gate '+n+'/13 PASS\n');
