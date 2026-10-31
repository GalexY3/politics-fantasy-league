"""Local temporal-identity *prototype* for PFL. No network, no real-person scoring.

This is a complementary layer over existing PFL warehouse.py and
evidence_warehouse.mjs, NOT their replacement. Only sources *labelled* synthetic
can become query-visible in this test harness; caller-provided labels are NOT
proof of fiction or authenticity. Never expose this pure library to untrusted
inputs or real data. Historical official data require a separate, server-owned
provenance/rights/as-of registry that does not exist in this scratch prototype.

Valid time:  when a fact holds in the represented world (half-open interval).
Knowledge time: when that *revision* was public AND locally captured.
Neither document issue date nor an event date may be fabricated into first_public_at.
"""

from __future__ import annotations

import dataclasses
import hashlib
import json
import math
import re
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "pfl.scratch.temporal_evidence.v1"
HEX = re.compile(r"[0-9a-f]{64}\Z")
REF = re.compile(r"[A-Za-z0-9_.:-]{1,100}\Z")
KINDS = frozenset({"ENTITY", "EVENT", "ROLE", "RELATION"})
STATES = frozenset({"OBSERVED", "EXPLICIT_ZERO", "UNKNOWN", "NOT_OBSERVED"})
REAL_BLOCK = "REAL_SOURCE_REQUIRES_INDEPENDENT_RIGHTS_PROVENANCE_AND_ASOF_GATE"
MAX_FILE_BYTES = 6_000_000


class ContractError(ValueError):
    """An untrusted record violates the declared temporal/source contract."""


def _required_id(value: object, label: str) -> str:
    if not isinstance(value, str) or not REF.fullmatch(value):
        raise ContractError("INVALID_" + label)
    return value


def _utc(value: str, label: str) -> datetime:
    if not isinstance(value, str) or "T" not in value:
        raise ContractError("INVALID_" + label)
    try:
        dt = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ContractError("INVALID_" + label) from error
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise ContractError("NAIVE_" + label)
    return dt.astimezone(timezone.utc)


def _optional_utc(value: str | None, label: str) -> datetime | None:
    return None if value is None else _utc(value, label)


def _assert_exact(value: float | int | None, state: str) -> None:
    if state not in STATES:
        raise ContractError("INVALID_OBSERVATION_STATE")
    if state in {"UNKNOWN", "NOT_OBSERVED"}:
        if value is not None:
            raise ContractError("UNKNOWN_MUST_HAVE_NULL_VALUE")
    elif state == "EXPLICIT_ZERO":
        if type(value) not in (int, float) or value != 0:
            raise ContractError("ZERO_REQUIRES_EXACT_NUMERIC_ZERO")
    elif value is None or isinstance(value, bool):
        raise ContractError("OBSERVED_REQUIRES_NON_NULL_VALUE")


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ContractError("DUPLICATE_JSON_KEY")
        result[key] = value
    return result


def _reject_non_json_constant(value: str):
    raise ContractError("NON_FINITE_JSON_NUMBER_" + value)


def read_json_bound(path: Path) -> tuple[dict, bytes]:
    """Read only existing local JSON, reject duplicate keys and oversized files."""
    p = Path(path)
    if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
        raise ContractError("MISSING_OR_OVERSIZED_LOCAL_JSON")
    body = p.read_bytes()
    if len(body) > MAX_FILE_BYTES:
        raise ContractError("LOCAL_JSON_CHANGED_OR_OVERSIZED")
    try:
        payload = json.loads(body.decode("utf-8"), object_pairs_hook=_no_duplicate_keys,
                             parse_constant=_reject_non_json_constant)
    except (UnicodeError, ValueError) as error:
        raise ContractError("INVALID_LOCAL_JSON") from error
    if not isinstance(payload, dict):
        raise ContractError("EXPECTED_JSON_OBJECT")
    return payload, body


def sha256_file(path: Path) -> str:
    """Digest file bytes without using that digest as proof of publisher origin."""
    h = hashlib.sha256()
    with Path(path).open("rb") as stream:
        while chunk := stream.read(1024 * 1024):
            h.update(chunk)
    return h.hexdigest()


@dataclass(frozen=True, order=True)
class SourceRef:
    """Namespaced *source-local* identity, never a canonical human crosswalk."""

    authority: str
    family: str
    local_id: str

    def __post_init__(self) -> None:
        for name in ("authority", "family", "local_id"):
            _required_id(getattr(self, name), name.upper())

    @classmethod
    def parse(cls, value: list[str] | tuple[str, str, str]) -> SourceRef:
        if not isinstance(value, (tuple, list)) or len(value) != 3:
            raise ContractError("BAD_NAMESPACED_REFERENCE")
        return cls(*value)

    def wire(self) -> list[str]:
        return [self.authority, self.family, self.local_id]


