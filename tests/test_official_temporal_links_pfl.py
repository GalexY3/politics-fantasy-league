"""Offline adversarial tests; no real political outcome or person records."""
from __future__ import annotations

import dataclasses
import json
import tempfile
import unittest
from pathlib import Path

from politics_fantasy.official_temporal_links import (
    ContractError, CongressProcess, DocumentaryGraph, Link, Node, Ref, Source,
    TimeEvidence, crosscheck_albacete_derivatives, read_existing_aggregate,
)

T0 = "2026-01-01T00:00:00Z"
T1 = "2026-01-02T00:00:00Z"
T2 = "2026-01-03T00:00:00Z"
T3 = "2026-01-04T00:00:00Z"
T4 = "2026-01-05T00:00:00Z"
T5 = "2026-01-06T00:00:00Z"
T6 = "2026-01-07T00:00:00Z"
H = "a" * 64
K = CongressProcess("XV", "121", "121/000001")
K2 = CongressProcess("XV", "122", "122/000001")
P = Ref("CONGRESO", "EXPEDIENTE", "XV:121/000001")
E = Ref("CONGRESO", "TRAMITE", "STAGE-A")
I = Ref("CONGRESO", "ORGANISMO", "CAMARA")
D = Ref("BOE", "DOCUMENT", "BOE-A-2026-1")


def conf(t=T1):
    return TimeEvidence("CONFIRMED", first_public_at=t,
                        evidence_basis="SYNTHETIC_ATTESTATION")


def bound(t=T3):
    return TimeEvidence("BOUNDED", available_by=t, evidence_basis="SYNTHETIC_BOUND")


def unknown():
    return TimeEvidence("UNKNOWN")


