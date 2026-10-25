import sys
import unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from audit_pleno_full import audit,git_blob_sha1

class AuditPlenoFullTests(unittest.TestCase):
    def fixture(self):
        return [{'id':'s1-v001','fecha':'2026-01-01','sesion':1,'totales':{'si':2,'no':1,'abstencion':0,'noVota':0},'votos':{'S':'1','N':'2'},'grupos':{'G1':[2,1,0,0]}},
                {'id':'s1-v002','fecha':'2026-01-01','sesion':1,'totales':{'si':1,'no':2,'abstencion':0,'noVota':0},'votos':{'S':'1','N':'2 3'},'grupos':{'G1':[1,2,0,0]}}]
    def test_coverage_and_year(self):
        r=audit(self.fixture());self.assertEqual(r['votes'],2);self.assertEqual(r['sessions'],1);self.assertEqual(r['gap'],1);self.assertEqual(r['majority_flips'],1)
    def test_duplicate_vote_id_refused(self):
        v=self.fixture();v[1]['id']=v[0]['id'];self.assertRaisesRegex(ValueError,'Duplicate',audit,v)
    def test_excess_nominal_refused(self):
        v=self.fixture();v[0]['votos']['S']='1 3 4';self.assertRaisesRegex(ValueError,'exceeds',audit,v)
    def test_group_mismatch_flagged(self):
        v=self.fixture();v[0]['grupos']['G1']=[1,1,0,0];self.assertEqual(audit(v)['group_total_mismatches'],['s1-v001'])
    def test_duplicate_codes_flagged(self):
        v=self.fixture();v[0]['votos']['S']='1 2';v[0]['votos']['N']='2';self.assertIn('s1-v001',audit(v)['duplicated_nominal_codes_in_vote'])
    def test_git_blob_sha(self):
        self.assertEqual(git_blob_sha1(b'test\n'),'9daeafb9864cf43055ae93beb0afd6c7d144bfa4')

if __name__=='__main__':unittest.main()
