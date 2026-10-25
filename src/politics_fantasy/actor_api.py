"""Read-only aggregate political-universe lab status, offline fixture only.

Never returns person names, private affiliations, political ratings or scores.
The JS actor-universe contract has separate strict referential/time validation.
This Python adapter is a local-dashboard STATUS reader, not a raw data importer.
"""
from __future__ import annotations
from collections import Counter
import json
from pathlib import Path

PROJECT = Path(__file__).resolve().parents[2]
DEFAULT = PROJECT / 'examples' / 'political_universe_fixture.json'


def local_actor_universe_status(path: Path | None = None) -> dict:
    p = DEFAULT if path is None else Path(path)
    blocked = {'status': 'NOT_AVAILABLE', 'real_people_scoring': False,
               'field_actors_verified': 0, 'mode': 'READ_ONLY_SYNTHETIC_LAB'}
    if not p.is_file():
        return {**blocked, 'reason': 'NO_FIXTURE_FILE'}
    try:
        data = json.loads(p.read_text(encoding='utf-8'))
        if not isinstance(data, dict) or data.get('dataset_class') != 'FIXTURE':
            return {**blocked, 'reason': 'NOT_SYNTHETIC_DATA'}
        sources = data.get('sources')
        actors = data.get('actors')
        events = data.get('events')
        if (not isinstance(sources, list) or not isinstance(actors, list)
                or not isinstance(events, list)
                or any(not isinstance(v, dict) for v in sources + actors + events)
                or any(v.get('kind') != 'FIXTURE' or v.get('state') != 'FIXTURE'
                       for v in sources)):
            return {**blocked, 'reason': 'BAD_FIXTURE_SCHEMA'}
        kinds = Counter(a.get('kind', 'UNKNOWN') for a in actors)
        return {
            'status': 'SYNTHETIC_ONLY',
            'mode': 'READ_ONLY_SYNTHETIC_LAB',
            'real_people_scoring': False,
            'field_actors_verified': 0,
            'sources': len(sources),
            'total_actors': len(actors),
            'actors_by_kind': dict(sorted(kinds.items())),
            'documented_events_in_fixture': len(events),
            'warning': 'Entirely fictitious records. Does not measure Spanish political participation.'
        }
    except (ValueError, UnicodeError, OSError):
        return {**blocked, 'reason': 'INVALID_OR_UNREADABLE_FILE'}
