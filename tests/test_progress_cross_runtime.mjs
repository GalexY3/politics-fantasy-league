import {test} from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {evaluate, compare} from '../src/politics_fantasy/progress_model.mjs';

const read = name => JSON.parse(readFileSync(new URL('../product/' + name, import.meta.url), 'utf8'));
const scopes = [read('progress_scope_v3_20261026.json'), read('progress_scope_v4_20261027.json')];
const clone = obj => structuredClone(obj);

if (process.argv.includes('--json')) {
  // pytest calls this same native implementation; no second JS evaluator.
  process.stdout.write(JSON.stringify(scopes.map(evaluate)));
} else {
  test('native V3 and V4 evaluate and compare the full snapshots', () => {
    const [v3, v4] = scopes.map(evaluate);
    assert.ok(Math.abs(v3.progress_pct - 36.35) < 1e-9);
    assert.ok(Math.abs(v4.progress_pct - 36.90) < 1e-9);
    for (const outcome of [v3, v4]) {
      assert.equal(outcome.track_count, 9);
      assert.equal(outcome.milestone_count, 36);
      assert.equal(outcome.release_blockers.length, 6);
      assert.equal(outcome.global_status, 'NOT_PUBLIC_RELEASE_READY');
      assert.equal(outcome.real_people_scoring_ready, false);
    }
    const comparison = compare(...scopes);
    assert.ok(Math.abs(comparison.work_effect_pp - 0.55) < 1e-9);
    assert.ok(Math.abs(comparison.scope_effect_pp) < 1e-9);
    const oldLevels = new Map(scopes[0].tracks.flatMap(t => t.milestones).map(m => [m.id, m.level]));
    const changes = scopes[1].tracks.flatMap(t => t.milestones)
      .filter(m => oldLevels.get(m.id) !== m.level).map(m => [m.id, oldLevels.get(m.id), m.level]);
    assert.deepEqual(changes, [['id.real', 0, 1], ['ev.person', 0, 1]]);
  });

  test('a missing critical milestone remains a blocker', () => {
    const modified = clone(scopes[1]);
    for (const track of modified.tracks)
      track.milestones = track.milestones.filter(m => m.id !== 'src.registry');
    const result = evaluate(modified);
    assert.ok(result.release_blockers.includes('Registro de partidos/candidaturas sin originales auditados'));
    assert.equal(result.global_status, 'NOT_PUBLIC_RELEASE_READY');
  });

  test('NaN is rejected rather than accepted as a numeric size', () => {
    const modified = clone(scopes[1]);
    modified.tracks[0].milestones[0].size = NaN;
    assert.throws(() => evaluate(modified), /BAD_MILESTONE_SIZE/);
  });

  test('different families report lineage mismatch; unsupported matching families still fail validation', () => {
    const different = clone(scopes[1]);
    different.scope_id = 'PFL-V2-20261026';
    assert.throws(() => compare(scopes[0], different), /SCOPE_LINEAGE_MISMATCH/);
    const sameUnsupported = clone(scopes[0]);
    sameUnsupported.scope_id = different.scope_id;
    assert.throws(() => compare(sameUnsupported, different), /BAD_SCOPE_VERSION/);
  });
}
