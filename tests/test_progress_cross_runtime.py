"""Compare full, unchanged V3/V4 inputs through the Python and JS evaluators."""
from copy import deepcopy
import json
from pathlib import Path
import subprocess

import pytest
from politics_fantasy.progress_api import InvalidScope, evaluate_scope

ROOT = Path(__file__).resolve().parents[1]
SCOPES = [ROOT / 'product/progress_scope_v3_20261026.json',
          ROOT / 'product/progress_scope_v4_20261027.json']
FIELDS = ('schema', 'scope_id', 'revision', 'review_date', 'objective', 'progress_pct',
          'progress_display_pct', 'level_histogram', 'track_count', 'milestone_count',
          'tracks', 'global_status', 'release_blockers', 'real_people_scoring_ready',
          'scientific_grade_separate', 'actor_influence_inferred')


def same_semantics(left, right):
    if isinstance(left, bool) or left is None or isinstance(left, str):
        assert left == right
    elif isinstance(left, (int, float)):
        assert left == pytest.approx(right, rel=0, abs=1e-9)
    elif isinstance(left, list):
        assert len(left) == len(right)
        for a, b in zip(left, right):
            same_semantics(a, b)
    elif isinstance(left, dict):
        assert left.keys() == right.keys()
        for key in left:
            same_semantics(left[key], right[key])
    else:
        pytest.fail(f'Unsupported comparison type: {type(left)}')


def load_scopes():
    return [json.loads(path.read_text(encoding='utf8')) for path in SCOPES]


def test_native_python_and_node_match_full_v3_v4():
    scopes = load_scopes()
    py = [evaluate_scope(scope) for scope in scopes]
    proc = subprocess.run(['node', str(ROOT / 'tests/test_progress_cross_runtime.mjs'), '--json'],
                          cwd=ROOT, capture_output=True, text=True, check=True, encoding='utf8')
    js = json.loads(proc.stdout)
    assert len(js) == len(py) == 2
    for p, j, expected in zip(py, js, (36.35, 36.90)):
        same_semantics({k: p[k] for k in FIELDS}, {k: j[k] for k in FIELDS})
        assert p['progress_pct'] == pytest.approx(expected, rel=0, abs=1e-9)
        assert (p['track_count'], p['milestone_count'], len(p['release_blockers'])) == (9, 36, 6)
    assert py[1]['progress_pct'] - py[0]['progress_pct'] == pytest.approx(0.55, rel=0, abs=1e-9)
    before = {m['id']: m['level'] for t in scopes[0]['tracks'] for m in t['milestones']}
    after = {m['id']: m['level'] for t in scopes[1]['tracks'] for m in t['milestones']}
    assert before.keys() == after.keys()
    assert {k: (before[k], after[k]) for k in before if before[k] != after[k]} == {
        'id.real': (0, 1), 'ev.person': (0, 1)}


def test_missing_critical_milestone_is_still_blocked():
    scope = deepcopy(load_scopes()[1])
    for track in scope['tracks']:
        track['milestones'] = [m for m in track['milestones'] if m['id'] != 'src.registry']
    result = evaluate_scope(scope)
    assert 'Registro de partidos/candidaturas sin originales auditados' in result['release_blockers']
    assert result['global_status'] == 'NOT_PUBLIC_RELEASE_READY'


def test_nan_is_rejected():
    scope = deepcopy(load_scopes()[1])
    scope['tracks'][0]['milestones'][0]['size'] = float('nan')
    with pytest.raises(InvalidScope, match='BAD_SIZE'):
        evaluate_scope(scope)
