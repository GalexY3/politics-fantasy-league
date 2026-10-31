"""Only provenance-bound documentary counts, never survival or outcome rates."""
from __future__ import annotations

import http.client
from hashlib import sha256
import json
from pathlib import Path
import threading
from http.server import ThreadingHTTPServer

import pytest

from politics_fantasy import procedural_coverage as source
from politics_fantasy.server import handler_factory


def test_current_counts_are_only_metadata_corroboration():
    r = source.coverage_status()
    assert r["status"] == "CONCORDANT_SOURCE_COUNTERS_NOT_CENSUS"
    assert r["editorial_count_total"] == 1753
    assert r["source_observed_rows"] == 1753
    assert [(x["year"],x["local_original_rows"]) for x in r["source_strata"]] == [
        (2024,686), (2025,543), (2026,524)]
    assert all(x["eligible_risk_denominator"] is None for x in r["source_strata"])
    assert r["eligible_longitudinal_risk_denominator"] is None
    assert r["independent_database_verified"] is False
    assert r["outcomes_admitted"] is False
    assert r["cross_institutional_links_admitted"] is False
    assert r["first_public_at"] is None
    assert len(r["missing_for_survival"]) == 6
    as_json=json.dumps(r)
    for forbidden in ("EXTRACTO", "TIPO_FINALIZACION", "SITUACION", "source_process_id"):
        assert forbidden not in as_json


def test_day_precision_cannot_reveal_source_before_november_1():
    for moment in ("2024-01-01T00:00:00Z",
                   "2026-10-31T00:00:00Z",
                   "2026-10-31T23:59:59.999999Z"):
        r=source.coverage_status(as_of=moment)
        assert r["status"] == "SOURCE_NOT_KNOWN_AT_REQUESTED_CUT"
        assert r["source_strata"] == []
        assert r["editorial_count_total"] is None
        assert r["safe_local_observation_by"] is None
        assert "1753" not in json.dumps(r) and "686" not in json.dumps(r)
    ready=source.coverage_status(as_of="2026-11-01T01:00:00+01:00")
    assert ready["editorial_count_total"] == 1753
    assert ready["safe_by_is_not_first_public_at"]


def test_invalid_asof_rejected_without_fallback():
    with pytest.raises(ValueError,match="AS_OF_REQUIRES_TIMEZONE"):
        source.coverage_status(as_of="2026-11-01T00:00:00")
    for bad in ("", "yesterday", "2026-11-01", "9"*100):
        with pytest.raises(ValueError,match="INVALID_AS_OF"):
            source.coverage_status(as_of=bad)


def test_bad_or_missing_provenance_quarantined_even_if_counts_plausible(tmp_path:Path):
    p=tmp_path/"source.json"
    original=source.MANIFEST.read_bytes()
    assert sha256(original).hexdigest()==source.EXPECTED_SHA256
    p.write_bytes(original.replace(b'"editorial_reported_count": 543',
                                   b'"editorial_reported_count": 999'))
    for path in (p,tmp_path/"missing.json"):
        r=source.coverage_status(path=path)
        assert r["status"]=="CROSSVIEW_QUARANTINED"
        assert r["source_observed_rows"] is None
        assert r["source_strata"]==[]
    # The future record is not examined to answer an earlier cut.
    old=source.coverage_status(path=p,as_of="2026-10-31T12:00:00Z")
    assert old["status"]=="SOURCE_NOT_KNOWN_AT_REQUESTED_CUT"


@pytest.mark.parametrize("edit",[
    lambda d:d.update(html_original_bytes_archived=True),
    lambda d:d.update(html_source_database_independent_from_csv=True),
    lambda d:d.update(eligible_longitudinal_risk_population_certified=True),
    lambda d:d.update(status_or_terminal_outcomes_analyzed=True),
    lambda d:d["cohorts"][0].update(editorial_reported_count=999),
    lambda d:d["cohorts"][0].update(year=2025),
    lambda d:d["cohorts"].append(d["cohorts"][0]),
])
def test_modified_manifest_cannot_pass_even_with_trusted_checksum_override(
        tmp_path:Path,monkeypatch,edit):
    payload=json.loads(source.MANIFEST.read_text(encoding="utf-8"))
    edit(payload)
    p=tmp_path/"changed.json"
    p.write_text(json.dumps(payload),encoding="utf-8")
    monkeypatch.setattr(source,"EXPECTED_SHA256",sha256(p.read_bytes()).hexdigest())
    d=source.coverage_status(path=p)
    assert d["status"]=="CROSSVIEW_QUARANTINED"
    assert d["eligible_longitudinal_risk_denominator"] is None


def test_duplicate_keys_rejected_even_with_digest_rewritten(tmp_path:Path,monkeypatch):
    raw=source.MANIFEST.read_bytes().replace(b'"publisher": "Parlamento de Canarias",',
       b'"publisher": "Parlamento de Canarias", "publisher": "CONGRESO",')
    p=tmp_path/"duplicate.json"
    p.write_bytes(raw)
    monkeypatch.setattr(source,"EXPECTED_SHA256",sha256(raw).hexdigest())
    assert source.coverage_status(path=p)["status"]=="CROSSVIEW_QUARANTINED"


def test_http_route_asof_and_local_host(tmp_path:Path):
    server=ThreadingHTTPServer(("127.0.0.1",0),
        handler_factory(tmp_path/"demo.sqlite",None,None))
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try:
        def request(uri,host=None):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET",uri,headers={"Host":host} if host else {})
            response=conn.getresponse()
            code,body=response.status,json.loads(response.read())
            conn.close()
            return code,body
        code,before=request("/api/procedural-coverage?as_of=2026-10-31T23%3A59%3A59Z")
        assert code==200 and before["source_strata"]==[] and before["editorial_count_total"] is None
        code,current=request("/api/procedural-coverage")
        assert code==200 and current["editorial_count_total"]==1753
        assert current["eligible_longitudinal_risk_denominator"] is None
        for uri in ("/api/procedural-coverage?as_of=2026-10-31T23%3A59%3A59",
                    "/api/procedural-coverage?as_of=invalid",
                    "/api/procedural-coverage?as_of=2026-10-31T00%3A00%3A00Z&as_of=2026-11-01T00%3A00%3A00Z",
                    "/api/procedural-coverage?admit=1"):
            assert request(uri)[0]==400
        assert request("/api/procedural-coverage",host="other.example")[0]==403
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
