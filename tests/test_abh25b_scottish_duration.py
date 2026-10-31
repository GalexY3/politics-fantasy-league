"""ABH25B C06 — synthetic falsification checks only."""
import json,unittest
from research.ABH25B_20261030.c06_scottish_closed_duration import durations
def page(second="2026-01-08T00:00:00Z",status="closed",ident="PE9999"):
    return json.dumps({"data":[{"pe_number":ident,"attributes":{
      "status":status,"opened_at":"2026-01-01T00:00:00Z","closed_at":second,
      "name":"UNEXPORTED_PETITIONER","title":"UNEXPORTED_TITLE","padding":"FICTITIOUS"}}]}).encode()
class DurationTests(unittest.TestCase):
    def test_duration_calendar_7_days_no_identity_export(self):
        x=durations(page())
        self.assertEqual(x["both_dates_valid"],1)
        self.assertEqual(x["median_calendar_days"],7)
        self.assertNotIn("UNEXPORTED",json.dumps(x))
    def test_missing_date_not_zero(self):
        x=durations(page(None))
        self.assertEqual(x["absent_dates"],1)
        self.assertIsNone(x["median_calendar_days"])
    def test_inverted_and_bad_state_not_silently_corrected(self):
        x=durations(page("2025-12-01T00:00:00Z"))
        self.assertEqual(x["reversed_dates"],1)
        self.assertEqual(x["both_dates_valid"],0)
        with self.assertRaisesRegex(ValueError,"STATE_MISMATCH"):durations(page(status="under_consideration"))
    def test_duplicate_ids_rejected(self):
        a=json.loads(page())["data"][0]
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ID"):
            durations(json.dumps({"data":[a,a]}).encode())
if __name__=="__main__":unittest.main()
