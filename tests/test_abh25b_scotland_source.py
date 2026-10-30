"""ABH25B C05 synthetic adversarial parser gate, no original Scottish data."""
import json,unittest
from research.ABH25B_20261030.c05_scottish_petition_lifecycle import audit
def fake(ids=('PE-01','PE-02')):
    return json.dumps({"data":[{"type":"petition","pe_number":i,
        "attributes":{"status":"closed","closed_at":"2026-03-01T00:00:00Z",
        "opened_at":"2026-01-01T00:00:00Z","updated_at":None,
        "title":"THIS_PRIVATE_TEXT_MUST_NEVER_EXPORT","petitioner":"NO_EXPORT"}} for i in ids]}).encode()
class ScottishSource(unittest.TestCase):
    def test_missing_response_is_metadata_absence_not_institutional_absence(self):
        q=audit(fake())
        self.assertEqual(q['records'],2)
        self.assertEqual(q['date_field_nonempty_counts']['closed_at'],2)
        self.assertEqual(q['response_or_publication_related_field_presence'],{})
        self.assertNotIn('THIS_PRIVATE_TEXT',json.dumps(q))
        self.assertFalse(q['population_generalization'])
    def test_duplicate_identifier_rejected(self):
        with self.assertRaisesRegex(ValueError,'DUPLICATE_PETITION_KEY'):audit(fake(('PE-01','PE-01')))
    def test_html_and_bad_rows_rejected(self):
        with self.assertRaises(Exception):audit(b'<html>'+b'a'*130+b'</html>')
        with self.assertRaisesRegex(ValueError,'ROW_SHAPE'):
            audit(json.dumps({'data':[{'pe_number':'P1','attributes':'not-a-dict', 'padding':'SYNTHETIC'*20}]}).encode())
if __name__=='__main__':unittest.main()
