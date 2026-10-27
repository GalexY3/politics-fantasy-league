from copy import deepcopy
import pytest
from politics_fantasy.progress_api import evaluate_scope, InvalidScope

BASE = {"scope_id": "PFL-V1-20261026", "revision": 4,
        "tracks": [{"id": "test", "name": "Synthetic", "weight": 100,
                    "milestones": [{"id": "test.good", "name": "Synthetic item",
                                    "why": "For differential testing",
                                    "size": 1, "level": 3,
                                    "evidence_ref": "synthetic/test",
                                    "evidence_class": "TEST"}]}]}

def test_baseline_stays_nonrelease():
    outcome = evaluate_scope(deepcopy(BASE))
    assert outcome["progress_pct"] == 60.0
    assert len(outcome["release_blockers"]) == 6
    assert outcome["global_status"] == "NOT_PUBLIC_RELEASE_READY"

@pytest.mark.parametrize("field,value", [
    ("id", "INVALID"),
    ("name", 7),
    ("why", 7),
    ("evidence_ref", "x"),
    ("size", 10001),
    ("size", float("nan")),
])
def test_bad_milestone_fails_closed(field, value):
    scope = deepcopy(BASE)
    scope["tracks"][0]["milestones"][0][field] = value
    with pytest.raises(InvalidScope):
        evaluate_scope(scope)

def test_bad_family_rejected():
    scope = deepcopy(BASE)
    scope["scope_id"] = "PFL-V2-20261026"
    with pytest.raises(InvalidScope):
        evaluate_scope(scope)

def test_missing_track_name_rejected():
    scope = deepcopy(BASE)
    del scope["tracks"][0]["name"]
    with pytest.raises(InvalidScope):
        evaluate_scope(scope)
