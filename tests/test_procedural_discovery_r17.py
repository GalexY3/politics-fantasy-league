"""R17 legal-all-received is NOT public, downloadable or a risk cohort."""
import json
from hashlib import sha256
from copy import deepcopy

import pytest

from politics_fantasy.procedural_discovery_r17 import MANIFEST, PIN, status
from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.registration_readiness_query import registration_readiness
from politics_fantasy.denominator_evidence_status import derive_denominator_evidence
from politics_fantasy.procedural_index_contract import GateError


CUT="2026-11-01T00:00:00Z"
BEFORE="2026-10-31T23:59:59Z"


def test_three_new_confidential_documentary_routes_not_case_cohorts():
    assert sha256(MANIFEST.read_bytes()).hexdigest()==PIN
    r=status(as_of=CUT)
    assert r["status"]=="R17_DOCUMENTARY_ONLY_CONFIDENTIAL_NO_CASE_COHORT"
    assert r["documentary_source_count"]==3
    assert r["manifest_sha256"]==PIN
    assert r["scientific_cycles"]==0
    assert r["real_denominator"] is None and r["historical_first_public_at"] is None
    assert all(x["source_originals_acquired"]==0
               and x["independent_entry_denominator"] is None
               and x["real_terminal_decisions"] is None
               and x["real_pending_or_censored"] is None
               and x["public_registry_available"] is False
               and x["distribution_rights_certified"] is False
               and x["first_public_at"] is None
               for x in r["source_rows"])
    x={a["source_id"]:a for a in r["source_rows"]}
    assert x["R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD"]["confidential_internal_register_mandated"] is True
    assert "MERE_USE" in x["R17_AIPI_NATIONAL_EXTERNAL_CHANNEL"]["terms_by_mere_access_status"] or "BINDING" in x["R17_AIPI_NATIONAL_EXTERNAL_CHANNEL"]["terms_by_mere_access_status"]


@pytest.mark.parametrize("cut",[
    "2010-01-01T00:00:00Z", "2026-10-10T12:00:00Z",BEFORE,
])
def test_historical_slices_hide_future_sources_counts_hashes_and_terms(cut):
    x=status(as_of=cut)
    assert x["source_rows"]==[]
    assert x["manifest_sha256"] is None
    assert x["documentary_source_count"] is None
    assert x["documentary_safe_by"] is None
    assert "AIPI" not in json.dumps(x)
    p=report(as_of=cut)
    assert p["r17_documentary_routes"]==[]
    assert p["r17_documentary_manifest_sha256"] is None
    assert "R17_OAAF" not in json.dumps(p["denominator_evidence"])


def test_scoped_r17_three_nonadditive_groups_after_cut_and_no_denominator():
    p=report(as_of=CUT)
    d=p["denominator_evidence"]
    assert d["source_groups_visible"]==47
    assert d["source_groups_additive"] is False
    assert len({r["source_id"] for r in d["reported_sources"]})==47
    assert {r["source_id"] for r in d["reported_sources"][-3:]}=={
        "R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD",
        "R17_AIPI_NATIONAL_EXTERNAL_CHANNEL",
        "R17_AVAF_VALENCIAN_ANTIFRAUD",
    }
    assert all(r["observed_source_local_items"] is None for r in d["reported_sources"][-3:])
    x=registration_readiness(readiness=p,source_id="R17_AIPI_NATIONAL_EXTERNAL_CHANNEL")
    assert x["population"]["independent_all_received_denominator"] is None
    assert x["rights"]["by_distribution"]["CONFIDENTIAL_CASE_REGISTER"]=="NO_PUBLIC_ORIGINAL_OR_DISTRIBUTION_PERMISSION"
    assert x["rights"]["real_original_ingestion_authorized"] is False
    assert x["clocks"]["first_public_at"] is None
    assert x["clocks"]["r17_terms_by_mere_access_status"].startswith("INDEXED_PORTAL_NOTICE")
    assert x["states"]["pending_known"] is None
    assert x["official_links"]["confirmed_dual_id_edges"] is None


def test_future_r17_source_and_nonexistent_source_scoped_outputs_equal():
    p=report(as_of=BEFORE)
    a=registration_readiness(readiness=p,source_id="R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD")
    b=registration_readiness(readiness=p,source_id="UNSEEN_FOREVER")
    assert a==b and a["source"] is None and a["rights"] is None


@pytest.mark.parametrize("mutate",[
    lambda x:x.__setitem__("scientific_AB_cycles",1),
    lambda x:x.__setitem__("terms_or_cookies_accepted",True),
    lambda x:x.__setitem__("independent_all_received_denominator",30),
    lambda x:x.__setitem__("real_case_records_or_outcomes_inspected",1),
    lambda x:x["nonadditive_documentary_routes"][0].__setitem__("public_preclassification_register_certified",True),
    lambda x:x["nonadditive_documentary_routes"][1].__setitem__("distribution_rights_certified",True),
    lambda x:x["nonadditive_documentary_routes"][2].__setitem__("official_dual_id_crosswalk",["SYNTHETIC:FORGED"]),
    lambda x:x["nonadditive_documentary_routes"][1].__setitem__("terms_by_mere_access_status","ACCEPTED"),
    lambda x:x["nonadditive_documentary_routes"][0].__setitem__("official_primary_url","https://evil.invalid"),
    lambda x:x["nonadditive_documentary_routes"][0].__setitem__("historical_case_first_public_at","2010-01-01T00:00:00Z"),
])
def test_any_unpinned_mutation_quarantines_manifest(tmp_path,mutate):
    x=json.loads(MANIFEST.read_text(encoding="utf-8"))
    mutate(x)
    out=tmp_path/"changed.json"
    out.write_text(json.dumps(x),encoding="utf-8")
    r=status(as_of=CUT,path=out)
    assert r["status"]=="R17_MANIFEST_QUARANTINED"
    assert r["source_rows"]==[] and r["manifest_sha256"] is None


def test_no_case_or_denominator_promotion_direct_assembler():
    p=report(as_of=CUT)
    bad=deepcopy(p["r17_documentary_routes"])
    bad[0]["public_registry_available"]=True
    with pytest.raises(GateError,match="R17_CONFIDENTIAL_REGISTER_NOT_PUBLIC_CENSUS"):
        derive_denominator_evidence(
            real_sources=p["institutional_sources"],as_of=CUT,
            r9_documentary_status="R9_DISCOVERY_NOT_KNOWN_AT_CUT",
            r9_regional_highlights=[],r9_national_highlights=[],
            r17_documentary_status="R17_DOCUMENTARY_ONLY_CONFIDENTIAL_NO_CASE_COHORT",
            r17_documentary_routes=bad)
    with pytest.raises(GateError,match="DOCUMENTARY_SOURCE_NOT_IN_KNOWLEDGE_AT_CUT"):
        derive_denominator_evidence(
            real_sources=p["institutional_sources"],as_of="2010-01-01T00:00:00Z",
            r9_documentary_status="R9_DISCOVERY_NOT_KNOWN_AT_CUT",
            r9_regional_highlights=[],r9_national_highlights=[],
            r17_documentary_status="R17_DOCUMENTARY_ONLY_CONFIDENTIAL_NO_CASE_COHORT",
            r17_documentary_routes=p["r17_documentary_routes"])


def test_invalid_cut_fails_and_missing_manifest_quarantines(tmp_path):
    with pytest.raises(ValueError):
        status(as_of="2026-11-01")
    assert status(as_of=CUT,path=tmp_path/"absent.json")["status"]=="R17_MANIFEST_QUARANTINED"
