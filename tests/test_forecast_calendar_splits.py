from datetime import date
import pytest
from politics_fantasy.forecast import rolling_origin_splits

@pytest.mark.parametrize('weeks', [
 ['ABC','DEF','GHI'],
 ['2026-02-01','2026-02-31','2026-03-07'],
 ['2026-W01-1','2026-01-12','2026-01-19'],
 ['2026-01-05','2026-01-05','2026-01-12']
])
def test_reject_noncanonical_or_invalid_calendar_weeks(weeks):
    with pytest.raises(ValueError,match='valid, unique and sorted ISO'):
        list(rolling_origin_splits(weeks,min_train=2))

@pytest.mark.parametrize('param', [{'min_train':True}, {'horizon':True}, {'horizon':1.5}])
def test_reject_noninteger_fold_parameters(param):
    args={'min_train':2,'horizon':1}
    args.update(param)
    with pytest.raises(ValueError,match='Invalid split parameters'):
        list(rolling_origin_splits(['2026-01-05','2026-01-12','2026-01-19'],**args))

def test_valid_folds_nonoverlapping_future():
    assert list(rolling_origin_splits(['2026-01-05','2026-01-12','2026-01-19'],2))==[
        (['2026-01-05','2026-01-12'],['2026-01-19'])
    ]
