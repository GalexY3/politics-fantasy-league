"""PFL links2: offline documentary graph prototype for Spanish public institutions.

Complement (not replacement) of warehouse.py, evidence_warehouse.mjs, and
temporal_evidence.py. No HTTP, source authentication, user-data acceptance,
real-person identity joins, or scientific outcomes. A label supplied by a caller
cannot certify an official source, a historical publication time, or a licence.
The host must maintain a separate server-owned original/rights/time registry.

Three *distinct* kinds of temporal access:
 CONFIRMED: exact first-publication independently attested (synthetic in tests).
 BOUNDED: a conservative available-by bound, never exact first publication.
 UNKNOWN: neither; never silently visible even for an old act/issue date.

The current lab accepts only explicitly synthetic nodes/links. Existing Spanish
aggregate files can be *audited without import* in metadata_smoke.py.
"""
from __future__ import annotations

import dataclasses
import hashlib
import json
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

SCHEMA = "pfl.links2.temporal.v1"
ID = re.compile(r"[A-Za-z0-9_.:/-]{1,120}\Z")
SHA = re.compile(r"[0-9a-f]{64}\Z")
MAX_INPUT = 2_000_000
CLASSES = frozenset({
    "INSTITUTION", "PROCESS", "PROCEDURAL_COMMUNICATION",
    "PROCEDURAL_DECISION", "DOCUMENT",
})
PREDICATES = {
    "INSTITUTION_OPERATES": ("INSTITUTION", "PROCEDURAL_COMMUNICATION"),
    "INSTITUTION_DECIDES": ("INSTITUTION", "PROCEDURAL_DECISION"),
    "PROCEDURE_STEP": ("PROCESS", "PROCEDURAL_COMMUNICATION"),
    "DECISION_STEP": ("PROCESS", "PROCEDURAL_DECISION"),
    "DOCUMENTS_STEP": ("PROCEDURAL_COMMUNICATION", "DOCUMENT"),
    "DECISION_DOCUMENTED": ("PROCEDURAL_DECISION", "DOCUMENT"),
    "PROCESS_PUBLISHED_IN_BOE": ("PROCESS", "DOCUMENT"),
}
QUALITIES = frozenset({"CONFIRMED", "BOUNDED", "UNKNOWN"})
SOURCE_CLASSES = frozenset({"SYNTHETIC_LAB", "EXISTING_AGGREGATE_DOCUMENTARY"})


class ContractError(ValueError):
    pass


def _id(value: str, label: str) -> str:
    if not isinstance(value, str) or not ID.fullmatch(value):
        raise ContractError("BAD_" + label)
    return value


def time_utc(value: str, label: str) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ContractError("BAD_" + label)
    try:
        d = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ContractError("BAD_" + label) from exc
    if d.tzinfo is None or d.utcoffset() is None:
        raise ContractError("NAIVE_" + label)
    return d.astimezone(timezone.utc)


@dataclass(frozen=True, order=True)
class Ref:
    """A source-issued ID, not a human-ID crosswalk or name matching rule."""
    authority: str
    family: str
    local_id: str

    def __post_init__(self):
        for name in ("authority", "family", "local_id"):
            _id(getattr(self, name), name.upper())

    def wire(self):
        return [self.authority, self.family, self.local_id]


@dataclass(frozen=True, order=True)
class CongressProcess:
    """An exact Congress expediente namespace: legislature, family, number."""
    legislature: str
    initiative_family: str
    expediente: str

    def __post_init__(self):
        for name in ("legislature", "initiative_family", "expediente"):
            _id(getattr(self, name), name.upper())

    def wire(self):
        return [self.legislature, self.initiative_family, self.expediente]


