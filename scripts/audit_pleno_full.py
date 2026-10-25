#!/usr/bin/env python3
"""Audit a PINNED copy of CongresoAbierto's secondary pleno.jsonl.

No direct downloads, no deputy names, no claims about official nominal completeness.
Usage:
  python scripts/audit_pleno_full.py /path/to/pleno.jsonl --out research/audit.json
Source at https://github.com/MarcoAnarmo/CongresoAbierto/blob/main/data/raw/votaciones/pleno.jsonl
Pinned Git blob SHA1: 71918bb689c7a62cfbbdafe0b9248eac6b5c4be1
This tool is *not* as-of-valid as a 2023-2026 predictor: the snapshot is recent.
"""
from __future__ import annotations
import argparse
import collections
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, median

OPTIONS = ('S', 'N', 'A', 'X')
SOURCE_BLOB_SHA1 = '71918bb689c7a62cfbbdafe0b9248eac6b5c4be1'

def git_blob_sha1(raw: bytes) -> str:
    return hashlib.sha1(f'blob {len(raw)}\0'.encode() + raw).hexdigest()

def nominal_codes(v: dict) -> list[list[str]]:
    votes = v.get('votos') or {}
    if set(votes) - set(OPTIONS):
        raise ValueError('Unknown category in vote map')
    return [str(votes.get(k, '')).split() for k in OPTIONS]

def official_totals(v: dict) -> list[int]:
    t = v['totales']
    xs = [t['si'], t['no'], t['abstencion'], t['noVota']]
    if any(not isinstance(z, int) or z < 0 for z in xs):
        raise ValueError('Invalid count')
    return xs

def audit(records: list[dict], *, require_source_sha: bool=False) -> dict:
    rows = []; years = collections.defaultdict(lambda: {'n':0, 'nom':0,'total':0,'gap':0,'sessions':set(),'codes':set(), 'flips':0,'nominal_positive':0})
    sessions={}; seen=set(); codes=set(); groups=[]; bad_groups=[]; dup_person=[]; cat_gap=[0]*4; no_nominal=[]; not350=[]; unknown=0
    for v in records:
        vid=v['id']; day=v['fecha']; year=day[:4]
        if vid in seen: raise ValueError('Duplicate vote id: '+vid)
        seen.add(vid)
        cs=nominal_codes(v); n=[len(q) for q in cs]; flat=[c for q in cs for c in q]
        if len(set(flat)) != len(flat): dup_person.append(vid)
        for q in flat: codes.add(q)
        t=official_totals(v)
        if any(x>t[i] for i,x in enumerate(n)): raise ValueError('Nominal count exceeds aggregate: '+vid)
        g=v.get('grupos') or {}; gt=[0]*4
        for key,gc in g.items():
            if len(gc)!=4 or any(not isinstance(k,int) or k<0 for k in gc): raise ValueError('Invalid group')
            for i,k in enumerate(gc): gt[i]+=k
            groups.append((vid,key,gc))
            if key=='?': unknown+=1
        if g and gt!=t: bad_groups.append(vid)
        T=sum(t); N=sum(n); gap=T-N
        for i in range(4): cat_gap[i]+=t[i]-n[i]
        if not N: no_nominal.append(vid)
        if T!=350: not350.append({'id':vid,'total':T})
        official_majority = (t[0]>t[1])-(t[0]<t[1]); nominal_majority=(n[0]>n[1])-(n[0]<n[1])
        flip = bool(N and official_majority != nominal_majority)
        sess=f"{day}|{v['sesion']}"
        y=years[year];y['n']+=1;y['nom']+=N;y['total']+=T;y['gap']+=gap;y['sessions'].add(sess);y['codes'].update(flat);y['flips']+=flip;y['nominal_positive']+=bool(N)
        s=sessions.setdefault(sess,{'year':year,'nom':0,'total':0,'gap':0,'votes':0})
        s['nom']+=N;s['total']+=T;s['gap']+=gap;s['votes']+=1
        rows.append({'id':vid,'year':year,'session':sess,'nom':n,'official':t,'gap':gap,'T':T,'N':N,'flip':flip, 'type':v.get('tipo',''),'groups':g})
    years_out={year:{'votes':y['n'],'sessions':len(y['sessions']),'nominal':y['nom'],'positions':y['total'],'gap':y['gap'],'coverage':y['nom']/y['total'],'unique_codes':len(y['codes']),'flips':y['flips'],'no_nominal':y['n']-y['nominal_positive']} for year,y in sorted(years.items())}
    n_options=[sum(r['nom'][i] for r in rows) for i in range(4)]
    t_options=[sum(r['official'][i] for r in rows) for i in range(4)]
    return {'source':'CongresoAbierto secondary JSONL; not official independently certified','votes':len(rows),'sessions':len(sessions),'unique_ids':len(seen),'unique_codes':len(codes),'nominal_rows':sum(r['N'] for r in rows), 'positions':sum(r['T'] for r in rows),'gap':sum(r['gap'] for r in rows),'gap_by_option':dict(zip(OPTIONS,cat_gap)),'count_by_option':dict(zip(OPTIONS,t_options)),'nominal_by_option':dict(zip(OPTIONS,n_options)), 'blank_nominal_ids':no_nominal,'not350':not350,'unknown_group_rows':unknown,'group_total_mismatches':bad_groups,'duplicated_nominal_codes_in_vote':dup_person,'fully_identified_votes':sum(r['N']==r['T'] for r in rows),'partially_identified_votes':sum(0<r['N']<r['T'] for r in rows),'majority_flips':sum(r['flip'] for r in rows),'majority_flips_by_year':{y:x['flips'] for y,x in years_out.items()},'years':years_out,'group_rows':len(groups),'sessions_summary':sessions, 'metric_definitions':{'gap':'sum of official aggregated categories minus sum of nominal codes; never number of absentee persons','flip':'sign(official sí−no) differs from sign(identified sí−no), excluding votes without nominal codes','coverage':'nominal entries / official aggregated positions within the same secondary source'}}

def main() -> None:
    ap=argparse.ArgumentParser();ap.add_argument('jsonl',type=Path);ap.add_argument('--out',type=Path);ap.add_argument('--strict-git-blob', action='store_true');args=ap.parse_args()
    raw=args.jsonl.read_bytes();sha=git_blob_sha1(raw)
    if args.strict_git_blob and sha!=SOURCE_BLOB_SHA1:raise SystemExit(f'Pinned Git SHA mismatch: got {sha}')
    rows=[json.loads(line) for line in raw.decode('utf-8').splitlines() if line.strip()]
    output=audit(rows);output['sha256']=hashlib.sha256(raw).hexdigest();output['git_blob_sha1']=sha;output['verified_source']=sha==SOURCE_BLOB_SHA1
    data=json.dumps(output,sort_keys=True,ensure_ascii=False,indent=2)
    if args.out:args.out.parent.mkdir(parents=True,exist_ok=True);args.out.write_text(data+'\n',encoding='utf-8')
    else:print(data)

if __name__=='__main__':main()
