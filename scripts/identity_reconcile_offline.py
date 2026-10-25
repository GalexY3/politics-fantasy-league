#!/usr/bin/env python3
"""Offline single-vote name linkage audit. Never emits deputy names or codes."""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from politics_fantasy.identity_reconcile import reconcile_vote

def main():
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--official",required=True,type=Path)
    ap.add_argument("--secondary",required=True,type=Path)
    ap.add_argument("--roster",required=True,type=Path)
    ap.add_argument("--id",required=True)
    ap.add_argument("--out",type=Path)
    args=ap.parse_args()
    source=json.loads(args.secondary.read_text(encoding="utf-8"))
    if isinstance(source,dict) and "votaciones" in source:source=source["votaciones"]
    if isinstance(source,list):
        candidates=[x for x in source if isinstance(x,dict) and x.get("id")==args.id]
    elif isinstance(source,dict):
        candidates=[source] if source.get("id")==args.id else []
    else:candidates=[]
    if len(candidates)!=1:raise SystemExit("Expected exactly one secondary vote by id")
    result=reconcile_vote(args.official.read_bytes(),candidates[0],args.roster.read_bytes())
    result["vote_id"]=args.id
    output=json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n"
    if args.out:
        args.out.parent.mkdir(parents=True,exist_ok=True)
        args.out.write_text(output,encoding="utf-8")
    else:print(output,end="")
if __name__=="__main__":main()
