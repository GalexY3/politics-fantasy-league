from datetime import datetime, timezone, timedelta
import pytest
from politics_fantasy.rollcall import NominalVote,rollcall_as_of
D=lambda d:datetime(2026,1,d,tzinfo=timezone.utc)
H='a'*64

def V(**kw):
    d=dict(vote_id='v1',person_id='p1',group_at_vote='A',choice='YES',occurred_at=D(1),first_public_at=D(2),recorded_at=D(3),source_url='https://congreso.es/demo',source_sha256=H,revision=1)
    d.update(kw);return NominalVote(**d)

def test_br30_01_choice_closed_vocabulary():
    with pytest.raises(ValueError,match='choice'):V(choice='MISSING')
    assert V(choice='NO_VOTE').choice=='NO_VOTE'

def test_br30_02_same_revision_conflict_fails_closed():
    with pytest.raises(ValueError,match='Conflicting'):rollcall_as_of([V(),V(choice='NO')],D(8))

def test_br30_03_not_yet_published_excluded():
    assert rollcall_as_of([V(first_public_at=D(7),recorded_at=D(7))],D(6))==[]

def test_br30_04_late_ingestion_cannot_backfill_history():
    assert rollcall_as_of([V(recorded_at=D(9))],D(8))==[]

def test_br30_05_last_known_revision_wins_not_last_row():
    old=V();new=V(choice='NO',recorded_at=D(7),revision=2)
    assert rollcall_as_of([new,old],D(8))==[new]
    assert rollcall_as_of([new,old],D(5))==[old]

def test_br30_06_historic_group_not_current_group():
    old=V(group_at_vote='A');v2=V(vote_id='v2',group_at_vote='B',occurred_at=D(4),first_public_at=D(5),recorded_at=D(6))
    assert [v.group_at_vote for v in rollcall_as_of([old,v2],D(8))]==['A','B']
