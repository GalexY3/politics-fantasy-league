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
    assert payload["source_groups_visible"]==16
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
