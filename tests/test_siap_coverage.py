"""One captured official index page: provenance and temporal adverse cases."""
import http.client
import json
from hashlib import sha256
from http.server import ThreadingHTTPServer
from pathlib import Path
import threading

import pytest

from politics_fantasy import siap_coverage as s
from politics_fantasy.server import handler_factory


def test_one_page_not_census_and_not_outcomes():
    r = s.status()
    assert r["status"] == "ONE_INDEX_PAGE_OF_UNCERTIFIED_POPULATION"
    assert r["source_index_pages"] == 44
    assert r["source_pages_captured"] == 1
    assert r["source_pages_missing"] == 43
    assert r["observed_links"] == 20
    assert r["original_sha256"] == s.ORIGINAL_SHA256
    assert r["historical_first_public_at"] is None
    assert r["eligible_risk_denominator"] is None
    assert not r["right_censoring_estimable"]
    assert not r["full_parliament_risk_population_verified"]
    assert not r["safe_local_observation_is_first_public_at"]
    assert not r["outcomes_analyzed"] and not r["real_person_scoring"]
    assert "202-" not in json.dumps(r)


def test_asof_precision_no_capture_leak():
    for cut in ("2024-01-01T00:00:00Z", "2026-10-31T06:02:48Z",
                "2026-10-31T06:02:48.999999Z"):
        r = s.status(as_of=cut)
        assert r["status"] == "NOT_YET_IN_LOCAL_OBSERVATORY"
        assert r["original_sha256"] is None
        assert r["observed_links"] is None
        assert r["source_index_pages"] is None
        assert "44" not in json.dumps(r)
    later = s.status(as_of="2026-10-31T08:02:49+02:00")
    assert later["observed_links"] == 20
    assert later["safe_local_observation_by"] == "2026-10-31T06:02:49+00:00"


def test_broken_manifest_can_never_reveal_counts(tmp_path: Path):
    p = tmp_path / "manifest.json"
    p.write_text('{"index_pages_captured":44,"outcomes":123456}', encoding="utf-8")
    for path in (p, tmp_path / "missing.json"):
        row = s.status(path=path)
        assert row["status"] == "INDEX_METADATA_QUARANTINED"
        assert row["observed_links"] is None
        assert row["source_index_pages"] is None


@pytest.mark.parametrize("modify", [
    lambda d: d.update(index_pages_captured=44),
    lambda d: d.update(institutional_entry_registry_complete=True),
    lambda d: d.update(pagination_complete=True),
    lambda d: d.update(pre_admission_processes_included_verified=True),
    lambda d: d.update(historical_first_public_at="2026-10-31T06:02:44Z"),
    lambda d: d.update(eligible_longitudinal_risk_denominator=20),
    lambda d: d.update(terms_accepted=True),
    lambda d: d.update(original_rows_published=True),
    lambda d: d.update(robots_receipt_sha256="0"*64),
    lambda d: d.update(source_errors=[]),
])
def test_mutated_trusted_sha_still_does_not_promote_coverage(tmp_path:Path,monkeypatch,modify):
    d=json.loads(s.MANIFEST.read_text(encoding="utf-8"))
    modify(d)
    p=tmp_path/"manifest.json"
    raw=json.dumps(d).encode("utf-8")
    p.write_bytes(raw)
    monkeypatch.setattr(s,"MANIFEST_SHA256",sha256(raw).hexdigest())
    r=s.status(path=p)
    assert r["status"]=="INDEX_METADATA_QUARANTINED"
    assert r["eligible_risk_denominator"] is None


def test_invalid_asof_is_rejected():
    with pytest.raises(ValueError,match="AS_OF_REQUIRES_TIMEZONE"):
        s.status(as_of="2026-10-31T06:02:49")
    for bad in ("", "2026-10-31", "yesterday", "0"*100):
        with pytest.raises(ValueError,match="INVALID_AS_OF"):
            s.status(as_of=bad)


def test_new_http_route_loopback_and_exact_query(tmp_path:Path):
    server=ThreadingHTTPServer(("127.0.0.1",0),
        handler_factory(tmp_path/"db.sqlite",None,None))
    worker=threading.Thread(target=server.serve_forever,daemon=True)
    worker.start()
    try:
        def get(uri,host=None):
            conn=http.client.HTTPConnection("127.0.0.1",server.server_port,timeout=5)
            conn.request("GET",uri,headers={"Host":host} if host else {})
            resp=conn.getresponse()
            result=resp.status,json.loads(resp.read())
            conn.close()
            return result
        code,old=get("/api/siap-index-coverage?as_of=2026-10-31T06%3A02%3A48Z")
        assert code==200 and old["observed_links"] is None
        code,now=get("/api/siap-index-coverage")
        assert code==200 and now["observed_links"]==20
        assert now["full_parliament_risk_population_verified"] is False
        for url in ("/api/siap-index-coverage?as_of=2026-10-31T06%3A02%3A49",
                    "/api/siap-index-coverage?as_of=invalid",
                    "/api/siap-index-coverage?as_of=2026-10-31T06%3A02%3A49Z&as_of=2026-10-31T06%3A02%3A50Z",
                    "/api/siap-index-coverage?publish=1"):
            assert get(url)[0]==400
        assert get("/api/siap-index-coverage",host="external.example")[0]==403
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=5)
