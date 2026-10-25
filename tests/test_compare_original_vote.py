import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'scripts'))
from compare_original_vote import summarize_official,compare
class OfficialStructuralTests(unittest.TestCase):
    def blob(self):
        return json.dumps({'data':{'totales':{'afavor':1,'enContra':0,'abstenciones':1,'noVotan':0},'votaciones':[{'voto':'Sí','diputado':'X'},{'voto':'Abstención','diputado':'Y'}]}}).encode()
    def test_official_same_nominal(self):
        r=summarize_official(self.blob());self.assertTrue(r['official_nominal_matches_aggregate'])
        self.assertNotIn('diputado',json.dumps(r))
    def test_secondary_mismatch_detected(self):
        r=compare(self.blob(),{'id':'id','totales':{'si':1,'no':1,'abstencion':0,'noVota':0}})
        self.assertFalse(r['secondary_counts_match_official'])
    def test_unknown_vote_label_fails(self):
        b=self.blob().replace(b'Abstenci\\u00f3n',b'OTRA')
        self.assertRaises(ValueError,summarize_official,b)
    def test_unknown_schema_fails_closed(self):
        self.assertRaises(ValueError,summarize_official,b'{}')
