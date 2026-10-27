import unittest
from xml.etree import ElementTree as ET
from politics_fantasy.source_original_senate_qa import audit_original_senate_session as audit

def fixture(label="NO VOTAN", totals=None, vote_day="08-OCT-2025"):
    t = {"tot_afirmativos":0, "tot_negativos":0, "tot_abstenciones":0,
         "tot_novotan":1, "tot_presentes":1, "tot_ausentes":0}
    if totals: t.update(totals)
    texts = "".join(f"<{key}>{value}</{key}>" for key,value in t.items())
    return (f"<main><sesion><fecha_sesion>07/10/2025</fecha_sesion>"
            f"<votacion><fecha_v>{vote_day}</fecha_v>{texts}"
            f"<resultado><VotoSenador><voto>{label}</voto></VotoSenador></resultado>"
            f"<ausentes/></votacion></sesion></main>").encode()

class SenateOriginalTests(unittest.TestCase):
    def test_plural_no_votan_accepted(self):
        r=audit(fixture())
        self.assertEqual(r["nominal_rows_verified"],1)
        self.assertEqual(r["vote_days"],["2025-10-08"])
    def test_singular_no_vota_rejected(self):
        with self.assertRaisesRegex(ValueError,"UNKNOWN_OFFICIAL_SENATE_LABEL"):
            audit(fixture(label="NO VOTA"))
    def test_wrong_presentes_rejected(self):
        with self.assertRaisesRegex(ValueError,"SENATE_VOTE_TOTAL_MISMATCH"):
            audit(fixture(totals={"tot_presentes":2}))
    def test_wrong_nonvoters_rejected(self):
        with self.assertRaisesRegex(ValueError,"SENATE_VOTE_TOTAL_MISMATCH"):
            audit(fixture(totals={"tot_novotan":0}))
    def test_missing_session_rejected(self):
        with self.assertRaisesRegex(ValueError,"MISSING_SESSION"):
            audit(b"<main/>")
    def test_bad_xml_rejected(self):
        with self.assertRaisesRegex(ValueError,"INVALID_XML"):
            audit(b"<main>")
    def test_no_first_publication_or_person_identity(self):
        r=audit(fixture())
        self.assertFalse(r["first_public_at_verified"])
        self.assertFalse(r["historical_person_ID_certified"])
        self.assertFalse(r["real_person_scoring"])
    def test_all_twelve_spanish_month_abbreviations(self):
        abbreviations=["ENE","FEB","MAR","ABR","MAY","JUN","JUL","AGO","SEP","OCT","NOV","DIC"]
        for index,abbr in enumerate(abbreviations,1):
            with self.subTest(month=abbr):
                result=audit(fixture(vote_day=f"08-{abbr}-2025"))
                self.assertEqual(result["vote_days"],[f"2025-{index:02d}-08"])
    def test_missing_vote_denied(self):
        with self.assertRaisesRegex(ValueError,"MISSING_VOTES"):
            audit(b"<main><sesion><fecha_sesion>07/10/2025</fecha_sesion></sesion></main>")

if __name__=="__main__":
    unittest.main()
