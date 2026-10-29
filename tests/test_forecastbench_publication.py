"""Offline tests: conservative source-publication boundary, no humans or network."""
from __future__ import annotations
import unittest
from politics_fantasy import forecastbench_publication as f

class OriginalPublicationTests(unittest.TestCase):
    def test_01_git_hash_known_vector(self):
        self.assertEqual(f.git_blob_sha1(b"abc"),"f2ba8f84ab5c1bce84a7b441cb1959cfc7093b7f")
    def test_02_oct1_is_unavailable_even_if_event_date_precedes_it(self):
        d=f.select_verified_checkpoint("2026-10-01T23:59:59Z")
        self.assertEqual(d["status"],"NO_ORIGINAL_PUBLIC_RESOLUTION_SET_AT_CUTOFF")
        self.assertEqual(d["historical_outcomes_scored"],0)
        self.assertTrue(d["not_a_zero_outcome_claim"])
    def test_03_oct6_is_unavailable(self):
        self.assertEqual(f.select_verified_checkpoint("2026-10-06T23:59:59Z")["status"],
                         "NO_ORIGINAL_PUBLIC_RESOLUTION_SET_AT_CUTOFF")
    def test_04_before_first_commit_even_same_day_unavailable(self):
        self.assertEqual(f.select_verified_checkpoint("2026-10-07T07:19:28Z")["status"],
                         "NO_ORIGINAL_PUBLIC_RESOLUTION_SET_AT_CUTOFF")
    def test_05_exact_first_publication_instant_unverified_as_checkpoint(self):
        self.assertEqual(f.select_verified_checkpoint("2026-10-07T07:19:29Z")["status"],
                         "NO_VERIFIED_EXACT_CHECKPOINT")
    def test_06_oct8_pins_first_public_snapshot(self):
        x=f.select_verified_checkpoint("2026-10-08T00:00:00Z")
        self.assertEqual(x["status"],"PINNED_PUBLIC_SNAPSHOT_METADATA")
        self.assertEqual(x["source_commit"],f.FIRST_PUBLIC_RESOLUTION_COMMIT)
        self.assertEqual(x["resolution_blob_sha1"],"0b67cfec67fad4b23899e8e48c6ca3a034344edc")
        self.assertFalse(x["per_record_first_public_at"])
    def test_07_oct29_pins_later_source_file(self):
        x=f.select_verified_checkpoint("2026-10-29T16:00:00Z")
        self.assertEqual(x["source_commit"],f.LATER_RESOLUTION_COMMIT)
        self.assertEqual(x["resolution_blob_sha1"],"b2ee53f09407e2b555668f66e286073ace6d5fce")
        self.assertFalse(x["publisher_authentication"])
    def test_08_intervening_dates_fail_closed(self):
        self.assertEqual(f.select_verified_checkpoint("2026-10-20T12:00:00Z")["status"],
                         "NO_VERIFIED_EXACT_CHECKPOINT")
    def test_09_invalid_timezones_formats_rejected(self):
        for x in ("2026-10-08","2026-10-08T02:00:00+02:00","2026-10-36T00:00:00Z","2026-10-08T00:00Z"):
            with self.subTest(x=x), self.assertRaisesRegex(ValueError,"CANONICAL_UTC_REQUIRED"):
                f.select_verified_checkpoint(x)
    def test_10_no_fake_blob_can_create_genuine_historical_outcome(self):
        with self.assertRaisesRegex(ValueError,"SOURCE_SNAPSHOT_GIT_BLOB_MISMATCH"):
            f.audit_verified_public_snapshot(b'{"questions":[]}',b'{"resolutions":[]}',
                                             as_of_instant="2026-10-08T00:00:00Z")
    def test_11_no_null_or_bytearray_bypass(self):
        for x in (b"",bytearray(b"abc"),"abc"):
            with self.assertRaisesRegex(ValueError,"BOUNDED_ORIGINAL_BYTES_REQUIRED"):
                f.git_blob_sha1(x)
    def test_12_no_self_attested_overrides(self):
        self.assertNotIn("verified",f.audit_verified_public_snapshot.__code__.co_varnames)
        self.assertFalse(f.select_verified_checkpoint("2026-10-08T00:00:00Z")["publisher_authentication"])
    def test_13_cutoff_without_source_is_invalid_not_zero_resolutions(self):
        with self.assertRaisesRegex(ValueError,"NO_ORIGINAL_PUBLIC_RESOLUTION_SET_AT_CUTOFF"):
            f.audit_verified_public_snapshot(b"abc",b"def",as_of_instant="2026-10-01T23:59:59Z")
    def test_14_manifest_not_writable(self):
        with self.assertRaises(TypeError):
            f._CHECKPOINTS["2026-10-08T00:00:00Z"]=("fake","fake","fake")
    def test_15_strict_zero_moment_boundary(self):
        d=f.select_verified_checkpoint("2026-10-07T07:19:29Z")
        self.assertEqual(d["scope"],"PUBLIC_GITHUB_REPOSITORY_ONLY")

if __name__=="__main__":
    unittest.main(verbosity=2)
