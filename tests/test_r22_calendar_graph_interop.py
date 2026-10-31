"""R22: a local legal day and a UTC day are different event cut contracts.

Prepatch oracle only. Fixtures are fixed SYNTHETIC data; no external calls,
protected originals, cases, personal data, rights or observed outcomes.
"""
from http.server import ThreadingHTTPServer
import http.client
import json
from threading import Thread

import pytest

from politics_fantasy.procedural_index_contract import (
    GateError, legal_day_completed,
)
from politics_fantasy.synthetic_institutional_demo import fixture, report
from politics_fantasy.synthetic_institutional_lineage import (
    audit_institutional_lineage,
)
from politics_fantasy.synthetic_registration_graph import audit_graph
from politics_fantasy.server import handler_factory


def test_madrid_civil_october_cut_is_completed_before_utc_midnight():
    as_of="2026-11-01T00:30:00+01:00"
    assert legal_day_completed(
        cut_on="2026-10-31",as_of=as_of,
        legal_calendar_zone="Europe/Madrid")
    # The registered stage events are in 2020, so the only relevant cut
    # interaction here is local-calendar completion, not stage membership.
    result=report(as_of=as_of,cut_on="2026-10-31")
    assert result["status"]=="SYNTHETIC_LINEAGE_DOCUMENTARY_ONLY"
    assert result["stage_graph"]["visible_claimed_edges"]==1
    assert result["legal_calendar_zone"]=="Europe/Madrid"
    assert result["historical_first_public_at"] is None
    assert result["scientific_AB_cycles"]==0


def test_legacy_utc_graph_still_rejects_same_utc_day_cut():
    units,links,bindings,stages,edges=fixture()
    with pytest.raises(GateError,match="LEGAL_EVENT_DAY_NOT_COMPLETED_AT_KNOWLEDGE"):
        audit_graph(records=stages,edges=edges,cut_on="2026-10-31",
                    as_of="2026-10-31T23:30:00Z")


def test_canary_legal_midnight_is_later_than_madrid_cut():
    as_of="2026-10-31T23:30:00Z"
    assert legal_day_completed(
        cut_on="2026-10-31",as_of=as_of,
        legal_calendar_zone="Europe/Madrid")
    assert not legal_day_completed(
        cut_on="2026-10-31",as_of=as_of,
        legal_calendar_zone="Atlantic/Canary")


def test_madrid_incomplete_previous_local_day_must_still_fail_closed():
    with pytest.raises(GateError,match="LINEAGE_LEGAL_DAY_INCOMPLETE"):
        report(as_of="2026-10-31T23:30:00+01:00",cut_on="2026-10-31")


def test_no_inference_that_admitted_local_day_means_historic_first_public():
    # A legal event cutoff is not an authenticated first-public witness.
    r=report(as_of="2026-11-01T00:30:00+01:00",cut_on="2026-10-31")
    assert r["legal_identity_authenticated"] is False
    assert r["historical_first_public_at"] is None
    assert r["registered_at_risk_certified"] is False
    assert r["all_received_denominator"] is None


def test_direct_graph_declared_madrid_zone_accepts_cut_but_canary_rejects():
    units,links,bindings,stages,edges=fixture()
    kwargs=dict(records=stages,edges=edges,cut_on="2026-10-31",
                as_of="2026-10-31T23:30:00Z")
    madrid=audit_graph(**kwargs,legal_calendar_zone="Europe/Madrid")
    assert madrid["status"]=="SYNTHETIC_DOCUMENTARY_GRAPH_ONLY"
    assert madrid["visible_claimed_edges"]==1
    with pytest.raises(GateError,match="LEGAL_EVENT_DAY_NOT_COMPLETED_AT_KNOWLEDGE"):
        audit_graph(**kwargs,legal_calendar_zone="Atlantic/Canary")


def test_invalid_legal_timezone_not_coerced_to_utc():
    _,_,_,stages,edges=fixture()
    with pytest.raises(GateError,match="LEGAL_CALENDAR_ZONE_REQUIRED"):
        audit_graph(records=stages,edges=edges,cut_on="2026-10-31",
                    as_of="2026-11-01T00:30:00+01:00",
                    legal_calendar_zone="Europe/Lisbon")


def test_actual_local_http_preserves_madrid_civil_cut_and_no_store(tmp_path):
    server=ThreadingHTTPServer(("127.0.0.1",0),handler_factory(
        tmp_path/"db.sqlite",None,None))
    thread=Thread(target=server.serve_forever,daemon=True)
    thread.start()
    try:
        conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
        conn.request("GET","/api/institutional-lineage-lab?cut_on=2026-10-31"
                     "&as_of=2026-11-01T00%3A30%3A00%2B01%3A00")
        resp=conn.getresponse()
        body=json.loads(resp.read())
        assert resp.status==200
        assert resp.getheader("Cache-Control")=="no-store"
        assert body["legal_calendar_zone"]=="Europe/Madrid"
        assert body["status"]=="SYNTHETIC_LINEAGE_DOCUMENTARY_ONLY"
        assert body["stage_graph"]["visible_claimed_edges"]==1
        assert body["all_received_denominator"] is None
        assert body["historical_first_public_at"] is None
        conn.close()
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=3)
