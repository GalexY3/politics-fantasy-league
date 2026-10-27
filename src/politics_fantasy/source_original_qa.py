"""Aggregate-only checks for original congressional votes; never a person identity certificate."""
from __future__ import annotations
from collections import Counter
from datetime import datetime

CONGRESS_LABELS={'Sí':'afavor','No':'enContra','Abstención':'abstenciones','No vota':'noVotan'}

def audit_congress_vote(original:dict)->dict:
    if not isinstance(original,dict) or not isinstance(original.get('votaciones'),list):
        raise ValueError('INVALID_OFFICIAL_VOTE_SHAPE')
    rows=original['votaciones'];totals=original.get('totales',{})
    count=Counter();non_sentinel=set();sentinel=0
    for row in rows:
        if not isinstance(row,dict) or row.get('voto') not in CONGRESS_LABELS:
            raise ValueError('UNSUPPORTED_VOTE_LABEL')
        if not isinstance(row.get('asiento'),str):
            raise ValueError('BAD_SEAT')
        seat=row['asiento']
        if seat=='-1':sentinel+=1
        else:
            if not seat.isdigit() or seat in non_sentinel:
                raise ValueError('DUPLICATE_OR_MALFORMED_NON_SENTINEL_SEAT')
            non_sentinel.add(seat)
        count[CONGRESS_LABELS[row['voto']]]+=1
    for key in CONGRESS_LABELS.values():
        if type(totals.get(key)) is not int or count[key]!=totals[key]:
            raise ValueError('ORIGINAL_TOTAL_MISMATCH')
    if totals.get('presentes')!=len(rows)-count['noVotan']:
        raise ValueError('PRESENT_COUNT_MISMATCH')
    return {'nominal_rows':len(rows),'unassigned_seat_minus_one':sentinel,
            'distinct_assigned_seats':len(non_sentinel),
            'exact_nominal_categories_and_totals':True,
            'stable_person_identity_certified':False,'first_public_at_certified':False}

def senate_event_day(session_ddmmyyyy:str,individual_vote_ddmonyyyy:str)->dict:
    header=datetime.strptime(session_ddmmyyyy,'%d/%m/%Y').date()
    monthmap={'ENE':'JAN','FEB':'FEB','MAR':'MAR','ABR':'APR','MAY':'MAY','JUN':'JUN','JUL':'JUL','AGO':'AUG','SEP':'SEP','OCT':'OCT','NOV':'NOV','DIC':'DEC'}
    parts=individual_vote_ddmonyyyy.upper().split('-')
    if len(parts)!=3 or parts[1] not in monthmap:
        raise ValueError('UNKNOWN_EVENT_DATE_FORMAT')
    day=datetime.strptime('-'.join([parts[0],monthmap[parts[1]],parts[2]]),'%d-%b-%Y').date()
    return {'session_header_day':header.isoformat(),'vote_event_day':day.isoformat(),
            'vote_day_differs_from_header':day!=header,'publication_timestamp_verified':False}
