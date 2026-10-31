"""Loopback-only HTTP security and as-of for real, binary-only SHA receipts."""
import http.client
from http.server import ThreadingHTTPServer
import json
import threading

import pytest

from politics_fantasy.server import handler_factory


@pytest.fixture
def svc(tmp_path):
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(tmp_path/"db.sqlite",None,None))
    t=threading.Thread(target=server.serve_forever,daemon=True)
    t.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        t.join(timeout=5)


def get(port,route,host=None):
    client=http.client.HTTPConnection("127.0.0.1",port,timeout=5)
    client.request("GET",route,headers={"Host":host} if host else {})
    response=client.getresponse()
    payload=json.loads(response.read())
    headers=dict(response.getheaders())
    status=response.status
    client.close()
    return status,payload,headers


def test_integrity_api_current_and_asof(svc):
    status,doc,headers=get(svc,"/api/retained-source-integrity")
    assert status==200
    assert doc["status"]=="PAST_LOCAL_BINARY_INTEGRITY_CONFIRMED"
    assert doc["total_files_verified"]==7
    assert not doc["actual_original_bytes_in_api_response"]
    assert not doc["individual_outcomes_in_response"]
    assert headers["X-Frame-Options"]=="DENY"
    assert headers["Cache-Control"]=="no-store"
    status,prior,_=get(svc,"/api/retained-source-integrity?as_of=2026-10-31T07%3A08%3A41Z")
    assert status==200
    assert prior["source_rows"]==[]
    assert prior["total_files_verified"] is None
    assert "67ae2bc" not in json.dumps(prior)
    assert get(svc,"/api/retained-source-integrity?as_of=2026-10-31T07%3A08%3A42Z")[1]["total_files_verified"]==7


@pytest.mark.parametrize("uri",[
    "/api/retained-source-integrity?as_of=2026-10-31",
    "/api/retained-source-integrity?as_of=invalid",
    "/api/retained-source-integrity?as_of=2026-10-31T07%3A08%3A42",
    "/api/retained-source-integrity?as_of=a&as_of=b",
    "/api/retained-source-integrity?admit=real",
    "/api/retained-source-integrity?file=../private",
])
def test_new_route_does_not_accept_arbitrary_queries(svc,uri):
    assert get(svc,uri)[0]==400


def test_dns_rebinding_host_rejected_without_leaking_status(svc):
    assert get(svc,"/api/retained-source-integrity",host="external.example")[0]==403
