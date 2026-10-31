"""Offline structural check of explicit registry-entry -> case references.

REGISTRATION and EXPEDIENTE are distinct units and may be many-to-many.
Only an explicitly referenced dual identifier is a *candidate* edge.
The SHA and URL in supplied rows are untrusted claims until original bytes,
rights and document authority are independently verified by a server-owned
source registry. This module never certifies those facts, and never reads
outcomes or invents a first-public timestamp.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Iterable
from urllib.parse import urlsplit

from .procedural_index_contract import (
    FrameScope, GateError, ID, NAMESPACE, SHA, MAX_CASES, day, utc,
)


@dataclass(frozen=True)
class ScopedRef:
    institution: str
    legislature: str
    family: str
    namespace: str
    local_id: str

    def __post_init__(self) -> None:
        if (not NAMESPACE.fullmatch(self.institution)
                or not ID.fullmatch(self.legislature)
                or not NAMESPACE.fullmatch(self.family)
                or not NAMESPACE.fullmatch(self.namespace)
                or not ID.fullmatch(self.local_id)):
            raise GateError("INVALID_INSTITUTION_SCOPED_REFERENCE")

    def matches(self, scope: FrameScope) -> bool:
        return (self.institution == scope.institution
                and self.legislature == scope.legislature
                and self.family == scope.family)


@dataclass(frozen=True)
class EntryRef:
    key: ScopedRef
    received_on: str

    def __post_init__(self) -> None:
        if not isinstance(self.key, ScopedRef):
            raise GateError("BAD_REGISTER_REFERENCE")
        day(self.received_on)


@dataclass(frozen=True)
class CaseRef:
    key: ScopedRef
    file_opened_on: str | None = None

    def __post_init__(self) -> None:
        if not isinstance(self.key, ScopedRef):
            raise GateError("BAD_CASE_REFERENCE")
        if self.file_opened_on is not None:
            day(self.file_opened_on)


@dataclass(frozen=True)
class DualIdDocumentLink:
    entry: ScopedRef
    case: ScopedRef
    claimed_original_sha256: str
    claimed_official_uri: str
    document_dated_on: str | None = None
    relation_basis: str = "CLAIMED_EXPLICIT_DUAL_ID_IN_ORIGINAL"
    first_public_at: None = None

    def __post_init__(self) -> None:
        if not isinstance(self.entry, ScopedRef) or not isinstance(self.case, ScopedRef):
            raise GateError("BAD_DOCUMENT_LINK_KEYS")
        if (not isinstance(self.claimed_original_sha256, str)
                or not SHA.fullmatch(self.claimed_original_sha256)):
            raise GateError("DOCUMENT_ORIGINAL_SHA_CLAIM_MISSING")
        if (not isinstance(self.claimed_official_uri, str)
                or len(self.claimed_official_uri) > 1500):
            raise GateError("DOCUMENT_SOURCE_URI_INVALID")
        url = urlsplit(self.claimed_official_uri)
        if (url.scheme != "https" or not url.hostname or url.username
                or url.password or url.port or url.fragment):
            raise GateError("DOCUMENT_SOURCE_URI_INVALID")
        if self.relation_basis != "CLAIMED_EXPLICIT_DUAL_ID_IN_ORIGINAL":
            raise GateError("LINK_BY_NAME_TITLE_OR_DATE_FORBIDDEN")
        if self.first_public_at is not None:
            raise GateError("DOCUMENT_FIRST_PUBLICATION_NOT_ESTABLISHED")
        if self.document_dated_on is not None:
            day(self.document_dated_on)


def audit_explicit_links(
    *, scope: FrameScope, entries: Iterable[EntryRef],
    cases: Iterable[CaseRef], links: Iterable[DualIdDocumentLink],
    capture_completed_at: str, as_of: str | None = None,
) -> dict:
    """Summarize structural evidence only; never claim all-received coverage.

    This function deliberately has no argument that promotes alleged source
    claims to verified rights, official link authority or a scientific frame.
    Before its local capture cutoff it suppresses counts *and diagnostics*,
    avoiding future availability leaks. It exposes no original identifiers.
    """
    if not isinstance(scope, FrameScope):
        raise GateError("INVALID_FRAME_SCOPE")
    if scope.risk_entry != "SOURCE_REPORTED_REGISTRATION":
        raise GateError("LINK_AUDIT_REQUIRES_REGISTRATION_ENTRY_FRAME")
    captured = utc(capture_completed_at)
    safe = captured.replace(microsecond=0) + timedelta(seconds=1)
    cutoff = utc(as_of) if as_of is not None else None
    base = {
        "schema": "pfl.procedural_dual_id_link_audit.v1",
        "first_public_at": None,
        "historical_public_predictor_admitted": False,
        "real_original_bytes_verified_by_this_module": False,
        "official_link_authority_independently_verified": False,
        "rights_to_use_identifiers_adjudicated": False,
        "complete_all_received_register_independently_verified": False,
        "denominator_for_survival_estimation": None,
        "statuses_or_terminal_outcomes_admitted": False,
        "unknown_is_not_rejection": True,
        "scientific_cycles": 0,
    }
    if cutoff is not None and cutoff < safe:
        return {**base, "status": "LINK_SNAPSHOT_NOT_KNOWN_AT_CUT",
                "source_scope": None, "local_capture_safe_by": None,
                "entry_rows": None, "file_rows": None, "document_links": None,
                "linked_entries": None, "linked_files": None}
    e, c, l = tuple(entries), tuple(cases), tuple(links)
    if len(e) > MAX_CASES or len(c) > MAX_CASES or len(l) > 4*MAX_CASES:
        raise GateError("LINK_INPUT_RESOURCE_BUDGET_EXCEEDED")
    if (any(not isinstance(x, EntryRef) for x in e)
            or any(not isinstance(x, CaseRef) for x in c)
            or any(not isinstance(x, DualIdDocumentLink) for x in l)):
        raise GateError("LINK_INPUT_TYPE_INVALID")
    all_keys = [x.key for x in (*e, *c)]
    if any(not x.matches(scope) for x in all_keys):
        raise GateError("CROSS_SCOPE_ENTRY_OR_FILE")
    for x in l:
        if not x.entry.matches(scope) or not x.case.matches(scope):
            raise GateError("CROSS_SCOPE_DOCUMENT_RELATION")
        if x.entry.namespace == x.case.namespace:
            raise GateError("REGISTRY_AND_CASE_NAMESPACE_COLLAPSED")
        if x.document_dated_on is not None and day(x.document_dated_on) > captured.date():
            raise GateError("DOCUMENT_DATE_AFTER_CAPTURE")
    if any(day(x.received_on) > captured.date() for x in e):
        raise GateError("REGISTRATION_DATE_AFTER_CAPTURE")
    if any(x.file_opened_on is not None and day(x.file_opened_on) > captured.date()
           for x in c):
        raise GateError("FILE_DATE_AFTER_CAPTURE")
    ek, ck = {x.key for x in e}, {x.key for x in c}
    if len(ek) != len(e) or len(ck) != len(c):
        raise GateError("DUPLICATE_SOURCE_LOCAL_ID")
    entry_namespaces = {key.namespace for key in ek}
    case_namespaces = {key.namespace for key in ck}
    if entry_namespaces & case_namespaces:
        raise GateError("MIXED_REGISTRY_AND_CASE_ID_NAMESPACE")
    if any(x.entry.namespace in case_namespaces
           or x.case.namespace in entry_namespaces for x in l):
        raise GateError("MIXED_REGISTRY_AND_CASE_ID_NAMESPACE")
    # Identical link-document replays are not independent corroboration.
    relation_doc = {(x.entry, x.case, x.claimed_original_sha256) for x in l}
    if len(relation_doc) != len(l):
        raise GateError("DUPLICATE_LINK_DOCUMENT_REPLAY")
    relationships = {(x.entry, x.case) for x in l}
    linked_e = {a for a,b in relationships if a in ek and b in ck}
    linked_c = {b for a,b in relationships if a in ek and b in ck}
    entry_date = {x.key: day(x.received_on) for x in e}
    per_entry = {key: set() for key in ek}
    per_file = {key: set() for key in ck}
    for a,b in relationships:
        if a in ek and b in ck:
            per_entry[a].add(b)
            per_file[b].add(a)
    return {
        **base, "status": "DOCUMENTARY_LINK_CANDIDATES_NOT_SCIENTIFIC_ADMISSION",
        "source_scope": scope.label(),
        "local_capture_safe_by": safe.isoformat(),
        "entry_rows": len(ek), "file_rows": len(ck),
        "document_links": len(l),
        "unique_claimed_dual_id_relations": len(relationships),
        "linked_entries": len(linked_e), "linked_files": len(linked_c),
        "entries_without_documented_file_link_in_this_snapshot": len(ek-linked_e),
        "files_without_documented_entry_link_in_this_snapshot": len(ck-linked_c),
        "candidate_links_referring_to_unobserved_entries": sum(a not in ek for a,b in relationships),
        "candidate_links_referring_to_unobserved_files": sum(b not in ck for a,b in relationships),
        "entries_with_multiple_file_links": sum(len(v)>1 for v in per_entry.values()),
        "files_with_multiple_entry_links": sum(len(v)>1 for v in per_file.values()),
        "links_dated_before_entry_as_documentary_anomalies": sum(
            x.document_dated_on is not None
            and x.entry in ek
            and day(x.document_dated_on)<entry_date[x.entry]
            for x in l),
        "link_orphan_is_not_negative_decision": True,
        "relations_only_claimed_until_origins_separately_replayed": True,
    }
