import json,unittest
from research.ABH25B_20261030.c09_c16_institutional_pages import parse,SOURCES
def sample(id='one',status='closed',n=1000):
    return json.dumps({'data':[{'id':id,'attributes':{
        'state':status,'signature_count':n,'response_threshold_reached_at':None,
        'government_response_at':None,'debate_outcome_at':None,
        'title':'private subject name must never appear','creator_name':'PRIVATE TEST'}}]}).encode()
class StageControls(unittest.TestCase):
    def test_missing_response_not_fabricated_and_pii_not_leaked(self):
        x=parse('C13',sample())
        self.assertEqual(x['government_response_date_present'],0)
        self.assertEqual(x['signatures_ge250'],1)
        self.assertNotIn('PRIVATE TEST',str(x));self.assertNotIn('private subject name',str(x))
    def test_distinct_status_does_not_equal_responded(self):
        x=parse('C16',sample(status='rejected',n=50000))
        self.assertEqual(x['state_counts'],{'rejected':1})
        self.assertEqual(x['government_response_date_present'],0)
    def test_bad_missing_ids_and_unsupported_data_fail(self):
        duplicated={'data':[{'id':'D','attributes':{'state':'closed'}},
                             {'id':'D','attributes':{'state':'closed'}}]}
        with self.assertRaisesRegex(ValueError,'DUPLICATE_ID'):
            parse('C09',json.dumps(duplicated).encode())
        with self.assertRaisesRegex(ValueError,'SCHEMA_NO_DATA_LIST'):
            parse('C09',json.dumps({'bad':'schema','padding':'x'*90}).encode())
    def test_arithmetic_threshold_boundary(self):
        x=parse('C10',sample(n=250))
        self.assertEqual(x['signatures_ge250'],1)
        self.assertEqual(x['signatures_ge10000'],0)
if __name__=='__main__':unittest.main()
