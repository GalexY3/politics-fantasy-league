"""R21 local-only HTTP: bitemporal institutional C15 demo, no real sources."""
import http.client
from http.server import ThreadingHTTPServer
import json
from threading import Thread

import pytest

from politics_fantasy.server import handler_factory


@pytest.fixture
def local(tmp_path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        handler_factory(tmp_path/"demo.sqlite", None, None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        yield server.server_port
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)


def fetch(port, suffix="", host=None):
    client=http.client.HTTPConnection("127.0.0.1",port,timeout=5)
    client.request("GET","/api/institutional-lineage-lab"+suffix,
                   headers=({"Host":host} if host else {}))
    result=client.getresponse()
    code,headers=result.status,dict(result.getheaders())
    body=json.loads(result.read())
    client.close()
    return code,body,headers


def test_two_http_snapshots_hide_future_merger_and_are_never_empirical(local):
    old=fetch(local,"?cut_on=2023-12-31&as_of=2026-04-01T00%3A00%3A00Z")
    late=fetch(local,"?cut_on=2023-12-31&as_of=2026-08-01T00%3A00%3A00Z")
    assert old[0]==late[0]==200
    assert old[2]["Cache-Control"]==late[2]["Cache-Control"]=="no-store"
    assert old[1]["link_classes"]["MERGER_PREDECESSOR"]==0
    assert late[1]["link_classes"]["MERGER_PREDECESSOR"]==2
    assert old[1]["complete_explicit_lineage_links"]==2
    assert late[1]["complete_explicit_lineage_links"]==4
    for response in (old[1],late[1]):
        assert response["evidence_class"]=="SYNTHETIC_LAB_ONLY"
        assert response["snapshot_mode"]=="HISTORICAL_SYNTHETIC_LAB"
        assert response["historical_first_public_at"] is None
        assert response["all_received_denominator"] is None
        assert response["legal_identity_authenticated"] is False
        assert response["scientific_AB_cycles"]==0
        assert "SYNTHETIC:UNIT" not in json.dumps(response)
        assert "SYNTHETIC:BODY" not in json.dumps(response)


def test_current_label_never_pretends_to_be_historical_attestation(local):
    code, data, headers=fetch(local)
    assert code==200 and data["snapshot_mode"]=="CURRENT_SYNTHETIC_LAB"
    assert data["registered_at_risk_certified"] is False
    assert data["official_source_ingestion"] is False
    assert data["source_reuse_rights_verified"] is False
    assert data["source_counts_additive"] is False
    assert headers["X-Content-Type-Options"]=="nosniff"
    assert headers["X-Frame-Options"]=="DENY"
    assert "default-src 'self'" in headers["Content-Security-Policy"]


@pytest.mark.parametrize("suffix", [
    "?as_of=bad", "?as_of=", "?as_of=2026-01-01",
    "?as_of=2026-04-01T00%3A00%3A00.000000001Z",
    "?cut_on=2032-01-01&as_of=2026-04-01T00%3A00%3A00Z",
    "?case_id=SYNTHETIC%3ASECRET",
    "?source_id=ANY_REAL_SOURCE",
    "?as_of=2026-04-01T00%3A00%3A00Z&as_of=2026-08-01T00%3A00%3A00Z",
    "?cut_on=2023-12-31&cut_on=2022-12-31",
    "?as_of=2026-04-01T00%3A00%3A00Z&insecure_mode=true",
])
def test_no_query_bypass_to_cases_rights_or_current(suffix,local):
    code,response,_=fetch(local,suffix)
    assert code==400
    assert response=={"error":"INVALID_SYNTHETIC_LINEAGE_CUT"}


def test_wrong_host_rejected_before_any_fixture(local):
    code,response,_=fetch(local,host="evil.example")
    assert code==403 and response["error"]=="LOCAL_HOST_REQUIRED"


def test_local_data_projection_has_no_personal_or_original_values(local):
    code,response,_=fetch(local)
    assert code==200
    raw=json.dumps(response).lower()
    for forbidden in ("person_name", "politician_name", "original_bytes",
                      "legal_entity_name", "private_id"):
        assert forbidden not in raw
    # An explicit null-valued gate is safer than silently suppressing its
    # name: no actual outcome should be populated by the synthetic lab.
    assert response["stage_graph"]["real_decisions_observed"] is None
