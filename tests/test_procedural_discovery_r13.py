"""Documentary Senate/GAIP/SAIP discovery cannot become R5 admission."""
from hashlib import sha256
import json

import pytest

from politics_fantasy.procedural_discovery_r13 import (
    MANIFEST,PIN,SENATE_SHA,REVIEW_SHA,status,
)


def test_eight_nonadditive_documentary_sources_pinned():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    r=status()
    assert r["status"]=="R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"
    assert r["documentary_source_count"]==8
    assert r["senate_age_source_count"]==4
    assert r["review_saip_source_count"]==4
    assert r["all_eight_documentary_sources_nonadditive"]
    assert r["denominator_independently_verified"] is None
    assert r["real_original_vintage_pairs"] is None
    assert r["actual_censored_cases"] is None
    assert r["real_terminal_decisions"] is None
    assert r["first_public_at"] is None
    assert r["scientific_cycles"]==0
    assert r["senate_report_not_petition_count"]
    assert r["saip_not_all_gaip_claims"]
    assert r["restore_point_index_not_real_capture_pair"]
    assert r["rights_by_access_may_block_ingestion"]
    assert all(x["pending_or_censored_cases"] is None for x in r["source_rows"])
    assert all(x["terminal_outcomes"] is None for x in r["source_rows"])


def test_hashes_and_zero_sensitive_assets():
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    assert d["private_matrix_sha256"]=={"senate":SENATE_SHA,"gaip_navarra":REVIEW_SHA}
    assert d["source_originals_downloaded"]==0
    assert d["case_outcomes_examined"]==0
    assert d["AB_scientific_cycles"]==0
    assert d["same_distribution_original_vintages_verified"]==0
    assert d["terms_accepted"] is False
    assert d["individual_identifiers_or_personal_data_exported"] is False
    assert d["historical_first_public_at"] is None


def test_before_safeby_hides_sha_titles_n_counts_quarantine_reasons():
    for old in ("2020-01-01T00:00:00Z","2026-10-31T23:59:59Z"):
        r=status(as_of=old)
        assert r["status"]=="R13_NOT_KNOWN_AT_CUT"
        assert r["documentary_source_count"] is None
        assert r["source_rows"]==[]
        assert r["manifest_sha256"] is None
        assert r["saip_not_all_gaip_claims"] is None
        assert r["rights_by_access_may_block_ingestion"] is None
        assert "SENATE_" not in str(r)
        assert "GAIP_RESOLUTIONS" not in str(r)
    assert status(as_of="2026-11-01T00:00:00Z")["documentary_source_count"]==8


@pytest.mark.parametrize("field,changed",[
    ("source_originals_downloaded",1),
    ("terms_accepted",True),
    ("AB_scientific_cycles",1),
    ("complete_scientific_denominator",True),
    ("same_distribution_original_vintages_verified",2),
    ("historical_first_public_at","2020-01-01T00:00:00Z"),
])
def test_manifest_claim_escalation_quarantined(tmp_path,field,changed):
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    d[field]=changed
    f=tmp_path/"bad.json"
    f.write_text(json.dumps(d),encoding="utf8")
    r=status(path=f)
    assert r["status"]=="R13_SOURCE_QUARANTINED"
    assert r["source_rows"]==[]
    assert r["manifest_sha256"] is None


@pytest.mark.parametrize("field,changed",[
    ("individual_originals_downloaded",1),
    ("individual_outcomes_inspected",True),
    ("complete_all_received_denominator",999),
    ("admission_or_censoring_certified",True),
    ("first_public_at","2020-01-01T00:00:00Z"),
    ("two_comparable_original_vintages",True),
    ("official_catalogue_url","javascript:alert(1)"),
    ("rights_scope","GENERAL_REUSE_ALLOWED_WITHOUT_REVIEW"),
])
def test_asset_outcome_temporal_rights_promotions_quarantined(tmp_path,field,changed):
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    d["documentary_sources"][0][field]=changed
    f=tmp_path/"bad.json"
    f.write_text(json.dumps(d),encoding="utf8")
    assert status(path=f)["status"]=="R13_SOURCE_QUARANTINED"


@pytest.mark.parametrize("cut",["","today","2026-10-31","2026-10-31T12:00:00"])
def test_invalid_historic_cut_rejected(cut):
    with pytest.raises(ValueError):
        status(as_of=cut)
