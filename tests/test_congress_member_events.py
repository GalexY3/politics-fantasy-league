"""Pure BOCG temporal-source regression tests. Public doc labels abstracted."""
import unittest
from politics_fantasy.congress_member_events import audit_member_event_ledger as audit

def row(key,kind,day,issue="BOCG-15-D-390",issue_day="2025-09-12"):
    return {"issuer":"Congreso de los Diputados","bulletin_id":issue,
            "item_key":key,"event_kind":kind,"event_day":day,
            "bulletin_issue_day":issue_day}

class MemberEventTests(unittest.TestCase):
    def test_2025_three_credential_lags_and_full_condition(self):
        rows=[row("member-a","FULL_CONDITION_ACQUIRED","2025-09-09"),
              row("member-b","FULL_CONDITION_ACQUIRED","2025-09-09"),
              row("member-c","FULL_CONDITION_ACQUIRED","2025-09-09"),
              row("member-a","CREDENTIAL_SUBMITTED","2025-08-01"),
              row("member-b","CREDENTIAL_SUBMITTED","2025-09-02"),
              row("member-c","CREDENTIAL_SUBMITTED","2025-09-09"),
              row("member-exit","FULL_CONDITION_CEASED","2025-09-02")]
        result=audit(rows)
        self.assertEqual(result["documented_event_rows"],7)
        self.assertEqual(result["by_event_kind"]["CREDENTIAL_SUBMITTED"],3)
        self.assertFalse(result["one_to_one_successorship_inferred"])
    def test_2023_lag_and_events(self):
        x=audit([row("member-1","FULL_CONDITION_CEASED","2023-12-06",
                     "BOCG-15-D-51","2023-12-15"),
                 row("member-2","FULL_CONDITION_ACQUIRED","2023-12-12",
                     "BOCG-15-D-51","2023-12-15")])
        self.assertEqual(x["observed_event_to_issue_lags"],[3,9])
    def test_duplicate_source_event_denied(self):
        r=row("m","FULL_CONDITION_ACQUIRED","2025-09-09")
        with self.assertRaisesRegex(ValueError,"DUPLICATE_SOURCE_EVENT_KEY"):
            audit([r,r])
    def test_multiple_kinds_per_member_are_distinct(self):
        x=audit([row("m","CREDENTIAL_SUBMITTED","2025-09-02"),
                 row("m","FULL_CONDITION_ACQUIRED","2025-09-09")])
        self.assertEqual(x["documented_event_rows"],2)
    def test_event_after_issue_is_denied(self):
        with self.assertRaisesRegex(ValueError,"EVENT_AFTER_ISSUE_DAY"):
            audit([row("m","FULL_CONDITION_ACQUIRED","2025-09-13")])
    def test_invalid_date_denied(self):
        with self.assertRaisesRegex(ValueError,"INVALID_DATE"):
            audit([row("m","FULL_CONDITION_ACQUIRED","2025-02-30")])
    def test_wrong_bulletin_date_denied(self):
        with self.assertRaisesRegex(ValueError,"ISSUE_DAY_MISMATCH"):
            audit([row("m","FULL_CONDITION_ACQUIRED","2025-09-09",issue_day="2025-09-11")])
    def test_untrusted_issuer_denied(self):
        r=row("m","FULL_CONDITION_ACQUIRED","2025-09-09")
        r["issuer"]="unknown"
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_ISSUER"):
            audit([r])
    def test_extra_identity_field_denied(self):
        r=row("m","FULL_CONDITION_ACQUIRED","2025-09-09");r["person_id"]="invented"
        with self.assertRaisesRegex(ValueError,"INVALID_EVENT_SCHEMA"):
            audit([r])
    def test_no_retroactive_publication_or_scoring(self):
        x=audit([row("m","FULL_CONDITION_ACQUIRED","2025-09-09")])
        self.assertFalse(x["first_public_at_exact_verified"])
        self.assertFalse(x["person_identity_certified"])
        self.assertFalse(x["real_person_scoring"])
        self.assertFalse(x["release_grade"])
if __name__=="__main__":unittest.main()
