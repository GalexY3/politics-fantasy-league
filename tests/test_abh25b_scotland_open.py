import json,unittest
from research.ABH25B_20261030.c08_scotland_open_age import analysis
def body(status="under consideration",date="2025-10-30T00:00:00Z",closed=None,ids=("PE1000",)):
    return json.dumps({"data":[{"pe_number":i,"attributes":{
      "status":status,"opened_at":date,"closed_at":closed,
      "petitioner":"SYNTHETIC_SECRET_DO_NOT_EXPORT"}} for i in ids]}).encode()
class ScottishOpenControls(unittest.TestCase):
    def test_one_year_open_is_censored_not_resolved(self):
        v=analysis(body())
        self.assertEqual(v["valid_open_ages"],1)
        self.assertTrue(v["right_censored"])
        self.assertTrue(v["closure_duration_not_observed"])
        self.assertNotIn("SYNTHETIC_SECRET",json.dumps(v))
    def test_missing_age_is_not_zero(self):
        v=analysis(body(date=None))
        self.assertIsNone(v["median_observed_age_days"])
        self.assertEqual(v["missing_opened_at"],1)
    def test_future_and_already_closed_are_explicit_red_flags(self):
        v=analysis(body(date="2027-01-01T00:00:00Z",closed="2026-01-01T00:00:00Z"))
        self.assertEqual(v["future_opened_at"],1);self.assertEqual(v["closed_at_when_open"],1)
    def test_duplicate_or_false_state_fail_closed(self):
        with self.assertRaisesRegex(ValueError,"DUPLICATE_ID"):
            analysis(body(ids=("PE1000","PE1000")))
        with self.assertRaisesRegex(ValueError,"STATE_MISMATCH"):
            analysis(body(status="closed"))
if __name__=='__main__':unittest.main()
