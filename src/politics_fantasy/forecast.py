"""Prequential baseline with explicit information availability: demo, not fitted to Spanish politics."""
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from math import log, exp, isfinite
from typing import Iterable
from .events import PoliticalEvent, as_utc, observable_event_revisions


@dataclass(frozen=True)
class Prediction:
    person_id: str
    prediction_as_of: datetime
    expected_events: float  # Legacy one-opportunity standardized value; NOT a future-horizon count.
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
    if (start >= as_of or type(exposure) is not int or exposure < 0
            or not isfinite(prior_events) or prior_events <= 0
            or not isfinite(prior_exposure) or prior_exposure <= 0):
        raise ValueError("Invalid history cutoff or nonpositive prior")
    history = [e for e in observable_event_revisions(list(events), as_of=as_of) if
               person_id in e.person_ids and start <= as_utc(e.occurred_at) < as_of and
               not e.kind.startswith("scheduled_")]
    n = len(history)
    rate = (n + prior_events) / (exposure + prior_exposure)
    return Prediction(person_id, as_of, rate, rate, n, exposure)



def expected_events_for_future_exposure(
    prediction: Prediction, *, future_exposure: int
) -> float:
    """Count forecast conditional on a *separately justified* future opportunity count.

    historical_rate().event_rate is the expected count per historical eligible
    opportunity. Neither observed events nor past exposure determine how many
    future opportunities will occur; do not silently assume this exposure.
    This helper is a deterministic projection, NOT calibrated for real politics.
    """
    if (not isinstance(prediction, Prediction) or type(future_exposure) is not int
            or future_exposure < 0 or not isfinite(prediction.event_rate)
            or prediction.event_rate < 0):
        raise ValueError('INVALID_FORECAST_EXPOSURE_OR_RATE')
    count = prediction.event_rate * future_exposure
    if not isfinite(count):
        raise ValueError('NONFINITE_FORECAST_COUNT')
    return float(count)


def poisson_log_loss(y: int, lam: float) -> float:
    """Poisson negative log likelihood up to a y-only constant; for model comparison."""
    if type(y) is not int or y < 0 or not isfinite(lam) or lam <= 0:
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
