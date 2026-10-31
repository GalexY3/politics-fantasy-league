"""R14 public metadata gate never becomes an empirical R5 admission."""
import json
from hashlib import sha256
from pathlib import Path

import pytest

from politics_fantasy.procedural_discovery_r14 import MANIFEST, PIN, status


def test_exact_reviewed_redaction_and_new_routes_only():
    assert sha256(MANIFEST.read_bytes()).hexdigest() == PIN
    r = status(as_of="2026-11-01T00:00:00Z")
    assert r["status"] == "R14_DOCUMENTARY_ONLY_NO_COHORT_CERTIFIED"
    assert r["new_documentary_routes_count"] == 4
    assert len({x["source_id"] for x in r["source_rows"]}) == 4
    assert r["manifest_sha256"] == PIN
    assert all(x["source_originals_acquired"] == 0 for x in r["source_rows"])
    assert all(x["independent_entry_denominator"] is None for x in r["source_rows"])
    assert all(x["real_terminal_decisions"] is None for x in r["source_rows"])
    assert all(x["real_pending_or_censored"] is None for x in r["source_rows"])
    assert all(x["first_public_at"] is None for x in r["source_rows"])
    assert r["existing_saip_enrichment"]["existing_source_id"] == "GENCAT_SAIP_INITIAL_FILINGS"
    assert r["existing_saip_enrichment"]["original_snapshots_compared"] == 0
    assert r["existing_saip_enrichment"]["column_names_not_verified"] == 20
    assert r["real_denominator"] is None and r["scientific_cycles"] == 0


@pytest.mark.parametrize("cut", [
    "2026-10-10T13:00:00Z", "2026-10-24T13:00:00Z",
    "2026-10-31T00:00:00Z", "2026-10-31T23:59:59Z"])
def test_edition_date_and_same_audit_day_never_leak_new_knowledge(cut):
    r = status(as_of=cut)
    assert r["status"] == "R14_NOT_KNOWN_AT_CUT"
    assert r["new_documentary_routes_count"] is None
    assert r["source_rows"] == []
    assert r["existing_saip_enrichment"] is None
    assert r["manifest_sha256"] is None
    assert r["documentary_safe_by"] is None
    assert "yjpn-vcw8" not in json.dumps(r)
    assert "Ciudad Real" not in json.dumps(r)


def test_quarantine_on_modified_or_missing_manifest(tmp_path: Path):
    altered = tmp_path / "r14.json"
    altered.write_bytes(MANIFEST.read_bytes() + b" ")
    q = status(as_of="2026-11-01T00:00:00Z", path=altered)
    assert q["status"] == "R14_SOURCE_QUARANTINED"
    assert q["source_rows"] == [] and q["manifest_sha256"] is None
    assert q["new_documentary_routes_count"] is None
    assert q["existing_saip_enrichment"] is None
    assert status(as_of="2026-11-01T00:00:00Z", path=tmp_path / "missing")[
        "status"] == "R14_SOURCE_QUARANTINED"


@pytest.mark.parametrize("mutation", [
    ("terms_accepted", True),
    ("case_outcomes_inspected", 1),
    ("all_received_denominator", 23400),
    ("individual_first_public_at", "2026-10-10T13:00:00Z"),
    ("historical_original_vintage_pairs_verified", 2),
    ("case_cross_institutional_joins_verified", 1),
])
def test_any_unauthorized_promotion_fails_closed(tmp_path, mutation):
    d = json.loads(MANIFEST.read_text(encoding="utf8"))
    k, v = mutation
    d[k] = v
    altered = tmp_path / "mutated.json"
    altered.write_text(json.dumps(d), encoding="utf8")
    r = status(as_of="2026-11-01T00:00:00Z", path=altered)
    assert r["status"] == "R14_SOURCE_QUARANTINED"
    assert r["real_denominator"] is None
    assert r["real_terminal_outcomes"] is None


def test_bad_asof_does_not_default_to_now():
    with pytest.raises(ValueError):
        status(as_of="2026-10-31")
