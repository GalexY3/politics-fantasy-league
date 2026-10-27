from datetime import datetime,timezone
import math
import pytest
from politics_fantasy.network import VoteRecord,covote_edges
T=datetime(2026,10,20,tzinfo=timezone.utc)
V=[VoteRecord('synthetic-vote',pid,'YES',T,T) for pid in ('A','B')]
@pytest.mark.parametrize('params',[{'alpha':float('nan')},{'beta':float('inf')},{'alpha':float('-inf')},{'min_joint':float('nan')},{'min_joint':1.5},{'min_joint':True}])
def test_invalid_graph_params(params):
 with pytest.raises(ValueError):covote_edges(V,as_of=T,min_joint=1,**params) if 'min_joint' not in params else covote_edges(V,as_of=T,**params)
def test_valid_graph():
 x=covote_edges(V,as_of=T,min_joint=1)
 assert len(x)==1 and math.isfinite(x[0]['agreement_smoothed'])
