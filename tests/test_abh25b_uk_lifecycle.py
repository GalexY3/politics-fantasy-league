import json,unittest
from research.ABH25B_20261030.c09_c11_uk_lifecycle import process,PROTOCOL
def page(mode,ident=1,eligible=False,response=False,debate=False):
    typ,_=PROTOCOL[mode]
    a={"state":typ,"signature_count":110000 if eligible else 12000,
       "response_threshold_reached_at":"2026-01-01T00:00:00Z",
       "government_response_at":"2026-01-20T00:00:00Z" if response else None,
       "debate_outcome_at":"2026-02-20T00:00:00Z" if debate else None,
       "debate_scheduled_on":None,"rejected_at":"2026-01-01T00:00:00Z",
       "rejection":{"reason":"SYNTHETIC_NOT_TO_EXPORT"}}
    return json.dumps({"data":[{"id":ident,"attributes":a}],"pad":"padding"*12}).encode()
def data(mode,eligible=False,response=False,debate=False):
    return {p:page(mode,p,eligible,response,debate) for p in PROTOCOL[mode][1]}
class UKLifecycle(unittest.TestCase):
    def test_open_response_missing_is_pending_not_policy_rejection(self):
        x=process(9,data(9,response=False))
        self.assertEqual(x["aggregates"]["threshold_pending_response"],2)
        self.assertEqual(x["aggregates"].get("response_at",0),0)
    def test_rejected_reason_object_is_admissibility_not_government_response(self):
        x=process(10,data(10))
        self.assertEqual(x["aggregates"]["rejection_object"],2)
        self.assertEqual(x["aggregates"].get("response_at",0),0)
        self.assertNotIn("SYNTHETIC_NOT_TO_EXPORT",json.dumps(x))
    def test_100k_eligibility_without_debate_not_silent_noncompliance(self):
        x=process(11,data(11,eligible=True,response=True,debate=False))
        self.assertEqual(x["aggregates"]["eligible_without_outcome_date"],2)
        self.assertTrue(x["discriminating_support_ok"])
        y=process(11,data(11,eligible=False))
        self.assertFalse(y["discriminating_support_ok"])
    def test_wrong_state_or_duplicate_or_page_adaptation_rejected(self):
        a=data(9)
        with self.assertRaisesRegex(ValueError,"PAGES_NOT_FROZEN"):
            process(9,{3:a[3]})
        a[11]=page(10,11)
        with self.assertRaisesRegex(ValueError,"STATE_FILTER_MISMATCH"):
            process(9,a)
        a=data(10)
        a[16]=a[4]
        with self.assertRaisesRegex(ValueError,"ROW_SCHEMA_OR_DUPLICATE"):
            process(10,a)
if __name__=="__main__":unittest.main()
