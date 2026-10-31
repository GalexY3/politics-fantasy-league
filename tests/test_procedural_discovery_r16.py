"""SHA-pinned official documentary leads cannot become empirical R5 cases."""
from hashlib import sha256
from pathlib import Path
import json

import pytest

from politics_fantasy.procedural_discovery_r16 import MANIFEST,PIN,status
from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.registration_readiness_query import registration_readiness


def test_three_source_descriptions_not_three_registry_cohorts():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    x=status(as_of="2026-11-01T00:00:00Z")
    assert x["status"]=="R16_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"
    assert x["documentary_source_count"]==3
    assert not x["source_groups_additive"]
    assert not x["rights_to_download_originals"]
    assert x["scientific_cycles"]==0
    assert all(x[k] is None for k in (
        "real_denominator","real_pending_or_censoring","terminal_outcomes",
        "historical_first_public_at","historical_original_pairs"))
    rows=x["source_rows"]
    assert len({r["source_id"] for r in rows})==3
    assert all(r["source_originals_acquired"]==0
               and r["independent_entry_denominator"] is None
               and r["first_public_at"] is None
               and not r["distribution_rights_certified"]
               for r in rows)
    assert "RECEIPT_3_VS_5_DAYS" in rows[0]["editorial_conflict"]


@pytest.mark.parametrize("cut",[
    "2010-01-01T00:00:00Z", "2026-10-10T13:00:00Z",
    "2026-10-31T00:00:00Z","2026-10-31T23:59:59Z",
])
def test_future_manifest_sources_rights_and_sha_hidden_at_earlier_cut(cut):
    old=status(as_of=cut)
    assert old["source_rows"]==[]
    assert old["documentary_source_count"] is None
    assert old["manifest_sha256"] is None
    assert old["documentary_safe_by"] is None
    assert "SINDIC_CV" not in json.dumps(old)
    assert "CTPDA" not in json.dumps(old)
    assert "f5c3a7" not in json.dumps(old)
    p=report(as_of=cut)
    assert p["r16_documentary_routes"]==[]
    assert p["r16_documentary_sources_count"] is None
    assert "SINDIC_CV" not in json.dumps(p["denominator_evidence"])


def test_new_leads_add_three_documentary_groups_not_case_denominators():
    p=report(as_of="2026-11-01T00:00:00Z")
    d=p["denominator_evidence"]
    assert d["source_groups_visible"]==47
    assert len({r["source_id"] for r in d["reported_sources"]})==47
    assert set(r["source_id"] for r in d["reported_sources"][-6:-3])=={
        "SINDIC_CV_COMPLAINT_REGISTRATION",
        "CTCYL_POST_REQUEST_ACCESS_COMPLAINTS",
        "CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS",
    }
    assert not d["source_groups_additive"]
    assert all(r["observed_source_local_items"] is None
               and r["known_pending_case_count"] is None
               and r["eligible_all_received_denominator"] is None
               for r in d["reported_sources"][-6:-3])
    x=registration_readiness(readiness=p,
        source_id="CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS")
    assert set(x["rights"]["by_distribution"])=={"CSV","ODS","XLS","XML"}
    assert all("NOT_EXACT_CASE" in v for v in
               x["rights"]["by_distribution"].values())
    assert x["clocks"]["first_public_at"] is None
    assert x["clocks"]["documentary_knowledge_safe_by"]=="2026-11-01T00:00:00+00:00"
    assert x["official_links"]["confirmed_dual_id_edges"] is None


def test_old_source_and_unknown_replay_identical_with_no_future_source_membership():
    p=report(as_of="2026-10-31T23:59:59Z")
    new=registration_readiness(readiness=p,source_id="SINDIC_CV_COMPLAINT_REGISTRATION")
    unknown=registration_readiness(readiness=p,source_id="MISSING_SOURCE")
    assert new==unknown
    assert new["source"] is None and new["rights"] is None
    assert "SINDIC" not in json.dumps(new)


@pytest.mark.parametrize("mutate",[
    lambda x: x.__setitem__("new_real_case_records_acquired",3),
    lambda x: x.__setitem__("scientific_AB_cycles",1),
    lambda x: x.__setitem__("independent_all_received_denominator",1000),
    lambda x: x.__setitem__("historical_individual_first_public_at",
                           "2020-01-01T00:00:00Z"),
    lambda x: x.__setitem__("terms_or_cookies_accepted",True),
    lambda x: x["three_documentary_routes_not_added_to_any_homogeneous_risk_set"][
        0].__setitem__("distribution_rights_certified",True),
    lambda x: x["three_documentary_routes_not_added_to_any_homogeneous_risk_set"][
        1].__setitem__("preclassification_padrón_complete",True),
    lambda x: x["three_documentary_routes_not_added_to_any_homogeneous_risk_set"][
        2].__setitem__("source_id","GENCAT_SAIP_INITIAL_FILINGS"),
])
def test_manifest_mutation_quarantined_before_HTTP_or_source_admission(tmp_path,mutate):
    x=json.loads(MANIFEST.read_text(encoding="utf8"))
    mutate(x)
    dest=tmp_path/"manifest.json"
    dest.write_text(json.dumps(x),encoding="utf8")
    out=status(as_of="2026-11-01T00:00:00Z",path=dest)
    assert out["status"]=="R16_MANIFEST_QUARANTINED"
    assert out["source_rows"]==[]
    assert out["manifest_sha256"] is None
    assert out["documentary_source_count"] is None


def test_missing_and_bad_asof_fail_closed(tmp_path):
    assert status(as_of="2026-11-01T00:00:00Z",
                  path=tmp_path/"missing.json")["status"]=="R16_MANIFEST_QUARANTINED"
    with pytest.raises(ValueError):
        status(as_of="2026-10-31")
