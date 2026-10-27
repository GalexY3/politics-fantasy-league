"""Streaming data-quality audit for NORMALIZED EVENTS (not an official-source parser).

Data are in JSON Lines to make the audit memory-bounded for large files.
Never infer political activity from undocumented missing records.
"""
from __future__ import annotations
from collections import Counter
from datetime import datetime
import json
import re
from pathlib import Path
from .events import as_utc

REQUIRED = ('event_id','source_id','event_kind','occurred_at','first_public_at',
            'source_url','raw_sha256','person_ids')


def audit_jsonl(path: Path, *, max_unique_ids: int = 5_000_000) -> dict:
    """Audit normalized JSONL. Memory O(unique ids) for duplicate detection.

    For bigger corpora use SQL/DuckDB external sort by (source,event_id,version).
    The result is descriptive only; data coverage needs an independent census.
    """
    counters = Counter()
    seen = set()
    min_date = max_date = None
    with path.open(encoding='utf-8') as f:
        for line_no, text in enumerate(f, 1):
            if not text.strip():
                continue
            counters['rows'] += 1
            try:
                row = json.loads(text)
                if not isinstance(row, dict):
                    raise ValueError('Row is not an object')
            except (json.JSONDecodeError, ValueError):
                counters['bad_json_or_type'] += 1
                continue
            missing = [k for k in REQUIRED if k not in row or row[k] is None]
            if missing:
                counters['missing_required'] += 1
                for key in missing: counters[f'missing_{key}'] += 1
                continue
            people = row['person_ids']
            digest = row['raw_sha256']
            if (not isinstance(people, list)
                    or any(not isinstance(person, str) or not person for person in people)
                    or len(set(people)) != len(people)
                    or not isinstance(digest, str)
                    or re.fullmatch(r'[0-9a-f]{64}', digest) is None):
                counters['bad_identity_or_hash'] += 1
                continue
            try:
                occurred, public = as_utc(row['occurred_at']), as_utc(row['first_public_at'])
            except (TypeError, ValueError):
                counters['bad_datetime'] += 1
                continue
            if public < occurred and not str(row['event_kind']).startswith('scheduled_'):
                counters['future_date_inconsistency'] += 1
            key = (row['source_id'], str(row['event_id']), str(row.get('source_revision', '?')))
            if key in seen:
                counters['duplicate_same_revision'] += 1
            elif len(seen) >= max_unique_ids:
                raise MemoryError('Too many IDs for in-memory audit; use external sort')
            seen.add(key)
            counters['parseable'] += 1
            day = occurred.date().isoformat()
            min_date = day if min_date is None else min(day, min_date)
            max_date = day if max_date is None else max(day, max_date)
            if len(row['person_ids']) == 0:
                counters['unattributed_events'] += 1
    return {'counts':dict(sorted(counters.items())),
            'minimum_event_day':min_date, 'maximum_event_day':max_date,
            'audit_method':'SCHEMA_VALIDITY_ONLY',
            'coverage_status':'NOT_INFERABLE_WITHOUT_SOURCE_CENSUS'}
