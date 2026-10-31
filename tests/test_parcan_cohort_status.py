"""Provenance-bound actual Canary metadata, no original rows or status outcomes."""
from __future__ import annotations

import http.client
import json
import threading
from http.server import ThreadingHTTPServer
from pathlib import Path

import pytest

import politics_fantasy.parcan_cohort_status as parcan_status
from politics_fantasy.parcan_cohort_status import status
from politics_fantasy.server import handler_factory


def test_current_real_captured_source_cohorts_are_not_parliament_census():
    d = status()
    assert d["ok"] is True and d["status"] == "AUDITED_METADATA_CURRENT_CAPTURE"
    assert d["observed_rows"] == 1754
    assert [x["rows_in_captured_distribution"] for x in d["source_cohorts"]] == [1, 686, 543, 524]
    assert [x["year"] for x in d["source_cohorts"]] == [2023, 2024, 2025, 2026]
    assert d["exposure_denominator"] is None
    assert not d["process_lifecycle_or_outcomes_admitted"]
    assert not d["real_person_scoring"]
    assert not d["complete_canarian_parliament_universe"]
    assert not d["congress_initiative_universe_verified"]
    assert not d["available_historial_vintages"]
    assert d["creation_monthly_status"] == "SOURCE_CREATION_MONTHS_AUDITED_ONLY"
    assert len(d["creation_monthly_observed_entries"]) == 34
    assert sum(m["observed_entries"] for m in d["creation_monthly_observed_entries"]) == 1754
    assert d["creation_monthly_first_public_at_verified"] is False
    assert d["creation_monthly_missing_months_unknown_not_zero"] is True
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
    assert old["local_snapshot_audited_at"] is None
    assert "686" not in json.dumps(old)
    assert "9ee689552272" not in json.dumps(old)
    now = status(as_of="2026-10-31T05:19:19Z")
    assert now["observed_rows"] == 1211
    assert now["creation_monthly_observed_entries"] is None
    assert [x["year"] for x in now["source_cohorts"]] == [2023, 2024, 2026]
    assert "13350568f6ef8f" not in json.dumps(now)
    assert "543" not in json.dumps(now)
    within_later_audit_second = status(as_of="2026-10-31T05:34:51.999999Z")
    assert within_later_audit_second["observed_rows"] == 1211
    assert "543" not in json.dumps(within_later_audit_second)
    later = status(as_of="2026-10-31T05:34:52Z")
    assert later["observed_rows"] == 1754
    assert [x["year"] for x in later["source_cohorts"]] == [2023, 2024, 2025, 2026]
    assert later["creation_monthly_observed_entries"] is None
    within_monthly_second = status(as_of="2026-10-31T05:49:50.999999Z")
    assert within_monthly_second["creation_monthly_observed_entries"] is None
    after_monthly = status(as_of="2026-10-31T05:49:51Z")
    assert after_monthly["creation_monthly_status"] == "SOURCE_CREATION_MONTHS_AUDITED_ONLY"
    assert len(after_monthly["creation_monthly_observed_entries"]) == 34


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


def test_pe2025_receipt_tampering_quarantines_all_current_aggregates(tmp_path: Path, monkeypatch):
    p = tmp_path / "altered.json"
    original = parcan_status.PE2025_RECEIPT.read_bytes()
    p.write_bytes(original.replace(b'"records_read": 543', b'"records_read": 999'))
    monkeypatch.setattr(parcan_status, "PE2025_RECEIPT", p)
    # Earlier as-of depends only on the earlier, independently pinned receipt.
    old = status(as_of="2026-10-31T05:25:00Z")
    assert old["ok"] and old["observed_rows"] == 1211
    assert "543" not in json.dumps(old)
    d = status()
    assert not d["ok"] and d["status"] == "METADATA_QUARANTINED"
    assert d["source_cohorts"] == [] and d["observed_rows"] is None
    monkeypatch.setattr(parcan_status, "PE2025_RECEIPT", tmp_path / "missing.json")
    old = status(as_of="2026-10-31T05:25:00Z")
    assert old["ok"] and old["observed_rows"] == 1211
    d = status()
    assert not d["ok"] and d["observed_rows"] is None


def test_second_precision_evidence_never_leaks_audit_during_same_second():
    for stamp in ("2026-10-31T05:19:18Z", "2026-10-31T05:19:18.999999Z"):
        d = status(as_of=stamp)
        assert d["observed_rows"] is None
        assert d["local_snapshot_audited_at"] is None
    assert status(as_of="2026-10-31T05:19:19Z")["observed_rows"] == 1211
    assert status(as_of="2026-10-31T05:34:51.999Z")["observed_rows"] == 1211
    assert status(as_of="2026-10-31T05:34:52Z")["observed_rows"] == 1754


def test_tampered_monthly_derivative_does_not_erase_provenance_of_original_cohorts(
        monkeypatch, tmp_path: Path):
    p = tmp_path / "month.json"
    p.write_text('{"creation_months_with_observed_records_only":[{"observed_entries":999999}]}',
                 encoding="utf-8")
    monkeypatch.setattr(parcan_status, "MONTHLY_RECEIPT", p)
    result = status()
    assert result["ok"] and result["observed_rows"] == 1754
    assert result["creation_monthly_status"] == "MONTHLY_DERIVATIVE_QUARANTINED"
    assert result["creation_monthly_observed_entries"] is None
    prior = status(as_of="2026-10-31T05:25:00Z")
    assert prior["ok"] and prior["observed_rows"] == 1211
    assert prior["creation_monthly_observed_entries"] is None


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
        assert code == 200 and current["observed_rows"] == 1754
        assert len(current["creation_monthly_observed_entries"]) == 34
        assert current["source_cohorts"][0]["individual_records_exposed"] is False
        code, prior = get("/api/spanish-process-cohorts?as_of=2026-10-31T05%3A25%3A00Z")
        assert code == 200 and prior["observed_rows"] == 1211
        assert prior["creation_monthly_observed_entries"] is None
        code, latest = get("/api/spanish-process-cohorts?as_of=2026-10-31T05%3A35%3A00Z")
        assert code == 200 and latest["observed_rows"] == 1754
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
