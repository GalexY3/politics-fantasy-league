"""C11: cloned immutable nested source metadata, synthetic records only."""
from datetime import datetime, timezone
import pytest
from politics_fantasy.events import PoliticalEvent, unique_events

D=lambda d: datetime(2026,10,d,tzinfo=timezone.utc)

def event(metadata):
    return PoliticalEvent('e','speech_recorded',D(1),D(2),('fictional',),
                          'https://example.invalid/synthetic','a'*64,'v1',metadata)

def test_source_alias_and_deep_field_cannot_mutate_event():
    data={'outer':{'items':[1,{'code':'OLD'}]}}
    e=event(data)
    data['outer']['items'][1]['code']='FORGED'
    assert e.metadata['outer']['items'][1]['code']=='OLD'
    with pytest.raises(TypeError):
        e.metadata['outer']['items'][1]['code']='CHANGED'
    with pytest.raises(TypeError):
        e.metadata['outer']['items'][0]=9

def test_deep_equal_duplicates_and_conflicting_revisions():
    a=event({'nested':[{'x':1}]})
    b=event({'nested':[{'x':1}]})
    assert unique_events([a,b])==[a]
    with pytest.raises(ValueError, match='Conflicting source revision'):
        unique_events([a,event({'nested':[{'x':2}]})])

def test_non_json_container_input_rejected():
    with pytest.raises(ValueError,match='Unsupported metadata'):
        event({'nested':set([1,2])})
