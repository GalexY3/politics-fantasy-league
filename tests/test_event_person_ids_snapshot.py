"""C14: fictional event identity list cannot mutate after frozen construction."""
from datetime import datetime,timezone
import pytest
from politics_fantasy.events import PoliticalEvent
D=lambda d:datetime(2026,10,d,tzinfo=timezone.utc)

def event(people):
    return PoliticalEvent('synthetic','speech_recorded',D(1),D(2),
                          people,'https://example.invalid/source','a'*64,'v1',{})

def test_caller_list_alias_does_not_mutate_scored_people():
    source=['F1']
    e=event(source)
    source.append('F2')
    assert e.person_ids==('F1',)
    with pytest.raises(AttributeError):
        e.person_ids.append('F3')

@pytest.mark.parametrize('bad',[['F1','F1'],[''],['F1',None],{'F1'},'F1'])
def test_invalid_person_id_container_fails_closed(bad):
    with pytest.raises(ValueError):
        event(bad)

def test_tuple_inputs_preserved():
    assert event(('F1','F2')).person_ids==('F1','F2')
