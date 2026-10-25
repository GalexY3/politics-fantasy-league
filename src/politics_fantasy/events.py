"""Typed, non-semantic event contract. All ingested events need verified provenance."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any


def as_utc(value: str | datetime) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("All clocks must be timezone-aware")
    return dt.astimezone(timezone.utc)


@dataclass(frozen=True)
class PoliticalEvent:
    event_id: str
    kind: str
    occurred_at: datetime
    first_public_at: datetime
    person_ids: tuple[str, ...]
    source_url: str
    raw_sha256: str
    source_version: str
    metadata: dict[str, Any]

    def __post_init__(self):
        if not self.event_id or not self.kind or not self.source_url or not self.source_version:
            raise ValueError("Missing event identity/provenance")
        if len(self.raw_sha256) != 64 or any(c not in '0123456789abcdef' for c in self.raw_sha256):
            raise ValueError("raw_sha256 must be lowercase hex SHA-256")
        if as_utc(self.first_public_at) < as_utc(self.occurred_at):
            # Some advance notices legitimately precede occurrences. They must have a
            # separate SCHEDULED kind, not be mislabelled observed events.
            if not self.kind.startswith("scheduled_"):
                raise ValueError("Observed event cannot be public before it occurred")
        if len(set(self.person_ids)) != len(self.person_ids):
            raise ValueError("Duplicate person in event; represent roles separately")

    def observable_at(self, as_of: datetime) -> bool:
        return as_utc(self.first_public_at) <= as_utc(as_of)


def unique_events(events: list[PoliticalEvent]) -> list[PoliticalEvent]:
    """Deduplicate exact same identity and revision; conflicting versions fail loudly."""
    found: dict[tuple[str, str], PoliticalEvent] = {}
    for e in events:
        key = (e.event_id, e.source_version)
        if key in found and found[key] != e:
            raise ValueError(f"Conflicting source revision for event: {key}")
        found[key] = e
    return list(found.values())
