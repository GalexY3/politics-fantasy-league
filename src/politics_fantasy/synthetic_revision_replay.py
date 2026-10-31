"""Version-aware institutional process replay, strictly synthetic.

Independent entry books, case files, explicit dual-ID documents, and dated
decisions are different source revisions. Their latest *locally captured*
revisions must be chosen separately at as_of; using an event/document date
as public availability would leak future information.

No evidence is ever promoted to a certified real denominator. All IDs must
use a synthetic namespace. A published version deleting an entry does NOT
prove the case was rejected, withdrawn, censored or never submitted.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import timedelta
from typing import Literal

from .denominator_lineage_contract import PopulationTarget
from .procedural_index_contract import GateError, ID, NAMESPACE, SHA, utc, day

ROLES={"ENTRY_BOOK","CASE_LEDGER","EXPLICIT_DUAL_ID","DECISION_EVENTS"}
TERMINAL={"INADMITTED","WITHDRAWN","LAPSED","APPROVED","REJECTED","TRANSFERRED_OUT"}
MAX_REVISIONS=500
MAX_CLAIMS=10000


def _sid(value:str) -> bool:
    return isinstance(value,str) and value.startswith("SYNTHETIC:") and bool(ID.fullmatch(value))


def _casekey(value:str,kind:str) -> bool:
    # A raw sequence number is not a globally unique registration identity:
    # institution is in the frame, and authority/channel namespace is in key.
    if not _sid(value):
        return False
    parts=value.split(":")
    return (len(parts)==5 and parts[:2]==["SYNTHETIC",kind]
            and bool(NAMESPACE.fullmatch(parts[2]))
            and bool(NAMESPACE.fullmatch(parts[3]))
            and bool(ID.fullmatch(parts[4])))


def _after_capture(value:str,precision:str):
    date=utc(value)
    if precision=="DATE":
        if date.time().isoformat() not in ("00:00:00","00:00:00+00:00"):
            raise GateError("DATE_CAPTURE_REQUIRES_MIDNIGHT_UTC")
        return date+timedelta(days=1)
    if precision=="SECOND":
        return date.replace(microsecond=0)+timedelta(seconds=1)
    if precision=="EXACT":
        return date
    raise GateError("BAD_CAPTURE_PRECISION")


def _capture_interval(rev):
    """Uncertainty interval for a source's captured clock, not publication."""
    end=_after_capture(rev.captured_at,rev.precision)
    when=utc(rev.captured_at)
    if rev.precision=="DATE":
        return (when,end)
    if rev.precision=="SECOND":
        return (when.replace(microsecond=0),end)
    return (when,when)


def _overlap(first,second):
    a,b=_capture_interval(first)
    c,d=_capture_interval(second)
    if a==b:
        return c<=a<d if c!=d else a==c
    if c==d:
        return a<=c<b
    return a<d and c<b


@dataclass(frozen=True)
class DualIdClaim:
    entry_id:str
    case_id:str
    basis:str="EXPLICIT_TWO_OFFICIAL_IDS_CLAIM"
    def __post_init__(self):
        if not (_casekey(self.entry_id,"REG") and _casekey(self.case_id,"CASE")
                and self.basis=="EXPLICIT_TWO_OFFICIAL_IDS_CLAIM"):
            raise GateError("CROSS_NAMESPACE_OR_UNEVIDENCED_ID_JOIN")


@dataclass(frozen=True)
class EventClaim:
    case_id:str
    state:str
    event_on:str
    document_on:str
    def __post_init__(self):
        if (not _casekey(self.case_id,"CASE")
                or self.state not in TERMINAL|{"ADMITTED","PENDING_AT_DOCUMENT_DATE"}
                or day(self.event_on)>day(self.document_on)):
            raise GateError("UNSAFE_EVENT_CLAIM_OR_TIME")


@dataclass(frozen=True)
class SourceRevision:
    revision_id:str
    source_id:str
    frame:PopulationTarget
    role:str
    captured_at:str
    precision:Literal["DATE","SECOND","EXACT"]
    original_sha_claim:str
    entries:tuple[str,...]=()
    cases:tuple[str,...]=()
    links:tuple[DualIdClaim,...]=()
    events:tuple[EventClaim,...]=()
    first_public_at:None=None
    all_received_certified:bool=False
    independent_denominator_certified:bool=False

    def __post_init__(self):
        if (not _sid(self.revision_id) or not _sid(self.source_id)
                or not isinstance(self.frame,PopulationTarget)
                or not self.frame.institution.startswith("SYNTHETIC_")
                or self.role not in ROLES
                or not isinstance(self.original_sha_claim,str)
                or not SHA.fullmatch(self.original_sha_claim)
                or self.first_public_at is not None
                or self.all_received_certified is not False
                or self.independent_denominator_certified is not False):
            raise GateError("REVISION_NOT_SYNTHETIC_OR_SCIENCE_PROMOTION")
        _after_capture(self.captured_at,self.precision)
        fields=(self.entries,self.cases,self.links,self.events)
        if any(type(v) is not tuple or len(v)>MAX_CLAIMS for v in fields):
            raise GateError("REVISION_RESOURCE_BUDGET_EXCEEDED")
        allowed={
            "ENTRY_BOOK":(True,False,False,False),
            "CASE_LEDGER":(False,True,False,False),
            "EXPLICIT_DUAL_ID":(False,False,True,False),
            "DECISION_EVENTS":(False,False,False,True),
        }[self.role]
        if any(bool(x) and not permitted for x,permitted in zip(fields,allowed)):
            raise GateError("HETEROGENEOUS_EVENT_GRAIN_COLLAPSE")
        if (any(not _casekey(x,"REG") for x in self.entries)
                or any(not _casekey(x,"CASE") for x in self.cases)
                or any(not isinstance(x,DualIdClaim) for x in self.links)
                or any(not isinstance(x,EventClaim) for x in self.events)):
            raise GateError("UNAUTHORIZED_CASE_ID_OR_TYPE")
        if len(set(self.entries))!=len(self.entries) or len(set(self.cases))!=len(self.cases):
            raise GateError("DUPLICATED_IDENTIFIERS_IN_ONE_REVISION")
        if len(set(self.links))!=len(self.links):
            raise GateError("REPLAYED_LINK_CLAIM_IN_ONE_REVISION")
        if len(set(self.events))!=len(self.events):
            raise GateError("REPLAYED_EVENT_IN_ONE_REVISION")
        if any(day(x.document_on)>utc(self.captured_at).date() for x in self.events):
            raise GateError("DOCUMENTED_EVENT_AFTER_CAPTURE")


