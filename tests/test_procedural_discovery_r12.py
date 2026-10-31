"""R12 six official documentary paths, never six scientific cohorts."""
from hashlib import sha256
import json

import pytest

from politics_fantasy.procedural_discovery_r12 import (
    MANIFEST,PIN,NORM_SHA,APPEALS_SHA,status,
)


def test_r12_published_metadata_is_pinned_and_unpromotable():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    result=status()
    assert result["status"]=="R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION"
    assert result["source_count"]==6
    assert result["normative_route_count"]==3
    assert result["appeals_route_count"]==3
    assert result["first_public_at"] is None
    assert result["independent_risk_denominator"] is None
    assert result["real_outcome_events"] is None
    assert result["real_censoring"] is None
    assert result["historical_original_case_vintage_pairs_verified"]==0
    assert result["scientific_cycles"]==0
    assert result["licensed_tarcja_csv_does_not_license_intake"]
    assert result["pan_is_not_intake_denominator"]
    assert all(x["original_available"] is False for x in result["source_routes"])
    assert all(x["censored_case_count"] is None for x in result["source_routes"])


def test_private_agent_hashes_and_zero_originals():
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    assert d["private_source_matrix_sha256"]=={"normative":NORM_SHA,"appeals":APPEALS_SHA}
    assert d["source_originals_downloaded"]==0
    assert d["case_outcomes_examined"]==0
    assert d["AB_cycles_executed"]==0
    assert d["terms_accepted"] is False
    assert d["source_local_identifiers_exported"] is False
    assert d["historical_vintages_of_same_case_distribution"] is False
    assert d["confirmed_first_public_at"] is None


def test_historical_cuts_hide_counts_names_sha_and_even_exclusion_reason():
    for past in ("2020-01-01T00:00:00Z","2026-10-31T23:59:59Z"):
        x=status(as_of=past)
        assert x["status"]=="R12_NOT_KNOWN_AT_CUT"
        assert x["source_count"] is None
        assert x["source_routes"]==[]
        assert x["source_manifest_sha256"] is None
        assert x["pan_is_not_intake_denominator"] is None
        assert x["tacrc_multiple_resources_per_resolution"] is None
        assert "TACRC" not in str(x)
        assert "AGE_PAN" not in str(x)
    assert status(as_of="2026-11-01T00:00:00Z")["source_count"]==6


@pytest.mark.parametrize("field,value",[
    ("source_originals_downloaded",1),
    ("terms_accepted",True),
    ("historical_vintages_of_same_case_distribution",True),
    ("complete_independent_registration_denominator",True),
    ("confirmed_first_public_at","2020-01-01"),
])
def test_adversarial_global_promotion_quarantined(tmp_path,field,value):
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    d[field]=value
    f=tmp_path/"modified.json"
    f.write_text(json.dumps(d),encoding="utf8")
    r=status(path=f)
    assert r["status"]=="R12_SOURCE_QUARANTINED"
    assert r["source_routes"]==[]
    assert r["source_manifest_sha256"] is None


@pytest.mark.parametrize("field,value",[
    ("source_originals_acquired",1),
    ("individual_decisions_inspected",True),
    ("all_received_denominator",179),
    ("official_case_link_certified",True),
    ("right_censoring_observed",0),
    ("historical_first_public_at","2020-01-01T00:00:00Z"),
    ("primary_index_url","javascript:alert(1)"),
    ("specific_rights_scope","ALL_PUBLIC"),
])
def test_adversarial_route_promotions_quarantined(tmp_path,field,value):
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    d["documentary_routes"][0][field]=value
    f=tmp_path/"modified.json"
    f.write_text(json.dumps(d),encoding="utf8")
    assert status(path=f)["status"]=="R12_SOURCE_QUARANTINED"


@pytest.mark.parametrize("cut",["", "today", "2026-10-31", "2026-10-31T09:00:00"])
def test_invalid_cut_not_silently_current(cut):
    with pytest.raises(ValueError):
        status(as_of=cut)
