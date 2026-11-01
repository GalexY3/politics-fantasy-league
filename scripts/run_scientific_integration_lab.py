"""Offline reproduction CLI for the fixed fictional PFL integration lab.

Usage: python scripts/run_scientific_integration_lab.py --cut early
No URLs, original files, cases, PII, licenses, external tokens or user JSON.
Node.js is required for the actual JS warehouse consumer; no silent fallback.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"src"))
from politics_fantasy.scientific_integration_lab import report


def main() -> None:
    parser=argparse.ArgumentParser(description="PFL fixed synthetic E2E research infrastructure lab")
    parser.add_argument("--cut",choices=("early","late"),default="late")
    parser.add_argument("--scenario",choices=("baseline","rights_spoof","privacy_probe"),
                        default="baseline")
    args=parser.parse_args()
    print(json.dumps(report(cut=args.cut,scenario=args.scenario),
                     ensure_ascii=False,sort_keys=True,indent=2))


if __name__=="__main__":
    main()
