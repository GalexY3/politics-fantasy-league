"""R8 source descriptions: real SHA pins, zero original access, synthetic attacks."""
import json
from pathlib import Path

import pytest

from politics_fantasy.procedural_discovery_r8 import (
    NATIONAL, REGIONAL, NATIONAL_SHA, REGIONAL_SHA, status,
)
from hashlib import sha256


def test_r8_real_documentary_matrices_held_by_sha_without_original_promotions():
    assert sha256(REGIONAL.read_bytes()).hexdigest()==REGIONAL_SHA
    assert sha256(NATIONAL.read_bytes()).hexdigest()==NATIONAL_SHA
    x=status()
    assert x["status"]=="R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION"
    assert x["regional_source_count"]==6 and x["national_documentary_assets_count"]==10
    assert len(x["national_core_routes"])==3
    assert x["scientific_cohort_added"] is False
    assert x["independent_all_received_denominator"] is None
    assert x["source_originals_admitted"]==0
    assert x["first_public_at"] is None
    assert "2027" not in str(x), "Unreplayed annual consultation count must not be exposed"


def test_cut_before_documentary_audit_hides_names_count_hash_and_clock():
    x=status(as_of="2026-10-31T23:59:59Z")
    assert x["status"]=="R8_NOT_KNOWN_AT_CUT"
    assert x["regional_routes"]==[] and x["national_core_routes"]==[]
    assert x["regional_source_count"] is None
    assert x["source_matrix_sha256"] is None and x["local_audit_safe_by"] is None
    assert "Balears" not in str(x) and "Consejo" not in str(x)
    y=status(as_of="2026-11-01T00:00:00Z")
    assert len(y["regional_routes"])==6


@pytest.mark.parametrize("field,changed",[
    ("full_received_before_mesa",True),
    ("independent_total",42),
    ("raw_sha256","a"*64),
    ("first_public_at","2024-01-01T00:00:00Z"),
    ("licence_for_bulk_registry_proven",True),
])
def test_attacker_cannot_promote_regional_manifests_by_edit(tmp_path:Path,field,changed):
    r=json.loads(REGIONAL.read_text(encoding="utf8"))
    r["sources"][0][field]=changed
    bad=tmp_path/"region.json"
    bad.write_text(json.dumps(r),encoding="utf8")
    assert status(regional_path=bad)["status"]=="R8_DOCUMENTARY_MANIFEST_QUARANTINED"


def test_national_outcome_and_rights_tampering_quarantined(tmp_path:Path):
    r=json.loads(NATIONAL.read_text(encoding="utf8"))
    r["original_downloads"]=1
    bad=tmp_path/"national.json"
    bad.write_text(json.dumps(r),encoding="utf8")
    assert status(national_path=bad)["status"]=="R8_DOCUMENTARY_MANIFEST_QUARANTINED"


@pytest.mark.parametrize("bad",["bad","2026-10-31","2026-10-31T12:00:00"])
def test_invalid_cut_rejected(bad):
    with pytest.raises(ValueError):
        status(as_of=bad)