@dataclass(frozen=True)
class TimeEvidence:
    """The *claimed* knowledge interval of a source revision.

    A bounded date is a safe "by" time only under an externally reviewed
    policy; never convert this field to first_public_at.
    """
    quality: str
    first_public_at: str | None = None
    available_by: str | None = None
    evidence_basis: str | None = None

    def __post_init__(self):
        if self.quality not in QUALITIES:
            raise ContractError("BAD_KNOWLEDGE_QUALITY")
        if self.quality == "CONFIRMED":
            if self.first_public_at is None or self.available_by is not None:
                raise ContractError("CONFIRMED_NEEDS_EXACT_FIRST_PUBLIC")
            if self.evidence_basis not in {"SYNTHETIC_ATTESTATION", "EXTERNAL_TRUSTED_WITNESS"}:
                raise ContractError("UNSUPPORTED_EXACT_TIME_BASIS")
            time_utc(self.first_public_at, "FIRST_PUBLIC")
        elif self.quality == "BOUNDED":
            if self.first_public_at is not None or self.available_by is None:
                raise ContractError("BOUND_NOT_AN_EXACT_FIRST_PUBLIC")
            if self.evidence_basis not in {"SYNTHETIC_BOUND", "CONSERVATIVE_POLICY_REVIEWED"}:
                raise ContractError("UNSUPPORTED_BOUND_BASIS")
            time_utc(self.available_by, "AVAILABLE_BY")
        elif (self.first_public_at is not None or self.available_by is not None
              or self.evidence_basis is not None):
            raise ContractError("UNKNOWN_CANNOT_ASSERT_AVAILABILITY")

    def availability(self) -> datetime | None:
        if self.quality == "UNKNOWN":
            return None
        return time_utc(self.first_public_at or self.available_by, "SOURCE_AVAILABILITY")


@dataclass(frozen=True)
class Source:
    source_id: str
    authority: str
    document_family: str
    sha256: str
    acquired_at: str
    evidence_class: str
    rights_status: str
    source_url: str

    def __post_init__(self):
        for field in ("source_id", "authority", "document_family"):
            _id(getattr(self, field), field.upper())
        if not isinstance(self.sha256, str) or not SHA.fullmatch(self.sha256):
            raise ContractError("BAD_SOURCE_SHA")
        time_utc(self.acquired_at, "ACQUIRED_AT")
        if self.evidence_class not in SOURCE_CLASSES:
            raise ContractError("UNSUPPORTED_SOURCE_CLASS")
        if self.evidence_class == "SYNTHETIC_LAB":
            if self.rights_status != "SYNTHETIC_ONLY" or not self.source_url.startswith("synthetic://"):
                raise ContractError("SYNTHETIC_PROVENANCE_REQUIRED")
        elif self.rights_status not in {"REUSE_REVIEW_PENDING", "CATALOG_LICENCE_ONLY"}:
            raise ContractError("UNTRUSTED_REAL_RIGHTS_ESCALATION")
        if not isinstance(self.source_url, str) or len(self.source_url) > 2048:
            raise ContractError("INVALID_SOURCE_URL")


@dataclass(frozen=True)
class Node:
    ref: Ref
    node_class: str
    source_id: str
    local_event_id: str
    revision: str
    process: CongressProcess | None
    occurred_at: str
    recorded_at: str
    knowledge: TimeEvidence
    event_status: str = "DOCUMENTED"   # or UNKNOWN, NEVER a political outcome

    def __post_init__(self):
        if self.node_class not in CLASSES:
            raise ContractError("INVALID_NODE_CLASS")
        for name in ("source_id", "local_event_id", "revision"):
            _id(getattr(self, name), name.upper())
        if not isinstance(self.ref, Ref) or self.ref.authority != self.source_id:
            raise ContractError("NODE_SOURCE_NAMESPACE_MISMATCH")
        if self.node_class in {"PROCESS", "PROCEDURAL_COMMUNICATION", "PROCEDURAL_DECISION"}:
            if not isinstance(self.process, CongressProcess):
                raise ContractError("PROCESS_KEY_REQUIRED")
        elif self.process is not None:
            raise ContractError("UNEXPECTED_PROCESS_KEY")
        if self.node_class == "DOCUMENT":
            if self.ref.authority == "BOE":
                if self.ref.family != "DOCUMENT" or not re.fullmatch(
                    r"BOE-A-(?:19|20)\d{2}-[1-9]\d*", self.ref.local_id
                ):
                    raise ContractError("BAD_BOE_DOCUMENT_ID")
        time_utc(self.occurred_at, "OCCURRED_AT")
        time_utc(self.recorded_at, "RECORDED_AT")
        if not isinstance(self.knowledge, TimeEvidence):
            raise ContractError("BAD_TIME_EVIDENCE")
        if self.knowledge.availability() is not None and (
            self.knowledge.availability() > time_utc(self.recorded_at, "RECORDED_AT")):
            raise ContractError("PUBLICATION_AFTER_CAPTURE")
        if self.event_status not in {"DOCUMENTED", "UNKNOWN"}:
            raise ContractError("INVALID_DOCUMENTARY_STATUS")

    @property
    def stable_key(self):
        return ("NODE", self.source_id, self.local_event_id)

    @property
    def rev_key(self):
        return (*self.stable_key, self.revision)


