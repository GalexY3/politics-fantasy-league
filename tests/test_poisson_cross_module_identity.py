"""All synthetic; identity of loss contracts, not an empirical forecast validation."""
from math import lgamma
import pytest
from politics_fantasy.forecast import poisson_log_loss
from politics_fantasy.evaluation import poisson_nll, relative_skill

@pytest.mark.parametrize('y',range(9))
@pytest.mark.parametrize('lam',[0.1,0.5,1.,2.,10.])
def test_partial_vs_full_poisson_nll(y,lam):
    short=poisson_log_loss(y,lam)
    full=poisson_nll(y,lam)
    assert full-short == pytest.approx(lgamma(y+1),abs=1e-12)

@pytest.mark.parametrize('model,baseline,expected',[(1.,2.,.5),(2.,1.,-1.),(0.,0.,None)])
def test_relative_skill_baseline_conventions(model,baseline,expected):
    assert relative_skill(model,baseline) == expected
