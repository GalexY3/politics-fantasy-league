from math import exp
import pytest
from politics_fantasy.evaluation import poisson_nll,count_mae,relative_skill,calibration_bins,purged_walk_forward,session_bootstrap_ci

def test_br30_19_full_poisson_nll_includes_factorial_and_zero_edge():
 assert poisson_nll(0,0)==0
 assert poisson_nll(2,2)==pytest.approx(2-2*__import__('math').log(2)+__import__('math').log(2))
 assert poisson_nll(1,0)==float('inf')

def test_br30_20_mae_requires_nonnegative_finite_counts():
 assert count_mae([(0,1.0),(2,2.0)])==pytest.approx(.5)
 with pytest.raises(ValueError):count_mae([])
 with pytest.raises(ValueError):count_mae([(1,-1)])

def test_br30_21_skill_vs_baseline_no_division_by_zero():
 assert relative_skill(2,4)==pytest.approx(.5)
 assert relative_skill(6,4)==pytest.approx(-.5)
 assert relative_skill(0,0) is None

def test_br30_22_calibration_never_fills_unobserved_bins():
 result=calibration_bins([(1,.1),(0,.2),(2,2.0)],edges=(.5,1.5),min_n=2)
 assert result[0]['n']==2 and result[0]['observed']==.5
 assert result[1]['observed'] is None and result[2]['status']=='LOW_SUPPORT'

def test_br30_23_purged_folds_have_nonoverlapping_temporal_windows():
 w=[f'2026-W{i:02d}' for i in range(1,10)]
 f=list(purged_walk_forward(w,min_train=3,gap=2,horizon=1))
 assert len(f)==4 and f[0]['train']==w[:3] and f[0]['purged']==w[3:5] and f[0]['test']==[w[5]]
 assert all(x['train'][-1]<x['purged'][0]<x['test'][0] for x in f)

def test_br30_24_cluster_bootstrap_keeps_session_units_and_is_reproducible():
 values={'s1':[0]*100,'s2':[10]}
 a=session_bootstrap_ci(values,seed=42)
 b=session_bootstrap_ci(values,seed=42)
 assert a==b and a['mean']==5 and a['clusters']==2
 assert a['lower']==0 and a['upper']==10
