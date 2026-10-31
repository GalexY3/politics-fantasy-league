"""Synthetic-only stage and censoring audit. Not an empirical estimator.

Registration, admission, termination and pending-at-cut need independent
evidence. No local capture implies historical publication; no missing
transition implies rejection or observed right censoring.
"""
from __future__ import annotations
from dataclasses import dataclass
from datetime import timedelta
from .denominator_lineage_contract import PopulationTarget
from .procedural_index_contract import GateError, ID, SHA, day, utc

TERMINAL=frozenset({"INADMITTED","WITHDRAWN","LAPSED","APPROVED","REJECTED","TRANSFERRED_OUT"})
STAGES=TERMINAL|{"ADMITTED","HEARD","REQUESTED_CORRECTION","RESUBMITTED"}
CHANNELS={"PAPER","ELECTRONIC","UNKNOWN","PAPER_ELECTRONIC_UNRECONCILED"}

def safe(stamp:str):
    return utc(stamp).replace(microsecond=0)+timedelta(seconds=1)

@dataclass(frozen=True)
class StageAct:
    stage:str
    occurred_on:str
    documented_on:str
    observed_at:str
    document_sha_claim:str
    first_public_at:None=None
    def __post_init__(self):
        if self.stage not in STAGES or self.first_public_at is not None:
            raise GateError("STAGE_OR_PUBLICATION_PROMOTION")
        if not isinstance(self.document_sha_claim,str) or not SHA.fullmatch(self.document_sha_claim):
            raise GateError("STAGE_SHA_CLAIM_INVALID")
        if not day(self.occurred_on)<=day(self.documented_on)<=utc(self.observed_at).date():
            raise GateError("STAGE_DATE_AFTER_DOCUMENT_OR_CAPTURE")

@dataclass(frozen=True)
class PendingWitness:
    pending_on:str
    observed_at:str
    document_sha_claim:str
    first_public_at:None=None
    def __post_init__(self):
        if self.first_public_at is not None or day(self.pending_on)>utc(self.observed_at).date():
            raise GateError("PENDING_DATE_OR_PUBLICATION_INVALID")
        if not isinstance(self.document_sha_claim,str) or not SHA.fullmatch(self.document_sha_claim):
            raise GateError("PENDING_SHA_CLAIM_INVALID")

@dataclass(frozen=True)
class EntryEpisode:
    episode_id:str
    frame:PopulationTarget
    entry_on:str
    entry_observed_at:str
    entry_sha_claim:str
    channel:str
    acts:tuple[StageAct,...]=()
    pending:tuple[PendingWitness,...]=()

    def __post_init__(self):
        if (not isinstance(self.episode_id,str)
                or not self.episode_id.startswith("SYNTHETIC:")
                or not ID.fullmatch(self.episode_id)
                or not isinstance(self.frame,PopulationTarget)
                or not self.frame.institution.startswith("SYNTHETIC_")):
            raise GateError("NON_SYNTHETIC_OR_UNKNOWN_FRAME")
        if self.channel not in CHANNELS or not isinstance(self.entry_sha_claim,str) or not SHA.fullmatch(self.entry_sha_claim):
            raise GateError("BAD_CHANNEL_OR_ENTRY_SHA")
        t=day(self.entry_on)
        if t<day(self.frame.window_first_day) or t>day(self.frame.window_last_day) or t>utc(self.entry_observed_at).date():
            raise GateError("ENTRY_NOT_IN_RISK_WINDOW_OR_CAPTURE")
        if (type(self.acts) is not tuple or len(self.acts)>40
                or type(self.pending) is not tuple or len(self.pending)>40):
            raise GateError("BAD_EVENT_RESOURCE_BUDGET")
        prior=t
        terminal=None
        for act in self.acts:
            if not isinstance(act,StageAct):
                raise GateError("BAD_STAGE_ACT")
            at=day(act.occurred_on)
            if at<prior or terminal is not None:
                raise GateError("BACKDATED_OR_POST_TERMINAL_ACT")
            if self.frame.entry_rule=="ADMISSION_FIRST" and act.stage=="INADMITTED":
                raise GateError("INADMISSION_NOT_IN_ADMITTED_FIRST_FRAME")
            if act.stage in TERMINAL:
                terminal=at
            prior=at
        for witness in self.pending:
            if not isinstance(witness,PendingWitness):
                raise GateError("BAD_PENDING_WITNESS")
            pt=day(witness.pending_on)
            if pt<t or (terminal is not None and pt>=terminal):
                raise GateError("PENDING_WITNESS_CONTRADICTS_EVENT_HISTORY")