@dataclass(frozen=True)
class Link:
    source_id: str
    local_event_id: str
    revision: str
    predicate: str
    subject: Ref
    object: Ref
    process: CongressProcess | None
    recorded_at: str
    knowledge: TimeEvidence
    crossref_basis: str | None = None

    def __post_init__(self):
        for name in ("source_id", "local_event_id", "revision"):
            _id(getattr(self, name), name.upper())
        if self.predicate not in PREDICATES:
            raise ContractError("FORBIDDEN_RELATION_TYPE")
        if not isinstance(self.subject, Ref) or not isinstance(self.object, Ref):
            raise ContractError("LINK_NEEDS_EXACT_ENDPOINTS")
        time_utc(self.recorded_at, "RECORDED_AT")
        if not isinstance(self.knowledge, TimeEvidence):
            raise ContractError("BAD_LINK_TIME_EVIDENCE")
        if self.knowledge.availability() is not None and (
            self.knowledge.availability() > time_utc(self.recorded_at, "RECORDED_AT")):
            raise ContractError("PUBLICATION_AFTER_CAPTURE")
        if self.predicate == "PROCESS_PUBLISHED_IN_BOE":
            if self.crossref_basis != "DIRECT_OFFICIAL_CROSS_REFERENCE":
                raise ContractError("BOE_PROCESS_JOIN_REQUIRES_DIRECT_REFERENCE")
            if not isinstance(self.process, CongressProcess):
                raise ContractError("BOE_JOIN_REQUIRES_PROCESS_KEY")
            if (self.object.authority != "BOE" or self.object.family != "DOCUMENT"):
                raise ContractError("BOE_JOIN_REQUIRES_BOE_DOCUMENT")
        elif self.crossref_basis is not None:
            raise ContractError("CROSSREF_BASIS_NOT_APPLICABLE")

    @property
    def stable_key(self):
        return ("LINK", self.source_id, self.local_event_id)

    @property
    def rev_key(self):
        return (*self.stable_key, self.revision)


