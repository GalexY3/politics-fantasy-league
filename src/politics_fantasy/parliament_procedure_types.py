"""Pure procedural source-kind validator for Congress XV. No scoring or identity resolution."""
from datetime import date

_TYPES = {
    "PLENARY_DIARY": {"FULL_CONDITION_ACQUIRED"},
    "MEMBER_PROFILE": {"COMMISSION_ROLE_STARTED", "FULL_CONDITION_REPORTED"},
    "INITIATIVE_FILE": {"ACTIVITY_STATEMENT_SUBMITTED", "ACTIVITY_STATEMENT_QUALIFIED"},
}


def audit_procedural_events(events):
    if not isinstance(events, list) or not events:
        raise ValueError("EVENTS_REQUIRED")
    out = []
    unique = set()
    for obj in events:
        if not isinstance(obj, dict) or set(obj) != {
            "issuer", "legislature", "record_family", "event_kind",
            "event_day", "record_ref",
        }:
            raise ValueError("INVALID_EVENT_SCHEMA")
        if obj["issuer"] != "Congreso de los Diputados" or obj["legislature"] != "XV":
            raise ValueError("UNSUPPORTED_SCOPE")
        family, kind = obj["record_family"], obj["event_kind"]
        if kind not in _TYPES.get(family, set()):
            raise ValueError("MISMATCHED_SOURCE_ASSERTION")
        try:
            value = date.fromisoformat(obj["event_day"])
            if value.isoformat() != obj["event_day"]:
                raise ValueError()
        except (TypeError, ValueError) as exc:
            raise ValueError("INVALID_EVENT_DAY") from exc
        if not isinstance(obj["record_ref"], str) or not obj["record_ref"].strip():
            raise ValueError("MISSING_RECORD_REFERENCE")
        key = (family, kind, obj["record_ref"], obj["event_day"])
        if key in unique:
            raise ValueError("DUPLICATE_PROCEDURE")
        unique.add(key)
        out.append((kind, obj["event_day"]))
    return {
        "source_events": len(out),
        "typed_event_days": dict(out),
        "all_claims_issuer_scoped": True,
        "first_public_at": None,
        "historical_person_id_certified": False,
        "real_person_scoring": False,
        "release_grade": False,
    }
