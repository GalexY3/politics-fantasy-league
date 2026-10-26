"""Local-only, read-only fixture status for PF-BR30J.

This is NOT a public API of verified political identities. No individual
names, statements, memberships or opinions returned. Fail closed.
"""
from __future__ import annotations

from collections import Counter
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "examples/actor_evidence_fixture_30j.json"


def status(path: Path | None = None) -> dict:
    p = Path(path) if path is not None else FIXTURE
    blocked = {"ok": False, "real_people_verified": 0, "real_person_scoring": False,
               "origin": "SYNTHETIC_ONLY"}
    try:
        if not p.exists() or p.stat().st_size > 100_000:
            return {**blocked, "error": "MISSING_OR_OVERSIZED"}
        x = json.loads(p.read_text(encoding="utf8"))
        if x.get("dataset_class") != "FULLY_FICTIONAL_ENGINEERING_FIXTURE":
            return {**blocked, "error": "NOT_FICTIONAL_BUNDLE"}
        sources, entities, roles, events = (
            x.get("sources"), x.get("entities"), x.get("roles"), x.get("events")
        )
        if any(not isinstance(z, list) for z in (sources, entities, roles, events)):
            return {**blocked, "error": "SCHEMA_MISSING"}
        if any(s.get("state") not in ("TEST_FIXTURE", "DOCUMENTED_ONLY")
               or s.get("kind") not in ("SYNTHETIC", "OFFICIAL")
               for s in sources if isinstance(s, dict)):
            return {**blocked, "error": "UNVERIFIED_SOURCE"}
        if any(not isinstance(o, dict) for o in entities + roles + events + sources):
            return {**blocked, "error": "INVALID_ROW"}
        if any(z.get("source_id") is None for z in entities + roles + events):
            return {**blocked, "error": "MISSING_PROVENANCE"}
        actor_types = Counter(z.get("type", "UNKNOWN") for z in entities)
        return {
            "ok": True, "origin": "SYNTHETIC_ONLY",
            "real_people_verified": 0, "real_person_scoring": False,
            "entities": len(entities), "events": len(events),
            "roles": len(roles), "sources": len(sources),
            "entities_by_type": dict(sorted(actor_types.items())),
            "uncertainty": "Fully fictitious example; official raw registry not downloaded."
        }
    except (OSError, ValueError, TypeError, KeyError, AttributeError):
        return {**blocked, "error": "INVALID_FIXTURE"}
