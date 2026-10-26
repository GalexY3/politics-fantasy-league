"""Scope-progress model: deterministic tests independent of political affiliation."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from politics_fantasy.progress_api import progress_status, evaluate_scope, InvalidScope, DEFAULT_SCOPE


def baseline():
    return json.loads(DEFAULT_SCOPE.read_text(encoding="utf8"))


def test_current_v2_global_and_tracks():
    r = progress_status()
    assert r["ok"] is True
    assert abs(r["progress_pct"] - 35.45) < 1e-8
    assert r["progress_display_pct"] == 35.5
    assert r["revision"] == 2
    assert r["track_count"] == 9
    assert r["milestone_count"] == 36
    assert sum(t["weight"] for t in r["tracks"]) == 100
    assert abs(sum(t["contribution_pp"] for t in r["tracks"]) - 35.525) < 1e-8


def test_maturity_and_release_gates():
    r = progress_status()
    assert r["level_histogram"] == {
        "0": 10, "1": 7, "2": 4, "3": 13, "4": 2, "5": 0
    }
    assert len(r["release_blockers"]) == 6
    assert r["global_status"] == "NOT_PUBLIC_RELEASE_READY"
    assert r["real_people_scoring_ready"] is False


def test_scope_expansion_changes_denominator_only():
    s = baseline()
    s["revision"] = 2
    s["tracks"][0]["milestones"].append({
        "id": "src.full_local", "name": "Nationwide municipal roster",
        "size": 1, "level": 0, "why": "Scope added without any imported original data",
        "evidence_ref": "research/BRANCH30J_20261026/REPORT.md",
        "evidence_class": "ABSENT"
    })
    r = evaluate_scope(s)
    assert abs(r["progress_pct"] - 33.83) < 1e-8


def test_invalid_weight_rejected():
    s = baseline()
    s["tracks"][0]["weight"] = 19
    with pytest.raises(InvalidScope, match="WEIGHTS_MUST_TOTAL_100"):
        evaluate_scope(s)


def test_unverified_source_cannot_make_progress(tmp_path: Path):
    s = baseline()
    s["tracks"][0]["milestones"][0]["evidence_ref"] = ""
    p = tmp_path / "scope.json"
    p.write_text(json.dumps(s))
    assert progress_status(p)["error"] == "SCOPE_INVALID_OR_UNVERIFIED"


def test_unknown_scope_returns_error(tmp_path: Path):
    s = baseline()
    s["scope_id"] = "PFL-OTHER-20261026"
    p = tmp_path / "scope.json"
    p.write_text(json.dumps(s))
    assert progress_status(p)["ok"] is False


def test_missing_file_fails_closed(tmp_path: Path):
    assert progress_status(tmp_path / "missing.json")["error"] == "SCOPE_UNAVAILABLE"