class LinksTests(unittest.TestCase):
    def setUp(self):
        self.g = DocumentaryGraph()
        self.g.add_source(Source("CONGRESO", "CONGRESO", "INITIATIVES", H, T0,
                                 "SYNTHETIC_LAB", "SYNTHETIC_ONLY", "synthetic://congreso"))
        self.g.add_source(Source("BOE", "BOE", "DAILY_SUMMARY", H, T0,
                                 "SYNTHETIC_LAB", "SYNTHETIC_ONLY", "synthetic://boe"))

    def process(self, **kw):
        base = dict(ref=P, node_class="PROCESS", source_id="CONGRESO",
                    local_event_id="initiative-1", revision="1", process=K,
                    occurred_at=T0, recorded_at=T1, knowledge=conf(T1))
        base.update(kw)
        return Node(**base)

    def stage(self, **kw):
        base = dict(ref=E, node_class="PROCEDURAL_COMMUNICATION", source_id="CONGRESO",
                    local_event_id="stage-a", revision="1", process=K,
                    occurred_at=T1, recorded_at=T2, knowledge=conf(T2))
        base.update(kw)
        return Node(**base)

    def office(self, **kw):
        base = dict(ref=I, node_class="INSTITUTION", source_id="CONGRESO",
                    local_event_id="institution", revision="1", process=None,
                    occurred_at=T0, recorded_at=T1, knowledge=conf(T1))
        base.update(kw)
        return Node(**base)

    def document(self, **kw):
        base = dict(ref=D, node_class="DOCUMENT", source_id="BOE",
                    local_event_id="boe-document", revision="1", process=None,
                    occurred_at=T2, recorded_at=T3, knowledge=bound(T3))
        base.update(kw)
        return Node(**base)

    def step_link(self, **kw):
        base = dict(source_id="CONGRESO", local_event_id="step-a", revision="1",
                    predicate="PROCEDURE_STEP", subject=P, object=E, process=K,
                    recorded_at=T2, knowledge=conf(T2))
        base.update(kw)
        return Link(**base)

    def boe_link(self, **kw):
        base = dict(source_id="CONGRESO", local_event_id="boe-crossref",
                    revision="1", predicate="PROCESS_PUBLISHED_IN_BOE",
                    subject=P, object=D, process=K, recorded_at=T4,
                    knowledge=conf(T4),
                    crossref_basis="DIRECT_OFFICIAL_CROSS_REFERENCE")
        base.update(kw)
        return Link(**base)

    def standard(self):
        for row in (self.office(), self.process(), self.stage(), self.document(),
                    self.step_link(), self.boe_link()):
            self.g.add(row)

    def test_exact_namespaced_references(self):
        self.assertNotEqual(P, Ref("BOE", "EXPEDIENTE", P.local_id))
        self.assertNotEqual(K, K2)

    def test_string_names_cannot_replace_source_key(self):
        with self.assertRaisesRegex(ContractError, "BAD_LOCAL_ID"):
            Ref("CONGRESO", "EXPEDIENTE", "a title with spaces")
        with self.assertRaisesRegex(ContractError, "BAD_LEGISLATURE"):
            CongressProcess("XV II", "121", "121/0001")

    def test_source_capture_not_self_admission_of_real(self):
        self.g.add_source(Source("OTHER", "OTHER", "AGGREGATE", H, T0,
                                 "EXISTING_AGGREGATE_DOCUMENTARY", "REUSE_REVIEW_PENDING",
                                 "https://example.invalid/aggregate"))
        with self.assertRaisesRegex(ContractError, "REAL_DATA_ADMISSION"):
            self.g.add(Node(ref=Ref("OTHER", "ORGANISMO", "A"),
                            node_class="INSTITUTION", source_id="OTHER",
                            local_event_id="fact", revision="1",
                            process=None, occurred_at=T0, recorded_at=T1,
                            knowledge=unknown()))

    def test_real_license_claim_cannot_elevate_rights(self):
        with self.assertRaisesRegex(ContractError, "UNTRUSTED_REAL_RIGHTS_ESCALATION"):
            Source("OTHER", "OTHER", "AGGREGATE", H, T0,
                   "EXISTING_AGGREGATE_DOCUMENTARY", "OPEN_LICENSE_VERIFIED",
                   "https://example.invalid/file")

    def test_confirmed_vs_bounded_vs_unknown(self):
        self.standard()
        old = self.g.snapshot(T2)
        self.assertEqual(len(old.confirmed_nodes), 3)
        self.assertEqual(len(old.bounded_nodes), 0)
        self.assertEqual(len(old.confirmed_links), 1)
        self.assertEqual(len(old.bounded_links), 0)
        after = self.g.snapshot(T4)
        self.assertEqual(len(after.bounded_nodes), 1)
        self.assertEqual(len(after.bounded_links), 1)
        self.assertEqual(len(after.confirmed_links), 1)
        self.assertEqual(after.coverage()["unverified_congress_eligibility_denominator"], None)

    def test_document_from_boe_never_creates_process(self):
        self.g.add(self.document())
        self.assertEqual(self.g.snapshot(T4).coverage()["visible_documentary_processes"], 0)
        self.assertIsNone(self.g.snapshot(T4).coverage()["legislative_success_rate"])

    def test_missing_boe_is_not_zero(self):
        self.g.add(self.process())
        coverage = self.g.snapshot(T2).coverage()
        self.assertEqual(coverage["registered_processes_without_linked_boe"], 1)
        self.assertEqual(coverage["registered_processes_without_linked_boe_semantics"],
                         "NOT_OBSERVED_NOT_ZERO")

    def test_two_documentary_alias_nodes_same_process_key_are_not_two_procedures(self):
        self.g.add(self.process())
        alternate=Ref("CONGRESO", "EXPEDIENTE", "XV:121/000001-ALIAS")
        self.g.add(self.process(ref=alternate, local_event_id="alias-of-initiative-1"))
        self.g.add(self.stage())
        self.g.add(self.step_link())
        observed=self.g.snapshot(T4).coverage()
        self.assertEqual(observed["visible_source_local_process_nodes"],2)
        self.assertEqual(observed["visible_documentary_processes"],1)
        self.assertEqual(observed["registered_processes_missing_observed_step"],0)
        self.assertEqual(observed["registered_processes_without_linked_boe"],1)
        self.assertEqual(observed["multiple_refs_for_same_claimed_process_key"],1)
        self.assertIsNone(observed["unverified_congress_eligibility_denominator"])
        self.assertTrue(observed["matching_claimed_key_does_not_verify_official_identity"])

    def test_no_automatic_join_based_on_title_or_date(self):
        self.g.add(self.process())
        self.g.add(self.document())
        self.assertEqual(len(self.g.snapshot(T4).bounded_links), 0)
        self.assertEqual(self.g.snapshot(T4).coverage()["registered_processes_without_linked_boe"], 1)

    def test_process_boe_join_requires_direct_cross_reference(self):
        with self.assertRaisesRegex(ContractError, "BOE_PROCESS_JOIN_REQUIRES_DIRECT_REFERENCE"):
            self.boe_link(crossref_basis=None)

    def test_process_join_different_expediente_rejected(self):
        self.g.add(self.process())
        self.g.add(self.document())
        self.g.add(self.boe_link(process=K2))
        with self.assertRaisesRegex(ContractError, "BOE_JOIN_PROCESS_KEY_MISMATCH"):
            self.g.snapshot(T4)

    def test_stage_join_different_expediente_rejected(self):
        self.g.add(self.process())
        self.g.add(self.stage(process=K2))
        self.g.add(self.step_link())
        with self.assertRaisesRegex(ContractError, "STAGE_JOIN_PROCESS_KEY_MISMATCH"):
            self.g.snapshot(T4)

    def test_ontology_institution_distinct_from_decision(self):
        self.g.add(self.process())
        self.g.add(self.office())
        self.g.add(self.stage())
        self.g.add(self.step_link(subject=I))
        with self.assertRaisesRegex(ContractError, "ONTOLOGICAL_EDGE_CLASS_MISMATCH"):
            self.g.snapshot(T4)

    def test_institution_participation_in_communication_not_membership(self):
        self.g.add(self.office())
        self.g.add(self.stage())
        self.g.add(Link(source_id="CONGRESO",local_event_id="speaker-role",
                        revision="1", predicate="INSTITUTION_OPERATES",
                        subject=I, object=E, process=K, recorded_at=T2, knowledge=conf(T2)))
        self.assertEqual(len(self.g.snapshot(T3).confirmed_links), 1)
        self.assertNotIn("MEMBER_OF_PARTY", {r.predicate for r in self.g.revisions.values()
                                            if isinstance(r, Link)})

    def test_forbid_person_or_partisan_relation(self):
        with self.assertRaisesRegex(ContractError, "FORBIDDEN_RELATION_TYPE"):
            self.step_link(predicate="SAME_PERSON")

    def test_crossref_document_has_valid_boe_id(self):
        with self.assertRaisesRegex(ContractError, "BAD_BOE_DOCUMENT_ID"):
            self.document(ref=Ref("BOE", "DOCUMENT", "BOE-FAKE-2026"))

    def test_capture_happened_after_first_publication_but_not_early_visible(self):
        self.g.add(self.process(knowledge=conf(T1), recorded_at=T4))
        self.assertEqual(len(self.g.snapshot(T3).confirmed_nodes), 0)
        self.assertEqual(len(self.g.snapshot(T4).confirmed_nodes), 1)

    def test_future_boe_crossref_does_not_leak_into_earlier_snapshot(self):
        self.standard()
        snap = self.g.snapshot(T3)
        self.assertEqual(snap.coverage()["registered_processes_without_linked_boe"], 1)
        self.assertEqual(snap.coverage()["bounded_visible_nodes"], 1)
        self.assertEqual(snap.coverage()["bounded_visible_links"], 0)
        self.assertEqual(self.g.snapshot(T4).coverage()["bounded_visible_links"], 1)

    def test_future_publication_date_cannot_precede_capture(self):
        with self.assertRaisesRegex(ContractError, "PUBLICATION_AFTER_CAPTURE"):
            self.process(knowledge=conf(T4), recorded_at=T2)

    def test_unknown_publication_cannot_be_canonicalized_to_issue_date(self):
        self.g.add(self.process(knowledge=unknown()))
        snap = self.g.snapshot(T5)
        self.assertEqual(snap.unknown_time, 1)
        self.assertEqual(snap.coverage()["visible_documentary_processes"], 0)

    def test_unknown_revision_blocks_old_snapshot_after_its_capture(self):
        self.g.add(self.process())
        self.g.add(self.process(revision="2", knowledge=unknown(), recorded_at=T3))
        self.assertEqual(len(self.g.snapshot(T2).confirmed_nodes), 1)
        later = self.g.snapshot(T4)
        self.assertEqual(len(later.confirmed_nodes), 0)
        self.assertEqual(later.embargoed_unresolved_revision, 1)

    def test_future_unknown_revision_not_leaked_through_diagnostics(self):
        self.g.add(self.process())
        before = self.g.snapshot(T2)
        self.g.add(self.process(revision="unknown-future", knowledge=unknown(),
                                recorded_at=T6))
        after_future_insert = self.g.snapshot(T2)
        self.assertEqual(before, after_future_insert)
        later = self.g.snapshot(T6)
        self.assertEqual(later.unknown_time, 1)
        self.assertEqual(later.embargoed_unresolved_revision, 1)

    def test_future_known_revision_not_leaked_through_diagnostics(self):
        self.g.add(self.process())
        before = self.g.snapshot(T2)
        self.g.add(self.process(revision="future", knowledge=conf(T5),
                                recorded_at=T5, occurred_at=T4))
        self.assertEqual(before, self.g.snapshot(T2))

    def test_conflicting_duplicate_same_source_event_revision_rejected(self):
        row = self.process()
        self.assertEqual(self.g.add(row), "ADDED")
        self.assertEqual(self.g.add(row), "DEDUPLICATED")
        with self.assertRaisesRegex(ContractError, "DUPLICATE_REVISION_CONFLICT"):
            self.g.add(dataclasses.replace(row,event_status="UNKNOWN"))

    def test_different_revision_old_backfill_does_not_win(self):
        self.g.add(self.process(revision="new", knowledge=conf(T2), recorded_at=T2))
        self.g.add(self.process(revision="old", knowledge=conf(T1), recorded_at=T4))
        snap = self.g.snapshot(T4)
        self.assertEqual([x.revision for x in snap.confirmed_nodes], ["new"])

    def test_two_revisions_same_first_public_fail_closed(self):
        self.g.add(self.process(revision="1"))
        self.g.add(self.process(revision="2"))
        with self.assertRaisesRegex(ContractError, "TIED_OR_AMBIGUOUS"):
            self.g.snapshot(T3)

    def test_different_sources_cannot_implicitly_dedup(self):
        self.g.add(self.process())
        other = Ref("BOE", "DOCUMENT", "BOE-A-2026-1")
        self.g.add(self.document(ref=other, local_event_id="initiative-1"))
        self.assertEqual(len(self.g.snapshot(T3).confirmed_nodes), 1)
        self.assertEqual(len(self.g.snapshot(T3).bounded_nodes), 1)

    def test_unobserved_endpoint_blocks_relation(self):
        self.g.add(self.process())
        self.g.add(self.step_link())
        snap = self.g.snapshot(T3)
        self.assertEqual(snap.blocked_unmatched_endpoint, 1)
        self.assertEqual(len(snap.confirmed_links), 0)

    def test_late_revised_event_does_not_resurrect_old_link(self):
        self.g.add(self.process())
        self.g.add(self.stage())
        self.g.add(self.step_link())
        self.g.add(self.stage(revision="2",occurred_at=T4,knowledge=conf(T4),recorded_at=T4))
        # Reconstructing as-of T4 with valid_at T2 must not return the old stage.
        snap = self.g.snapshot(T4,valid_at=T2)
        self.assertEqual(len(snap.confirmed_links), 0)
        self.assertEqual(snap.blocked_unmatched_endpoint, 1)

    def test_snapshot_valid_time_cannot_be_future_of_knowledge(self):
        with self.assertRaisesRegex(ContractError, "VALID_AT_AFTER_AS_OF"):
            self.g.snapshot(T2,valid_at=T3)

    def test_bounded_snapshot_remains_distinct_from_exact(self):
        self.g.add(self.process(knowledge=bound(T2),recorded_at=T2))
        self.assertEqual(len(self.g.snapshot(T1).bounded_nodes), 0)
        self.assertEqual(len(self.g.snapshot(T2).bounded_nodes), 1)
        self.assertEqual(len(self.g.snapshot(T2).confirmed_nodes), 0)

    def test_future_bound_cannot_declare_available_now(self):
        self.g.add(self.process(knowledge=bound(T4),recorded_at=T4))
        self.assertEqual(len(self.g.snapshot(T3).bounded_nodes), 0)

    def test_unknown_cannot_falsely_assert_timestamp(self):
        with self.assertRaisesRegex(ContractError, "UNKNOWN_CANNOT_ASSERT_AVAILABILITY"):
            TimeEvidence("UNKNOWN",available_by=T1)
        with self.assertRaisesRegex(ContractError, "BOUND_NOT_AN_EXACT_FIRST_PUBLIC"):
            TimeEvidence("BOUNDED",first_public_at=T1,available_by=T2,
                         evidence_basis="SYNTHETIC_BOUND")

    def test_no_external_timestamp_claim_accepted_in_lab(self):
        with self.assertRaisesRegex(ContractError, "NO_EXTERNAL_TIMESTAMP_WITNESS_IN_LAB"):
            self.g.add(self.process(
                knowledge=TimeEvidence("CONFIRMED",first_public_at=T1,
                                      evidence_basis="EXTERNAL_TRUSTED_WITNESS")))

    def test_source_capture_must_precede_assertion(self):
        with self.assertRaisesRegex(ContractError, "ASSERTION_BEFORE_CAPTURE"):
            self.g.add(self.process(recorded_at="2025-12-31T00:00:00Z",
                                    knowledge=unknown()))

    def test_manifest_deterministic_and_no_scientific_cycles(self):
        self.standard()
        m = self.g.manifest()
        self.assertEqual(m, self.g.manifest())
        self.assertEqual(len(m["canonical_sha256"]), 64)
        self.assertFalse(m["boe_is_risk_population"])
        self.assertEqual(m["scientific_cycles_consumed"], 0)
        self.assertFalse(m["real_source_admission_enabled"])

    def test_canonical_hash_independent_of_insertion_order(self):
        p,s = self.process(),self.stage()
        self.g.add(p);self.g.add(s)
        other=DocumentaryGraph()
        for src in self.g.sources.values():
            other.add_source(src)
        other.add(s);other.add(p)
        self.assertEqual(self.g.manifest()["canonical_sha256"],
                         other.manifest()["canonical_sha256"])

    def test_duplicate_ref_same_cutoff_rejected(self):
        self.g.add(self.process())
        self.g.add(self.process(local_event_id="different-id"))
        with self.assertRaisesRegex(ContractError, "DUPLICATED_NODE_REFERENCE"):
            self.g.snapshot(T2)

    def test_local_aggregate_json_with_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            p=Path(folder)/"bad.json"
            p.write_text('{"schema":"x","schema":"y"}',encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "DUPLICATE_JSON_KEY"):
                read_existing_aggregate(p)

    def test_real_aggregate_missing_schema_rejected(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            p=Path(folder)/"bad.json"
            p.write_text('{"schema":"imaginary"}',encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "UNKNOWN_AGGREGATE_KIND"):
                read_existing_aggregate(p)

    def test_real_aggregate_hash_check(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            p=Path(folder)/"data.json"
            p.write_text('{"schema":"imaginary"}',encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "AGGREGATE_SHA_MISMATCH"):
                read_existing_aggregate(p,expected_sha256="0"*64)

    def _two_fictional_derivatives(self, folder: str):
        n = Path(folder) / "n.json"
        m = Path(folder) / "m.json"
        narrow = {
            "dataset_class": "OFFICIAL_2023_SINGLE_PROVINCE_CANDIDACY_LIST_LABELS",
            "source_document": "BOE-A-2023-15066",
            "original_sha256": "a" * 64,
            "scope": {"province": "Albacete", "national_coverage_claimed": False,
                      "proclaimed_lists": 2},
            "lists": [
                {"order": 1, "acronym": "FAKE-A", "entity_type": "ELECTORAL_CANDIDACY_LABEL",
                 "registered_party_id": None, "named_person_count": 0},
                {"order": 2, "acronym": "FAKE-B", "entity_type": "ELECTORAL_CANDIDACY_LABEL",
                 "registered_party_id": None, "named_person_count": 0},
            ],
        }
        multi = {
            "id": "BOE_A_2023_15066_MULTIPROVINCE_EXTRACT",
            "model": "OFFICIAL_ORIGINAL_PDF_DOCUMENTARY_CANDIDACIES_NOT_LEGAL_PARTIES",
            "original_sha256": "a" * 64,
            "provinces": [
                {"province_label": "ALBACETE", "province_id": "ALBACETE",
                 "congress_candidacies": 2, "lists": [
                    {"position": 1, "acronym": "FAKE-A",
                     "entity_semantics": "ELECTORAL_LIST_NOT_REGISTERED_PARTY",
                     "legal_party_registration_id": None, "person_count_joined": 0},
                    {"position": 2, "acronym": "FAKE-B",
                     "entity_semantics": "ELECTORAL_LIST_NOT_REGISTERED_PARTY",
                     "legal_party_registration_id": None, "person_count_joined": 0},
                 ]},
            ],
        }
        n.write_text(json.dumps(narrow), encoding="utf-8")
        m.write_text(json.dumps(multi), encoding="utf-8")
        return n, m, narrow, multi

    def test_derivative_join_is_only_ordinal_and_same_source(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            n,m,_,_ = self._two_fictional_derivatives(folder)
            result = crosscheck_albacete_derivatives(n,m)
            self.assertEqual(result["candidacy_label_ordinals_aligned"], 2)
            self.assertFalse(result["independent_publisher_verification"])
            self.assertEqual(result["congress_initiatives_inferred"], 0)

    def test_derivative_crosscheck_refuses_mismatched_label(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            n,m,_,multi = self._two_fictional_derivatives(folder)
            multi["provinces"][0]["lists"][1]["acronym"] = "ANOTHER"
            m.write_text(json.dumps(multi), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "DERIVATIVE_LABEL_ALIGNMENT_MISMATCH"):
                crosscheck_albacete_derivatives(n,m)

    def test_derivative_crosscheck_refuses_mismatched_original_sha(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            n,m,_,multi = self._two_fictional_derivatives(folder)
            multi["original_sha256"] = "0" * 64
            m.write_text(json.dumps(multi), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "DERIVATIVES_DISAGREE"):
                crosscheck_albacete_derivatives(n,m)

    def test_derivative_crosscheck_refuses_duplicate_ordinal(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            n,m,_,multi = self._two_fictional_derivatives(folder)
            multi["provinces"][0]["lists"][1]["position"] = 1
            m.write_text(json.dumps(multi), encoding="utf-8")
            with self.assertRaisesRegex(ContractError, "DERIVATIVE_LABEL_ALIGNMENT_MISMATCH"):
                crosscheck_albacete_derivatives(n,m)


if __name__ == "__main__":
    unittest.main()
