"""ABH25B C01/C02 adversarial synthetic parser tests — no original outcomes."""
import json,unittest
from research.ABH25B_20261030.c01_uk_response_latency import PAGES,summarize_pages
from research.ABH25B_20261030.c02_canada_schema import inspect_xml

def demo_page(pid,with_response=True, inversion=False):
    attrs={"state":"closed","signature_count":12500,
      "response_threshold_reached_at":"2026-01-01T00:00:00Z",
      "government_response_at":"2025-12-28T00:00:00Z" if inversion else ("2026-01-22T00:00:00Z" if with_response else None),
      "government_response":{"summary":"SYNTHETIC"} if with_response else None,
      "debate_outcome_at":None}
    return json.dumps({"data":[{"id":str(pid),"type":"petition","attributes":attrs}]}).encode()

class OfficialParserControls(unittest.TestCase):
    def test_uk_lag_21_day_boundary_and_fixed_sample(self):
        raw={p:demo_page(p) for p in PAGES}
        result=summarize_pages(raw)
        self.assertEqual(result["n"],4)
        self.assertEqual(result["lag_gt14_le21"],4)
        self.assertEqual(result["lag_gt21"],0)
        self.assertEqual(result["median_days"],21)
        self.assertTrue(result["no_titles_or_person_data_exported"])
        with self.assertRaisesRegex(ValueError,"UNEXPECTED_SELECTED_PAGES"):
            summarize_pages({PAGES[0]:raw[PAGES[0]]})
    def test_uk_nonresponse_not_zero_or_21_day_compliance(self):
        raw={p:demo_page(p) for p in PAGES}
        raw[PAGES[-1]]=demo_page(PAGES[-1],False)
        v=summarize_pages(raw)
        self.assertEqual(v["eligible_lags"],3)
        self.assertEqual(v["threshold_only"],1)
        self.assertEqual(v["government_response_at_present"],3)
    def test_uk_duplicate_page_ids_refused(self):
        raw={p:demo_page(PAGES[0]) for p in PAGES}
        with self.assertRaisesRegex(ValueError,"CROSS_PAGE_DUPLICATE"):
            summarize_pages(raw)
    def test_uk_inversions_reported_not_silently_corrected(self):
        raw={p:demo_page(p,inversion=(i==0)) for i,p in enumerate(PAGES)}
        v=summarize_pages(raw)
        self.assertEqual(v["inverted_response_dates"],1)
        self.assertEqual(v["eligible_lags"],3)
    def test_canada_schema_no_identity_export_and_no_response_assumption(self):
        sample=b'<?xml version="1.0"?><Petitions><Petition><PetitionNumber>123</PetitionNumber><Status>Certified</Status><SignatureCount>456</SignatureCount><PetitionerName>Alice</PetitionerName></Petition></Petitions>'
        r=inspect_xml(sample)
        self.assertEqual(r["xml_root"],"Petitions")
        self.assertTrue(r["has_petition_or_signature_field"])
        self.assertFalse(r["has_explicit_response_field"])
        self.assertNotIn("Alice",json.dumps(r))
    def test_canada_html_and_entities_refused(self):
        with self.assertRaisesRegex(ValueError,"HTML_NOT_XML"):
            inspect_xml(b'<html>'+b'a'*120+b'</html>')
        with self.assertRaisesRegex(ValueError,"DOCTYPE_OR_ENTITY_NOT_ALLOWED"):
            inspect_xml(b'<!DOCTYPE foo [<!ENTITY ex "bad">]><root>'+b'a'*120+b'</root>')
if __name__=="__main__":
    unittest.main()
