"""Offline early/late comparison of genuine, self-contained S9 browser exports.

All test inputs are generated from the unchanged author-closed Python registry.
The script must never try to resolve original files, account data or URLs.
"""
from __future__ import annotations

from copy import deepcopy
from hashlib import sha256
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


def _pair_receipt(envelope: dict) -> dict:
    """An independent JSON encoder, not the code under test, makes the receipt."""
    scope = {key: value for key, value in envelope.items()
             if key != "pair_receipt"}
    raw = json.dumps(scope, sort_keys=True, separators=(",", ":"),
                     ensure_ascii=False, allow_nan=False).encode("utf-8")
    return {
        "schema": "pfl.synthetic_scientific_registry_browser_pair_receipt.v1",
        "canonicalization": "JSON_UTF8_SORTED_KEYS_COMPACT_V1",
        "canonical_json": raw.decode("utf-8"),
        "bytes": len(raw),
        "sha256": sha256(raw).hexdigest(),
    }


def _pair_export(db: Path, *, valid_at: str = "2026-09-15",
                 family: str = "all", publication: str = "as_of") -> dict:
    """Exactly the stipulated single-browser-export fields, nested in one pair."""
    early_pub = ("as_of" if publication == "as_of"
                 or publication > "2026-10-15T12:00:00Z" else publication)
    pair = {
        "schema": "pfl.synthetic_scientific_registry_browser_pair_export.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "comparison_kind": "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE",
        "exports": {
            "early": export_of(db, cut="early", valid_at=valid_at,
                               family=family, published=early_pub),
            "late": export_of(db, cut="late", valid_at=valid_at,
                              family=family, published=publication),
        },
        "R5": "STOP_R5",
        "release_gates_passed": 0,
        "scientific_ab_cycles": 0,
        "rights_for_public_display_admitted": False,
        "external_authenticity_certified": False,
    }
    pair["pair_receipt"] = _pair_receipt(pair)
    return pair


