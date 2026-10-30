"""Research-only institutional ballot and seat-grain checks; does not authenticate bytes."""
from collections import Counter

FIELDS = ('registered', 'voters', 'candidacy', 'blank', 'valid', 'null')

def _counts(d):
    if not isinstance(d, dict):
        raise ValueError('INVALID_COUNTS')
    for k in FIELDS:
        x = d.get(k)
        if type(x) is not int or x < 0:
            raise ValueError('INVALID_COUNT_' + k)
    if d['voters'] > d['registered']:
        raise ValueError('VOTERS_EXCEED_CENSUS')
    if d['valid'] + d['null'] != d['voters']:
        raise ValueError('BALLOT_IDENTITY_FAIL')
    if d['candidacy'] + d['blank'] != d['valid']:
        raise ValueError('VALID_IDENTITY_FAIL')

def audit_electoral_scope(record):
    if not isinstance(record, dict):
        raise ValueError('INVALID_RECORD')
    kind, scope = record.get('election_kind'), record.get('seat_scope')
    if kind not in ('GALICIA_PARL_2024', 'SPAIN_EU_2024'):
        raise ValueError('UNKNOWN_ELECTION_KIND')
    expected = 'province' if kind == 'GALICIA_PARL_2024' else 'state'
    if scope != expected:
        raise ValueError('INVALID_SEAT_SCOPE')
    counts = record.get('totals')
    _counts(counts)
    seats = record.get('seats')
    if type(seats) is not int or seats != (75 if expected == 'province' else 61):
        raise ValueError('INVALID_TOTAL_SEATS')
    districts = record.get('districts')
    if scope == 'state':
        if districts not in (None, []):
            raise ValueError('PROVINCE_SEAT_ALLOCATION_FORBIDDEN')
    else:
        if not isinstance(districts, list) or len(districts) != 4:
            raise ValueError('INCOMPLETE_DISTRICTS')
        names = [d.get('id') for d in districts if isinstance(d, dict)]
        if len(names) != 4 or len(set(names)) != 4:
            raise ValueError('DUPLICATE_OR_INVALID_DISTRICT')
        sums = Counter()
        for d in districts:
            _counts(d.get('counts'))
            if type(d.get('seats')) is not int or d['seats'] < 1:
                raise ValueError('INVALID_PROVINCE_SEATS')
            sums['seats'] += d['seats']
            for k in FIELDS:
                sums[k] += d['counts'][k]
        if sums['seats'] != seats or any(sums[k] != counts[k] for k in FIELDS):
            raise ValueError('PROVINCE_SUM_MISMATCH')
    return {'status': 'COHERENT_TRANSCRIPTION_NOT_AUTHENTICATED',
            'kind': kind, 'seat_scope': scope, 'original_bytes_verified': False}
