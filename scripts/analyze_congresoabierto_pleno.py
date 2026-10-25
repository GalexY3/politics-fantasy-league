#!/usr/bin/env python3
"""Offline usage: python scripts/analyze_congresoabierto_pleno.py --input data/raw/pleno.jsonl --output data/local_field/coverage.json"""
from __future__ import annotations
import argparse
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from politics_fantasy.historical_coverage import analyze_file, public_summary


def main(argv=None):
    p=argparse.ArgumentParser(description="Reproducible coverage audit of versioned secondary Congreso Abierto JSONL")
    p.add_argument('--input',required=True,type=Path,help="Locally downloaded data/raw/votaciones/pleno.jsonl")
    p.add_argument('--output',required=True,type=Path,help="Safe aggregated report; must not exist")
    p.add_argument('--require-upstream-blob', action='store_true',help="Abort if SHA1 does not match the audited published upstream version")
    args=p.parse_args(argv)
    result=analyze_file(args.input)
    if args.require_upstream_blob and not result['upstream_blob_matches']:
        p.error('Input does not match audited upstream git blob version')
    body=(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+'\n').encode('utf-8')
    args.output.parent.mkdir(parents=True,exist_ok=True)
    with args.output.open('xb') as f:f.write(body)
    print(json.dumps({'report':str(args.output),'source_sha256':result['source_sha256'],
        'source_git_blob_sha1':result['source_git_blob_sha1'],'summary':public_summary(result)['summary']},ensure_ascii=False))

if __name__=='__main__':main()
