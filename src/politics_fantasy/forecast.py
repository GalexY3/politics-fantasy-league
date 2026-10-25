"""Prequential baseline with explicit information availability: demo, not fitted to Spanish politics."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import log, exp
from typing import Iterable
from .events import PoliticalEvent, as_utc, unique_events


@dataclass(frozen=True)
class Prediction:
    person_id: str
    prediction_as_of: datetime
    expected_events: float
    event_rate: float
    observed_history: int
    eligible_exposure: int
    status: str = "DEMO_BASELINE_UNVALIDATED"


def historical_rate(
    events: Iterable[PoliticalEvent], *, person_id: str,
    as_of: datetime, start: datetime, exposure: int, prior_events: float = 1.0,
    prior_exposure: float = 2.0,
) -> Prediction:
    """Posterior mean of a rate given eligible opportunities, Gamma-Poisson smoothing.

    `exposure` must reflect known historical opportunities; it cannot be future
    event count. A prediction requires a separate future exposure forecast.
    """
    as_of, start = as_utc(as_of), as_utc(start)
    if start >= as_of or exposure < 0 or prior_events <= 0 or prior_exposure <= 0:
        raise ValueError("Invalid history cutoff or nonpositive prior")
    history = [e for e in unique_events(list(events)) if
               person_id in e.person_ids and start <= as_utc(e.occurred_at) < as_of and
               e.observable_at(as_of) and not e.kind.startswith("scheduled_")]
    n = len(history)
    rate = (n + prior_events) / (exposure + prior_exposure)
    return Prediction(person_id, as_of, rate, rate, n, exposure)


def poisson_log_loss(y: int, lam: float) -> float:
    """Poisson negative log likelihood up to a y-only constant; for model comparison."""
    if y < 0 or lam <= 0:
        raise ValueError("Invalid y or lambda")
    return lam - y * log(lam)


def rolling_origin_splits(weeks: list[str], min_train: int, horizon: int = 1):
    """Chronological expanding-window folds; no random shuffling and no re-use of future."""
    if len(weeks) != len(set(weeks)) or weeks != sorted(weeks):
        raise ValueError("Weeks must be unique and sorted ISO dates")
    if min_train < 2 or horizon < 1:
        raise ValueError("Invalid split parameters")
    for test_begin in range(min_train, len(weeks) - horizon + 1):
        yield weeks[:test_begin], weeks[test_begin:test_begin + horizon]