@dataclass(frozen=True)
class Snapshot:
    as_of: str
    confirmed_nodes: tuple[Node, ...]
    bounded_nodes: tuple[Node, ...]
    confirmed_links: tuple[Link, ...]
    bounded_links: tuple[Link, ...]
    unknown_time: int
    blocked_future_or_uncaptured: int
    blocked_non_admitted: int
    blocked_unmatched_endpoint: int
    blocked_untrusted_reference: int
    embargoed_unresolved_revision: int
    congressional_population_census_verified: bool = False
    real_person_scoring: bool = False

    def coverage(self) -> dict:
        """The denominator is merely the documents in this constructed snapshot."""
        nodes = (*self.confirmed_nodes, *self.bounded_nodes)
        processes = [n for n in nodes if n.node_class == "PROCESS"]
        # Different documentary Ref aliases of the *same asserted* typed
        # CongressProcess are not independent institutional procedures. This
        # deduplication is within the SYNTHETIC graph only: the typed keys are
        # still unverified claims, not a signed register or true denominator.
        process_refs: dict[CongressProcess, set[Ref]] = {}
        for n in processes:
            process_refs.setdefault(n.process, set()).add(n.ref)
        step_links = [l for l in (*self.confirmed_links, *self.bounded_links)
                      if l.predicate in {"PROCEDURE_STEP", "DECISION_STEP"}]
        published = [l for l in (*self.confirmed_links, *self.bounded_links)
                     if l.predicate == "PROCESS_PUBLISHED_IN_BOE"]
        with_step = {x.subject for x in step_links}
        with_boe = {x.subject for x in published}
        return {
            "visible_documentary_processes": len(process_refs),
            "visible_source_local_process_nodes": len(processes),
            "multiple_refs_for_same_claimed_process_key": sum(
                len(refs)>1 for refs in process_refs.values()),
            "registered_processes_missing_observed_step": sum(
                not (refs & with_step) for refs in process_refs.values()),
            "registered_processes_without_linked_boe": sum(
                not (refs & with_boe) for refs in process_refs.values()),
            "registered_processes_without_linked_boe_semantics": "NOT_OBSERVED_NOT_ZERO",
            "matching_claimed_key_does_not_verify_official_identity": True,
            "confirmed_visible_nodes": len(self.confirmed_nodes),
            "bounded_visible_nodes": len(self.bounded_nodes),
            "confirmed_visible_links": len(self.confirmed_links),
            "bounded_visible_links": len(self.bounded_links),
            "unknown_first_public_or_bound": self.unknown_time,
            "blocked_future_or_uncaptured": self.blocked_future_or_uncaptured,
            "blocked_unmatched_endpoint": self.blocked_unmatched_endpoint,
            "unverified_congress_eligibility_denominator": None,
            "observatory_coverage_rate": None,
            "congress_population_census_verified": False,
            "legislative_success_rate": None,
            "real_person_scoring": False,
        }


def _canonical_bytes(obj) -> bytes:
    return json.dumps(obj, sort_keys=True, ensure_ascii=False,
                      separators=(",", ":"), allow_nan=False).encode("utf-8")


