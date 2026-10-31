"""Source-scoped contractual status; no data or outcome retrieval."""
import json
from copy import deepcopy

import pytest

from politics_fantasy.procedural_index_contract import GateError
from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.registration_readiness_query import registration_readiness


def view(source, when="2026-11-01T00:00:00Z"):
    return registration_readiness(readiness=report(as_of=when), source_id=source)


def test_saip_is_single_existing_r13_source_with_r14_enrichment():
    r = view("GENCAT_SAIP_INITIAL_FILINGS")
    assert r["status"]=="SOURCE_VISIBLE_WITHOUT_CERTIFIED_REGISTRATION_POPULATION"
    assert r["source"]["source_id"]=="GENCAT_SAIP_INITIAL_FILINGS"
    assert r["source"]["source_groups_additive"] is False
    assert len(r["rights"]["by_distribution"])==4
    assert all("UNVERIFIED" in s for s in r["rights"]["by_distribution"].values())
    assert r["clocks"]["documentary_knowledge_safe_by"]=="2026-11-01T00:00:00+00:00"
    assert r["clocks"]["saip_catalogue_schema"]=={
        "publisher_declared_columns":35, "columns_indexed":15,
        "columns_not_verified":20, "editorial_restore_entries":2,
        "original_restore_pairs":0}
    assert r["clocks"]["first_public_at"] is None
    assert r["states"]["terminal_known"] is None
    assert r["states"]["pending_known"] is None
    assert r["states"]["right_censored_known"] is None
    assert r["population"]["independent_all_received_denominator"] is None
    assert r["official_links"]["confirmed_dual_id_edges"] is None
    assert r["science"]["R5_passed"] is False


def test_later_clm_source_cannot_be_queried_at_earlier_cut():
    old="2026-10-31T23:59:59Z"
    hidden=view("CLM_GENERAL_ACCESS_STATISTICS",old)
    unknown=view("NONEXISTENT_SOURCE_X",old)
    assert hidden==unknown
    assert hidden["rights"] is None
    assert "CLM" not in json.dumps(hidden)
    current=view("CLM_GENERAL_ACCESS_STATISTICS")
    assert current["source"]["source_id"]=="CLM_GENERAL_ACCESS_STATISTICS"
    assert current["population"]["observed_source_local_items_not_denominator"] is None
    assert current["clocks"]["saip_catalogue_schema"] is None
    assert "TERMS" in current["rights"]["scope"]


def test_old_knowledge_is_not_retroactively_enriched_with_saip():
    for cut in ("2020-01-01T00:00:00Z","2026-10-31T12:00:00Z"):
        x=view("GENCAT_SAIP_INITIAL_FILINGS",cut)
        assert x==view("MISSING_FOREVER",cut)
        assert "yjpn" not in json.dumps(x)
        assert "2026-11" not in json.dumps(x)


def test_source_local_counts_are_not_scientific_denominator():
    x=view("PARCAN_SOURCE_LOCAL")
    assert x["population"]["observed_source_local_items_not_denominator"]==1754
    assert x["population"]["eligible_survival_population"] is None
    assert x["population"]["registered_at_risk_unit_certified"] is False
    assert x["rights"]["by_distribution"]=={}
    assert x["states"]["negative_dispositions_observed"] is None
    assert not x["official_links"]["cross_institutional_linkage_authorized"]


def test_fake_denominator_or_case_outcome_promotion_fails_closed():
    doc=report(as_of="2026-11-01T00:00:00Z")
    bad=deepcopy(doc)
    next(row for row in bad["denominator_evidence"]["reported_sources"]
         if row["source_id"]=="ARAGON_GENERAL_ACCESS_STATISTICS")[
             "eligible_all_received_denominator"]=100
    with pytest.raises(GateError,match="UNATTESTED"):
        registration_readiness(readiness=bad,source_id="ARAGON_GENERAL_ACCESS_STATISTICS")
    bad=deepcopy(doc)
    bad["r14_saip_enrichment_not_additive"]["original_snapshots_compared"]=2
    with pytest.raises(GateError,match="UNTRUSTED_SAIP"):
        registration_readiness(readiness=bad,source_id="GENCAT_SAIP_INITIAL_FILINGS")


@pytest.mark.parametrize("bad",["", "x?show=1", "<img>", "X"*161])
def test_untrusted_source_ids_rejected(bad):
    with pytest.raises(GateError):
        registration_readiness(readiness=report(),source_id=bad)
