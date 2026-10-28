"""Reproducible prequential diagnostics. Inputs in tests are ALL synthetic.

No causality, predictivity or calibration for Spanish MPs is demonstrated.
"""
from __future__ import annotations
from collections import defaultdict
from math import isfinite, lgamma, log
from random import Random
from typing import Iterable


def poisson_nll(y: int, lam: float) -> float:
    """Full Poisson negative log likelihood, including the target-only term."""
    if type(y) is not int or y<0 or not isfinite(lam) or lam<0:
        raise ValueError('Invalid count or rate')
    if lam==0:return 0.0 if y==0 else float('inf')
    return lam-y*log(lam)+lgamma(y+1)


def count_mae(pairs: Iterable[tuple[int,float]]) -> float:
    rows=list(pairs)
    if not rows:raise ValueError('Empty evaluation')
    for y,lam in rows:
        if type(y) is not int or y<0 or not isfinite(lam) or lam<0:
            raise ValueError('Invalid count forecast')
    return sum(abs(y-lam) for y,lam in rows)/len(rows)


def relative_skill(model_loss: float, baseline_loss: float) -> float | None:
    """Same-fold scores, lower loss wins. Undefined if baseline has zero loss."""
    if not isfinite(model_loss) or not isfinite(baseline_loss) or model_loss<0 or baseline_loss<0:
        raise ValueError('Invalid loss')
    return 1-model_loss/baseline_loss if baseline_loss>0 else None


def calibration_bins(rows: Iterable[tuple[int,float]], *, edges: tuple[float,...], min_n: int=2) -> list[dict]:
    """Use predetermined numeric cutoffs and require >=min_n support per bin."""
    if min_n<1 or any(not isfinite(x) or x<=0 for x in edges) or tuple(sorted(set(edges)))!=edges:
        raise ValueError('Invalid calibration cutoffs')
    buckets=[[] for _ in range(len(edges)+1)]
    for y,lam in rows:
        if type(y) is not int or y<0 or not isfinite(lam) or lam<0:raise ValueError('Invalid case')
        k=0
        while k<len(edges) and lam>=edges[k]: k+=1
        buckets[k].append((y,lam))
    out=[]
    for j,bucket in enumerate(buckets):
        n=len(bucket)
        out.append({'lower':None if j==0 else edges[j-1],
                    'upper':None if j==len(edges) else edges[j],
                    'n':n,
                    'observed':sum(y for y,_ in bucket)/n if n>=min_n else None,
                    'predicted':sum(v for _,v in bucket)/n if n>=min_n else None,
                    'status':'ESTIMATED_SYNTHETIC' if n>=min_n else 'LOW_SUPPORT'})
    return out


def purged_walk_forward(weeks: list[str], *, min_train: int, gap: int, horizon: int=1):
    """Chronological weekly folds with excluded gap rows before each forecast."""
    if weeks!=sorted(set(weeks)) or min_train<2 or gap<0 or horizon<1:
        raise ValueError('Invalid chronological validation design')
    for i in range(min_train,len(weeks)-gap-horizon+1):
        train=weeks[:i]
        purge=weeks[i:i+gap]
        test=weeks[i+gap:i+gap+horizon]
        yield {'train':train,'purged':purge,'test':test}


def session_bootstrap_ci(session_values: dict[str,list[float]], *, replicates: int=400,
                         seed: int=29, level: float=.95) -> dict:
    """Equal-weight mean of session means; each session is one resampling unit.

    NOT the pooled mean over all observed votes when session sizes differ.
    """
    if not session_values or replicates<20 or not 0<level<1:
        raise ValueError('Invalid cluster bootstrap design')
    sessions=sorted(session_values)
    means=[]
    for values in session_values.values():
        if not values or any(not isfinite(v) for v in values):raise ValueError('Invalid session values')
    if len(sessions)<2:raise ValueError('At least two independent sessions required')
    for key in sessions:
        val=session_values[key]
        means.append(sum(val)/len(val))
    mean=sum(means)/len(means)
    rng=Random(seed)
    draws=[]
    for _ in range(replicates):
        picks=[means[rng.randrange(len(means))] for _ in sessions]
        draws.append(sum(picks)/len(picks))
    draws.sort()
    a=(1-level)/2
    li=max(0,min(replicates-1,int(a*replicates)))
    hi=max(0,min(replicates-1,int((1-a)*replicates)))
    return {'mean':mean,'lower':draws[li],'upper':draws[hi], 'clusters':len(sessions),
            'status':'CLUSTER_BOOTSTRAP_SYNTHETIC_NOT_EXTERNAL'}

def record_weighted_cluster_bootstrap_ci(
    session_values: dict[str,list[float]], *, replicates: int=400,
    seed: int=29, level: float=.95
) -> dict:
    """Bootstrap the pooled *record* mean by resampling whole sessions.

    Each session's entire observed block is selected or omitted together.
    For unequal cluster sizes this estimand differs from session_bootstrap_ci,
    which gives every session mean the same point-estimate weight.
    No causal effect or real-source authenticity is implied.
    """
    if (not session_values or type(replicates) is not int or replicates<20
            or type(seed) is not int or not 0<level<1):
        raise ValueError('Invalid record-weighted cluster bootstrap design')
    keys=sorted(session_values)
    if len(keys)<2:
        raise ValueError('At least two independent sessions required')
    blocks=[]
    for key in keys:
        vals=session_values[key]
        if not vals or any(not isfinite(v) for v in vals):
            raise ValueError('Invalid session values')
        total=sum(vals)
        if not isfinite(total):
            raise ValueError('Nonfinite session total')
        blocks.append((total,len(vals)))
    total=sum(t for t,n in blocks)
    denominator=sum(n for t,n in blocks)
    mean=total/denominator
    if not isfinite(mean):
        raise ValueError('Nonfinite pooled mean')
    rng=Random(seed)
    draws=[]
    for _ in range(replicates):
        sampled=[blocks[rng.randrange(len(blocks))] for _ in blocks]
        numerator=sum(t for t,n in sampled)
        size=sum(n for t,n in sampled)
        value=numerator/size
        if not isfinite(value):
            raise ValueError('Nonfinite bootstrap draw')
        draws.append(value)
    draws.sort()
    a=(1-level)/2
    li=max(0,min(replicates-1,int(a*replicates)))
    hi=max(0,min(replicates-1,int((1-a)*replicates)))
    return {'mean':mean,'lower':draws[li],'upper':draws[hi],
            'clusters':len(blocks),'observed_records':denominator,
            'estimand':'RECORD_WEIGHTED_MEAN_WITH_SESSION_BLOCK_RESAMPLING',
            'status':'CLUSTER_BOOTSTRAP_SYNTHETIC_NOT_EXTERNAL'}
