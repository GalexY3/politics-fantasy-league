/** Sidecar achievements V1 contract. No AB Atlas mutation or real-person scores. */
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { Script } from 'node:vm';

const dir=dirname(fileURLToPath(import.meta.url));
const parent=join(dir,'..','ab_atlas');
const registry=JSON.parse(readFileSync(join(parent,'ACHIEVEMENTS_REGISTRY.json'),'utf8'));
const page=readFileSync(join(parent,'ACHIEVEMENTS_Atlas_Politics_Fantasy.html'),'utf8');
const atlas=readFileSync(join(parent,'AB_Atlas_Politics_Fantasy.html'),'utf8');

test('versioned registry preserves original 90 IDs and supports audited new goals',()=>{
  assert.equal(registry.schema,'pfl.achievements.v1');
  assert.ok(registry.version>=1);
  assert.equal(registry.tracks.length,9);
  assert.equal(registry.tracks.reduce((n,t)=>n+t.weight,0),100);
  const originalIds=new Set(registry.change_log[0].affected_ids);
  assert.equal(originalIds.size,90);
  assert.ok(registry.achievements.length>=90);
  const ids=new Set(registry.achievements.map(a=>a.id));
  assert.equal(ids.size,registry.achievements.length);
  for(const id of originalIds)assert.ok(ids.has(id),'Missing historical ID: '+id);
  for(const id of ids){
    if(originalIds.has(id))continue;
    assert.ok(registry.change_log.some(e=>e.type==='achievement.created'&&e.achievement_id===id),id);
  }
  for(const section of registry.tracks){
    const group=registry.achievements.filter(a=>a.track_id===section.id);
    assert.ok(group.length>=10,section.id);
    for(const a of group){
      assert.ok(a.title.length>=8,a.id);
      assert.ok(a.criteria.length>=45,a.id);
      assert.ok(['locked','unlocked','retired'].includes(a.status));
      if(a.status==='unlocked'){assert.ok(a.evidence.length);assert.ok(a.verified_by);assert.ok(a.verified_at);}
      else {assert.deepEqual(a.evidence,[]);assert.equal(a.verified_by,null);}
      for(const dep of a.prerequisites)assert.ok(ids.has(dep));
    }
  }
});

test('V4 contract preserved and achievement progress never replaces existing metrics',()=>{
  assert.equal(registry.v4_baseline.progress_contractual_percent,36.9);
  assert.equal(registry.v4_baseline.critical_release_gates_passed,0);
  const weighted=registry.tracks.reduce((sum,t)=>sum+t.weight*t.baseline_progress_pct/100,0);
  assert.ok(Math.abs(weighted-36.9)<1e-9);
  assert.match(registry.policy.symbolic,/never automatically gives project 100%/);
  assert.match(registry.policy.scoring,/separate from contractual V4/);
});

test('audit chain and no automatically conferred achievements',()=>{
  assert.equal(registry.change_log.length,registry.version);
  assert.equal(registry.change_log[0].type,'registry.created');
  assert.equal(registry.change_log[0].affected_ids.length,90);
  for(const [i,e] of registry.change_log.entries()){assert.equal(e.seq,i+1);assert.equal(e.registry_version,i+1);}
  for(const a of registry.achievements.filter(a=>a.status==='unlocked')){
    assert.equal(registry.change_log.filter(e=>e.achievement_id===a.id).at(-1)?.type,'achievement.unlocked');
  }
});

test('Atlas contains a reachable achievements tab and same-folder iframe',()=>{
  assert.match(atlas,/data-tab="achievements"/);
  assert.match(atlas,/id="pane-achievements"/);
  assert.match(atlas,/src="ACHIEVEMENTS_Atlas_Politics_Fantasy.html"/);
  assert.match(atlas,/achievements:'Logros de Politics Fantasy'/);
});

test('Achievements UI script parses as JavaScript and embeds exact initial registry',()=>{
  const match=page.match(/<script type="application\/json" id="baseline">([\s\S]+?)<\/script><script>([\s\S]+?)<\/script>/);
  assert.ok(match,'embedded data and script blocks');
  new Script(match[2],{filename:'achievements-browser.js'});
  const snapshot=JSON.parse(match[1]);
  assert.deepEqual(snapshot,registry);
});

test('Achievement UI offers evidence, reversible retirement and audited JSON export',()=>{
  for(const feature of ['achievement.unlocked','achievement.relocked','achievement.retired','achievement.restored','achievement.created','achievement.edited']){
    assert.ok(page.includes(feature),feature);
  }
  assert.match(page,/function validate\(x\)/);
  assert.match(page,/localStorage\.setItem/);
  assert.match(page,/ACHIEVEMENTS_REGISTRY\.json/);
  assert.match(page,/const verifier=prompt/);
  assert.equal((page.match(/id="export"/g)||[]).length,1);
});
