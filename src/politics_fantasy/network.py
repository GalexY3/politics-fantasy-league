"""Descriptive temporal roll-call co-voting graph; NO inferred ideology or causality."""
from __future__ import annotations
from collections import defaultdict
from dataclasses import dataclass
from datetime import datetime
from itertools import combinations
from math import isfinite
from .events import as_utc

ALLOWED={'YES','NO','ABSTAIN'}

@dataclass(frozen=True)
class VoteRecord:
    vote_event_id: str
    person_id: str
    choice: str
    occurred_at: datetime
    first_public_at: datetime


def covote_edges(votes: list[VoteRecord], *, as_of: datetime, min_joint: int = 3,
                 alpha: float = 1.0, beta: float = 1.0) -> list[dict]:
    """Beta-smoothed descriptive agreement, identical exposure event per pair.

    Baseline agreement may be high for almost every pair due to party discipline;
    a high edge score never proves personal collaboration or influence.
    """
    as_of=as_utc(as_of)
    if (type(min_joint) is not int or min_joint < 1
            or type(alpha) not in (int, float) or not isfinite(alpha) or alpha <= 0
            or type(beta) not in (int, float) or not isfinite(beta) or beta <= 0):
        raise ValueError('Invalid regularization')
    by_vote=defaultdict(dict)
    for vote in votes:
        if as_utc(vote.occurred_at)>as_of or as_utc(vote.first_public_at)>as_of:
            continue
        if vote.choice not in ALLOWED:
            continue
        if (not isinstance(vote.vote_event_id, str) or not vote.vote_event_id.strip()
                or not isinstance(vote.person_id, str) or not vote.person_id.strip()):
            raise ValueError('INVALID_VOTE_OR_PERSON_ID')
        v=by_vote[vote.vote_event_id]
        if vote.person_id in v and v[vote.person_id]!=vote.choice:
            raise ValueError('Conflicting vote choice for same person/event')
        v[vote.person_id]=vote.choice
    joint=defaultdict(lambda:[0,0])
    for v in by_vote.values():
        for left,right in combinations(sorted(v),2):
            joint[(left,right)][0]+=1
            joint[(left,right)][1]+=int(v[left]==v[right])
    return [{'left':left,'right':right,'joint_votes':n,'agreements':same,
             'agreement_smoothed':(same+alpha)/(n+alpha+beta),
             'status':'DESCRIPTIVE_NOT_CAUSAL'}
            for (left,right),(n,same) in sorted(joint.items()) if n>=min_joint]
