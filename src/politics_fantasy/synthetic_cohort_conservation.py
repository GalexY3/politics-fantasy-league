"""Conservative synthetic cohort stock/flow and competing-risk QA.

Two clocks: cut_on is the legal event-time boundary; as_of is local knowledge.
The identity N_received = N_terminal + N_positive_pending_at_cut + N_unknown
partitions visible *fictional* episodes only. It DOES NOT establish an
independent all-received denominator or prove unknowns survived.
A positive pending witness from earlier than cut_on is never carried forward.
"""
from __future__ import annotations

from dataclasses import dataclass

from .denominator_lineage_contract import PopulationTarget
from .procedural_index_contract import GateError, day, utc
from .procedural_stage_accounting import (
    EntryEpisode, ReintroductionClaim, TERMINAL, safe,
)

MAX_EPISODES=500
MAX_LINKS=500


@dataclass(frozen=True)
class CohortCut:
    cut_on:str
    as_of:str

    def __post_init__(self):
        if day(self.cut_on)>utc(self.as_of).date():
            raise GateError("COHORT_CUT_EVENT_TIME_AFTER_CAPTURE")


def _status(episode:EntryEpisode,*,cut:CohortCut):
    """Evidence known at as_of about an event-time legal cut."""
    available=[
        a for a in episode.acts
        if day(a.occurred_on)<=day(cut.cut_on) and safe(a.observed_at)<=utc(cut.as_of)
    ]
    endings=[a for a in available if a.stage in TERMINAL]
    if len(endings)>1:
        raise GateError("CONFLICTING_TERMINAL_EVENTS_FOR_CUT")
    pending=[
        p for p in episode.pending
        if day(p.pending_on)==day(cut.cut_on) and safe(p.observed_at)<=utc(cut.as_of)
    ]
    if endings and pending:
        raise GateError("SAME_CUT_TERMINAL_AND_POSITIVE_PENDING_CONTRADICT")
    if endings:
        return endings[0].stage
    if pending:
        return "PENDING_POSITIVE_EXACT_CUT"
    return "UNKNOWN_NOT_OBSERVED_AT_CUT"


def _visible(episodes:tuple[EntryEpisode,...],cut:CohortCut):
    return {
        e.episode_id:e for e in episodes
        if day(e.entry_on)<=day(cut.cut_on) and safe(e.entry_observed_at)<=utc(cut.as_of)
    }


def audit_cuts(*,frame:PopulationTarget,
               episodes:tuple[EntryEpisode,...],
               early:CohortCut,late:CohortCut,
               reintroductions:tuple[ReintroductionClaim,...]=())->dict:
    """Two documentary views of fiction, never a real hazard or causal result."""
    if (not isinstance(frame,PopulationTarget)
            or not frame.institution.startswith("SYNTHETIC_")
            or type(episodes) is not tuple or len(episodes)>MAX_EPISODES
            or type(reintroductions) is not tuple or len(reintroductions)>MAX_LINKS
            or not isinstance(early,CohortCut) or not isinstance(late,CohortCut)
            or day(early.cut_on)>=day(late.cut_on)
            or utc(early.as_of)!=utc(late.as_of)
            or any(not isinstance(e,EntryEpisode) or e.frame!=frame for e in episodes)
            or any(not isinstance(x,ReintroductionClaim) for x in reintroductions)):
        raise GateError("INVALID_OR_UNLICENSED_SYNTHETIC_STOCK_FLOW_SCOPE")
    keys={e.episode_id for e in episodes}
    if len(keys)!=len(episodes):
        raise GateError("DUPLICATE_COHORT_EPISODE_ID")
    emap={e.episode_id:e for e in episodes}
    for link in reintroductions:
        if (link.earlier_episode not in keys or link.later_episode not in keys):
            raise GateError("REINTRODUCTION_REFERENCES_UNOBSERVED_EPISODE")
        if (day(emap[link.earlier_episode].entry_on)>=
                day(emap[link.later_episode].entry_on)):
            raise GateError("REINTRODUCTION_NOT_FORWARD_IN_EVENT_TIME")
    base={
        "schema":"pfl.synthetic_cohort_stock_flow.v1",
        "mode":"SYNTHETIC_ONLY_NO_REAL_CASES",
        "R5_empirical_gate_passed":False,
        "all_received_denominator":None,
        "independent_auditor_denominator":None,
        "right_censored_real_cases":None,
        "historical_first_public_at":None,
        "source_original_sha_verified":False,
        "AB_cycles_executed":0,
        "no_missingness_imputation":True,
        "two_event_cuts_use_same_capture_knowledge":True,
    }
    known={e.episode_id:e for e in episodes if safe(e.entry_observed_at)<=utc(early.as_of)}
    if not known:
        return {**base,"status":"NO_SYNTHETIC_COHORT_SOURCE_KNOWN_AS_OF",
                "early":None,"late":None,
                "newly_registered_between_cuts":None,
                "documented_terminal_transitions_between_cuts":None,
                "reintroduction_claims_known_at_later_cut":None,
                "stock_conservation_certified":False}

    def describe(cut:CohortCut):
        visible=_visible(episodes,cut)
        counts={k:0 for k in sorted(TERMINAL)}
        counts.update({"PENDING_POSITIVE_EXACT_CUT":0,
                       "UNKNOWN_NOT_OBSERVED_AT_CUT":0})
        status={}
        for episode_id,e in visible.items():
            state=_status(e,cut=cut)
            counts[state]+=1
            status[episode_id]=state
        assert len(visible)==sum(counts.values())
        return {
            "cut_on":cut.cut_on,
            "registered_episodes_visible":len(visible),
            "known_terminal_by_cause":{k:counts[k] for k in sorted(TERMINAL)},
            "positive_pending_on_exact_cut":counts["PENDING_POSITIVE_EXACT_CUT"],
            "unknown_followup_or_older_pending":counts["UNKNOWN_NOT_OBSERVED_AT_CUT"],
            "accounting_equals_visible_synthetic_rows":True,
            "censored_case_count":None,
        },status

    first,s0=describe(early)
    second,s1=describe(late)
    arrivals=set(s1)-set(s0)
    departures={
        k:sum(s0.get(key) not in TERMINAL and v==k for key,v in s1.items()
              if key in s0)
        for k in sorted(TERMINAL)
    }
    new_same_interval_terminals={
        k:sum(s1[key]==k for key in arrivals)
        for k in sorted(TERMINAL)
    }
    if any(s0.get(key) in TERMINAL and s0[key]!=s1.get(key) for key in s0):
        raise GateError("TERMINAL_EVENT_REVERSED_BETWEEN_CUTS")
    claims=sum(link.earlier_episode in s1 and link.later_episode in s1
               for link in reintroductions)
    return {**base,"status":"SYNTHETIC_DOCUMENTARY_STOCK_FLOW_ONLY",
            "early":first,"late":second,
            "newly_registered_between_cuts":len(arrivals),
            "documented_terminal_transitions_between_cuts":departures,
            "terminal_claims_among_newly_registered":new_same_interval_terminals,
            "terminal_transitions_counted_only_for_earlier_registered":True,
            "reintroduction_claims_known_at_later_cut":claims,
            "same_episode_only_once_per_cut":True,
            "terminal_state_not_inferred_from_absence":True,
            "old_pending_not_carried_forward_to_later_cut":True,
            "stock_conservation_certified":False,
            "meaning_of_counts":"SYNTHETIC_KNOWN_SOURCE_LOCAL_EPISODES_ONLY",
            "failing_independent_denominator_gate":True}