@dataclass(frozen=True)
class FileReceipt:
    """Exact bytes check; rights and issuer authentication are NOT self-attested."""

    source_id: str
    sha256: str
    bytes: int
    captured_at: str
    origin: str  # SYNTHETIC or DOCUMENTED_REAL_UNADJUDICATED
    rights_state: str  # SYNTHETIC or RIGHTS_PENDING_REVIEW or CATALOG_LICENSE_ONLY

    def __post_init__(self) -> None:
        _required_id(self.source_id, "SOURCE_ID")
        if not HEX.fullmatch(self.sha256):
            raise ContractError("INVALID_SOURCE_SHA256")
        if type(self.bytes) is not int or not 0 < self.bytes <= MAX_FILE_BYTES:
            raise ContractError("INVALID_SOURCE_BYTE_SIZE")
        _utc(self.captured_at, "CAPTURED_AT")
        if self.origin not in {"SYNTHETIC", "DOCUMENTED_REAL_UNADJUDICATED"}:
            raise ContractError("UNSUPPORTED_SOURCE_ORIGIN")
        allowed = ({"SYNTHETIC"} if self.origin == "SYNTHETIC"
                   else {"RIGHTS_PENDING_REVIEW", "CATALOG_LICENSE_ONLY"})
        if self.rights_state not in allowed:
            raise ContractError("UNATTESTED_RIGHTS_ESCALATION")

    @classmethod
    def check_local(cls, path: Path, *, source_id: str, captured_at: str,
                    origin: str, rights_state: str,
                    expected_sha256: str | None = None) -> FileReceipt:
        p = Path(path)
        if not p.is_file() or p.stat().st_size > MAX_FILE_BYTES:
            raise ContractError("MISSING_OR_OVERSIZED_SOURCE")
        body = p.read_bytes()
        digest = hashlib.sha256(body).hexdigest()
        if expected_sha256 is not None and (
            not isinstance(expected_sha256, str)
            or not HEX.fullmatch(expected_sha256) or expected_sha256 != digest
        ):
            raise ContractError("SOURCE_DIGEST_MISMATCH")
        return cls(source_id, digest, len(body), captured_at, origin, rights_state)

    @property
    def query_admitted(self) -> bool:
        # Test harness only: a synthetics label is NOT proof a dataset is
        # fictional. The embedding application MUST reject untrusted callers.
        # Future real admission requires a separately attested trusted registry;
        # a user-supplied 'rights_verified=True' must not elevate evidence.
        return self.origin == "SYNTHETIC"


@dataclass(frozen=True)
class TemporalRecord:
    """One immutable published revision of a source-local documentary assertion."""

    kind: str
    source_id: str
    source_record_id: str  # EVENT: external source-event identity, not timestamp/name
    revision: str
    source_sha256: str
    subject: SourceRef
    predicate: str
    object: SourceRef | None
    valid_from: str
    valid_to: str | None
    first_public_at: str | None  # for THIS revision; None means UNKNOWN
    recorded_at: str  # local ingestion; never retroactively overridden
    observation_state: str = "OBSERVED"
    value: str | float | int | None = "DOCUMENTED"
    zero_basis: str | None = None

    def __post_init__(self) -> None:
        if self.kind not in KINDS:
            raise ContractError("UNSUPPORTED_RECORD_KIND")
        for name in ("source_id", "source_record_id", "revision", "predicate"):
            _required_id(getattr(self, name), name.upper())
        if not HEX.fullmatch(self.source_sha256):
            raise ContractError("INVALID_RAW_SHA256")
        if not isinstance(self.subject, SourceRef):
            raise ContractError("INVALID_SUBJECT_REFERENCE")
        if (self.kind in {"ENTITY", "EVENT"}
                and self.subject.authority != self.source_id):
            raise ContractError("SOURCE_ISSUED_NODE_SCOPE_MISMATCH")
        if self.kind in {"ROLE", "RELATION"}:
            if not isinstance(self.object, SourceRef):
                raise ContractError("ROLE_OR_RELATION_NEEDS_EXPLICIT_OBJECT")
        elif self.object is not None:
            raise ContractError("NODE_RECORD_HAS_OBJECT")
        if self.kind == "RELATION" and self.predicate.upper() in {
            "SAME_AS", "SAME_PERSON", "ALIAS_OF", "MEMBER_OF_POLITICAL_PARTY"
        }:
            raise ContractError("IDENTITY_OR_PRIVATE_MEMBERSHIP_UNATTESTED")
        a = _utc(self.valid_from, "VALID_FROM")
        b = _optional_utc(self.valid_to, "VALID_TO")
        if b is not None and b <= a:
            raise ContractError("INVALID_VALID_TIME_INTERVAL")
        if self.kind == "EVENT" and b is not None:
            raise ContractError("EVENT_IS_A_POINT_NOT_INTERVAL")
        known = _optional_utc(self.first_public_at, "FIRST_PUBLIC_AT")
        recorded = _utc(self.recorded_at, "RECORDED_AT")
        if known is not None and known > recorded:
            raise ContractError("REVISION_PUBLISHED_AFTER_CAPTURE")
        if self.kind == "EVENT" and known is not None and known < a:
            if not self.predicate.startswith("SCHEDULED_"):
                raise ContractError("OBSERVED_EVENT_PUBLIC_BEFORE_OCCURRED")
        if not isinstance(self.observation_state, str):
            raise ContractError("INVALID_OBSERVATION_STATE")
        if (self.value is not None and type(self.value) not in (str, int, float)):
            raise ContractError("UNSUPPORTED_VALUE_TYPE")
        if type(self.value) is float and not math.isfinite(self.value):
            raise ContractError("NON_FINITE_VALUE")
        _assert_exact(self.value, self.observation_state)
        if self.observation_state == "EXPLICIT_ZERO":
            if self.zero_basis != "SOURCE_EXPLICIT_NUMERIC_ZERO":
                raise ContractError("UNSUPPORTED_ZERO_BASIS")
        elif self.zero_basis is not None:
            raise ContractError("ZERO_BASIS_NOT_APPLICABLE")

    @property
    def logical_key(self) -> tuple[str, str, str]:
        return (self.kind, self.source_id, self.source_record_id)

    @property
    def revision_key(self) -> tuple[str, str, str, str]:
        return (*self.logical_key, self.revision)

    def wire(self) -> dict:
        obj = dataclasses.asdict(self)
        obj["subject"] = self.subject.wire()
        obj["object"] = self.object.wire() if self.object is not None else None
        return obj


