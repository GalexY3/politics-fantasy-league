#!/usr/bin/env python3
"""Compare ONE official Congreso vote JSON (downloaded by user) to secondary vote.

Outputs aggregate counts and SHA, *never* names or individual codes. Does not prove
historical roster completeness or first-publication time. No live network access.
"""
from __future__ import annotations
import argparse
import json
import hashlib
from pathlib import Path

VOTE_LABELS={'Sí':'si','No':'no','Abstención':'abstencion','No vota':'noVota'}
FIELDS=('si','no','abstencion','noVota')

def summarize_official(blob:bytes)->dict:
    d=json.loads(blob)
    if not isinstance(d,dict):raise ValueError('Expected JSON object')
    x=d.get('data',d)
    if not isinstance(x,dict) or 'totales' not in x:raise ValueError('Unknown official schema')
    t=x['totales'];candidates={'si':t.get('afavor'),'no':t.get('enContra'),'abstencion':t.get('abstenciones'),'noVota':t.get('noVotan')}
    if any(not isinstance(v,int) or v<0 for v in candidates.values()):raise ValueError('Invalid official count fields')
    votes=x.get('votaciones')
    nominal={k:0 for k in FIELDS}
    if votes is not None:
        if not isinstance(votes,list):raise ValueError('Expected a vote list')
        for row in votes:
            if not isinstance(row,dict) or row.get('voto') not in VOTE_LABELS:raise ValueError('Unrecognized vote category')
            nominal[VOTE_LABELS[row['voto']]]+=1
    return {'sha256_official':hashlib.sha256(blob).hexdigest(),'counts_official':candidates,
            'counts_official_nominal':nominal if votes is not None else None,
            'official_nominal_matches_aggregate':(nominal==candidates) if votes is not None else None,
            'status':'STRUCTURAL_OFFICIAL_AGGREGATE_CHECK_ONLY'}

def compare(official_bytes:bytes,secondary_record:dict)->dict:
    official=summarize_official(official_bytes)
    counts=secondary_record.get('totales')
    if not isinstance(counts,dict) or any(k not in counts for k in FIELDS):raise ValueError('Invalid secondary totals')
    return {**official,'secondary_vote_id':secondary_record['id'],
            'secondary_counts_match_official':all(counts[k]==official['counts_official'][k] for k in FIELDS),
            'next_step':'Resolve official nominal names against DATE-SPECIFIC roster. Never infer missing == No vota.'}

def main():
    p=argparse.ArgumentParser();p.add_argument('official_json',type=Path);p.add_argument('secondary_json',type=Path);
    p.add_argument('--id',required=True);p.add_argument('--out',type=Path);args=p.parse_args()
    secondary=json.loads(args.secondary_json.read_text(encoding='utf-8'))
    if isinstance(secondary,dict) and 'votaciones' in secondary:secondary=secondary['votaciones']
    if isinstance(secondary,list):match=[x for x in secondary if x.get('id')==args.id]
    else:match=[secondary] if secondary.get('id')==args.id else []
    if len(match)!=1:raise SystemExit('Expected exactly one match by vote ID in secondary source')
    result=compare(args.official_json.read_bytes(),match[0])
    s=json.dumps(result,ensure_ascii=False,indent=2)+'\n'
    if args.out:args.out.write_text(s,encoding='utf-8')
    else:print(s)

if __name__=='__main__':main()
