"""C09: synthetic opportunity exposure forecast units; no political calibration."""
from datetime import datetime, timezone
import pytest
from politics_fantasy.forecast import Prediction, expected_events_for_future_exposure


def pred(rate=0.25):
    return Prediction('FICTIONAL', datetime(2026,10,28,tzinfo=timezone.utc),
                      rate,rate,2,8)


@pytest.mark.parametrize('exposure,count', [(0,0.0),(1,0.25),(5,1.25)])
def test_projected_count_requires_explicit_future_exposure(exposure,count):
    assert expected_events_for_future_exposure(pred(),future_exposure=exposure)==pytest.approx(count)


@pytest.mark.parametrize('bad', [-1,1.5,True,'5'])
def test_invalid_future_exposure_is_not_a_valid_count(bad):
    with pytest.raises(ValueError,match='INVALID_FORECAST_EXPOSURE_OR_RATE'):
        expected_events_for_future_exposure(pred(),future_exposure=bad)


def test_invalid_rate_is_rejected_even_if_future_count_is_zero():
    with pytest.raises(ValueError,match='INVALID_FORECAST_EXPOSURE_OR_RATE'):
        expected_events_for_future_exposure(pred(float('inf')),future_exposure=0)


def test_legacy_one_opportunity_field_is_not_a_future_horizon_forecast():
    p=pred()
    assert p.expected_events==p.event_rate
    assert expected_events_for_future_exposure(p,future_exposure=5)==5*p.event_rate
