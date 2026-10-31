"""R11 deterministic SHA lineage from two independently scoped scratch agents."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path

import pytest

ROOT=Path(__file__).resolve().parents[1]
DOCUMENT=ROOT/"data/source_manifests/r11_scoped_documentary_gates_20261031.json"
EXPECTED="e53ac2e61bb8d2cce67afdc1f035dd6b92deabaf0ba6c70611f2a0b41c599c66"


def test_git_document_is_only_redacted_metadata():
    assert sha256(DOCUMENT.read_bytes()).hexdigest()==EXPECTED
    obj=json.loads(DOCUMENT.read_text(encoding="utf8"))
    assert len(obj["source_routes"])==7
    assert obj["real_original_datasets_acquired"]==0
    assert obj["real_case_outcomes_read"]==0
    assert obj["scientific_cycles_executed"]==0
    assert not obj["case_identifiers_or_person_data_exported"]
    assert not obj["reuser_terms_accepted"]


def test_replay_real_worker_matrices_with_pinned_shas_if_mounted():
    spec=importlib.util.spec_from_file_location(
        "redact_r11",ROOT/"scripts/redact_r11_source_gates.py")
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not module.MUNICIPAL.is_file() or not module.ECONOMIC.is_file():
        pytest.skip("R11 private scratch not mounted; reviewed Git manifest pinned")
    assert sha256(module.MUNICIPAL.read_bytes()).hexdigest()==module.MUNICIPAL_SHA
    assert sha256(module.ECONOMIC.read_bytes()).hexdigest()==module.ECONOMIC_SHA
    assert module.sanitized()==json.loads(DOCUMENT.read_text(encoding="utf8"))
