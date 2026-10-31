"""Real source *metadata* composition, not real science or outcome inference."""
import http.client
from http.server import ThreadingHTTPServer
import json
from pathlib import Path
import threading

import pytest

from politics_fantasy.procedural_population_readiness import report
from politics_fantasy.server import handler_factory


def test_current_sources_have_distinct_grains_and_no_survival_denominator():
    result=report()
    assert result["schema"]=="pfl.spanish_procedural_population_readiness.v1"
    assert result["source_groups"]==3
    can,cat,congress=result["institutional_sources"]
    assert can["observed_metadata_rows"]==1754
    assert can["source_distributions_visible"]==4
    assert cat["observed_metadata_rows"]==20
    assert cat["index_pages_captured"]==1 and cat["index_pages_required"]==44
    assert congress["observed_metadata_rows"] is None
    assert congress["provenance_status"]=="DISCOVERY_NOT_ORIGINAL_CAPTURE"
    assert len(result["coverage_gates"])==9
    assert all(g["scientific_admission"]=="NOT_ATTESTED" for g in result["coverage_gates"])
    assert result["risk_set_denominator"] is None
    assert result["terminal_events_observed_for_scientific_use"] is None
    assert result["dated_transitions_observed_for_scientific_use"] is None
    assert not result["reusable_scientific_cohort"]
    linkage=result["linkage_and_identification"]
    assert linkage["independent_register_denominator"] is None
    assert linkage["event_by_cut_bounds"] is None
    assert linkage["event_by_cut_status"]=="NOT_IDENTIFIABLE_ON_CURRENT_REAL_SOURCES"
    assert linkage["unlinked_records_are_not_rejections"]
    assert not result["cross_institution_joins_admitted"]
    assert result["scientific_cycles"]==0
    assert result["r8_documentary_status"]=="R8_DOCUMENTARY_ONLY_NO_SOURCE_ADMISSION"
    assert result["r8_regional_source_count"]==6
    assert result["r8_national_documentary_assets_count"]==10
    assert result["r8_consejo_de_estado_is_not_congreso_risk_set"]
    assert result["retained_original_integrity"]["official_originals_byte_checked"]==5
    assert result["retained_original_integrity"]["private_derivatives_byte_checked"]==2
    assert not result["retained_original_integrity"]["actual_source_census_verified"]
    assert result["r9_documentary_status"]=="R9_DISCOVERY_ONLY_RIGHTS_AND_DENOMINATORS_BLOCKED"
    assert result["r9_regional_sources_documented"]==8
    assert result["r9_national_assets_documented"]==11
    assert result["r9_pre_AJ_outcome_header_exposure"]
    assert result["r10_documentary_status"]=="R10_DOCUMENTARY_ONLY_NO_RISK_FRAME"
    assert result["r10_regional_documentary_assets"]==6
    assert result["r10_national_documentary_routes"]==3
    assert result["r10_pre_AJ_outcome_category_exposure"] is True
    assert result["r11_documentary_status"]=="R11_DOCUMENTARY_RIGHTS_AND_RISK_FRAME_BLOCKED"
    assert result["r11_documentary_source_count"]==7
    assert result["r11_municipal_documentary_routes"]==4
    assert result["r11_economic_documentary_routes"]==3
    assert result["r11_rights_by_use_block"] is True
    assert result["r12_documentary_status"]=="R12_DOCUMENTARY_ONLY_NO_ADMISSIBLE_POPULATION"
    assert result["r12_documentary_routes_count"]==6
    assert result["r12_normative_route_count"]==3
    assert result["r12_appeal_route_count"]==3
    assert result["r12_no_case_vintage_pairs"]==0
    assert result["r12_outcome_selected_csv_not_all_resources"] is True
    assert result["r13_documentary_status"]=="R13_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"
    assert result["r13_documentary_sources_count"]==8
    assert result["r13_senate_age_routes_count"]==4
    assert result["r13_legal_transparency_routes_count"]==4
    assert result["r13_senate_report_not_petition_count"] is True
    assert result["r13_saip_not_gaip_denominator"] is True
    assert result["r13_restore_points_are_not_two_originals"] is True
    assert result["r14_documentary_status"] in {
        "R14_NOT_KNOWN_AT_CUT", "R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"}
    assert result["r14_new_documentary_routes_count"] in {None,4}
    assert result["r14_saip_enrichment_not_additive"] is None or (
        result["r14_saip_enrichment_not_additive"]["original_snapshots_compared"] == 0)
    assert result["r10_registration_channel_break"]["is_observed_change_in_political_behavior"] is False
    assert result["r9_no_independent_national_or_regional_denominator"] is True
    assert "source_process_id" not in json.dumps(result)
    assert "TIPO_FINALIZACION" not in json.dumps(result)


