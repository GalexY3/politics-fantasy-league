"""Congress membership event *documentary* records, not a personal identity service.

Dates: event_day = effective legal event; bulletin_issue_day = official issue.
Neither date proves exact first_public_at. Data is source-scoped and must not be
treated as historical training data until original availability is established.
"""
from __future__ import annotations
from collections import Counter
from datetime import date

EVENT_KINDS = frozenset({
    "FULL_CONDITION_ACQUIRED", "FULL_CONDITION_CEASED", "CREDENTIAL_SUBMITTED"
})
BOCG_IDS = frozenset({"BOCG-15-D-51", "BOCG-15-D-390"})
_REQUIRED = frozenset({
    "issuer", "bulletin_id", "item_key", "event_kind", "event_day", "bulletin_issue_day"
})


def _strict_date(value: object) -> date:
    if not isinstance(value, str) or len(value) != 10:
        raise ValueError("INVALID_DATE")
    try:
        parsed = date.fromisoformat(value)
    except ValueError as exc:
        raise ValueError("INVALID_DATE") from exc
    if parsed.isoformat() != value:
        raise ValueError("INVALID_DATE")
    return parsed


def audit_member_event_ledger(rows: list[dict]) -> dict:
    """Verify event types and issue/effective semantics, never resolve people."""
    if not isinstance(rows, list) or not rows:
        raise ValueError("RECORDS_REQUIRED")
    seen = set()
    kinds = Counter()
    bulletins = set()
    lags = []
    for row in rows:
        if not isinstance(row, dict) or set(row) != _REQUIRED:
            raise ValueError("INVALID_EVENT_SCHEMA")
        if row["issuer"] != "Congreso de los Diputados":
            raise ValueError("UNSUPPORTED_ISSUER")
        if row["bulletin_id"] not in BOCG_IDS:
            raise ValueError("UNKNOWN_BULLETIN")
        if row["event_kind"] not in EVENT_KINDS:
            raise ValueError("UNSUPPORTED_EVENT_KIND")
        item_key = row["item_key"]
        if not isinstance(item_key, str) or not item_key.strip():
            raise ValueError("INVALID_ITEM_KEY")
        key = (row["bulletin_id"], item_key, row["event_kind"])
        if key in seen:
            raise ValueError("DUPLICATE_SOURCE_EVENT_KEY")
        seen.add(key)
        event_day = _strict_date(row["event_day"])
        issue_day = _strict_date(row["bulletin_issue_day"])
        if event_day > issue_day:
            raise ValueError("EVENT_AFTER_ISSUE_DAY")
        if ((row["bulletin_id"] == "BOCG-15-D-51" and
             issue_day != date(2023, 12, 15)) or
            (row["bulletin_id"] == "BOCG-15-D-390" and
             issue_day != date(2025, 9, 12))):
            raise ValueError("ISSUE_DAY_MISMATCH")
        lags.append((issue_day - event_day).days)
        kinds[row["event_kind"]] += 1
        bulletins.add(row["bulletin_id"])
    return {
        "documented_event_rows": len(rows),
        "source_issues": sorted(bulletins),
        "by_event_kind": dict(sorted(kinds.items())),
        "observed_event_to_issue_lags": sorted(set(lags)),
        "first_public_at_exact_verified": False,
        "source_editor_authenticated": False,
        "person_identity_certified": False,
        "one_to_one_successorship_inferred": False,
        "real_person_scoring": False,
        "release_grade": False,
    }
