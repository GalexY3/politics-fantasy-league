"""Typed, non-semantic event contract. All ingested events need verified provenance."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any
from types import MappingProxyType
from collections.abc import Mapping


def as_utc(value: str | datetime) -> datetime:
    dt = datetime.fromisoformat(value.replace("Z", "+00:00")) if isinstance(value, str) else value
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ValueError("All clocks must be timezone-aware")
    return dt.astimezone(timezone.utc)


def _immutable_metadata(value):
    """Recursively snapshot JSON-like metadata, including nested collections."""
    if isinstance(value, dict):
        if any(not isinstance(key, str) for key in value):
            raise ValueError('Metadata keys must be strings')
        return MappingProxyType({key: _immutable_metadata(x) for key, x in value.items()})
    if isinstance(value, (list, tuple)):
        return tuple(_immutable_metadata(x) for x in value)
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    raise ValueError('Unsupported metadata value')


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
    metadata: Mapping[str, Any]

    def __post_init__(self):
        if not isinstance(self.metadata, dict):
            raise ValueError('Event metadata must be a JSON object')
        object.__setattr__(self, 'metadata', _immutable_metadata(self.metadata))
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


def observable_event_revisions(events: list[PoliticalEvent], *, as_of: datetime) -> list[PoliticalEvent]:
    """Resolve each event to its latest public revision at the knowledge cutoff.

    A revision's ``first_public_at`` must describe when that revision became
    public. Equally recent revisions are ambiguous and must be reconciled by
    the caller; version labels do not provide a chronological order. Keep
    ``unique_events`` separate so archives can retain all source revisions.
    """
    cutoff = as_utc(as_of)
    revisions: dict[str, list[PoliticalEvent]] = {}
    for event in unique_events(events):
        if event.observable_at(cutoff):
            revisions.setdefault(event.event_id, []).append(event)
    resolved = []
    for event_id, candidates in revisions.items():
        latest_publication = max(as_utc(event.first_public_at) for event in candidates)
        latest = [event for event in candidates if as_utc(event.first_public_at) == latest_publication]
        if len(latest) != 1:
            raise ValueError(f"Ambiguous public revisions for event: {event_id}")
        resolved.append(latest[0])
    return resolved
