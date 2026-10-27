import unittest
from politics_fantasy.boe_2023_publication_bound import assess_boe_2023_document as f

class Test2023BoeBound(unittest.TestCase):
    def test_june_document_not_same_day(self):
        self.assertFalse(f(document_id='BOE-A-2023-15066',as_of='2023-06-27T23:59:59+02:00')['available_under_assumption'])
    def test_june_document_next_midnight(self):
        self.assertTrue(f(document_id='BOE-A-2023-15066',as_of='2023-06-28T00:00:00+02:00')['available_under_assumption'])
    def test_september_document_not_same_day(self):
        self.assertFalse(f(document_id='BOE-A-2023-18907',as_of='2023-09-01T23:59:59+02:00')['available_under_assumption'])
    def test_september_document_next_day(self):
        self.assertTrue(f(document_id='BOE-A-2023-18907',as_of='2023-09-02T00:00:00+02:00')['available_under_assumption'])
    def test_unknown_source_is_denied(self):
        self.assertEqual(f(document_id='BOE-A-2023-FAKE',as_of='2026-10-27T00:00:00+01:00')['reason'],'UNKNOWN_OR_UNVERIFIED_DOCUMENT')
    def test_no_naive_datetime(self):
        self.assertFalse(f(document_id='BOE-A-2023-18907',as_of='2023-09-02T00:00:00')['available_under_assumption'])
    def test_signing_or_legal_date_not_first_publication(self):
        r=f(document_id='BOE-A-2023-18907',as_of='2026-10-27T00:00:00+01:00')
        self.assertIsNone(r['first_public_at'])
        self.assertFalse(r['original_historical_web_timestamp_witnessed'])
    def test_not_real_person_release(self):
        r=f(document_id='BOE-A-2023-15066',as_of='2026-10-27T00:00:00+01:00')
        self.assertFalse(r['real_person_scoring'])
        self.assertFalse(r['release_grade'])
    def test_utc_conversion(self):
        self.assertTrue(f(document_id='BOE-A-2023-15066',as_of='2023-06-27T22:00:00Z')['available_under_assumption'])
        self.assertFalse(f(document_id='BOE-A-2023-15066',as_of='2023-06-27T21:59:59Z')['available_under_assumption'])
    def test_bad_cutoff(self):
        self.assertFalse(f(document_id='BOE-A-2023-15066',as_of='garbage')['available_under_assumption'])
if __name__=='__main__':unittest.main()
