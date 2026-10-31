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
    assert not result["cross_institution_joins_admitted"]
    assert result["scientific_cycles"]==0
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