@dataclass(frozen=True)
class ReintroductionClaim:
    earlier_episode:str
    later_episode:str
    document_sha_claim:str
    basis:str="CLAIMED_OFFICIAL_CROSS_EPISODE_REFERENCE"
    independent_authority_verified:bool=False
    locally_observed_at:str|None=None
    def __post_init__(self):
        if (not all(isinstance(x,str) and x.startswith("SYNTHETIC:") and ID.fullmatch(x)
                    for x in (self.earlier_episode,self.later_episode))
                or self.earlier_episode==self.later_episode
                or not isinstance(self.document_sha_claim,str) or not SHA.fullmatch(self.document_sha_claim)
                or self.basis!="CLAIMED_OFFICIAL_CROSS_EPISODE_REFERENCE"
                or self.independent_authority_verified is not False):
            raise GateError("REINTRODUCTION_REQUIRES_UNVERIFIED_EXPLICIT_DUAL_IDS")
        if self.locally_observed_at is not None:
            utc(self.locally_observed_at)

def audit_lab(*,frame:PopulationTarget,episodes:tuple[EntryEpisode,...],
              as_of:str,claims:tuple[ReintroductionClaim,...]=())->dict:
    """Stage observations at locally witnessed cutoff; no real source rows."""
    t=utc(as_of)
    if (not isinstance(frame,PopulationTarget) or not frame.institution.startswith("SYNTHETIC_")
            or type(episodes) is not tuple or len(episodes)>500
            or type(claims) is not tuple or len(claims)>500
            or any(not isinstance(e,EntryEpisode) or e.frame!=frame for e in episodes)
            or any(not isinstance(l,ReintroductionClaim) for l in claims)):
        raise GateError("SYNTHETIC_ONLY_STAGE_AUDIT")
    records={e.episode_id:e for e in episodes}
    if len(records)!=len(episodes):
        raise GateError("DUPLICATE_EPISODES")
    for link in claims:
        if (link.earlier_episode not in records or link.later_episode not in records
                or day(records[link.earlier_episode].entry_on)>=day(records[link.later_episode].entry_on)):
            raise GateError("UNTRUSTED_REINTRODUCTION_LINK")
        if (link.locally_observed_at is not None
                and utc(link.locally_observed_at).date() <
                    day(records[link.later_episode].entry_on)):
            raise GateError("REINTRODUCTION_CLAIM_SEEN_BEFORE_LATER_ENTRY")
    visible=[e for e in episodes if safe(e.entry_observed_at)<=t]
    base={"schema":"pfl.synthetic_procedural_stage_audit.v1",
          "scientific_cycles":0,"real_outcomes_analyzed":False,
          "all_received_denominator":None,"first_public_at":None,
          "claim_sha_not_verified_original":True,
          "pending_absence_is_not_right_censoring":True}
    if not visible:
        return {**base,"status":"NO_LAB_INPUT_KNOWN_AT_CUT",
                "visible_episode_count":None,"terminal_by_cause":None,
                "observed_pending_at_last_witness":None,
                "unknown_followup":None,"reintroduction_claims_visible":None}
    endings={kind:0 for kind in sorted(TERMINAL)}
    observed_pending=unknown=0
    for e in visible:
        steps=[a for a in e.acts if safe(a.observed_at)<=t]
        end=next((a.stage for a in steps if a.stage in TERMINAL),None)
        if end is not None:
            endings[end]+=1
        elif any(safe(p.observed_at)<=t and day(p.pending_on)<=t.date() for p in e.pending):
            observed_pending+=1
        else:
            unknown+=1
    ids={e.episode_id for e in visible}
    return {**base,"status":"LAB_ONLY_NOT_EMPIRICAL",
            "visible_episode_count":len(visible),
            "terminal_by_cause":endings,
            "observed_pending_at_last_witness":observed_pending,
            "unknown_followup":unknown,
            "reintroduction_claims_visible":len({
                (l.earlier_episode,l.later_episode) for l in claims
                if l.earlier_episode in ids and l.later_episode in ids
                and l.locally_observed_at is not None
                and safe(l.locally_observed_at)<=t}),
            "replayed_or_multiple_documents_are_one_claimed_relation":True,
            "reintroduction_without_observation_is_unknown":True,
            "later_pending_status_not_inferred":True,
            "reintroduction_claim_is_not_verified_identity":True}
