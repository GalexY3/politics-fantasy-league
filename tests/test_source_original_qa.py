"""Synthetic fixture regressions for source_original_qa; never real personal data."""
import unittest
from politics_fantasy.source_original_qa import audit_congress_vote,senate_event_day

def fixture(rows,yes=0,no=0,abs_=0,nov=0):
    return {'totales':{'afavor':yes,'enContra':no,'abstenciones':abs_,
            'noVotan':nov,'presentes':len(rows)-nov},'votaciones':rows}
def row(seat,vote):return {'asiento':seat,'voto':vote}

class TestSourceControls(unittest.TestCase):
    def test_repeated_missing_seat_is_not_person_key(self):
        x=audit_congress_vote(fixture([row('-1','Sí'),row('-1','No')],yes=1,no=1))
        self.assertEqual(x['unassigned_seat_minus_one'],2)
        self.assertEqual(x['distinct_assigned_seats'],0)
        self.assertFalse(x['stable_person_identity_certified'])
    def test_duplicate_real_seat_rejected(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE'):
            audit_congress_vote(fixture([row('7','Sí'),row('7','No')],yes=1,no=1))
    def test_category_reconciliation(self):
        x=audit_congress_vote(fixture([row('9','Sí'),row('10','No'),
            row('11','Abstención'),row('-1','No vota')],yes=1,no=1,abs_=1,nov=1))
        self.assertTrue(x['exact_nominal_categories_and_totals'])
    def test_total_mismatch_rejected(self):
        with self.assertRaisesRegex(ValueError,'TOTAL_MISMATCH'):
            audit_congress_vote(fixture([row('10','Sí')],yes=0,no=1))
    def test_present_mismatch_rejected(self):
        x=fixture([row('10','Sí')],yes=1);x['totales']['presentes']=0
        with self.assertRaisesRegex(ValueError,'PRESENT_COUNT_MISMATCH'):
            audit_congress_vote(x)
    def test_vote_day_prioritized_over_session_header(self):
        x=senate_event_day('07/10/2025','08-OCT-2025')
        self.assertEqual(x['vote_event_day'],'2025-10-08')
        self.assertTrue(x['vote_day_differs_from_header'])
    def test_unknown_category_rejected(self):
        with self.assertRaisesRegex(ValueError,'UNSUPPORTED'):
            audit_congress_vote(fixture([row('10','No sé')],yes=1))
    def test_no_timestamp_copied_from_event_day(self):
        self.assertFalse(senate_event_day('07/10/2025','08-OCT-2025')['publication_timestamp_verified'])

    def test_null_original_totals_rejected_with_validation_error(self):
        source=fixture([row('1','Sí')],yes=1)
        source['totales']=None
        with self.assertRaisesRegex(ValueError,'INVALID_OFFICIAL_TOTALS_SHAPE'):
            audit_congress_vote(source)
    def test_noncanonical_assigned_seat_rejected(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_OR_MALFORMED'):
            audit_congress_vote(fixture([row('001','Sí')],yes=1))

if __name__=='__main__':unittest.main()