class DocumentaryGraph:
    """A controlled offline *lab*; source labels supplied by clients are not proof."""
    def __init__(self):
        self.sources: dict[str, Source] = {}
        self.revisions: dict[tuple[str, str, str, str], Node | Link] = {}

    def add_source(self, source: Source):
        old = self.sources.get(source.source_id)
        if old is not None and old != source:
            raise ContractError("SOURCE_ID_CONFLICT")
        self.sources[source.source_id] = source
        return "IDEMPOTENT" if old else "ADDED"

    def add(self, assertion: Node | Link):
        if not isinstance(assertion, (Node, Link)):
            raise ContractError("UNKNOWN_ASSERTION")
        source = self.sources.get(assertion.source_id)
        if source is None:
            raise ContractError("SOURCE_NOT_REGISTERED")
        if time_utc(assertion.recorded_at, "RECORDED_AT") < time_utc(source.acquired_at, "ACQUIRED_AT"):
            raise ContractError("ASSERTION_BEFORE_CAPTURE")
        # In this isolated harness, only synthetic facts are query-admitted;
        # real aggregate is metadata-audited but not integrated as graph facts.
        if source.evidence_class != "SYNTHETIC_LAB":
            raise ContractError("REAL_DATA_ADMISSION_REQUIRES_TRUSTED_REGISTRY")
        if assertion.knowledge.quality == "CONFIRMED" and (
                assertion.knowledge.evidence_basis != "SYNTHETIC_ATTESTATION"):
            raise ContractError("NO_EXTERNAL_TIMESTAMP_WITNESS_IN_LAB")
        if assertion.knowledge.quality == "BOUNDED" and (
                assertion.knowledge.evidence_basis != "SYNTHETIC_BOUND"):
            raise ContractError("NO_EXTERNAL_BOUND_WITNESS_IN_LAB")
        old = self.revisions.get(assertion.rev_key)
        if old is not None:
            if old != assertion:
                raise ContractError("DUPLICATE_REVISION_CONFLICT")
            return "DEDUPLICATED"
        self.revisions[assertion.rev_key] = assertion
        return "ADDED"

    def _eligible_revisions(self, cutoff: datetime):
        grouped: dict[tuple[str, str, str], list[Node | Link]] = {}
        no_time, future, denied, embargoed = 0, 0, 0, 0
        for fact in self.revisions.values():
            source = self.sources[fact.source_id]
            if source.evidence_class != "SYNTHETIC_LAB":
                denied += 1
                continue
            grouped.setdefault(fact.stable_key, []).append(fact)
        selected: list[Node | Link] = []
        for _, rows in sorted(grouped.items()):
            # Future captures do not exist for the historical observer.
            # Even exposing their count in diagnostics/coverage is leakage.
            rows = [r for r in rows
                    if time_utc(r.recorded_at, "RECORDED_AT") <= cutoff]
            if not rows:
                continue
            # An unknown-time revision already captured by cutoff could modify
            # a prior state. Therefore block the *whole identity* at this cut.
            uncertain = [r for r in rows if r.knowledge.quality == "UNKNOWN"]
            no_time += len(uncertain)
            if uncertain:
                embargoed += 1
                continue
            candidates = []
            for row in rows:
                if row.knowledge.quality == "UNKNOWN":
                    no_time += 1
                    continue
                if row.knowledge.availability() > cutoff:
                    future += 1
                    continue
                candidates.append(row)
            if not candidates:
                continue
            newest_time = max(r.knowledge.availability() for r in candidates)
            top = [r for r in candidates if r.knowledge.availability() == newest_time]
            if len(top) != 1:
                raise ContractError("TIED_OR_AMBIGUOUS_PUBLIC_REVISIONS")
            selected.append(top[0])
        return selected, no_time, future, denied, embargoed

    def snapshot(self, as_of: str, *, valid_at: str | None = None) -> Snapshot:
        cut = time_utc(as_of, "AS_OF")
        valid = time_utc(valid_at or as_of, "VALID_AT")
        if valid > cut:
            raise ContractError("VALID_AT_AFTER_AS_OF")
        selected, unknown, future, denied, embargoed = self._eligible_revisions(cut)
        nodes = [r for r in selected if isinstance(r, Node)
                 and time_utc(r.occurred_at, "OCCURRED_AT") <= valid]
        # Nodes with the same exact Ref from distinct logical IDs are ambiguous;
        # do not silently let the last one win.
        byref: dict[Ref, Node] = {}
        for n in nodes:
            if n.ref in byref:
                raise ContractError("DUPLICATED_NODE_REFERENCE_NEEDS_RECONCILIATION")
            byref[n.ref] = n
        candidate_links = [r for r in selected if isinstance(r, Link)]
        linked = []
        unmatched, untrusted = 0, 0
        for link in candidate_links:
            a, b = byref.get(link.subject), byref.get(link.object)
            if a is None or b is None or a.event_status != "DOCUMENTED" or b.event_status != "DOCUMENTED":
                unmatched += 1
                continue
            expected = PREDICATES[link.predicate]
            if (a.node_class, b.node_class) != expected:
                raise ContractError("ONTOLOGICAL_EDGE_CLASS_MISMATCH")
            if link.predicate in {"PROCEDURE_STEP", "DECISION_STEP", "PROCESS_PUBLISHED_IN_BOE"}:
                if a.process != link.process and link.predicate == "PROCESS_PUBLISHED_IN_BOE":
                    raise ContractError("BOE_JOIN_PROCESS_KEY_MISMATCH")
                if link.predicate != "PROCESS_PUBLISHED_IN_BOE" and (
                        a.process != b.process or a.process is None):
                    raise ContractError("STAGE_JOIN_PROCESS_KEY_MISMATCH")
            # Do not infer legislature/cross-reference merely from document
            # title, text, chronological coincidence, or a matching acronym.
            if link.predicate == "PROCESS_PUBLISHED_IN_BOE":
                if b.ref.authority != "BOE" or a.ref.authority != "CONGRESO":
                    raise ContractError("BOE_JOIN_WRONG_AUTHORITIES")
            # A link may only be used once BOTH endpoint observations are
            # known, and it cannot be stronger than its weakest endpoint.
            level = ("BOUNDED" if "BOUNDED" in {
                link.knowledge.quality, a.knowledge.quality, b.knowledge.quality
            } else "CONFIRMED")
            linked.append((link, level))
        confirmed_nodes = tuple(sorted((n for n in nodes if n.knowledge.quality == "CONFIRMED"),
                                       key=lambda n: n.ref))
        bounded_nodes = tuple(sorted((n for n in nodes if n.knowledge.quality == "BOUNDED"),
                                     key=lambda n: n.ref))
        confirmed_links = tuple(sorted((l for l, q in linked if q == "CONFIRMED"),
                                       key=lambda l: l.rev_key))
        bounded_links = tuple(sorted((l for l, q in linked if q == "BOUNDED"),
                                     key=lambda l: l.rev_key))
        return Snapshot(as_of, confirmed_nodes, bounded_nodes, confirmed_links, bounded_links,
                        unknown, future, denied, unmatched, untrusted, embargoed)

    def manifest(self) -> dict:
        sources = [dataclasses.asdict(s) for s in sorted(self.sources.values(), key=lambda x:x.source_id)]
        row = [dataclasses.asdict(r) for r in sorted(self.revisions.values(), key=lambda x:x.rev_key)]
        return {
            "schema": SCHEMA,
            "source_count": len(sources), "revision_count": len(row),
            "canonical_sha256": hashlib.sha256(_canonical_bytes({"sources":sources,"assertions":row})).hexdigest(),
            "data_exported": False, "real_source_admission_enabled": False,
            "congress_risk_population_verified": False,
            "boe_is_risk_population": False, "real_person_scoring": False,
            "scientific_cycles_consumed": 0,
        }