def replay(*,target:PopulationTarget,revisions:tuple[SourceRevision,...],as_of:str)->dict:
    """Return source-version *synthetic* structural QA, never real outcomes."""
    cut=utc(as_of)
    if (not isinstance(target,PopulationTarget)
            or not target.institution.startswith("SYNTHETIC_")
            or type(revisions) is not tuple or len(revisions)>MAX_REVISIONS
            or any(not isinstance(x,SourceRevision) or x.frame!=target for x in revisions)):
        raise GateError("REAL_OR_MIXED_INSTITUTION_REPLAY_FORBIDDEN")
    ids={x.revision_id for x in revisions}
    if len(ids)!=len(revisions):
        raise GateError("DUPLICATE_REVISION_ID")
    visible=[x for x in revisions if _after_capture(x.captured_at,x.precision)<=cut]
    base={
        "schema":"pfl.synthetic_revision_replay.v1",
        "mode":"SYNTHETIC_LAB_NOT_EMPIRICAL",
        "scientific_cycles":0,
        "real_originals_verified":False,
        "right_to_process_real_cases":False,
        "independent_all_received_denominator":None,
        "actual_population_membership":None,
        "first_public_at":None,
        "historical_public_predictor_certified":False,
        "unobserved_is_not_rejection_withdrawal_or_censor":True,
    }
    if not visible:
        return {**base,"status":"NO_LOCAL_SNAPSHOT_KNOWN_AT_CUT",
                "source_revisions_visible":None,"visible_entry_ids":None,
                "visible_case_ids":None,"dual_id_edges_valid_in_visible_frames":None,
                "orphan_link_claims":None,"terminal_claims_by_type":None,
                "pending_at_document_date_claims":None,
                "registered_without_documented_case_link":None}
    # Every revision supersedes only earlier revisions of its OWN source and
    # ROLE; revisions of different issuers/units are not additive vintages.
    latest={}
    for x in visible:
        key=(x.source_id,x.role)
        current=latest.get(key)
        if current is not None and _overlap(current,x):
            raise GateError("CONFLICTING_REVISIONS_SAME_SOURCE_AND_INSTANT")
        if current is not None and current.original_sha_claim==x.original_sha_claim:
            if ((current.entries,current.cases,current.links,current.events)
                    !=(x.entries,x.cases,x.links,x.events)):
                raise GateError("SAME_ORIGINAL_SHA_CANNOT_CHANGE_DOCUMENTED_ROWS")
        if current is None or _after_capture(x.captured_at,x.precision)>_after_capture(
                current.captured_at,current.precision):
            latest[key]=x
    entries={x for rev in latest.values() for x in rev.entries}
    cases={x for rev in latest.values() for x in rev.cases}
    links={x for rev in latest.values() for x in rev.links}
    events={x for rev in latest.values() for x in rev.events}
    linked={(x.entry_id,x.case_id) for x in links
            if x.entry_id in entries and x.case_id in cases}
    terminals={s:0 for s in sorted(TERMINAL)}
    # Not case-based hazards: deduplicate repeated terminal claims and
    # identify contradiction instead of inventing which disposition prevailed.
    claims={}
    for ev in events:
        if ev.case_id in cases and ev.state in TERMINAL:
            claims.setdefault(ev.case_id,set()).add(ev.state)
    conflicting=sum(len(v)>1 for v in claims.values())
    for states in claims.values():
        if len(states)==1:
            terminals[next(iter(states))]+=1
    return {
        **base,"status":"VISIBLE_SYNTHETIC_SOURCE_REVISIONS_ONLY",
        "source_revisions_visible":len(latest),
        "visible_entry_ids":len(entries),
        "visible_case_ids":len(cases),
        "dual_id_edges_valid_in_visible_frames":len(linked),
        "orphan_link_claims":len(links)-len(linked),
        "registered_without_documented_case_link":len(entries-{a for a,_ in linked}),
        "terminal_claims_by_type":terminals,
        "contradictory_terminal_claims_quarantined":conflicting,
        "pending_at_document_date_claims":sum(
            ev.state=="PENDING_AT_DOCUMENT_DATE" and ev.case_id in cases for ev in events),
        "pending_at_document_date_not_followup_cut":True,
        "repeated_revisions_not_new_cases":True,
        "unlinked_is_not_inadmitted":True,
    }
