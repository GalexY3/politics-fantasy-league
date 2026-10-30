import assert from 'node:assert/strict';
import {mkdtemp,mkdir,writeFile,rm} from 'node:fs/promises';
import {tmpdir} from 'node:os';
import {resolve,join} from 'node:path';
import {spawnSync} from 'node:child_process';
import {replayVerifiedSource} from '../scripts/replay_forecastbench_vintages.mjs';
import {SOURCE_VINTAGES} from '../src/politics_fantasy/forecastbench_vintage_replay.mjs';
let pass=0;
async function check(title,fn){await fn();pass++;process.stdout.write('PASS '+pass+' '+title+'\n')}
const first='2026-10-08T00:00:00Z',last='2026-10-29T16:00:00Z';
await check('published source version plan has three distinct original SHA sets',()=>{
 assert.equal(SOURCE_VINTAGES.length,3);
 assert.notEqual(SOURCE_VINTAGES[0].cohorts['2026-09-27'].resolutions,SOURCE_VINTAGES[2].cohorts['2026-09-27'].resolutions);
});
await check('missing directory rejected before reading',async()=>{
 await assert.rejects(replayVerifiedSource({snapshot_dir:'',from_instant:first,to_instant:last}),/SOURCE_DIR_REQUIRED/);
});
await check('prepublication source failure occurs without file IO',async()=>{
 await assert.rejects(replayVerifiedSource({snapshot_dir:'/no/real/path',from_instant:'2026-10-01T23:59:59Z',to_instant:last}),/NO_VERIFIED_PUBLIC_VINTAGE/);
});
await check('reverse-ordered snapshots rejected before file IO',async()=>{
 await assert.rejects(replayVerifiedSource({snapshot_dir:'/no/real/path',from_instant:last,to_instant:first}),/INVALID_REPLAY_ORDER/);
});
const folder=await mkdtemp(join(tmpdir(),'pfl-public-vintage-'));
try{
 const v=SOURCE_VINTAGES[0];
 const path=join(folder,v.commit,'question_sets','2026-09-27-llm.json');
 await mkdir(resolve(path,'..'),{recursive:true});
 await writeFile(path,Buffer.from('{"personal":"do not print"}'));
 await check('file from correctly named original commit rejected if byte hash wrong',async()=>{
  await assert.rejects(replayVerifiedSource({snapshot_dir:folder,from_instant:first,to_instant:last}),/ORIGINAL_VINTAGE_BLOB_MISMATCH/);
 });
 await check('CLI error never prints raw question, local path or file contents',()=>{
  const a=spawnSync(process.execPath,['scripts/replay_forecastbench_vintages.mjs','--snapshots-dir',folder,'--from',first,'--to',last],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(a.status,2);assert.equal(a.stdout,'');assert.equal(a.stderr,'REPLAY_FAILED:ORIGINAL_VINTAGE_BLOB_MISMATCH\n');
  assert.equal(a.stderr.includes(folder),false);assert.equal(a.stderr.includes('personal'),false);
 });
 await check('CLI bad args do not open source paths',()=>{
  const a=spawnSync(process.execPath,['scripts/replay_forecastbench_vintages.mjs','--snapshots-dir',folder,'--wrong',first,'--to',last],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(a.status,2);assert.equal(a.stderr,'REPLAY_FAILED:USAGE_SNAPSHOTS_DIR_FROM_TO\n');
 });
 await check('CLI before first source commit rejects non-existent directory before IO',()=>{
  const a=spawnSync(process.execPath,['scripts/replay_forecastbench_vintages.mjs','--snapshots-dir',folder,'--from','2026-10-01T23:59:59Z','--to',last],{cwd:process.cwd(),encoding:'utf8'});
  assert.equal(a.status,2);assert.equal(a.stderr,'REPLAY_FAILED:NO_VERIFIED_PUBLIC_VINTAGE\n');
 });
}finally{await rm(folder,{recursive:true,force:true})}
process.stdout.write('PFL public original bitemporal CLI '+pass+'/8 PASS\n');
