import unittest
from politics_fantasy.identity_field_conflicts import audit_birth_assertions as audit

C17 = [
 {'source_ref':'moncloa_2008','publisher_lineage':'Gobierno','birth_day':'1951-07-21'},
 {'source_ref':'moncloa_2012','publisher_lineage':'Gobierno','birth_day':'1951-07-21'},
 {'source_ref':'congreso_2023','publisher_lineage':'Congreso','birth_day':'1951-07-29'},
 {'source_ref':'psoe_2017','publisher_lineage':'PSOE','birth_day':'1951-07-29'},
 {'source_ref':'psoe_2024','publisher_lineage':'PSOE','birth_day':'1951-07-29'},
]
class TestDOBConflict(unittest.TestCase):
 def test_01_real_source_assertion_conflict(self):
  r=audit(C17); self.assertTrue(r['has_conflict']);self.assertEqual(r['observed_values'],['1951-07-21','1951-07-29'])
 def test_02_editorial_lineage_count(self):
  self.assertEqual(audit(C17)['publisher_lineages'],3)
 def test_03_same_lineage_reuse_not_independent(self):
  self.assertEqual(audit(C17)['publisher_lineage_assertions']['Gobierno'],['1951-07-21'])
 def test_04_one_claim_no_certificate(self):
  r=audit(C17[:1]);self.assertFalse(r['has_conflict']);self.assertFalse(r['same_person_certified'])
 def test_05_impossible_birth_day_rejected(self):
  with self.assertRaisesRegex(ValueError,'INVALID_BIRTH_DAY'):audit([{**C17[0],'birth_day':'1951-02-30'}])
 def test_06_duplicate_source_ref_rejected(self):
  with self.assertRaisesRegex(ValueError,'DUPLICATE_SOURCE_REF'):audit([C17[0],C17[0]])
 def test_07_order_does_not_change_summary(self):
  self.assertEqual(audit(C17),audit(list(reversed(C17))))
 def test_08_source_lineage_unknown_rejected(self):
  with self.assertRaisesRegex(ValueError,'UNKNOWN_PUBLISHER_LINEAGE'):audit([{**C17[0],'publisher_lineage':''}])
 def test_09_no_date_of_publication_inferred(self):
  self.assertIsNone(audit(C17)['first_public_at'])
 def test_10_never_auto_same_or_different(self):
  r=audit(C17);self.assertFalse(r['different_person_certified']);self.assertFalse(r['person_link_automatically_resolved'])
 def test_11_no_real_scoring_or_release(self):
  r=audit(C17);self.assertFalse(r['real_person_scoring']);self.assertFalse(r['release_grade'])
if __name__=='__main__':unittest.main()
