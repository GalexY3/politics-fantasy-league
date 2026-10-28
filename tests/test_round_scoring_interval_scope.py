"""C15: a malformed event outside the fictional scoring interval cannot poison it."""
from datetime import datetime,timezone,timedelta
from politics_fantasy.product import seed_demo,connect,state

NOW=datetime(2026,10,28,tzinfo=timezone.utc)

def test_future_irrelevant_invalid_sha_does_not_crash_past_score(tmp_path):
    path=tmp_path/'game.sqlite'
    seed_demo(path,now=NOW)
    before=state(path,pilot_csv=None,when=NOW)
    past=next(x for x in before['rounds'] if x['id']=='past')
    previous=past['scores']['demo']
    assert previous is not None
    with connect(path) as db:
        when=(NOW+timedelta(days=100)).isoformat(timespec='seconds')
        db.execute("INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)",
                   ('SYN-IRRELEVANT','F01','speech_recorded',when,when,
                    'not-a-valid-sha256','synthetic://fixture','v1'))
    after=state(path,pilot_csv=None,when=NOW)
    assert next(x for x in after['rounds'] if x['id']=='past')['scores']['demo']==previous

def test_non_synthetic_inside_period_cannot_receive_a_score(tmp_path):
    path=tmp_path/'game.sqlite'
    seed_demo(path,now=NOW)
    with connect(path) as db:
        when=(NOW-timedelta(days=13)).isoformat(timespec='seconds')
        db.execute("INSERT INTO demo_event VALUES(?,?,?,?,?,?,?,?)",
                   ('FOREIGN-IN-ROUND','F01','speech_recorded',when,when,
                    'a'*64,'https://example.invalid/nonfiction','v1'))
    after=state(path,pilot_csv=None,when=NOW)
    assert next(x for x in after['rounds'] if x['id']=='past')['scores']['demo'] is None
