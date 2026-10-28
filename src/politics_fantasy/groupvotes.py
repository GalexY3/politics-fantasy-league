"""Third-party historical group vote CSV reconciliation; not source certification.

Do not treat groups as static memberships and do not infer missing nominal entries.
CSV is a snapshot; acquisition time is not original publication time.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
import csv
import hashlib
import io

from .field_ingest import (Provenance, Parsed, IndividualRow, AggregateRow,
                           SOURCE_PAGE, MAX_CSV_BYTES, _id, _count, _day)

REQUIRED = frozenset(('votacion_id','fecha','grupo','si','no','abstencion','no_vota'))
CATEGORIES = ('YES','NO','ABSTAIN','NO_VOTE')

@dataclass(frozen=True)
class GroupRow:
    vote_id: str
    day: date
    group: str
    yes: int
    no: int
    abstain: int
    no_vote: int
    source_line: int

    def counts(self) -> dict[str, int]:
        return {'YES':self.yes,'NO':self.no,'ABSTAIN':self.abstain,'NO_VOTE':self.no_vote}

@dataclass(frozen=True)
class GroupSnapshot:
    provenance: Provenance
    rows: tuple[GroupRow, ...]
    certified: bool = False


def read_group_snapshot(path: Path, *, acquired_at:datetime, max_rows:int=100_000)->GroupSnapshot:
    if acquired_at.tzinfo is None or acquired_at.utcoffset() is None:
        raise ValueError('Acquisition timestamp must be offset-aware')
    if isinstance(max_rows,bool) or not isinstance(max_rows,int) or max_rows<1:
        raise ValueError('Invalid row budget')
    with Path(path).open('rb') as handle:
        data=handle.read(MAX_CSV_BYTES+1)
    if len(data)>MAX_CSV_BYTES:
        raise ValueError('Input too large')
    try:
        source=data.decode('utf-8-sig')
    except UnicodeError as e:
        raise ValueError('Expected UTF-8') from e
    if '\x00' in source:raise ValueError('NUL forbidden')
    reader=csv.DictReader(io.StringIO(source,newline=''),restkey='__extra__')
    if not reader.fieldnames or len(set(reader.fieldnames))!=len(reader.fieldnames) or not REQUIRED.issubset(reader.fieldnames):
        raise ValueError('Required group CSV header missing or duplicated')
    seen=set();result=[]
    for index,raw in enumerate(reader,2):
        if len(result)>=max_rows:raise ValueError('Group row budget exceeded')
        if '__extra__' in raw or any(v is None for v in raw.values()):raise ValueError('Malformed group CSV row')
        try:
            vote=_id(raw['votacion_id']);day=_day(raw['fecha']);group=raw['grupo'].strip()
            if not group or len(group)>128 or any(ord(ch)<32 for ch in group):raise ValueError('Invalid group label')
            nums=tuple(_count(raw[k]) for k in ('si','no','abstencion','no_vota'))
            if sum(nums)>350:raise ValueError('Group tally exceeds chamber capacity')
        except ValueError as e:
            raise ValueError(f'Invalid group CSV at line {index}: {e}') from e
        key=(vote,group)
        if key in seen:raise ValueError(f'Duplicate group vote at line {index}')
        seen.add(key);result.append(GroupRow(vote,day,group,*nums,index))
    if not result:raise ValueError('Group CSV has no observations')
    return GroupSnapshot(Provenance(SOURCE_PAGE,hashlib.sha256(data).hexdigest(),len(data),
                                   acquired_at.astimezone(timezone.utc).isoformat()),tuple(result))


def majority(r:GroupRow)->str:
    """Historical compatibility: *modal* expressed option, not >50% majority.

    Do not interpret this as an absolute majority or full group membership.
    Prefer strict_majority(..., denominator=...) for explicit denominators.
    """
    expressed={'YES':r.yes,'NO':r.no,'ABSTAIN':r.abstain}
    peak=max(expressed.values())
    if not peak:return 'NO_EXPRESSED_CHOICE'
    leaders=[k for k,v in expressed.items() if v==peak]
    return leaders[0] if len(leaders)==1 else 'TIE'


def strict_majority(r:GroupRow, *, denominator:str='EXPRESSED_ONLY')->str:
    """More than half of explicitly recorded options; not membership proof.

    EXPRESSED_ONLY includes YES, NO, ABSTAIN. ALL_RECORDED_STATUSES also
    includes explicit NO_VOTE. Neither denominator establishes how many
    group members were eligible, present or absent at the vote.
    """
    if denominator not in ('EXPRESSED_ONLY', 'ALL_RECORDED_STATUSES'):
        raise ValueError('UNKNOWN_GROUP_DENOMINATOR')
    expressed={'YES':r.yes,'NO':r.no,'ABSTAIN':r.abstain}
    if not any(expressed.values()):
        return 'NO_EXPRESSED_CHOICE'
    total=sum(expressed.values())
    if denominator=='ALL_RECORDED_STATUSES':
        total+=r.no_vote
    peak=max(expressed.values())
    leaders=[kind for kind,value in expressed.items() if value==peak]
    if len(leaders)!=1:
        return 'TIE'
    return leaders[0] if peak*2>total else 'NO_ABSOLUTE_MAJORITY'


def reconcile_groups(groups:GroupSnapshot, aggregates:Parsed, individuals:Parsed|None=None)->dict:
    if aggregates.data_kind!='aggregate' or (individuals is not None and individuals.data_kind!='individual'):
        raise ValueError('Wrong snapshot kinds')
    by_vote=defaultdict(Counter); by_group={}
    groups_by_vote=defaultdict(list)
    for r in groups.rows:
        groups_by_vote[r.vote_id].append(r)
        for k,v in r.counts().items():by_vote[r.vote_id][k]+=v
        by_group[(r.vote_id,r.group)]=r
    conflicting_dates=sum(len({row.day for row in rows})>1 for rows in groups_by_vote.values())
    totals={r.vote_id:r for r in aggregates.rows}
    checks=[]
    for vid in sorted(set(by_vote)|set(totals)):
        agg=totals.get(vid)
        vote_groups=groups_by_vote.get(vid,[])
        dates_match=bool(agg and all(r.day==agg.day for r in vote_groups))
        source={k:by_vote[vid][k] for k in CATEGORIES}
        target=({'YES':agg.yes,'NO':agg.no,'ABSTAIN':agg.abstain,'NO_VOTE':agg.no_vote} if agg else None)
        if len({row.day for row in vote_groups})>1:status='GROUP_INTERNAL_DATE_CONFLICT'
        elif not agg:status='GROUP_ONLY_NO_AGGREGATE'
        elif not vote_groups:status='AGGREGATE_ONLY_NO_GROUPS'
        elif not dates_match:status='GROUP_DATE_CONFLICT'
        elif source==target:status='GROUP_TOTALS_MATCH_UNCERTIFIED'
        elif any(source[k]>target[k] for k in CATEGORIES):status='GROUP_EXCEEDS_AGGREGATE'
        else:status='GROUP_PARTIAL_OR_FILTERED'
        checks.append({'vote_id':vid,'status':status,'group_rows':len(vote_groups)})
    individual_mismatches=0;individual_undercounts=0;unmatched_individuals=0
    if individuals is not None:
        nominal=defaultdict(Counter)
        for row in individuals.rows:
            assert isinstance(row,IndividualRow)
            gr=by_group.get((row.vote_id,row.group_label))
            if gr is None:unmatched_individuals+=1
            nominal[row.vote_id,row.group_label][row.choice]+=1
        for key,gr in by_group.items():
            observed=nominal.get(key,Counter())
            if any(observed[k]>gr.counts()[k] for k in CATEGORIES):
                individual_mismatches+=1
            if any(observed[k]<gr.counts()[k] for k in CATEGORIES):
                individual_undercounts+=1
    return {'status':'THIRD_PARTY_SNAPSHOT_RECONCILIATION_NOT_CERTIFICATION',
            'summary':dict(sorted(Counter(x['status'] for x in checks).items())),
            'votes_checked':len(checks),
            'aggregate_consistent':bool(checks) and all(x['status']=='GROUP_TOTALS_MATCH_UNCERTIFIED' for x in checks),
            'nominal_group_overages':individual_mismatches,
            'nominal_group_undercounts':individual_undercounts if individuals is not None else None,
            'nominal_group_complete':(not individual_mismatches and not individual_undercounts and not unmatched_individuals) if individuals is not None else None,
            'group_votes_with_conflicting_dates':conflicting_dates,
            'nominal_unmatched_group_rows':unmatched_individuals,
            'groups_sha256':groups.provenance.sha256}


def group_release_difference(old:GroupSnapshot,new:GroupSnapshot)->dict:
    """Revision of *snapshots*, not a reconstruction of historical publication."""
    before={(r.vote_id,r.group):r for r in old.rows}
    after={(r.vote_id,r.group):r for r in new.rows}
    same=before.keys()&after.keys()
    changed=sum((before[k].day,before[k].yes,before[k].no,before[k].abstain,before[k].no_vote)!=
                (after[k].day,after[k].yes,after[k].no,after[k].abstain,after[k].no_vote) for k in same)
    return {'added':len(after.keys()-before.keys()),'removed':len(before.keys()-after.keys()),
            'modified':changed,'old_sha256':old.provenance.sha256,'new_sha256':new.provenance.sha256,
            'old_observed_at':old.provenance.acquired_at,'new_observed_at':new.provenance.acquired_at,
            'meaning':'SNAPSHOT_DIFFERENCE_NOT_FIRST_PUBLICATION'}
