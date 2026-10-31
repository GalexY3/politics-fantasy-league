"""R14: synthetic proofs that metadata cannot replace authorized originals."""
from dataclasses import replace
import unittest

from politics_fantasy.r14_documentary_frame_gate import (
    Frame, Asset, ArchiveHint, ProbeError, audit,
)

SRC="SYNTHETIC:SOURCE_YJPN"
DATASET="SYNTHETIC:YJPN_VCW8"
S="f"*64
ASOF="2026-11-01T00:00:00Z"


def frame(**changes):
    args=dict(institution="SYNTHETIC_GENCAT",family="SYNTHETIC_SAIP",
              regime="SYNTHETIC_2026",entry_stage="ALL_RECEIVED",
              unit="SYNTHETIC_REQUEST",first_day="2015-01-01T00:00:00Z",
              last_day="2026-12-31T00:00:00Z")
    args.update(changes)
    return Frame(**args)


def source(**changes):
    args=dict(source_id=SRC,publisher_id="SYNTHETIC:PUBLISHER_GENCAT",
              backend_id="SYNTHETIC:SAME_BACKEND",dataset_id=DATASET,frame=frame(),
              role="INITIAL_INTAKE",rights="GENERAL_TERMS_BIND_ON_ACCESS",
              locally_known_on="2026-10-31")
    args.update(changes)
    return Asset(**args)


def hint(**changes):
    args=dict(source_id=SRC,dataset_id=DATASET,
              described_at="2026-10-24T13:00:00Z",
              locally_known_on="2026-10-31")
    args.update(changes)
    return ArchiveHint(**args)


