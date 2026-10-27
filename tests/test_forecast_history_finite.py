from datetime import datetime,timezone
import math
import pytest
from politics_fantasy.forecast import historical_rate

T=datetime(2026,3,1,tzinfo=timezone.utc); START=datetime(2026,1,1,tzinfo=timezone.utc)
@pytest.mark.parametrize('bad', [{'exposure':float('nan')},{'exposure':1.5},{'exposure':True},{'prior_events':float('nan')},{'prior_exposure':float('inf')},{'prior_exposure':float('nan')}])
def test_bad_prior_or_exposure(bad):
 with pytest.raises(ValueError):historical_rate([],person_id='synthetic',start=START,as_of=T,exposure=3,**bad) if 'exposure' not in bad else historical_rate([],person_id='synthetic',start=START,as_of=T,**bad)

def test_good_history_rate():
 result=historical_rate([],person_id='synthetic',start=START,as_of=T,exposure=3)
 assert result.event_rate==0.2 and result.observed_history==0
