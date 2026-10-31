"""Reproducible SHA-pinned whitelist replay from private agent matrices."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
OUTPUT=ROOT/"data/source_manifests/r12_normative_appeals_documentary_redacted_20261031.json"
EXPECTED="c865517ce8bc25cc2b1b835185e6710a518d7558b424147335ee0a66a3cc98a5"


def test_redacted_manifest_contains_no_decisions_or_identifiers():
    assert sha256(OUTPUT.read_bytes()).hexdigest()==EXPECTED
    d=json.loads(OUTPUT.read_text(encoding="utf8"))
    assert len(d["documentary_routes"])==6
    assert not d["source_local_identifiers_exported"]
    assert d["source_originals_downloaded"]==0
    assert d["case_outcomes_examined"]==0
    assert d["AB_cycles_executed"]==0
    assert not d["terms_accepted"]
    assert all(x["historical_first_public_at"] is None for x in d["documentary_routes"])


def test_original_worker_matrix_replay_by_private_sha_if_mounted():
    spec=importlib.util.spec_from_file_location(
        "r12_whitelist",ROOT/"scripts/redact_r12_legal_normative_sources.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not module.NORMATIVE.is_file() or not module.APPEALS.is_file():
        pytest.skip("R12 private scratch not mounted")
    assert sha256(module.NORMATIVE.read_bytes()).hexdigest()==module.NORMATIVE_SHA
    assert sha256(module.APPEALS.read_bytes()).hexdigest()==module.APPEALS_SHA
    assert module.sanitized()==json.loads(OUTPUT.read_text(encoding="utf8"))
