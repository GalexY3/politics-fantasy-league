"""R9 sanitizer publishes no IDs/outcomes, including with real worker scratch."""
from hashlib import sha256
import importlib.util
import json
from pathlib import Path
import re

import pytest

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/source_manifests/r9_regional_documentary_redacted_20261031.json"
NAT=ROOT/"data/source_manifests/r9_national_documentary_redacted_20261031.json"


def test_published_manifests_exclude_private_case_identifiers_and_outcome_values():
    alltext=REG.read_text(encoding="utf8")+NAT.read_text(encoding="utf8")
    assert not re.search(r"\b(?:09|10)/PPLI-?\d{4,}",alltext)
    for forbidden in ("3833","13432","30374","9155","9160","source_text_scope","reported_count"):
        assert forbidden not in alltext
    assert "individual_source_local_ids_republished" in alltext
    assert '"real_source_originals_downloaded": 0' in alltext
    assert '"scientific_cycles": 0' in alltext
    for path in (REG,NAT):
        d=json.loads(path.read_text(encoding="utf8"))
        assert not d["source_local_ids_or_outcomes_published"]
        assert d["preserved_full_matrix_outside_git"]
        assert all(x["all_received_denominator"] is None for x in d["entries"])


def test_replayed_redaction_matches_real_worker_scratch_only_when_available():
    path=ROOT/"scripts/redact_r9_documentary_sources.py"
    spec=importlib.util.spec_from_file_location("redactor_r9",path)
    module=importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    if not module.REGIONAL.exists() or not module.NATIONAL.exists():
        pytest.skip("Independent worker scratch not mounted; pinned Git manifests still tested")
    a,b=module.sanitized()
    assert a==json.loads(REG.read_text(encoding="utf8"))
    assert b==json.loads(NAT.read_text(encoding="utf8"))
    assert sha256(module.REGIONAL.read_bytes()).hexdigest()==module.REGIONAL_SOURCE_SHA
    assert sha256(module.NATIONAL.read_bytes()).hexdigest()==module.NATIONAL_SOURCE_SHA
