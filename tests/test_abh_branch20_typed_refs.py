"""AB-H C04 focused offline acceptance; fixture values from official XIV/XV URLs.
These tests do not certify that two historical records belong to the same person.
"""
import unittest
from politics_fantasy.typed_refs import (
    InstitutionalRef, same_institutional_record, certify_same_person, scoring_enabled
)


class ScopedRefContract(unittest.TestCase):
    def test_same_full_namespace(self):
        a=InstitutionalRef("Congreso","XIV","diputado","187")
        self.assertTrue(same_institutional_record(a, InstitutionalRef("Congreso","XIV","diputado","187")))

    def test_same_number_different_legislature(self):
        self.assertFalse(same_institutional_record(
            InstitutionalRef("Congreso","XIV","diputado","187"),
            InstitutionalRef("Congreso","XV","diputado","187")))

    def test_same_number_different_family(self):
        self.assertFalse(same_institutional_record(
            InstitutionalRef("Congreso","XV","diputado","408"),
            InstitutionalRef("Congreso","XV","declaracion","408")))

    def test_blank_family_rejected(self):
        with self.assertRaises(ValueError):
            InstitutionalRef("Congreso","XV","","312")

    def test_caller_forgery_cannot_certify_person(self):
        self.assertFalse(certify_same_person(
            InstitutionalRef("Congreso","XIV","diputado","187"),
            InstitutionalRef("Congreso","XV","diputado","312"),
            attested_crosswalk={"approved":True,"signature":"fake"}))

    def test_scoring_is_off(self):
        self.assertFalse(scoring_enabled(InstitutionalRef("Congreso","XV","diputado","312")))


if __name__ == "__main__":
    unittest.main()
