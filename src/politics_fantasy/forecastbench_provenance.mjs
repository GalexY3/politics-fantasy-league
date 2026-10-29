/**
 * Independent local byte-integrity gate for the original PUBLIC ForecastBench
 * question+resolution records. No HTTP, no person history, no license grants.
 *
 * Original data: Forecasting Research Institute, Karger et al. (ICLR 2025),
 * forecastingresearch/forecastbench-datasets, datasets CC BY-SA 4.0.
 * Pinned original commit: 027ba0b3017a60e0e64602d724284ac6b2d91134.
 * These SHA1 objects were checked against original GitHub metadata before
 * this module was written; SHA1 is a Git identity check, not a security
 * signature, license review, participant privacy certification or SHA256.
 */
import {createHash} from 'node:crypto';
export const PUBLIC_DATASET_PIN = Object.freeze({
 repo:'forecastingresearch/forecastbench-datasets',
 commit:'027ba0b3017a60e0e64602d724284ac6b2d91134',
 license:'CC-BY-SA-4.0',
 blobs:Object.freeze({
  'question_sets/2026-09-27-llm.json':'d4c7e1286d76fbaa1c9911ffb0b97cbcc16440c0',
  'resolution_sets/2026-09-27_resolution_set.json':'b2ee53f09407e2b555668f66e286073ace6d5fce',
  'question_sets/2026-10-11-llm.json':'fe9772f2275edcada671c4082cf9103185f1becf',
  'resolution_sets/2026-10-11_resolution_set.json':'d8416bccbfcd4736e9772748bb42fd4cc403db7e'
 })
});
const HEX=/^[a-f0-9]{40}$/;
export function gitBlobHash(bytes) {
 if(!Buffer.isBuffer(bytes))throw Error('RAW_BUFFER_REQUIRED');
 if(bytes.byteLength===0||bytes.byteLength>5_000_000)throw Error('SOURCE_BYTES_OUT_OF_BOUNDS');
 return createHash('sha1').update(Buffer.from('blob '+bytes.length+'\0','ascii')).update(bytes).digest('hex');
}
export function verifyBlobAgainstExpected(bytes,expected){
 if(typeof expected!=='string'||!HEX.test(expected))throw Error('INVALID_EXPECTED_GIT_BLOB_SHA');
 const actual=gitBlobHash(bytes);
 if(actual!==expected)throw Error('ORIGINAL_SOURCE_BYTES_MISMATCH');
 return Object.freeze({byte_identity_matches_expected_blob:true,
                      content_bytes:bytes.byteLength,blob_sha1:actual,
                      independently_authenticated:false,licensed_for_personal_processing:false});
}
export function verifyPinnedForecastBenchBuffers(buffers){
 if(buffers===null||typeof buffers!=='object'||Array.isArray(buffers))throw Error('INVALID_PINNED_FILES');
 const required=Object.keys(PUBLIC_DATASET_PIN.blobs);
 const actual=Reflect.ownKeys(buffers);
 if(actual.length!==required.length||actual.some(k=>typeof k!=='string'||!required.includes(k)))throw Error('MISSING_OR_EXTRA_SOURCE_FILE');
 const outputs=Object.create(null);
 for(const name of required){
  if(!Object.hasOwn(buffers,name))throw Error('MISSING_OR_EXTRA_SOURCE_FILE');
  outputs[name]=verifyBlobAgainstExpected(buffers[name],PUBLIC_DATASET_PIN.blobs[name]);
 }
 return Object.freeze({status:'FOUR_PINNED_PUBLIC_GIT_BLOBS_MATCH',
   upstream_repo:PUBLIC_DATASET_PIN.repo,upstream_commit:PUBLIC_DATASET_PIN.commit,
   checked_files:required.length,per_file:{...outputs},
   release_ready:false,personal_record_rights_established:false,
   meaning:'Git blob identity is NOT rights, independent publisher authenticity or causal evidence'});
}
