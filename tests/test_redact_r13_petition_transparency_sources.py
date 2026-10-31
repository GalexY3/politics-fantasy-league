"""Private SHA lineage / whitelist-only reproducibility R13."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data/source_manifests/r13_petition_transparency_documentary_redacted_20261031.json"
PIN="0bf0cfc12424ee9aa3ca1dc4a6f2d0eaf5de18cc52b0cab4f7ad2cf6ed707fa0"


def test_only_documentary_fields_and_zero_person_or_case_export():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    assert len(d["documentary_sources"])==8
    assert d["source_originals_downloaded"]==0
    assert d["case_outcomes_examined"]==0
    assert d["AB_scientific_cycles"]==0
    assert d["terms_accepted"] is False
    assert not d["individual_identifiers_or_personal_data_exported"]
    assert not d["complete_scientific_denominator"]
    assert all(x["first_public_at"] is None for x in d["documentary_sources"])


def test_replay_private_worker_sha_pinned_matrices_only_if_accessible():
    path=ROOT/"scripts/redact_r13_petition_transparency_sources.py"
    spec=importlib.util.spec_from_file_location("redact_r13",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not module.SENATE.exists() or not module.REVIEW.exists():
        pytest.skip("R13 private worker scratch not mounted")
    assert sha256(module.SENATE.read_bytes()).hexdigest()==module.SENATE_SHA
    assert sha256(module.REVIEW.read_bytes()).hexdigest()==module.REVIEW_SHA
    assert module.sanitized()==json.loads(MANIFEST.read_text(encoding="utf8"))
