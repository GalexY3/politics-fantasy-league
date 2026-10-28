"""US House vote aggregate invariants: research-only, not authenticated API or forecasts."""
from datetime import date

PARTIES = ('Republican', 'Democratic')
TOTALS = ('yea', 'nay', 'present', 'not_voting')
PREVOTE = frozenset(('house', 'year', 'roll', 'date', 'question', 'vote_type'))


def _positive_integer(x, label, zero=True):
    if type(x) is not int or x < (0 if zero else 1):
        raise ValueError('INVALID_' + label)


def audit_record(row):
    if type(row) is not dict or row.get('house') != 'US_HOUSE':
        raise ValueError('INVALID_HOUSE')
    year, roll = row.get('year'), row.get('roll')
    if year not in (2025, 2026) or type(year) is not int:
        raise ValueError('INVALID_YEAR')
    _positive_integer(roll, 'ROLL', zero=False)
    if not isinstance(row.get('source_url'), str) or row['source_url'] != f'https://clerk.house.gov/Votes/{year}{roll}':
        raise ValueError('INVALID_SOURCE_KEY')
    d = row.get('date')
    try:
        if not isinstance(d, str) or date.fromisoformat(d).isoformat() != d:
            raise ValueError('bad')
    except ValueError:
        raise ValueError('INVALID_DATE') from None
    if not all(isinstance(row.get(k), str) and row[k].strip() for k in ('question', 'vote_type')):
        raise ValueError('MISSING_PROCEDURE')
    totals, parties = row.get('totals'), row.get('parties')
    if type(totals) is not dict or type(parties) is not dict:
        raise ValueError('INVALID_AGGREGATES')
    for k in TOTALS:
        _positive_integer(totals.get(k), 'TOTAL_' + k)
    if not set(PARTIES).issubset(parties) or not set(parties).issubset(set(PARTIES) | {'Independent'}):
        raise ValueError('INVALID_PARTIES')
    computed = dict.fromkeys(TOTALS, 0)
    for p in parties.values():
        if type(p) is not dict:
            raise ValueError('INVALID_PARTY_ROW')
        for k in TOTALS:
            val = p.get(k, 0 if k == 'present' else None)
            _positive_integer(val, 'PARTY_' + k)
            computed[k] += val
    if any(computed[k] != totals[k] for k in TOTALS):
        raise ValueError('PARTY_TOTAL_MISMATCH')
    groups = [parties[k] for k in PARTIES]
    for group in groups:
        if group['yea'] + group['nay'] == 0 or group['yea'] == group['nay']:
            raise ValueError('NO_GROUP_MAJORITY')
    return {'house': 'US_HOUSE', 'year': year, 'roll': roll,
            'shared_group_majority': (groups[0]['yea'] > groups[0]['nay']) == (groups[1]['yea'] > groups[1]['nay']),
            'not_voting_is_attendance': False, 'original_xml_verified': False}


def prevote_features(payload):
    if type(payload) is not dict or set(payload) != PREVOTE:
        raise ValueError('POSTVOTE_FEATURE_LEAK_OR_MISSING_INPUT')
    if payload.get('house') != 'US_HOUSE' or not isinstance(payload.get('question'), str):
        raise ValueError('INVALID_PREVOTE_CONTEXT')
    return dict(payload)