def read_existing_aggregate(path: Path, *, expected_sha256: str | None = None) -> dict:
    """Read-only bounded JSON metadata audit. NO output of labels or person rows.

    This validates a known local *derivative*, not its linked original PDF/XLSX,
    historical timestamp, issuer signature, or re-use rights.
    """
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_INPUT:
        raise ContractError("MISSING_OR_OVERSIZED_AGGREGATE")
    raw = p.read_bytes()
    if len(raw) > MAX_INPUT:
        raise ContractError("AGGREGATE_CHANGED_OR_OVERSIZED")
    digest = hashlib.sha256(raw).hexdigest()
    if expected_sha256 is not None and digest != expected_sha256:
        raise ContractError("AGGREGATE_SHA_MISMATCH")
    def strict(pairs):
        out = {}
        for k, v in pairs:
            if k in out:
                raise ContractError("DUPLICATE_JSON_KEY")
            out[k] = v
        return out
    try:
        doc = json.loads(raw.decode("utf-8"), object_pairs_hook=strict,
                         parse_constant=lambda x: (_ for _ in ()).throw(ContractError("NONFINITE_JSON")))
    except ContractError:
        raise
    except (UnicodeError, ValueError) as exc:
        raise ContractError("INVALID_AGGREGATE_JSON") from exc
    if not isinstance(doc, dict):
        raise ContractError("AGGREGATE_NOT_OBJECT")
    if doc.get("dataset_class") == "OFFICIAL_2023_SINGLE_PROVINCE_CANDIDACY_LIST_LABELS":
        scope = doc.get("scope")
        labels = doc.get("lists")
        if (doc.get("source_document") != "BOE-A-2023-15066"
                or not isinstance(scope, dict) or scope.get("province") != "Albacete"
                or scope.get("national_coverage_claimed") is not False
                or not isinstance(labels, list)
                or not isinstance(scope.get("proclaimed_lists"), int)
                or scope["proclaimed_lists"] != len(labels)
                or any(not isinstance(z, dict) or z.get("entity_type") != "ELECTORAL_CANDIDACY_LABEL"
                       or z.get("registered_party_id") is not None
                       or z.get("named_person_count") != 0 for z in labels)):
            raise ContractError("AGGREGATE_SEMANTICS_MISMATCH")
        report = {
            "scope": "BOE_2023_ALBACETE_CANDIDACY_LABELS_ONLY",
            "candidate_labels_count_documented": len(labels),
            "legal_party_id_resolved": 0,
            "nominal_people_joined": 0,
            "legislative_process_records": 0,
            "congress_risk_denominator": None,
        }
    elif doc.get("schema") == "PFL_BOCG_EVENT_COUNTS_1":
        rows = doc.get("rows")
        if (not isinstance(rows, list) or doc.get("first_public_at_exact") is not None
                or doc.get("source_signed_original_verified") is not False
                or any(not isinstance(r, dict) or r.get("issuer") != "Congreso de los Diputados"
                       or not isinstance(r.get("event_kind"), str) for r in rows)):
            raise ContractError("AGGREGATE_SEMANTICS_MISMATCH")
        unique = [(r.get("bulletin_id"), r.get("item_key"), r.get("event_kind")) for r in rows]
        if any(not all(isinstance(v, str) and v for v in key) for key in unique) or len(set(unique)) != len(unique):
            raise ContractError("DUPLICATE_OR_INVALID_SOURCE_EVENT_IDENTITY")
        report = {
            "scope": "TWO_SELECTED_BOCG_ISSUES_NONPERSON_AGGREGATE",
            "documentary_rows": len(rows),
            "event_kind_counts": {kind: sum(r["event_kind"] == kind for r in rows)
                                  for kind in sorted(set(r["event_kind"] for r in rows))},
            "cross_document_person_identity_verified": False,
            "first_public_at_verified": False,
            "full_congress_member_denominator": None,
            "congress_initiative_population": None,
        }
    elif doc.get("schema") == "pfl.source_capture_manifest.v1":
        distributions = doc.get("distribution")
        if (not isinstance(distributions, list) or len(distributions) != 2
                or {r.get("id") for r in distributions if isinstance(r, dict)}
                != {"INTERIOR_CONGRESO_ELECTED", "INTERIOR_CONGRESO_RESULTS"}
                or doc.get("first_public_at") is not None
                or doc.get("row_count_verified") is not None):
            raise ContractError("SOURCE_CAPTURE_MANIFEST_MISMATCH")
        for r in distributions:
            if (not isinstance(r, dict) or not isinstance(r.get("sha256"), str)
                    or not SHA.fullmatch(r["sha256"])
                    or type(r.get("byte_length")) is not int or r["byte_length"] <= 0):
                raise ContractError("SOURCE_CAPTURE_MANIFEST_MISMATCH")
        report = {
            "scope": "INTERIOR_TWO_XLSX_CAPTURE_RECEIPTS_ONLY",
            "distribution_count": len(distributions),
            "row_count_verified": None,
            "first_public_at_verified": False,
            "congress_initiative_population": None,
        }
    else:
        raise ContractError("UNKNOWN_AGGREGATE_KIND")
    return {
        "status": "LOCAL_DOCUMENTARY_AGGREGATE_CHECKED_NOT_ADMITTED",
        "local_json_sha256": digest,
        "local_json_bytes": len(raw),
        "derived_report": report,
        "reused_source_original_bytes_verified_here": False,
        "rights_for_this_application_reviewed": False,
        "historical_first_public_at_authenticated": False,
        "real_facts_joined": 0,
        "real_person_scoring": False,
        "release_grade": False,
    }


