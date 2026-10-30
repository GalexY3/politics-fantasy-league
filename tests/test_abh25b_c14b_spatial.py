import json,unittest
from research.ABH25B_20261030.c14b_uk_geographic_signatures import select_id,evaluate
class SpatialControls(unittest.TestCase):
 def page(self):
  return json.dumps({'data':[{'id':str(n),'attributes':{'state':'closed'}} for n in range(50,75)]}).encode()
 def test_minimum_original_id_selection_frozen(self):
  self.assertEqual(select_id(self.page()),50)
 def test_hhi_and_null_person_data(self):
  raw=json.dumps({'data':{'id':'50','attributes':{'signature_count':100,
    'signatures_by_constituency':[{'name':'Named Member is NOT signer','signature_count':75},
                                  {'name':'X','signature_count':25}]}}}).encode()
  x=evaluate(raw,50)
  self.assertAlmostEqual(x['hhi_raw_signature_shares'],0.625)
  self.assertEqual(x['observed_constituency_signatures'],100)
  self.assertNotIn('Named Member',str(x))
  self.assertTrue(x['not_MP_or_party_support'])
 def test_bad_detail_or_missing_counts_fail(self):
  raw=json.dumps({'data':{'id':'50','attributes':{'signatures_by_constituency':[]}}}).encode()
  with self.assertRaisesRegex(ValueError,'NO_OFFICIAL_CONSTITUENCY_BREAKDOWN'):
   evaluate(raw,50)
if __name__=='__main__':unittest.main()
