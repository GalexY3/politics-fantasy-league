"""Offline early/late comparison of genuine, self-contained S9 browser exports.

All test inputs are generated from the unchanged author-closed Python registry.
The script must never try to resolve original files, account data or URLs.
"""
from __future__ import annotations

from copy import deepcopy
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from politics_fantasy.scientific_registry import (
    enroll_synthetic_fixture, query_registry,
)
from scripts import compare_scientific_exports as comparison

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "compare_scientific_exports.py"
ENV = {**os.environ, "PYTHONIOENCODING": "utf-8",
       "PYTHONDONTWRITEBYTECODE": "1"}


def export_of(registry_db: Path, *, cut: str, valid_at: str = "2026-09-15",
              family: str = "all", published: str = "as_of") -> dict:
    result = query_registry(registry_db, cut=cut, valid_at=valid_at,
                            family=family, published_until=published)
    receipt = result["snapshot_receipt"]
    return {
        "schema": "pfl.synthetic_scientific_registry_browser_export.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "query": {
            "cut": cut, "as_of": result["as_of"], "valid_at": valid_at,
            "family": family, "published_until": result["published_until"],
        },
        "source_contract": result["schema"],
        "receipt_schema": receipt["schema"],
        "snapshot_receipt": receipt,
        "R5": "STOP_R5",
        "release_gates_passed": 0,
        "scientific_ab_cycles": 0,
        "external_authenticity_certified": False,
        "rights_for_public_display_admitted": False,
    }


def files(tmp_path: Path, *, family: str = "all",
          valid_at: str = "2026-09-15") -> tuple[Path, Path]:
    db = tmp_path / "science.sqlite3"
    e = export_of(db, cut="early", valid_at=valid_at, family=family)
    l = export_of(db, cut="late", valid_at=valid_at, family=family)
    paths = (tmp_path / "early.json", tmp_path / "late.json")
    for path, data in zip(paths, (e, l)):
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                        encoding="utf-8")
    return paths


def cli(*paths: Path) -> tuple[int, dict]:
    result = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), *(str(p) for p in paths)],
        cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8",
        check=False, timeout=20,
    )
    assert not result.stderr
    return result.returncode, json.loads(result.stdout)


def test_offline_comparison_two_verified_public_cuts_and_graphs(tmp_path):
    early, late = files(tmp_path)
    code, result = cli(early, late)
    assert code == 0 and result["status"] == "PASS"
    assert result["comparison_kind"] == "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE"
    assert result["source_integrity_verified_independently"] is True
    assert result["early"]["sha256"] != result["late"]["sha256"]
    assert result["descriptors"]["early_visible"] == 2
    assert result["descriptors"]["late_visible"] == 6
    assert len(result["descriptors"]["visible_only_late"]) == 4
    assert result["descriptors"]["visible_only_early"] == []
    assert result["descriptors"]["same_id_changed_revision_or_sha"] == []
    assert result["absence_means_negative"] is False
    assert result["independent_denominator_established"] is False
    assert result["publisher_identity_verified"] is False
    assert result["rights_for_public_display_admitted"] is False
    assert result["scientific_ab_cycles"] == result["release_gates_passed"] == 0
    assert result["R5"] == "STOP_R5"
    public = json.dumps(result)
    assert "AUTHOR_ALPHA:" not in public
    assert "AUTHOR_BETA:" not in public
    assert "SYN:S9_" not in public


def test_new_synthetic_intakes_change_only_late_visibility_not_real_admission(tmp_path):
    db = tmp_path / "science.sqlite3"
    for name in ("sandbox_alpha_v1", "sandbox_beta_v1",
                 "sandbox_alpha_v2", "sandbox_bad_issuer"):
        enroll_synthetic_fixture(db, name)
    e, l = (export_of(db, cut=cut) for cut in ("early", "late"))
    summary = comparison.compare(
        comparison.load_export(_write(tmp_path / "early.json", e)),
        comparison.load_export(_write(tmp_path / "late.json", l)),
    )
    assert summary["typed_and_sandbox_counts"]["early"]["synthetic_intake_records"] == 0
    assert summary["typed_and_sandbox_counts"]["late"]["synthetic_intake_records"] == 4
    assert summary["typed_and_sandbox_counts"]["late"]["intake_revisions_not_new_decisions"]
    assert summary["real_sources_admitted"] == 0
    assert summary["R5"] == "STOP_R5"


def _write(path: Path, payload: dict) -> Path:
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


@pytest.mark.parametrize("corruption", (
    "tampered_digest", "fake_rights", "duplicate_key", "invalid_json", "too_large",
))
def test_corrupted_early_receipt_never_yields_comparison(tmp_path, corruption):
    early, late = files(tmp_path)
    source = json.loads(early.read_text(encoding="utf-8"))
    if corruption == "tampered_digest":
        source["snapshot_receipt"]["sha256"] = "f" * 64
        _write(early, source)
    elif corruption == "fake_rights":
        source["rights_for_public_display_admitted"] = True
        _write(early, source)
    elif corruption == "duplicate_key":
        raw = early.read_text(encoding="utf-8")
        early.write_text(raw.replace('"R5": "STOP_R5",',
                                    '"R5": "STOP_R5", "R5": "STOP_R5",', 1),
                         encoding="utf-8")
    elif corruption == "invalid_json":
        early.write_bytes(b"{not-json")
    else:
        early.write_bytes(b"X" * 1_048_577)
    code, report = cli(early, late)
    assert code != 0 and report["status"] == "FAIL"
    assert report["publisher_identity_verified"] is False
    assert report["rights_for_public_display_admitted"] is False
    assert "snapshot" not in report


def test_swapped_or_mismatched_filters_fail_closed(tmp_path):
    early, late = files(tmp_path)
    status, body = cli(late, early)
    assert status == 1 and body["error_code"] == "EARLY_AND_LATE_EXPORTS_REQUIRED"
    db = tmp_path / "science.sqlite3"
    _write(late, export_of(db, cut="late", family="CHAIN"))
    status, body = cli(early, late)
    assert status == 1 and body["error_code"] == "COMPARISON_FILTERS_DIFFER"
    _write(late, export_of(db, cut="late", valid_at="2026-10-10"))
    status, body = cli(early, late)
    assert status == 1 and body["error_code"] == "COMPARISON_FILTERS_DIFFER"


def test_missing_source_and_extra_argument_do_not_expose_paths(tmp_path):
    early, late = files(tmp_path)
    missing = tmp_path / "private-dir" / "not-found.json"
    for argv in ((missing, late), (early, late, missing)):
        code, body = cli(*argv)
        assert code != 0 and body["status"] == "FAIL"
        assert str(tmp_path) not in json.dumps(body)
        assert "username" not in json.dumps(body)
