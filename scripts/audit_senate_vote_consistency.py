"""Aggregate-only internal consistency of one previously exposed Senate XML.

This cannot establish identity, independent corroboration or as-of availability.
"""
from __future__ import annotations
from collections import Counter
from pathlib import Path
import argparse
import hashlib
import json
import unicodedata
import xml.etree.ElementTree as ET

EXPECTED_SHA = '671436ba27f90aa9c19fc342fc8508f7d1ddf122aa422b64edca5d6b150a6a71'
STRICT_LABELS = {'SI':'yes', 'NO':'no', 'ABSTENCION':'abstain', 'NO VOTA':'no_vote', 'NV':'no_vote', 'NULO':'null'}
TOTAL_FIELDS = {'yes':'tot_afirmativos', 'no':'tot_negativos', 'abstain':'tot_abstenciones',
                'no_vote':'tot_novotan', 'null':'tot_nulos'}


def normalize(raw: str | None) -> str:
    value = unicodedata.normalize('NFKD', raw or '')
    return ' '.join(''.join(c for c in value if not unicodedata.combining(c)).upper().split())


def nonnegative(raw: str | None) -> int | None:
    text = (raw or '').strip()
    return int(text) if text.isascii() and text.isdigit() else None


def audit_vote(vote: ET.Element, labels: dict[str,str]) -> dict:
    rows = list(vote.iter('VotoSenador'))
    absent = list(vote.iter('ausencia'))
    tallies = Counter()
    unknown = Counter()
    seats = Counter()
    missing_seat = 0
    for row in rows:
        value = normalize(row.findtext('voto'))
        if value in labels:
            tallies[labels[value]] += 1
        else:
            unknown[value or '<MISSING>'] += 1
        seat = (row.findtext('escano') or '').strip()
        if seat:
            seats[seat] += 1
        else:
            missing_seat += 1
    totals = {key: nonnegative(vote.findtext(field)) for key,field in TOTAL_FIELDS.items()}
    matches = {key: (None if unknown or value is None else tallies[key] == value)
               for key,value in totals.items()}
    declared_absent = nonnegative(vote.findtext('tot_ausentes'))
    return {'vote_number': (vote.findtext('num_vot') or '').strip(),
            'vote_code': (vote.findtext('CodVotacion') or '').strip(),
            'nominal_rows': len(rows), 'known_vote_counts': {k:tallies[k] for k in TOTAL_FIELDS},
            'unknown_labels': dict(sorted(unknown.items())), 'declared_totals': totals,
            'candidate_category_matches': matches, 'seats_missing': missing_seat,
            'duplicate_seat_rows': sum(n-1 for n in seats.values() if n>1),
            'absence_rows': len(absent), 'declared_absence': declared_absent,
            'absence_count_match': None if declared_absent is None else len(absent)==declared_absent,
            'declared_present': nonnegative(vote.findtext('tot_presentes'))}


def audit_file(source: Path, output: Path) -> dict:
    blob = source.read_bytes()
    digest = hashlib.sha256(blob).hexdigest()
    if digest != EXPECTED_SHA:
        raise ValueError('Source hash differs from the preregistered capture')
    root = ET.fromstring(blob)
    votes = list(root.iter('votacion'))
    if not votes:
        raise ValueError('No voting elements')
    strict = [audit_vote(v,STRICT_LABELS) for v in votes]
    # The XML actually uses NO VOTAN. This extra mapping was observed only
    # after preregistration and remains a labelled linguistic assumption.
    candidate_labels = {**STRICT_LABELS, 'NO VOTAN':'no_vote'}
    candidate = [audit_vote(v,candidate_labels) for v in votes]
    result = {'id':'CDX05', 'source_sha256':digest, 'source_bytes':len(blob),
              'source_url':'https://www.senado.es/legis15/votaciones/ses_60.xml',
              'source_exposed_before_preregistration':True, 'votes':len(votes),
              'preregistered_mapping':STRICT_LABELS, 'strict':strict,
              'posthoc_candidate_mapping':{'NO VOTAN':'no_vote'}, 'posthoc_candidate':candidate,
              'label_semantics_independently_certified':False,
              'limitation':'Internal consistency within one file, not independent corroboration, identity or first publication.'}
    output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    return result


if __name__ == '__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('source',type=Path)
    parser.add_argument('output',type=Path)
    args=parser.parse_args()
    result=audit_file(args.source,args.output)
    print(json.dumps({'votes':result['votes'],'strict_unknown_votes':sum(bool(v['unknown_labels']) for v in result['strict']),
        'posthoc_candidate_mismatches':sum(any(x is False for x in v['candidate_category_matches'].values()) for v in result['posthoc_candidate'])},ensure_ascii=False))
