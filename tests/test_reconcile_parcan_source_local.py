"""Synthetic-only adversarials for cross-year, source-local metadata QA."""
from __future__ import annotations

from hashlib import sha256
import json
from pathlib import Path
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import reconcile_parcan_source_local as audit


def row(scope: str, year: int, kind: str, leg: int, ident: str, digest: str):
    return {
        "schema": "pfl.parcan_source_local_process_metadata.v1",
        "authority": "PARLAMENTO_CANARIAS",
        "source_scope": scope, "legislature": leg, "process_family": kind,
        "source_process_id": ident, "created_on": f"{year}-03-02",
        "source_sha256": digest, "recorded_at": "2026-10-31T05:50:00+00:00",
        "first_public_at": None, "terminal_state": None, "transition_events": None,
        "outcome_fields_analyzed": False, "historical_asof_admitted": False,
        "scope_population_certified": False,
    }


def test_conservative_months_and_readonly_outcomes(monkeypatch):
    scopes = {
        "test:2024": (11, "PE", 2024, 1, "a" * 64),
        "test:2025": (11, "PE", 2025, 1, "b" * 64),
    }
    monkeypatch.setattr(audit, "SCOPES", scopes)
    d1 = (json.dumps(row("test:2024", 2024, "PE", 11, "one", "a" * 64))+"\n").encode()
    d2 = (json.dumps(row("test:2025", 2025, "PE", 11, "two", "b" * 64))+"\n").encode()
    src = (("a.jsonl", sha256(d1).hexdigest(), 1),
           ("b.jsonl", sha256(d2).hexdigest(), 1))
    result = audit.audit_payloads([d1, d2], expected_sources=src)
    assert result["source_local_total"] == 2
    assert result["source_local_unique_keys"] == 2
    assert len(result["creation_months_with_observed_records_only"]) == 2
    assert result["missing_months_are_unknown_not_zero"] is True
    assert result["source_creation_date_is_first_public_at"] is False
    assert result["publisher_census_completeness_certified"] is False
    assert "source_process_id" not in json.dumps(result)


@pytest.mark.parametrize("modify,reason", [
    (lambda d: d.update(first_public_at="2024-03-02T00:00:00Z"),
     "SOURCE_LOCAL_SEMANTICS_CHANGED"),
    (lambda d: d.update(terminal_state="APPROVED"),
     "SOURCE_LOCAL_SEMANTICS_CHANGED"),
    (lambda d: d.update(outcome_fields_analyzed=True),
     "SOURCE_LOCAL_SEMANTICS_CHANGED"),
    (lambda d: d.update(created_on="2027-03-02"), "WRONG_SOURCE_YEAR"),
    (lambda d: d.update(created_on="2024-02-30"), "INVALID_DATE_ONLY"),
    (lambda d: d.update(EXTRACTO="PRIVATE_PERSON"), "UNKNOWN_SOURCE_LOCAL_FIELD"),
    (lambda d: d.update(legislature=12), "SOURCE_LOCAL_SEMANTICS_CHANGED"),
])
def test_adversarial_source_local_fields_fail_closed(monkeypatch, modify, reason):
    monkeypatch.setattr(audit, "SCOPES", {"test:2024": (11, "PE", 2024, 1, "a" * 64)})
    item = row("test:2024", 2024, "PE", 11, "one", "a" * 64)
    modify(item)
    body = (json.dumps(item)+"\n").encode()
    with pytest.raises(audit.AuditError, match=reason):
        audit.audit_payloads([body], expected_sources=[("mock.jsonl",sha256(body).hexdigest(),1)])


def test_previously_frozen_hash_cannot_be_swapped(monkeypatch):
    monkeypatch.setattr(audit, "SCOPES", {"test:2024": (11, "PE", 2024, 1, "a" * 64)})
    d = (json.dumps(row("test:2024", 2024, "PE", 11, "one", "a" * 64))+"\n").encode()
    with pytest.raises(audit.AuditError, match="LOCAL_JSONL_SHA_MISMATCH"):
        audit.audit_payloads([d], expected_sources=[("mock.jsonl","f"*64,1)])


def test_cross_distribution_duplicate_keys_rejected(monkeypatch):
    monkeypatch.setattr(audit, "SCOPES", {
        "s1": (11, "PE", 2024, 1, "a" * 64),
        "s2": (11, "PE", 2025, 1, "b" * 64),
    })
    d1=(json.dumps(row("s1",2024,"PE",11,"DUP","a"*64))+"\n").encode()
    d2=(json.dumps(row("s2",2025,"PE",11,"DUP","b"*64))+"\n").encode()
    with pytest.raises(audit.AuditError, match="DUPLICATE_CROSS_DISTRIBUTION_PROCESS_ID"):
        audit.audit_payloads([d1,d2],expected_sources=[
            ("a.jsonl",sha256(d1).hexdigest(),1),("b.jsonl",sha256(d2).hexdigest(),1)])


def test_duplicate_json_properties_rejected(monkeypatch):
    monkeypatch.setattr(audit, "SCOPES", {"test:2024": (11, "PE", 2024, 1, "a" * 64)})
    d = (json.dumps(row("test:2024",2024,"PE",11,"one","a"*64))[:-1] + ', "created_on": "2024-01-01"}\n').encode()
    with pytest.raises(audit.AuditError, match="DUPLICATE_JSON_KEY"):
        audit.audit_payloads([d],expected_sources=[("a.jsonl",sha256(d).hexdigest(),1)])
