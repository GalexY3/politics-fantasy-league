from datetime import datetime,timezone
import pytest
from politics_fantasy.rollcall import NominalVote
from politics_fantasy.structural import majority_margin,expressed_diversity,direct_standardization,simpson_reversal,pair_agreement
T=datetime(2026,1,1,tzinfo=timezone.utc)
def V(v,p,c,g='A'):
 return NominalVote(v,p,g,c,T,T,T,'https://congreso.es/demo','a'*64)

def test_br30_13_majority_margin_has_tie_and_empty_as_distinct_states():
 rows=[V('v1','a','YES'),V('v1','b','YES'),V('v1','c','NO'),V('v1','d','NO_VOTE')]
 assert majority_margin(rows,vote_id='v1',group_id='A')==pytest.approx(1/3)
 assert majority_margin(rows,vote_id='v9',group_id='A') is None

def test_br30_14_entropy_excludes_no_vote_from_expressed_diversity():
 assert expressed_diversity(['YES','YES','NO_VOTE'])==0
 assert expressed_diversity(['YES','NO','ABSTAIN'])==pytest.approx(1)
 assert expressed_diversity(['NO_VOTE']) is None

def test_br30_15_standardization_forbids_missing_strata_and_normalizes_weights():
 assert direct_standardization({'a':(10,10),'b':(0,10)},{'a':.25,'b':.75})==.25
 with pytest.raises(ValueError):direct_standardization({'a':(1,1)},{'a':.4,'b':.6})

def test_br30_16_simpson_reversal_flag_not_treated_as_causality():
 A={'easy':(9,10),'hard':(20,100)}
 B={'easy':(80,100),'hard':(1,10)}
 r=simpson_reversal(A,B)
 assert r['reversal'] and all(x>0 for x in r['stratum_differences'].values()) and r['pooled_difference']<0

def test_br30_17_pair_exposure_requires_both_expressed_not_no_vote():
 votes=[V('v1','a','YES'),V('v1','b','YES'),V('v2','a','YES'),V('v2','b','NO_VOTE'),V('v3','a','NO')]
 r=pair_agreement(votes,left='a',right='b')
 assert r['joint_n']==1 and r['observed']==1

def test_br30_18_marginal_chance_baseline_deflates_trivial_agreement():
 votes=[V('v1','a','YES'),V('v1','b','YES'),V('v2','a','YES'),V('v2','b','YES')]
 r=pair_agreement(votes,left='a',right='b')
 assert r['observed']==1 and r['chance']==1 and r['excess']==0
 votes=[V('v1','a','YES'),V('v1','b','YES'),V('v2','a','NO'),V('v2','b','NO')]
 assert pair_agreement(votes,left='a',right='b')['excess']==pytest.approx(.5)
