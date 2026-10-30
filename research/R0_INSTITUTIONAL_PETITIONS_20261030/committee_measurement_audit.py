"""Selected-case posthoc measurement audit, not a new scientific experiment.

No fetching, fuzzy matching, names, titles or raw decision text in output.
See CONTINUATION20_20261030/C39_AUDIT_CONTRACT.json for selection exposure.
"""
import csv
import hashlib
from html.parser import HTMLParser
from io import StringIO
import re
import unicodedata

CSV_SHA = 'a57572556e945076a421760b0ed6a0b43335c5378abf78b5e179190e4c009d4a'
CASES = {2760: 'examination', 3021: 'classification',
         3070: 'examination', 4583: 'classification'}
MISSING = {'', 'nan', 'none', 'null'}


class Text(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.parts = []

    def handle_data(self, data):
        self.parts.append(data)


def audit(csv_bytes, minute_bytes, *, expected_sha=CSV_SHA):
    if not 50 < len(csv_bytes) <= 16_000_000 or not 50 < len(minute_bytes) <= 2_000_000:
        raise ValueError('SOURCE_SIZE')
    digest = hashlib.sha256(csv_bytes).hexdigest()
    if digest != expected_sha:
        raise ValueError('C38_SNAPSHOT_MISMATCH')
    parser = Text()
    parser.feed(minute_bytes.decode('utf-8-sig'))
    text = re.sub(r'\s+', ' ', unicodedata.normalize('NFKC', ' '.join(parser.parts)))
    for identifier, kind in CASES.items():
        if kind == 'examination':
            pattern = rf"La commission se prononce pour l.examen de la pétition n.\s*{identifier}\b"
        else:
            pattern = rf"La pétition n.\s*{identifier} est donc classée"
        if not re.search(pattern, text):
            raise ValueError('EXPLICIT_DECISION_ANCHOR_MISSING')
    reader = csv.DictReader(StringIO(csv_bytes.decode('utf-8-sig'), newline=''), delimiter=';')
    required = {'identifiant', 'statut', 'decision_commission'}
    if (reader.fieldnames is None or len(reader.fieldnames) != len(set(reader.fieldnames))
            or not required.issubset(reader.fieldnames)):
        raise ValueError('CSV_SCHEMA')
    matched, seen = {}, set()
    for row in reader:
        key = str(row.get('identifiant') or '').strip()
        if not key or key in seen:
            raise ValueError('DUPLICATE_OR_EMPTY_ID')
        seen.add(key)
        if key in {str(x) for x in CASES}:
            matched[int(key)] = row
    groups = {kind: {'matched': 0, 'missing_decision_field': 0,
                     'open_status': 0, 'terminal_status': 0, 'other_status': 0}
              for kind in ('examination', 'classification')}
    for key, row in matched.items():
        group = groups[CASES[key]]
        group['matched'] += 1
        group['missing_decision_field'] += str(row['decision_commission'] or '').strip().lower() in MISSING
        status = str(row['statut'] or '').strip().lower()
        category = ('open_status' if status == 'ouverte' else 'terminal_status'
                    if status in {'classee', 'expiree', 'archivee'} else 'other_status')
        group[category] += 1
    return {'schema': 'pfl.c39.posthoc.measurement_result.v1',
            'csv_sha256': digest, 'minute_sha256': hashlib.sha256(minute_bytes).hexdigest(),
            'csv_records': len(seen), 'selected_cases': len(CASES), 'matched': len(matched),
            'unmatched': len(CASES) - len(matched), 'groups': groups,
            'status': 'COMPLETE_SELECTED_CASE_AUDIT' if len(matched) == len(CASES) else 'INCONCLUSIVE_UNMATCHED_CASES',
            'scientific_cycle_count': 0, 'independent_confirmation': False,
            'causal': False, 'population_missingness_estimate': False,
            'nonempty_field_agreement_with_minute_tested': False}
