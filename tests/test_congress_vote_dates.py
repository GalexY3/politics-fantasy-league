"""Negative and real-source format regression tests for C09."""
import pytest
from politics_fantasy.congress_vote_dates import normalized_vote_date

@pytest.mark.parametrize("raw",["23/07/2026","23/7/2026","23/07/2026"])
def test_authentic_vote_date_spellings(raw):
    assert normalized_vote_date(raw)=="2026-07-23"

@pytest.mark.parametrize("raw",["31/02/2026","00/01/2026","23/13/2026","2026-07-23","7/23/2026","23/7/26","23/7/9999"," 23/7/2026","",None,True])
def test_invalid_or_out_of_scope_dates_fail_closed(raw):
    with pytest.raises(ValueError):normalized_vote_date(raw)
