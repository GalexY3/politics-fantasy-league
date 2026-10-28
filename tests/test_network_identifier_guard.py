from datetime import datetime, timezone
import pytest
from politics_fantasy.network import VoteRecord,covote_edges

T=datetime(2026,10,27,tzinfo=timezone.utc)
AS=datetime(2026,10,28,tzinfo=timezone.utc)
def v(event,person,choice='YES'):
    return VoteRecord(event,person,choice,T,T)

def test_empty_event_id_does_not_manufacture_covote_edge():
    with pytest.raises(ValueError,match='INVALID_VOTE_OR_PERSON_ID'):
        covote_edges([v('','FICTIONAL_A'),v('','FICTIONAL_B')],as_of=AS,min_joint=1)

def test_missing_person_id_is_rejected():
    with pytest.raises(ValueError,match='INVALID_VOTE_OR_PERSON_ID'):
        covote_edges([v('vote1','   ')],as_of=AS,min_joint=1)

def test_separate_votes_have_no_joint_exposure():
    assert covote_edges([v('vote1','FICTIONAL_A'),v('vote2','FICTIONAL_B')],as_of=AS,min_joint=1)==[]

def test_same_named_vote_has_one_pair():
    edges=covote_edges([v('vote1','FICTIONAL_A'),v('vote1','FICTIONAL_B')],as_of=AS,min_joint=1)
    assert len(edges)==1
    assert edges[0]['joint_votes']==1 and edges[0]['agreements']==1
    assert edges[0]['status']=='DESCRIPTIVE_NOT_CAUSAL'
