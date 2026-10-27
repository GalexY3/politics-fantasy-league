"""Illustrative fantasy scoring contract, NOT a social valuation of politicians."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from typing import Mapping
from .events import PoliticalEvent, as_utc, observable_event_revisions


@dataclass(frozen=True)
class Rule:
    version: str
    weights: Mapping[str, float]
    per_kind_week_cap: Mapping[str, int]


DEMO_RULE = Rule(
    "demo-0.1-SYNTHETIC",
    {"speech_recorded": 2.0, "question_registered": 1.5, "initiative_registered": 3.0},
    {"speech_recorded": 3, "question_registered": 5, "initiative_registered": 2},
)


def person_week_points(
    events: list[PoliticalEvent], *, person_id: str, start: datetime, end: datetime,
    knowledge_cutoff: datetime, rule: Rule = DEMO_RULE,
) -> float:
    """Observed events in [start,end), published by cutoff; missing data NEVER assigned zero quality."""
    start, end, knowledge_cutoff = map(as_utc, (start, end, knowledge_cutoff))
    if end <= start or knowledge_cutoff < end:
        raise ValueError("Round must close before score is finalized")
    counts: dict[str, int] = {}
    for event in observable_event_revisions(events, as_of=knowledge_cutoff):
        if person_id not in event.person_ids or not (start <= as_utc(event.occurred_at) < end):
            continue
        if event.kind not in rule.weights:
            continue  # explicit unknown, not an implicit negative score
        counts[event.kind] = counts.get(event.kind, 0) + 1
    return float(sum(rule.weights[k] * min(counts[k], rule.per_kind_week_cap[k])
                     for k in counts))


def league_points(
    events: list[PoliticalEvent], *, lineup: tuple[str, ...],
    start: datetime, end: datetime, cutoff: datetime, rule: Rule = DEMO_RULE,
) -> float:
    if len(lineup) != len(set(lineup)):
        raise ValueError("Cannot select same figure twice")
    return sum(person_week_points(events, person_id=p, start=start, end=end,
                                  knowledge_cutoff=cutoff, rule=rule) for p in lineup)
