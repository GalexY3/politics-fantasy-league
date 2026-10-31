"""Local HTTP cannot transform source counts into risk-set denominator."""
import http.client
import json
import threading
from http.server import ThreadingHTTPServer

import pytest
from politics_fantasy.server import handler_factory


@pytest.fixture
def local(tmp_path):
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(tmp_path/"unused.db",None,None))
    thread=threading.Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def get(port,route,host=None):
    conn=http.client.HTTPConnection("127.0.0.1",port,timeout=3)
    conn.request("GET",route,headers={"Host":host} if host else {})
    resp=conn.getresponse()
    code,payload=resp.status,json.loads(resp.read())
    conn.close()
    return code,payload


def test_denominator_http_real_and_historical_scope(local):
    code,payload=get(local,"/api/denominator-evidence")
    assert code==200
    assert payload["eligible_risk_denominator"] is None
    assert payload["source_groups_visible"]==37
    assert payload["source_groups_additive"] is False
    assert payload["real_case_outcomes_observed_for_analysis"] is None
    assert payload["case_level_right_censoring_observed_for_analysis"] is None
    code,old=get(local,"/api/denominator-evidence?as_of=2024-01-01T00%3A00%3A00Z")
    assert code==200 and old["source_groups_visible"]==0
    assert "GALICIA" not in json.dumps(old).upper()
    assert old["reported_sources"]==[]


@pytest.mark.parametrize("q",[
    "?as_of=invalid","?as_of=2026-10-31","?as_of=2026-11-01T00%3A00%3A00",
    "?as_of=2024-01-01T00%3A00%3A00Z&as_of=2026-11-01T00%3A00%3A00Z",
    "?source=private","?include_outcomes=true"])
def test_denominator_http_does_not_accept_case_filters(local,q):
    assert get(local,"/api/denominator-evidence"+q)[0]==400


def test_denominator_http_wrong_host_rejected(local):
    assert get(local,"/api/denominator-evidence",host="evil.invalid")[0]==403


def test_single_source_query_returns_only_source_scope_never_total(local):
    code,x=get(local,"/api/denominator-evidence?source_id=PARCAN_SOURCE_LOCAL")
    assert code==200 and x["source_groups_visible"]==1
    assert x["reported_sources"][0]["observed_source_local_items"]==1754
    assert x["eligible_risk_denominator"] is None
    assert x["reported_sources"][0]["known_terminal_case_count"] is None


def test_madrid_source_has_no_census_and_no_original_case_ids(local):
    code,x=get(local,"/api/denominator-evidence?source_id=R11-A")
    assert code==200
    assert x["source_groups_visible"]==1
    assert x["reported_sources"][0]["source_id"]=="R11-A"
    assert x["reported_sources"][0]["observed_source_local_items"] is None
    assert x["reported_sources"][0]["known_pending_case_count"] is None
    assert x["eligible_risk_denominator"] is None


def test_old_cut_does_not_disclose_whether_future_r10_source_exists(local):
    p="/api/denominator-evidence?as_of=2024-01-01T00%3A00%3A00Z&source_id="
    a=get(local,p+"R10_A_CTBG_APPEALS")
    b=get(local,p+"UNKNOWN_FUTURE")
    assert a==b
    assert a[0]==200
    assert a[1]["source_groups_visible"]==0
    assert a[1]["reported_sources"]==[]
    assert "CTBG" not in str(a[1])


def test_r14_future_source_query_is_indistinguishable_from_unknown(local):
    old="/api/denominator-evidence?as_of=2026-10-31T23%3A59%3A59Z&source_id="
    a=get(local,old+"CLM_GENERAL_ACCESS_STATISTICS")
    b=get(local,old+"SOURCE_UNDOCUMENTED")
    assert a==b
    assert a[1]["reported_sources"]==[]
    new="/api/denominator-evidence?as_of=2026-11-01T00%3A00%3A00Z&source_id="
    code,post=get(local,new+"CLM_GENERAL_ACCESS_STATISTICS")
    assert code==200
    assert post["source_groups_visible"]==1
    assert post["reported_sources"][0]["observed_source_local_items"] is None
    assert post["reported_sources"][0]["known_terminal_case_count"] is None
    assert post["eligible_risk_denominator"] is None


def test_r16_future_source_not_enumerated_as_http_denominator(local):
    old="/api/denominator-evidence?as_of=2026-10-31T23%3A59%3A59Z&source_id="
    a=get(local,old+"CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS")
    b=get(local,old+"UNKNOWN_R16_SOURCE")
    assert a==b and a[0]==200
    assert a[1]["source_groups_visible"]==0
    assert "CTPDA" not in json.dumps(a[1])
    after="/api/denominator-evidence?as_of=2026-11-01T00%3A00%3A00Z&source_id="
    code,doc=get(local,after+"CTPDA_ANDALUCIA_SELECTED_REVIEW_RESOLUTIONS")
    assert code==200
    assert doc["source_groups_visible"]==1
    assert doc["eligible_risk_denominator"] is None
    assert doc["reported_sources"][0]["observed_source_local_items"] is None
    assert doc["reported_sources"][0]["known_terminal_case_count"] is None


def test_r17_confidential_register_and_unknown_identical_before_cut(local):
    base="/api/denominator-evidence?as_of=2026-10-31T23%3A59%3A59Z&source_id="
    a=get(local,base+"R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD")
    b=get(local,base+"UNKNOWN_R17")
    assert a==b and a[0]==200
    assert "OAAF" not in json.dumps(a[1])
    later="/api/denominator-evidence?as_of=2026-11-01T00%3A00%3A00Z&source_id="
    code,visible=get(local,later+"R17_OAAF_ANDALUCIA_EXTERNAL_FRAUD")
    assert code==200 and visible["source_groups_visible"]==1
    assert visible["reported_sources"][0]["observed_source_local_items"] is None
    assert visible["eligible_risk_denominator"] is None
    assert visible["reported_sources"][0]["known_terminal_case_count"] is None


@pytest.mark.parametrize("suffix",[
    "?source_id=",
    "?source_id=PARCAN_SOURCE_LOCAL&source_id=R10_A_CTBG_APPEALS",
    "?source_id=PARCAN_SOURCE_LOCAL&as_of=bad",
    "?source_id=%3Cscript%3E",
    "?source_id=PARCAN_SOURCE_LOCAL&include_rows=true",
])
def test_source_specific_query_rejects_ambiguous_or_unsafe_params(local,suffix):
    assert get(local,"/api/denominator-evidence"+suffix)[0]==400