@dataclass(frozen=True)
class Snapshot:
    as_of: str
    valid_at: str
    records: tuple[TemporalRecord, ...]
    blocked_unknown_publication: int
    blocked_unadjudicated_source: int
    blocked_unresolved_reference: int
    scientific_grade: bool = False
    real_person_scoring: bool = False

    def state_of(self, kind: str, source_id: str, source_record_id: str) -> str:
        for r in self.records:
            if r.logical_key == (kind, source_id, source_record_id):
                return r.observation_state
        return "NOT_OBSERVED"  # NOT 0: there may be no observed denominator.


class TemporalLedger:
    """In-memory versioned assertions; caller cannot certify real data for itself."""

    def __init__(self) -> None:
        self._sources: dict[tuple[str, str], FileReceipt] = {}
        self._records: dict[tuple[str, str, str, str], TemporalRecord] = {}

    def register_source(self, receipt: FileReceipt) -> None:
        key = (receipt.source_id, receipt.sha256)
        previous = self._sources.get(key)
        if previous is not None and previous != receipt:
            raise ContractError("CONFLICTING_SOURCE_RECEIPT")
        self._sources[key] = receipt

    def add(self, record: TemporalRecord) -> str:
        receipt = self._sources.get((record.source_id, record.source_sha256))
        if receipt is None:
            raise ContractError("UNREGISTERED_SOURCE_DIGEST")
        if _utc(record.recorded_at, "RECORDED_AT") < _utc(receipt.captured_at, "CAPTURED_AT"):
            raise ContractError("RECORD_PREDATES_LOCAL_CAPTURE")
        key = record.revision_key
        if key in self._records:
            if self._records[key] != record:
                raise ContractError("SAME_SOURCE_EVENT_REVISION_CONFLICT")
            return "DEDUPLICATED_IDENTICAL"
        self._records[key] = record
        return "NEW_REVISION"

    def snapshot(self, *, as_of: str, valid_at: str | None = None,
                 event_start: str | None = None, event_end: str | None = None) -> Snapshot:
        t = _utc(as_of, "AS_OF")
        v = _utc(valid_at or as_of, "VALID_AT")
        if v > t:
            raise ContractError("VALID_AT_AFTER_KNOWLEDGE_CUTOFF")
        ev_start = _optional_utc(event_start, "EVENT_START")
        ev_end = _optional_utc(event_end, "EVENT_END")
        if ev_start is not None and ev_end is not None and ev_end <= ev_start:
            raise ContractError("INVALID_EVENT_WINDOW")

        candidates: dict[tuple[str, str, str], list[TemporalRecord]] = {}
        unknown, barred = 0, 0
        # The existence of a not-yet-captured record, including a blocked
        # source, cannot influence a historical diagnosis or a visible count.
        unresolved_revision_keys: set[tuple[str, str, str]] = set()
        for row in self._records.values():
            receipt = self._sources[(row.source_id, row.source_sha256)]
            if (_utc(receipt.captured_at, "CAPTURED_AT") > t
                    or _utc(row.recorded_at, "RECORDED_AT") > t):
                continue
            if not receipt.query_admitted:
                barred += 1
                continue
            if row.first_public_at is None:
                unknown += 1
                unresolved_revision_keys.add(row.logical_key)
                continue
            if _utc(row.first_public_at, "FIRST_PUBLIC_AT") <= t:
                candidates.setdefault(row.logical_key, []).append(row)

        # Choose the latest SOURCE-PUBLISHED revision *before* valid-time and
        # window filtering. If an already captured revision has no independently
        # established publication time, quarantine the *logical identity*, not
        # just the revision: selecting v1 could misrepresent the latest state.
        # A future captured revision cannot impose this quarantine retroactively.
        selected: list[TemporalRecord] = []
        for key, rows in sorted(candidates.items()):
            if key in unresolved_revision_keys:
                continue
            last_publication = max(_utc(x.first_public_at, "FIRST_PUBLIC_AT") for x in rows)
            last = [x for x in rows if _utc(x.first_public_at, "FIRST_PUBLIC_AT") == last_publication]
            if len(last) != 1:
                raise ContractError("AMBIGUOUS_SAME_TIME_SOURCE_REVISIONS")
            selected.append(last[0])

        def active(x: TemporalRecord) -> bool:
            start = _utc(x.valid_from, "VALID_FROM")
            end = _optional_utc(x.valid_to, "VALID_TO")
            if x.kind == "EVENT":
                return start <= v and (ev_start is None or start >= ev_start) and (
                    ev_end is None or start < ev_end)
            return start <= v and (end is None or v < end)

        visible = [x for x in selected if active(x)]
        # References are source-local and exact: source-name equality alone is
        # insufficient. A ROLE or RELATION is invisible unless both endpoints
        # themselves have eligible visible ENTITY/EVENT assertions at this cut.
        nodes = {x.subject for x in visible if x.kind in {"ENTITY", "EVENT"}
                 and x.observation_state == "OBSERVED"}
        unresolved = sum(x.subject not in nodes or x.object not in nodes
                         for x in visible if x.kind in {"ROLE", "RELATION"})
        results = [x for x in visible if x.kind in {"ENTITY", "EVENT"}
                   or (x.subject in nodes and x.object in nodes)]
        results.sort(key=lambda x: (x.kind, x.source_id, x.source_record_id, x.revision))
        return Snapshot(as_of, valid_at or as_of, tuple(results), unknown, barred, unresolved)

    def manifest(self) -> dict:
        """Deterministic audit manifest: no original bytes and no personal names."""
        src = [dataclasses.asdict(x) for _, x in sorted(self._sources.items())]
        rows = [x.wire() for _, x in sorted(self._records.items())]
        raw = json.dumps({"sources": src, "records": rows},
                         ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
        return {
            "schema": SCHEMA,
            "source_receipts": src,
            "source_receipt_count": len(src),
            "record_revision_count": len(rows),
            "canonical_contract_sha256": hashlib.sha256(raw).hexdigest(),
            "real_source_ingest_admitted": False,
            "historical_publication_authenticated": False,
            "complete_population": False,
            "real_person_scoring": False,
            "release_grade": False,
        }


def audit_real_documentary_only(path: Path, *, source_id: str, captured_at: str,
                                rights_state: str = "RIGHTS_PENDING_REVIEW",
                                expected_sha256: str | None = None) -> dict:
    """Read-only versioned real JSON smoke; *never* imports facts or outputs rows."""
    payload, body = read_json_bound(path)
    receipt = FileReceipt.check_local(
        path, source_id=source_id, captured_at=captured_at,
        origin="DOCUMENTED_REAL_UNADJUDICATED", rights_state=rights_state,
        expected_sha256=expected_sha256)
    # Compare the bytes read for schema with the bytes verified in the receipt:
    # fail if another process changed the source in between.
    if hashlib.sha256(body).hexdigest() != receipt.sha256:
        raise ContractError("REAL_SOURCE_CHANGED_BETWEEN_READS")
    schema_label = payload.get("schema", payload.get("dataset_class"))
    if not isinstance(schema_label, str) or len(schema_label) > 128:
        schema_label = "UNLABELLED_OR_INVALID_SCHEMA"
    return {
        "status": "BLOCKED_REAL_INGEST", "reason": REAL_BLOCK,
        "local_versioned_file_sha256": receipt.sha256,
        "local_file_bytes": receipt.bytes, "source_id": receipt.source_id,
        "local_json_schema_label": schema_label,
        "rights_state": receipt.rights_state, "first_public_at_verified": False,
        "records_imported": 0, "persons_exported": 0,
        "historical_asof_ready": False, "real_person_scoring": False,
        "release_grade": False,
    }
