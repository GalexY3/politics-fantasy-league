"""C12: group-level modal report must not misstate plurality as a strict majority."""
from datetime import date
from politics_fantasy.groupvotes import GroupRow
from politics_fantasy.groupmetrics import group_vote_measure

def r(yes,no,abst):
    return GroupRow('s202-v01',date(2026,9,30),'SYNTHETIC-GROUP',yes,no,abst,0,2)

def test_modal_four_of_nine_not_majority():
    x=group_vote_measure(r(4,3,2))
    assert x['majority']=='YES'  # Legacy documented modal field.
    assert x['majority_kind']=='MODAL_EXPRESSED_NOT_STRICT'
    assert x['strict_majority']=='NO_ABSOLUTE_MAJORITY'
    assert x['nonmodal_choices']==5
    assert x['dissent_from_group_majority'] is None

def test_genuine_majority_and_tie():
    x=group_vote_measure(r(6,3,0))
    assert x['strict_majority']=='YES'
    assert x['dissent_from_group_majority']==3
    y=group_vote_measure(r(1,1,0))
    assert y['strict_majority']=='TIE'
    assert y['dissent_from_group_majority'] is None
