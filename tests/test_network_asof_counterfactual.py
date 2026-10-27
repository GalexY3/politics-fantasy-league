from datetime import datetime, timezone
import pytest
from politics_fantasy.network import VoteRecord, covote_edges

def t(day): return datetime(2026,1,day,tzinfo=timezone.utc)
def v(vid,person,choice,occurred,published): return VoteRecord(vid,person,choice,t(occurred),t(published))

def test_future_only_votes_not_in_prior_asof_graph():
    past=[v('v1','A','YES',1,2),v('v1','B','YES',1,2),v('v2','A','NO',3,4),v('v2','B','YES',3,4)]
    future=[v('v3','A','YES',5,6),v('v3','B','YES',5,6)]
    assert covote_edges(past,as_of=t(4),min_joint=1)==covote_edges(past+future,as_of=t(4),min_joint=1)
    assert covote_edges(past+future,as_of=t(6),min_joint=1)[0]['joint_votes']==3

def test_conflicting_same_event_vote_rejected():
    rows=[v('v1','A','YES',1,2),v('v1','A','NO',1,2)]
    with pytest.raises(ValueError,match='Conflicting vote choice'):
        covote_edges(rows,as_of=t(4),min_joint=1)
