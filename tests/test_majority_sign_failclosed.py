"""C03 preregistered synthetic validity controls; never a claim about actual deputies."""
import pytest
from politics_fantasy.majority_sign import compare_ballot


def ballot(votes, totals=None):
    return {'totales': totals or {'si':9, 'no':3}, 'votos': votes}


def test_overlap_across_yes_no_does_not_become_strict_reversal():
    assert compare_ballot(ballot({'S': 'a b', 'N': 'a b c d'})) == 'INVALID_DUPLICATE_NOMINAL_CODE'


def test_duplicate_within_single_option_is_rejected():
    assert compare_ballot(ballot({'S': 'a a', 'N': 'b c d'})) == 'INVALID_DUPLICATE_NOMINAL_CODE'


def test_unknown_option_not_masked_as_a_nominal_ballot():
    assert compare_ballot(ballot({'Y': 'a'})) == 'INVALID_NOMINAL_SCHEMA'


def test_nonstring_vote_list_not_silently_accepted():
    assert compare_ballot(ballot({'S':['a'], 'N':'b'})) == 'INVALID_NOMINAL_SCHEMA'


@pytest.mark.parametrize('totals', [{'si':True, 'no':3},{'si':9.0, 'no':3},{'si':-1, 'no':3}])
def test_invalid_yes_no_counts_rejected(totals):
    assert compare_ballot(ballot({'S':'a', 'N':'b'}, totals)) == 'INVALID_TOTALS'


def test_disjoint_direction_reversal_is_still_distinguished():
    assert compare_ballot(ballot({'S':'a b', 'N':'c d e'})) == 'STRICT_REVERSAL'


def test_disjoint_tie_and_absent_nominal_still_work():
    assert compare_ballot(ballot({'S':'a', 'N':'b'})) == 'TIE_INVOLVED'
    assert compare_ballot(ballot({'S':'', 'N':''})) == 'NO_NOMINAL'
