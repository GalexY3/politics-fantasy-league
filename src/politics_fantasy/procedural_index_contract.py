"""Offline contract for admission of a *candidate* parliamentary risk frame.

Nothing in this module downloads data, accesses outcomes, authenticates a
publisher, approves rights or counts a real AB-H experiment. A coherent
multi-page index remains a publisher's *own* index, not proof that all initial
registrations, inadmissions, terminal failures or historical revisions exist.

Any calls on externally supplied pages are untrusted exploration, and any
actual user/political source needs an independently verified rights-and-byte
registry outside this module before public or scientific admission.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from hashlib import sha256
import json
import re
from typing import Iterable
from urllib.parse import urlsplit
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

SHA = re.compile(r"[0-9a-f]{64}\Z")
NAMESPACE = re.compile(r"[A-Z][A-Z0-9_]{2,50}\Z")
ID = re.compile(r"[A-Za-z0-9_.:/-]{1,160}\Z")
MAX_PAGES = 600
MAX_CASES = 150_000
MAX_SPAN_SECONDS = 3600
LEGAL_CIVIL_ZONES = frozenset({"UTC", "Europe/Madrid", "Atlantic/Canary"})


class GateError(ValueError):
    """Page or source contract invalid, not a finding on political processes."""


def utc(stamp: str) -> datetime:
    if not isinstance(stamp, str) or "T" not in stamp or len(stamp) > 42:
        raise GateError("INVALID_TIMESTAMP")
    try:
        dt = datetime.fromisoformat(stamp.replace("Z", "+00:00"))
    except ValueError as exc:
        raise GateError("INVALID_TIMESTAMP") from exc
    if dt.tzinfo is None or dt.utcoffset() is None:
        raise GateError("TIMESTAMP_NEEDS_TZ")
    return dt.astimezone(timezone.utc)


def day(stamp: str) -> date:
    if not isinstance(stamp, str) or len(stamp) != 10:
        raise GateError("INVALID_EVENT_DATE")
    try:
        parsed = date.fromisoformat(stamp)
    except ValueError as exc:
        raise GateError("INVALID_EVENT_DATE") from exc
    if parsed.isoformat() != stamp:
        raise GateError("NONCANONICAL_EVENT_DATE")
    return parsed


def legal_civil_date(stamp: str, legal_calendar_zone: str) -> date:
    """Civil day in a *declared* legal jurisdiction, never UTC.date by default.

    This calendar contract is synthetic tooling: it does not authenticate the
    jurisdiction or convert a legal day into historical publication evidence.
    """
    if type(legal_calendar_zone) is not str or legal_calendar_zone not in LEGAL_CIVIL_ZONES:
        raise GateError("LEGAL_CALENDAR_ZONE_REQUIRED")
    try:
        return utc(stamp).astimezone(ZoneInfo(legal_calendar_zone)).date()
    except ZoneInfoNotFoundError as exc:
        raise GateError("LEGAL_CALENDAR_TZDATA_UNAVAILABLE") from exc


def legal_day_completed(*, cut_on: str, as_of: str, legal_calendar_zone: str) -> bool:
    """True only after the NEXT local midnight (DST-aware) has been reached."""
    cut = day(cut_on)
    legal_civil_date(as_of, legal_calendar_zone)  # validate both clock and zone
    try:
        next_midnight = datetime.combine(
            cut + timedelta(days=1), time.min,
            tzinfo=ZoneInfo(legal_calendar_zone)
        ).astimezone(timezone.utc)
    except (OverflowError, ZoneInfoNotFoundError) as exc:
        raise GateError("LEGAL_CIVIL_BOUNDARY_UNAVAILABLE") from exc
    return utc(as_of) >= next_midnight


@dataclass(frozen=True)
class FrameScope:
    institution: str
    legislature: str
    family: str
    risk_entry: str
    selection_rule: str
    registry_scope: str

    def __post_init__(self):
        if (not NAMESPACE.fullmatch(self.institution)
                or not ID.fullmatch(self.legislature)
                or not NAMESPACE.fullmatch(self.family)
                or self.risk_entry not in {"SOURCE_REPORTED_REGISTRATION", "OFFICIAL_PRESENTATION", "OFFICIAL_ADMISSION"}
                or self.selection_rule not in {"ALL_REGISTERED_AT_RISK", "PUBLICATIONS_ONLY", "UNKNOWN"}
                or self.registry_scope not in {"PARTIAL_EDITORIAL_INDEX", "ALL_PRESENTED_CLAIM_UNATTESTED"}):
            raise GateError("INVALID_FRAME_SCOPE")

    def label(self) -> str:
        return f"{self.institution}:{self.legislature}:{self.family}:{self.risk_entry}"


@dataclass(frozen=True)
class CaseRef:
    local_id: str
    entry_occurred_on: str | None

    def __post_init__(self):
        if not isinstance(self.local_id, str) or not ID.fullmatch(self.local_id):
            raise GateError("BAD_CASE_ID")
        if self.entry_occurred_on is not None:
            day(self.entry_occurred_on)


@dataclass(frozen=True)
class PageEvidence:
    page: int
    expected_pages: int
    next_page: int | None
    source_sha256: str
    source_url: str
    captured_at: str
    source_reported_total: int | None
    scope: FrameScope
    cases: tuple[CaseRef, ...]
    original_rights: str
    status_columns_inspected: bool = False
    first_public_at: str | None = None

    def __post_init__(self):
        if (type(self.page) is not int or type(self.expected_pages) is not int
                or not 1 <= self.page <= self.expected_pages <= MAX_PAGES):
            raise GateError("INVALID_PAGE_NUMBER")
        if (self.next_page is not None
                and (type(self.next_page) is not int or self.next_page != self.page + 1)):
            raise GateError("PAGINATION_NOT_FORWARD_CONTIGUOUS")
        if not isinstance(self.source_sha256, str) or not SHA.fullmatch(self.source_sha256):
            raise GateError("MISSING_OR_INVALID_RAW_SHA")
        if (not isinstance(self.source_url, str) or len(self.source_url) > 1500
                or not self.source_url.startswith("https://")
                or "@" in self.source_url.split("/", 3)[2]):
            raise GateError("INVALID_OFFICIAL_URL_CANDIDATE")
        utc(self.captured_at)
        if (self.source_reported_total is not None
                and (type(self.source_reported_total) is not int
                     or not 0 <= self.source_reported_total <= MAX_CASES)):
            raise GateError("INVALID_EDITORIAL_TOTAL")
        if (not isinstance(self.scope, FrameScope) or not isinstance(self.cases, tuple)
                or len(self.cases) > 1000
                or any(not isinstance(ref, CaseRef) for ref in self.cases)):
            raise GateError("INVALID_PAGE_CASES")
        if self.original_rights not in {"CATALOGUE_LICENSE_REVIEWED", "GENERAL_NOTICE_UNRESOLVED", "UNKNOWN"}:
            raise GateError("INVALID_RIGHTS_CLASS")
        if self.status_columns_inspected is not False or self.first_public_at is not None:
            raise GateError("OUTCOME_OR_HISTORICAL_PUBLICATION_PROMOTION")
        if any(ref.entry_occurred_on is not None and day(ref.entry_occurred_on) >
               utc(self.captured_at).date() for ref in self.cases):
            raise GateError("EVENT_DATE_AFTER_OBSERVATION")


@dataclass(frozen=True)
class FrameAudit:
    scope: FrameScope
    page_count: int
    expected_pages: int
    observed_case_rows: int
    distinct_case_keys: int
    duplicate_case_keys: int
    missing_entry_dates: int
    source_reported_total: int | None
    internal_publisher_count_equal: bool | None
    raw_capture_sha256: tuple[str, ...]
    capture_end: str
    missing_pages: tuple[int, ...]
    index_is_prospective_census: bool
    independent_entry_registry_proven: bool = False
    external_rights_adjudicated_for_science: bool = False
    historical_source_revisions_certified: bool = False
    historical_first_public_at: None = None
    dated_transitions_admitted: bool = False
    terminal_outcomes_admitted: bool = False
    denominator_eligible_for_survival: None = None

    def report(self, *, as_of: str | None = None) -> dict:
        """No counts at all before local *end of capture*, independent of event dates."""
        if as_of is not None and utc(as_of) < utc(self.capture_end):
            return {
                "status": "INDEX_NOT_YET_OBSERVED_AT_CUT",
                "source_scope": None, "page_count": None,
                "observed_case_rows": None, "publisher_total": None,
                "historical_first_public_at": None,
                "risk_population_denominator": None, "outcomes_admitted": False,
                "local_observation_is_first_public_at": False,
            }
        # Never expose case IDs, event dates, raw URLs or uncontrolled text.
        return {
            "status": "PUBLISHER_INDEX_INTERNAL_AUDIT_NOT_POPULATION_CENSUS",
            "source_scope": self.scope.label(),
            "page_count": self.page_count,
            "expected_pages": self.expected_pages,
            "missing_pages": list(self.missing_pages),
            "observed_case_rows": self.observed_case_rows,
            "distinct_case_keys": self.distinct_case_keys,
            "duplicate_case_keys": self.duplicate_case_keys,
            "missing_entry_dates": self.missing_entry_dates,
            "publisher_total": self.source_reported_total,
            "internal_publisher_count_equal": self.internal_publisher_count_equal,
            "publisher_index_complete_from_pagination": not bool(self.missing_pages),
            "all_registered_confirmed_by_independent_registry": False,
            "risk_population_denominator": None,
            "historical_first_public_at": None,
            "historical_asof_admitted": False,
            "transitions_admitted": False,
            "outcomes_admitted": False,
            "censoring_estimable": False,
            "original_hashes_count": len(self.raw_capture_sha256),
            "local_capture_safe_by": self.capture_end,
            "local_observation_is_first_public_at": False,
            "real_person_scoring": False,
        }


def audit_pages(pages: Iterable[PageEvidence], *, require_all_pages: bool = False) -> FrameAudit:
    """Analyze one capture series. Status/outcome fields are forbidden by contract.

    A consistent publisher index, even if it contains all reported rows,
    cannot certify the independent registration denominator. Pagination drift
    and partial pages are flagged rather than converted to missing outcomes.
    """
    rows = tuple(pages)
    if not rows or len(rows) > MAX_PAGES:
        raise GateError("INVALID_PAGE_SERIES")
    scope = rows[0].scope
    pages_expected = rows[0].expected_pages
    counts = {x.source_reported_total for x in rows}
    if (len(counts) != 1 or any(x.scope != scope or x.expected_pages != pages_expected for x in rows)):
        raise GateError("SOURCE_FILTER_OR_EDITORIAL_TOTAL_DRIFT")
    page_hosts = {urlsplit(x.source_url).hostname for x in rows}
    if len(page_hosts) != 1 or None in page_hosts:
        raise GateError("MIXED_SOURCE_HOSTS_OR_PUBLISHERS")
    order = [x.page for x in rows]
    if len(set(order)) != len(order) or order != sorted(order):
        raise GateError("DUPLICATE_OR_OUT_OF_ORDER_PAGES")
    if order[0] != 1 or any(b != a+1 for a, b in zip(order,order[1:])):
        raise GateError("NONCONTIGUOUS_PAGINATION")
    for x in rows:
        should_next = x.page + 1 if x.page < pages_expected else None
        if x.next_page != should_next:
            raise GateError("INVALID_PAGER_LINK")
    times = [utc(x.captured_at) for x in rows]
    if any(b < a for a,b in zip(times,times[1:])):
        raise GateError("NONMONOTONE_PAGE_CAPTURES")
    if (times[-1] - times[0]).total_seconds() > MAX_SPAN_SECONDS:
        raise GateError("CAPTURE_WINDOW_TOO_WIDE_FOR_STABLE_INDEX")
    if len({x.source_sha256 for x in rows}) != len(rows):
        raise GateError("REPLAYED_OR_DUPLICATE_SOURCE_PAGE")
    cases: dict[str, CaseRef] = {}
    repeated = 0
    for x in rows:
        for c in x.cases:
            if c.local_id in cases:
                if cases[c.local_id] != c:
                    raise GateError("CONTRADICTORY_SOURCE_CASE_ENTRY")
                repeated += 1
            else:
                cases[c.local_id] = c
        if len(cases) > MAX_CASES:
            raise GateError("TOO_MANY_CASES")
    missing = tuple(range(order[-1]+1, pages_expected+1))
    if missing and require_all_pages:
        raise GateError("MISSING_PAGES_AT_CENSUS_GATE")
    total = rows[0].source_reported_total
    concordant = (len(cases) == total) if total is not None and not missing else None
    if concordant is False:
        raise GateError("EDITORIAL_TOTAL_MISMATCH")
    # Conservative by-second bound: captures may have rounded or truncated
    # response clocks. This is never exact first public availability.
    end = times[-1].replace(microsecond=0) + timedelta(seconds=1)
    return FrameAudit(
        scope=scope, page_count=len(rows), expected_pages=pages_expected,
        observed_case_rows=sum(len(x.cases) for x in rows),
        distinct_case_keys=len(cases), duplicate_case_keys=repeated,
        missing_entry_dates=sum(c.entry_occurred_on is None for c in cases.values()),
        source_reported_total=total, internal_publisher_count_equal=concordant,
        raw_capture_sha256=tuple(x.source_sha256 for x in rows),
        capture_end=end.isoformat(), missing_pages=missing,
        index_is_prospective_census=False,
    )


def prospective_capture_delta(older: tuple[PageEvidence, ...],
                              newer: tuple[PageEvidence, ...]) -> dict:
    """Only aggregate source-local differences; not entry events or outcomes.

    Both snapshots must have all pages. An identical scope without certified
    entry coverage does not make missing IDs 'failures' or new IDs 'filings'.
    """
    a, b = audit_pages(older, require_all_pages=True), audit_pages(newer, require_all_pages=True)
    if a.scope != b.scope:
        raise GateError("CROSS_SCOPE_OR_INSTITUTIONAL_JOIN")
    if utc(a.capture_end) >= utc(b.capture_end):
        raise GateError("NONINCREASING_VINTAGE_ORDER")
    def by_id(records):
        return {c.local_id: c.entry_occurred_on for p in records for c in p.cases}
    left, right = by_id(older), by_id(newer)
    return {
        "schema": "pfl.procedural_index_delta.v1",
        "scope": a.scope.label(),
        "earlier_index_rows": len(left), "later_index_rows": len(right),
        "first_observed_only_in_later_index": len(right.keys() - left.keys()),
        "absent_from_later_index": len(left.keys() - right.keys()),
        "source_reported_entry_date_changed": sum(
            left[k] != right[k] for k in left.keys() & right.keys()),
        "appeared_is_not_filed_event": True,
        "disappeared_is_not_failed_outcome": True,
        "first_public_at": None,
        "events_or_outcomes_admitted": False,
        "real_person_scoring": False,
        "scientific_cycles": 0,
    }


@dataclass(frozen=True)
class RegistryEntry:
    """An observed registration, which may lack a later expediente assignment.

    This is an engineering contract only. The receipt/register provenance and
    rights must be independently adjudicated before any real-data admission.
    """
    entry_id: str
    received_on: str
    process_id: str | None = None
    first_public_at: None = None

    def __post_init__(self):
        if not isinstance(self.entry_id,str) or not ID.fullmatch(self.entry_id):
            raise GateError("BAD_REGISTER_ENTRY_ID")
        day(self.received_on)
        if self.process_id is not None and (
                not isinstance(self.process_id,str) or not ID.fullmatch(self.process_id)):
            raise GateError("BAD_LINKED_EXPEDIENTE_ID")
        if self.first_public_at is not None:
            raise GateError("REGISTER_FIRST_PUBLICATION_NOT_VERIFIED")


ALLOWED_STRUCTURAL_ACTS = frozenset({
    "RECEIPT_LOGGED", "REFERRED_TO_DESK", "FILE_ASSIGNED",
    "PUBLICATION_REFERENCE", "CORRECTION_RECORDED",
})


@dataclass(frozen=True)
class StructuralAct:
    """A neutral documentary operation, not a terminal outcome."""
    event_id: str
    process_id: str
    occurred_on: str
    event_kind: str
    first_public_at: None = None

    def __post_init__(self):
        if (not isinstance(self.event_id,str) or not ID.fullmatch(self.event_id)
                or not isinstance(self.process_id,str) or not ID.fullmatch(self.process_id)):
            raise GateError("BAD_STRUCTURAL_ACT_REFERENCE")
        day(self.occurred_on)
        if self.event_kind not in ALLOWED_STRUCTURAL_ACTS:
            raise GateError("TERMINAL_OUTCOME_KIND_FORBIDDEN")
        if self.first_public_at is not None:
            raise GateError("ACT_FIRST_PUBLICATION_NOT_VERIFIED")


def reconcile_registry_to_acts(*, scope: FrameScope,
                               entries: Iterable[RegistryEntry],
                               acts: Iterable[StructuralAct],
                               captured_at: str) -> dict:
    """Synthetic-only structural relationship QA, never an empirical lifecycle.

    Missing case assignments and unmatched documents are uncertainty, not
    failures. Every flag remains a source-metadata observation until the real
    registry witness/complete stream are separately authenticated.
    """
    if not isinstance(scope,FrameScope):
        raise GateError("UNKNOWN_INSTITUTIONAL_SCOPE")
    if scope.selection_rule != "ALL_REGISTERED_AT_RISK":
        raise GateError("REGISTER_FILTER_NOT_ALL_RECEIVED")
    t=utc(captured_at)
    registers=tuple(entries)
    events=tuple(acts)
    if len(registers)>MAX_CASES or len(events)>2*MAX_CASES:
        raise GateError("RESOURCE_BUDGET_EXCEEDED")
    if any(not isinstance(e,RegistryEntry) for e in registers):
        raise GateError("BAD_REGISTER_ROW")
    if any(not isinstance(e,StructuralAct) for e in events):
        raise GateError("BAD_EVENT_ROW")
    by_entry={}
    by_event={}
    for row in registers:
        if row.entry_id in by_entry:
            if by_entry[row.entry_id]!=row:
                raise GateError("DUPLICATE_REGISTER_ENTRY_CONFLICT")
            raise GateError("DUPLICATE_REGISTER_ENTRY_REPLAY")
        if day(row.received_on)>t.date():
            raise GateError("REGISTER_ISSUED_AFTER_CAPTURE")
        by_entry[row.entry_id]=row
    for row in events:
        if row.event_id in by_event:
            if by_event[row.event_id]!=row:
                raise GateError("DUPLICATE_EVENT_ID_CONFLICT")
            raise GateError("DUPLICATE_EVENT_ID_REPLAY")
        if day(row.occurred_on)>t.date():
            raise GateError("EVENT_AFTER_CAPTURE")
        by_event[row.event_id]=row
    associated={}
    for row in registers:
        if row.process_id is not None:
            associated.setdefault(row.process_id,[]).append(day(row.received_on))
    by_case_acts={}
    for row in events:
        by_case_acts.setdefault(row.process_id,[]).append(row)
    register_cases=set(associated)
    event_cases=set(by_case_acts)
    chronologically_anomalous=sum(
        day(act.occurred_on)<min(associated[act.process_id])
        for act in events if act.process_id in associated
    )
    return {
        "schema":"pfl.registry_structural_acts_audit.v1",
        "status":"SYNTHETIC_RELATIONSHIP_QA_ONLY",
        "scope":scope.label(),
        "recorded_entries":len(by_entry),
        "registered_entries_without_process_assignment":sum(e.process_id is None for e in registers),
        "distinct_linked_processes":len(register_cases),
        "structural_acts":len(by_event),
        "distinct_processes_with_acts":len(event_cases),
        "processes_in_both_register_and_act_stream":len(register_cases&event_cases),
        "registered_processes_without_act_in_this_stream":len(register_cases-event_cases),
        "act_stream_processes_without_registered_match":len(event_cases-register_cases),
        "act_dates_before_linked_register_date":chronologically_anomalous,
        "cross_institutional_matches_inferred":0,
        "unknown_is_not_failure":True,
        "unlinked_is_not_rejected":True,
        "source_first_public_at_verified":False,
        "eligible_registry_population_independently_verified":False,
        "events_from_real_sources_admitted":False,
        "terminal_outcomes_examined":False,
        "scientific_cycles":0,
    }
