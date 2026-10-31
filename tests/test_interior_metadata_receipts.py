"""Offline integrity assertions on the metadata-only Spanish-source report."""
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
P = ROOT / "research/PFL_SYSTEM20_20261031/INTERIOR_METADATA"


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def test_frozen_parser_and_policy_sha():
    receipt = json.loads((P / "receipts/frozen_code.json").read_text(encoding="utf-8"))
    for name, expected in receipt["code_sha256"].items():
        assert sha(P / name) == expected
    assert sha(P / "receipts/phase1_final.json") == receipt["phase1_sha256"]
    assert sha(P / "metadata_policy.json") == "bfb0548942cf0f6f03336d0a4eb86c0d7408118bb9594abbe4975217b2e7e929"


def test_phase2_metadata_source_year_counts_and_no_outcomes():
    receipt = json.loads((P / "receipts/phase2.json").read_text(encoding="utf-8"))
    assert receipt["causal_or_abh_conclusions"] is False
    assert receipt["source_first_public_at"] is None
    assert receipt["download_requests"] == 0
    assert receipt["raw_originals_recaptured"] is False
    first, second = receipt["outputs"]
    assert first["rows_scanned"] == 5600 and second["rows_scanned"] == 6203
    assert first["valid_year_rows"] == 5600 and second["valid_year_rows"] == 6203
    assert len(first["year_counts"]) == len(second["year_counts"]) == 15
    assert first["year_counts"]["2019"] == 700
    assert first["metadata_key_collision_rows"] == 4768
    assert second["metadata_key_names"] == []
    assert second["duplicate_claim"].startswith("NOT_TESTABLE:")
    assert first["person_rows_or_outcome_values_exported"] is False
    assert second["person_rows_or_outcome_values_exported"] is False


def test_policy_does_not_select_any_disallowed_cell():
    policy = json.loads((P / "metadata_policy.json").read_text(encoding="utf-8"))
    assert policy["schema"] == "INTERIOR_METADATA_ONLY_V1"
    assert policy["sources"]["Elecciones-Congreso-cargos-electos.xlsx"]["columns"] == ["A", "B", "C", "D", "E"]
    assert policy["sources"]["Elecciones-Congreso.xlsx"]["columns"] == ["A", "B", "C"]
    assert all(x["status"] == "AGGREGATE_EXPLORATORY_ONLY"
               for x in json.loads((P / "receipts/phase2.json").read_text(encoding="utf-8"))["outputs"])
