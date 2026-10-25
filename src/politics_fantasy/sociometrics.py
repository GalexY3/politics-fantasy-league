"""Sociological indicators with denominators and missingness made explicit.

Tests and example inputs are synthetic. This is NOT an estimate of real groups.
"""
from __future__ import annotations
from collections import Counter, defaultdict
from dataclasses import dataclass
from typing import Iterable, Mapping
from .rollcall import NominalVote, EXPRESSED

@dataclass(frozen=True)
class Participation:
    person_id: str
    eligible: int
    expressed: int
    no_vote: int
    unknown: int
    rate: float | None
    status: str


def participation(votes: Iterable[NominalVote], *, person_id: str, eligible_vote_ids: Iterable[str]) -> Participation:
    """Only compute complete-census participation; omitted row=UNKNOWN, not NO_VOTE."""
    eligible=list(eligible_vote_ids)
    if len(eligible)!=len(set(eligible)):raise ValueError('Duplicated census opportunities')
    if not eligible: return Participation(person_id,0,0,0,0,None,'NO_EXPOSURE')
    records={}
    for v in votes:
        if v.person_id!=person_id:continue
        if v.vote_id not in eligible:raise ValueError('Observed vote not in supplied eligible census')
        if v.vote_id in records:raise ValueError('Duplicate snapshot row; resolve revisions first')
        records[v.vote_id]=v.choice
    expressed=sum(x in EXPRESSED for x in records.values())
    no_vote=sum(x=='NO_VOTE' for x in records.values())
    unknown=len(eligible)-len(records)
    return Participation(person_id,len(eligible),expressed,no_vote,unknown,
                         expressed/len(eligible) if unknown==0 else None,
                         'CENSUS_COMPLETE_SYNTHETIC' if unknown==0 else 'INCOMPLETE_CENSUS')


def group_choice_counts(votes: Iterable[NominalVote]) -> dict[str,dict[str,int]]:
    """Describes recorded group-at-vote rows, not a census of all parliamentarians."""
    out=defaultdict(Counter)
    seen=set()
    for v in votes:
        if (v.vote_id,v.person_id) in seen:raise ValueError('Unresolved duplicate nominal row')
        seen.add((v.vote_id,v.person_id))
        out[v.group_at_vote][v.choice]+=1
    return {g:dict(sorted(c.items())) for g,c in sorted(out.items())}


def majority_by_group_vote(votes: Iterable[NominalVote]) -> dict[tuple[str,str],str | None]:
    """One per-session vote/group majority; tie or 0 expressed votes returns None."""
    tally=defaultdict(Counter)
    seen=set()
    for v in votes:
        key=(v.vote_id,v.person_id)
        if key in seen:raise ValueError('Unresolved duplicate')
        seen.add(key)
        if v.choice in EXPRESSED:
            tally[(v.vote_id,v.group_at_vote)][v.choice]+=1
        else:
            tally[(v.vote_id,v.group_at_vote)] += Counter()
    groups=set((v.vote_id,v.group_at_vote) for v in votes)
    out={}
    for key in groups:
        counts=tally[key]
        most=max(counts.values(),default=0)
        winners=[c for c,n in counts.items() if n==most]
        out[key]=winners[0] if most>0 and len(winners)==1 else None
    return out


def dissent_report(votes: Iterable[NominalVote], *, exclude_groups: frozenset[str]=frozenset({'Mixto'})) -> dict[str,dict]:
    """Exclude abstention? NO: expressed ABSTAIN is a legitimate preference.

    Denominator is expressed votes with UNAMBIGUOUS group majority; no_vote,
    ties and heterogeneous groups are ineligible. Never label motive/ideology.
    """
    rows=list(votes)
    maj=majority_by_group_vote(rows)
    result=defaultdict(lambda:{'eligible_expressed':0,'dissent':0,'excluded':0})
    for v in rows:
        x=result[v.person_id]
        winner=maj[(v.vote_id,v.group_at_vote)]
        if v.choice not in EXPRESSED or v.group_at_vote in exclude_groups or winner is None:
            x['excluded']+=1
            continue
        x['eligible_expressed']+=1
        x['dissent']+=int(v.choice!=winner)
    return {k:{**v,'rate':v['dissent']/v['eligible_expressed'] if v['eligible_expressed'] else None,
               'status':'DESCRIPTIVE_SYNTHETIC_NOT_MOTIVATION'} for k,v in sorted(result.items())}
