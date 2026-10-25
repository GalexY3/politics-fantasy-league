#!/usr/bin/env python3
"""Post-hoc adversarial refinement of vote-sign differences in secondary JSONL.

Official-like totals and identified-person subset are from *the same source*.
A sign reversal is NOT a reversal of Congress's official decision.
"""
from __future__ import annotations
import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path

UPSTREAM='71918bb689c7a62cfbbdafe0b9248eac6b5c4be1'

def sign(value: int) -> int:
    return (value > 0) - (value < 0)

def compare_ballot(r: dict) -> str:
    yes, no = r['totales']['si'], r['totales']['no']
    votes = r.get('votos', {}) or {}
    n_yes=len(votes.get('S','').split())
    n_no=len(votes.get('N','').split())
    n_any=sum(len(v.split()) for v in votes.values())
    if n_any==0:return 'NO_NOMINAL'
    a,b=sign(yes-no),sign(n_yes-n_no)
    if a==b:return 'SAME_SIGN'
    if 0 in (a,b):return 'TIE_INVOLVED'
    return 'STRICT_REVERSAL'


def compute(path: Path, *, verify_blob: bool=True) -> dict:
    content=path.read_bytes()
    blob=hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    if verify_blob and blob!=UPSTREAM:
        raise ValueError('Not the audited historical git blob: need explicit --no-verify to analyze a different revision')
    counts=Counter();year=defaultdict(Counter)
    seen=set()
    for line in content.splitlines():
        if not line.strip():continue
        r=json.loads(line)
        if r['id'] in seen:raise ValueError('duplicate vote ID')
        seen.add(r['id'])
        kind=compare_ballot(r)
        counts[kind]+=1
        year[r['fecha'][:4]][kind]+=1
    return {'source_blob_sha1':blob,'secondary_source_only':True,
       'official_decisions_questioned':False,
       'total_votaciones':len(seen),
       'count_by_type':dict(sorted(counts.items())),
       'by_year':{y:dict(sorted(c.items())) for y,c in sorted(year.items())},
       'interpretation':'Distinguish strict +/- reversal from any change involving 0 (tie); neither challenges official outcome'}


def main():
    p=argparse.ArgumentParser()
    p.add_argument('input',type=Path)
    p.add_argument('--no-verify',action='store_true')
    args=p.parse_args()
    print(json.dumps(compute(args.input,verify_blob=not args.no_verify),ensure_ascii=False,indent=2,sort_keys=True))

if __name__=='__main__':main()
