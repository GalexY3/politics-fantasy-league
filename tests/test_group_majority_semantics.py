"""C07: group plurality vs strict majority, all synthetic rows and explicit denominators."""
from datetime import date
import pytest

from politics_fantasy.groupvotes import GroupRow, majority, strict_majority


def row(yes, no, abstain, no_vote):
    return GroupRow('vote-SYN', date(2026, 10, 28), 'FICTIONAL-GROUP',
                    yes, no, abstain, no_vote, 1)


def test_plurality_is_not_an_absolute_majority():
    r=row(4,3,2,0)
    assert majority(r)=='YES'  # legacy modal vote is 4/9
    assert strict_majority(r)=='NO_ABSOLUTE_MAJORITY'


def test_expressed_majority_and_recorded_group_denominator_disagree():
    r=row(6,3,0,9)
    assert majority(r)=='YES'
    assert strict_majority(r,denominator='EXPRESSED_ONLY')=='YES'  # 6/9
    assert strict_majority(r,denominator='ALL_RECORDED_STATUSES')=='NO_ABSOLUTE_MAJORITY'  # 6/18


def test_strict_absolute_majority_is_reached_with_both_denominators():
    r=row(6,3,0,0)
    assert strict_majority(r)=='YES'
    assert strict_majority(r,denominator='ALL_RECORDED_STATUSES')=='YES'


def test_tied_modal_candidates_not_forced():
    r=row(1,1,0,0)
    assert majority(r)=='TIE'
    assert strict_majority(r)=='TIE'


def test_explicit_nonvoters_only_no_expressed():
    r=row(0,0,0,9)
    assert majority(r)=='NO_EXPRESSED_CHOICE'
    assert strict_majority(r)=='NO_EXPRESSED_CHOICE'


def test_unknown_denominator_fail_closed():
    with pytest.raises(ValueError, match='UNKNOWN_GROUP_DENOMINATOR'):
        strict_majority(row(1,0,0,0),denominator='GROUP_REGISTER_MEMBERS')


def test_abstention_can_be_strict_majority_as_separate_observed_option():
    r=row(2,1,5,0)
    assert strict_majority(r)=='ABSTAIN'
