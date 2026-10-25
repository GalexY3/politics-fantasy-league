"""Research-grade primitives for SYNTHETIC nominal-vote fixtures.

Never silently interpret missing entries as NO_VOTE. A historical snapshot requires
both publication and LOCAL observation before the as-of; original upstream revision
history/affiliation-at-time require independent certification before empirical use.
"""
from __future__ import annotations
from collections import defaultdict, Counter
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable
from urllib.parse import urlsplit
from .events import as_utc

CHOICES=frozenset({'YES','NO','ABSTAIN','NO_VOTE'})
EXPRESSED=frozenset({'YES','NO','ABSTAIN'})


@dataclass(frozen=True)
class NominalVote:
    vote_id: str
    person_id: str
    group_at_vote: str
    choice: str
    occurred_at: datetime
    first_public_at: datetime
    recorded_at: datetime
    source_url: str
    source_sha256: str
    revision: int = 1

    def __post_init__(self):
        if not all(isinstance(x,str) and x.strip() for x in (self.vote_id,self.person_id,self.group_at_vote)):
            raise ValueError('Missing vote, person, or historical group')
        if self.choice not in CHOICES:raise ValueError('Unknown vote choice')
        if not isinstance(self.revision,int) or isinstance(self.revision,bool) or self.revision<1:
            raise ValueError('Invalid source revision')
        if urlsplit(self.source_url).scheme!='https' or not urlsplit(self.source_url).netloc:
            raise ValueError('HTTPS source URL required')
        if len(self.source_sha256)!=64 or any(c not in '0123456789abcdef' for c in self.source_sha256):
            raise ValueError('Invalid source SHA256')
        if as_utc(self.first_public_at)<as_utc(self.occurred_at):
            raise ValueError('Published before occurred (schedule should use another type)')
        if as_utc(self.recorded_at)<as_utc(self.first_public_at):
            raise ValueError('Local record cannot predate stated original publication')


def rollcall_as_of(votes: Iterable[NominalVote], as_of: datetime) -> list[NominalVote]:
    """One latest *recorded and published* revision per (vote_id, person_id).

    Input archives must contain revisions, not just today's state. Conflicting
    same revisions fail rather than choosing an arbitrary winner.
    """
    at=as_utc(as_of)
    revisions={}
    for v in votes:
        if min(as_utc(v.first_public_at),as_utc(v.recorded_at))>at:
            continue
        if as_utc(v.occurred_at)>at or as_utc(v.first_public_at)>at or as_utc(v.recorded_at)>at:
            continue
        key=(v.vote_id,v.person_id,v.revision)
        if key in revisions and revisions[key]!=v:
            raise ValueError('Conflicting nominal-vote revision')
        revisions[key]=v
    result={}
    for v in revisions.values():
        key=(v.vote_id,v.person_id)
        old=result.get(key)
        if old is None or v.revision>old.revision:
            result[key]=v
        elif v.revision==old.revision and v!=old:
            raise ValueError('Ambiguous nominal vote')
    return sorted(result.values(),key=lambda v:(v.vote_id,v.person_id))


def _group_votations(votes: Iterable[NominalVote]):
    grouped=defaultdict(list)
    for v in votes:grouped[v.vote_id].append(v)
    return grouped
