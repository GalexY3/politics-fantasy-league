"""Conservative sociological identifiability and missingness diagnostics.

Algebraic bounds are conditional on *independently supplied*, verified roster size;
this module cannot certify that roster, provenance, or historical availability.
"""
from __future__ import annotations
from collections import defaultdict
from datetime import datetime, timezone
from .field_ingest import Parsed,IndividualRow


def research_readiness(report:dict)->dict:
    """An internal receipt never certifies the original political data."""
    reconciliation=report.get('reconciliation',{})
    group=report.get('group_audit')
    gaps=['OFFICIAL_SOURCE_NOT_INDEPENDENTLY_ATTESTED',
          'HISTORICAL_ROSTER_UNVERIFIED',
          'ORIGINAL_PUBLICATION_TIMES_UNVERIFIED',
          'COMPETENT_FIELD_BASELINE_NOT_EVALUATED']
    if reconciliation.get('any_unresolved') is not False:
        gaps.append('NOMINAL_AGGREGATE_DISCREPANCY')
    if group is None:
        gaps.append('GROUP_TABLE_ABSENT')
    elif group.get('aggregate_consistent') is not True or group.get('nominal_group_complete') is not True:
        gaps.append('GROUP_RECONCILIATION_DISCREPANCY')
    return {'status':'NOT_READY_FOR_EMPIRICAL_CLAIMS',
            'discriminating_blockers':gaps,
            'VSDS_upper_bound_without_new_field_validation':1,
            'scientific_claim':'NOT_EVALUABLE_FROM_SNAPSHOTS_ALONE'}


def observed_label_transitions(individual:Parsed)->dict:
    if individual.data_kind!='individual':raise ValueError('Expected nominal observations')
    labels=defaultdict(lambda:defaultdict(set))
    for row in individual.rows:
        assert isinstance(row,IndividualRow)
        labels[row.deputy_id][row.day].add(row.group_label)
    same_day_conflicts=sum(len(group)>1 for days in labels.values() for group in days.values())
    changed_between_days=0
    for days in labels.values():
        series=[next(iter(groups)) for _,groups in sorted(days.items()) if len(groups)==1]
        if len(set(series))>1:changed_between_days+=1
    return {'deputy_ids_with_different_reported_group_over_time':changed_between_days,
            'same_day_group_conflicts':same_day_conflicts,
            'interpretation':'OBSERVED_LABEL_DIFFERENCE_NOT_CAUSAL_PARTY_DEFECTION',
            'historical_roster_certified':False}


def as_of_snapshot_gate(report:dict, as_of:datetime)->dict:
    if as_of.tzinfo is None or as_of.utcoffset() is None:raise ValueError('As-of cutoff must be timezone aware')
    snapshots=report.get('source_snapshots',{})
    acquired=[]
    for x in snapshots.values():
        instant=datetime.fromisoformat(x['observed_at'])
        if instant.tzinfo is None:raise ValueError('Source acquisition must be timezone aware')
        acquired.append(instant.astimezone(timezone.utc))
    if not acquired:raise ValueError('Source snapshots missing')
    if any(t>as_of.astimezone(timezone.utc) for t in acquired):
        return {'eligible_for_historical_prediction':False,'reason':'SNAPSHOT_ACQUIRED_AFTER_PREDICTION_CUTOFF'}
    return {'eligible_for_historical_prediction':False,'reason':'ORIGINAL_PUBLICATION_UNVERIFIED_EVEN_WHEN_ACQUIRED_EARLY',
            'usable_for_descriptive_audit_as_of':True}


def yes_share_bounds(*,yes:int,observed:int,eligible_roster:int|None)->dict:
    if any(type(x) is not int or x<0 for x in (yes,observed)) or yes>observed:
        raise ValueError('Invalid observed counts')
    if eligible_roster is None:
        return {'lower':None,'upper':None,'unknown_count':None,
                'reason':'INDEPENDENT_HISTORICAL_ROSTER_REQUIRED'}
    if type(eligible_roster) is not int or eligible_roster<1 or observed>eligible_roster:
        raise ValueError('Roster must be positive and >= observed rows')
    unknown=eligible_roster-observed
    return {'lower':yes/eligible_roster,'upper':(yes+unknown)/eligible_roster,
            'unknown_count':unknown,'reason':'ALGEBRAIC_BOUNDS_CONDITIONAL_ON_VALIDATED_ROSTER'}
