"""Provenance-bound actual Canary metadata, no original rows or status outcomes."""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

from politics_fantasy.parcan_cohort_status import status
from politics_fantasy.server import handler_factory


def test_current_real_captured_source_cohorts_are_not_parliament_census():
    d = status()
    assert d["ok"] is True and d["status"] == "AUDITED_METADATA_CURRENT_CAPTURE"
    assert d["observed_rows"] == 1211
    assert [x["rows_in_captured_distribution"] for x in d["source_cohorts"]] == [1, 686, 524]
    assert [x["year"] for x in d["source_cohorts"]] == [2023, 2024, 2026]
    assert d["exposure_denominator"] is None
    assert not d["process_lifecycle_or_outcomes_admitted"]
    assert not d["real_person_scoring"]
    assert not d["complete_canarian_parliament_universe"]
    assert not d["congress_initiative_universe_verified"]
    assert not d["available_historial_vintages"]
    assert all(x["first_public_at"] is None and not x["source_population_complete"]
               for x in d["source_cohorts"])
    assert "EXTRACTO" not in json.dumps(d)
    assert "TIPO_FINALIZACION" not in json.dumps(d)


def test_pre_capture_asof_fails_closed_not_zero():
    old = status(as_of="2026-10-30T23:59:59Z")
    assert old["ok"] and old["status"] == "NOT_KNOWN_TO_LOCAL_OBSERVATORY_AT_CUT"
    assert old["source_cohorts"] == []
    assert old["observed_rows"] is None
    assert old["exposure_denominator"] is None
    assert "686" not in json.dumps(old)
    assert "9ee689552272" not in json.dumps(old)
    now = status(as_of="2026-10-31T05:19:19Z")
    assert now["observed_rows"] == 1211


def test_bad_asof_is_not_silently_coerced_to_current():
    with pytest.raises(ValueError, match="AS_OF_REQUIRES_TIMEZONE"):
        status(as_of="2026-10-31T05:19:19")
    for bad in ("2026-10-31", "not-a-time", "", "9" * 400):
        with pytest.raises(ValueError, match="INVALID_AS_OF"):
            status(as_of=bad)


def test_tampered_or_missing_receipt_cannot_publish_metadata(tmp_path: Path):
    p = tmp_path / "fake.json"
    p.write_text('{"outcomes_analyzed":true,"source_cohorts":[{"records_read":9999}]}',
                 encoding="utf-8")
    for target in (p, tmp_path / "none.json"):
        d = status(path=target)
        assert not d["ok"]
        assert d["status"] == "METADATA_QUARANTINED"
        assert d["observed_rows"] is None
        assert d["source_cohorts"] == []


def test_local_http_asof_and_host_controls(tmp_path: Path):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0), handler_factory(tmp_path / "db.sqlite", None, None))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        def get(path: str, host: str | None = None):
            conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=8)
            conn.request("GET", path, headers={"Host": host} if host else {})
            response = conn.getresponse()
            result = response.status, json.loads(response.read())
            conn.close()
            return result
        code, old = get("/api/spanish-process-cohorts?as_of=2026-10-30T23%3A59%3A59Z")
        assert code == 200 and old["observed_rows"] is None
        code, current = get("/api/spanish-process-cohorts")
        assert code == 200 and current["observed_rows"] == 1211
        assert current["source_cohorts"][0]["individual_records_exposed"] is False
        for path in (
            "/api/spanish-process-cohorts?as_of=2026-10-31T05:19:18",
            "/api/spanish-process-cohorts?as_of=invalid",
            "/api/spanish-process-cohorts?as_of=2026-10-30T00:00:00Z&as_of=2026-10-31T05:19:18Z",
            "/api/spanish-process-cohorts?force=real",
        ):
            code, data = get(path)
            assert code == 400 and data["error"] == "INVALID_AS_OF_OR_QUERY"
        code, data = get("/api/spanish-process-cohorts", host="evil.example")
        assert code == 403 and data["error"] == "LOCAL_HOST_REQUIRED"
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=8)