def test_historical_snapshot_no_future_count_or_external_sha_disclosed():
    prior=report(as_of="2026-10-30T00:00:00Z")
    a,b,_=prior["institutional_sources"]
    assert a["observed_metadata_rows"] is None
    assert b["observed_metadata_rows"] is None
    assert a["source_distributions_visible"] is None
    assert b["index_pages_required"] is None
    as_text=json.dumps(prior)
    assert "1754" not in as_text and "3846b9fec" not in as_text
    assert prior["r8_regional_source_count"] is None
    assert prior["r8_regional_routes"]==[]
    assert prior["r8_audit_safe_by"] is None
    assert prior["retained_original_integrity"]["official_originals_byte_checked"] is None
    assert prior["retained_original_integrity"]["local_audit_safe_by"] is None
    assert prior["r9_regional_sources_documented"] is None
    assert prior["r9_national_highlights"]==[]
    assert prior["r9_pre_AJ_outcome_header_exposure"] is None
    assert prior["r10_regional_documentary_assets"] is None
    assert prior["r10_national_highlights"]==[]
    assert prior["r10_registration_channel_break"] is None
    assert prior["r10_pre_AJ_outcome_category_exposure"] is None
    assert prior["r11_documentary_status"]=="R11_DOCUMENTARY_NOT_KNOWN_AT_CUT"
    assert prior["r11_documentary_source_count"] is None
    assert prior["r11_documentary_routes"]==[]
    assert prior["r11_rights_by_use_block"] is None
    assert prior["r12_documentary_status"]=="R12_NOT_KNOWN_AT_CUT"
    assert prior["r12_documentary_routes_count"] is None
    assert prior["r12_documentary_routes"]==[]
    assert prior["r12_no_case_vintage_pairs"] is None
    assert prior["r13_documentary_status"]=="R13_NOT_KNOWN_AT_CUT"
    assert prior["r13_documentary_sources_count"] is None
    assert prior["r13_documentary_sources"]==[]
    assert prior["r13_senate_report_not_petition_count"] is None
    assert prior["r13_restore_points_are_not_two_originals"] is None
    assert prior["r14_documentary_status"]=="R14_NOT_KNOWN_AT_CUT"
    assert prior["r14_new_documentary_routes_count"] is None
    assert prior["r14_documentary_routes"]==[]
    assert prior["r14_saip_enrichment_not_additive"] is None
    assert prior["r14_documentary_manifest_sha256"] is None
    assert prior["r9_no_independent_national_or_regional_denominator"] is None
    middle=report(as_of="2026-10-31T05:20:00Z")
    assert middle["institutional_sources"][0]["observed_metadata_rows"]==1211
    assert middle["institutional_sources"][1]["observed_metadata_rows"] is None
    later=report(as_of="2026-10-31T06:02:49Z")
    assert later["institutional_sources"][0]["observed_metadata_rows"]==1754
    assert later["institutional_sources"][1]["observed_metadata_rows"]==20
    assert later["risk_set_denominator"] is None


@pytest.mark.parametrize("value",["", "2026-10-31", "missing", "2026-10-31T06:02:49"])
def test_invalid_cut_is_not_silently_replaced_by_current(value):
    with pytest.raises(ValueError):
        report(as_of=value)


def test_http_status_historical_cut_and_duplicate_query(tmp_path: Path):
    server=ThreadingHTTPServer(("127.0.0.1",0),
        handler_factory(tmp_path/"db.sqlite",None,None))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        def get(uri,host=None):
            c=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            c.request("GET",uri,headers={"Host":host} if host else {})
            resp=c.getresponse()
            status,payload=resp.status,json.loads(resp.read())
            c.close()
            return status,payload
        status,old=get("/api/procedural-population-readiness?as_of=2026-10-30T00%3A00%3A00Z")
        assert status==200 and old["institutional_sources"][0]["observed_metadata_rows"] is None
        status,current=get("/api/procedural-population-readiness")
        assert status==200 and current["institutional_sources"][1]["observed_metadata_rows"]==20
        for uri in (
            "/api/procedural-population-readiness?as_of=2026-10-30",
            "/api/procedural-population-readiness?as_of=invalid",
            "/api/procedural-population-readiness?as_of=x&as_of=y",
            "/api/procedural-population-readiness?admit=real",
        ):
            assert get(uri)[0]==400
        assert get("/api/procedural-population-readiness",host="external.example")[0]==403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=5)
