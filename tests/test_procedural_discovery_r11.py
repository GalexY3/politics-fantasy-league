"""SHA-pinned R11 source leads, rights gates and temporal non-disclosure."""
from hashlib import sha256
import json
from pathlib import Path

import pytest

from politics_fantasy.procedural_discovery_r11 import (
    MANIFEST,PIN,REGIONAL_SOURCE_SHA,ECONOMIC_SOURCE_SHA,status,
)


def test_published_documentary_manifest_real_sha_and_zero_source_originals():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    r=status()
    assert r["status"]=="R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED"
    assert r["documentary_source_count"]==7
    assert r["municipal_source_count"]==4 and r["economic_source_count"]==3
    assert r["real_case_rows_admitted"]==0
    assert r["real_originals_downloaded"]==0
    assert r["eligible_scientific_denominator"] is None
    assert r["real_terminal_outcomes"] is None
    assert r["real_pending_events"] is None
    assert r["historical_first_public_at"] is None
    assert r["rights_by_mere_use_block"]
    assert r["publisher_2026_feed_gap_known"]
    assert all(x["independent_denominator"] is None for x in r["source_routes"])
    assert all(x["dataset_acquired"] is False for x in r["source_routes"])


def test_private_worker_originals_not_republished_as_case_rows():
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    assert d["upstream_private_worker_sha256"]=={
        "municipal":REGIONAL_SOURCE_SHA,"economic":ECONOMIC_SOURCE_SHA,
    }
    assert not d["case_identifiers_or_person_data_exported"]
    assert not d["reuser_terms_accepted"]
    assert not d["admissible_population_complete"]
    assert not d["publisher_same_origin_counts_independent"]
    assert all(x["outcomes_evaluated"] is None for x in d["source_routes"])
    assert all(x["case_level_denominator_verified"] is None for x in d["source_routes"])
    assert "concesionario_individual" not in MANIFEST.read_text(encoding="utf8")


def test_older_cut_hides_r11_titles_counts_rights_diagnostics_and_shas():
    for stamp in ("2024-01-01T00:00:00Z","2026-10-31T23:59:59.999Z"):
        x=status(as_of=stamp)
        assert x["status"]=="R11_DOCUMENTARY_NOT_KNOWN_AT_CUT"
        assert x["source_routes"]==[]
        assert x["documentary_source_count"] is None
        assert x["rights_by_mere_use_block"] is None
        assert x["publisher_2026_feed_gap_known"] is None
        assert x["source_matrix_sha256"] is None
        assert "MADRID" not in str(x).upper()
        assert "PLACSP" not in str(x).upper()
    x=status(as_of="2026-11-01T00:00:00Z")
    assert x["documentary_source_count"]==7


@pytest.mark.parametrize("field,value",[
    ("reuser_terms_accepted",True),
    ("real_original_datasets_acquired",1),
    ("admissible_population_complete",True),
    ("historical_public_witness_verified",True),
])
def test_modified_global_claim_quarantines(tmp_path:Path,field,value):
    x=json.loads(MANIFEST.read_text(encoding="utf8"))
    x[field]=value
    p=tmp_path/"r11_tampered.json"
    p.write_text(json.dumps(x),encoding="utf8")
    r=status(path=p)
    assert r["status"]=="R11_DOCUMENTARY_QUARANTINED"
    assert r["source_routes"]==[]
    assert r["source_matrix_sha256"] is None


@pytest.mark.parametrize("field,value",[
    ("rights_evaluation","UNRESTRICTED_REUSE"),
    ("originals_acquired",1),
    ("case_level_denominator_verified",101),
    ("historical_first_public_at","2020-01-01T00:00:00Z"),
    ("primary_catalogue_url","javascript:alert(1)"),
])
def test_modified_asset_rights_or_url_quarantines(tmp_path:Path,field,value):
    x=json.loads(MANIFEST.read_text(encoding="utf8"))
    x["source_routes"][0][field]=value
    p=tmp_path/"r11_tampered.json"
    p.write_text(json.dumps(x),encoding="utf8")
    assert status(path=p)["status"]=="R11_DOCUMENTARY_QUARANTINED"


@pytest.mark.parametrize("stamp",["", "today", "2026-10-31", "2026-10-31T17:00:00"])
def test_invalid_asof_cannot_implicitly_use_current_time(stamp):
    with pytest.raises(ValueError):
        status(as_of=stamp)