def crosscheck_albacete_derivatives(narrow_path: Path, multi_path: Path) -> dict:
    """Compare *two local derivatives of the SAME BOE PDF* without outputting names.

    This detects inconsistencies between two stored transcriptions but is NOT
    independent evidence of the original's authenticity or release time.
    Neither derivative is a Congress legislative-process risk population.
    """
    def load_bound(path):
        p = Path(path)
        if not p.is_file() or p.stat().st_size > MAX_INPUT:
            raise ContractError("MISSING_OR_OVERSIZED_DERIVATIVE")
        b = p.read_bytes()
        if len(b) > MAX_INPUT:
            raise ContractError("OVERSIZED_DERIVATIVE")
        def unique(pairs):
            o = {}
            for k, v in pairs:
                if k in o:
                    raise ContractError("DUPLICATE_JSON_KEY")
                o[k] = v
            return o
        try:
            v = json.loads(
                b.decode("utf-8"), object_pairs_hook=unique,
                parse_constant=lambda _: (_ for _ in ()).throw(ContractError("NONFINITE_JSON"))
            )
        except ContractError:
            raise
        except (ValueError, UnicodeError) as exc:
            raise ContractError("INVALID_DERIVATIVE_JSON") from exc
        if not isinstance(v, dict):
            raise ContractError("DERIVATIVE_NOT_OBJECT")
        return v, hashlib.sha256(b).hexdigest()

    narrow, sha_narrow = load_bound(narrow_path)
    multi, sha_multi = load_bound(multi_path)
    if (narrow.get("dataset_class") != "OFFICIAL_2023_SINGLE_PROVINCE_CANDIDACY_LIST_LABELS"
            or narrow.get("source_document") != "BOE-A-2023-15066"
            or multi.get("id") != "BOE_A_2023_15066_MULTIPROVINCE_EXTRACT"
            or multi.get("model") != "OFFICIAL_ORIGINAL_PDF_DOCUMENTARY_CANDIDACIES_NOT_LEGAL_PARTIES"):
        raise ContractError("INCOMPARABLE_DOCUMENTARY_DERIVATIVES")
    if (not isinstance(narrow.get("original_sha256"), str)
            or not SHA.fullmatch(narrow["original_sha256"])
            or multi.get("original_sha256") != narrow["original_sha256"]):
        raise ContractError("DERIVATIVES_DISAGREE_ON_ORIGINAL_REFERENCE")
    provinces = multi.get("provinces")
    if not isinstance(provinces, list):
        raise ContractError("NO_PROVINCES_IN_DERIVATIVE")
    matches = [p for p in provinces if isinstance(p, dict) and p.get("province_id") == "ALBACETE"]
    if len(matches) != 1 or matches[0].get("province_label") != "ALBACETE":
        raise ContractError("AMBIGUOUS_PROVINCE_JOIN")
    original_scope = narrow.get("scope")
    left = narrow.get("lists")
    right = matches[0].get("lists")
    if (not isinstance(original_scope, dict) or original_scope.get("province") != "Albacete"
            or original_scope.get("national_coverage_claimed") is not False
            or not isinstance(left, list) or not isinstance(right, list)
            or not left or len(left) != len(right)
            or len(left) != original_scope.get("proclaimed_lists")
            or len(right) != matches[0].get("congress_candidacies")):
        raise ContractError("DERIVATIVE_LIST_COUNT_MISMATCH")
    # Check exact ordinal+acronym comparison, never a person crosswalk.
    for index, (a, b) in enumerate(zip(left, right), start=1):
        if (not isinstance(a, dict) or not isinstance(b, dict)
                or type(a.get("order")) is not int or a["order"] != index
                or type(b.get("position")) is not int or b["position"] != index
                or not isinstance(a.get("acronym"), str) or not a["acronym"]
                or a["acronym"] != b.get("acronym")
                or a.get("entity_type") != "ELECTORAL_CANDIDACY_LABEL"
                or b.get("entity_semantics") != "ELECTORAL_LIST_NOT_REGISTERED_PARTY"
                or a.get("registered_party_id") is not None
                or b.get("legal_party_registration_id") is not None
                or a.get("named_person_count") != 0
                or b.get("person_count_joined") != 0):
            raise ContractError("DERIVATIVE_LABEL_ALIGNMENT_MISMATCH")
    return {
        "status": "SAME_ORIGINAL_TWO_DERIVATIVES_AGREE_LOCAL_ONLY",
        "versioned_derivative_sha256": {
            "single_province": sha_narrow, "multi_province": sha_multi
        },
        "candidacy_label_ordinals_aligned": len(left),
        "real_people_compared": 0, "legal_party_id_asserted": 0,
        "original_pdf_bytes_replayed_here": False,
        "independent_publisher_verification": False,
        "first_public_at_verified": False,
        "congress_initiatives_inferred": 0,
        "scientific_result": False,
    }
