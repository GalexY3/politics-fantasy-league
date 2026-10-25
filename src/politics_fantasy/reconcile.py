"""Conservation and coverage audit between vote-level and nominal CSV tables.

A match checks *consistency* of provided bytes; it does not certify the source
or guarantee that secret/roll-call votes, absent deputies or filtered rows exist.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from .field_ingest import Parsed, IndividualRow, AggregateRow

CATEGORIES = ('YES', 'NO', 'ABSTAIN', 'NO_VOTE')


def reconcile(individual: Parsed, aggregate: Parsed) -> dict:
    if individual.data_kind!='individual' or aggregate.data_kind!='aggregate':
        raise ValueError('Expected individual and aggregate snapshots')
    nominal=defaultdict(Counter)
    dates={}
    for r in individual.rows:
        nominal[r.vote_id][r.choice]+=1
        if r.vote_id in dates and dates[r.vote_id]!=r.day:
            raise ValueError('Conflicting individual vote dates')
        dates[r.vote_id]=r.day
    totals={r.vote_id:r for r in aggregate.rows}
    checks=[]
    for vote_id in sorted(set(totals)|set(nominal)):
        a=totals.get(vote_id);n=nominal.get(vote_id)
        expected=({'YES':a.yes,'NO':a.no,'ABSTAIN':a.abstain,'NO_VOTE':a.no_vote} if a else None)
        got={k:n[k] if n else 0 for k in CATEGORIES}
        if not a:status='NOMINAL_ONLY_MISSING_AGGREGATE'
        elif not n:status='AGGREGATE_ONLY_MISSING_NOMINAL'
        elif a.day!=dates[vote_id]:status='DATE_CONFLICT'
        elif got==expected:status='COUNTS_MATCH_NOT_CERTIFIED'
        elif any(got[k]>expected[k] for k in CATEGORIES):status='NOMINAL_EXCEEDS_AGGREGATE_CONFLICT'
        else:status='PARTIAL_NOMINAL_OR_FILTERED'
        checks.append({'vote_id':vote_id,'status':status,'observed':got,'published_total':expected,
                       'observed_count':sum(got.values()),
                       'total_count':sum(expected.values()) if expected is not None else None})
    summary=dict(sorted(Counter(x['status'] for x in checks).items()))
    return {'status':'SOURCE_CONSISTENCY_ONLY_NOT_VALIDATION',
            'tables':{'individual_sha256':individual.provenance.sha256,
                      'aggregate_sha256':aggregate.provenance.sha256},
            'votes':checks,'summary':summary,'any_unresolved':any(x['status']!='COUNTS_MATCH_NOT_CERTIFIED' for x in checks),
            'attribution_required':True}


def group_snapshot(individual: Parsed) -> dict:
    if individual.data_kind!='individual':raise ValueError('Nominal source required')
    tally=defaultdict(Counter)
    for r in individual.rows:
        tally[r.group_label][r.choice]+=1
    # There is no population census here; a missing row MUST NOT be classified as no-vote.
    return {k:{**{name:tally[k][name] for name in CATEGORIES}, 'coverage':'OBSERVED_ROWS_ONLY',
               'group_history':'LABEL_AS_REPORTED_UNVERIFIED'} for k in sorted(tally)}


def snapshot_difference(old: Parsed, new: Parsed) -> dict:
    """Compare released snapshots without treating new/revised rows as historical fact."""
    if old.data_kind!=new.data_kind:raise ValueError('Same table type required')
    def indexed(p):
        return {(r.vote_id, r.deputy_id) if isinstance(r,IndividualRow) else r.vote_id:r for r in p.rows}
    old_rows=indexed(old);new_rows=indexed(new)
    keys=set(old_rows)&set(new_rows)
    changes=[k for k in keys if old_rows[k]!=new_rows[k]]
    # Ignore source_line: additions above a row cannot make a scientific revision.
    if old.data_kind=='individual':
        changes=[k for k in keys if (old_rows[k].day,old_rows[k].group_label,old_rows[k].choice,
                                     old_rows[k].topic_label)!=(new_rows[k].day,new_rows[k].group_label,
                                                               new_rows[k].choice,new_rows[k].topic_label)]
    else:
        changes=[k for k in keys if (old_rows[k].day,old_rows[k].yes,old_rows[k].no,
                                     old_rows[k].abstain,old_rows[k].no_vote)!=(new_rows[k].day,
                                         new_rows[k].yes,new_rows[k].no,new_rows[k].abstain,new_rows[k].no_vote)]
    return {'added':len(new_rows.keys()-old_rows.keys()),
            'removed':len(old_rows.keys()-new_rows.keys()),
            'modified':len(changes),
            'status':'SNAPSHOT_CHANGE_NOT_ORIGINAL_PUBLICATION_HISTORY'}
