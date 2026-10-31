"""Aggregate-only metadata for a real Spanish source, no subject scoring."""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

from politics_fantasy.official_source_status import published_sources
from politics_fantasy.server import handler_factory


def test_manifest_metadata_ignores_person_level_content():
    payload = published_sources()
    assert payload["ok"] is True
    assert payload["distribution_count"] == 2
    assert payload["source_corpus_admitted"] is False
    assert payload["first_public_at_verified"] is False
    assert payload["congress_initiative_population_verified"] is False
    assert payload["real_person_scoring"] is False
    assert payload["source_aggregate_metadata_reproduced"] is True
    assert payload["metadata_rows_scanned"] == 11803
    observed = [x["metadata_audit"] for x in payload["source_data"]]
    assert sorted(x["rows_in_document"] for x in observed) == [5600, 6203]
    assert all(x["observed_years"] == 15 and x["first_year"] == "1977"
               and x["last_year"] == "2023" for x in observed)
    assert all(len(x["sha256"]) == 64 and not x["official_bytes_preserved_in_git"]
               for x in payload["source_data"])
    assert "C:\\Users" not in json.dumps(payload)


def test_malformed_manifest_fails_closed(tmp_path: Path):
    p = tmp_path / "bad.json"
    p.write_text('{"schema":"pfl.source_capture_manifest.v1","distribution":[]}', encoding="utf-8")
    assert published_sources(p)["ok"] is False
    assert published_sources(tmp_path / "missing.json")["source_data"] == []


def test_metadata_tamper_is_quarantined_and_does_not_block_capture_manifest(tmp_path: Path):
    p = tmp_path / "aggregate.json"
    p.write_text('{"phase":"PHASE2_AGGREGATE_NON_OUTCOME","outputs":[]}', encoding="utf-8")
    data = published_sources(aggregate_path=p)
    assert data["ok"] is True
    assert data["source_aggregate_metadata_reproduced"] is False
    assert data["metadata_rows_scanned"] == 0
    assert all(d["metadata_audit"]["coverage_status"] == "AGGREGATE_UNAVAILABLE_OR_UNREVIEWED"
               for d in data["source_data"])


def test_source_metadata_exposed_on_loopback_without_raw_subjects(tmp_path: Path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), handler_factory(tmp_path / "game.sqlite", None, None))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def request(host: str | None = None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
            headers = {"Host": host} if host else {}
            conn.request("GET", "/api/scientific-sources", headers=headers)
            response = conn.getresponse()
            status = response.status
            body = json.loads(response.read())
            conn.close()
            return status, body
        status, payload = request()
        assert status == 200 and payload["distribution_count"] == 2
        assert payload["metadata_rows_scanned"] == 11803
        assert "real_person_scoring" in payload and not payload["real_person_scoring"]
        status, payload = request("untrusted.example")
        assert status == 403
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=8)
