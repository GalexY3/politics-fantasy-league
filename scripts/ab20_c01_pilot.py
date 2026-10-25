"""Conservative AB20 C01 arithmetic audit of manually copied official public vote totals.

The HTML source itself was NOT downloaded into this environment. This pilot is NOT a
nominal-vote parser, not representative of all parliamentary sessions, not a forecast.
"""
from __future__ import annotations
from collections import Counter
from hashlib import sha256
from pathlib import Path
import argparse
import csv
import json
import statistics

FIELDS = ('row_id', 'legislature', 'session', 'event_date', 'source_url', 'source_line_yes',
          'yes', 'no', 'abstain', 'reading_method')

def audit(csv_path: Path) -> dict:
    rows = list(csv.DictReader(csv_path.open(encoding='utf-8', newline='')))
    if not rows:
        raise ValueError('empty sample')
    if any(tuple(row.keys()) != FIELDS for row in rows):
        raise ValueError('schema mismatch')
    if len({row['row_id'] for row in rows}) != len(rows):
        raise ValueError('duplicated row id')
    counts = []
    for row in rows:
        if row['legislature'] != 'XV' or row['session'] != '193' or row['event_date'] != '2026-07-23':
            raise ValueError('session mismatch')
        if not row['source_url'].startswith('https://www.congreso.es/'):
            raise ValueError('unexpected source')
        x = [int(row[c]) for c in ('yes','no','abstain')]
        if any(n < 0 for n in x):
            raise ValueError('negative vote counts')
        # Membership is a fixture-specific invariant, not a permanent schema rule.
        if sum(x) > 350:
            raise ValueError('total exceeds 350 (arithmetic incompatibility)')
        counts.append(sum(x))
    hist = Counter(counts)
    return {
        'type': 'OBSERVATIONAL_AGGREGATE_MANUAL_TRANSCRIPTION',
        'status': 'PILOT_RESULT_NOT_INDEPENDENTLY_CONFIRMED',
        'n_rows': len(rows), 'sessions': 1, 'observed_event_date': '2026-07-23',
        'count_with_total_le_350': sum(x<=350 for x in counts),
        'total_min': min(counts), 'total_max': max(counts),
        'total_median': statistics.median(counts),
        'total_mean': statistics.mean(counts),
        'votes_total_histogram': {str(k): hist[k] for k in sorted(hist)},
        'gaps_to_350_arithmetic_only': {str(k): (350-k) for k in sorted(hist)},
        'max_unattributed_arithmetic_gap': max(350-x for x in counts),
        'WARNING': 'Gap is not absence. Source HTML byte stream, first-published-at, and nominal detail absent; no generalization or predictive training permitted.',
        'source': 'https://www.congreso.es/es/opendata/votaciones',
        'csv_sha256': sha256(csv_path.read_bytes()).hexdigest(),
    }

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--input', type=Path, required=True)
    ap.add_argument('--output', type=Path, required=True)
    args = ap.parse_args()
    result = audit(args.input)
    args.output.parent.mkdir(exist_ok=True, parents=True)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False)+'\n', encoding='utf-8')
    print(json.dumps(result, ensure_ascii=False, indent=2))
if __name__ == '__main__':
    main()
