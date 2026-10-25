import sys
from pathlib import Path
from datetime import datetime, timezone
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'src'))
from politics_fantasy.network import VoteRecord, covote_edges

def dt(day):return datetime(2026,1,day,tzinfo=timezone.utc)

def test_rollcalls_are_asof_and_descriptive():
    votes=[VoteRecord(f'v{j}',pid,choice,dt(j),dt(j+1))
           for j in (1,3,5) for pid,choice in [('A','YES'),('B','YES'),('C','NO')]]
    r=covote_edges(votes,as_of=dt(4),min_joint=1)
    ab=next(x for x in r if x['left']=='A' and x['right']=='B')
    assert ab['joint_votes']==2
    assert ab['agreements']==2
    assert abs(ab['agreement_smoothed'] - .75)<1e-12
    assert ab['status']=='DESCRIPTIVE_NOT_CAUSAL'