#!/usr/bin/env python3
"""Source-backed descriptive audit of user-provided public CongresoAbierto JSONL.

Example (do NOT commit the original source):
PYTHONPATH=src python scripts/audit_public_pleno.py --jsonl ./data/local/pleno.jsonl --out ./data/local/historical_coverage_audit.json
"""
import argparse, json
from pathlib import Path
from politics_fantasy.historical_coverage import load_jsonl, summary, KNOWN_GIT_BLOB

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--jsonl',type=Path,required=True)
    p.add_argument('--out',type=Path,required=True)
    p.add_argument('--accept-new-blob',action='store_true',help='Treat as different source version; hash remains recorded')
    args=p.parse_args()
    rows,provenance=load_jsonl(args.jsonl,expected_blob_sha1=None if args.accept_new_blob else KNOWN_GIT_BLOB)
    result=summary(rows,provenance)
    args.out.parent.mkdir(parents=True,exist_ok=True)
    # Exclusive create (no silent overwrites). Avoid dumping original nominal codes.
    with args.out.open('x',encoding='utf8') as f:
        json.dump(result,f,ensure_ascii=False,indent=2,sort_keys=True)
        f.write('\n')
    print('Audit:',len(rows),'records; summary:',args.out,'source SHA256:',provenance['sha256'])
if __name__=='__main__':main()
