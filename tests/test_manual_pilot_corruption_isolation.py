"""C17: a malformed manual aggregate cannot poison the fictional game /api/state."""
from datetime import datetime,timezone
import pytest
from politics_fantasy.product import seed_demo,state

NOW=datetime(2026,10,28,tzinfo=timezone.utc)

@pytest.mark.parametrize('body',[
    'yes,no,abstain,event_date\n2,1,0,2026-07-23\n',
    'row_id,yes,no,abstain,event_date\nx,BOGUS,1,0,2026-07-23\n',
    'row_id,yes,no,abstain,event_date\nx,-1,1,0,2026-07-23\n',
    'row_id,yes,no,abstain,event_date\nx,300,100,0,2026-07-23\n',
])
def test_bad_manual_pilot_is_quarantined_not_raised(tmp_path,body):
    db=tmp_path/'demo.sqlite'
    seed_demo(db,now=NOW)
    pilot=tmp_path/'manual.csv'
    pilot.write_text(body,encoding='utf8')
    report=state(db,pilot_csv=pilot,when=NOW)
    assert report['observatory']['status']=='MANUAL_AGGREGATE_INVALID'
    assert report['observatory']['votes']==[]
    assert len(report['figures'])==10
    assert report['mode']=='SYNTHETIC_FICTIONAL_DEMO_ONLY'

def test_valid_manual_pilot_still_explicitly_uncertified(tmp_path):
    db=tmp_path/'demo.sqlite'
    seed_demo(db,now=NOW)
    pilot=tmp_path/'manual.csv'
    pilot.write_text('row_id,yes,no,abstain,event_date\nx,2,1,0,2026-07-23\n',encoding='utf8')
    report=state(db,pilot_csv=pilot,when=NOW)
    assert report['observatory']['status']=='EXPLORATORY_MANUAL_AGGREGATE_NOT_VALIDATED'
    assert report['observatory']['votes'][0]['total']==3
    assert report['research_status']=='NO_REAL_INDIVIDUAL_PLAYER_SCORING_OR_PREDICTIONS'
