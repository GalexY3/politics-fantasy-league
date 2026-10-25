"""Trust gates: source availability != event date, consistency != coverage.

Tooling supports a future field corpus, but cannot independently attest
publisher identity, historical group labels or coverage without provenance.
"""
from __future__ import annotations
from collections import Counter
from datetime import date, datetime, timezone
from math import isfinite
from typing import Iterable
from .field_ingest import Parsed, IndividualRow, AggregateRow
from .reconcile import reconcile


def _utc(when: datetime) -> datetime:
    if when.tzinfo is None or when.utcoffset() is None:
        raise ValueError('Naive datetime cannot be a bitemporal cutoff')
    return when.astimezone(timezone.utc)


def as_of_import(parsed: Parsed, when: datetime) -> Parsed | None:
    """Snapshot-level availability, NEVER retrospectively assign 2026 source to 2023."""
    observed=datetime.fromisoformat(parsed.provenance.acquired_at)
    return parsed if _utc(observed)<=_utc(when) else None


def quality_gates(individual: Parsed, aggregate: Parsed, *, chamber_capacity: int | None=350) -> dict:
    comparison=reconcile(individual,aggregate)
    exceeding=[]
    for row in aggregate.rows:
        n=row.yes+row.no+row.abstain+row.no_vote
        if chamber_capacity is not None and n>chamber_capacity:
            exceeding.append(row.vote_id)
    date_in_future=[]
    for p in (individual,aggregate):
        imported=_utc(datetime.fromisoformat(p.provenance.acquired_at)).date()
        date_in_future.extend(row.vote_id for row in p.rows if row.day>imported)
    samples=Counter(row.choice for row in individual.rows)
    return {'consistency':comparison['summary'], 'nominal_exceeds_seats':sorted(set(exceeding)),
            'event_dated_after_import':sorted(set(date_in_future)),
            'nominal_decisions':{choice:samples[choice] for choice in ('YES','NO','ABSTAIN','NO_VOTE')},
            'passes_consistency':not comparison['any_unresolved'],
            'allows_historical_membership_assertion':False,
            'allows_missing_row_as_absence':False,
            'source_certified':False,
            'passes_field_inference':False,
            'status':'STRUCTURAL_CHECKS_ONLY_NOT_INDEPENDENT_SOURCE_VERIFICATION'}


def coverage_gate(gates: dict, *, roster_verified: bool, original_publication_verified: bool,
                  license_reviewed: bool) -> dict:
    """An explicit conservative gate; no boolean proves real-world verification."""
    blockers=[]
    if not gates['passes_consistency']:blockers.append('COUNTS_NOT_RECONCILED')
    if gates['nominal_exceeds_seats']:blockers.append('CHAMBER_CAPACITY_FLAG')
    if gates['event_dated_after_import']:blockers.append('FUTURE_EVENT_DATE')
    if not roster_verified:blockers.append('ROSTER_NOT_VERIFIED')
    if not original_publication_verified:blockers.append('HISTORICAL_PUBLICATION_NOT_VERIFIED')
    if not license_reviewed:blockers.append('LICENSE_NOT_REVIEWED')
    # No API in this software can independently certify an upstream dataset.
    blockers.append('EXTERNAL_SOURCE_ATTESTATION_REQUIRED')
    return {'candidate_valid_for_manual_review':not blockers[:-1],
            'automated_source_certified':False,
            'inference_ready':False,
            'blockers':blockers}


def cluster_inventory(individual: Parsed) -> dict:
    """Count sessions by vote ID, not 'independent' nominal MPs or weeks."""
    if individual.data_kind!='individual':raise ValueError('Nominal required')
    per_vote={r.vote_id for r in individual.rows}
    sessions={v.split('-v')[0] for v in per_vote}
    days={r.day for r in individual.rows}
    return {'nominal_rows':len(individual.rows),'votes':len(per_vote),
            'sessions':len(sessions),'calendar_days':len(days),
            'inference_unit':'SESSIONS_NOT_NOMINAL_ROWS'}


def topic_provenance(individual: Parsed) -> dict:
    """A title-keyword topic label is not an official subject classification."""
    if individual.data_kind!='individual':raise ValueError('Nominal required')
    topics=Counter(r.topic_label or '__MISSING__' for r in individual.rows)
    return {'source':'THIRD_PARTY_TITLE_KEYWORDS',
            'is_institutional_classification':False,'n_labels':len(topics),
            'missing_topic_rows':topics['__MISSING__'],
            'warning':'Keywords and agenda selection must be validated before inference'}
