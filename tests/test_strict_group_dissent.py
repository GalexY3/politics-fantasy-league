"""MAIN20B C04: synthetic majority/plurality estimand, no real MPs or party-discipline claims."""
from datetime import datetime, timezone
import pytest
from politics_fantasy.rollcall import NominalVote
from politics_fantasy.sociometrics import (
    majority_by_group_vote, dissent_report,
    strict_majority_by_group_vote, strict_majority_dissent_report,
)
from politics_fantasy.lab import local_lab_report

T=datetime(2026,1,1,tzinfo=timezone.utc)


def row(person, choice, vote="vote-fictional", group="G-fictional"):
    return NominalVote(vote,person,group,choice,T,T,T,
                       "https://example.invalid/fiction", "0"*64)


def fixture(yes, no, abstain, no_vote=0):
    records=[]
    for choice,n in (("YES",yes),("NO",no),("ABSTAIN",abstain),("NO_VOTE",no_vote)):
        for _ in range(n):
            records.append(row("P"+str(len(records)+1),choice))
    return records


def test_plurality_is_not_strict_majority_or_definable_strict_dissent():
    records=fixture(4,3,2)
    assert majority_by_group_vote(records)[("vote-fictional","G-fictional")]=="YES"
    assert strict_majority_by_group_vote(records)[("vote-fictional","G-fictional")] is None
    assert sum(x["dissent"] for x in dissent_report(records).values())==5
    strict=strict_majority_dissent_report(records)
    assert sum(x["eligible_expressed"] for x in strict.values())==0
    assert all(x["rate"] is None and x["excluded"]==1 for x in strict.values())


def test_true_strict_majority_allows_nonmajority_choice_counts():
    r=fixture(6,3,0)
    assert strict_majority_by_group_vote(r)[("vote-fictional","G-fictional")]=="YES"
    out=strict_majority_dissent_report(r)
    assert sum(x["eligible_expressed"] for x in out.values())==9
    assert sum(x["dissent"] for x in out.values())==3
    assert {x["criterion"] for x in out.values()}=={"STRICT_GT_HALF_OF_EXPRESSED_GROUP_ROWS"}


def test_abstain_can_be_strict_majority_and_no_vote_excluded():
    r=fixture(1,1,4,2)
    assert strict_majority_by_group_vote(r)[("vote-fictional","G-fictional")]=="ABSTAIN"
    out=strict_majority_dissent_report(r)
    assert sum(x["eligible_expressed"] for x in out.values())==6
    assert sum(x["dissent"] for x in out.values())==2
    assert sum(x["excluded"] for x in out.values())==2


def test_ties_and_heterogeneous_mixto_group_excluded():
    tie=fixture(1,1,0)
    assert strict_majority_by_group_vote(tie)[("vote-fictional","G-fictional")] is None
    assert all(x["rate"] is None for x in strict_majority_dissent_report(tie).values())
    mixed=[row("P1","YES",group="Mixto"),row("P2","YES",group="Mixto")]
    assert sum(x["eligible_expressed"] for x in strict_majority_dissent_report(mixed).values())==0


def test_duplicate_person_vote_rejected_by_shared_baseline():
    x=row("same","YES")
    with pytest.raises(ValueError,match="Unresolved duplicate"):
        strict_majority_by_group_vote([x,x])


def test_local_lab_declares_strict_not_modal_comparison():
    out=local_lab_report()
    assert out["dissent_criterion"]=="STRICT_GT_HALF_OF_EXPRESSED_GROUP_ROWS"
    assert out["real_politician_scoring"] is False
    assert out["value_grade"]["scientific_novelty_grade"]==0