class R14DocumentaryGateTests(unittest.TestCase):
    def test_restore_edition_is_not_local_knowledge_before_audit(self):
        r=audit(entry=source(),comparator=None,
                hints=(hint(described_at="2026-10-10T13:00:00Z"),),
                as_of="2026-10-11T00:00:00Z")
        self.assertEqual(r["status"],"NO_DOCUMENTARY_ASSET_KNOWN_AS_OF")
        self.assertIsNone(r["listed_restore_hints"])
        self.assertIsNone(r["comparator_same_frame"])
        self.assertIsNone(r["first_public_at"])

    def test_date_precision_does_not_expose_on_audit_day(self):
        r=audit(entry=source(),comparator=None,hints=(hint(),),
                as_of="2026-10-31T23:59:59Z")
        self.assertIsNone(r["listed_restore_hints"])
        self.assertEqual(r["status"],"NO_DOCUMENTARY_ASSET_KNOWN_AS_OF")

    def test_future_comparator_is_not_leaked_through_earlier_hint(self):
        c=source(source_id="SYNTHETIC:COMPARATOR",role="CASE_FILE",
                 publisher_id="SYNTHETIC:DIFFERENT_PUBLISHER",
                 backend_id="SYNTHETIC:DIFFERENT_BACKEND",
                 locally_known_on="2026-11-03")
        early=audit(entry=source(),comparator=c,hints=(hint(),),as_of=ASOF)
        self.assertEqual(early["listed_restore_hints"],1)
        self.assertIsNone(early["comparator_same_frame"])
        self.assertIsNone(early["comparator_independent_backend"])
        late=audit(entry=source(),comparator=c,hints=(hint(),),
                   as_of="2026-11-04T00:00:00Z")
        self.assertTrue(late["comparator_same_frame"])
        self.assertIsNone(late["comparator_independent_backend"])
        self.assertTrue(late["comparator_declared_backend_ids_differ"])
        self.assertIsNone(late["independent_denominator"])

    def test_invalid_or_backdated_documentary_audit_rejected(self):
        with self.assertRaisesRegex(ProbeError,"LOCAL_AUDIT_DAY"):
            hint(locally_known_on="2026-10-31T09:00:00Z")
        with self.assertRaisesRegex(ProbeError,"EDITORIAL_EDITION_AFTER_LOCAL_AUDIT"):
            hint(locally_known_on="2026-10-09")

    def test_empty_hints_do_not_leak_source_or_counts(self):
        result=audit(entry=source(),comparator=None,hints=(),as_of=ASOF)
        self.assertEqual(result["status"],"NO_DOCUMENTARY_VERSION_HINT_KNOWN_AS_OF")
        for key in ("listed_restore_hints","comparator_same_frame",
                    "asset_license_sufficient","same_dataset_restore_hints"):
            self.assertIsNone(result[key])
        self.assertIsNone(result["first_public_at"])

    def test_restore_buttons_are_not_originals_or_first_public(self):
        h1=hint(described_at="2026-10-10T13:00:00Z")
        h2=hint(described_at="2026-10-24T13:00:00Z")
        r=audit(entry=source(),comparator=None,hints=(h1,h2),as_of=ASOF)
        self.assertEqual(r["listed_restore_hints"],2)
        self.assertTrue(r["same_dataset_restore_hints"])
        self.assertFalse(r["two_real_original_vintages_compared"])
        self.assertIsNone(r["independent_denominator"])
        self.assertFalse(r["R5_passed"])
        self.assertEqual(r["AB_cycles"],0)

    def test_earlier_cut_hides_future_restore_labels_and_any_diagnostic(self):
        r=audit(entry=source(),comparator=source(),hints=(hint(),),
                as_of="2026-10-23T23:00:00Z")
        self.assertIsNone(r["listed_restore_hints"])
        self.assertIsNone(r["comparator_same_frame"])
        self.assertIsNone(r["comparator_independent_backend"])
        self.assertIsNone(r["comparator_declared_backend_ids_differ"])
        self.assertIsNone(r["asset_license_sufficient"])
        self.assertNotIn(SRC,str(r))

    def test_shared_backend_is_not_independent_total(self):
        c=source(source_id="SYNTHETIC:COUNTER_A",role="CASE_FILE")
        r=audit(entry=source(),comparator=c,hints=(hint(),),as_of=ASOF)
        self.assertTrue(r["comparator_same_frame"])
        self.assertIsNone(r["comparator_independent_backend"])
        self.assertFalse(r["comparator_declared_backend_ids_differ"])
        self.assertTrue(r["publisher_claim_not_independent_total"])

    def test_same_publisher_not_independent_even_if_backend_text_differs(self):
        c=source(source_id="SYNTHETIC:COUNTER_B",role="CASE_FILE",
                 backend_id="SYNTHETIC:OTHER_BACKEND")
        r=audit(entry=source(),comparator=c,hints=(hint(),),as_of=ASOF)
        self.assertIsNone(r["comparator_independent_backend"])
        self.assertFalse(r["comparator_declared_backend_ids_differ"])

    def test_unrelated_institution_does_not_create_matching_frame(self):
        other=source(source_id="SYNTHETIC:CITYREAL_REGISTER",
                     publisher_id="SYNTHETIC:PUBLISHER_CITYREAL",
                     backend_id="SYNTHETIC:CITYREAL_BACKEND",
                     frame=frame(institution="SYNTHETIC_CIUDADREAL"),role="CASE_FILE")
        r=audit(entry=source(),comparator=other,hints=(hint(),),as_of=ASOF)
        self.assertFalse(r["comparator_same_frame"])
        self.assertIsNone(r["comparator_independent_backend"])
        self.assertTrue(r["comparator_declared_backend_ids_differ"])
        self.assertIsNone(r["independent_denominator"])

    def test_claimed_asset_rights_still_need_external_legal_and_R5_review(self):
        e=source(rights="ASSET_LICENSE_REVIEWED_NO_ACCEPTANCE")
        r=audit(entry=e,comparator=None,hints=(hint(),),as_of=ASOF)
        self.assertFalse(r["asset_license_sufficient"])
        self.assertFalse(r["rights_for_real_original_granted"])

    def test_same_sha_text_does_not_mean_authenticated_original(self):
        a=hint(original_sha256=S)
        b=hint(original_sha256=S,described_at="2026-10-10T13:00:00Z")
        r=audit(entry=source(),comparator=None,hints=(a,b),as_of=ASOF)
        self.assertFalse(r["two_real_original_vintages_compared"])
        self.assertFalse(r["originals_present"])

    def test_archive_hint_from_another_dataset_is_not_same_vintage(self):
        a=hint()
        b=hint(dataset_id="SYNTHETIC:DIFFERENT_SAIP",
               described_at="2026-10-10T13:00:00Z")
        with self.assertRaisesRegex(ProbeError,"MIXED_DATASET_ARCHIVE_HINTS"):
            audit(entry=source(),comparator=None,hints=(a,b),as_of=ASOF)

    def test_single_unrelated_restore_cannot_fake_asset_vintage(self):
        with self.assertRaisesRegex(ProbeError,"MIXED_DATASET_ARCHIVE_HINTS"):
            audit(entry=source(),comparator=None,
                  hints=(hint(dataset_id="SYNTHETIC:OTHER_DATASET"),),as_of=ASOF)

    def test_identical_restore_entries_do_not_count_twice(self):
        with self.assertRaisesRegex(ProbeError,"DUPLICATE_EDITORIAL_RESTORE_HINT"):
            audit(entry=source(),comparator=None,hints=(hint(),hint()),as_of=ASOF)

    def test_mixed_source_hints_are_rejected_not_fuzzy_merged(self):
        with self.assertRaisesRegex(ProbeError,"MIXED_SOURCE_ARCHIVE_HINTS"):
            audit(entry=source(),comparator=None,
                  hints=(hint(source_id="SYNTHETIC:OTHER_SOURCE"),),as_of=ASOF)

    def test_non_initial_intake_asset_cannot_define_entry_frame(self):
        with self.assertRaisesRegex(ProbeError,"INVALID_DOCUMENTARY_FRAME_INPUT"):
            audit(entry=source(role="TERMINAL_DECISION"),comparator=None,
                  hints=(hint(),),as_of=ASOF)

    def test_false_real_original_promotion_rejected(self):
        with self.assertRaisesRegex(ProbeError,"REAL_ASSET"):
            replace(source(),verified_original=True)
        with self.assertRaisesRegex(ProbeError,"REAL_ASSET"):
            replace(source(),independently_audited_population=True)
        with self.assertRaisesRegex(ProbeError,"RESTORE_HINT"):
            replace(hint(),original_bytes_authenticated=True)
        with self.assertRaisesRegex(ProbeError,"RESTORE_HINT"):
            replace(hint(),first_public_at="2020-01-01T00:00:00Z")

    def test_real_ids_and_invalid_rights_rejected(self):
        with self.assertRaises(ProbeError):
            source(source_id="REAL:PERSON_DOCUMENT_1")
        with self.assertRaises(ProbeError):
            source(rights="CC_BY_4_UNCONDITIONAL")
        with self.assertRaises(ProbeError):
            source(total_claim=True)

    def test_wrong_scope_or_window_rejected(self):
        with self.assertRaises(ProbeError):
            frame(institution="SENADO_REAL")
        with self.assertRaises(ProbeError):
            frame(first_day="2027-01-01T00:00:00Z")
        with self.assertRaises(ProbeError):
            frame(entry_stage="ALL_PAID_RESOLUTIONS")

    def test_unspecified_timezone_rejected(self):
        with self.assertRaisesRegex(ProbeError,"EXPLICIT_UTC"):
            audit(entry=source(),comparator=None,hints=(hint(),),as_of="2026-10-31")
        with self.assertRaisesRegex(ProbeError,"EXPLICIT_UTC"):
            hint(described_at="2026-10-31T12:00:00")


if __name__ == "__main__":
    unittest.main()