def _pair_file(tmp_path: Path, pair: dict, filename: str | None = None) -> Path:
    if filename is None:
        filename = "pfl-s9-pair-" + pair["exports"]["early"]["query"]["valid_at"] + (
            "-" + pair["pair_receipt"]["sha256"][:12] + ".json")
    path = tmp_path / filename
    path.write_text(json.dumps(pair, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return path


def _pair_cli(path: Path, *extra: str) -> tuple[int, dict]:
    # Explicit --pair is exclusive with the legacy early.json late.json mode.
    raw = subprocess.run(
        [sys.executable, "-B", str(SCRIPT), "--pair", str(path), *extra],
        cwd=ROOT, env=ENV, capture_output=True, text=True, encoding="utf-8",
        errors="replace", check=False, timeout=20,
    )
    assert not raw.stderr, "FAIL must use structured JSON without paths/tracebacks"
    answer = json.loads(raw.stdout)
    assert answer["schema"] == comparison.SCHEMA
    assert answer["publisher_identity_verified"] is False
    assert answer["rights_for_public_display_admitted"] is False
    assert str(path) not in raw.stdout
    assert "AUTHOR_ALPHA:FILE_1" not in raw.stdout
    return raw.returncode, answer


@pytest.mark.parametrize("family,publication,valid_at,late_sources", [
    ("all", "as_of", "2026-09-15", 6),
    ("all", "2026-09-19T12:00:00Z", "2026-10-10", 2),
    ("all", "2026-10-30T12:00:00Z", "2026-10-10", 6),
    ("CHAIN", "as_of", "2026-09-15", 2),
    ("PP04", "as_of", "2026-09-11", 2),
    ("CHRONICLE", "as_of", "2026-09-15", 2),
])
def test_single_pair_download_compares_identically_to_legacy_two_files(
        tmp_path, family, publication, valid_at, late_sources):
    db = tmp_path / "fixture.sqlite3"
    pair = _pair_export(db, family=family, publication=publication,
                        valid_at=valid_at)
    destination = _pair_file(tmp_path, pair)
    assert destination.name == ("pfl-s9-pair-" + valid_at + "-"
                                + pair["pair_receipt"]["sha256"][:12] + ".json")
    code, by_pair = _pair_cli(destination)
    assert code == 0 and by_pair["status"] == "PASS"
    assert by_pair["pair_sha256"] == pair["pair_receipt"]["sha256"]
    assert by_pair["descriptors"]["late_visible"] == late_sources
    assert by_pair["shared_valid_at"] == valid_at
    assert by_pair["shared_family"] == family
    assert by_pair["R5"] == "STOP_R5"
    assert by_pair["scientific_ab_cycles"] == by_pair["release_gates_passed"] == 0
    assert by_pair["real_sources_admitted"] == 0
    # Legacy CLI remains byte-for-byte compatible at the JSON contract level.
    early_file = _write(tmp_path / "legacy-early.json", pair["exports"]["early"])
    late_file = _write(tmp_path / "legacy-late.json", pair["exports"]["late"])
    old_code, old = cli(early_file, late_file)
    assert old_code == 0
    assert {k: v for k, v in by_pair.items() if k != "pair_sha256"} == old


def test_actual_s9_v4_four_intake_pair_is_persistently_synthetic(tmp_path):
    db = tmp_path / "registry.sqlite3"
    for name in ("sandbox_alpha_v1", "sandbox_beta_v1",
                 "sandbox_alpha_v2", "sandbox_bad_issuer"):
        enroll_synthetic_fixture(db, name)
    pair = _pair_export(db, valid_at="2026-10-10")
    file = _pair_file(tmp_path, pair)
    code, result = _pair_cli(file)
    assert code == 0 and result["status"] == "PASS"
    counts = result["typed_and_sandbox_counts"]
    assert counts["early"]["synthetic_intake_records"] == 0
    assert counts["late"]["synthetic_intake_records"] == 4
    assert counts["late"]["synthetic_assessments"] == 8
    assert counts["late"]["intake_revisions_not_new_decisions"] is True
    assert result["publisher_identity_verified"] is False
    assert result["independent_denominator_established"] is False
    assert _pair_cli(file) == (code, result)


@pytest.mark.parametrize("mutation,error_code", [
    ("extra_outer", "PAIR_CONTRACT_INVALID"),
    ("omit_outer", "PAIR_CONTRACT_INVALID"),
    ("wrong_schema", "PAIR_CONTRACT_INVALID"),
    ("rights_true", "PAIR_CONTRACT_INVALID"),
    ("external_authenticated", "PAIR_CONTRACT_INVALID"),
    ("ab_cycles", "PAIR_CONTRACT_INVALID"),
    ("gates_boolean", "PAIR_CONTRACT_INVALID"),
    ("extra_receipt", "PAIR_RECEIPT_INVALID"),
    ("wrong_receipt_schema", "PAIR_RECEIPT_INVALID"),
    ("wrong_canonicalization", "PAIR_RECEIPT_INVALID"),
    ("receipt_length", "PAIR_RECEIPT_LENGTH_MISMATCH"),
    ("pair_sha", "PAIR_RECEIPT_SHA_MISMATCH"),
    ("canonical_not_sorted", "PAIR_CANONICAL_NOT_EXACT"),
    ("envelope_differs", "PAIR_RECEIPT_SCOPE_MISMATCH"),
    ("early_nested_sha", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("late_nested_sha", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("early_rights", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("late_rights", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("invalid_export_extra", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("early_clock_spoof", "PAIR_NESTED_EXPORT_NOT_VERIFIED"),
    ("exports_extra_cut", "PAIR_EXPORTS_INVALID"),
    ("exports_missing_late", "PAIR_EXPORTS_INVALID"),
    ("valid_at_conflict", "COMPARISON_FILTERS_DIFFER"),
    ("family_conflict", "COMPARISON_FILTERS_DIFFER"),
    ("swapped_cuts", "EARLY_AND_LATE_EXPORTS_REQUIRED"),
    ("early_publication_unclamped", "PAIR_PUBLICATION_CEILING_INCONSISTENT"),
])
def test_pair_fail_closed_with_valid_individual_or_recomputed_hashes(
        tmp_path, mutation, error_code):
    db = tmp_path / "fixture.sqlite3"
    pair = _pair_export(db)
    r = pair["pair_receipt"]
    if mutation == "extra_outer":
        pair["arbitrary"] = "should-not-pass"
    elif mutation == "omit_outer":
        del pair["evidence_class"]
    elif mutation == "wrong_schema":
        pair["schema"] = "pfl.synthetic_scientific_registry.v1"
    elif mutation == "rights_true":
        pair["rights_for_public_display_admitted"] = True
    elif mutation == "external_authenticated":
        pair["external_authenticity_certified"] = True
    elif mutation == "ab_cycles":
        pair["scientific_ab_cycles"] = 1
    elif mutation == "gates_boolean":
        pair["release_gates_passed"] = False
    elif mutation == "extra_receipt":
        r["source_id"] = "SENSITIVE_CANARY"
    elif mutation == "wrong_receipt_schema":
        r["schema"] = "not-the-pair-receipt"
    elif mutation == "wrong_canonicalization":
        r["canonicalization"] = "ARBITRARY_JSON"
    elif mutation == "receipt_length":
        r["bytes"] += 1
    elif mutation == "pair_sha":
        r["sha256"] = "f" * 64
    elif mutation == "canonical_not_sorted":
        r["canonical_json"] = r["canonical_json"].replace(
            ',"evidence_class":', ', "evidence_class":', 1)
        assert ', "evidence_class":' in r["canonical_json"]
        raw = r["canonical_json"].encode()
        r["bytes"], r["sha256"] = len(raw), sha256(raw).hexdigest()
    elif mutation == "envelope_differs":
        pair["comparison_kind"] = "AUTHOR_STIPULATED_SNAPSHOT_VISIBILITY_NOT_REAL_CHANGE"
        # Even a syntactically identical meaning with changed receipt scope
        # must not pass (pair SHA is still correct for its OLD scope).
        pair["exports"] = deepcopy(pair["exports"])
        pair["exports"]["late"]["query"]["family"] = "CHAIN"
    elif mutation in ("early_nested_sha", "late_nested_sha"):
        pair["exports"][mutation.split("_")[0]]["snapshot_receipt"]["sha256"] = "0" * 64
    elif mutation in ("early_rights", "late_rights"):
        pair["exports"][mutation.split("_")[0]]["rights_for_public_display_admitted"] = True
    elif mutation == "invalid_export_extra":
        pair["exports"]["early"]["source_id"] = "SENSITIVE_CANARY"
    elif mutation == "early_clock_spoof":
        pair["exports"]["early"]["query"]["as_of"] = "2026-11-01T12:00:00Z"
    elif mutation == "exports_extra_cut":
        pair["exports"]["future"] = deepcopy(pair["exports"]["late"])
    elif mutation == "exports_missing_late":
        del pair["exports"]["late"]
    elif mutation in ("valid_at_conflict", "family_conflict"):
        chosen = (("2026-10-10", "all") if mutation == "valid_at_conflict"
                  else ("2026-09-15", "CHAIN"))
        pair["exports"]["late"] = export_of(
            db, cut="late", valid_at=chosen[0], family=chosen[1])
    elif mutation == "swapped_cuts":
        pair["exports"]["early"], pair["exports"]["late"] = (
            pair["exports"]["late"], pair["exports"]["early"])
    elif mutation == "early_publication_unclamped":
        # The two independently valid downloads may still not originate from
        # a single browser pair selection with early clock clamping.
        pair["exports"]["early"] = export_of(
            db, cut="early", published="2026-09-19T12:00:00Z")
    if mutation not in (
        "receipt_length", "pair_sha", "canonical_not_sorted", "envelope_differs",
        "extra_receipt", "wrong_receipt_schema", "wrong_canonicalization",
    ):
        pair["pair_receipt"] = _pair_receipt(pair)
    code, report = _pair_cli(_pair_file(tmp_path, pair, "tampered.json"))
    assert code == 1 and report["status"] == "FAIL"
    assert report["error_code"] == error_code
    assert "SENSITIVE_CANARY" not in json.dumps(report)
    assert "exports" not in report
    assert "pair_sha256" not in report


@pytest.mark.parametrize("attack,error_code", [
    ("duplicate_outer", "PAIR_JSON_NOT_VERIFIED"),
    ("duplicate_nested", "PAIR_JSON_NOT_VERIFIED"),
    ("duplicate_canonical", "PAIR_CANONICAL_JSON_INVALID"),
    ("nonfinite", "PAIR_JSON_NOT_VERIFIED"),
    ("truncated", "PAIR_JSON_NOT_VERIFIED"),
    ("oversize", "INPUT_TOO_LARGE"),
])
def test_pair_malformed_json_never_echoes_payload_or_path(tmp_path, attack, error_code):
    pair = _pair_export(tmp_path / "fixture.sqlite3")
    file = _pair_file(tmp_path, pair, "private-SENSITIVE_CANARY.json")
    if attack == "duplicate_outer":
        raw = file.read_text(encoding="utf-8")
        assert '"R5": "STOP_R5"' in raw
        file.write_text(raw.replace(
            '"R5": "STOP_R5"', '"R5": "STOP_R5", "R5": "STOP_R5"', 1),
            encoding="utf-8")
    elif attack == "duplicate_nested":
        raw = file.read_text(encoding="utf-8")
        assert '"source_contract":' in raw
        file.write_text(raw.replace(
            '"source_contract":', '"source_contract": "DUPLICATE", "source_contract":',
            1), encoding="utf-8")
    elif attack == "duplicate_canonical":
        raw = pair["pair_receipt"]["canonical_json"]
        changed = raw.replace('"schema":', '"schema":"DUPLICATE","schema":', 1)
        assert changed != raw
        pair["pair_receipt"]["canonical_json"] = changed
        changed_bytes = changed.encode("utf-8")
        pair["pair_receipt"]["bytes"] = len(changed_bytes)
        pair["pair_receipt"]["sha256"] = sha256(changed_bytes).hexdigest()
        _pair_file(tmp_path, pair, file.name)
    elif attack == "nonfinite":
        file.write_text(file.read_text(encoding="utf-8").replace(
            '"release_gates_passed": 0', '"release_gates_passed": NaN', 1),
            encoding="utf-8")
    elif attack == "truncated":
        file.write_bytes(b'{"schema":')
    elif attack == "oversize":
        file.write_bytes(b'X' * 1_048_577)
    code, report = _pair_cli(file)
    assert code == 1 and report["error_code"] == error_code
    assert "SENSITIVE_CANARY" not in json.dumps(report)


def test_pair_missing_invalid_argument_or_legacy_mix_never_echo_path(tmp_path):
    early, late = files(tmp_path)
    for arguments in (
        ("--pair", str(tmp_path / "SENSITIVE_CANARY-absent.json")),
        ("--pair", str(early), str(late)),
        ("--pair", str(early), str(late), str(early)),
        ("--pair",),
    ):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            cwd=ROOT, env=ENV, capture_output=True, encoding="utf-8",
            text=True, timeout=15, check=False,
        )
        assert result.returncode == 1 and not result.stderr
        data = json.loads(result.stdout)
        assert data["status"] == "FAIL"
        assert "SENSITIVE_CANARY" not in result.stdout
        assert str(tmp_path) not in result.stdout
