/** First-party Node suite, callable from any working directory. */
import {readdirSync} from 'node:fs';
import {resolve,join} from 'node:path';
import {fileURLToPath} from 'node:url';
import {spawnSync} from 'node:child_process';
const root=fileURLToPath(new URL('../',import.meta.url));
function discover(dir){return readdirSync(dir,{withFileTypes:true}).flatMap(e=>e.isDirectory()?discover(join(dir,e.name)):(/^test_.*\.(mjs|cjs)$/.test(e.name)?[join(dir,e.name)]:[]));}
const files=[...discover(resolve(root,'tests')),...discover(resolve(root,'src/politics_fantasy'))].sort();
if(files.length===0)throw Error('NO_NODE_TESTS_DISCOVERED');
console.log(JSON.stringify({test_files:files.length,scope:['tests','src/politics_fantasy'],archives_excluded:true}));
const r=spawnSync(process.execPath,['--test',...files],{cwd:root,stdio:'inherit'});
if(r.error)throw r.error;
process.exitCode=r.status??1;
