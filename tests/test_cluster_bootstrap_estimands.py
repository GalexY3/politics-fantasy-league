"""C05: session-equal versus record-equal estimands with clustered uncertainty.

All inputs are synthetic, not Spanish parliamentary observations.
"""
import pytest
from politics_fantasy.evaluation import (
    session_bootstrap_ci, record_weighted_cluster_bootstrap_ci,
)


def test_unbalanced_clusters_produce_different_legitimate_estimands():
    rows={'session-A':[0.0]*100, 'session-B':[10.0]}
    a=session_bootstrap_ci(rows, seed=42)
    b=record_weighted_cluster_bootstrap_ci(rows, seed=42)
    assert a['mean']==pytest.approx(5.0)
    assert b['mean']==pytest.approx(10/101)
    assert b['observed_records']==101
    assert b['clusters']==2
    assert b['estimand']=='RECORD_WEIGHTED_MEAN_WITH_SESSION_BLOCK_RESAMPLING'


def test_balanced_session_sizes_agree_on_point_estimate():
    rows={'session-A':[0.0,0.0], 'session-B':[10.0,10.0]}
    assert session_bootstrap_ci(rows)['mean']==pytest.approx(5.0)
    assert record_weighted_cluster_bootstrap_ci(rows)['mean']==pytest.approx(5.0)


def test_reproducible_and_full_session_draws_not_iid_row_resampling():
    rows={'session-A':[0.0]*100, 'session-B':[10.0]}
    a=record_weighted_cluster_bootstrap_ci(rows, seed=8, replicates=100)
    b=record_weighted_cluster_bootstrap_ci(rows, seed=8, replicates=100)
    assert a==b
    # For two full-session draws, endpoints can only be those three values:
    assert any(a['lower']==pytest.approx(x) for x in (0.0,10/101,10.0))
    assert any(a['upper']==pytest.approx(x) for x in (0.0,10/101,10.0))


@pytest.mark.parametrize('bad', [{},{'one':[1.0]},{'A':[],'B':[1.0]},{'A':[float('nan')],'B':[1.0]}])
def test_unsafe_clusters_fail_closed(bad):
    with pytest.raises(ValueError):
        record_weighted_cluster_bootstrap_ci(bad)


def test_illegal_replicate_count_rejected():
    with pytest.raises(ValueError):
        record_weighted_cluster_bootstrap_ci({'A':[0.0],'B':[1.0]},replicates=2)
