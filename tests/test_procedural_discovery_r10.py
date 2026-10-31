"""Actual R10 metadata SHA checks and adversarial source-scope tests."""
from hashlib import sha256
import json
from pathlib import Path
import pytest

from politics_fantasy.procedural_discovery_r10 import (
    MANIFEST,PIN,REGIONAL_UPSTREAM,NATIONAL_UPSTREAM,status,
)


def test_r10_redacted_metadata_has_real_pinned_worker_lineage_but_no_originals():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    assert d["upstream_private_worker_matrices_sha256"]=={
        "regional":REGIONAL_UPSTREAM,"national":NATIONAL_UPSTREAM}
    result=status()
    assert result["status"]=="R10_DOCUMENTARY_ONLY_NO_RISK_FRAME"
    assert result["regional_total"]==6 and result["national_routes_total"]==3
    assert len(result["regional_routes"])==3
    assert len(result["national_routes"])==3
    assert result["new_originals_acquired"]==0
    assert result["science_denominator"] is None
    assert result["terminal_real_events"] is None
    assert result["right_censored_real_cases"] is None
    assert result["pre_mesa_and_post_referral_populations_must_not_be_summed"]
    assert result["dissolution_pending_stock_not_total_prior_initiatives"]
    assert result["outcome_headings_seen_before_AJ"]
    assert result["administrative_register_regime_change"]["is_observed_change_in_political_behavior"] is False


def test_cut_prior_to_date_only_audit_hides_the_source_totals_and_diagnostics():
    for when in ("2025-01-01T00:00:00Z","2026-10-31T23:59:59.999Z"):
        x=status(as_of=when)
        assert x["status"]=="R10_DOCUMENTARY_NOT_KNOWN_AT_CUT"
        assert x["regional_total"] is None
        assert x["national_routes_total"] is None
        assert x["manifest_sha256"] is None
        assert x["regional_routes"]==[] and x["national_routes"]==[]
        assert x["administrative_register_regime_change"] is None
        assert x["outcome_headings_seen_before_AJ"] is None
        assert "Andalucía" not in str(x) and "CTBG" not in str(x)
    assert status(as_of="2026-11-01T00:00:00Z")["regional_total"]==6


@pytest.mark.parametrize("path,field,value",[
    ("reg","all_received_register_count",100),
    ("reg","data_distribution_licence","PUBLIC_DOMAIN"),
    ("reg","known_case_decisions",3),
    ("national","rights_to_acquire_case_source",True),
    ("national","independent_entry_denominator",50),
    ("national","first_public_at","2026-03-20T00:00:00Z"),
])
def test_tampered_source_cannot_promote_rights_denominator_or_first_public(tmp_path, path, field, value):
    d=json.loads(MANIFEST.read_text(encoding="utf8"))
    xs=d["regional_documentary_assets"] if path=="reg" else d["distinct_institutional_entry_routes"]
    xs[0][field]=value
    forged=tmp_path/"forged.json"
    forged.write_text(json.dumps(d),encoding="utf8")
    result=status(path=forged)
    assert result["status"]=="R10_DOCUMENTARY_QUARANTINED"
    assert result["regional_routes"]==[]
    assert result["national_routes"]==[]


def test_untrusted_extra_json_fields_quarantine(tmp_path):
    obj=json.loads(MANIFEST.read_text(encoding="utf8"))
    obj["scientific_census"]=True
    p=tmp_path/"forged.json"
    p.write_text(json.dumps(obj),encoding="utf8")
    assert status(path=p)["status"]=="R10_DOCUMENTARY_QUARANTINED"


@pytest.mark.parametrize("cut",["2026-10-31","unknown","2026-10-31T12:00:00"])
def test_invalid_cut_never_defaults_to_today(cut):
    with pytest.raises(ValueError):
        status(as_of=cut)
