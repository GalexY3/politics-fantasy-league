"""Exact private-worker SHA lineage and sanitization of R10 findings."""
import importlib.util
from hashlib import sha256
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"data/source_manifests/r10_documentary_constraints_redacted_20261031.json"
EXPECTED="c81f3524098e505f332af05163902e777feb322c0b76dee65543f4bee82e0a19"


def test_redacted_doc_is_not_source_case_archive():
    raw=MANIFEST.read_bytes()
    assert sha256(raw).hexdigest()==EXPECTED
    doc=json.loads(raw.decode("utf8"))
    assert doc["schema"]=="pfl.r10.documentary_constraints_redacted.v1"
    assert doc["real_source_originals_downloaded"]==0
    assert doc["AB_cycles_executed"]==0
    assert doc["no_source_ids_or_outcome_values_exported"]
    assert not doc["all_received_denominator_certified"]
    assert not doc["historic_first_public_at_verified"]
    assert len(doc["regional_documentary_assets"])==6
    assert len(doc["distinct_institutional_entry_routes"])==3
    assert not any(x["all_received_register_count"] is not None for x in doc["regional_documentary_assets"])
    assert not any(x["all_received_register_count"] is not None for x in doc["distinct_institutional_entry_routes"])
    assert "PPLI-000" not in str(doc) and "ILPA-00" not in str(doc)


def test_real_worker_bytes_recreate_sanitized_index_when_scratch_present():
    spec=importlib.util.spec_from_file_location(
        "r10_redactor",ROOT/"scripts/redact_r10_documentary_sources.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not module.REGIONAL.is_file() or not module.NATIONAL.is_file():
        pytest.skip("Independent R10 scratch not mounted; manifest verified by Git pin")
    assert sha256(module.REGIONAL.read_bytes()).hexdigest()==module.REGIONAL_SHA
    assert sha256(module.NATIONAL.read_bytes()).hexdigest()==module.NATIONAL_SHA
    assert module.sanitize()==json.loads(MANIFEST.read_text(encoding="utf8"))
