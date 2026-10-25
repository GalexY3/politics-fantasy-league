"""Explicit-denominator synthetic sociology experiments; no ideology inference."""
from __future__ import annotations
from collections import Counter, defaultdict
from itertools import combinations
from math import log, isfinite
from typing import Iterable, Mapping
from .rollcall import NominalVote, EXPRESSED


def majority_margin(votes: Iterable[NominalVote], *, vote_id: str, group_id: str) -> float | None:
    """Top minus runner-up expressed votes, divided by expressed n; 0 is a tie."""
    counts=Counter(v.choice for v in votes if v.vote_id==vote_id and v.group_at_vote==group_id and v.choice in EXPRESSED)
    n=sum(counts.values())
    if n==0:return None
    ranked=sorted(counts.values(),reverse=True)+[0]
    return (ranked[0]-ranked[1])/n


def expressed_diversity(choices: Iterable[str]) -> float | None:
    """Normalized Shannon entropy in 3 expressed categories, no_vote excluded."""
    seq=list(choices)
    if any(c not in EXPRESSED|{'NO_VOTE'} for c in seq):raise ValueError('Unknown choice')
    counts=Counter(c for c in seq if c in EXPRESSED)
    n=sum(counts.values())
    if not n:return None
    return -sum((x/n)*log(x/n) for x in counts.values())/log(3)


def direct_standardization(strata: Mapping[str,tuple[int,int]], weights: Mapping[str,float]) -> float:
    """Apply common, EXTERNALLY specified distribution to within-stratum rates.

    No imputation for absent strata and no rates with denominator 0.
    """
    if not weights or set(weights)!=set(strata) or any(not isfinite(w) or w<0 for w in weights.values()) or abs(sum(weights.values())-1)>1e-10:
        raise ValueError('All common strata must be specified with normalized weights')
    ans=0.0
    for k,w in weights.items():
        y,n=strata[k]
        if not isinstance(y,int) or not isinstance(n,int) or n<=0 or not 0<=y<=n:
            raise ValueError('Invalid stratum count')
        ans+=w*(y/n)
    return ans


def simpson_reversal(a: Mapping[str,tuple[int,int]], b: Mapping[str,tuple[int,int]]) -> dict:
    """Flag reversal between two groups. Descriptive arithmetic, NOT confounding diagnosis."""
    if not a or set(a)!=set(b):raise ValueError('Common strata required')
    ra={k:direct_standardization({k:v},{k:1.0}) for k,v in a.items()}
    rb={k:direct_standardization({k:v},{k:1.0}) for k,v in b.items()}
    na=sum(n for _,n in a.values());nb=sum(n for _,n in b.values())
    pooled_a=sum(y for y,_ in a.values())/na
    pooled_b=sum(y for y,_ in b.values())/nb
    diffs=[ra[k]-rb[k] for k in a]
    sign_all=1 if all(d>0 for d in diffs) else -1 if all(d<0 for d in diffs) else 0
    pooled_diff=pooled_a-pooled_b
    return {'reversal':bool(sign_all and pooled_diff*sign_all<0), 'pooled_difference':pooled_diff,
            'stratum_differences':{k:ra[k]-rb[k] for k in a},
            'status':'DESCRIPTIVE_SYNTHETIC_NOT_CAUSAL'}


def pair_agreement(votes: Iterable[NominalVote], *, left: str, right: str) -> dict:
    """Joint-exposure-only agreement; all nonexpressions are excluded, never matched."""
    if left==right:raise ValueError('Pair must contain distinct persons')
    by_vote=defaultdict(dict)
    for v in votes:
        if v.person_id not in (left,right):continue
        if v.person_id in by_vote[v.vote_id]:raise ValueError('Unresolved duplicate')
        by_vote[v.vote_id][v.person_id]=v.choice
    joint=[(d[left],d[right]) for d in by_vote.values() if left in d and right in d and d[left] in EXPRESSED and d[right] in EXPRESSED]
    if not joint:return {'joint_n':0,'observed':None,'chance':None,'excess':None,'status':'NO_JOINT_EXPOSURE'}
    n=len(joint)
    aa=Counter(a for a,_ in joint);bb=Counter(b for _,b in joint)
    obs=sum(a==b for a,b in joint)/n
    chance=sum(aa[c]*bb[c] for c in EXPRESSED)/(n*n)
    return {'joint_n':n,'observed':obs,'chance':chance,'excess':obs-chance,
            'status':'DESCRIPTIVE_SYNTHETIC_NOT_INFLUENCE'}
