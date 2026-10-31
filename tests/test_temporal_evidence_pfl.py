"""Adversarial, entirely synthetic tests. No political-person data are imported."""
from __future__ import annotations

import dataclasses
import json
import tempfile
import unittest
from pathlib import Path

from politics_fantasy.temporal_evidence import (
    ContractError, FileReceipt, SourceRef, TemporalLedger, TemporalRecord,
    audit_real_documentary_only, read_json_bound, sha256_file,
)

T0 = "2026-01-01T00:00:00Z"
T1 = "2026-02-01T00:00:00Z"
T2 = "2026-03-01T00:00:00Z"
T3 = "2026-04-01T00:00:00Z"
T4 = "2026-05-01T00:00:00Z"
ROOT = Path(__file__).resolve().parent
ACTOR = SourceRef("TEST", "institucion", "organismo-a")
ACTOR2 = SourceRef("TEST", "institucion", "organismo-b")
EVENT = SourceRef("TEST", "acontecimiento", "evento-uno")
OTHER = SourceRef("TEST2", "institucion", "organismo-a")


class TemporalTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "fixture.json"
        self.path.write_text('{"synthetic":true}\n', encoding="utf-8")
        self.receipt = FileReceipt.check_local(
            self.path, source_id="TEST", captured_at=T1, origin="SYNTHETIC",
            rights_state="SYNTHETIC")
        self.registry = TemporalLedger()
        self.registry.register_source(self.receipt)

    def make(self, **override):
        vals = {
            "kind": "ENTITY", "source_id": "TEST", "source_record_id": "A",
            "revision": "v1", "source_sha256": self.receipt.sha256,
            "subject": ACTOR, "object": None, "predicate": "DOCUMENTED",
            "valid_from": T0, "valid_to": None, "first_public_at": T1,
            "recorded_at": T1, "observation_state": "OBSERVED", "value": "record",
        }
        vals.update(override)
        return TemporalRecord(**vals)

    def add_nodes(self):
        self.registry.add(self.make())
        self.registry.add(self.make(source_record_id="B", subject=ACTOR2))
        self.registry.add(self.make(source_record_id="C", subject=EVENT,
                                    kind="EVENT", valid_from=T0))

    def test_namespaced_reference_no_name_match(self):
        self.assertNotEqual(ACTOR, OTHER)
        self.assertNotEqual(ACTOR2, ACTOR)
        self.assertEqual(SourceRef.parse(ACTOR.wire()), ACTOR)

    def test_identity_bad_reference(self):
        with self.assertRaisesRegex(ContractError, "BAD_NAMESPACED"):
            SourceRef.parse(["only", "two"])
        with self.assertRaisesRegex(ContractError, "INVALID_LOCAL_ID"):
            SourceRef("X", "Y", "injected name")

    def test_foreign_node_identity_cannot_be_issued_by_wrong_source(self):
        with self.assertRaisesRegex(ContractError, "SOURCE_ISSUED_NODE_SCOPE_MISMATCH"):
            self.make(subject=OTHER)

    def test_file_hash_read_only_and_expected(self):
        self.assertEqual(sha256_file(self.path), self.receipt.sha256)
        with self.assertRaisesRegex(ContractError, "SOURCE_DIGEST_MISMATCH"):
            FileReceipt.check_local(self.path, source_id="TEST", captured_at=T1,
                                    origin="SYNTHETIC", rights_state="SYNTHETIC",
                                    expected_sha256="0" * 64)

    def test_real_source_cannot_self_claim_verified(self):
        with self.assertRaisesRegex(ContractError, "UNATTESTED_RIGHTS_ESCALATION"):
            FileReceipt.check_local(self.path, source_id="TEST", captured_at=T1,
                                    origin="DOCUMENTED_REAL_UNADJUDICATED",
                                    rights_state="OPEN_LICENSE_VERIFIED")
        with self.assertRaisesRegex(ContractError, "UNATTESTED_RIGHTS_ESCALATION"):
            FileReceipt.check_local(self.path, source_id="TEST", captured_at=T1,
                                    origin="SYNTHETIC", rights_state="CATALOG_LICENSE_ONLY")

    def test_unregistered_hash_rejected(self):
        with self.assertRaisesRegex(ContractError, "UNREGISTERED_SOURCE_DIGEST"):
            self.registry.add(self.make(source_sha256="a" * 64))

    def test_captured_after_record_is_rejected(self):
        with self.assertRaisesRegex(ContractError, "RECORD_PREDATES"):
            self.registry.add(self.make(recorded_at=T0, first_public_at=T0))

    def test_idempotent_identity_source_revision(self):
        row = self.make()
        self.assertEqual(self.registry.add(row), "NEW_REVISION")
        self.assertEqual(self.registry.add(row), "DEDUPLICATED_IDENTICAL")
        self.assertEqual(self.registry.manifest()["record_revision_count"], 1)

    def test_conflicting_duplicate_same_source_event_revision(self):
        self.registry.add(self.make())
        with self.assertRaisesRegex(ContractError, "SAME_SOURCE_EVENT_REVISION_CONFLICT"):
            self.registry.add(self.make(value="changed"))

    def test_different_source_same_record_id_not_deduplicated(self):
        other_file = Path(self.tmp.name) / "other.json"
        other_file.write_text('{"synthetic":"other"}', encoding="utf-8")
        receipt = FileReceipt.check_local(
            other_file, source_id="TEST2", captured_at=T1,
            origin="SYNTHETIC", rights_state="SYNTHETIC")
        self.registry.register_source(receipt)
        self.registry.add(self.make())
        self.registry.add(self.make(source_id="TEST2", source_sha256=receipt.sha256,
                                    subject=OTHER))
        self.assertEqual(len(self.registry.snapshot(as_of=T1).records), 2)

    def test_late_archive_blocks_future_ingestion(self):
        self.registry.add(self.make(first_public_at=T0, recorded_at=T2))
        self.assertEqual(len(self.registry.snapshot(as_of=T1).records), 0)
        self.assertEqual(len(self.registry.snapshot(as_of=T2).records), 1)

    def test_unknown_first_publication_is_not_retroinferred(self):
        self.registry.add(self.make(first_public_at=None))
        snap = self.registry.snapshot(as_of=T4)
        self.assertEqual(snap.blocked_unknown_publication, 1)
        self.assertEqual(snap.state_of("ENTITY", "TEST", "A"), "NOT_OBSERVED")

    def test_revision_chronology_not_lexicographic(self):
        self.registry.add(self.make(revision="z-old", first_public_at=T1, recorded_at=T3))
        self.registry.add(self.make(revision="a-new", first_public_at=T2, recorded_at=T2,
                                    value="corrected"))
        snap = self.registry.snapshot(as_of=T4)
        self.assertEqual(snap.records[0].value, "corrected")
        self.assertEqual(snap.records[0].revision, "a-new")

    def test_tied_published_revisions_fail_closed(self):
        self.registry.add(self.make(revision="r1", first_public_at=T1))
        self.registry.add(self.make(revision="r2", first_public_at=T1))
        with self.assertRaisesRegex(ContractError, "AMBIGUOUS_SAME_TIME"):
            self.registry.snapshot(as_of=T2)

    def test_revision_selected_before_valid_filter(self):
        self.registry.add(self.make(valid_from=T0, revision="r1", first_public_at=T1))
        self.registry.add(self.make(valid_from=T2, revision="r2",
                                    first_public_at=T3, recorded_at=T3))
        # New correction removes the previously assumed validity in January.
        snap = self.registry.snapshot(as_of=T4, valid_at=T1)
        self.assertEqual(snap.state_of("ENTITY", "TEST", "A"), "NOT_OBSERVED")
        self.assertEqual(len(self.registry.snapshot(as_of=T2, valid_at=T1).records), 1)

    def test_role_referential_integrity_asof(self):
        self.add_nodes()
        relation = self.make(kind="ROLE", source_record_id="R",
                             subject=ACTOR, object=EVENT, predicate="PUBLIC_SPEAKER")
        self.registry.add(relation)
        self.assertEqual(len(self.registry.snapshot(as_of=T2).records), 4)

    def test_role_with_unobserved_endpoint_not_visible(self):
        self.registry.add(self.make())
        self.registry.add(self.make(kind="ROLE", source_record_id="R",
                                    subject=ACTOR, object=EVENT, predicate="PUBLIC_SPEAKER"))
        snap = self.registry.snapshot(as_of=T2)
        self.assertEqual(snap.blocked_unresolved_reference, 1)
        self.assertEqual(len(snap.records), 1)

    def test_endpoint_capture_later_blocks_role_in_historical_cutoff(self):
        self.registry.add(self.make())
        self.registry.add(self.make(kind="EVENT", source_record_id="E", subject=EVENT,
                                    valid_from=T1, first_public_at=T2, recorded_at=T2))
        self.registry.add(self.make(kind="ROLE", source_record_id="R", subject=ACTOR,
                                    object=EVENT, predicate="SPEAKER"))
        before = self.registry.snapshot(as_of=T1)
        after = self.registry.snapshot(as_of=T3)
        self.assertEqual(len(before.records), 1)
        self.assertEqual(len(after.records), 3)

    def test_relation_cross_source_unverified_identity_link_denied(self):
        with self.assertRaisesRegex(ContractError, "IDENTITY_OR_PRIVATE_MEMBERSHIP"):
            self.make(kind="RELATION", object=OTHER, predicate="SAME_AS")
        with self.assertRaisesRegex(ContractError, "IDENTITY_OR_PRIVATE_MEMBERSHIP"):
            self.make(kind="RELATION", object=OTHER,
                      predicate="MEMBER_OF_POLITICAL_PARTY")

    def test_historical_role_half_open_interval(self):
        self.add_nodes()
        self.registry.add(self.make(kind="ROLE", source_record_id="R",
                                    subject=ACTOR, object=ACTOR2,
                                    predicate="HOLDS_PUBLIC_ROLE",
                                    valid_from=T0, valid_to=T2))
        self.assertEqual(len(self.registry.snapshot(as_of=T1).records), 4)
        self.assertEqual(len(self.registry.snapshot(as_of=T2).records), 3)

    def test_state_unknown_is_not_zero(self):
        self.registry.add(self.make(observation_state="UNKNOWN", value=None))
        self.assertEqual(self.registry.snapshot(as_of=T2).state_of("ENTITY", "TEST", "A"),
                         "UNKNOWN")
        self.assertEqual(self.registry.snapshot(as_of=T2).state_of("ENTITY", "TEST", "X"),
                         "NOT_OBSERVED")

    def test_explicit_zero_requires_both_numeric_and_basis(self):
        with self.assertRaisesRegex(ContractError, "UNSUPPORTED_ZERO_BASIS"):
            self.make(observation_state="EXPLICIT_ZERO", value=0)
        with self.assertRaisesRegex(ContractError, "UNSUPPORTED_VALUE_TYPE"):
            self.make(observation_state="EXPLICIT_ZERO", value=False,
                      zero_basis="SOURCE_EXPLICIT_NUMERIC_ZERO")
        self.registry.add(self.make(observation_state="EXPLICIT_ZERO", value=0,
                                    zero_basis="SOURCE_EXPLICIT_NUMERIC_ZERO"))
        self.assertEqual(self.registry.snapshot(as_of=T1).state_of("ENTITY", "TEST", "A"),
                         "EXPLICIT_ZERO")

    def test_unknown_may_not_carry_false_numeric_data(self):
        with self.assertRaisesRegex(ContractError, "UNKNOWN_MUST_HAVE_NULL_VALUE"):
            self.make(observation_state="NOT_OBSERVED", value=0)

    def test_future_event_cannot_be_passed_off_as_observed(self):
        with self.assertRaisesRegex(ContractError, "OBSERVED_EVENT_PUBLIC_BEFORE_OCCURRED"):
            self.make(kind="EVENT", valid_from=T3, first_public_at=T1)
        self.make(kind="EVENT", valid_from=T3, first_public_at=T1,
                  predicate="SCHEDULED_MEETING")

    def test_non_aware_dates_rejected(self):
        with self.assertRaisesRegex(ContractError, "NAIVE_VALID_FROM"):
            self.make(valid_from="2026-01-01T00:00:00")
        with self.assertRaisesRegex(ContractError, "NAIVE_AS_OF"):
            self.registry.snapshot(as_of="2026-01-01T00:00:00")

    def test_event_revision_window_cannot_resurrect_prior_revision(self):
        self.registry.add(self.make(kind="EVENT", valid_from=T0, revision="old",
                                    source_record_id="E"))
        self.registry.add(self.make(kind="EVENT", valid_from=T3, revision="new",
                                    source_record_id="E", first_public_at=T4, recorded_at=T4))
        self.assertEqual(len(self.registry.snapshot(as_of=T4,
                                                    event_start=T0, event_end=T2).records), 0)

    def test_valid_at_future_disallowed(self):
        with self.assertRaisesRegex(ContractError, "VALID_AT_AFTER_KNOWLEDGE_CUTOFF"):
            self.registry.snapshot(as_of=T1, valid_at=T2)

    def test_deterministic_manifest_and_not_release_grade(self):
        self.registry.add(self.make())
        manifest = self.registry.manifest()
        self.assertEqual(manifest, self.registry.manifest())
        self.assertEqual(len(manifest["canonical_contract_sha256"]), 64)
        self.assertFalse(manifest["real_source_ingest_admitted"])
        self.assertFalse(manifest["release_grade"])
        self.assertFalse(manifest["historical_publication_authenticated"])

    def test_manifest_is_independent_of_insert_order(self):
        a, b = self.make(), self.make(source_record_id="B", subject=ACTOR2)
        self.registry.add(a)
        self.registry.add(b)
        other = TemporalLedger()
        other.register_source(self.receipt)
        other.add(b)
        other.add(a)
        self.assertEqual(self.registry.manifest()["canonical_contract_sha256"],
                         other.manifest()["canonical_contract_sha256"])

    def test_duplicate_json_object_keys_rejected(self):
        p = Path(self.tmp.name) / "dupe.json"
        p.write_text('{"x":1,"x":2}', encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "INVALID_LOCAL_JSON"):
            read_json_bound(p)

    def test_nonfinite_json_and_values_rejected(self):
        p = Path(self.tmp.name) / "nan.json"
        p.write_text('{"number":NaN}', encoding="utf-8")
        with self.assertRaisesRegex(ContractError, "INVALID_LOCAL_JSON"):
            read_json_bound(p)
        with self.assertRaisesRegex(ContractError, "NON_FINITE_VALUE"):
            self.make(value=float("inf"))

    def test_real_documentary_smoke_is_blocked(self):
        smoke = audit_real_documentary_only(
            self.path, source_id="ES_LOCAL_VERSION", captured_at=T2)
        self.assertEqual(smoke["status"], "BLOCKED_REAL_INGEST")
        self.assertFalse(smoke["historical_asof_ready"])
        self.assertEqual(smoke["records_imported"], 0)
        self.assertEqual(smoke["persons_exported"], 0)


if __name__ == "__main__":
    unittest.main()
