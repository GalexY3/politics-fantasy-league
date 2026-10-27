import unittest
from politics_fantasy.bocg_within_issue_pairs import pair_within_bocg as pair

A=["ANTUÑANO COLINA, Pablo","JÓDAR PÉREZ, Irene","RODRÍGUEZ HERRER, María Elvira"]
C=["ANTUÑANO COLINA, Pablo","RODRÍGUEZ HERRER, María Elvira","JÓDAR PÉREZ, Irene"]
def go(a=A,c=C,issuer="Congreso de los Diputados",issue="BOCG-15-D-390"):
    return pair(issuer=issuer,bulletin_id=issue,condition_names=a,credential_names=c)

class TestBocgMentionPairs(unittest.TestCase):
    def test_original_two_different_orderings_join_by_name_not_position(self):
        r=go()
        self.assertEqual(r["status"],"SAME_DOCUMENT_MENTIONS_MATCHED")
        self.assertEqual(r["paired_ordinals_condition_to_credential"],[[1,1],[3,2],[2,3]])
    def test_accent_variants_may_match_within_issue(self):
        r=go(c=["Antunano Colina, Pablo","Rodriguez Herrer, Maria Elvira","Jodar Perez, Irene"])
        self.assertEqual(r["count"],3)
    def test_duplicated_person_label_denied(self):
        self.assertEqual(go(c=[C[0],C[0],C[2]])["status"],"AMBIGUOUS_REPEATED_NAME")
    def test_missing_credential_mention_denied(self):
        self.assertEqual(go(c=C[:2])["status"],"MISSING_OR_EXTRA_SOURCE_MENTION")
    def test_unknown_source_scope_denied(self):
        with self.assertRaisesRegex(ValueError,"UNSUPPORTED_SOURCE_SCOPE"):
            go(issue="BOCG-15-D-999")
    def test_no_canonical_person_claim(self):
        r=go()
        self.assertFalse(r["same_person_across_documents_certified"])
        self.assertFalse(r["real_person_scoring"])
        self.assertFalse(r["release_grade"])
        self.assertIsNone(r["first_public_at"])
    def test_empty_lists_not_certifiable(self):
        self.assertNotEqual(go(a=[],c=[])["status"],"SAME_DOCUMENT_MENTIONS_MATCHED")
if __name__=="__main__": unittest.main()
