import unittest
from politics_fantasy.parliament_procedure_types import audit_procedural_events as audit

def event(family,kind,day,ref="source-1"):
 return dict(issuer="Congreso de los Diputados",legislature="XV",record_family=family,event_kind=kind,event_day=day,record_ref=ref)

class Procedures(unittest.TestCase):
 def test_four_different_events_retained(self):
  rows=[event("PLENARY_DIARY","FULL_CONDITION_ACQUIRED","2026-09-15"),
   event("MEMBER_PROFILE","COMMISSION_ROLE_STARTED","2026-09-16"),
   event("INITIATIVE_FILE","ACTIVITY_STATEMENT_SUBMITTED","2026-09-15"),
   event("INITIATIVE_FILE","ACTIVITY_STATEMENT_QUALIFIED","2026-09-22")]
  self.assertEqual(audit(rows)["source_events"],4)
 def test_wrong_source_cannot_prove_full_status(self):
  with self.assertRaisesRegex(ValueError,"MISMATCHED_SOURCE_ASSERTION"):
   audit([event("INITIATIVE_FILE","FULL_CONDITION_ACQUIRED","2026-09-15")])
 def test_duplicate_procedure_denied(self):
  with self.assertRaisesRegex(ValueError,"DUPLICATE_PROCEDURE"):
   audit([event("PLENARY_DIARY","FULL_CONDITION_ACQUIRED","2026-09-15")]*2)
 def test_bogus_event_day_denied(self):
  with self.assertRaisesRegex(ValueError,"INVALID_EVENT_DAY"):
   audit([event("MEMBER_PROFILE","COMMISSION_ROLE_STARTED","2026-09-31")])
 def test_does_not_infer_person_identity_or_first_publication(self):
  v=audit([event("PLENARY_DIARY","FULL_CONDITION_ACQUIRED","2026-09-15")])
  self.assertIsNone(v["first_public_at"])
  self.assertFalse(v["historical_person_id_certified"])
  self.assertFalse(v["real_person_scoring"])
if __name__=="__main__": unittest.main()
