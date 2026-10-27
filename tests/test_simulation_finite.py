import math
import pytest
from politics_fantasy.simulation import gini, simulate_auction

@pytest.mark.parametrize('v',[float('nan'),float('inf'),-1,2])
def test_volatility_rejected(v):
    with pytest.raises(ValueError):simulate_auction(volatility=v)

@pytest.mark.parametrize('v',[float('nan'),float('inf')])
def test_popularity_rejected(v):
    with pytest.raises(ValueError):simulate_auction(popularity_weight=v)

@pytest.mark.parametrize('v',[float('nan'),float('inf')])
def test_nonfinite_inequality_rejected(v):
    with pytest.raises(ValueError):gini([1,v])

def test_valid_market_still_stable():
    d=simulate_auction(seed=47,clubs=10,assets=100,rounds=12)
    assert math.isfinite(d.price_gini) and 0<=d.price_gini<=1
    assert math.isfinite(d.mean_value) and d.mean_value>0
