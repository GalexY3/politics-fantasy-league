from datetime import datetime,timezone
import pytest
from politics_fantasy.events import PoliticalEvent
from politics_fantasy.forecast import historical_rate
UTC=timezone.utc
def t(day): return datetime(2026,1,day,tzinfo=UTC)
def ev(id,occ,pub,version='v1',kind='speech_recorded'):
    return PoliticalEvent(id,kind,t(occ),t(pub),('F_SYN',),'synthetic://fixture','a'*64,version,{})
def rate(events,cut=10):
    return historical_rate(events,person_id='F_SYN',start=t(1),as_of=t(cut),exposure=8)
def test_late_publication_same_occurrence_not_leaked():
    known=[ev('e1',2,3)]
    later=ev('e2',4,11)
    assert rate(known)==rate(known+[later])
def test_late_revision_does_not_rewrite_past_cutoff():
    old=ev('e1',2,3)
    revised=ev('e1',2,11,'v2','scheduled_speech')
    assert rate([old])==rate([old,revised])
def test_new_publication_changes_only_later_asof():
    before=[ev('e1',2,3)]
    later=ev('e2',4,11)
    assert rate(before+[later],10).observed_history==1
    assert rate(before+[later],12).observed_history==2
def test_publication_at_cutoff_included():
    assert rate([ev('e1',9,10)],10).observed_history==1
def test_event_occurred_at_cutoff_not_historical():
    assert rate([ev('e1',10,10)],10).observed_history==0
def test_ambiguous_equal_publication_timestamp_refused():
    old=ev('e1',2,3)
    newer=ev('e1',2,3,'v2','question_registered')
    with pytest.raises(ValueError,match='Ambiguous public revisions'):
        rate([old,newer])
