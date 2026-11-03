"""Adversarial offline checks for the actual browser S9 export envelope."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

from politics_fantasy import scientific_registry as registry
from scripts import verify_scientific_snapshot as verifier


ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "scripts" / "verify_scientific_snapshot.py"
ALLOWLISTED = (
    "sandbox_alpha_v1", "sandbox_beta_v1",
    "sandbox_alpha_v2", "sandbox_bad_issuer",
)


def browser_export(temp_root: Path, *, cut: str = "late",
                   valid_at: str = "2026-09-15", family: str = "all",
                   published_until: str = "as_of",
                   enrolled: tuple[str, ...] = ()) -> dict:
    """Build precisely the 11-field app.js exportBody, not a registry HTTP body."""
    sqlite_path = temp_root / "fixtures" / "scientific_registry_synthetic.sqlite3"
    for fixture in enrolled:
        assert fixture in ALLOWLISTED
        registry.enroll_synthetic_fixture(sqlite_path, fixture)
    queried = registry.query_registry(
        sqlite_path, cut=cut, valid_at=valid_at,
        family=family, published_until=published_until,
    )
    receipt = queried["snapshot_receipt"]
    return {
        "schema": "pfl.synthetic_scientific_registry_browser_export.v1",
        "evidence_class": "SYNTHETIC_LAB_ONLY",
        "query": {
            "cut": cut, "as_of": queried["as_of"], "valid_at": valid_at,
            "family": family, "published_until": queried["published_until"],
        },
        "source_contract": queried["schema"],
        "receipt_schema": receipt["schema"],
        "snapshot_receipt": receipt,
        "R5": "STOP_R5", "release_gates_passed": 0, "scientific_ab_cycles": 0,
        "external_authenticity_certified": False,
        "rights_for_public_display_admitted": False,
    }


def write_export(path: Path, data: object) -> Path:
    # Same pretty printer as JSON.stringify(exportBody,null,2)+'\n',
    # including the fixed insertion order and non-ASCII UTF-8.
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n",
                    encoding="utf-8")
    return path


def run_cli(path: Path | str, *, cwd: Path | None = None) -> tuple[int, dict, str]:
    env = {**os.environ, "PYTHONPATH": "", "PYTHONDONTWRITEBYTECODE": "1",
           "PYTHONIOENCODING": "utf-8"}
    run = subprocess.run(
        [sys.executable, "-B", str(CLI), str(path)],
        cwd=cwd or ROOT, env=env, timeout=10, capture_output=True,
        text=True, encoding="utf-8", errors="replace", check=False,
    )
    assert not run.stderr, "The offline verifier must not print input paths or tracebacks"
    result = json.loads(run.stdout)
    assert result["schema"] == verifier.SCHEMA
    assert result["status"] in ("PASS", "FAIL")
    assert "password" not in run.stdout
    assert "AUTHOR_ALPHA:FILE_1" not in run.stdout
    return run.returncode, result, run.stdout


def resign(data: dict, scope: dict | None = None) -> dict:
    """Recompute a perfectly self-consistent digest after a malicious change."""
    if scope is None:
        scope = json.loads(data["snapshot_receipt"]["canonical_json"])
    body = verifier.canonical(scope)
    data["snapshot_receipt"]["canonical_json"] = body.decode("utf-8")
    data["snapshot_receipt"]["bytes"] = len(body)
    data["snapshot_receipt"]["sha256"] = hashlib.sha256(body).hexdigest()
    return data


@pytest.mark.parametrize("cut,valid_at,family,publication,fixtures,descriptors,intakes,assessments", [
    ("early", "2026-09-11", "all", "as_of", (), 2, 0, 0),
    ("late", "2026-09-15", "all", "as_of", (), 6, 0, 8),
    ("late", "2026-10-10", "all", "as_of", ALLOWLISTED, 6, 4, 8),
    ("late", "2026-10-10", "CHAIN", "as_of", ALLOWLISTED, 2, 0, 0),
    ("late", "2026-10-10", "all", "2026-10-30T12:00:00Z",
     ALLOWLISTED, 6, 0, 0),
])
def test_real_closed_s9_receipt_contract_offline(
        tmp_path, cut, valid_at, family, publication, fixtures,
        descriptors, intakes, assessments):
    export = browser_export(tmp_path, cut=cut, valid_at=valid_at,
                            family=family, published_until=publication,
                            enrolled=fixtures)
    result = verifier.verify(export)
    assert result["status"] == "PASS"
    assert result["synthetic_only"] is True
    assert result["source_descriptors"] == descriptors
    assert result["intake_count"] == intakes
    assert result["synthetic_assessments_rejected_r5"] == assessments
    assert result["sha256"] == export["snapshot_receipt"]["sha256"]
    assert result["public_release_eligible"] is False
    assert result["publisher_identity_verified"] is False
    assert result["rights_for_public_display_admitted"] is False
    assert not (tmp_path / "accounts.sqlite3").exists()


def test_cli_offline_from_other_working_directory_with_no_project_pythonpath(tmp_path):
    file_path = write_export(
        tmp_path / "downloaded_snapshot.json",
        browser_export(tmp_path),
    )
    code, reply, output = run_cli(file_path, cwd=tmp_path)
    assert code == 0 and reply["status"] == "PASS"
    assert reply["cut"] == "late"
    assert reply["source_descriptors"] == 6
    assert reply["intake_count"] == 0
    assert reply["R5"] == "STOP_R5"
    assert reply["release_gates_passed"] == reply["scientific_ab_cycles"] == 0
    assert str(file_path) not in output
    assert "canonical_json" not in reply


def test_cli_four_intakes_v4_with_rejected_fixture_and_stable_sha(tmp_path):
    data = browser_export(
        tmp_path, valid_at="2026-10-10", enrolled=ALLOWLISTED,
    )
    path = write_export(tmp_path / "synthetic-four-intakes.json", data)
    first_code, first, first_line = run_cli(path)
    second_code, second, second_line = run_cli(path)
    assert first_code == second_code == 0
    assert first_line == second_line
    assert first["sha256"] == data["snapshot_receipt"]["sha256"]
    assert first["intake_count"] == 4
    assert first["validated_synthetic_intakes"] == 3
    assert first["rejected_synthetic_intakes"] == 1
    assert first["synthetic_assessments_rejected_r5"] == 8
    assert first["public_release_eligible"] is False


@pytest.mark.parametrize("mutator,expected", [
    (lambda p: p["snapshot_receipt"].__setitem__("sha256", "0" * 64),
     "RECEIPT_SHA_MISMATCH"),
    (lambda p: p["snapshot_receipt"].__setitem__(
        "bytes", p["snapshot_receipt"]["bytes"] + 1), "RECEIPT_LENGTH_MISMATCH"),
    (lambda p: p.__setitem__("rights_for_public_display_admitted", True),
     "EXPORT_NOT_SYNTHETIC_BLOCKED"),
    (lambda p: p.__setitem__("external_authenticity_certified", True),
     "EXPORT_NOT_SYNTHETIC_BLOCKED"),
    (lambda p: p.__setitem__("release_gates_passed", True),
     "EXPORT_NOT_SYNTHETIC_BLOCKED"),
    (lambda p: p.__setitem__("scientific_ab_cycles", 1),
     "EXPORT_NOT_SYNTHETIC_BLOCKED"),
    (lambda p: p.__setitem__("source_contract", "pfl.empirical_sources.v1"),
     "EXPORT_NOT_SYNTHETIC_BLOCKED"),
    (lambda p: p.__setitem__("password", "SENSITIVE_CANARY"),
     "EXPORT_CONTRACT_INVALID"),
    (lambda p: p["snapshot_receipt"].__setitem__("arbitrary", "SENSITIVE_CANARY"),
     "RECEIPT_CONTRACT_INVALID"),
    (lambda p: p["query"].__setitem__("cut", "future"),
     "QUERY_NOT_ALLOWLISTED"),
    (lambda p: p["query"].__setitem__("published_until", "2026-12-01T12:00:00Z"),
     "QUERY_FUTURE_PUBLICATION"),
])
def test_fail_closed_envelope_and_receipt_mutations(tmp_path, mutator, expected):
    payload = browser_export(tmp_path)
    mutator(payload)
    path = write_export(tmp_path / "untrusted.json", payload)
    code, reply, output = run_cli(path)
    assert code == 1 and reply["status"] == "FAIL"
    assert reply["error_code"] == expected
    assert "SENSITIVE_CANARY" not in output
    assert str(path) not in output
    assert set(reply) == {
        "schema", "status", "error_code", "public_release_eligible",
        "publisher_identity_verified",
    }


def test_rejects_rewritten_canonical_digest_even_with_new_matching_sha(tmp_path):
    data = browser_export(tmp_path)
    scope = json.loads(data["snapshot_receipt"]["canonical_json"])
    scope["distributions"][0]["sha256_public_descriptor"] = "f" * 64
    resign(data, scope)
    with pytest.raises(verifier.VerificationError, match="DESCRIPTORS_NOT_CLOSED"):
        verifier.verify(data)


@pytest.mark.parametrize("kind,expected", [
    ("future_scope_query", "QUERY_FUTURE_PUBLICATION"),
    ("future_intake_visibility", "INTAKE_TEMPORAL_LEAK"),
    ("disclosure_flag", "UNAUTHORIZED_REAL_OR_RIGHTS_CLAIM"),
    ("private_id", "PRIVATE_SOURCE_IDENTIFIER"),
    ("source_descriptor_swap", "DESCRIPTORS_NOT_CLOSED"),
    ("intake_count", "INTAKE_COUNT_INVALID"),
    ("invalid_intake_public_sha", "INTAKE_ENTRY_INVALID"),
    ("invalid_assessment_public_sha", "ASSESSMENTS_NOT_CLOSED"),
])
def test_resigned_but_unauthorized_public_projection_fails(tmp_path, kind, expected):
    data = browser_export(tmp_path, enrolled=ALLOWLISTED)
    scope = json.loads(data["snapshot_receipt"]["canonical_json"])
    if kind == "future_scope_query":
        data["query"]["cut"] = "early"
        data["query"]["as_of"] = "2026-10-15T12:00:00Z"
        scope["cut"] = "early"
        scope["as_of"] = "2026-10-15T12:00:00Z"
        # A late publication cannot be made observable by re-signing.
        data["query"]["published_until"] = "2026-10-30T12:00:00Z"
        scope["published_until"] = "2026-10-30T12:00:00Z"
    elif kind == "future_intake_visibility":
        # Keep a perfectly legal early knowledge cut but illegally smuggle
        # the four late S9 intakes into that snapshot.
        early = browser_export(tmp_path, cut="early", enrolled=ALLOWLISTED)
        data["query"] = early["query"]
        old = json.loads(early["snapshot_receipt"]["canonical_json"])
        old["snapshot"]["synthetic_intake"] = scope["snapshot"]["synthetic_intake"]
        scope = old
    elif kind == "disclosure_flag":
        scope["snapshot"]["synthetic_intake"]["rights_for_public_display"] = True
    elif kind == "private_id":
        scope["snapshot"]["synthetic_intake"]["entries"][0]["source_id"] = "AUTHOR_ALPHA:FILE_1"
    elif kind == "source_descriptor_swap":
        scope["distributions"].reverse()
    elif kind == "intake_count":
        scope["snapshot"]["synthetic_intake"]["intake_count"] = 3
    elif kind == "invalid_intake_public_sha":
        scope["snapshot"]["synthetic_intake"]["entries"][0]["public_descriptor_sha256"] = "0" * 64
    elif kind == "invalid_assessment_public_sha":
        scope["snapshot"]["admission_assessments"]["assessments"][0]["public_receipt_sha256"] = "0" * 64
    resign(data, scope)
    code, reply, output = run_cli(write_export(tmp_path / "forged.json", data))
    assert code == 1 and reply["error_code"] == expected
    assert "AUTHOR_ALPHA:FILE_1" not in output


def test_rejects_noncanonical_json_even_with_matching_sha_and_length(tmp_path):
    data = browser_export(tmp_path)
    canonical_str = data["snapshot_receipt"]["canonical_json"]
    modified = canonical_str.replace('"schema":', '"schema": ', 1)
    assert modified != canonical_str
    data["snapshot_receipt"]["canonical_json"] = modified
    data["snapshot_receipt"]["bytes"] = len(modified.encode("utf-8"))
    data["snapshot_receipt"]["sha256"] = hashlib.sha256(modified.encode("utf-8")).hexdigest()
    code, reply, _ = run_cli(write_export(tmp_path / "noncanonical.json", data))
    assert code == 1 and reply["error_code"] == "CANONICAL_BYTES_NOT_EXACT"


def test_nested_duplicate_json_keys_rejected_even_if_its_digest_matches(tmp_path):
    data = browser_export(tmp_path)
    original = data["snapshot_receipt"]["canonical_json"]
    altered = original.replace('"cut":"late"', '"cut":"late","cut":"late"', 1)
    assert altered != original
    data["snapshot_receipt"]["canonical_json"] = altered
    data["snapshot_receipt"]["bytes"] = len(altered.encode("utf-8"))
    data["snapshot_receipt"]["sha256"] = hashlib.sha256(altered.encode("utf-8")).hexdigest()
    code, reply, _ = run_cli(write_export(tmp_path / "duplicate_canonical.json", data))
    assert code == 1 and reply["error_code"] == "JSON_DUPLICATE_KEY"


def test_top_level_duplicate_json_keys_and_nan_rejected(tmp_path):
    data = browser_export(tmp_path)
    normal = write_export(tmp_path / "fixture.json", data).read_text(encoding="utf-8")
    duplicate = normal.replace('"R5": "STOP_R5"', '"R5": "STOP_R5", "R5": "STOP_R5"', 1)
    assert duplicate != normal
    (tmp_path / "duplicate.json").write_text(duplicate, encoding="utf-8")
    code, reply, _ = run_cli(tmp_path / "duplicate.json")
    assert code == 1 and reply["error_code"] == "JSON_DUPLICATE_KEY"
    (tmp_path / "nonfinite.json").write_text(
        normal.replace('"release_gates_passed": 0', '"release_gates_passed": NaN', 1),
        encoding="utf-8",
    )
    code, reply, _ = run_cli(tmp_path / "nonfinite.json")
    assert code == 1 and reply["error_code"] == "JSON_NONFINITE_NUMBER"


def test_missing_and_oversize_files_are_fail_closed_without_path_or_content(tmp_path):
    secret_path = tmp_path / "private-account-do-not-echo-SENSITIVE_CANARY.json"
    code, reply, output = run_cli(secret_path)
    assert code == 1 and reply["error_code"] == "INPUT_UNAVAILABLE_OR_INVALID"
    assert "SENSITIVE_CANARY" not in output
    secret_path.write_bytes(b"SENSITIVE_CANARY" * (verifier.MAX_INPUT_BYTES // 16 + 2))
    code, reply, output = run_cli(secret_path)
    assert code == 1 and reply["error_code"] == "INPUT_TOO_LARGE"
    assert "SENSITIVE_CANARY" not in output
    assert str(secret_path) not in output


def test_raw_private_identifiers_rejected_without_reprinting_any_value(tmp_path):
    payload = browser_export(tmp_path, enrolled=("sandbox_alpha_v1",))
    scope = json.loads(payload["snapshot_receipt"]["canonical_json"])
    scope["snapshot"]["synthetic_intake"]["entries"][0]["label"] = "AUTHOR_ALPHA:FILE_1"
    resign(payload, scope)
    code, reply, raw = run_cli(write_export(tmp_path / "secret-label.json", payload))
    assert code == 1 and reply["error_code"] == "PRIVATE_SOURCE_IDENTIFIER"
    assert "AUTHOR_ALPHA" not in raw and "secret-label" not in raw


def test_new_arbitrary_author_label_not_part_of_closed_synthetic_fixture(tmp_path):
    payload = browser_export(tmp_path, enrolled=("sandbox_alpha_v1",))
    scope = json.loads(payload["snapshot_receipt"]["canonical_json"])
    scope["snapshot"]["synthetic_intake"]["entries"][0]["label"] = (
        "Una etiqueta de entrada no incluida en el fixture autor-cerrado"
    )
    resign(payload, scope)
    code, reply, text = run_cli(write_export(tmp_path / "modified-label.json", payload))
    assert code == 1 and reply["error_code"] == "INTAKE_ENTRY_INVALID"
    assert "etiqueta de entrada" not in text


def test_invalid_arguments_are_machine_readable_and_do_not_echo_untrusted_paths(tmp_path):
    run = subprocess.run(
        [sys.executable, "-B", str(CLI), "--bad-option",
         str(tmp_path / "SENSITIVE_CANARY.json")],
        cwd=tmp_path, capture_output=True, text=True, encoding="utf-8",
        timeout=10, check=False,
    )
    assert run.returncode == 1 and not run.stderr
    body = json.loads(run.stdout)
    assert body["error_code"] == "ARGUMENTS_INVALID"
    assert "SENSITIVE_CANARY" not in run.stdout
